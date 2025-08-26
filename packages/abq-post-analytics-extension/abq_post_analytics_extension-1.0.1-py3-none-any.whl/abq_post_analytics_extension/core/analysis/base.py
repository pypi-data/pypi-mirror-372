# -*- coding: UTF-8 -*-
import time
from collections import OrderedDict

try:
    from typing import Generator
except ImportError:
    pass
import numpy as np
from abq_post_analytics_extension.utils.system_utilities import AbqPostExtensionBase
from abq_post_analytics_extension.core.access import PackagedOdb, PackagedFrame, PackagedFieldValue, \
    PackagedElementFieldValue, PackagedOdbSet, \
    FieldValuesManager, PackagedFieldOutputValues, PackagedFramesManager, PackagedNode, PackagedElement
from abq_post_analytics_extension.utils.misc_utils import omit_representation_sequence, check_type, \
    check_sequence_type, get_nested_attribute


class PackagedOdbObjects(AbqPostExtensionBase):
    """
    该类用于创建与缓存进行各种后处理操作都需要使用的各层封装ODB对象。
    执行不同的后处理操作使用一个本类对象管理的同一个封装odb对象以避免重复的比如缓存和建立索引的初始化操作。
    """

    def __init__(self, odb_path=None, step_name=None, step_index=0,
                 packaged_odb_object_factory=None, *args, **kwargs):
        """
        初始化PackagedOdbObjects实例。
        :param odb_path:  odb文件的路径，默认为None。如果未指定路径，则尝试从当前目录下查找odb文件。
        :type odb_path: str|None
        :param step_name: 需要访问的步骤的名称，可以是字符串或None。有值时覆盖step_index的设置
        :type step_name: str|None
        :param step_index: 需要访问的步骤的索引，可以是非负整数或None。None时默认为0，分析步名称或索引，至少指定一个。
        :type step_index: int|None
        :param packaged_odb_object_factory: 可选参数，用于指定一个工厂函数或对象，该工厂用于生成特定的封装ODB对象。
        :type packaged_odb_object_factory: PackagedObjectFactory
        在封装ODB对象的结构中，由上级节点创建的下级节点的对象均使用此对象指定的类，如果上级节点未设置此项则由父节点获取。
        如果再封装ODB对象的结构中要使用其他的封装ODB类对象，将修改了类映射的PackagedObjectFactory对象传入此项。
        """
        super(PackagedOdbObjects, self).__init__(*args, **kwargs)
        # 输入验证
        check_type(odb_path, str, None)
        check_type(step_name, str, None)
        check_type(step_index, int, None)
        self.packaged_odb = PackagedOdb(odb_path, packaged_odb_object_factory)
        self.packaged_root_assembly = self.packaged_odb.get_packaged_root_assembly()
        self.packaged_step = self.packaged_odb.get_packaged_step_by_name_or_index(step_name, step_index)
        self.packaged_frames = self.packaged_step.packaged_frames

    @property
    def field_output_type_constant(self):
        """
        获取场输出输出类型常量对象。管理当前分析步支持的场输出输出类型。 该属性方法用于获取或初始化场输出输出类型常量对象。

        :return: 包含有效节点类型和单元类型的场输出输出类型常量对象。
        :rtype: FieldOutputTypeConstant
        """
        return self.packaged_step.field_output_type_constant

    def close(self):
        """
        关闭封装ODB对象。结束所有子进程，释放资源

        :return:  None
        """
        self.packaged_odb.close()


class OdbAnalyzerBase(AbqPostExtensionBase):
    def __init__(self, packaged_odb_objects, *args, **kwargs):
        """
        初始化OdbReader类的构造方法。

        验证输入参数是否为PackagedOdbObjects类型，确保类型安全。

        :param packaged_odb_objects: 一个PackagedOdbObjects实例，包含封装的ODB对象。
        :type packaged_odb_objects: PackagedOdbObjects
        """
        # 使用check_type函数验证输入参数的类型，确保其为PackagedOdbObjects。
        # 这一步是必要的类型检查，以防止类型错误的输入导致的运行时错误。
        super(OdbAnalyzerBase, self).__init__(*args, **kwargs)
        check_type(packaged_odb_objects, PackagedOdbObjects)

        # 将验证后的PackagedOdbObjects实例赋值给类的成员变量，以便在类的其他方法中使用。
        self.packaged_odb_objects = packaged_odb_objects

    @property
    def field_output_type_constant(self):
        """
        获取场输出输出类型常量对象。管理当前分析步支持的场输出输出类型。 该属性方法用于获取或初始化场输出输出类型常量对象。

        :return: 包含有效节点类型和单元类型的场输出输出类型常量对象。
        :rtype: FieldOutputTypeConstant
        """
        return self.packaged_odb_objects.field_output_type_constant


