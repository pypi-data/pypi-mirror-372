# -*- coding: UTF-8 -*-
import copy
import os
import threading
from collections import OrderedDict

try:
    from typing import Generator
except ImportError:
    pass
from abq_post_analytics_extension.utils.system_utilities import AbqPostExtensionBase
from abq_post_analytics_extension.core.analysis.base import FrameHandlerBase, PackagedMeshObjectsSelectorBase
from abq_post_analytics_extension.utils.file_operations import ExtendedFile
from abq_post_analytics_extension.utils.misc_utils import check_type, get_nested_attribute
from abq_post_analytics_extension.core.access import FieldValuesManager, PackagedFieldValue, PackagedElementFieldValue, \
    PackagedFieldOutputValues, PackagedFrame


class FeatureCalculatorBase(AbqPostExtensionBase):
    def __init__(self, name, *args, **kwargs):
        """
        初始化 FeatureCalculatorBase 类的实例。

        :param name: 特征名称。
        :type name: str
        """
        super(FeatureCalculatorBase, self).__init__(name=name, *args, **kwargs)
        check_type(name, str, None)

    def process_each_value(self, value):
        """
        处理单个输入值。

        :param value: 输入的数值，用于计算特征。
        """
        raise NotImplementedError()

    def get_result_data(self):
        """
        获取最终的计算结果。

        :return: 最终的特征值。
        """
        raise NotImplementedError()


class AverageCalculator(FeatureCalculatorBase):
    """
    计算平均值的特征计算器。
    """

    def __init__(self, name=None, if_calculate_abs=False):
        """
        初始化 AverageCalculator 实例。

        :param if_calculate_abs: 是否计算绝对值的平均值，默认为 False。
        :type if_calculate_abs: bool
        """
        super(AverageCalculator, self).__init__(name)
        self._sum = 0
        self._count = 0
        self._if_calculate_abs = if_calculate_abs
        if name is None:
            name = self._init_default_name()
        else:
            check_type(name, str)
        self._name = name

    def _init_default_name(self):
        """
        初始化默认的名称。

        :return: 默认的名称。
        """
        if self._if_calculate_abs:
            abs_str = "Abs a"
        else:
            abs_str = "A"
        return "{}verage value".format(abs_str)

    def process_each_value(self, value):
        """
        处理每个值，累加到总和并增加计数。
        如果配置了比较绝对值，则计算当前值的绝对值。

        :param value: 当前处理的值。
        """
        if self._if_calculate_abs:
            value = abs(value)
        self._sum += value
        self._count += 1

    def get_average_value(self):
        """
        计算并返回平均值。

        :return: 计算得到的平均值。
        """
        if self._count == 0:
            return 0  # 或者返回 None，根据需求决定
        return self._sum / self._count

    def get_result_data(self):
        """
        计算并返回平均值。

        :return: 计算得到的平均值。
        """
        return self.get_average_value()


class VarianceCalculator(AverageCalculator):
    """
    计算方差的特征计算器。
    """

    def __init__(self, name=None, if_calculate_abs=False):
        """
        初始化 VarianceCalculator 实例。

        :param if_calculate_abs: 是否计算绝对值的方差，默认为 False。
        :type if_calculate_abs: bool
        """
        super(VarianceCalculator, self).__init__(name, if_calculate_abs)
        self._sum_of_squares = 0

    def _init_default_name(self):
        if self._if_calculate_abs:
            abs_str = "Abs v"
        else:
            abs_str = "V"
        return "{}ariance value".format(abs_str)

    def process_each_value(self, value):
        """
        处理每个值，累加到总和和平方和，并增加计数。
        如果配置了比较绝对值，则计算当前值的绝对值。

        :param value: 当前处理的值。
        """
        super(VarianceCalculator, self).process_each_value(value)
        if self._if_calculate_abs:
            value = abs(value)
        self._sum_of_squares += value ** 2

    def get_variance_value(self):
        """
        计算并返回方差。

        :return: 计算得到的方差。
        """
        if self._count == 0:
            return 0
        mean = self.get_average_value()
        variance = (self._sum_of_squares / self._count) - (mean ** 2)
        return variance

    def get_result_data(self):
        """
        计算并返回方差。

        :return: 计算得到的方差。
        """
        return self.get_variance_value()


class StandardDeviationCalculator(VarianceCalculator):
    """
    计算标准差的特征计算器。
    """

    def __init__(self, name=None, if_calculate_abs=False):
        """
        初始化 StandardDeviationCalculator 实例。

        :param if_calculate_abs: 是否计算绝对值的标准差，默认为 False。
        :type if_calculate_abs: bool
        """
        super(StandardDeviationCalculator, self).__init__(name, if_calculate_abs)

    def _init_default_name(self):
        if self._if_calculate_abs:
            abs_str = "Abs s"
        else:
            abs_str = "S"
        return "{}tandard deviation value".format(abs_str)

    def get_standard_deviation_value(self):
        """
        计算并返回标准差。

        :return: 计算得到的标准差。
        """
        if self._count == 0:
            return 0
        return self.get_variance_value() ** 0.5

    def get_result_data(self):
        """
        计算并返回标准差。

        :return: 计算得到的标准差。
        """
        return self.get_standard_deviation_value()


class CoefficientOfVariationCalculator(StandardDeviationCalculator):
    """
    计算变异系数的特征计算器。
    """

    def __init__(self, name=None, if_calculate_abs=False):
        """
        初始化 CoefficientOfVariationCalculator 实例。
        """
        super(CoefficientOfVariationCalculator, self).__init__(name, if_calculate_abs)

    def _init_default_name(self):
        if self._if_calculate_abs:
            abs_str = "Abs c"
        else:
            abs_str = "C"
        return "{}oefficient of variation value".format(abs_str)

    def get_coefficient_of_variation(self):
        """
        计算并返回变异系数。

        :return: 计算得到的变异系数。
        """
        average_value = self.get_average_value()
        if self._count == 0:
            return 0
        if average_value == 0:
            return float('inf')
        return self.get_standard_deviation_value() / average_value

    def get_result_data(self):
        """
        计算并返回变异系数。

        :return: 计算得到的变异系数。
        """
        return self.get_coefficient_of_variation()


class FeatureSelectorBase(AbqPostExtensionBase):
    def __init__(self, name, *args, **kwargs):
        """
        初始化 FeatureCalculatorBase 类的实例。

        :param name: 特征名称。
        :type name: str
        """
        super(FeatureSelectorBase, self).__init__(name=name, *args, **kwargs)
        check_type(name, str, None)

    def process_each_value(self, value, item=None):
        """
        处理单个输入值及其对应的索引。

        该方法用于处理传入的单个数值，并根据需要更新内部状态。如果提供了 `item` 参数，它将用于在获取最终结果时返回与结果值相关的额外信息。

        :param item: 可选参数，可以是管理 `value` 值的对象的引用或 `value` 的索引。用于在获取最终结果时返回结果值与相关联的其他信息。
        :param value: 输入的数值，用于比较以选择特征点。
        """
        raise NotImplementedError()

    def get_result_value_with_item(self):
        """
        获取最终的选择结果。

        :return: 包含两项，分别是最终选择的值及其对应的索引或其他相关信息。
        :rtype: tuple[Any,Any]
        """
        raise NotImplementedError()


