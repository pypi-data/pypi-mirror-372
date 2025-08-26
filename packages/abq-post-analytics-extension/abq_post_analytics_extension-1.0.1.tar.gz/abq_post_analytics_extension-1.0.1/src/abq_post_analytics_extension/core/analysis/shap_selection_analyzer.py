# -*- coding: UTF-8 -*-
import os
import numpy as np

try:
    from typing import Generator, Type
except ImportError:
    pass

from abq_post_analytics_extension.core.analysis.analyzer import SpecifyFieldHistoryValueAnalyzer
from abq_post_analytics_extension.core.analysis.base import CoordinatesPackagedMeshObjectsSelector, OdbAnalyzerBase, \
    FrameHandlerType
from abq_post_analytics_extension.utils.misc_utils import sample_list, check_type
from abq_post_analytics_extension.utils.scientific_computing import is_3d_vector


class _Line(object):
    """
    线段等间距点生成器类。
    """
    def __init__(self, name, start_coordinate, end_coordinate, points_num=None, points_spacing=None):
        """
        初始化线段等间距点生成器。

        该构造函数初始化了一个线段等间距点生成器对象，该对象用于在给定的起始点和结束点之间生成等间距的点。
        用户可以指定生成的点的数量（points_num），或者点之间的间距（points_spacing）。如果两者都指定了，
        则以points_num为准。

        :param name: 线段的名称，用于标识线段。
        :type name: str
        :param start_coordinate: 线段的起始点，必须是一个3D向量。
        :type start_coordinate: list[float]
        :param end_coordinate: 线段的结束点，必须是一个3D向量。
        :type end_coordinate: list[float]
        :param points_num: (可选) 在线段上生成的点的数量。
        :type points_num: int
        :param points_spacing: (可选) 相邻点之间的间距。
        :type points_spacing: float
        :raises TypeError: 如果name不是字符串，则抛出此异常。
        :raises TypeError: 如果起始点或结束点不是3D向量，则抛出此异常。
        :raises ValueError: 如果既没有指定点的数量也没有指定点的间距，则抛出此异常。
        """
        if not isinstance(name, str):
            raise TypeError("The name must be a string.")
        # 检查起始点和结束点是否为3D向量
        if not all(is_3d_vector(coordinate)
                   for coordinate in (start_coordinate, end_coordinate)):
            raise TypeError("The start_coordinate and end_coordinate must be 3D vectors.")
        # 确保要么指定了点的数量，要么指定了点的间距
        if points_num is None and points_spacing is None:
            raise ValueError("Either points_num or points_spacing must be specified.")

        # 保存初始化参数作为对象的属性
        self._name = name
        self._start_coordinate = start_coordinate
        self._end_coordinate = end_coordinate
        self._points_num = points_num
        self._points_spacing = points_spacing
        self._coordinates_on_line = None
        self._coordinates_on_line_with_density = None
        self.density = 1
        self._coordinates_length_with_density = None

    @property
    def name(self):
        """
        获取线段的名称。

        :return: 线段的名称。
        """
        return self._name

    @property
    def coordinates_length(self):
        """
        返回线上坐标点的数量。

        该属性方法返回线上坐标点的数量，即点数量或点间距的较大值。

        :return: 线上坐标点的数量。
        :rtype: int
        """
        return len(self.coordinates_on_line)

    @property
    def coordinates_on_line_with_density(self):
        """
        根据密度采样线上的坐标。

        这个属性方法用于获取在一条线上的坐标点，这些坐标点是根据预设的密度进行采样的。
        它首先检查是否已经计算并存储了带有指定密度的坐标，如果没有，则在调用时进行计算和存储。

        :return: 带有指定密度采样的线坐标列表。
        :rtype: list[list[float]]
        """
        if self._coordinates_on_line_with_density is None:
            # 如果还未计算带有密度采样的坐标，则现在进行计算
            self._coordinates_on_line_with_density = sample_list(self.coordinates_on_line, self.density)
        return self._coordinates_on_line_with_density

    @property
    def coordinates_length_with_density(self):
        """
        考虑密度因素的坐标长度属性

        此属性根据当前设置的密度（density）计算并返回调整后的坐标长度。密度通过一个名为density的实例变量来设置，
        该变量表示每单位长度内的坐标点数量。此方法通过计算基于给定密度的有效坐标点数量，提供了对坐标长度的
        一种更细致的访问方式。

        :return: 考虑密度因素后，坐标点的数量（整数类型）
        :rtype: int
        """
        if self._coordinates_length_with_density is None:
            # 计算并返回考虑密度因素后的坐标点数量
            self._coordinates_length_with_density = len(self.coordinates_on_line_with_density)
        return self._coordinates_length_with_density

    @property
    def coordinates_on_line(self):
        """
        根据起始坐标、结束坐标和指定的点数量或点间距，生成线上坐标点的属性。

        该属性方法会在请求坐标点数据时被触发，根据事先设置的点的数量或点间距，
        计算并返回线上的一系列坐标点。如果点的数量和点间距都未被明确指定，则会
        根据点的数量来生成坐标点。

        :return: 包含线上所有坐标点的列表。
        :rtype: list[list[float]]
        """
        # 检查是否已计算坐标点，如果未计算则根据点数量或点间距进行计算
        if self._coordinates_on_line is None:
            if self._points_num is not None:
                # 如果点的数量已设置，则根据点的数量生成点
                self._coordinates_on_line = self._generate_points_on_line_by_num(
                    self._start_coordinate, self._end_coordinate, self._points_num)
            else:
                # 如果点的数量未设置，则根据点间距生成点
                self._coordinates_on_line = self._generate_points_on_line_by_spacing(
                    self._start_coordinate, self._end_coordinate, self._points_spacing)
        return self._coordinates_on_line

    def get_coordinates_with_density(self, density=None):
        """
        根据指定的密度采样坐标。

        该方法用于获取坐标点，但不是直接返回所有坐标，而是根据指定的密度进行采样。
        如果没有指定密度，或者指定的密度为None，则使用对象默认的密度进行采样。
        特别地，当密度为1时，直接返回所有坐标点，不进行采样。

        :param density: 采样的密度，决定了从坐标集中采样多少点。
        :type density: int|None
        :return: 根据指定密度采样得到的坐标点列表。
        :rtype: list[list[float]]
        """
        # 检查是否提供了密度参数，如果没有提供，则使用对象默认的密度
        if density is None:
            density = self.density

        # 如果密度为1，直接返回所有坐标点，不进行采样
        if density == 1:
            return self.coordinates_on_line
        # 否则，根据指定的密度对坐标点进行采样，并返回采样后的坐标点列表
        else:
            return sample_list(self.coordinates_on_line, density)

    @staticmethod
    def _generate_points_on_line_by_num(start, end, num):
        """
        根据指定点数生成直线上的点。

        该函数主要用于在线段上均匀分布指定数量的点。它首先计算出起点和终点之间的距离，
        然后基于这个距离和所需点的数量，利用另一个函数generate_points_on_line_by_spacing来生成这些点。

        :param start: 线的起点坐标，可以是二维或更高维度的点。
        :type start: list[float]|tuple[float]|numpy.ndarray
        :param end: 线的终点坐标，必须与起点有相同的维度。
        :type end: list[float]|tuple[float]|numpy.ndarray
        :param num: 需要生成的点的数量，包括起点和终点在内。
        :type num: int
        :return: 一个包含所有生成点坐标的列表 [(x1, y1, z1), ...]
        :rtype: list[list[float]]
        """
        # 将起点和终点转换为numpy数组，以便进行后续的向量计算
        start, end = np.array(start), np.array(end)

        # 计算点之间的间距，使用numpy的linalg.norm计算欧氏距离
        spacing = np.linalg.norm(end - start) / (num - 1)

        # 调用另一个函数，根据计算出的间距生成点
        return _Line._generate_points_on_line_by_spacing(
            start, end, spacing)

    @staticmethod
    def _generate_points_on_line_by_spacing(start, end, spacing):
        """
        根据指定间距在三维空间中的线段上生成一系列点（包括端点）。

        :param start: 线段的起点坐标 (x1, y1, z1)，
        :type start: list[float]|tuple[float]|numpy.ndarray
        :param end: 线段的终点坐标 (x2, y2, z2)，
        :type end: list[float]|tuple[float]|numpy.ndarray
        :param spacing: 在线段上生成点的间距
        :type spacing: float
        :return: 一个包含所有生成点坐标的列表 [(x, y, z), ...]
        :rtype: list[list[float]]
        """
        start, end = np.array(start), np.array(end)
        # 计算线段的方向向量
        direction = end - start
        # 计算线段的长度
        length = np.linalg.norm(direction)
        # 计算单位方向向量
        unit_direction = direction / length

        # 计算从起点到终点之间可以放置多少个点
        num_points = int(length // spacing)

        # 生成点
        points = []
        for i in range(num_points + 1):
            point = start + i * spacing * unit_direction
            points.append(point)
        if not all(np.isclose(points[-1], end)):
            points.append(tuple(end))

        return points


class LinePackagedMeshObjectsSelector(CoordinatesPackagedMeshObjectsSelector):
    """
    线上多点的包含坐标的几何odb节点或单元对象管理器。
    """

    def __init__(self, packaged_odb_objects, instance_name=None, set_name=None):
        """
        初始化CoordinatesPackagedMeshObjectsHandler类。

        获取指定实例或集合名称的实例或集合中的坐标的几何odb节点或单元对象

        :param instance_name: 实例名称。
        :type instance_name: str
        :param set_name: 集合名称，实例名称或集合名称，至少指定一个。
        :type set_name: str
        :param packaged_odb_objects: 一个PackagedOdbObjects实例，包含封装的ODB对象。
        :type packaged_odb_objects: PackagedOdbObjects
        """
        super(LinePackagedMeshObjectsSelector, self).__init__(packaged_odb_objects, instance_name, set_name)
        self._line = None

    @property
    def coordinates_list(self):
        if len(self._coordinates_list) == 0:
            if self._line is None:
                raise ValueError("line is not set yet.")
            self.add_coordinates(self._line.coordinates_on_line)
        return self._coordinates_list

    def set_line(self, name, start_coordinate, end_coordinate, points_num=None, points_spacing=None):
        """
        设置线段。

        :param name: 线段的名称，用于标识线段。
        :type name: str
        :param start_coordinate: 线段的起始点，必须是一个3D向量。
        :param end_coordinate: 线段的结束点，必须是一个3D向量。
        :param points_num: (可选) 在线段上生成的点的数量。
        :type points_num: int
        :param points_spacing: (可选) 相邻点之间的间距。与points_num两者必有其一
        :type points_spacing: float
        :return:
        """
        self.name = name
        self._line = _Line(name, start_coordinate, end_coordinate, points_num, points_spacing)


class LinesPackagedMeshObjectsSelectorManager(OdbAnalyzerBase):
    """
    多条LinePackagedMeshObjectsHandler线段对象的管理器。
    """

    def __init__(self, packaged_odb_objects, instance_name=None, set_name=None):
        """


        :param packaged_odb_objects: 一个PackagedOdbObjects实例，包含封装的ODB对象。
        :type packaged_odb_objects: PackagedOdbObjects
        :param instance_name: 实例名称，add_line方法添加线对象时默认使用此项。
        :type instance_name: str
        :param set_name: 集合名称，add_line方法添加线对象时默认使用此项。
        :type set_name: str
        """
        super(LinesPackagedMeshObjectsSelectorManager, self).__init__(packaged_odb_objects)
        self._lines = []
        self._instance_name = instance_name
        self._set_name = set_name

    def add_line(
            self, name, start_coordinate, end_coordinate, points_num=None, points_spacing=None, instance_name=None,
            set_name=None):
        """
        添加线段。

        :param name: 表示线段的唯一标识符。可以用于在帧处理器（FrameHandlerBase的子类，如果实现了相关功能）返回的结果中，区分不同的线段。
        :type name: str
        :param start_coordinate: 线段的起始点，必须是一个3D向量。
        :param end_coordinate: 线段的结束点，必须是一个3D向量。
        :param points_num: (可选) 在线段上生成的点的数量。
        :type points_num: int
        :param points_spacing: (可选) 相邻点之间的间距。与points_num两者必有其一
        :type points_spacing: float
        :param instance_name: 实例名称。默认使用self._instance_name。
        :type instance_name: str
        :param set_name: 集合名称，默认使用self._set_name。实例名称或集合名称，至少指定一个。
        :type set_name: str
        :return:
        """
        if instance_name is None:
            instance_name = self._instance_name
        if set_name is None:
            set_name = self._set_name
        line_handler = LinePackagedMeshObjectsSelector(self.packaged_odb_objects, instance_name, set_name)
        line_handler.set_line(name, start_coordinate, end_coordinate, points_num, points_spacing)
        self._lines.append(line_handler)

    def get_lines(self):
        """
        获取每个线段。

        :return: 每个线段的LinePackagedMeshObjectsHandler对象。
        :rtype: Generator[LinePackagedMeshObjectsSelector]
        """
        for line in self._lines:
            yield line


class LinesFieldHistoryValueAnalyzer(FrameHandlerType):
    def send_frame(self, packaged_frame):
        """
        发送数据帧并接收处理后的消息。

        本函数遍历所有的帧处理器，将打包后的数据帧发送给每个处理器进行处理。
        每个处理器处理后的消息会被收集起来，最终返回第一个处理器的消息。
        :param packaged_frame: 打包后的数据帧，准备发送给每个帧处理器。
        :return: 返回第一个帧处理器处理后的消息。
        """
        # 初始化消息列表，用于收集每个帧处理器处理后的消息
        message_list = []
        # 遍历所有帧处理器
        for frame_handler in self._get_every_frame_handler():
            # 将数据帧发送给当前处理器，并接收处理后的消息
            message = frame_handler.send_frame(packaged_frame)
            # 将处理后的消息添加到消息列表中
            message_list.append(message)
        # 返回第一个帧处理器处理后的消息
        return message_list[0]

    def __init__(
            self, field_output_type, packaged_meshes_handler, support_packaged_meshes_handler=None,
            data_relative_type=None, feature_algorithm=None, data_attribute_names=None, if_load_data=True,
            specify_field_history_value_analyzer=None, *args, **kwargs):
        """
        :param field_output_type: 要获取的场输出的类型，"U"或"S"或“A”或其他支持的类型。
        :type field_output_type: str
        :param packaged_meshes_handler: 获取多条线上的几何odb单元或节点的对象
        :type packaged_meshes_handler: LinesPackagedMeshObjectsSelectorManager
        :param support_packaged_meshes_handler: 支座的获取几何odb单元或节点的对象，要分析相对支座的值时需传入此项。
        :type support_packaged_meshes_handler: PackagedMeshObjectsHandlerBase|None
        :param data_relative_type: 数据的相对类型，可以是
            - "real"，默认值（类常量REAL_TYPE）表示分析每个数据点真实值；
            - "first_frame_relate"（类常量FIRST_FRAME_TYPE）表示分析每个数据点相对于其首帧的值；
            - "support_relate"（类常量SUPPORT_TYPE）表示分析每个数据点相对于同一帧的支座值
        :type data_relative_type: str|None
        :param feature_algorithm:
            - 如果为 None，默认使用ExtremaValueSelector()默认选项创建对象，即获取每个属性绝对值最大的
                PackagedFieldValue 或 PackagedElementFieldValue 对象。
            - 如果是 FeatureCalculatorBase | FeatureSelectorBase 的实例，则根据设定条件获取相应值。
            - 如果是字典，键为属性名称，值为获取该属性值的条件。
                此时，condition 的键将覆盖 data_attribute_names 的设置，只会获取键指定的属性值。
            - 当前对象使用的ValueSelectorBase子类对象是此参数传入的对象使用copy.deepcopy()创建的副本，不会修改原对象。
        :type feature_algorithm: None | FeatureCalculatorBase | FeatureSelectorBase |
            dict[str, list[FeatureCalculatorBase | FeatureSelectorBase] | FeatureCalculatorBase | FeatureSelectorBase]
        :param data_attribute_names: 需要处理的场输出PackagedFieldValue或PackagedElementFieldValue对象的属性名称
        :type data_attribute_names: list[str]|None
        :param if_load_data: 是否在调用handle_frame处理数据前先加载传入其中的FieldValuesManager
                对象的当前对象data_attribute_names属性指定的数据，默认为True
        :type if_load_data: bool
        :param specify_field_history_value_analyzer: （SpecifyFieldHistoryValueAnalyzer类或其子类或None）
            指定要处理的数据帧的处理器类，默认为SpecifyFieldHistoryValueAnalyzer，
        """
        super(LinesFieldHistoryValueAnalyzer, self).__init__(*args, **kwargs)
        check_type(packaged_meshes_handler, LinesPackagedMeshObjectsSelectorManager)
        self._packaged_meshes_handler = packaged_meshes_handler
        self._field_output_type = field_output_type
        self._data_attribute_names = data_attribute_names
        self._support_packaged_meshes_handler = support_packaged_meshes_handler
        self._data_relative_type = data_relative_type
        self._feature_algorithm = feature_algorithm
        self._if_load_data = if_load_data
        if specify_field_history_value_analyzer is None:
            specify_field_history_value_analyzer = SpecifyFieldHistoryValueAnalyzer
        else:
            check_type(specify_field_history_value_analyzer, SpecifyFieldHistoryValueAnalyzer)
        self._frame_max_history_datas_handler_type = specify_field_history_value_analyzer
        self._frame_max_history_datas_handlers = []
        self._init_frame_handlers()

    def _init_frame_handlers(self):
        """
        初始化帧处理程序列表。

        遍历打包的网格处理程序的每一行，为每一行创建一个帧最大历史数据处理程序实例，
        并将其添加到帧最大历史数据处理程序列表中。

        :return: None
        """
        # 遍历打包的网格处理程序的每一行
        for line in self._packaged_meshes_handler.get_lines():
            # 创建帧最大历史数据处理程序实例
            frame_max_history_datas_handler = self._frame_max_history_datas_handler_type(
                self._field_output_type, line, self._support_packaged_meshes_handler,
                self._data_relative_type, self._feature_algorithm, self._data_attribute_names, self._if_load_data)
            # 将实例添加到帧最大历史数据处理程序列表中
            self._frame_max_history_datas_handlers.append(frame_max_history_datas_handler)

    def _get_every_frame_handler(self):
        """
        一个生成器函数，用于迭代地获取每个帧的最大历史数据处理器。

        :return: 一个帧的最大历史数据处理器，每次迭代返回一个。
        :rtype: Generator[SpecifyFieldHistoryValueAnalyzer]
        """
        # 迭代帧的最大历史数据处理器列表
        for frame_max_history_datas_handler in self._frame_max_history_datas_handlers:
            # 在每次迭代中返回当前的帧最大历史数据处理器
            yield frame_max_history_datas_handler

    def generate_datas_dict(self, generate_type, customize_data_attribute_names=None):
        """
        生成数据字典的迭代器。

        本函数通过遍历每一个帧处理器，并调用帧处理器的generate_datas_dict方法，
        来收集并生成包含数据字典的迭代器。

        :param generate_type: 生成数据的类型，必须为 “sect”（类常量SECT_TYPE） 或 "calc"（类常量CALC_TYPE）。
            - “sect”（类常量SECT_TYPE）：获取由FeatureCalculatorBase定义的计算特征值方法得到的特征值结果。
            - "calc"（类常量CALC_TYPE）：获取由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据。
        :type generate_type: str
        :param customize_data_attribute_names: 自定义数据属性名称列表，用于生成特定的数据字典。
        :yield: 数据字典，包含帧处理器处理后的数据。
        """
        # 遍历每一个帧处理器
        for frame_handler in self._get_every_frame_handler():
            # 调用帧处理器的generate_datas_dict方法，生成并收集数据字典
            for datas_dict in frame_handler.generate_datas_dict(generate_type, customize_data_attribute_names):
                # 将数据字典传递给调用者
                yield datas_dict

    def save_datas(
            self, sect_file_name=None, calc_file_name=None, file_name_prefix="", folder_path=None, covered=True,
            save_columns_name=None):
        """
        将数据保存到文件中。

        :param file_name_prefix: 文件名前缀，添加到设置的或默认的文件名中。
        :type file_name_prefix: str
        :param covered: 布尔值，指示是否覆盖现有文件。如果为True，则覆盖文件；如果为False，则追加到文件。
        :type covered: bool
        :param save_columns_name: 是否保存列名。如果为True，则保存列名；如果为False，则不保存列名。默认为与covered相同。
        :type save_columns_name: bool | None
        :param sect_file_name: 由FeatureCalculatorBase定义的计算特征值方法得到的特征值结果数据保存的文件名。
            如果未指定，则使用默认文件名"specify_field_history_values_calc_datas.txt"。
        :type sect_file_name: str  | None
        :param calc_file_name: 由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据数据保存的文件名。
            如果未指定，则使用默认文件名"specify_field_history_values_sect_datas.txt"。
        :type calc_file_name: str | None
        :param folder_path: 数据保存的文件夹路径。如果未指定，则使用当前工作目录。
        :type folder_path: str | None
       """
        # 遍历每一个数据处理者，为它们保存数据
        for index, handler in enumerate(self._get_every_frame_handler()):
            covered_ = False
            # 对于第一个数据处理者，根据covered变量的值决定是否覆盖数据
            if index == 0:
                if covered:
                    covered_ = True
            else:
                # 对于非第一个数据处理者，不保存列名
                save_columns_name = False
            # 调用数据处理者的保存数据方法，传入必要的参数
            handler.save_datas(
                sect_file_name, calc_file_name, file_name_prefix, folder_path, covered_, save_columns_name)


if __name__ == "__main__":
    pass