class PackagedMeshObjectsSelectorBase(OdbAnalyzerBase):
    """
    PackagedMeshObjectsHandlerBase类是用于处理封装的网格对象的基础类。
    """

    def __init__(self, packaged_odb_objects, name=None):

        """
        初始化PackagedMeshObjectsHandlerBase类的构造函数。

        :param packaged_odb_objects: 一个PackagedOdbObjects实例，包含封装的ODB对象。
        :type packaged_odb_objects: PackagedOdbObjects
        :param name: 网格名称，默认为None。
        :type name: str|None
        """
        # 调用父类的构造函数进行初始化
        super(PackagedMeshObjectsSelectorBase, self).__init__(packaged_odb_objects, name)
        # 初始化_packaged_meshes属性为None，它将在子类中被初始化
        check_type(name, str, None)
        self._nodes_set = None
        self._element_set = None
        self._if_send_progress = True

    def set_if_send_progress(self, value):
        """
        设置是否发送进度，默认为True。

        :param value: 是否发送进度。
        :type value:bool
        :return: None
        """
        check_type(value, bool, None)
        self._if_send_progress = value

    def get_node_set(self):
        """
        获取并缓存封装的节点集合。

        :return: 封装的节点集合。
        :rtype: PackagedOdbSet
        """
        pass

    def get_element_set(self):
        """
        获取并缓存封装的元素集合。

        :return: 封装的元素集合。
        :rtype: PackagedOdbSet
        """
        pass

    def get_set_by_field_output_type(self, field_output_type):
        """
        根据场输出类型获取相应的节点或单元集合。

        :param field_output_type: 场输出类型，用于确定是节点场输出还是单元场输出。
        :type field_output_type: str
        :return: 无返回值，但会根据场输出类型获取相应的节点或单元集合，并在需要时发送进度信息。
        :rtype: None
        """

        # 验证输入的场输出类型序列是否为字符串类型
        check_type(field_output_type, str)

        # 记录开始时间，用于后续计算耗时
        time_0 = time.time()

        # 标记是否为首次加载
        first_load = True

        # 判断场输出类型是否为节点场输出
        if self.field_output_type_constant.determine_node_field_output_type(field_output_type):
            # 如果场输出类型是节点场输出，则获取节点集合
            meshes_type = "nodes"
            if self._nodes_set:
                first_load = False
            packaged_set = self.get_node_set()
        else:
            # 如果场输出类型是单元场输出，则获取单元集合
            meshes_type = "elements"
            if self._element_set:
                first_load = False
            packaged_set = self.get_element_set()
        # 如果需要发送进度信息且为首次加载，则发送进度信息
        if self._if_send_progress and first_load:
            self.packaged_odb_objects.packaged_odb._progress_monitor.send_progress(
                self, taken_time=time.time() - time_0,
                info=self._packaged_meshes_info_str(meshes_type, packaged_set))
        return packaged_set

    def _packaged_meshes_info_str(self, meshes_type, packaged_set):
        """
        返回当前对象的进度信息字符串，该字符串将发送到 progress_monitor 对象进行处理。

        子类需要实现该方法，以提供具体的进度信息。
        :param meshes_type: (str): 网格类型，可以是“node”或“element”。
        :type meshes_type: str
        :param packaged_set: 打包的节点或元素数据列表。
        :type packaged_set: PackagedOdbSet
        :return: 当前对象的进度信息字符串。
        :rtype: str
        """

        pass


class AllPackagedMeshObjectsSelector(PackagedMeshObjectsSelectorBase):

    def __init__(self, packaged_odb_objects, instance_name=None, set_name=None):
        """
        AllPackagedMeshObjectsHandler范围选择器类用于选择设定的实例或集合中的所有封装的odb几何单元或节点。

        根据指定的实例名称和/或集合名称获取几何odb单元或节点。具体行为如下：
        - 如果仅提供instance_name：选择该实例中的所有几何对象
        - 如果仅提供set_name：先在装配体集合中查找该集合，如果未找到则在各个实例集合中查找
        - 如果同时提供instance_name和set_name：直接获取指定实例中的指定集合

        至少需要提供instance_name或set_name中的一个参数。

        :param packaged_odb_objects: 一个PackagedOdbObjects实例，包含封装的ODB对象。
        :type packaged_odb_objects: PackagedOdbObjects
        :param instance_name: 实例名称
        :type instance_name: str|None
        :param set_name: 集合名称。实例名称或集合名称，至少指定一个。
        :type set_name: str|None
        """
        super(AllPackagedMeshObjectsSelector, self).__init__(packaged_odb_objects)
        # 检查instance_name与set_name至少有一个不为None
        if instance_name is None and set_name is None:
            raise ValueError("instance_name and set_name cannot both be None.")
        self._instance_name = instance_name
        self._set_name = set_name

    def get_node_set(self):
        """
        获取节点集合。

        本方法旨在获取当前处理的有限元模型中的特定节点集合。首先通过调用父类的同名方法以执行任何预定义的获取节点集合逻辑，
        然后检查当前实例的节点集合是否已经存在。如果不存在，则通过实例名称和集合名称从打包的数据库对象中获取节点容器。
        如果获取到的节点容器是 PackagedOdbSet 类型，则直接返回该容器；否则，尝试从实例中获取节点集合。

        :return: 包装的节点集合。
        """
        # 调用父类方法以执行任何预处理或确保基类的行为被正确执行
        super(AllPackagedMeshObjectsSelector, self).get_node_set()

        # 检查当前实例的节点集合是否已经存在
        if self._nodes_set is None:
            # 通过实例名称和集合名称从打包的数据库对象中获取节点容器
            node_container = self.packaged_odb_objects.packaged_root_assembly. \
                get_node_container_by_instance_name_and_set_name(self._instance_name, self._set_name)
            # 判断获取到的节点容器类型
            if isinstance(node_container, PackagedOdbSet):
                # 如果节点容器是 PackagedOdbSet 类型，则直接返回
                self._nodes_set = node_container
            else:
                # 否则，尝试从实例中获取节点集合并返回
                self._nodes_set = node_container.get_node_set_of_instance()
        return self._nodes_set

    def get_element_set(self):
        """
        获取元素集合。

        本方法旨在获取当前处理的有限元模型中的特定元素集合。首先通过调用父类的同名方法以执行任何预定义的获取元素集合逻辑，
        然后检查当前实例的元素集合是否已经存在。如果不存在，则通过实例名称和集合名称从打包的数据库对象中获取元素容器。
        如果获取到的元素容器是 PackagedOdbSet 类型，则直接返回该容器；否则，尝试从实例中获取元素集合。

        :return: 包装的元素集合。
        :rtype: PackagedOdbSet
        """
        # 调用父类方法以执行任何预处理或确保基类的行为被正确执行
        super(AllPackagedMeshObjectsSelector, self).get_element_set()
        # 检查当前实例的元素集合是否已经存在
        if self._element_set is None:
            # 通过实例名称和集合名称从打包的数据库对象中获取元素容器
            element_container = self.packaged_odb_objects.packaged_root_assembly. \
                get_element_container_by_instance_name_and_set_name(self._instance_name, self._set_name)
            # 判断获取到的元素容器类型
            if isinstance(element_container, PackagedOdbSet):
                # 如果元素容器是 PackagedOdbSet 类型，则直接返回
                self._element_set = element_container
            else:
                # 否则，尝试从实例中获取元素集合并返回
                self._element_set = element_container.get_element_set_of_instance()
        return self._element_set

    def _packaged_meshes_info_str(self, meshes_type, packaged_set):
        """
        生成网格加载信息的字符串描述

        :param meshes_type: 网格类型，如"nodes"或"elements"
        :type meshes_type: str
        :param packaged_set: 包含网格数据的封装集合对象
        :type packaged_set: PackagedOdbSet
        :return: 网格加载信息的字符串描述
        :rtype: str
        """
        # 基础信息：加载的网格类型
        meshes_info_str = "Loading geometric '{}' from\n".format(meshes_type)
        # 添加实例名称信息（如果存在）
        if self._instance_name:
            meshes_info_str += "instance:'{}' ".format(self._instance_name)
        # 添加集合名称信息（如果存在）
        if self._set_name:
            meshes_info_str += "set:'{}'".format(self._set_name)
        # 添加网格数量统计信息
        meshes_info_str += "\n\nThe number of '{}':'{}'".format(meshes_type, packaged_set.length)
        return meshes_info_str

    def __str__(self):
        """
        返回对象的字符串表示形式

        该方法用于格式化输出当前对象的类名、实例名称和集合名称，
        主要用于调试和日志记录。

        返回格式示例：
        "class name:'AllPackagedMeshObjectsHandler',argus:instance_name='instance1'set_name='set1'"

        :return: 包含类名、实例名和集合名的格式化字符串
        :rtype: str
        """
        return "class name:'{}',argus:instance_name='{}'set_name='{}'". \
            format(self.__class__.__name__, self._instance_name, self._set_name)