class ExtremaValueSelector(FeatureSelectorBase):
    """
    选择最值(最大值或最小值)的特征选择器。

    该类用于遍历一系列值，找到其中的最值（或绝对值最值），并记录其索引。
    """

    def __init__(self, name=None, select_type="MAX", if_compare_abs=True):
        """
        初始化 ExtremaValueSelector 实例。

        :param if_compare_abs: 是否比较绝对值，默认为 True。
        :type if_compare_abs: bool
        :param select_type: 选择类型，可以是 "MAX"（获取最大值）或 "MIN"（获取最小值），默认为 "MAX"。
        :type select_type: str
        """
        super(ExtremaValueSelector, self).__init__(name)
        check_type(if_compare_abs, bool)
        check_type(select_type, str)
        if select_type != "MAX" and select_type != "MIN":
            raise ValueError("select_type must be 'MAX' or 'MIN'")
        self._select_type = select_type
        self._if_compare_abs = if_compare_abs
        self._extrema_value = None
        self._extrema_value_item = None
        if name is None:
            name = self._init_default_name()
        else:
            check_type(name, str)
        self._name = name

    def _init_default_name(self):
        """
        初始化默认的名称。

        :return: 默认的名称。
        """
        name = ""
        if self._if_compare_abs:
            name += "Abs "
        if self._select_type == "MAX":
            name += "Max "
        elif self._select_type == "MIN":
            name += "Min "
        return "{}value".format(name)

    def process_each_value(self, value, item=None):
        """
        处理每个值并根据选择类型更新极值信息。

        本函数根据实例变量_if_compare_abs决定是否取值的绝对值，
        然后根据_select_type决定是寻找最大值还是最小值，并更新相应的极值和关联项。

        :param value: 要处理的值。
        :param item: 与值关联的项（默认为None）。
        :return: 无返回值。
        """
        if self._if_compare_abs:
            value = abs(value)
        if self._select_type == "MAX":
            if self._extrema_value is None or value > self._extrema_value:
                self._extrema_value = value
                self._extrema_value_item = item
        elif self._select_type == "MIN":
            if self._extrema_value is None or value < self._extrema_value:
                self._extrema_value = value
                self._extrema_value_item = item

    def get_result_value_with_item(self):
        """
        获取结果值及其对应的项

        此方法返回一个元组，包含两个属性：
        - self._extrema_value: 存储的极值
        - self._extrema_value_item: 与极值相关联的项

        :return: 包含极值和对应项的元组
        :rtype: tuple[Any,Any]
        """
        return self._extrema_value, self._extrema_value_item