class LabelsPackagedMeshObjectsSelector(PackagedMeshObjectsSelectorBase):
    def __init__(self, packaged_odb_objects, name="labels_meshes_handler"):
        """
        LabelsPackagedMeshObjectsSelector 编号选择器类用于获取指定实例名称与节点或单元编号的几何 ODB 节点或单元对象。

        由于输出数据库（ODB）中节点编号与单元编号属于不同的编号体系，因此一个
        LabelsPackagedMeshObjectsSelector 选择器实例只能选择节点或单元中的一种类型。
        如果需要同时选择节点和单元，则需要分别创建 LabelsPackagedMeshObjectsSelector
        选择器实例，并为每种类型单独添加相应的编号。

        要获取的实例名称与节点/单元编号通过 add_instance_name_label() 实例方法添加。

        :param packaged_odb_objects: 一个 PackagedOdbObjects 实例，包含封装的 ODB 对象。
        :type packaged_odb_objects: PackagedOdbObjects
        :param name: 名称。默认为 "labels_meshes_handler"
        :type name: str
        """

        super(LabelsPackagedMeshObjectsSelector, self).__init__(packaged_odb_objects, name)
        self._instance_names_labels = []

    def add_instance_name_label(self, instance_name, label):
        """
        向指定实例名称添加单元或节点的编号（仅一种）。

        :param instance_name: 实例名称。
        :type instance_name: str
        :param label: 要添加的编号。
        :type label: int
        :return:
        """
        # 检查类型
        check_type(instance_name, str)
        check_type(label, int)
        self._instance_names_labels.append((instance_name, label))

    def _generate_instance_name_label_pair(self):
        """
        生成实例名称与标签的元组序列。

        此函数是一个生成器，用于迭代地生成实例名称和标签的元组对。
        它遍历实例名称与标签列表的字典，对于每个实例名称，依次与其关联的每个标签生成一个元组对。

        :return: 生成的实例名称与标签的元组对。
        :rtype: tuple
        """
        # 遍历实例名称与标签列表的字典
        for instance_name, label_list in self._instance_names_labels:
            # 对于每个实例名称，依次生成与每个标签的元组对
            for label in label_list:
                yield instance_name, label

    def get_node_set(self):
        """
        获取节点集合。

        如果节点集合尚未创建，则根据实例名称和标签创建一个新的节点集合。
        该方法确保节点集合只被创建一次，以提高性能。

        :return: 代表一组节点的对象。
        :rtype: PackagedOdbSet
        """
        super(LabelsPackagedMeshObjectsSelector, self).get_node_set()
        # 检查节点集合是否已经存在，如果不存在则创建
        if self._nodes_set is None:
            # 使用OrderedDict保持实例名称的顺序
            labels = OrderedDict()
            # 遍历实例名称和标签，将标签按实例名称分组
            for instance_name, label in self._instance_names_labels:
                # 获取实例名称对应的标签列表，如果不存在则创建
                label_list = labels.setdefault(instance_name, [])
                # 将标签添加到对应的实例名称后面
                label_list.append(label)
            # 使用实例名称和标签创建节点集合
            self._nodes_set = self.packaged_odb_objects.packaged_root_assembly.create_node_set_from_node_labels(
                self.name, labels)
        # 返回节点集合
        return self._nodes_set

    def get_element_set(self):
        """
        获取元素集合。

        如果元素集合尚未创建，则根据实例名称和标签创建一个新的元素集合。
        该方法确保元素集合只被创建一次，以提高性能。

        :return: 代表一组元素的对象。
        :rtype: PackagedOdbSet
        """
        super(LabelsPackagedMeshObjectsSelector, self).get_element_set()
        # 检查元素集合是否已经存在，如果不存在则创建
        if self._element_set is None:
            # 使用OrderedDict保持实例名称的顺序
            labels = OrderedDict()
            # 遍历实例名称和标签，将标签按实例名称分组
            for instance_name, label in self._instance_names_labels:
                # 获取实例名称对应的标签列表，如果不存在则创建
                label_list = labels.setdefault(instance_name, [])
                # 将标签添加到对应的实例名称后面
                label_list.append(label)
            # 使用实例名称和标签创建元素集合
            self._element_set = self.packaged_odb_objects.packaged_root_assembly.create_element_set_from_element_labels(
                self.name, labels)
        # 返回元素集合
        return self._element_set

    def _packaged_meshes_info_str(self, meshes_type, packaged_set):
        """
        生成网格加载信息的字符串描述

        :param meshes_type: 网格类型，如"nodes"(节点)或"elements"(单元)
        :type meshes_type: str
        :param packaged_set: 封装好的网格数据集对象
        :type packaged_set: PackagedOdbSet
        :return: 格式化的网格加载信息字符串
        :rtype: str
        """
        # 基础信息：加载的网格类型
        meshes_info_str = "Loading geometric '{}' from\n".format(meshes_type)
        # 添加实例名称和网格标签的数量信息
        meshes_info_str += "instans names and meshes labels, number:'{}'".format(len(self._instance_names_labels))
        # 添加具体的实例名称和网格标签数据(使用omit_representation_sequence简化显示)
        meshes_info_str += "\ndatas:'{}'".format(omit_representation_sequence(self._instance_names_labels))
        # 添加网格数据集的总数量信息
        meshes_info_str += "\n\nThe number of '{}':'{}'".format(meshes_type, packaged_set.length)
        return meshes_info_str

    def __str__(self):
        """
        生成对象的字符串表示形式

        该方法返回一个包含以下信息的格式化字符串：
        - 当前对象的类名
        - 实例名称和标签列表的长度
        - 实例名称和标签列表的前5项内容（如果总长度超过5项，则末尾添加"..."表示省略)

        主要用于调试和日志记录，便于查看对象的基本信息。

        返回格式示例：
        "class name:'LabelsPackagedMeshObjectsHandler',argus:length='10'instance_names_labels_dict=[('inst1',1),('inst2',2)]..."

        :return: 包含对象信息的格式化字符串
        :rtype: str
        """
        info = "class name:'{}',argus:length='{}'instance_names_labels_dict='{}'". \
            format(self.__class__.__name__, len(self._instance_names_labels), self._instance_names_labels[:5])
        if len(self._instance_names_labels) > 5:
            info += "..."
        return info