class FieldOutputDataAnalyzerBase(FrameHandlerBase):
    REAL_TYPE = "real"
    FIRST_FRAME_TYPE = "first_frame_relate"
    SUPPORT_TYPE = "support_relate"

    def __init__(self, field_output_type, packaged_meshes_selector, support_packaged_meshes_handler=None,
                 data_relative_type=None, feature_algorithm=None, data_attribute_names=None, if_load_data=True, *argus,
                 **kwargs):
        """
        构造函数，用于初始化FieldOutputDataAnalyzerBase对象。

        :param field_output_type: 要获取的场输出的类型，"U"或"S"或“A”或其他支持的类型。
        :type field_output_type: str
        :param packaged_meshes_selector: 获取几何odb单元或节点的对象
        :type packaged_meshes_selector: PackagedMeshObjectsHandlerBase
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
        """
        super(FieldOutputDataAnalyzerBase, self).__init__(
            field_output_type, packaged_meshes_selector, data_attribute_names, if_load_data, *argus, **kwargs)
        self._feature_algorithm = self._init_feature_algorithm(feature_algorithm)
        self._data_attribute_names = self._init_a_feature_algorithm(
            feature_algorithm).keys()  # 更新_data_attribute_names属性
        self._relative_datas = None
        if data_relative_type is None:
            data_relative_type = self.REAL_TYPE
        else:
            if data_relative_type not in [self.REAL_TYPE, self.FIRST_FRAME_TYPE, self.SUPPORT_TYPE]:
                raise ValueError("data_relative_type must be '{}','{}','{}'".format(
                    self.REAL_TYPE, self.FIRST_FRAME_TYPE, self.SUPPORT_TYPE))
        self._data_relative_type = data_relative_type
        check_type(support_packaged_meshes_handler, PackagedMeshObjectsSelectorBase, None)
        self._support_packaged_meshes_handler = support_packaged_meshes_handler
        if self._data_relative_type == self.SUPPORT_TYPE:
            if self._support_packaged_meshes_handler is None:
                raise ValueError("if data_relative_type is '{}', support_packaged_meshes_handler must be not None".
                                 format(self.SUPPORT_TYPE))

        self.__if_save_all_field_value_datas = False
        self.__save_all_field_value_datas_folder_path = None
        self.__save_all_field_value_datas_attribute_names_dict = None
        self.__save_all_field_value_datas_file_name = None
        self.__save_all_field_value_datas_auto_save_num = None
        self.__if_first_save_all_field_value_datas = True
        self.__datas_to_save_all_field_value_datas = []
        self.__save_add_datas_thread = None

    @property
    def _support_packaged_set(self):
        """
        获取支持打包集。

        本方法尝试获取与特定字段输出类型相关联的支持打包集。
        如果未设置必要的打包集处理程序，将引发异常。
        如果找到的支持打包集为空，也会引发异常。

        :return: 支持的打包集。
        :rtype: PackagedSet
        :raises NotImplementedError: 如果未设置 _support_packaged_meshes_handler 属性。
        :raises ValueError: 如果找不到任何支持的打包集。
        """
        # 检查是否设置了支持打包网格处理程序
        if self._support_packaged_meshes_handler is None:
            raise NotImplementedError(
                "PackagedMeshesHandler object is not set for the _support_packaged_meshes_handler property "
                "to set support meshes")
        # 通过字段输出类型获取支持的打包集
        support_packaged_set = self._support_packaged_meshes_handler.get_set_by_field_output_type(
            self.field_output_type)
        # 检查支持的打包集是否为空
        if support_packaged_set.length == 0:
            raise ValueError("No support meshes found at:'{}'".format(self._support_packaged_meshes_handler))
        # 返回支持的打包集
        return support_packaged_set

    def _init_feature_algorithm(self, feature_algorithm):
        """
        初始化特征算法。

        该方法根据输入的实例化方法参数的特征算法参数来初始化self._feature_algorithm属性（在实例化方法中自动调用）。
        它是一个抽象方法，意味着在子类中必须被重写以实现具体的特征算法初始化逻辑。

        :param feature_algorithm: 特征算法的相关参数或配置。该参数的具体类型和内容取决于所使用的特定特征算法。
        :return: 该方法没有返回值，但可能会通过设置实例变量或调用其他方法来间接产生效果。
        """
        raise NotImplementedError()

    def _init_a_feature_algorithm(self, feature_algorithm):
        """
        初始化特征算法。

        该方法根据提供的特征算法参数，初始化一个新的特征算法对象。如果参数是一个字典，
        则遍历字典的键值对，检查并复制每个值到新的有序字典中。如果参数不是字典，则根据其是否为None
        进行不同处理，最终生成一个包含默认或指定算法的有序字典。

        :param feature_algorithm: 特征算法参数，可以是字典、None或特征计算/选择器基类的实例。
        :return: 初始化后的特征算法对象，以有序字典形式（键为属性名称，值为算法对象的列表）返回。
        :rtype: OrderedDict[str, list[FeatureCalculatorBase | FeatureSelectorBase]]
        """
        try:
            # 检查condition参数类型，并对其进行处理
            if isinstance(feature_algorithm, dict):
                new_feature_algorithm = OrderedDict()
                # 如果condition是字典，遍历其键值对
                for key, value in feature_algorithm.items():
                    new_feature_algorithm[key] = []
                    check_type(key, str)  # 检查键的类型是否为字符串
                    if isinstance(value, (list, tuple)):
                        # 如果值是列表或元组，检查其中元素的类型
                        for index, a_value in enumerate(value):
                            check_type(a_value, FeatureCalculatorBase, FeatureSelectorBase)
                            new_feature_algorithm[key].append(copy.deepcopy(a_value))
                    else:
                        # 如果值不是列表或元组，检查其类型并将其包装成列表
                        check_type(value, FeatureCalculatorBase, FeatureSelectorBase)
                        new_feature_algorithm[key] = [copy.deepcopy(value)]
            else:
                # 如果condition不是字典，根据其是否为None进行不同处理
                if feature_algorithm is None:
                    algorithm = ExtremaValueSelector()  # 如果为None，使用默认选项创建ExtremaValueSelector对象
                else:
                    check_type(feature_algorithm, FeatureCalculatorBase, FeatureSelectorBase)
                    algorithm = copy.deepcopy(feature_algorithm)
                new_feature_algorithm = OrderedDict(
                    (attribute_name, [copy.deepcopy(algorithm)]) for attribute_name in
                    self.data_attribute_names)
        except TypeError as e:
            raise TypeError("The type of feature_algorithm is not correct: {}".format(e))
        return new_feature_algorithm

    @staticmethod
    def _update_a_feature_algorithm_dict(feature_algorithm_dict, field_value_item, if_get_relative_datas=True):
        """
        更新特征算法字典中的每个特征算法对象。

        本函数根据特征算法字典中的每个特征算法对象的类型（特征选择器或特征计算器），
        调用其处理函数，以更新或计算特征值。

        :param feature_algorithm_dict: 包含特征算法对象的字典，键为特征属性名，值为特征算法对象列表。
        :type feature_algorithm_dict: OrderedDict[str, list[FeatureCalculatorBase | FeatureSelectorBase]]
        :param field_value_item: 包含场输出数据值的项目，用于更新所有属性名称下的所有特征算法对象。
        :type field_value_item: PackagedFieldValue|PackagedElementFieldValue
        :param if_get_relative_datas: 是否获取相对数据，默认为True。
        :type if_get_relative_datas: bool
        :return: 无返回值。
        """
        # 遍历特征算法字典，更新每个特征算法对象
        for attribute_name, feature_algorithms in feature_algorithm_dict.items():
            # 根据是否获取相对数据的标志，选择合适的方法获取字段值数据
            if if_get_relative_datas:
                field_value_data = field_value_item.get_relative_data(attribute_name)
            else:
                field_value_data = get_nested_attribute(field_value_item, attribute_name)
            if field_value_data is None:
                raise ValueError("Current output type: '{}', value: '{}', is None".format(
                    field_value_item.field_output_type, attribute_name))
            # 遍历当前特征属性对应的特征算法列表
            for feature_algorithm in feature_algorithms:
                # 如果算法是特征选择器类型，调用其处理函数并传入当前字段值和全局索引
                if isinstance(feature_algorithm, FeatureSelectorBase):
                    feature_algorithm.process_each_value(field_value_data, field_value_item)
                # 如果算法是特征计算器类型，调用其处理函数并传入当前字段值
                elif isinstance(feature_algorithm, FeatureCalculatorBase):
                    feature_algorithm.process_each_value(field_value_data)

    def _update_feature_algorithms(self, current_packaged_frame, current_field_values_manager):
        """
        更新特征算法。

        :param current_packaged_frame: (PackagedFrame): 当前的封装帧对象。
        :type current_packaged_frame: PackagedFrame
        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        :return:
        """
        raise NotImplementedError

    def set_save_all_field_value_datas(
            self, if_save=False, file_name=None, folder_path=None, field_value_data_attribute_names_dict=None,
            auto_save_num=1000):
        """
        设置保存所有字段值数据的参数。

        本函数用于配置保存字段值数据的相关参数，包括文件名、保存路径、是否保存、字段值数据的属性名称字典和自动保存的数量。

        :param file_name: 指定保存文件的名称，默认为"all_field_value_datas.txt"。
        :param folder_path: 指定保存文件的文件夹路径，默认为当前工作目录。
        :param if_save: 布尔值，指示是否保存数据。
        :param field_value_data_attribute_names_dict: 字典，包含字段值数据的属性名称映射。
        :param auto_save_num: 整数，表示自动保存的阈值数量(即读取到多少个场输出数据时保存一次，根据需要的内存占用即运行效率调整)，默认为1000。
        """
        # 设置保存数据的文件夹路径，如果未指定则使用当前工作目录
        if folder_path is None:
            folder_path = os.getcwd()
        else:
            # 检查文件夹路径类型是否为字符串
            check_type(folder_path, str)
        # 设置保存数据的文件名，如果未指定则使用默认文件名
        if file_name is None:
            if self._data_relative_type == self.REAL_TYPE:
                relative_type_str = "real_"
            elif self._data_relative_type == self.FIRST_FRAME_TYPE:
                relative_type_str = "first_frame_relative_"
            else:
                relative_type_str = "support_relative_"
            name_prefix = self.name if self.name else "all_field_value"
            file_name = "name_prefix_{}datas.txt".format(relative_type_str)
        else:
            # 检查文件名类型是否为字符串
            check_type(file_name, str)
        # 检查是否保存数据的标志类型是否为布尔值
        check_type(if_save, bool)
        # 设置是否保存所有字段值数据的标志
        self.__if_save_all_field_value_datas = if_save
        # 设置字段值数据的属性名称字典，如果未提供则使用默认字典
        if field_value_data_attribute_names_dict is None:
            field_value_data_attribute_names_dict = self.default_all_field_value_attribute_names_dict
        else:
            # 检查字段值数据属性名称字典类型是否为字典
            check_type(field_value_data_attribute_names_dict, dict)
        # 检查自动保存数量的类型是否为整数
        check_type(auto_save_num, int)
        # 设置保存所有字段值数据的文件夹路径
        self.__save_all_field_value_datas_folder_path = folder_path
        # 设置保存所有字段值数据的属性名称字典
        self.__save_all_field_value_datas_attribute_names_dict = field_value_data_attribute_names_dict
        # 设置保存所有字段值数据的文件名
        self.__save_all_field_value_datas_file_name = file_name
        # 设置自动保存的阈值数量
        self.__save_all_field_value_datas_auto_save_num = auto_save_num

    def _auto_save_all_field_value_datas(self, current_field_values_manager):
        """
        自动保存当前帧中指定对象的所有场输出数据到文件。

        该方法根据当前场输出数据管理器中的数据，自动将所有场输出数据保存到指定的文件中。
        它会检查是否需要保存所有场输出数据，如果是，则遍历当前场输出数据管理器中的每个项目，
        获取其场输出数据属性，并根据情况将其写入文件。

        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        """
        if self.__if_save_all_field_value_datas:
            def write_list_to_file():
                with ExtendedFile("a", self.__save_all_field_value_datas_file_name,
                                  self.__save_all_field_value_datas_folder_path) as file:
                    file.write_multidimensional_list(self.__datas_to_save_all_field_value_datas)
                self.__datas_to_save_all_field_value_datas = []

            for packaged_item in current_field_values_manager.get_every_managed_item():
                datas_dict = self.get_field_value_attributes(
                    packaged_item, self.__save_all_field_value_datas_attribute_names_dict)
                if packaged_item.if_set_relative_packaged_field_value:
                    # 初始化一个有序字典来存储相对数据
                    relative_datas = OrderedDict()
                    # 遍历默认字段值数据属性名称字典，计算并存储相对数据
                    for k, v in self.default_field_value_data_attribute_names_dict.items():
                        relative_datas["Relative " + k] = packaged_item.get_relative_data(v)
                    # 更新字典，添加相对数据
                    datas_dict.update(relative_datas)
                if self.__if_first_save_all_field_value_datas:
                    self.__datas_to_save_all_field_value_datas.append(list(datas_dict.keys()))
                    with ExtendedFile("w", self.__save_all_field_value_datas_file_name,
                                      self.__save_all_field_value_datas_folder_path) as file:
                        file.write_multidimensional_list(self.__datas_to_save_all_field_value_datas)
                    self.__datas_to_save_all_field_value_datas = []
                    self.__if_first_save_all_field_value_datas = False
                self.__datas_to_save_all_field_value_datas.append(list(datas_dict.values()))
                # 检查待保存的数据量是否达到了自动保存的阈值
                if len(self.__datas_to_save_all_field_value_datas) >= self.__save_all_field_value_datas_auto_save_num:
                    # 如果有未完成的保存线程，等待其完成
                    if self.__save_add_datas_thread is not None:
                        self.__save_add_datas_thread.join()
                    # 创建并启动新线程以写入数据到文件
                    self.__save_add_datas_thread = threading.Thread(target=write_list_to_file)
                    self.__save_add_datas_thread.start()

    def _end_save_all_field_value_datas(self):
        """
        结束保存所有字段值的数据。
        此方法用于检查是否需要保存字段值数据，如果需要且有待保存的数据，则将其保存到指定的文件中。

        :return:  None
        """
        if self.__if_save_all_field_value_datas:
            if self.__save_add_datas_thread is not None:
                self.__save_add_datas_thread.join()
                self.__save_add_datas_thread = None
            if len(self.__datas_to_save_all_field_value_datas) > 0:
                with ExtendedFile(
                        "a", self.__save_all_field_value_datas_file_name,
                        self.__save_all_field_value_datas_folder_path) as file:
                    file.write_multidimensional_list(self.__datas_to_save_all_field_value_datas)

    def handle_frame(self, current_packaged_frame, current_field_output_values, current_field_values_manager):
        """
        处理单个封装帧与这一帧下的指定类型的场输出值对象的方法。

        本方法依据_data_relative_type的值，选择不同的处理方法来处理当前帧。本方法不接受任何参数，也不返回任何值。

        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        :param current_packaged_frame: (PackagedFrame): 当前的封装帧对象。
        :type current_packaged_frame: PackagedFrame
        :param current_field_output_values: 指定场输出类型的当前场输出值对象。
        :type current_field_output_values: PackagedFieldOutputValues
        """
        if self._data_relative_type == self.REAL_TYPE:
            return self.handle_frame_analysis_real_field_values(
                current_packaged_frame, current_field_output_values, current_field_values_manager)
        elif self._data_relative_type == self.FIRST_FRAME_TYPE:
            return self.handle_frame_analysis_first_frame_relative_field_values(
                current_packaged_frame, current_field_output_values, current_field_values_manager)
        elif self._data_relative_type == self.SUPPORT_TYPE:
            return self.handle_frame_analysis_support_relative_field_values(
                current_packaged_frame, current_field_output_values, current_field_values_manager)

    def end_handle(self):
        """
        结束帧之后处理的方法。
        此方法在结束帧处理时释放资源，并保存自动保存场输出值过程中未保存的场输出值的数据。

        本方法主要用于清理不再需要的数据，通过将_relative_datas设置为None来释放资源，
        并调用_end_save_all_field_value_datas方法来保存数据。
        """
        self._relative_datas = None
        self._end_save_all_field_value_datas()

    def handle_frame_analysis_real_field_values(
            self, current_packaged_frame, current_field_output_values, current_field_values_manager):
        """
        将所有帧的所有真实场输出数据依次传入各特征值算法中，分析数据集。

        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        :param current_packaged_frame: (PackagedFrame): 当前的封装帧对象。
        :type current_packaged_frame: PackagedFrame
        :param current_field_output_values: 指定场输出类型的当前场输出值对象。
        :type current_field_output_values: PackagedFieldOutputValues
        :return: 控制帧遍历行为的消息
        :rtype: str | None
        """
        self._update_feature_algorithms(current_packaged_frame, current_field_values_manager)
        self._auto_save_all_field_value_datas(current_field_values_manager)

    def handle_frame_analysis_first_frame_relative_field_values(
            self, current_packaged_frame, current_field_output_values, current_field_values_manager):
        """
        将所有帧的所有相对第零帧的场输出数据依次传入各特征值算法中，分析数据集。

        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        :param current_packaged_frame: (PackagedFrame): 当前的封装帧对象。
        :type current_packaged_frame: PackagedFrame
        :param current_field_output_values: 指定场输出类型的当前场输出值对象。
        :type current_field_output_values: PackagedFieldOutputValues
        :return: 控制帧遍历行为的消息
        :rtype: str | None
        """
        if self._relative_datas is None:
            self._relative_datas = current_field_values_manager
            self._relative_datas.load_generated_packaged_items(attribute_names=self.data_attribute_names)
        current_field_values_manager.set_managed_relative_data(self._relative_datas)
        self._update_feature_algorithms(current_packaged_frame, current_field_values_manager)
        self._auto_save_all_field_value_datas(current_field_values_manager)

    def _creat_field_value_object(self, field_values_manager):
        """
        创建并返回一个包装后的字段值对象。

        根据数据属性名称加载打包项目，并根据场输出数据类型决定创建的字段值对象类型。
        计算并设置这些字段值对象的平均属性值。

        :param field_values_manager: 字段值管理器对象，用于加载和管理字段值数据
        :type field_values_manager: FieldValuesManager
        :return: 一个包装后的字段值对象，包含计算出的平均属性值
        """
        # 加载数据属性名称对应的打包项目
        field_values_manager.load_generated_packaged_items(attribute_names=self.data_attribute_names)
        # 计算支座值
        if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
            support_field_value = PackagedFieldValue()
        else:
            support_field_value = PackagedElementFieldValue()

        # 初始化属性字典
        attributes = {}
        # 遍历所有数据属性名称，包括默认的和自定义的
        for attribute_name in set(self.data_attribute_names + self.default_data_attribute_names):
            # 获取指定属性名称的列表
            support_data_list = field_values_manager.get_specified_attribute_list(attribute_name)
            # 计算列表平均值并存储到属性字典中
            attributes[attribute_name] = sum(support_data_list) / len(support_data_list)

        # 设置字段值对象的属性
        support_field_value.set_attributes(**attributes)
        # 返回计算后的字段值对象
        return support_field_value

    def handle_frame_analysis_support_relative_field_values(
            self, current_packaged_frame, current_field_output_values, current_field_values_manager):
        """
        将所有帧的所有相对支座的场输出数据依次传入各特征值算法中，分析数据集。

        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        :param current_packaged_frame: (PackagedFrame): 当前的封装帧对象。
        :type current_packaged_frame: PackagedFrame
        :param current_field_output_values: 指定场输出类型的当前场输出值对象。
        :type current_field_output_values: PackagedFieldOutputValues
        :return: 控制帧遍历行为的消息
        :rtype: str | None
        """
        support_field_values_manager = current_field_output_values.get_packaged_field_values_manager_by_set(
            self._support_packaged_set)
        support_field_value = self._creat_field_value_object(support_field_values_manager)
        current_field_values_manager.set_managed_relative_data(support_field_value)
        self._update_feature_algorithms(current_packaged_frame, current_field_values_manager)
        self._auto_save_all_field_value_datas(current_field_values_manager)

    SECT_TYPE = "sect"
    CALC_TYPE = "calc"

    def _creat_a_sect_algorithm_dict(self, feature_algorithm, attribute_type, other_info=None):
        """
        创建一个选择算法字典。

        该方法用于根据特征选择算法和属性类型，创建一个有序字典，用于存储和组织特征的相关信息。
        子类可修改此方法以使_generate_datas_dict_from_a_feature_algorithms()方法生成选择出的特征值的结果的不同格式。

        :param feature_algorithm: 特征选择算法实例，必须是FeatureSelectorBase的子类。
        :param attribute_type: 特征的属性类型，用于描述特征的某种属性。
        :param other_info: 其他信息，子类修改生成数据的格式时可能会用到。
        :return: 一个OrderedDict实例，包含特征的属性类型、名称、值以及可能的相对值等信息。
        """
        # 确保feature_algorithm是FeatureSelectorBase的子类实例
        check_type(feature_algorithm, FeatureSelectorBase)
        # 初始化一个有序字典来存储特征的相关信息
        datas_dict = OrderedDict()
        # 存储数据的属性类型
        datas_dict["Attribute type"] = attribute_type
        # 存储特征名称
        datas_dict["Feature name"] = feature_algorithm.name
        # 获取特征的值和对应的项
        field_value_data, field_value_item = feature_algorithm.get_result_value_with_item()
        # 存储特征值
        datas_dict["Feature value"] = field_value_data
        # 更新字典，添加特征值的其他属性
        datas_dict.update(self.get_field_value_attributes(field_value_item))
        # 如果设置了相对打包字段值，计算并存储相对数据
        if field_value_item.if_set_relative_packaged_field_value:
            # 初始化一个有序字典来存储相对数据
            relative_datas = OrderedDict()
            # 遍历默认字段值数据属性名称字典，计算并存储相对数据
            for k, v in self.default_field_value_data_attribute_names_dict.items():
                relative_datas["Relative " + k] = field_value_item.get_relative_data(v)
            # 更新字典，添加相对数据
            datas_dict.update(relative_datas)
        # 返回填充好的有序字典
        return datas_dict

    def _creat_a_calc_algorithm_dict(self, feature_algorithm, attribute_type, other_info=None):
        """
        创建一个计算算法字典。

        该方法用于根据给定的特征计算算法和属性类型，创建一个有序字典，
        用于存储计算结果和相关元数据。
        子类可修改此方法以使_generate_datas_dict_from_a_feature_algorithms()方法生成的计算出的特征值的结果的不同格式。

        :param feature_algorithm: 特征计算算法实例，必须是FeatureCalculatorBase的子类。
        :param attribute_type: 属性类型，表示所计算特征的类型。
        :param other_info: 其他信息，子类修改生成数据的格式时可能会用到。
        :return: 一个OrderedDict实例，包含属性类型、特征名称和特征值。
        """
        # 确保传入的feature_algorithm是FeatureCalculatorBase的子类
        check_type(feature_algorithm, FeatureCalculatorBase)
        # 初始化一个有序字典用于存储计算算法的相关信息
        datas_dict = OrderedDict()
        # 存储数据的属性类型
        datas_dict["Attribute type"] = attribute_type
        # 存储特征名称
        datas_dict["Feature name"] = feature_algorithm.name
        # 存储特征计算结果
        datas_dict["Feature value"] = feature_algorithm.get_result_data()
        # 存储场输出类型
        datas_dict["Field Output Type"] = self.field_output_type
        # 返回填充了相关信息的字典
        return datas_dict

    def _generate_datas_dict_from_a_feature_algorithms(
            self, generate_type, feature_algorithms, customize_data_attribute_names=None, other_info=None):
        """
        根据特征算法生成数据字典。

        本函数旨在根据提供的特征工程算法（包括特征选择和特征计算算法）生成一个有序字典，
        该字典包含数据的信息。根据generate_type的值，本函数将执行不同的逻辑。

        :param generate_type: 生成数据的类型，必须为 “sect”（类常量SECT_TYPE） 或 "calc"（类常量CALC_TYPE）。
            - “sect”（类常量SECT_TYPE）：获取由FeatureCalculatorBase定义的计算特征值方法得到的特征值结果。
            - "calc"（类常量CALC_TYPE）：获取由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据。
        :type generate_type: str
        :param feature_algorithms:包含特征工程算法的字典，键为属性名，值为算法列表。
        :type feature_algorithms: OrderedDict[str, list[FeatureCalculatorBase | FeatureSelectorBase]]
        :param customize_data_attribute_names: 自定义属性名称列表，用于输出数据时为数据项的名称提供自定义的标识，
            长度需与对象中设置的数据属性名称列表相同。默认采用类中定义的标识字典。
        :type customize_data_attribute_names: list[str]|None
        :return: 一个生成器，每次迭代产生一个包含数据信息的OrderedDict对象。
        :param other_info: 其他信息，子类修改生成数据的格式时可能会用到。
        :rtype: Generator[OrderedDict[str, any]]
        """

        def front_insert_data_dict(datas_dict):
            """
            在数据字典中添加前缀信息，如“Meshes name”，并返回新的数据字典。
            """
            new_datas_dict = OrderedDict()
            meshes_name = self._packaged_meshes_handler.name
            if meshes_name is not None:
                new_datas_dict["Meshes name"] = meshes_name
            new_datas_dict.update(datas_dict)
            return new_datas_dict

        # 检查generate_type是否为0或1，如果不是，抛出异常
        if generate_type not in [self.SECT_TYPE, self.CALC_TYPE]:
            raise ValueError("generate_type must be '{}' or '{}'".format(self.SECT_TYPE, self.CALC_TYPE))
        # 验证自定义数据属性名称，确保它们是有效的
        customize_data_attribute_names = self._verify_customize_attribute_names(customize_data_attribute_names)
        # 遍历特征算法字典，生成数据字典
        for i, (attribute_name, feature_algorithms_list) in enumerate(feature_algorithms.items()):
            # 初始化一个有序字典，用于存储数据信息
            for feature_algorithm in feature_algorithms_list:
                datas_dict = OrderedDict()
                # 根据generate_type的不同，执行不同的逻辑
                if generate_type == self.CALC_TYPE:
                    # 如果是FeatureCalculatorBase的实例，存储计算结果
                    if isinstance(feature_algorithm, FeatureCalculatorBase):
                        if feature_algorithm.get_result_data() is None:
                            raise ValueError(
                                "The result of the feature calculation is None.It is possible that no values were "
                                "passed to the data processor during the analysis process. Please check if the current "
                                "single frame analyzer object has been added to the manager or other settings")
                        datas_dict = self._creat_a_calc_algorithm_dict(
                            feature_algorithm, customize_data_attribute_names[i], other_info)
                        yield front_insert_data_dict(datas_dict)
                elif generate_type == self.SECT_TYPE:
                    # 如果是FeatureSelectorBase的实例，存储选择的结果及其属性
                    if isinstance(feature_algorithm, FeatureSelectorBase):
                        if feature_algorithm.get_result_value_with_item()[0] is None:
                            raise ValueError(
                                "The result of the feature calculation is None.It is possible that no values were "
                                "passed to the data processor during the analysis process. Please check if the current "
                                "single frame analyzer object has been added to the manager or other settings")
                        datas_dict = self._creat_a_sect_algorithm_dict(
                            feature_algorithm, customize_data_attribute_names[i], other_info)
                        yield front_insert_data_dict(datas_dict)

    @staticmethod
    def _save_same_key_dictionary_iterator(
            dictionary_iterator, file_name, folder_path=None, covered=True, save_columns_name=None):
        """
        保存具有相同键的字典迭代器到文件中。

        :param dictionary_iterator: 一个生成字典的迭代器，所有字典具有相同的键
        :type dictionary_iterator: Generator[dict[str, any]]
        :param covered: 布尔值，指示是否覆盖现有文件。如果为True，则覆盖文件；如果为False，则追加到文件。
        :type covered: bool
        :param save_columns_name: 是否保存列名。如果为True，则保存列名；如果为False，则不保存列名。默认为与covered相同。
        :type save_columns_name: bool | None
        :param file_name: 数据保存的文件名。如果未指定，则使用默认文件名。
        :type file_name: str | None
        :param folder_path: 数据保存的文件夹路径。如果未指定，则使用当前工作目录。
        :type folder_path: str | None
        :return:
        """
        # 如果未指定文件夹路径，则使用当前工作目录
        if folder_path is None:
            folder_path = os.getcwd()
        if save_columns_name is None:
            save_columns_name = covered
        else:
            check_type(save_columns_name, bool)
        # 检查迭代器是否为空
        try:
            first_dict = next(dictionary_iterator)
        except StopIteration:
            return
        # 根据covered参数决定文件的初始写入模式
        mode = "w" if covered else "a"
        try:
            with ExtendedFile(mode, file_name, folder_path) as file:
                # 写入第一行（列名）
                if save_columns_name:
                    file.write_multidimensional_list(list(first_dict.keys()))
                file.write_multidimensional_list(list(first_dict.values()))
                # 写入剩余的数据
                for datas_dict in dictionary_iterator:
                    file.write_multidimensional_list(list(datas_dict.values()))
        except IOError as e:
            print("File operation failed:{}".format(e))

    def generate_datas_dict(self, generate_type, customize_data_attribute_names=None):
        """
        根据特征算法生成数据字典。

        本函数旨在根据提供的特征工程算法（包括特征选择和特征计算算法）生成一个有序字典，
        该字典包含数据的信息。根据generate_type的值，本函数将执行不同的逻辑。

        :param generate_type: 生成数据的类型，必须为 “sect”（类常量SECT_TYPE） 或 "calc"（类常量CALC_TYPE）。
            - “sect”（类常量SECT_TYPE）：获取由FeatureCalculatorBase定义的计算特征值方法得到的特征值结果。
            - "calc"（类常量CALC_TYPE）：获取由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据。
        :type generate_type: str
        :param customize_data_attribute_names: 自定义属性名称列表，用于输出数据时为数据项的名称提供自定义的标识，
            长度需与对象中设置的数据属性名称列表相同。默认采用类中定义的标识字典。
        :type customize_data_attribute_names: list[str]|None
        :return: 一个生成器，每次迭代产生一个包含数据信息的OrderedDict对象。
        """
        raise NotImplementedError("This method must be implemented in subclasses.")

    def _default_creat_result_file_names(self, base_name, file_name_prefix=""):
        """
        生成默认的结果文件名。

        根据数据相对类型生成默认的sect和calc结果文件名。如果提供了文件名前缀，
        则将其添加到生成的文件名中。

        :param base_name: 文件的基本名称，用于生成默认文件名。
        :param file_name_prefix: 文件名前缀，默认为空字符串。
        :return: 包含两个字符串的元组，第一个是sect文件名，第二个是calc文件名。
        :rtype: tuple[str, str]
        """
        # 检查base_name和file_name_prefix的类型是否为str
        check_type(base_name, str)
        check_type(file_name_prefix, str)
        # 根据_data_relative_type的值确定相对类型字符串
        if self._data_relative_type == self.REAL_TYPE:
            relative_type_str = "real"
        elif self._data_relative_type == self.FIRST_FRAME_TYPE:
            relative_type_str = "first_frame_relative"
        else:
            relative_type_str = "support_relative"
        # 设置默认sect文件名或检查传入的文件名类型
        sect_file_name = "{}{}_sect_{}_datas.txt".format(
            file_name_prefix, base_name, relative_type_str)
        # 设置默认calc文件名或检查传入的文件名类型
        calc_file_name = "{}{}_calc_{}_datas.txt".format(
            file_name_prefix, base_name, relative_type_str)
        # 返回生成的sect和calc文件名
        return sect_file_name, calc_file_name

    def save_datas(
            self, sect_file_name, calc_file_name, file_name_prefix="", folder_path=None, covered=True,
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
        :type sect_file_name: str
        :param calc_file_name: 由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据数据保存的文件名。
        :type calc_file_name: str
        :param folder_path: 数据保存的文件夹路径。如果未指定，则使用当前工作目录。
        :type folder_path: str | None
       :return:
       """
        check_type(sect_file_name, str)
        check_type(calc_file_name, str)
        # 生成sect数据字典
        sect_datas_generator = self.generate_datas_dict(generate_type=self.SECT_TYPE)
        # 检查是否有数据，以及获取处理后的数据生成器
        self._save_same_key_dictionary_iterator(
            sect_datas_generator, sect_file_name, folder_path, covered, save_columns_name)
        # 生成calc数据字典并重复上述过程
        calc_datas_generator = self.generate_datas_dict(generate_type=self.CALC_TYPE)
        self._save_same_key_dictionary_iterator(
            calc_datas_generator, calc_file_name, folder_path, covered, save_columns_name)


class AllFrameAllFieldValueAnalyzer(FieldOutputDataAnalyzerBase):
    def __init__(self, field_output_type, packaged_meshes_selector, support_packaged_meshes_handler=None,
                 data_relative_type=None, feature_algorithm=None, data_attribute_names=None, if_load_data=True, *argus,
                 **kwargs):
        """
        初始化全帧全节点/单元帧分析器AllFrameAllFieldValueAnalyzer，用于分析所有帧中指定网格对象的场输出数据特征值。

        该分析器会对packaged_meshes_handler参数指定的所有节点/单元的场输出数据，
        执行feature_algorithm参数指定的特征值处理算法。

        :param field_output_type: 要获取的场输出的类型，"U"或"S"或“A”或其他支持的类型。
        :type field_output_type: str
        :param packaged_meshes_selector: 获取几何odb单元或节点的对象
        :type packaged_meshes_selector: PackagedMeshObjectsHandlerBase
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
        """
        super(AllFrameAllFieldValueAnalyzer, self).__init__(
            field_output_type, packaged_meshes_selector,support_packaged_meshes_handler,data_relative_type,
            feature_algorithm,data_attribute_names, if_load_data, *argus, **kwargs)
    def _init_feature_algorithm(self, feature_algorithm):
        """
        初始化特征算法。

        该方法根据提供的特征算法参数，初始化一个新的特征算法对象。如果参数是一个字典，
        则遍历字典的键值对，检查并复制每个值到新的有序字典中。如果参数不是字典，则根据其是否为None
        进行不同处理，最终生成一个包含默认或指定算法的有序字典。

        :param feature_algorithm: 特征算法参数，可以是字典、None或特征计算/选择器基类的实例。
        :return: 初始化后的特征算法对象，以有序字典形式（键为属性名称，值为算法对象的列表）返回。
        :rtype: OrderedDict[str, list[FeatureCalculatorBase | FeatureSelectorBase]]
        """
        return self._init_a_feature_algorithm(feature_algorithm)

    def _update_feature_algorithms(self, current_packaged_frame, current_field_values_manager):
        """
        更新特征算法。

        遍历每个字段值字典，根据数据属性名称生成的每个指定属性字典，
        对于每个属性名和对应的特征算法，根据算法类型执行相应的处理过程。

        :param current_field_values_manager: 当前字段值管理器，用于管理和访问字段值。
        :return:
        """
        for field_value_item in current_field_values_manager.get_every_managed_item():
            self._update_a_feature_algorithm_dict(self._feature_algorithm, field_value_item)

    def generate_datas_dict(self, generate_type, customize_data_attribute_names=None):
        """
        根据特征算法生成数据字典。

        本函数旨在根据提供的特征工程算法（包括特征选择和特征计算算法）生成一个有序字典，
        该字典包含数据的信息。根据generate_type的值，本函数将执行不同的逻辑。

        :param generate_type: 生成数据的类型，必须为 “sect”（类常量SECT_TYPE） 或 "calc"（类常量CALC_TYPE）。
            - “sect”（类常量SECT_TYPE）：获取由FeatureCalculatorBase定义的计算特征值方法得到的特征值结果。
            - "calc"（类常量CALC_TYPE）：获取由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据。
        :type generate_type: str
        :param customize_data_attribute_names: 自定义属性名称列表，用于输出数据时为数据项的名称提供自定义的标识，
            长度需与对象中设置的数据属性名称列表相同。默认采用类中定义的标识字典。
        :type customize_data_attribute_names: list[str]|None
        :return: 一个生成器，每次迭代产生一个包含数据信息的OrderedDict对象。
        :rtype: Generator[OrderedDict[str, any]]
        """
        return self._generate_datas_dict_from_a_feature_algorithms(
            generate_type, self._feature_algorithm, customize_data_attribute_names)

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
            如果未指定，则使用默认文件名"all_frame_all_field_values_calc_datas.txt"。
        :type sect_file_name: str  | None
        :param calc_file_name: 由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据数据保存的文件名。
            如果未指定，则使用默认文件名"all_frame_all_field_values_sect_datas.txt"。
        :type calc_file_name: str | None
        :param folder_path: 数据保存的文件夹路径。如果未指定，则使用当前工作目录。
        :type folder_path: str | None
       :return:
       """
        check_type(file_name_prefix, str)
        base_name = self.name if self.name else "all_frame_all_field_feature_values"
        auto_sect_file_name, auto_calc_file_name = self._default_creat_result_file_names(
            base_name=base_name, file_name_prefix=file_name_prefix)
        sect_file_name = auto_sect_file_name if sect_file_name is None else sect_file_name
        calc_file_name = auto_calc_file_name if calc_file_name is None else calc_file_name
        super(AllFrameAllFieldValueAnalyzer, self).save_datas(
            sect_file_name, calc_file_name, file_name_prefix, folder_path, covered, save_columns_name)


class SpecifyFieldHistoryValueAnalyzer(FieldOutputDataAnalyzerBase):
    def __init__(self, field_output_type, packaged_meshes_selector, support_packaged_meshes_handler=None,
                 data_relative_type=None, feature_algorithm=None, data_attribute_names=None, if_load_data=True, *argus,
                 **kwargs):
        """
        初始化指定节点/单元时程分析器SpecifyFieldHistoryValueAnalyzer，用于分析指定节点/单元时程数据的特征值。

        该分析器会对packaged_meshes_handler参数指定的每一个节点/单元的场输出时程数据，
        执行feature_algorithm参数指定的特征值处理算法。

        :param field_output_type: 要获取的场输出的类型，"U"或"S"或“A”或其他支持的类型。
        :type field_output_type: str
        :param packaged_meshes_selector: 获取几何odb单元或节点的对象
        :type packaged_meshes_selector: PackagedMeshObjectsHandlerBase
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
        """
        super(SpecifyFieldHistoryValueAnalyzer, self).__init__(
            field_output_type, packaged_meshes_selector,support_packaged_meshes_handler,data_relative_type,
            feature_algorithm,data_attribute_names, if_load_data, *argus, **kwargs)
    def _init_feature_algorithm(self, feature_algorithm):
        """
        初始化特征算法。

        为每个由几何选择对象指定的要分析的场输出数据项创建特征算法的深拷贝。

        :param feature_algorithm: 特征算法参数，可以是字典、None或特征计算/选择器基类的实例。
        :return: 一个包含特征算法深拷贝的列表，每个列表元素对应一个特征算法的有序字典形式（键为属性名称，值为算法对象的列表）。
        :rtype: list[OrderedDict[str, list[FeatureCalculatorBase | FeatureSelectorBase]]]
        """
        # 调用父类的方法初始化特征算法
        new_feature_algorithm = self._init_a_feature_algorithm(feature_algorithm)
        # 为每个打包的网格创建特征算法的深拷贝
        return [copy.deepcopy(new_feature_algorithm) for _ in range(len(self.get_packaged_meshes()))]

    def _update_feature_algorithms(self, current_packaged_frame, current_field_values_manager):
        """
        更新特征算法。

        本方法通过遍历当前字段值管理器中的每个管理项，逐一更新特征算法字典。

        :param current_field_values_manager: 当前字段值管理器，用于管理和访问字段值。
        :return:
        """
        for index, field_value_item in enumerate(current_field_values_manager.get_every_managed_item()):
            self._update_a_feature_algorithm_dict(self._feature_algorithm[index], field_value_item)

    def generate_datas_dict(self, generate_type, customize_data_attribute_names=None):
        """
        根据特征算法生成数据字典。

        本函数通过遍历特征与算法的列表，调用内部函数_generate_datas_dict_from_a_feature_algorithms，
        生成与特定特征和算法相关联的数据字典，并使用生成器逐一返回这些数据。

        :param generate_type: 生成数据的类型，必须为 “sect”（类常量SECT_TYPE） 或 "calc"（类常量CALC_TYPE）。
            - “sect”（类常量SECT_TYPE）：获取由FeatureCalculatorBase定义的计算特征值方法得到的特征值结果。
            - "calc"（类常量CALC_TYPE）：获取由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据。
        :type generate_type: str
        :param customize_data_attribute_names: 自定义属性名称列表，用于输出数据时为数据项的名称提供自定义的标识，
            长度需与对象中设置的数据属性名称列表相同。默认采用类中定义的标识字典。
        :type customize_data_attribute_names: list[str]|None
        :return: 一个生成器，每次迭代产生一个包含数据信息的OrderedDict对象。
        """
        # 遍历特征与算法的列表，每个元素是一个特征与算法的字典
        for index, feature_algorithm_dict in enumerate(self._feature_algorithm):
            # 调用内部函数生成数据字典，并使用生成器逐一返回这些数据
            for datas in self._generate_datas_dict_from_a_feature_algorithms(
                    generate_type, feature_algorithm_dict, customize_data_attribute_names, index):
                yield datas

    def _creat_a_calc_algorithm_dict(self, feature_algorithm, attribute_type, other_info=None):
        """
        创建一个计算算法字典。

        该方法用于根据给定的特征计算算法和属性类型，创建一个有序字典，
        用于存储计算结果和相关元数据。
        子类可修改此方法以使_generate_datas_dict_from_a_feature_algorithms()方法生成的计算出的特征值的结果的不同格式。

        :param feature_algorithm: 特征计算算法实例，必须是FeatureCalculatorBase的子类。
        :param attribute_type: 属性类型，表示所计算特征的类型。
        :return: 一个OrderedDict实例，包含属性类型、特征名称和特征值。
        """
        mesh_index = other_info
        datas_dict = super(SpecifyFieldHistoryValueAnalyzer, self)._creat_a_calc_algorithm_dict(
            feature_algorithm, attribute_type, other_info)
        datas_dict.update(self.get_field_value_attributes(
            self.get_packaged_meshes()[mesh_index], self.default_packaged_mesh_data_attribute_names_dict))
        # 返回填充了相关信息的字典
        return datas_dict

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
        :return:
        """
        check_type(file_name_prefix, str)
        base_name = self.name if self.name else "specify_field_history_feature_values"
        auto_sect_file_name, auto_calc_file_name = self._default_creat_result_file_names(
            base_name=base_name, file_name_prefix=file_name_prefix)
        sect_file_name = auto_sect_file_name if sect_file_name is None else sect_file_name
        calc_file_name = auto_calc_file_name if calc_file_name is None else calc_file_name
        super(SpecifyFieldHistoryValueAnalyzer, self).save_datas(
            sect_file_name, calc_file_name, file_name_prefix, folder_path, covered, save_columns_name)


class PerFrameFieldValueAnalyzer(FieldOutputDataAnalyzerBase):
    """
    每一帧的所有场输出数据的值分析器。
    """

    def _init_feature_algorithm(self, feature_algorithm):
        """
        需要为每一帧创建一组特征值计算器，在对象初始化时调用次方法时，因当前对象尚未获取帧信息，实际的特征值计算器将在后续设置。

        :param feature_algorithm: 特征算法的相关参数或配置。该参数的具体类型和内容取决于所使用的特定特征算法。
        :return: 该方法没有返回值，但可能会通过设置实例变量或调用其他方法来间接产生效果。
        """
        return feature_algorithm

    def start_handle(self):
        """
        初始化并复制特性算法以匹配帧的数量。

        本方法首先调用`_init_a_feature_algorithm`方法初始化一个新的特性算法实例。
        然后，通过深拷贝该实例，创建一个包含多个相同特性算法实例的列表，
        列表长度与`frame_manager`管理的帧数相匹配。

        由于self.frame_manager属性在此时才会被设置，故在此方法中实现self._feature_algorithm的每一帧特征值算法的字典列表的初始化

        :return: 该方法没有返回值，但可能会通过设置实例变量或调用其他方法来间接产生效果。
        :rtype: None
        """
        # 初始化一个新的特性算法实例
        new_feature_algorithm = self._init_a_feature_algorithm(self._feature_algorithm)

        # 深拷贝特性算法实例，以匹配帧的数量
        self._feature_algorithm = [copy.deepcopy(new_feature_algorithm) for _ in range(
            self.frame_manager.get_item_generator_length())]

    def _update_feature_algorithms(self, current_packaged_frame, current_field_values_manager):
        """
        更新特征算法。

        为self._feature_algorithm列表中的每一帧的特征计算器传入当前帧的所有场输出数据

        :param current_packaged_frame: (PackagedFrame): 当前的封装帧对象。
        :type current_packaged_frame: PackagedFrame
        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        :return:
        """
        frame_index = current_packaged_frame.manager_index
        for field_value_item in current_field_values_manager.get_every_managed_item():
            self._update_a_feature_algorithm_dict(self._feature_algorithm[frame_index], field_value_item)

    def _creat_a_calc_algorithm_dict(self, feature_algorithm, attribute_type, other_info=None):
        """
        创建一个计算算法字典。

        在父类`_creat_a_calc_algorithm_dict`方法的基础上，添加每组数据的帧信息。

        :param feature_algorithm: 特征计算算法实例，必须是FeatureCalculatorBase的子类。
        :param attribute_type: 属性类型，表示所计算特征的类型。
        :param other_info: 其他信息，子类修改生成数据的格式时可能会用到。
        :return: 一个OrderedDict实例，包含属性类型、特征名称和特征值。
        """
        frame_index = other_info
        datas_dict = super(PerFrameFieldValueAnalyzer, self)._creat_a_calc_algorithm_dict(
            feature_algorithm, attribute_type, other_info)
        datas_dict.update(self.get_field_value_attributes(
            self.frame_manager.get_packaged_item_by_index(frame_index),
            self.default_packaged_frame_data_attribute_names_dict))
        # 返回填充了相关信息的字典
        return datas_dict

    def generate_datas_dict(self, generate_type, customize_data_attribute_names=None):
        # 遍历特征与算法的列表，每个元素是一个特征与算法的字典
        for frame_index, feature_algorithm_dict in enumerate(self._feature_algorithm):
            # 调用内部函数生成数据字典，并使用生成器逐一返回这些数据
            for datas in self._generate_datas_dict_from_a_feature_algorithms(
                    generate_type, feature_algorithm_dict, customize_data_attribute_names, frame_index):
                yield datas

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
            如果未指定，则使用默认文件名"per_frame_field_feature_values_calc_datas.txt"。
        :type sect_file_name: str  | None
        :param calc_file_name: 由FeatureSelectorBase定义的特征选择方法得到的特征值点的所有数据数据保存的文件名。
            如果未指定，则使用默认文件名"per_frame_field_feature_values_sect_datas.txt"。
        :type calc_file_name: str | None
        :param folder_path: 数据保存的文件夹路径。如果未指定，则使用当前工作目录。
        :type folder_path: str | None
       :return:
       """
        check_type(file_name_prefix, str)
        base_name = self.name if self.name else "per_frame_field_feature_values"
        auto_sect_file_name, auto_calc_file_name = self._default_creat_result_file_names(
            base_name=base_name, file_name_prefix=file_name_prefix)
        sect_file_name = auto_sect_file_name if sect_file_name is None else sect_file_name
        calc_file_name = auto_calc_file_name if calc_file_name is None else calc_file_name
        super(PerFrameFieldValueAnalyzer, self).save_datas(
            sect_file_name, calc_file_name, file_name_prefix, folder_path, covered, save_columns_name)


class FieldValuesSaver(FieldOutputDataAnalyzerBase):
    def __init__(
            self, field_output_type, packaged_meshes_selector, file_name=None, folder_path=None,
            field_value_data_attribute_names_dict=None, auto_save_num=1000, support_packaged_meshes_handler=None,
            data_relative_type=None, data_attribute_names=None, *argus, **kwargs):
        """
        创建一个FieldValuesSaver对象，用于保存场输出数据。

        :param field_output_type: 要获取的场输出的类型，"U"或"S"或“A”或其他支持的类型。
        :type field_output_type: str
        :param packaged_meshes_selector: 获取几何odb单元或节点的对象
        :type packaged_meshes_selector: PackagedMeshObjectsHandlerBase
        :param support_packaged_meshes_handler: 支座的获取几何odb单元或节点的对象，要分析相对支座的值时需传入此项。
        :type support_packaged_meshes_handler: PackagedMeshObjectsHandlerBase|None
        :param data_relative_type: 数据的相对类型，可以是
            - "real"，默认值（类常量REAL_TYPE）表示分析每个数据点真实值；
            - "first_frame_relate"（类常量FIRST_FRAME_TYPE）表示分析每个数据点相对于其首帧的值；
            - "support_relate"（类常量SUPPORT_TYPE）表示分析每个数据点相对于同一帧的支座值
        :type data_relative_type: str|None
        :param data_attribute_names: 需要处理的场输出PackagedFieldValue或PackagedElementFieldValue对象的属性名称
        :type data_attribute_names: list[str]|None
        :param file_name: 指定保存文件的名称，默认为"all_field_value_datas.txt"。
        :param folder_path: 指定保存文件的文件夹路径，默认为当前工作目录。
        :param field_value_data_attribute_names_dict: 字典，包含字段值数据的属性名称映射。
        :param auto_save_num: 整数，表示自动保存的阈值数量(即读取到多少个场输出数据时保存一次，根据需要的内存占用即运行效率调整)，默认为1000。
        """

        class PassAlgorithm(FeatureCalculatorBase):
            def process_each_value(self, value):
                pass

        if_load_data = True
        feature_algorithm = PassAlgorithm("")
        super(FieldValuesSaver, self).__init__(
            field_output_type, packaged_meshes_selector, support_packaged_meshes_handler, data_relative_type,
            feature_algorithm, data_attribute_names, if_load_data, *argus, **kwargs)
        self.set_save_all_field_value_datas(
            True, file_name, folder_path, field_value_data_attribute_names_dict, auto_save_num)

    def _init_feature_algorithm(self, feature_algorithm):
        pass

    def _update_feature_algorithms(self, current_packaged_frame, current_field_values_manager):
        pass


if __name__ == "__main__":
    pass