class CoordinatesPackagedMeshObjectsSelector(PackagedMeshObjectsSelectorBase):
    def __init__(self, packaged_odb_objects, instance_name=None, set_name=None, name="coordinates_meshes_handler"):
        """
        CoordinatesPackagedMeshObjectsSelector坐标选择器类用于获取指定实例或集合中特定坐标的几何ODB节点或单元对象。

        该类根据指定的实例名称和/或集合名称，在其定义的范围内查找与给定坐标匹配的几何对象（节点或单元）。
        具体行为如下：
        - 如果仅提供instance_name：在该实例的所有几何对象中查找匹配坐标的对象
        - 如果仅提供set_name：先在装配体集合中查找该集合，如果未找到则在各个实例集合中查找匹配坐标的对象
        - 如果同时提供instance_name和set_name：在指定实例的指定集合中查找匹配坐标的对象

        坐标通过add_coordinate()或add_coordinates()方法添加到实例中。

        :param packaged_odb_objects: 一个PackagedOdbObjects实例，包含封装的ODB对象。
        :type packaged_odb_objects: PackagedOdbObjects
        :param instance_name: 实例名称，默认为None。
        :type instance_name: str | None
        :param set_name: 集合名称，实例名称或集合名称至少指定一个。
        :type set_name: str | None
        :param name: 选择器名称，默认为"coordinates_meshes_handler"。
        :type name: str
        :raises ValueError: 当instance_name和set_name都为None时抛出异常。
        """

        super(CoordinatesPackagedMeshObjectsSelector, self).__init__(packaged_odb_objects, name)
        self._coordinates_list = []
        if instance_name is None and set_name is None:
            raise ValueError("instance_name and set_name cannot both be None.")
        self._instance_name = instance_name
        self._set_name = set_name

    @property
    def coordinates_list(self):
        """
        获取坐标列表属性
        实例中通过坐标获取几何节点或单元时，访问此方法得到实例管理的坐标，
        子类若有生成坐标的步骤，在此方法中调用。

        :return: 返回内部的坐标列表
        :rtype: list
        """
        return self._coordinates_list

    def add_coordinate(self, coordinate):
        """
        向坐标列表中添加一个坐标。

        :param coordinate: 长度为3的列表、元组或numpy数组，每个元素必须是整数或浮点数。
        :type coordinate: list/tuple/np.ndarray
        :return:  None
        :rtype: None
        :raises TypeError: 如果坐标不符合要求，将抛出TypeError。
        """
        # 检查坐标是否为列表、元组或numpy数组，长度为3，并且所有元素都是整数或浮点数
        if not (isinstance(coordinate, (list, tuple, np.ndarray)) and len(coordinate) == 3 and all(
                isinstance(c, (int, float)) for c in coordinate)):
            raise TypeError("coordinate must be a list or tuple of length 3 containing only integers or floats.")
        # 将验证通过的坐标添加到坐标列表中
        self._coordinates_list.append(coordinate)

    def add_coordinates(self, coordinates):
        """
        批量添加坐标信息。

        该方法接受一个包含多个坐标的列表、元组或NumPy数组作为输入，并逐个添加这些坐标。
        这种设计允许一次性添加多个坐标，简化调用过程。

        :param coordinates: 包含多个坐标的列表、元组或NumPy数组。
        :type coordinates: list | tuple | np.ndarray
        :return:
        """
        # 检查coordinates类型是否为列表、元组或NumPy数组，确保类型安全
        check_type(coordinates, list, tuple, np.ndarray)

        # 遍历坐标集合，逐个添加坐标
        for coordinate in coordinates:
            self.add_coordinate(coordinate)

    def get_node_set(self):
        """
        获取节点集合对象。

        如果当前实例中的_nodes_set属性为空，则通过调用父类的get_node_set方法
        和创建节点集合的逻辑来初始化它。确保节点集合仅在首次请求时创建，
        之后将缓存并返回相同的集合对象。

        :return: 节点集合对象，表示根据坐标创建的节点组。
        :rtype: NodeSet
        """
        # 调用父类的get_node_set方法，以确保继承了任何初始化或通用逻辑
        super(CoordinatesPackagedMeshObjectsSelector, self).get_node_set()

        # 检查_nodes_set是否已经初始化
        if self._nodes_set is None:
            # 如果_nodes_set未初始化，则使用提供的坐标列表创建节点集合
            self._nodes_set = self.packaged_odb_objects.packaged_root_assembly.create_node_set_from_coordinates(
                self.name, self.coordinates_list, self._instance_name, self._set_name)

        # 返回初始化后的节点集合对象
        return self._nodes_set

    def get_element_set(self):
        """
        获取元素集合对象。

        如果当前实例中的_elements_set属性为空，则通过调用父类的get_element_set方法
        和创建元素集合的逻辑来初始化它。确保元素集合仅在首次请求时创建，
        之后将缓存并返回相同的集合对象。

        :return: 元素集合对象，表示根据某些条件创建的元素组。
        :rtype: ElementSet
        """
        # 调用父类的get_element_set方法，以确保继承了任何初始化或通用逻辑
        super(CoordinatesPackagedMeshObjectsSelector, self).get_element_set()
        # 检查_elements_set是否已经初始化
        if self._element_set is None:
            # 如果_elements_set未初始化，则使用提供的条件创建元素集合
            self._element_set = self.packaged_odb_objects.packaged_root_assembly.create_element_set_from_coordinates(
                self.name, self.coordinates_list, self._instance_name, self._set_name)
        # 返回初始化后的元素集合对象
        return self._element_set

    def _packaged_meshes_info_str(self, meshes_type, packaged_set):
        """
        生成网格加载进度信息字符串

        该方法用于构造一个描述网格加载状态的详细字符串，包含以下信息：
        - 网格类型（节点/单元）
        - 所属实例名称（如果存在）
        - 所属集合名称（如果存在）
        - 坐标点数量
        - 坐标数据（截断显示）
        - 实际加载的网格数量

        :param meshes_type: 网格类型，'nodes' 或 'elements'
        :type meshes_type: str
        :param packaged_set: 已加载的网格集合对象
        :type packaged_set: PackagedOdbSet
        :return: 格式化的进度信息字符串
        :rtype: str
        """
        meshes_info_str = "Loading geometric '{}' from\n".format(meshes_type)
        if self._instance_name:
            meshes_info_str += "instance:'{}' ".format(self._instance_name)
        if self._set_name:
            meshes_info_str += "set:'{}'".format(self._set_name)
        meshes_info_str += "\ncoordinates number:'{}'".format(len(self.coordinates_list))
        meshes_info_str += "\ndatas:'{}'".format(omit_representation_sequence(self.coordinates_list))
        meshes_info_str += "\n\nThe number of '{}':'{}'".format(meshes_type, packaged_set.length)
        return meshes_info_str

    def __str__(self):
        """
        返回对象的字符串表示形式，用于调试和日志记录。

        格式包含以下信息：
        1. 类名
        2. 实例名称 (_instance_name)
        3. 集合名称 (_set_name)
        4. 坐标列表长度 (_coordinates_list长度)
        5. 前5个坐标值 (_coordinates_list前5项)

        如果坐标数量超过5个，结尾会添加"..."表示省略

        :return: 格式化的对象信息字符串
        :rtype: str
        """
        info = "class name:'{}',argus:instance_name='{}'set_name='{}'coordinates_length='{}'coordinates='{}'". \
            format(self.__class__.__name__, self._instance_name, self._set_name, len(self._coordinates_list),
                   self._coordinates_list[:5])
        if len(self._coordinates_list) > 5:
            info += "..."
        return info


class FieldOutputDatasGetter(OdbAnalyzerBase):
    def __init__(self, packaged_odb_objects, frame_start=None, frame_end=None):
        """
        创建一个FieldOutputDatasGetter对象，用于获取指定帧的场输出数据。

        :param frame_start: (int, 可选): 起始帧的索引，默认为None，表示从第一帧开始。
        :type frame_start: int
        :param frame_end: (int, 可选): 结束帧的索引，默认为None，表示到最后一帧结束。
        :type frame_end: int
        :param packaged_odb_objects: 一个PackagedOdbObjects实例，包含封装的ODB对象。
        :type packaged_odb_objects: PackagedOdbObjects
        """
        super(FieldOutputDatasGetter, self).__init__(packaged_odb_objects)
        self._frames_manager = \
            self.packaged_odb_objects.packaged_frames.get_frames_manager(frame_start, frame_end)
        self._frames_manager.set_if_send_progress(True)
        self._frame_handlers = []
        self._frame_handlers_message = []

    @property
    def frames_manager(self):
        """
        获取帧管理器。

        :return: 帧管理器对象。
        """
        return self._frames_manager

    @property
    def frame_handlers(self):
        """
        获取所有的帧处理器。

        :return: (list[FrameHandlerType]): 所有的帧处理器。
        :rtype: list[FrameHandlerType]
        """
        if not self._frame_handlers:
            raise RuntimeError("Please add frame_handler first")
        return self._frame_handlers

    def add_frame_handler(self, frame_handler):
        """
        添加帧处理项

        :param frame_handler: (FrameHandlerBase): 一个帧处理项实例，必须继承自FrameHandlerBase
        :type frame_handler: FrameHandlerType
        :return: 该方法没有返回值
        :rtype: None
        """
        # 确保传入的帧处理句柄是FrameHandlerBase的子类
        check_type(frame_handler, FrameHandlerType)
        # 将验证过的帧处理句柄添加到处理器列表中
        frame_handler.frame_manager = self.frames_manager
        self._frame_handlers.append(frame_handler)
        self._frame_handlers_message.append(None)

    def get_field_output_datas(self, start=None, end=None, **kwargs):
        """
        将管理的帧分发给所有的帧处理程序。

        该函数从frames_manager中获取每一个管理的帧，并将其发送给每一个帧处理程序。
        在所有帧处理完毕后，向每一个帧处理程序发送None信号，表示所有帧已处理完毕。

        对于从send_frame()中返回的消息，目前支持：
        - "continue": 从当前帧以后跳过对本对象 `send_frame` 方法的调用。当所有帧处理程序都返回"continue"，则直接退出，不处理剩下的帧。
        - 其他或 None: 正常遍历之后的帧，执行各处理

        :param start: 托管项的起始索引，默认为None，表示从第一个托管项开始
        :type start: int|None
        :param end: 托管项的结束索引，默认为None，表示到所有托管项结束
        :type end: int|None
        :param kwargs: 其他传递给frames_manager的get_every_managed_item方法的关键字参数，用于获取管理的帧。
        :return: 无返回值。
        """
        # 遍历所有管理的帧，将每一个帧发送给所有帧处理程序
        for packaged_frame in self.frames_manager.get_every_managed_item(
                start=start, end=end, if_add_packaged_items=True, **kwargs):
            # 如果所有帧处理程序都返回"continue"，则直接退出，不处理剩下的帧
            if all(element == "continue" for element in self._frame_handlers_message):
                break
            for i, frame_handler in enumerate(self.frame_handlers):
                last_message = self._frame_handlers_message[i]
                if last_message == "continue":
                    continue
                else:
                    pass
                message = frame_handler.send_frame(packaged_frame)
                self._frame_handlers_message[i] = message
        # 所有帧处理完毕后，向帧处理程序发送None信号
        for frame_handler in self.frame_handlers:
            # 等待所有帧处理程序结束
            frame_handler.send_frame(None)


class FrameHandlerType(AbqPostExtensionBase):
    """
    FrameHandlerType是一个抽象类，用于定义帧处理程序。
    """

    def __init__(self, *args, **kwargs):
        super(FrameHandlerType, self).__init__(*args, **kwargs)

    def send_frame(self, packaged_frame):
        raise NotImplementedError("Please implement the send_frame method")


class FrameHandlerBase(FrameHandlerType):
    """
    FrameHandlerBase是一个基础类，用于处理帧数据。
    它提供了一个框架，包括发送帧、处理帧和结束处理的功能。
    """
    __frame_data_attribute_names = OrderedDict([('Frame ID', 'frame_id'), ('Step Time', 'step_time')])

    __node_field_value_info_attribute_names = OrderedDict([
        ("Field Output Type", "field_output_type"), ('Instance Name', 'instance_name'), ('Node Label', 'node_label'),
        ('Coordinates X', 'packaged_node.coordinates_x'), ('Coordinates Y', 'packaged_node.coordinates_y'),
        ('Coordinates Z', 'packaged_node.coordinates_z'), ('Frame ID', 'packaged_frame.frame_id'),
        ('Step Time', 'packaged_frame.step_time')])
    __node_field_value_data_attribute_names = OrderedDict([(
        "X data", "x_data"), ("Y data", "y_data"), ("Z data", "z_data"), ("Magnitude data", "magnitude_data")])
    __all_node_field_value_attribute_names = OrderedDict()
    __all_node_field_value_attribute_names.update(__node_field_value_info_attribute_names)
    __all_node_field_value_attribute_names.update(__node_field_value_data_attribute_names)
    __node_mesh_data_attribute_names = OrderedDict([
        ('Instance Name', 'instance_name'), ('Node Label', 'label'), ('Coordinates X', 'coordinates_x'),
        ('Coordinates Y', 'coordinates_y'), ('Coordinates Z', 'coordinates_z')])

    __element_field_value_info_attribute_names = OrderedDict([
        ("Field Output Type", "field_output_type"), ('Instance Name', 'instance_name'),
        ('Element Label', 'element_label'),
        ('Coordinates X', 'packaged_element.mean_coordinate_x'),
        ('Coordinates Y', 'packaged_element.mean_coordinate_y'),
        ('Coordinates Z', 'packaged_element.mean_coordinate_z'),
        ('Frame ID', 'packaged_frame.frame_id'), ('Step Time', 'packaged_frame.step_time')])
    __element_field_value_data_attribute_names = OrderedDict([("Average Mises data", "average_mises_data")])
    __all_element_field_value_attribute_names = OrderedDict()
    __all_element_field_value_attribute_names.update(__element_field_value_info_attribute_names)
    __all_element_field_value_attribute_names.update(__element_field_value_data_attribute_names)
    __element_mesh_data_attribute_names = OrderedDict([
        ('Instance Name', 'instance_name'), ('Element Label', 'label'), ('Coordinates X', 'coordinates_x'),
        ('Coordinates Y', 'coordinates_y'), ('Coordinates Z', 'coordinates_z')])

    def __init__(self, field_output_type, packaged_meshes_handler, data_attribute_names=None, if_load_data=True, *args,
                 **kwargs):
        """
        构造函数，用于初始化FrameHandlerBase对象。

        :param field_output_type: 要获取的场输出的类型，"U"或"S"或“A”或其他支持的类型。
        :type field_output_type: str
        :param packaged_meshes_handler: 获取几何odb单元或节点的对象
        :type packaged_meshes_handler: PackagedMeshObjectsSelectorBase
        :param data_attribute_names: 需要处理的场输出PackagedFieldValue或PackagedElementFieldValue对象的属性名称
        :type data_attribute_names: list[str]
        :param if_load_data: 是否在调用handle_frame处理数据前先加载传入其中的FieldValuesManager
                对象的当前对象data_attribute_names属性指定的数据，默认为True
        """
        super(FrameHandlerBase, self).__init__(*args, **kwargs)

        if data_attribute_names is not None:
            check_sequence_type(data_attribute_names, str)
        self._data_attribute_names = data_attribute_names
        # 检查封装的网格对象处理器的类型
        check_type(packaged_meshes_handler, PackagedMeshObjectsSelectorBase)
        self._packaged_meshes_handler = packaged_meshes_handler
        # 验证场输出数据类型的合法性
        self.field_output_type_constant.verify_all_field_output_type(field_output_type)
        self.field_output_type = field_output_type
        packaged_set = self._packaged_meshes_handler.get_set_by_field_output_type(
            self.field_output_type)
        if packaged_set.length == 0:
            raise RuntimeError("No packaged meshes found at:'{}'".format(str(self._packaged_meshes_handler)))
        self._packaged_set = packaged_set
        check_type(if_load_data, bool)
        self._if_load_data = if_load_data
        self._frame_manager = None
        self.__if_start_handle_frame = True

    def get_packaged_meshes(self):
        """
        根据字段输出类型获取打包后的网格数据。

        本方法首先调用`determine_node_field_output_type`方法判断当前字段输出类型是否为节点类型。
        如果是节点类型，则调用`get_packaged_nodes`方法获取打包后的节点数据；
        否则，调用`get_packaged_elements`方法获取打包后的单元数据。

        :return: 打包后的节点数据或单元数据，具体返回值类型取决于字段输出类型。
        :rtype: list[PackagedNode]|list[PackagedElement]
        """
        if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
            return self.packaged_set.get_packaged_nodes()
        return self.packaged_set.get_packaged_elements()

    @property
    def field_output_type_constant(self):
        return self._packaged_meshes_handler.field_output_type_constant

    @property
    def frame_manager(self):
        """
        获取当前对象使用的FieldOutputDatasGetter对象中管理的帧管理器对象。

        :return: 帧管理器对象
        :rtype: PackagedFramesManager
        """
        if self._frame_manager is None:
            raise RuntimeError("FrameManager is not set")
        return self._frame_manager

    @frame_manager.setter
    def frame_manager(self, frame_manager):
        """
        设置当前对象使用的FieldOutputDatasGetter对象中管理的帧管理器对象。
        :param frame_manager: 帧管理器对象
        :return: None
        """
        check_type(frame_manager, PackagedFramesManager)
        self._frame_manager = frame_manager

    @property
    def packaged_set(self):
        """
        获取打包后的集合

        此属性用于获取经过处理或包装后的集合数据返回给调用者它反映了对象内部状态的封装，通过此方法调用者可以安全地访问到经过特定处理的集合数据，而无需直接访问对象内部属性

        :return: 返回内部状态_packaged_set，它是一个经过特定处理的集合
        :rtype: PackagedOdbSet
        """
        return self._packaged_set

    @property
    def default_packaged_mesh_data_attribute_names_dict(self):
        """
        根据场输出数据类型决定返回节几何点数据属性名称字典还是几何单元属性名称字典。

        :return: 如果场输出数据类型符合节点场输出数据类型条件，则返回节点几何点数据属性名称字典；
        :rtype: dict[str, str]
        """
        # 根据场输出数据类型判断是否符合节点场输出数据类型的条件
        if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
            # 如果符合，返回节点字段值数据属性名称字典
            return self.__node_mesh_data_attribute_names
        else:
            # 如果不符合，返回元素字段值数据属性名称字典
            return self.__element_mesh_data_attribute_names

    @property
    def default_packaged_frame_data_attribute_names_dict(self):
        """
        默认帧数据属性名称字典。
        :return:
        """
        return self.__frame_data_attribute_names

    @property
    def default_field_value_data_attribute_names_dict(self):
        """
        根据场输出数据类型决定返回节点字段值数据属性名称字典还是元素字段值数据属性名称字典。

        :return: 如果场输出数据类型符合节点场输出数据类型条件，则返回节点字段值数据属性名称字典；
                 否则，返回元素字段值数据属性名称字典。
        :rtype: dict[str, str]
        """
        # 根据场输出数据类型判断是否符合节点场输出数据类型的条件
        if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
            # 如果符合，返回节点字段值数据属性名称字典
            return self.__node_field_value_data_attribute_names
        else:
            # 如果不符合，返回元素字段值数据属性名称字典
            return self.__element_field_value_data_attribute_names

    @property
    def default_field_value_info_attribute_names_dict(self):
        """
        根据场输出数据类型决定返回节点字段值信息属性名称字典还是元素字段值信息属性名称字典。

        :return: 节点字段值信息属性名称字典或元素字段值信息属性名称字典
        :rtype: dict[str, str]
        """
        # 根据场输出数据类型判断是否符合节点场输出数据类型的条件
        if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
            # 如果符合，返回节点字段值数据属性名称字典
            return self.__node_field_value_info_attribute_names
        else:
            # 如果不符合，返回元素字段值数据属性名称字典
            return self.__element_field_value_info_attribute_names

    @property
    def default_all_field_value_attribute_names_dict(self):
        """
        根据当前对象的场输出类型，返回节点的或单元的类中定义的各属性名称字典
        :return: 字典
        :rtype: dict
        """
        if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
            # 如果符合，返回节点字段值数据属性名称字典
            return self.__all_node_field_value_attribute_names.copy()
        else:
            # 如果不符合，返回元素字段值数据属性名称字典
            return self.__all_element_field_value_attribute_names

    @property
    def default_data_attribute_names(self):
        """
        根据场输出数据类型返回类中定义的默认的数据属性名称列表。
        :return: 数据属性名称列表。
        :rtype: list[str]
        """
        # 使用FieldOutputTypeConstant类来确定场输出数据类型是否为节点类型
        if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
            # 如果是节点类型，返回节点字段值的数据属性名称列表
            return list(self.__node_field_value_data_attribute_names.values())
        else:
            # 如果不是节点类型，返回元素字段值的数据属性名称列表
            return list(self.__element_field_value_data_attribute_names.values())

    @property
    def data_attribute_names(self):
        """
        根据场输出数据类型返回数据属性名称列表。

        本方法首先检查是否已经缓存了数据属性名称列表，如果未缓存，则根据场输出数据类型
        动态确定返回类中定义的默认的节点的数据属性名称列表还是单元的数据属性名称列表。

        :return: 数据属性名称列表。
        :rtype: list[str]
        """
        # 检查是否已缓存数据属性名称列表
        if self._data_attribute_names is None:
            self._data_attribute_names = self.default_data_attribute_names
        return self._data_attribute_names

    def send_frame(self, packaged_frame):
        """
        发送并处理封装好的帧数据。

        本函数根据提供的packaged_frame对象的类型，决定是启动一个新的处理线程来处理该帧，
        还是调用结束处理函数。如果packaged_frame不为None，则会获取帧的字段输出值及其管理器，
        并根据需要加载相关数据，然后创建并启动一个处理线程。如果packaged_frame为None，则调用
        结束处理函数。

        返回的消息用于控制 `FieldOutputDatasGetter` 对象的帧遍历行为：
        - "continue": 从当前帧以后跳过对本对象 `send_frame` 方法的调用
        - 其他或 None: 正常遍历之后的帧，执行各处理

        :param packaged_frame: 封装好的帧数据对象；如果为 None，则表示没有帧数据可处理
        :type packaged_frame: PackagedFrame | None
        :return: 消息，用于控制 `FieldOutputDatasGetter` 对象的帧遍历行为
        :rtype: str | None
        """
        # 检查packaged_frame的类型是否为PackagedFrame或None
        check_type(packaged_frame, PackagedFrame, None)
        # 检查是否满足开始处理帧的条件
        if self.__if_start_handle_frame:
            # 调用start_handle方法以开始处理
            self.start_handle()
            # 重置条件标志，防止重复触发
            self.__if_start_handle_frame = False
        # 根据packaged_frame是否为None，选择相应的处理方法
        if packaged_frame is not None:
            # 如果packaged_frame不为None，进行帧处理
            current_packaged_frame = packaged_frame
            # 获取当前帧的字段输出值
            current_field_output_values = current_packaged_frame.get_field_output_values(self.field_output_type)
            # 获取当前帧的字段输出值管理器，并加载字段输出值管理器所需的数据
            current_field_values_manager = current_field_output_values.get_packaged_field_values_manager_by_set(
                self.packaged_set)
            if self._if_load_data:
                current_field_values_manager.load_generated_packaged_items(attribute_names=self.data_attribute_names)
            return self.handle_frame(current_packaged_frame, current_field_output_values, current_field_values_manager)
        else:
            # 如果packaged_frame为None，调用结束处理函数
            self.end_handle()

    def start_handle(self):
        """
        首帧开始前处理函数。

        该方法是一个占位符方法，用于启动具体的处理逻辑。
        具体的功能实现应该由继承该类的子类来完成。

        :return:  None
        """
        pass

    def handle_frame(self, current_packaged_frame, current_field_output_values, current_field_values_manager):
        """
        处理单个封装帧与这一帧下的指定类型的场输出值对象的方法。

        返回的消息用于控制 `FieldOutputDatasGetter` 对象的帧遍历行为：
        - "continue": 从当前帧以后跳过对本对象 `send_frame` 方法的调用
        - "break": 直接结束退出，不再处理之后的所有帧
        - 其他或 None: 正常遍历之后的帧，执行各处理

        此方法，需要由子类实现具体的帧处理逻辑。

        :param current_field_values_manager: 当前帧中的当前对象指定的几何对象的场输出数据管理器。
        :type current_field_values_manager: FieldValuesManager
        :param current_packaged_frame: (PackagedFrame): 当前的封装帧对象。
        :type current_packaged_frame: PackagedFrame
        :param current_field_output_values: 指定场输出类型的当前场输出值对象。
        :type current_field_output_values: PackagedFieldOutputValues
        :return: 控制帧遍历行为的消息
        :rtype: str | None
        """
        raise NotImplementedError

    def end_handle(self):
        """
        结束帧之后处理的方法。

        此方法是一个占位符，意在由子类实现具体的结束处理逻辑。

        :return: None
        """
        pass

    def get_field_value_attributes(self, field_value, data_name_attribute_names_dict=None):
        """
        根据提供的字段值和数据名称属性名字典，获取相应的属性值。

        :param field_value: 字段值，用于提取属性的基点。
        :type field_value: PackagedFieldValue | PackagedElementFieldValue | PackagedNode | PackagedElement
        :param data_name_attribute_names_dict: 可选参数，一个字典，键为数据名称，值为属性名列表，用于指定需要提取的属性。
            默认为FrameHandlerBase类中定义的属性名称字典all_node_field_value_attribute_names
            或all_element_field_value_attribute_names
        :type data_name_attribute_names_dict: dict[str,str] | None
        :return: 一个有序字典，键为数据名称，值为从字段值中提取的属性值。
        :rtype: OrderedDict[str,any]
        """
        check_type(field_value, PackagedFieldValue, PackagedElementFieldValue, PackagedNode, PackagedElement,
                   PackagedFrame)
        # 初始化一个有序字典来存储数据名称和对应的属性值
        datas = OrderedDict()
        # 如果未提供数据名称属性名字典，则根据场输出数据类型决定使用哪个属性名字典
        if data_name_attribute_names_dict is None:
            data_name_attribute_names_dict = self.default_all_field_value_attribute_names_dict
        # 遍历数据名称属性名字典，提取每个数据名称对应的属性值
        for data_name, attribute_names in data_name_attribute_names_dict.items():
            # 使用属性名列表提取嵌套属性，并将结果存储在有序字典中
            datas[data_name] = get_nested_attribute(field_value, attribute_names)
        # 返回包含数据名称和属性值的有序字典
        return datas

    def get_field_value_manager_attributes(self, field_value_manager, data_name_attribute_names_dict=None):
        """
        根据提供的字段值和数据名称属性名字典，获取相应的属性值。

        :param field_value_manager: 多个场输出数据对象的管理器，从中获取所有管理对象的指定属性的列表
        :type field_value_manager: FieldValuesManager
        :param data_name_attribute_names_dict: 可选参数，一个字典，键为数据名称，值为属性名列表，用于指定需要提取的属性。
            默认为FrameHandlerBase类中定义的属性名称字典all_node_field_value_attribute_names
            或all_element_field_value_attribute_names
        :type data_name_attribute_names_dict: dict[str,str] | None
        :return: 一个有序字典，键为数据名称，值为从场输出管理器中获取的属性值列表
        :rtype: OrderedDict[str,list[any]]
        """
        check_type(field_value_manager, FieldValuesManager)
        # 初始化一个有序字典来存储数据名称和对应的属性值
        datas = OrderedDict()
        # 如果未提供数据名称属性名字典，则根据场输出数据类型决定使用哪个属性名字典
        if data_name_attribute_names_dict is None:
            data_name_attribute_names_dict = self.default_all_field_value_attribute_names_dict
        for data_name, attribute_names in data_name_attribute_names_dict.items():
            # 使用属性名列表提取嵌套属性，并将结果存储在有序字典中
            datas[data_name] = field_value_manager.get_specified_attribute_list(attribute_names)
        return datas

    def _verify_customize_attribute_names(self, customize_data_attribute_names=None):
        """
        验证和处理自定义属性名称列表，用以输出数据时标明每个参数名称。

        如果提供的自定义属性名称列表为空，则根据当前场输出数据类型，
        从类中定义的节点字段值或元素字段值的每个属性名称的自定义名称字典中生成一个自定义属性名称列表，
        如果类默认项中为提供当前参数名称的自定义名称，则使用当前参数的名称。

        :param customize_data_attribute_names: 用户提供的自定义属性名称列表。
        :type customize_data_attribute_names: list[str]|None
        :return: 处理后的自定义属性名称列表。
        :rtype: list[str]

        :raises ValueError: 如果提供的自定义属性名称数量与数据属性名称数量不匹配。
        """
        # 检查是否提供了自定义属性名称列表
        if customize_data_attribute_names is None:
            # 初始化自定义属性名称列表
            customize_data_attribute_names = []
            # 根据场输出数据类型确定使用节点字段值还是元素字段值
            if self.field_output_type_constant.determine_node_field_output_type(self.field_output_type):
                attribute_names_dict = self.__node_field_value_data_attribute_names
            else:
                attribute_names_dict = self.__element_field_value_data_attribute_names
            # 反转属性名称字典，以便根据属性名称获取自定义属性名称
            reverse_attribute_names_dict = {value: key for key, value in attribute_names_dict.items()}
            # 遍历数据属性名称列表，获取对应的自定义属性名称
            for attribute_name in self.data_attribute_names:
                try:
                    customize_data_attribute_name = reverse_attribute_names_dict[attribute_name]
                except KeyError:
                    customize_data_attribute_name = attribute_name
                customize_data_attribute_names.append(customize_data_attribute_name)
            return customize_data_attribute_names
        # 检查自定义属性名称列表的类型
        check_sequence_type(customize_data_attribute_names, str)
        # 检查提供的自定义属性名称数量是否与数据属性名称数量匹配
        if len(customize_data_attribute_names) != len(self.data_attribute_names):
            raise ValueError(
                "The number of customize_attribute_names:'{}' must be equal to the number of data_attribute_names"
                ":'{}'.".format(len(customize_data_attribute_names), len(self.data_attribute_names)))
        return customize_data_attribute_names


if __name__ == "__main__":
    pass
