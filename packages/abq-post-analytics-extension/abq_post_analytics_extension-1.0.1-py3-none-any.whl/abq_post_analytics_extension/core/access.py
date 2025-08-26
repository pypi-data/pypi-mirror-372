# -*- coding: UTF-8 -*-
import os
import time
from collections import OrderedDict

try:
    from typing import Generator
except ImportError:
    pass

import numpy as np
from scipy.spatial import KDTree


from odbAccess import openOdb
# def openOdb(*argus, **kwargs):
#     raise NotImplementedError("openOdb is not supported in this version")
#     return None


from ..utils.system_utilities import AbqPostExtensionBase
from ..utils.misc_utils import PackageBase as _PackageBaseBase, check_type, \
    iterate_deep, check_sequence_type, get_nested_attribute, Singleton, \
    FieldOutputTypeConstant, get_element_from_2d_list
from ..utils.file_operations import FileOperations


def _customize_len(obj):
    """
    自定义长度函数，尝试获取对象的长度。

    该函数首先尝试使用内置的len()函数获取对象的长度。
    如果对象不支持len()函数，则假设对象为空，返回长度为0。

    :param obj: 任意对象，该函数尝试获取该对象的长度。
    :type obj: 任意对象
    :return: 对象的长度，如果无法确定长度，则返回0。
    :rtype: int
    """
    try:
        return len(obj)
    except Exception as e:
        return 0


class PackagedObjectFactory(Singleton):
    """
    PackagedObjectFactory 类用于创建和管理各种包装对象。
    该类通过动态构建类映射表 `class_map`，允许用户通过点属性方式访问和创建这些类的实例。
    """

    def _initialize(self):
        """
        初始化 PackagedObjectFactory 实例。

        通过设置对象属性来存储各个类，并自动构建 `class_map`。
        """
        # 设置对象属性，存储各个类
        self.packaged_odb_class = PackagedOdb
        self.packaged_root_assembly_class = PackagedRootAssembly
        self.packaged_odb_set_class = PackagedOdbSet
        self.packaged_instance_class = PackagedInstance
        self.packaged_node_class = PackagedNode
        self.packaged_element_class = PackagedElement
        self.packaged_step_class = PackagedStep
        self.packaged_frames_class = PackagedFrames
        self.packaged_frame_class = PackagedFrame
        self.packaged_frame_manager_class = PackagedFramesManager
        self.packaged_field_output_class = PackagedFieldOutputs
        self.packaged_field_output_values_class = PackagedFieldOutputValues
        self.field_values_manager = FieldValuesManager
        self.packaged_field_value_class = PackagedFieldValue
        self.packaged_element_field_value_class = PackagedElementFieldValue

        # 自动构建 class_map
        self.class_map = {
            name: cls for name, cls in self.__dict__.items() if name.startswith('packaged_')
        }
        # 从 class_map 中提取 allowed_classes 列表，用于验证创建对象时的类是否有效
        self.allowed_classes = list(self.class_map.values())

    def create_object(self, object_type, *args, **kwargs):
        """
        创建并返回指定类型的对象。

        :param object_type: 需要创建的对象的类，必须是 `allowed_classes` 列表中的一个类或这些类的子类。
        :param args: 传递给类构造函数的位置参数。
        :param kwargs: 传递给类构造函数的关键字参数。
        :return: 创建的对象实例。
        :raises ValueError: 如果 `object_type` 不在 `allowed_classes` 列表中。
        :raises Exception: 如果在创建对象时发生任何异常。
        """
        if any([issubclass(object_type, obj) for obj in self.allowed_classes]):
            raise ValueError("object_type must be one of the allowed classes")
        try:
            return object_type(*args, **kwargs)
        except Exception as e:
            # 记录异常信息
            print("An error occurred while creating the object:{}".format(e))
            raise


class _PackageBase(_PackageBaseBase, AbqPostExtensionBase):
    """
    基类，除用于包装其他对象并提供统一的属性访问接口，添加对父节点的引用即访问所有父节点的方法。
    """

    def get_packaged_item(self):
        """
        获取包装的原始odb对象。
        
        :return: 包装的原始odb对象。
        """
        return self.odb_source

    def __init__(self, parent_node=None, *argus, **kwargs):
        """
        初始化类的构造方法。

        该构造方法用于初始化类的实例，可以接受额外的位置参数（*argus）和关键字参数（**kwargs），
        以便于在创建实例时传递可变数量的参数。

        :param parent_node: 父节点，用于建立节点树结构。
        :param argus: 额外的位置参数，允许在初始化时传递未在参数列表中明确指定的参数。
        :param kwargs: 额外的关键字参数，允许在初始化时传递以键值对形式指定的参数。
        """
        super(_PackageBase, self).__init__(*argus, **kwargs)
        self._odb_source = None
        check_type(parent_node, _PackageBase, None)
        self.parent_node = parent_node

    @property
    def _packaged_odb_object_factory(self):
        """
        获取打包的ODB对象工厂方法。

        该方法通过调用扩展管理器的get_packaged_object_factory方法来获取一个对象工厂，
        该对象工厂可能用于创建或管理打包的ODB对象。

        :return: 调用abq_ext_manager的get_packaged_object_factory方法返回的对象工厂。
        :rtype: PackagedObjectFactory
        """
        return self._abq_ext_manager.get_packaged_object_factory()

    def get_parents(self):
        """
        返回一个迭代器，依次访问当前节点及其每一个父节点。
        
        :return: 一个迭代器，依次访问当前节点及其每一个父节点。
        :rtype: Iterator[_PackageBase]
        """
        # 首先返回当前节点
        yield self

        # 遍历并返回所有父节点
        current_node = self
        while current_node.parent_node is not None:
            yield current_node.parent_node
            current_node = current_node.parent_node

    def get_parent(self):
        """
        获取当前对象的父对象。

        本函数通过调用 `self.get_parents()` 方法获取一个包含所有父对象的生成器。
        由于我们需要获取第一个父对象，因此首先调用 `next(parents_generator)` 来忽略掉第一个父对象（第一个父对象为自身）。
        然后再次调用 `next(parents_generator)` 来获取并返回第二个父对象，即实际意义上的第一个父对象。
        如果父对象不存在，则返回None。

        :return: 当前对象的第一个父对象。如果父对象不存在，则返回None。
        :rtype: Any
        """
        parents_generator = self.get_parents()
        try:
            next(parents_generator)
        except StopIteration:
            # 如果生成器为空（即没有父对象），则返回None
            return None
        return next(parents_generator)

    def get_specified_type_parent(self, specified_type):
        """
        获取特定类型的父级对象。

        遍历所有父级对象，寻找符合指定类型的父级对象。如果找到，则返回该父级对象；
        如果没有找到，则返回None。这个方法用于在复杂的对象关系中快速定位到特定类型的父级对象。

        :param specified_type: 指定的类型，用于匹配父级对象的类型。
        :return: 符合指定类型的父级对象，如果没有找到，则返回None。
        :rtype: Any
        """
        for parent in self.get_parents():
            if isinstance(parent, specified_type):
                return parent
        parent_name = ""
        for parent in self.get_parents():
            parent_name += str(parent) + "->"

        raise RuntimeError("No parent of type {} found. parents are:'{}'".format(specified_type, parent_name))

    @staticmethod
    def _accessing_attributes_and_delete_odb_source(obj, if_delete_odb_source=True, attribute_names=None):
        """
        删除对象的ODB源，并访问对象的指定属性。

        该方法主要用于在删除对象的ODB源之前或之后，访问对象的特定属性。
        它首先检查传入参数的类型，然后根据参数if_delete_odb_source的值决定是否删除对象的ODB源。
        如果指定了attribute_names参数，它会尝试访问对象上这些属性的值。
        
        :param obj: 有delete_odb_source()方法的待处理的对象实例。
        :type obj: object
        :param if_delete_odb_source: 布尔值，指示是否删除对象的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :param attribute_names: 可选参数，包含属性名称的序列，指示方法应访问的对象上的属性。
        :type attribute_names: Sequence[str]
        :return: 无直接返回值，但会根据attribute_names参数访问并使用（但不返回）对象的属性。
        :rtype: None
        """
        # 检查obj是否为对象实例
        check_type(obj, object)
        # 检查if_delete_odb_source是否为布尔值
        check_type(if_delete_odb_source, bool)

        # 如果attribute_names参数被提供，则检查其是否为字符串序列
        if attribute_names is not None:
            check_sequence_type(attribute_names, str)
            # 遍历attribute_names中的每个属性名称，尝试访问对象上相应的属性
            for attr_name in attribute_names:
                _ = get_nested_attribute(obj, attr_name)
        # 如果if_delete_odb_source为True，则调用对象的delete_odb_source方法删除ODB源
        if if_delete_odb_source:
            obj.delete_odb_source()

    def set_attributes(self, **kwargs):
        """
        动态设置对象的属性。

        该方法通过接受一系列关键字参数的形式，为对象动态地设置属性。如果关键字参数对应的属性已存在且为私有属性，
        则更新该私有属性的值；如果不存在，則直接设置为对象的属性。
        
        :param kwargs: 包含若干属性名-值对的关键字参数字典。
        :type kwargs: dict[str, Any]
        :return: 无返回值。
        :rtype: None
        """
        # 遍历关键字参数字典，为对象动态设置私有属性
        for attribute_name, value in kwargs.items():
            # 检查对象是否已有对应名称的私有属性
            if hasattr(self, "_" + attribute_name):
                # 更新私有属性的值
                setattr(self, "_" + attribute_name, value)
            else:
                # 设置新属性的值
                setattr(self, attribute_name, value)

    def delete_odb_source(self):
        """
        删除ODB数据源。

        通过将ODB数据源设置为None来删除它。这通常在不再需要ODB数据源时进行，
        以便释放与之相关的资源。
        
        :return: 无返回值。
        :rtype: None
        """
        # 将ODB数据源设置为None，表示删除或释放该数据源
        self._odb_source = None

    @property
    def odb_source(self):
        """
        获取ODB资源。

        该方法首先检查_odb_source属性是否已初始化，如果未初始化，
        则调用get_packaged_item_by_parent方法从父节点获取当前对象的odb资源。
        如果_ODB_SOURCE仍然为None，则抛出一个运行时错误，表明未找到ODB源。
        :return: 当前对象管理的odb资源对象
        :rtype: Any
        :raises RuntimeError: 如果_odb_source为None，则抛出一个运行时错误。
        """
        # 检查_ODB_SOURCE是否已初始化
        if self._odb_source is None:
            # 如果未初始化，则调用GET_PACKAGED_ITEM_BY_PARENT方法进行初始化
            self._odb_source = self.get_packaged_item_by_parent()

        # 再次检查_ODB_SOURCE是否为None
        if self._odb_source is not None:
            # 如果_ODB_SOURCE已初始化，则返回该值
            return self._odb_source

        # 如果_ODB_SOURCE仍然为None，则抛出一个运行时错误
        raise RuntimeError("No odb source found.")

    def get_packaged_item_by_parent(self):
        """
        通过父级对象获取当前对象的封装的odb对象，加载odb资源。

        :return: 重新由父项加载的当前对象封装的odb对象
        :rtype: Any
        """
        raise NotImplementedError


class PackagedOdb(_PackageBase):
    """
    该类用于封装和管理Abaqus的odb文件。
    它提供了初始化odb路径和资源、获取包装项、以及odb的生命周期管理等功能。
    """
    _odb_source_dict = {}

    def get_packaged_item_by_parent(self):
        """
        根据父节点获取打包后的条目。

        此方法未实现，因为当前对象是一个 odb 根节点，不存在父节点供参考。
        因此，没有可用的方法来根据父节点获取打包后的条目。

        Raises:
            NotImplementedError: 当尝试在odb根节点上调用此方法时，抛出异常。
        """
        raise NotImplementedError("The current object is an odb root node, there is no such method available")

    def __init__(self, odb_path=None, *args, **kwargs):
        """
        初始化PackagedOdb实例。

        :param odb_path: odb文件的路径，默认为None。
                如果未指定路径，则尝试从当前目录下查找odb文件。
                如果指定为文件夹的路径，则在此路径下搜索odb文件
        :type odb_path: str or None
        """
        super(PackagedOdb, self).__init__(*args, **kwargs)
        # 初始化odb路径和资源
        self.odb_path = None
        self.odb_name = None
        self._init_odb_path(odb_path)
        # self._odb_odb = None
        self._odb_steps = None
        self._packaged_root_assembly = None
        self._step_names = None
        # 发送进度信息
        self._logger.info("Open the abaqus output database named '{}' with path '{}'and step name: '{}'".format(
            self.odb_name, self.odb_path, self.step_names))
        self._progress_monitor.send_progress(self, message_type="init")
        self._abq_ext_manager.add_objects_to_be_closed(self)
        self.field_outputs_node_instance_label_index_dict = None
        self.field_outputs_element_instance_label_index_dict = None

    @property
    def name(self):
        """
        获取当前对象名称。
        
        :return: 当前对象名称。
        :rtype: str
        """
        if self._name is None:
            return self.odb_name
        return self._name

    @name.setter
    def name(self, value):
        """
        设置当前对象名称。
        
        :param value: 新名称。
        :return: 无返回值。
        """
        check_type(value, str, None)
        self._name = value

    @property
    def odb_source(self):
        """
        获取Odb实例的属性装饰器方法。

        该方法用作属性访问，以封装Odb实例的懒加载机制。
        它尝试在首次访问时打开Odb文件，并在失败时抛出异常。

        :return: Odb实例，如果成功打开的话。
        :rtype:Odb

        :raises:RuntimeError: 当尝试打开Odb文件失败时。
        """
        # 检查是否已经存在Odb实例，如果不存在则尝试创建
        if self._odb_source is None:
            if self.odb_path not in self._odb_source_dict:
                try:
                    # 尝试使用指定路径打开Odb文件
                    odb_source = openOdb(self.odb_path)
                    if odb_source is None:
                        raise RuntimeError("Failed to open ODB file: %s" % self.odb_path)
                except Exception as e:
                    # 如果打开Odb文件失败，抛出包含详细错误信息的异常
                    raise RuntimeError("Failed to open ODB file: %s. Error message: %s" % (self.odb_path, str(e)))
                self._odb_source_dict[self.odb_path] = odb_source
            self._odb_source = self._odb_source_dict[self.odb_path]
        return self._odb_source

    @property
    def odb_steps(self):
        """
        获取Odb实例的步骤属性装饰器方法。
        :return: Odb实例的步骤属性。
        :rtype:  dict[str, OdbStep]
        """
        if self._odb_steps is None:
            self._odb_steps = self.odb_source.steps
        return self._odb_steps

    @property
    def step_names(self):
        """
        获取步骤名称列表。
        
        :return: 步骤名称列表。
        :rtype: list[str]
        """
        if self._step_names is None:
            self._step_names = list(self.odb_steps.keys())
        return self._step_names

    def get_packaged_step_by_name(self, step_name):
        """
        根据步骤名称获取打包后的步骤对象。

        如果给定的步骤名称在步骤名称列表中不存在，则抛出一个 ValueError 异常，包含步骤名称和有效的步骤名称列表。
        如果步骤名称在打包步骤字典中不存在，则创建一个新的 PackagedStep 对象，并将其添加到打包步骤字典中。
        
        :param step_name: 要获取的步骤的名称。
        :type step_name: str
        :return: 打包后的步骤对象。
        :rtype: PackagedStep
        :raises ValueError: 如果给定的步骤名称在步骤名称列表中不存在。
        """
        check_type(step_name, str)
        # 检查步骤名称是否在步骤名称列表中
        if step_name not in self.step_names:
            raise ValueError(
                "step name: '{}' does not exist, valid step names are: '{}'".format(step_name, self.step_names))
        # 创建一个新的 PackagedStep 对象
        packaged_step = self._packaged_odb_object_factory.packaged_step_class(
            self.odb_steps[step_name], parent_node=self)
        # 返回打包后的步骤对象
        return packaged_step

    def get_packaged_step_by_index(self, step_index):
        """
        根据索引获取打包后的步骤。

        :param step_index: 步骤的索引
        :type step_index: int
        :return: 打包后的步骤对象
        :rtype: PackagedStep
        :raises IndexError: 如果索引超出范围
        """
        check_type(step_index, int)
        if not 0 <= step_index < len(self.step_names):
            raise IndexError(
                "step index:'{}' out of range: '{}',valid step names are: '{}'".
                format(step_index, len(self.step_names), self.step_names))
        return self.get_packaged_step_by_name(self.step_names[step_index])

    def get_packaged_step_by_name_or_index(self, step_name=None, step_index=None):
        """
        根据名称或索引获取打包的步骤。

        该函数允许通过名称或索引检索工作流中的特定步骤。
        如果同时提供了名称和索引，函数将优先使用名称来检索步骤。

        :param step_name: (str, 可选): 要检索的步骤的名称。默认为 None。
        :type step_name: str or None
        :param step_index: (int, 可选): 要检索的步骤的索引。默认为 None。
        :type step_index: int or None
        :return: 封装分析步对象对象。
        :rtype: PackagedStep

        :raises ValueError: 如果 step_name 和 step_index 都为 None，将引发 ValueError，表示至少需要提供一个参数。
        """
        # 检查是否两个参数都为 None
        if step_name is None and step_index is None:
            raise ValueError("step_name 和 step_index 不能同时为 None")

        # 如果提供了 step_name，则按名称检索步骤
        if step_name is not None:
            return self.get_packaged_step_by_name(step_name)

        # 否则按索引检索步骤
        return self.get_packaged_step_by_index(step_index)

    def _init_odb_path(self, odb_path):
        """
        初始化ODB文件路径。

        :param odb_path: ODB文件路径，如果为None，则使用当前工作目录作为搜索路径。
        :type odb_path: str or None
        :return: 无
        :rtype: None
        """
        # 初始化搜索路径为None
        search_path = None
        # 如果odb_path为None，使用当前工作目录作为搜索路径
        if odb_path is None:
            search_path = os.getcwd()
        # 如果odb_path是一个目录，直接使用它作为搜索路径
        elif os.path.isdir(odb_path):
            search_path = odb_path
        # 如果搜索路径不为空，尝试查找并设置ODB文件路径
        if search_path:
            # 尝试从当前目录下查找odb文件
            try:
                # 防止find_files_path_with_keyword返回空列表
                odb_paths = FileOperations.find_files_path_with_keyword(path=search_path, keyword=".odb")
                # 如果没有找到odb文件，抛出IOError异常
                if not odb_paths:
                    raise IOError("No.odb files found.")
                # 设置找到的第一个odb文件路径
                odb_path = odb_paths[0]
            except IndexError:
                # 如果列表为空，抛出IOError异常
                raise IOError("No.odb files found.")
        # 获取odb的绝对路径和文件名
        self.odb_path = os.path.abspath(odb_path)
        self.odb_name = os.path.basename(self.odb_path)

    def get_packaged_root_assembly(self):
        """
        返回包装后的根组件对象。

        如果当前对象的_packaged_root_assembly属性为空，则创建一个新的PackagedRootAssembly实例。
        这个实例将当前对象作为参数，并设置其parent_node属性为当前对象。

        :return: 当前对象的包装根组件实例
        :rtype: PackagedRootAssembly
        """
        # 检查是否已经存在包装根组件实例
        if self._packaged_root_assembly is None:
            # 如果不存在，则创建新的实例并设置其parent_node属性
            self._packaged_root_assembly = self._packaged_odb_object_factory.packaged_root_assembly_class(
                self.odb_source.rootAssembly)
            self._packaged_root_assembly.parent_node = self
        # 返回包装根组件实例
        return self._packaged_root_assembly

    def _release_source(self):
        if self.odb_path in self._odb_source_dict:
            del self._odb_source_dict[self.odb_path]

    def __enter__(self):
        """
        支持上下文管理器的进入操作。

        :return: 当前的PackagedOdb实例。
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支持上下文管理器的退出操作。

        :param exc_type: 异常类型。
        :param exc_val: 异常值。
        :param exc_tb: 异常追踪。
        """
        # 关闭odb资源
        if self.odb_source:
            self.odb_source.close()
        self._release_source()

    def close(self):
        """
        关闭操作函数

        本函数用于执行关闭操作，但在执行关闭操作之前，会通过进度监控器发送一个进度信息。当前仅发送进度信息，无其他操作

        :return: 无返回值
        """
        self._release_source()
        # 发送进度信息
        self._progress_monitor.send_progress(self, message_type="end")
        self._logger.info("Close the packaged odb named '{}'".format(self.odb_name))

    # def __del__(self):
    #     """
    #     当实例被销毁时，自动调用此方法以释放资源。
    #     """
    #     # self.__exit__(None, None, None)


class _GainOdbSet(_PackageBase):
    """
    含有节点集与单元集的输出数据库对象获取odb集合对象的功能的类，例如PackagedRootAssembly和PackagedInstance
    此类提供对象中集合名称管理、由名称获取封装odb集合、缓存访问过的集合的功能
    使用时需设置_packaged_root_assembly属性指定装配类
    """

    def get_packaged_item_by_parent(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        super(_GainOdbSet, self).__init__(*args, **kwargs)
        self.name = None
        self._odb_node_sets = None
        self._nodes_sets_names = None
        self._odb_element_sets = None
        self._element_sets_names = None
        self._packaged_root_assembly = None
        self._packaged_node_sets_dict = {}
        self._packaged_element_sets_dict = {}

    def get_packaged_item(self):
        pass

    @property
    def packaged_root_assembly(self):
        """
        获取包装根组件对象。
        
        :return: 包装根组件对象。
        :rtype: PackagedRootAssembly
        """
        if self._packaged_root_assembly is None:
            self._packaged_root_assembly = \
                self.get_specified_type_parent(self._packaged_odb_object_factory.packaged_root_assembly_class)
        return self._packaged_root_assembly

    @property
    def odb_node_set(self):
        """
        获取ABAQUS分析数据库中的节点集，子类重写此方法获取自己的节点集以使用本类中与节点集相关的操作

        :return: 返回节点集的实例。
        """
        raise NotImplementedError(
            "The subclass overrides this method to get its own node-set to use the node-set "
            "related operations in the class")

    @property
    def nodes_sets_names(self):
        """
        获取节点集的名称列表。

        :return: 节点集名称的列表。
        :rtype: list[str]
        """
        return list(self.odb_node_set.keys())

    def get_packaged_node_set_by_name(self, name):
        """
        通过名称获取打包的节点集。

        此函数确保节点集名称在实例中存在，并返回相应的打包节点集对象。
        如果节点集名称不存在，会抛出含有所有可用节点集名称的详细错误信息。
        访问过的节点集会缓存在一个字典中待下次使用
        
        :param name: 节点集的名称。
        :type name: str
        :return: 打包节点集对象。
        :rtype: PackagedOdbSet
        """
        # 检查节点集名称是否存在于实例中
        if name not in self.nodes_sets_names:
            if not self.nodes_sets_names:
                raise ValueError(
                    "node set name '{}' not found in instance '{}'\nnodes set names list is empty".
                    format(name, self.name))
            # 获取最长名称长度
            max_length = max(len(str(item)) for item in self.nodes_sets_names)
            # 构建所有节点集名称的字符串
            names_str = "".join("{:<{}}".format(name_, max_length) for name_ in self.nodes_sets_names)
            # 抛出详细的异常信息
            raise ValueError(
                "node set name '{}' not found in instance '{}'\nnodes set names are:\n{}".
                format(name, self.name, names_str))
        # 如果名称不在_packaged_node_sets_dict中且未被实例化，则实例化
        if name not in self._packaged_node_sets_dict:
            packaged_odb_set = self._packaged_odb_object_factory.packaged_odb_set_class(
                self.odb_node_set[name], name, True)
            packaged_odb_set.parent_node = self
            self._packaged_node_sets_dict[name] = packaged_odb_set
        return self._packaged_node_sets_dict[name]

    @property
    def odb_element_set(self):
        """
        获取ABAQUS分析数据库中的单元集，子类重写此方法获取自己的节点集以使用本类中与单元集相关的操作

        :return: 返回单元集的实例。
        """
        raise NotImplementedError(
            "The subclass overrides this method to get its own element-set to use the element-set "
            "related operations in the class")

    @property
    def element_sets_names(self):
        """
        获取单元集合的名称列表。

        :return: 单元集合名称的列表。
        :rtype: list[str]
        """
        return list(self.odb_element_set.keys())

    def get_packaged_element_set_by_name(self, name):
        """
        根据名称获取单元集。
        访问过的单元集会缓存在一个字典中待下次使用

        :param name: 单元集的名称
        :type name: str
        :return: 包含该名称的单元集
        :rtype: PackagedOdbSet
        """
        # 检查节点集名称是否存在于实例中
        if name not in self.element_sets_names:
            if not self.element_sets_names:
                raise ValueError(
                    "element set name '{}' not found in instance '{}'\nelements set names list is empty".
                    format(name, self.name))
            # 获取最长名称长度
            max_length = max(len(str(item)) for item in self.element_sets_names)
            # 构建所有节点集名称的字符串
            names_str = "".join("{:<{}}".format(name_, max_length) for name_ in self.element_sets_names)
            # 抛出详细的异常信息
            raise ValueError(
                "element set name '{}' not found in instance '{}'\nelements set names are:\n{}".
                format(name, self.name, names_str))
        if name not in self._packaged_element_sets_dict:
            packaged_odb_set = self._packaged_odb_object_factory.packaged_odb_set_class(
                self.odb_element_set[name], name, False)
            packaged_odb_set.parent_node = self
            self._packaged_element_sets_dict[name] = packaged_odb_set
        return self._packaged_element_sets_dict[name]

    @staticmethod
    def auto_create_set_name(name, names):
        """
        自动创建一个不重复的名字。

        通过在原有名字后添加索引来确保名字在给定的名字集合中是唯一的。
        
        :param name: 原始名字。
        :type name: str
        :param names: 包含现有名字的集合。
        :type names: list[str]
        :return: 一个不重复的名字。
        :rtype: str
        """
        # 检查输入的name是否为字符串类型
        check_type(name, str)

        i = 0
        while True:
            # 如果当前名字在已有的名字集合中，生成一个新的名字，格式为"原始名字_索引"
            if name in names:
                name = "{}_{}".format(name, i + len(names))
            else:
                # 如果生成的名字是唯一的，停止循环
                break
            i += 1
        return name


class _OdbNodesElementsOptions(_PackageBase):
    """
    对于有OdbMeshNodeArray和OdbMeshNodeArray属性的封装Odb对象，此类提供节点与单元的通用操作。
    继承此类后重写odb_elements、odb_nodes两方法，获取当前对象中的节点与单元Odb对象以使用本类中提供的功能。
    """

    def get_packaged_item_by_parent(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        super(_OdbNodesElementsOptions, self).__init__(*args, **kwargs)
        self.name = None
        self._odb_nodes = None
        self._nodes_length = None
        self._odb_elements = None
        self._elements_length = None
        self._node_coordinates_np = None
        self._node_bounds = None
        self._element_coordinates_np = None
        self._element_bounds = None
        self._elements_kd_tree = None
        self._nodes_kd_tree = None
        self._packaged_nodes = None
        self._packaged_elements = None
        self._instance_name_label_nodes_dict = None
        self._instance_name_label_elements_dict = None

        self._packaged_root_assembly = None

    @property
    def packaged_root_assembly(self):
        """
        获取封装根装配件对象。
        
        :return: 封装根装配件对象。
        :rtype: PackagedRootAssembly
        """
        if self._packaged_root_assembly is None:
            self._packaged_root_assembly = self.get_specified_type_parent(PackagedRootAssembly)
        return self._packaged_root_assembly

    def get_packaged_nodes(self, if_delete_odb_source=True, attribute_names=None):
        """
        获取并缓存打包后的所有节点的列表。本类对象中其他获取结点的方法均基于此方法。

        本函数负责根据给定的参数，从系统中获取所有节点，并根据需求处理这些节点。
        如果设置了attribute_names参数，将预加载这些属性在每个节点中。
        此外，如果if_delete_odb_source参数为True，将删除每个节点的ODB源。
        使用父节点中的PackagedRootAssembly对象的set_field_value_index_of_packaged_nodes()方法
        设置packaged_nodes的几何节点对应的场输出数据节点的索引属性。
        
        :param if_delete_odb_source: 一个布尔值，指示是否删除封装节点对象的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :param attribute_names: 一个包含属性名称的迭代器，指示需要在封装节点对象中加载的属性，
                默认为None，加载预定义的属性:["coordinates","instance_name","label"]，传入列表时，加载设定的属性。
        :type attribute_names: list[str]
        :return: 一个包含所有打包后节点的列表。
        :rtype: list[PackagedOdbNode]
        """
        # 如果尚未初始化_packaged_nodes，则从头开始获取所有节点
        if self._packaged_nodes is None:
            if attribute_names is None:
                attribute_names = ["coordinates", "instance_name", "label"]  # 初始化_packaged_nodes列表
            self._packaged_nodes = []
            # 遍历所有节点进行处理
            for packaged_node in self.get_every_node():
                self._accessing_attributes_and_delete_odb_source(packaged_node, if_delete_odb_source, attribute_names)
                # 将处理后的节点添加到列表中
                self._packaged_nodes.append(packaged_node)
        # 返回打包后的节点列表
        return self._packaged_nodes

    def get_packaged_elements(self, if_delete_odb_source=True, attribute_names=None):
        """
        获取并缓存所有单元的列表。本类对象的其他获取单元的方法都基于此方法。

        本函数负责根据条件处理一组单元，处理包括可能的删除odb源以及访问指定的属性。
        如果尚未初始化_packaged_elements，则从头开始获取所有单元，并对每个单元进行处理。
        
        :param if_delete_odb_source: 是否删除odb源，默认为True。
        :type if_delete_odb_source: bool
        :param attribute_names: 一个包含要加载的属性名称的列表，如果需要加载封装单元对象的特定属性。
                    为空时，默认为["instance_name", "label", "type", "mean_coordinate"]
        :type attribute_names: list[str]
        :return: 一个包含所有处理后的单元的列表。
        :rtype: list[PackagedOdbElement]
        """
        # 如果尚未初始化_packaged_elements，则从头开始获取所有单元
        if self._packaged_elements is None:
            if attribute_names is None:
                attribute_names = ["instance_name", "label", "type", "mean_coordinate"]
            self._packaged_elements = []
            # 遍历每个单元，进行必要的处理
            for packaged_element in self.get_every_element():
                # 对每个单元进行处理，包括可能的删除odb源和访问属性
                self._accessing_attributes_and_delete_odb_source(packaged_element, if_delete_odb_source,
                                                                 attribute_names)
                # 将处理后的单元添加到列表中
                self._packaged_elements.append(packaged_element)
        # 返回处理后的单元列表
        return self._packaged_elements

    @property
    def nodes_kd_tree(self):
        """
        返回节点的KD树表示。如果尚未创建，则先构建KD树。

        :return: KDTree对象，表示节点的KD树表示。
        :rtype: KDTree
        """
        if self._nodes_kd_tree is None:
            # 如果KD树尚未构建，则使用节点坐标构建KD树
            self._nodes_kd_tree = KDTree(self.node_coordinates_np)
        return self._nodes_kd_tree

    def get_nodes_by_coordinates(self, coordinates):
        """
        根据坐标获取节点。

        本函数通过KD树查询给定坐标附近的节点。它使用KD树进行高效的空间搜索，
        找到距离给定坐标最近的节点并返回。

        :param coordinates: 坐标列表，用于查询附近的节点。
        :return: 包含附近节点的列表，按距离排序。
        """
        # 使用KD树查询坐标，返回距离和索引
        distances, indices = self.nodes_kd_tree.query(np.array(coordinates))
        # 根据索引返回打包好的节点列表
        return [self.get_packaged_nodes()[index] for index in indices]

    def get_node_by_instance_name_and_label(self, instance_name, label):
        """
        根据实例名称和标签获取节点。

        本函数通过实例名称和节点标签从字典中获取对应的节点对象。如果字典未初始化，
        则会遍历所有封装的节点，并根据实例名称和标签建立索引。

        :param instance_name: 节点所属的实例名称。
        :type instance_name: str
        :param label: 节点的标签。
        :type label: str
        :return: 匹配的节点对象。如果不存在，则抛出异常。
        :rtype: PackagedOdbNode
        :raises: 如果同一实例中的节点标签重复，将抛出异常。
        """
        # 检查字典是否已初始化，未初始化则进行初始化
        if self._instance_name_label_nodes_dict is None:
            self._instance_name_label_nodes_dict = {}
            # 遍历所有封装的节点，根据实例名称和标签建立索引
            for packaged_node in self.get_packaged_nodes():
                # 如果实例名称不在字典中，则添加实例名称作为键
                if packaged_node.instance_name not in self._instance_name_label_nodes_dict:
                    self._instance_name_label_nodes_dict[packaged_node.instance_name] = {}
                    # 检查该实例下是否已存在相同的标签，如果存在则抛出异常
                if packaged_node.label not in self._instance_name_label_nodes_dict[packaged_node.instance_name]:
                    self._instance_name_label_nodes_dict[packaged_node.instance_name][
                        packaged_node.label] = packaged_node
                else:
                    raise Exception(
                        "The labels of nodes in the same instance are repeated. "
                        "The current operation only supports unique node numbers in the same instance")
        # 返回匹配的节点对象
        return self._instance_name_label_nodes_dict[instance_name][label]

    @property
    def elements_kd_tree(self):
        """
        构建或返回单元坐标KD树

        此属性用于构建或获取一个KD树，该KD树是基于单元的坐标构建的。
        KD树是一种空间分割数据结构，用于组织多维空间中的点，以便进行
        高效的最近邻查询等操作。

        :return: 构建好的KD树实例，如果之前已构建，则返回已构建的实例
        :rtype: KDTree
        """
        if self._elements_kd_tree is None:
            # 如果KD树尚未构建，则使用单元坐标构建KD树
            self._elements_kd_tree = KDTree(self.element_coordinates_np)
        return self._elements_kd_tree

    def get_elements_by_coordinates(self, coordinates):
        """
        根据给定的坐标获取单元列表。

        该方法通过KD树查询最接近的单元坐标，并返回这些单元。
        KD树是一种空间分割树，可以用于多维空间的数据搜索。

        :param coordinates: 坐标元组，用于查询单元。
        :return: 单元列表，包含与给定坐标最接近的单元。
        :rtype: list[PackagedOdbElement]
        """
        # 使用KD树查询坐标，返回距离和索引
        distances, indices = self.elements_kd_tree.query(np.array(coordinates))
        # 根据索引返回打包好的节点列表
        return [self.get_packaged_elements()[index] for index in indices]

    def get_element_by_instance_name_and_label(self, instance_name, label):
        """
        根据实例名称和标签获取单元。

        本函数通过实例名称和标签从packaged_elements中获取特定的单元。它首先检查一个缓存字典，
        该字典存储了根据实例名称和标签的单元映射。如果缓存未初始化，则遍历所有打包的单元并填充缓存。
        该方法保证了在相同实例名称下标签的唯一性。

        :param instance_name: 实例的名称，用于在缓存中定位单元。
        :type instance_name: str
        :param label: 单元的标签，用于精确匹配所需的单元。
        :type label: str
        :return: 匹配给定实例名称和标签的单元。
        :rtype: PackagedOdbElement
        :raises Exception: 如果检测到相同实例名称下标签重复，则抛出异常。
        """
        # 检查缓存字典是否为空，为空则初始化并填充。
        if self._instance_name_label_elements_dict is None:
            self._instance_name_label_elements_dict = {}
            # 遍历所有打包的单元，填充缓存字典。
            for packaged_element in self.get_packaged_elements():
                # 如果实例名称不在缓存字典中，则初始化该实例名称的条目。
                if packaged_element.instance_name not in self._instance_name_label_elements_dict:
                    self._instance_name_label_elements_dict[packaged_element.instance_name] = {}
                # 检查标签是否已经存在，确保标签的唯一性。
                if packaged_element.label not in self._instance_name_label_elements_dict[
                    packaged_element.instance_name]:
                    self._instance_name_label_elements_dict[packaged_element.instance_name][
                        packaged_element.label] = packaged_element
                else:
                    # 如果检测到标签重复，抛出异常。
                    raise Exception(
                        "The labels of elements in the same instance are repeated. "
                        "The current operation only supports unique element numbers in the same instance")
        # 返回通过实例名称和标签定位的单元。
        return self._instance_name_label_elements_dict[instance_name][label]

    @property
    def node_coordinates_np(self):
        """
        获取所有节点坐标的Numpy数组

        :return: 如果 `_node_coordinates_np` 为空，则计算并返回所有节点的坐标Numpy数组；
                 否则直接返回已缓存的 `_node_coordinates_np`。
        :rtype: numpy.ndarray
        """
        # 检查是否已缓存节点坐标Numpy数组，如果没有则需要重新计算
        if self._node_coordinates_np is None:
            # 通过遍历所有节点，收集每个节点的坐标，然后将这些坐标转换为Numpy数组以提高计算效率
            self._node_coordinates_np = np.array([np.array(node.coordinates) for node in self.get_packaged_nodes()])
        # 返回缓存的节点坐标Numpy数组
        return self._node_coordinates_np

    @property
    def element_coordinates_np(self):
        """
        获取所有单元平均坐标的Numpy数组
        :return: 如果 `_element_coordinates_np` 为空，则计算并返回所有单元平均坐标的Numpy数组；
        :rtype: numpy.ndarray
        """
        if self._element_coordinates_np is None:
            self._element_coordinates_np = np.array(
                [np.array(element.mean_coordinate) for element in self.get_packaged_elements()])
        return self._element_coordinates_np

    @staticmethod
    def _get_bounds(coordinates_np):
        """
        计算三维坐标的边界

        :param coordinates_np: 形状为 (n, 3) 的 NumPy 数组，其中 n 是点的数量，3 表示 (x, y, z) 坐标
        :type coordinates_np: numpy.ndarray
        :return: 形状为 (3, 2) 的 NumPy 数组，表示每个坐标轴的最小值和最大值
        :rtype: numpy.ndarray
        """
        # 使用 NumPy 的 amin 和 amax 函数计算每个坐标轴的上下限
        bounds = np.array([
            [np.amin(coordinates_np[:, 0]), np.amax(coordinates_np[:, 0])],
            [np.amin(coordinates_np[:, 1]), np.amax(coordinates_np[:, 1])],
            [np.amin(coordinates_np[:, 2]), np.amax(coordinates_np[:, 2])]
        ])
        return bounds

    @property
    def element_bounds(self):
        """
        计算并返回单元的边界

        如果单元的边界尚未计算，则使用单元的坐标数组计算边界

        :return: 单元的边界
        :rtype: numpy.ndarray
        """
        if self._element_bounds is None:
            # 如果边界尚未计算，则基于单元的坐标数组计算边界
            self._element_bounds = self._get_bounds(self.element_coordinates_np)
        return self._element_bounds

    @property
    def node_bounds(self):
        """
        计算并返回节点坐标的边界。

        该方法会返回每个坐标轴（x, y, z）的最小和最大值，形成边界框。

        :return: 边界框的numpy数组，形状为(3, 2)，其中每一行分别表示
                 x, y, z轴的最小和最大值。
        :rtype: numpy.ndarray
        """
        if self._node_bounds is None:
            self._node_bounds = self._get_bounds(self.node_coordinates_np)
        return self._node_bounds

    @property
    def odb_nodes(self):
        """
        获取节点信息。

        本方法用作属性访问器，确保外部访问节点信息时，
        可以通过节点属性透明地获取所需信息。
        子类需根据自身获取节点属性的不同方式重写此获取结点的方法后可使用本类的功能。

        如果子类未重写此方法，则会抛出异常。

        :return: OdbMeshNodeArray object
        :rtype: OdbMeshNodeArray
        """
        raise NotImplementedError(
            "This method needs to be overridden by subclasses to provide specific node information.")

    def get_odb_node_by_index(self, index):
        """
        通过索引获取odb几何节点对象。
        
        :param index: 索引
        :type index: int
        :return: odb几何节点对象
        :rtype: OdbMeshNode
        """
        raise NotImplementedError(
            "This method needs to be overridden by subclasses to provide specific node information.")

    def get_odb_element_by_index(self, index):
        """
        通过索引获取odb单元对象。
        
        :param index: 索引
        :type index: int
        :return: odb单元对象
        :rtype: OdbMeshElement
        """
        raise NotImplementedError(
            "This method needs to be overridden by subclasses to provide specific node information.")

    @property
    def nodes_length(self):
        """
        返回节点的数量。

        该属性通过计算节点列表的长度来获取节点数量，并缓存该值以避免重复计算。

        :return: 节点的数量。
        :rtype: int
        """
        # 如果节点数量尚未被缓存
        if self._nodes_length is None:
            # 通过计算节点列表的长度来获取节点数量，并将结果缓存
            self._nodes_length = len(self.get_packaged_nodes())
        # 返回缓存的节点数量
        return self._nodes_length

    @property
    def odb_elements(self):
        """
        获取单元信息。

        本方法用作属性访问器，确保外部访问单元信息时，
        可以通过单元属性透明地获取所需信息。
        子类需根据自身获取单元属性的不同方式重写此获取单元的方法后可使用本类的功能。


        :return: OdbMeshElementArray object
        :rtype:  list[OdbMeshElement]
        """
        raise NotImplementedError(
            "This method needs to be overridden by subclasses to provide specific element information.")

    @property
    def elements_length(self):
        """
        返回单元列表的长度

        :return: 单元列表的长度，如果之前没有计算过，则计算并保存长度
        :rtype: int
        """
        # 检查是否已经计算过单元列表的长度，如果没有，则进行计算
        if self._elements_length is None:
            self._elements_length = len(self.get_packaged_elements())
        # 返回保存的单元列表长度
        return self._elements_length

    def creat_packaged_node(self, odb_node, index):
        """
        创建一个包装过的节点。

        本方法用于将给定的原始节点包装成一个特定类的实例，以便于管理和使用。
        如果未指定特定的包装节点类，则使用默认的 PackagedNode 类。
        
        :param odb_node: 原始节点对象，需要被包装。
        :type odb_node: OdbMeshNode
        :param index: 节点在odb保存节点的序列中的索引或位置，用于唯一标识该节点。
        :type index: int
        :return: 创建并关联的一个包装过的节点实例。
        :rtype: PackagedNode
        """
        # 创建指定类的实例，使用提供的原始节点和索引
        packaged_node = self._packaged_odb_object_factory.packaged_node_class(odb_node, index)
        # 设置新创建的包装节点的父节点为当前实例，建立父子关系
        packaged_node.parent_node = self
        return packaged_node

    def get_every_node(self):
        """
        生成每个节点的包装对象。

        通过遍历实例中的所有节点，返回每个节点的包装对象。

        :yield: PackagedNode对象，代表每个节点的包装。
        :rtype: Generator[PackagedNode, None, None]
        """
        i = 0
        for node in iterate_deep(self.odb_nodes):
            yield self.creat_packaged_node(node, i)
            i += 1

    def creat_packaged_element(self, odb_element, index):
        """
        创建一个包装后的单元。

        该方法用于将给定的ODB单元包装成一个特定类的实例，以便在当前上下文中使用。
        如果未提供自定义的包装类，则使用默认的PackagedElement类。
        
        :param odb_element: 要包装的ODB几何单元对象。
        :type odb_element: OdbMeshElement
        :param index: 索引
        :type index: int
        :return: 返回一个包装后的几何单元对象。
        :rtype: PackagedElement
        """
        # 创建并初始化包装后的单元实例
        packaged_element = self._packaged_odb_object_factory.packaged_element_class(odb_element, index)

        # 设置包装后单元的父节点为当前实例，以维护单元间的层级关系
        packaged_element.parent_node = self

        # 返回创建的包装后单元实例
        return packaged_element

    def get_every_element(self):
        """
        获取序列中的每个单元，并包装为PackagedElement对象。
        跳过实例名称为空的单元，此类单元为在装配模块中定义的参考点。

        本函数通过遍历单元序列，为每个单元添加索引信息，然后以生成器的方式返回包装后的单元。
        这样做可以在不一次性加载所有单元的情况下，仍然能够处理每个单元，节省内存。

        :return: 生成的PackagedElement对象，其中包含了单元值和单元在序列中的索引。
        :rtype: Generator[PackagedElement, None, None]
        """
        # 遍历项目中的每一个单元，使用enumerate和自定义的深层遍历函数
        for index, element in enumerate(iterate_deep(self.odb_elements)):
            # 将单元及其索引打包到自定义的PackagedElement对象中
            packaged_element = self.creat_packaged_element(element, index)
            # 如果单元的实例名称为空，则跳过该单元
            if len(packaged_element.instance_name) == 0:
                continue
            # 设置打包的网格对象，并返回生成器
            yield packaged_element


class PackagedRootAssembly(_GainOdbSet, _OdbNodesElementsOptions):
    """
    代表一个包装后的实例集合，继承自PackageBase。

    该类用于管理特定包装数据库中的实例。
    """
    rootAssembly_name = "rootAssembly"

    def get_packaged_item_by_parent(self):
        packaged_odb = self.get_parent()
        return packaged_odb.get_packaged_root_assembly()

    @property
    def odb_node_set(self):
        """
        获取odb节点集对象
        :return: odb节点集对象
        :rtype: dict[str, OdbSet]
        """
        if self._odb_node_sets is None:
            self._odb_node_sets = self.odb_source.nodeSets
        return self._odb_node_sets

    @property
    def odb_element_set(self):
        """
        获取odb单元集对象
        :return: odb单元集对象
        :rtype: dict[str, OdbSet]
        """
        if self._odb_element_sets is None:
            self._odb_element_sets = self.odb_source.elementSets
        return self._odb_element_sets

    def __init__(self, odb_source, *args, **kwargs):
        """
        初始化PackagedRootAssembly对象。

        :param odb_source: 包装后的数据库对象，包含实例信息。
        """

        # 存储包装后的数据库对象
        super(PackagedRootAssembly, self).__init__(*args, **kwargs)
        self.name = "rootAssembly"
        self._packaged_root_assembly = self
        self._odb_source = odb_source
        # 获取根组件的实例列表
        self.odb_instances = self.odb_source.instances
        # 计算实例的数量
        self.instances_length = len(self.odb_instances)
        # 获取实例名称的列表
        self._instance_names = None
        self._packaged_instance_dict = OrderedDict()
        # 查询最近节点与单元所用所用的kd树
        self._nodes_kd_tree = {}
        self._elements_kd_tree = {}
        self._logger.info("Open rootAssembly with instance names:'{}'".format(self.instance_names))

    @property
    def instance_names(self):
        """
        获取实例名称列表。
        :return: 实例名称列表
        :rtype: list[str]
        """
        if self._instance_names is None:
            self._instance_names = list(self.odb_instances.keys())
        return self._instance_names

    def get_every_instance(self):
        """
        遍历所有实例并生成包装后的实例对象。

        该方法使用yield语句生成器形式返回每个实例，而不是一次性返回所有实例的列表。
        这样做可以节省内存，特别是当实例数量很大时，并且允许调用者逐个处理实例。

        生成的实例是通过PackagedInstance类包装的。
        :return: 一个生成器，每次迭代产生一个PackagedInstance对象。
        :rtype: Generator[PackagedInstance]
        """
        for instance_name in self.instance_names:
            yield self.get_instance_by_name(instance_name)

    @property
    def packaged_instances(self):
        """
        获取所有实例的列表

        该属性方法返回调用`get_every_instance`方法获取的所有实例列表。

        :return: 实例列表
        :rtype: list[PackagedInstance]
        """
        return list(self.get_every_instance())

    def get_instance_by_name(self, instance_name):
        """
        根据实例名称获取包装后的实例对象。

        :param instance_name: 实例的名称。
        :type instance_name: str
        :return: 包装后的实例对象。
        :rtype: PackagedInstance
        :raises KeyError: 如果实例名称不存在。
        """
        try:
            if instance_name == self.rootAssembly_name:
                return self
            if instance_name not in self._packaged_instance_dict:
                # 尝试根据实例名称获取实例对象
                instance = self.odb_instances[instance_name]
                # 返回包装后的实例对象
                packaged_instance = self._packaged_odb_object_factory.packaged_instance_class(instance)
                packaged_instance.parent_node = self
                self._packaged_instance_dict[instance_name] = packaged_instance
            return self._packaged_instance_dict[instance_name]
        except KeyError:
            # 如果实例名称不存在，抛出KeyError异常
            raise KeyError("Instance name:'{}' not found. names are{}".format(instance_name, str(self.instance_names)))

    def get_instance_by_index(self, index):
        """
        根据索引获取包装后的实例对象。

        :param index: 实例的索引。
        :return: 包装后的实例对象。
        :raises IndexError: 如果索引超出范围。
        """
        # 检查索引是否在有效范围内
        if not 0 <= index < self.instances_length:
            # 如果索引超出范围，抛出IndexError异常
            raise IndexError("index {} is out of range.".format(index))
        # 根据索引获取实例名称，并通过名称获取实例对象
        instance_name = self.instance_names[index]
        return self.get_instance_by_name(instance_name)

    def get_node_by_instance_name_and_label(self, instance_name, label):
        """
        通过实例名称和标签获取节点。

        本函数旨在通过指定的实例名称和标签来获取特定的节点。首先，它会设置节点实例的索引，
        然后通过实例名称获取相应的实例。接着，利用获取的实例和相同的实例名称及标签，从中提取
        对应的节点，并更新该节点的场输出数据索引。最后，返回更新后的节点。

        :param instance_name: 实例的名称，用于定位特定的实例。
        :param label: 节点的标签，用于进一步定位特定的节点。
        :return: 包装后的节点对象，包含更新的场输出值索引。
        """
        # 通过实例名称获取实例对象
        packaged_instance = self.get_instance_by_name(instance_name)
        # 通过实例名称和标签获取节点对象
        packaged_node = packaged_instance.get_node_by_instance_name_and_label(instance_name, label)
        # 返回包装后的节点对象
        return packaged_node

    def get_node_set_by_name(self, set_name, instance_name=None):
        """
        根据集合名称和实例名称获取节点集合。
        
        :param set_name: 要查找的节点集合的名称。
        :type set_name: str
        :param instance_name: 要查找的实例名称。如果为None，则在所有实例中查找。
        :type instance_name: str, optional
        :return: 找到的节点集合对象。
        :rtype: NodeSet
        :raises ValueError: 如果未找到指定的节点集合。
        """
        check_type(set_name, str)
        check_type(instance_name, str, None)
        node_set = None
        if instance_name is None:
            # 从装配中获取
            try:
                node_set = self.get_packaged_node_set_by_name(set_name)
            except ValueError:
                pass
            # 如果instance_name为None，则在所有实例中查找名为set_name的集合
            instances = self.get_every_instance()
            for instance in instances:
                try:
                    node_set = instance.get_packaged_node_set_by_name(set_name)
                    break
                except ValueError:
                    continue
            if node_set is None:
                raise ValueError("Set '{}' not found in rootAssembly or any instance.".format(set_name))
        else:
            # 如果instance_name和set_name都不为None，则在指定实例中查找名为set_name的集合
            instance = self.get_instance_by_name(instance_name)
            try:
                node_set = instance.get_packaged_node_set_by_name(set_name)
            except ValueError:
                raise ValueError("Set '{}' not found in instance '{}'.".format(set_name, instance_name))
        return node_set

    def get_element_set_by_name(self, set_name, instance_name=None):
        """
        根据集合名称和实例名称获取单元集合。
        
        :param set_name: 要查找的单元集合的名称。
        :type set_name: str
        :param instance_name: 要查找的实例名称。如果为None，则在所有实例中查找。
        :type instance_name: str, optional
        :return: 找到的单元集合对象。
        :rtype: ElementSet
        :raises ValueError: 如果未找到指定的单元集合。
        """
        check_type(set_name, str)
        check_type(instance_name, str, None)
        element_set = None
        if instance_name is None:
            # 从装配中获取
            try:
                element_set = self.get_packaged_element_set_by_name(set_name)
            except ValueError:
                pass
            # 如果instance_name为None，则在所有实例中查找名为set_name的集合
            instances = self.get_every_instance()
            for instance in instances:
                try:
                    element_set = instance.get_packaged_element_set_by_name(set_name)
                    break
                except ValueError:
                    continue
            if element_set is None:
                raise ValueError("Set '{}' not found in rootAssembly or any instance.".format(set_name))
        else:
            # 如果instance_name和set_name都不为None，则在指定实例中查找名为set_name的集合
            instance = self.get_instance_by_name(instance_name)
            try:
                element_set = instance.get_packaged_element_set_by_name(set_name)
            except ValueError:
                raise ValueError("Set '{}' not found in instance '{}'.".format(set_name, instance_name))
        return element_set

    def get_node_by_coordinate(self, coordinates, instance_name=None, set_name=None):
        """
        根据实例名称与集合名称和坐标获取节点。
        实例名称与集合名称至少设定一项。
            只指定了实例名称就从实例中的所有结点找目标值。
            只设定了集合名称就先从在装配中创建的集合中找指定集合，再从每个实例中找指定集合，最后从指定集合的所有节点中找目标值。
            两者都设定了就只在指定实例中找指定集合，再找目标结点。
            未找到目标值均会抛出异常。

        :param coordinates: 三维坐标tuple或list或np.ndarray的列表
        :param instance_name: 实例名称
        :param set_name: 集合名称
        :return: 匹配的节点
        """
        if not all([isinstance(coord, (tuple, list, np.ndarray)) and len(coord) == 3 for coord in coordinates]):
            raise Exception("coordinates must be a list of tuples or lists or numpy.ndarray with length 3.")
        # 获取节点容器
        nodes_container = self.get_node_container_by_instance_name_and_set_name(instance_name, set_name)
        # 将coordinates转换为numpy数组格式，以方便后续处理
        coordinates = np.array([np.array(coordinate) for coordinate in coordinates])
        packaged_nodes = nodes_container.get_nodes_by_coordinates(coordinates)
        return packaged_nodes

    def get_node_container_by_instance_name_and_set_name(self, instance_name=None, set_name=None):
        """
        根据实例名称和集合名称获取节点容器。

        该函数根据提供的实例名称和集合名称来定位并返回相应的节点容器（例如节点集）。
        它根据实例名称和集合名称参数的存在与否，决定返回哪种类型的集合。

        :param instance_name: 实例的名称。如果为 None，则表示未指定实例名称。
        :param set_name: 集合的名称。如果为 None，则表示未指定集合名称。
        :return: 节点容器: 根据实例名称和集合名称返回相应的节点容器。具体的返回类型取决于所调用方法的实现。
        :rtype: PackagedOdbSet|PackagedInstance
        """
        # 检查 instance_name 和 set_name 是否均为 None，如果是，则抛出错误
        if instance_name is None and set_name is None:
            raise ValueError("instance_name 和 set_name 不能同时为 None。")
        # 验证 instance_name 和 set_name 的类型，确保它们是 str 或 None
        check_type(instance_name, str, None)
        check_type(set_name, str, None)
        # 如果 instance_name 为 None，尝试通过 set_name 获取节点集
        if instance_name is None:
            return self.get_node_set_by_name(set_name)
        else:
            # 如果 set_name 为 None，尝试通过 instance_name 获取节点集
            if set_name is None:
                return self.get_instance_by_name(instance_name)
            else:
                # 如果 instance_name 和 set_name 均已提供，尝试获取指定实例下的节点集
                return self.get_node_set_by_name(set_name, instance_name)

    def get_element_container_by_instance_name_and_set_name(self, instance_name=None, set_name=None):
        """
        根据实例名称和集合名称获取单元容器。

        该函数根据提供的实例名称和集合名称来定位并返回相应的单元容器（例如单元集或节点集）。
        它根据实例名称和集合名称参数的存在与否，决定返回哪种类型的集合。

        :param instance_name: 实例的名称。如果为 None，则表示未指定实例名称。
        :param set_name: 集合的名称。如果为 None，则表示未指定集合名称。
        :return: 单元容器: 根据实例名称和集合名称返回相应的单元容器。
        :rtype: PackagedOdbSet|PackagedInstance
        """
        # 检查 instance_name 和 set_name 是否均为 None，如果是，则抛出错误
        if instance_name is None and set_name is None:
            raise ValueError("instance_name 和 set_name 不能同时为 None。")
        # 验证 instance_name 和 set_name 的类型，确保它们是 str 或 None
        check_type(instance_name, str, None)
        check_type(set_name, str, None)
        # 如果 instance_name 为 None，尝试通过 set_name 获取节点集
        if instance_name is None:
            return self.get_element_set_by_name(set_name)
        else:
            # 如果 set_name 为 None，尝试通过 instance_name 获取单元集
            if set_name is None:
                return self.get_instance_by_name(instance_name)
            else:
                # 如果 instance_name 和 set_name 均已提供，尝试获取指定实例下的节点集
                return self.get_element_set_by_name(set_name, instance_name)

    def get_element_by_instance_name_and_label(self, instance_name, label):
        """
        通过实例名称和标签获取单元。

        该函数首先验证packaged_field_values参数是否为PackagedFieldValues类型。然后，通过instance_name参数从当前对象中获取对应的PackagedInstance。
        接着，从获取到的PackagedInstance中根据instance_name和label参数获取特定的单元。最后，利用packaged_field_values设置索引到获取的单元上，并返回这个处理后的单元。

        :param instance_name: 实例的名称，用于定位特定的PackagedInstance。
        :param label: 单元的标签，与instance_name一起用于定位具体的单元。
        :return: 处理后的单元对象。
        :raises: 如果packaged_field_values不是PackagedFieldValues类型，抛出异常。
        """
        # 通过实例名称获取对应的PackagedInstance
        packaged_instance = self.get_instance_by_name(instance_name)
        # 通过实例名称和标签从PackagedInstance中获取单元
        packaged_element = packaged_instance.get_element_by_instance_name_and_label(instance_name, label)
        # 返回处理后的单元
        return packaged_element

    def get_elements_by_coordinates(
            self, coordinates, instance_name=None, set_name=None):
        """
        根据实例名称和集合名称和坐标获取单元。
        实例名称与集合名称至少设定一项。
            只指定了实例名称就从实例中的所有结点找目标值。
            只设定了集合名称就先从在装配中创建的集合中找指定集合，再从每个实例中找指定集合，最后从指定集合的所有节点中找目标值。
            两者都设定了就只在指定实例中找指定集合，再找目标结点。
            未找到目标值均会抛出异常。

        该方法通过给定的坐标和实例名称，从指定实例中查找最近的单元。
        它使用KD树来加速坐标点的查询过程，并为找到的单元设置field_value_indexes。
        :param set_name: 集合名称
        :param coordinates: 一个坐标列表，每个坐标对应于要查询的位置。
        :param instance_name: 实例的名称。
        :return: 一个包含查询到的单元的列表，这些单元已经根据给定的坐标和实例名称进行了处理和筛选。
        :raises Exception: 如果packaged_field_values不是PackagedFieldValues类型，则抛出异常。
        """

        # 将coordinates转换为numpy数组格式，以方便后续处理
        coordinates = np.array([np.array(coordinate) for coordinate in coordinates])
        elements_container = self.get_element_container_by_instance_name_and_set_name(instance_name, set_name)
        packaged_elements = elements_container.get_elements_by_coordinates(coordinates)
        return packaged_elements

    def create_node_set_from_coordinates(self, created_set_name, coordinates, instance_name=None, set_name=None):
        """
        根据实例名称和集合名称和坐标获取结点。
        实例名称与集合名称至少设定一项。
            只指定了实例名称就从实例中的所有结点找目标值。
            只设定了集合名称就先从在装配中创建的集合中找指定集合，再从每个实例中找指定集合，最后从指定集合的所有节点中找目标值。
            两者都设定了就只在指定实例中找指定集合，再找目标结点。
            未找到目标值均会抛出异常。
            
        :param created_set_name: 要创建的节点集的名称。
        :param coordinates: 一个坐标列表，每个坐标对应于要查询的位置
        :param coordinates: 用于查找节点的坐标。
        :param set_name: 集合名称，用于指定特定的集合。默认为None。
        :param instance_name: 实例名称，用于指定特定的实例。默认为None。
        :return: 一个包含查询到的节点的列表，这些节点已经根据给定的坐标和实例名称进行了处理和筛选。
        :param set_name: 集合名称，用于指定特定的集合。默认为None。
        :param instance_name: 实例名称，用于指定特定的实例。默认为None。
        :return: 返回通过`creat_element_set_from_element_labels`方法创建的节点集。
        :rtype: PackagedNodeSet
        """
        # 根据坐标获取单元
        packaged_nodes = self.get_node_by_coordinate(coordinates, instance_name, set_name)
        # 初始化一个字典来存储节点标签
        node_labels = {}
        # 遍历获取到的单元，提取实例名称和标签
        for packaged_node in packaged_nodes:
            instance_name, label = packaged_node.instance_name, packaged_node.label
            # 如果实例名称不在字典中，则初始化一个空列表
            if instance_name not in node_labels:
                node_labels[instance_name] = []
            # 将标签添加到对应实例名称的列表中
            node_labels[instance_name].append(label)
        # 根据节点标签创建节点集并返回
        return self.create_node_set_from_node_labels(created_set_name, node_labels)

    def create_element_set_from_coordinates(self, created_set_name, coordinates, instance_name=None,
                                            set_name=None):
        """
        根据实例名称和集合名称和坐标获取结点。
        实例名称与集合名称至少设定一项。
            只指定了实例名称就从实例中的所有结点找目标值。
            只设定了集合名称就先从在装配中创建的集合中找指定集合，再从每个实例中找指定集合，最后从指定集合的所有节点中找目标值。
            两者都设定了就只在指定实例中找指定集合，再找目标结点。
            未找到目标值均会抛出异常。
            
        :param created_set_name: 要创建的单元集的名称。
        :type created_set_name: str
        :param coordinates: 用于查找单元的坐标。
        :type coordinates: list[tuple[float, float, float]]
        :param instance_name: 实例名称，用于指定特定的实例。默认为None。
        :type instance_name: str
        :param set_name: 集合名称，用于指定特定的集合。默认为None。
        :type set_name: str
        :return: 返回通过`creat_element_set_from_element_labels`方法创建的单元集。
        :rtype: PackagedElementSet
        """
        # 根据坐标获取单元
        packaged_elements = self.get_elements_by_coordinates(coordinates, instance_name, set_name)
        # 初始化一个字典来存储单元标签
        element_labels = {}
        # 遍历获取到的单元，提取实例名称和标签
        for packaged_element in packaged_elements:
            instance_name, label = packaged_element.instance_name, packaged_element.label
            # 如果实例名称不在字典中，则初始化一个空列表
            if instance_name not in element_labels:
                element_labels[instance_name] = []
            # 将标签添加到对应实例名称的列表中
            element_labels[instance_name].append(label)
        # 根据单元标签创建单元集并返回
        return self.create_element_set_from_element_labels(created_set_name, element_labels)

    def _init_labels(self, labels, name):
        """
        初始化标签。

        此函数对给定的标签字典进行验证和转换，确保每个标签键是字符串类型，并且每个标签值是整数类型的序列。
        此外，它还会检查标签字典中的每个实例名称是否在实例字典中，如果不在则抛出异常。
        最后，它会返回一个包含唯一标签键值对的元组。
        :param labels: 节点标签字典，包含要创建节点集的实例名称与节点标签。
        :type labels: dict[str,list[int]]
        :param name: 节点集的名称，用于标识该节点集。
        :type name: str
        :return: 一个元组，包含排序后的标签键值对。
        :rtype: tuple[tuple[str,list[int]]]
        """
        # 检查实例名称是否在实例字典中，若不在则抛出异常
        for k in labels.keys():
            check_type(k, str)
            if k not in self.instance_names:
                raise ValueError("instance named '{}' not found.".format(name))
        # 遍历节点标签字典，检查实例名称是否在实例字典中，若不在则抛出异常
        node_labels_ = []
        for key, item in labels.items():
            check_sequence_type(item, int)
            node_labels_.append((key, sorted(set(item))))
        return tuple(node_labels_)

    def create_node_set_from_node_labels(self, name, node_labels, auto_name=True):
        """
        此方法从节点标签序列创建节点集，并将其存储在内部字典中。

        得到的节点集中的节点有序（各实例中的节点编号递增）且唯一。

        :param name: 节点集的名称，用于标识该节点集。
        :type name: str
        :param node_labels: 节点标签字典，包含要创建节点集的实例名称与节点标签。
        :type node_labels: dict[str,list[int]]
        :param auto_name: 如果为True，则重名时自动生成节点集名称，否则会抛出重名异常。默认为True。
        :type auto_name: bool
        :return: 返回创建的节点集对象。
        :rtype: PackagedOdbSet
        :raises ValueError: 如果节点集名称已经存在，则抛出此异常。
        """
        if auto_name:
            name = self.auto_create_set_name(name, self.nodes_sets_names)
        else:
            # 检查节点集名称是否已存在，若存在则抛出异常
            if name in self.nodes_sets_names:
                raise ValueError("Node set named '{}' already exists.".format(name))
        node_labels_ = self._init_labels(node_labels, name)
        # 从节点标签序列创建节点集对象
        odb_set = self.odb_source.NodeSetFromNodeLabels(name, node_labels_)
        # 将节点集对象封装为内部使用的格式
        packaged_set = self._packaged_odb_object_factory.packaged_odb_set_class(odb_set, name, True)

        packaged_set.parent_node = self
        # 将封装后的节点集存储在内部字典中，并更新节点集名称列表
        self._packaged_node_sets_dict[name] = packaged_set
        self.nodes_sets_names.append(name)
        # 返回创建的节点集对象
        return self._packaged_node_sets_dict[name]

    def create_element_set_from_element_labels(self, name, element_labels, auto_name=True):
        """
        此方法从单元标签字典创建单元集，并将其存储在内部字典中。

        得到的单元集中的单元有序（各实例中的单元编号递增）且唯一。

        :param auto_name:
        :param name: 单元集的名称，用于标识该单元集。
        :type name: str
        :param element_labels: 单元标签字典，包含要创建单元集的实例名称与单元标签。
                {“instance-1”:[1,2,3,4], "instance-2":[5,6,7,8]}
        :type element_labels: dict[str, list[int]]
        :return: 返回创建的单元集对象。
        :rtype: PackagedOdbSet
        :raises ValueError: 如果单元集名称已经存在，则抛出此异常。
        """
        if auto_name:
            name = self.auto_create_set_name(name, self.element_sets_names)
        else:
            # 检查单元集名称是否已存在，若存在则抛出异常
            if name in self.element_sets_names:
                raise ValueError("Element set named '{}' already exists.".format(name))

        element_labels_ = self._init_labels(element_labels, name)

        # 从单元标签序列创建单元集对象
        odb_set = self.odb_source.ElementSetFromElementLabels(name, tuple(element_labels_))

        # 将单元集对象封装为内部使用的格式
        packaged_set = self._packaged_odb_object_factory.packaged_odb_set_class(odb_set, name, False)

        packaged_set.parent_node = self

        # 将封装后的单元集存储在内部字典中，并更新单元集名称列表
        self._packaged_element_sets_dict[name] = packaged_set
        self.element_sets_names.append(name)

        # 返回创建的单元集对象
        return self._packaged_element_sets_dict[name]


class PackagedOdbSet(_OdbNodesElementsOptions):

    def get_packaged_item_by_parent(self):
        parent = self.get_parent()
        if self.if_node:
            return parent.get_packaged_node_set_by_name(self.name).odb_source
        return parent.get_packaged_element_set_by_name(self.name).odb_source

    def __init__(self, odb_source, name, if_node, *args, **kwargs):
        super(PackagedOdbSet, self).__init__(*args, **kwargs)
        check_type(if_node, bool)
        self._odb_source = odb_source
        self.name = name
        self.if_node = if_node
        self._odb_faces = None
        self._instance_names = None
        self._packaged_root_assembly = None
        self._logger.info("Open odb set:'{}', with '{}' nodes and '{}' elements.".format(
            self.name, _customize_len(self.odb_nodes), _customize_len(self.odb_elements)))
        self._field_instance_label_index_dict = OrderedDict()

    @property
    def length(self):
        """
        根据节点类型返回长度。

        如果当前节点为if_node类型，则返回nodes_length，否则返回elements_length。
        这个属性主要用于提供一个根据节点类型来决定返回哪种长度的便捷方法。

        :return: 如果是if_node类型，则返回self.nodes_length；否则返回self.elements_length。
        :rtype: int
        """
        # 根据节点类型决定返回哪种长度
        if self.if_node:
            return self.nodes_length
        return self.elements_length

    @property
    def field_instance_label_index_dict(self):
        """
        当前集合对应的场输出数据值的场输出类型-实例名称-编号-序号字典。
        由PackagedFieldOutputValues对象在使用本对象选取指定数据时初始化并使用。

        :return: 有序字典{field_output_type:{instance_name: {label: [index1, index2, ...]}}}
        :rtype: dict[str, dict[str, dict[str, list[int]]]]
        """
        return self._field_instance_label_index_dict

    @property
    def instance_names(self):
        """
        获取集合中的odb实例名称列表。
        :return: 实例名称列表
        :rtype: list[str]
        """
        if self._instance_names is None:
            self._instance_names = list(self.odb_source.instanceNames)
        return self._instance_names

    @property
    def packaged_root_assembly(self):
        """
        获取包含当前集合的根装配PackagedRootAssembly对象。
        :return: 包含当前集合的根装配对象
        :rtype: PackagedRootAssembly
        """
        if self._packaged_root_assembly is None:
            self._packaged_root_assembly = \
                self.get_specified_type_parent(self._packaged_odb_object_factory.packaged_root_assembly_class)
        return self._packaged_root_assembly

    @property
    def odb_faces(self):
        """
        获取OdbSet中的面信息

        :return: 面信息列表
        :rtype:  SymbolicConstant
        """
        # 检查面信息是否已经加载，如果未加载，则从OdbSet中获取并加载
        if self._odb_faces is None:
            self._odb_faces = self.odb_source.faces
        return self._odb_faces

    @property
    def odb_nodes(self):
        """
        获取ODB节点信息的属性。

        :return: ODB中的所有节点信息。
        :rtype: list[OdbMeshNode]
        """
        # 检查是否已经加载了ODB节点信息
        if self._odb_nodes is None:
            # 如果尚未加载，则从ODB集中加载节点信息
            self._odb_nodes = self.odb_source.nodes
        # 返回ODB节点信息
        return self._odb_nodes

    def get_odb_node_by_index(self, index):
        check_type(index, int)
        # 遍历可迭代对象中的每一个单元
        list_2d = False
        try:
            iter(self.odb_nodes[0])
            list_2d = True
        except TypeError:
            # 如果当前单元不可迭代，则直接返回该单元
            pass
        if list_2d:
            return get_element_from_2d_list(self.odb_nodes, index)
        else:
            return self.odb_nodes[index]

    def get_odb_element_by_index(self, index):
        check_type(index, int)
        # 遍历可迭代对象中的每一个单元
        list_2d = False
        try:
            iter(self.odb_nodes[0])
            list_2d = True
        except TypeError:
            # 如果当前单元不可迭代，则直接返回该单元
            pass
        if list_2d:
            return get_element_from_2d_list(self.odb_elements, index)
        else:
            return self.odb_elements[index]

    @property
    def odb_elements(self):
        # 检查是否已经缓存了ODB的单元信息
        if self._odb_elements is None:
            # 如果尚未缓存，则从ODB集中获取单元信息并进行缓存
            self._odb_elements = self.odb_source.elements
        # 返回ODB的单元信息
        return self._odb_elements


class PackagedInstance(_OdbNodesElementsOptions, _GainOdbSet):
    """
    包装实例类，继承自PackageBase。

    该类用于封装某个实例，提供对该实例节点的访问和操作。
    """

    def get_packaged_item_by_parent(self):
        packaged_root_assembly = self.get_parent()
        return packaged_root_assembly.get_instance_by_name(self.name).odb_source

    def __init__(self, odb_source, *args, **kwargs):
        """
        初始化PackagedInstance对象。

        :param odb_instance: 需要被封装的实例。
        """
        super(PackagedInstance, self).__init__(*args, **kwargs)
        if odb_source is None:
            raise ValueError("instance cannot be None.")
        self._odb_source = odb_source  # 存储被封装的实例对象
        self.name = self.odb_source.name

        self._logger.info(
            "Open odb instance: '{}', with '{}' nodes and '{}' elements.".format(
                self.name, _customize_len(self.odb_nodes), _customize_len(self.odb_elements)))

    @property
    def odb_node_set(self):
        """
        获取ABAQUS分析数据库中的节点集

        :return: 返回节点集的实例。如果尚未初始化，则先初始化节点集。
        """
        # 检查节点集是否已经初始化
        if self._odb_node_sets is None:
            # 如果尚未初始化，从ABAQUS数据库实例中获取节点集并进行初始化
            self._odb_node_sets = self.odb_source.nodeSets
        # 返回节点集实例
        return self._odb_node_sets

    @property
    def odb_element_set(self):
        """
        获取ABAQUS分析数据库中的单元集

        :return: 返回单元集的实例。如果尚未初始化，则先初始化单元集。
        """
        # 检查单元集是否已经初始化
        if self._odb_element_sets is None:
            # 如果尚未初始化，从ABAQUS数据库实例中获取单元集并进行初始化
            self._odb_element_sets = self.odb_source.elementSets
        # 返回单元集实例
        return self._odb_element_sets

    @property
    def odb_nodes(self):
        """
        获取节点信息。

        本方法用作属性访问器，确保外部访问节点信息时，
        可以通过实例的节点属性透明地获取所需信息。

        :return: OdbMeshNodeArray object
        """
        # 检查内部变量_nodes是否已初始化，如果没有，则从实例中获取节点信息并赋值给内部变量
        if self._odb_nodes is None:
            self._odb_nodes = self.odb_source.nodes
        return self._odb_nodes

    def get_odb_node_by_index(self, index):
        check_type(index, int)
        if index < 0 or index > len(self.odb_nodes):
            raise ValueError("index out of range")
        return self.odb_nodes[index]

    def get_odb_element_by_index(self, index):
        check_type(index, int)
        if index < 0 or index > len(self.odb_elements):
            raise ValueError("index out of range")
        return self.odb_elements[index]

    @property
    def odb_elements(self):
        # 检查是否已经获取过elements，如果没有，则从实例中获取
        if self._odb_elements is None:
            self._odb_elements = self.odb_source.elements
        # 返回elements列表
        return self._odb_elements

    def get_node_set_of_instance(self, name=None):
        """
        获取当前实例的节点集。

        该方法根据当前实例的节点生成一个节点集，并返回该节点集。如果未提供节点集名称，则使用默认名称。
        
        :param name: 节点集的名称。如果未提供，则使用默认名称 "Set_{self.name}"。
        :type name: str
        :return: 生成的节点集对象。
        :rtype: NodeSet
        """
        # 如果未提供节点集名称，则使用默认名称
        if name is None:
            name = "Set_{}".format(self.name)
        else:
            # 检查名称是否为字符串类型
            check_type(name, str)
        # 获取当前实例的所有节点的标签，并构建标签字典
        labels = {self.name: [node.label for node in self.get_packaged_nodes()]}
        # 使用父节点的创建方法生成节点集并返回
        return self.parent_node.create_node_set_from_node_labels(name, labels)

    def get_element_set_of_instance(self, name=None):
        """
        获取当前实例的单元集。

        该方法根据当前实例的单元生成一个单元集，并返回该单元集。如果未提供单元集名称，则使用默认名称。
        
        :param name: 单元集的名称。如果未提供，则使用默认名称 "ElementSet_{self.name}"。
        :return: 生成的单元集对象。
        """
        # 如果未提供单元集名称，则使用默认名称
        if name is None:
            name = "ElementSet_{}".format(self.name)
        else:
            # 检查名称是否为字符串类型
            check_type(name, str)
        # 获取当前实例的所有单元的标签，并构建标签字典
        labels = {self.name: [element.label for element in self.get_packaged_elements()]}
        # 使用父节点的创建方法生成单元集并返回
        return self.parent_node.create_element_set_from_element_labels(name, labels)


class PackagedNode(_PackageBase):
    """
    表示一个封装的节点，继承自PackageBase类。

    该类用于封装节点信息，包括节点的索引、节点本身、节点的坐标、节点的标签和节点的实例名称。
    """

    def get_packaged_item_by_parent(self):
        return self.parent_node.get_odb_node_by_index(self.index)

    def __init__(self, odb_source, index=None, *args, **kwargs):
        """
        初始化PackagedNode对象。

        :param odb_source: 被封装的节点对象。
        :param index: 节点的索引，可选参数，默认为None。
        """
        super(PackagedNode, self).__init__(*args, **kwargs)

        self._index = index
        self._odb_source = odb_source
        self._packaged_instance = None
        self._packaged_root_assembly = None
        self._coordinates = None
        self._instance_name = None
        self._label = None

    @property
    def index(self):
        """
        当前几何节点在获取当前节点的几何数据库（集合PackagedOdbSet或实例PackagedInstance）中的索引。
        :return: 返回当前对象的索引值_index。
        :rtype: int
        """
        return self._index

    @property
    def packaged_root_assembly(self):
        """
        获取当前对象的包装根组件。

        通过此属性，可以在对象的父节点中自动寻找并缓存包装根组件。
        如果未找到且未设置，则抛出 ValueError 异常。
        
        :return: 当前对象的包装根组件。
        :rtype: PackagedRootAssembly
        :raises ValueError: 如果未找到包装根组件且未手动设置。
        """
        # 如果已缓存包装根组件，则直接返回
        if self._packaged_root_assembly is None:
            self._packaged_root_assembly = \
                self.get_specified_type_parent(self._packaged_odb_object_factory.packaged_root_assembly_class)
        # 如果未找到且未缓存，则抛出异常
        if self._packaged_root_assembly is None:
            raise ValueError("packaged_root_assembly is not get.")
        # 返回缓存的包装根组件
        return self._packaged_root_assembly

    @property
    def packaged_instance(self):
        """
        获取封装实例对象。

        该属性主要用于获取当前对象的封装实例。如果封装实例尚未被创建，
        则尝试通过实例名称从封装的根组件中获取。如果仍然无法获取到封装实例，
        则抛出一个值错误异常。
        
        :return: 封装实例对象。
        :rtype: PackagedInstance
        :raises ValueError: 如果封装实例未设置。
        """
        # 检查封装实例是否已经存在
        if self._packaged_instance is None:
            # 如果不存在，尝试通过实例名称从封装的根组件中获取
            self._packaged_instance = self.packaged_root_assembly.get_instance_by_name(self.instance_name)
        # 再次检查封装实例是否存在
        if self._packaged_instance is None:
            # 如果仍然不存在，抛出异常
            raise ValueError("packaged_instance is not set.")
        # 返回封装实例
        return self._packaged_instance

    @property
    def coordinates(self):
        """
        获取节点的坐标。
        :return: 节点的坐标。
        :rtype: list
        """
        if self._coordinates is None:
            self._coordinates = np.array(self.odb_source.coordinates).tolist()
        return self._coordinates

    @property
    def coordinates_x(self):
        """
        获取节点的X坐标。
        :return: 节点的X坐标。
        :rtype: float
        """
        return self.coordinates[0]

    @property
    def coordinates_y(self):
        """
        获取节点的Y坐标。
        
        :return: 节点的Y坐标。
        :rtype: float 
        """
        return self.coordinates[1]

    @property
    def coordinates_z(self):
        """
        获取节点的Z坐标。
        
        :return: 节点的Z坐标。
        :rtype: float 
        """
        return self.coordinates[2]

    @property
    def instance_name(self):
        """
        获取节点的实例名称。
        :return: 节点的实例名称。
        :rtype: str
        """
        if self._instance_name is None:
            self._instance_name = self.odb_source.instanceName
        return self._instance_name

    @property
    def label(self):
        """
        获取节点的标签。

        如果标签尚未被获取，则从节点对象中获取并保存。
        :return: 节点的标签。
        :rtype: int
        """
        if self._label is None:
            self._label = self.odb_source.label
        return self._label


class PackagedElement(_PackageBase):
    def get_packaged_item_by_parent(self):
        return self.parent_node.get_odb_element_by_index(self.index)

    def __init__(self, odb_element, index, *args, **kwargs):
        """
        初始化方法

        :param odb_element: 单元对象，不能为空
        :param index: 单元的索引位置
        """
        super(PackagedElement, self).__init__(*args, **kwargs)
        # 检查element是否为None，因为element是关键属性，不能为空
        if odb_element is None:
            raise ValueError("element is None")

        # 初始化属性
        self.odb_element = odb_element  # 当前单元
        self._index = index  # 单元的索引位置
        self._packaged_instance = None
        self._packaged_root_assembly = None
        self._instance_name = None
        self._label = None
        self._type = None
        self._connectivity = None
        self._connecting_packaged_nodes = None
        self._mean_coordinate = None

    @property
    def index(self):
        """
        当前几何节点在获取当前节点的几何数据库（集合PackagedOdbSet或实例PackagedInstance）中的索引。
        
        :return: 返回当前对象的索引值_index。
        :rtype: int
        """
        return self._index

    def delete_odb_source(self):
        self.odb_element = None

    @property
    def packaged_root_assembly(self):
        """
        获取封装的根组件实例。

        该方法用于获取当前对象的封装的根组件实例。如果实例尚未被初始化（即self._packaged_root_assembly为None），
        则尝试通过get_specified_type_parent方法获取。如果无法获取到实例，将抛出ValueError异常。
        
        :return: 封装的根组件实例。
        :rtype: PackagedRootAssembly
        :raises ValueError: 如果无法获取到封装的根组件实例。
        """
        # 检查是否已经缓存了封装的根组件实例
        if self._packaged_root_assembly is None:
            # 尝试获取封装的根组件实例
            self._packaged_root_assembly = self.get_specified_type_parent(PackagedRootAssembly)
        # 再次检查是否成功获取到实例
        if self._packaged_root_assembly is None:
            # 如果没有获取到，抛出异常
            raise ValueError("packaged_root_assembly is not get.")
        # 返回封装的根组件实例
        return self._packaged_root_assembly

    @property
    def packaged_instance(self):
        """
        获取封装实例对象。
        :return: 封装实例对象。
        :rtype: PackagedInstance
        """
        if self._packaged_instance is None:
            self._packaged_instance = self.packaged_root_assembly.get_instance_by_name(self.instance_name)
        if self._packaged_instance is None:
            raise ValueError("packaged_instance is not set.")
        return self._packaged_instance

    def get_packaged_item(self):
        """
        获取被封装的实例对象。

        :return: 被封装的实例对象。
        """
        return self.odb_element

    @property
    def connectivity(self):
        """
        获取单元的连接性信息
        :return: tuple[int]
        """
        if self._connectivity is None:
            self._connectivity = tuple(self.odb_element.connectivity)
        # 返回连接性信息
        return self._connectivity

    @property
    def connecting_packaged_nodes(self):
        """
        获取连接的封装节点列表的属性。

        该属性负责构建和返回一个节点列表，这些节点是通过连接属性（_connectivity）指定的。
        它首先检查私有变量 _connecting_packaged_nodes 是否已被初始化，
        如果没有，则通过 _packaged_instance 的 get_node_by_label 方法查询每个连接对应的节点，
        并将结果存储在 _connecting_packaged_nodes 列表中。

        :return: 返回连接的封装节点列表。如果列表尚未创建，则先进行创建。
        :rtype: list[PackagedNode]
        """
        if self._connecting_packaged_nodes is None:
            # 如果连接的封装节点列表尚未初始化，则根据连接性属性构建节点列表
            self._connecting_packaged_nodes = [
                self.packaged_instance.get_node_by_instance_name_and_label(self.instance_name, connect)
                for connect in self.connectivity]
        return self._connecting_packaged_nodes

    @property
    def mean_coordinate(self):
        """
        计算所有连接节点坐标的平均值。

        :return: 平均坐标 (x, y, z) 的 numpy 数组
        :rtype: numpy.ndarray
        """
        if self._mean_coordinate is None:
            try:
                # 直接构建 numpy 数组
                coordinates = np.array([packaged_node.coordinates
                                        for packaged_node in self.connecting_packaged_nodes])
                # 计算各坐标值的平均三维坐标
                mean_coordinate = np.mean(coordinates, axis=0)
                self._mean_coordinate = mean_coordinate.tolist()
            except Exception as e:
                print("Error calculating mean coordinate: {}".format(e))
                raise
        return self._mean_coordinate

    @property
    def mean_coordinate_x(self):
        """
        获取平均坐标的 x 坐标。
        :return:平均坐标的 x 坐标。
        """
        return self.mean_coordinate[0]

    @property
    def mean_coordinate_y(self):
        """
        获取平均坐标的 y 坐标。
        :return: 平均坐标的 y 坐标。
        """
        return self.mean_coordinate[1]

    @property
    def mean_coordinate_z(self):
        """
        获取平均坐标的 z 坐标。
        :return: 平均坐标的 z 坐标。
        """
        return self.mean_coordinate[2]

    @property
    def instance_name(self):
        """
        获取实例名称。
        :return: 实例名称。
        :rtype: str
        """
        if self._instance_name is None:
            self._instance_name = self.odb_element.instanceName
        # 返回实例名称
        return self._instance_name

    @property
    def label(self):
        """
        获取单元的标签
        :return: 单元的标签
        """
        if self._label is None:
            self._label = self.odb_element.label
        return self._label

    @property
    def type(self):
        """
        获取单元的类型。
        Returns:
            self._type: 当前单元的类型。
        """
        if self._type is None:
            self._type = self.odb_element.type
        return self._type


class PackagedStep(_PackageBase):
    """
    管理abaqus step 操作的类。这个类允许用户通过名称或索引访问特定的步骤。
    """

    def get_packaged_item_by_parent(self):
        packaged_odb = self.get_parent()
        return packaged_odb.get_packaged_step_by_name(self.step_name).odb_source

    def __init__(self, odb_source, *args, **kwargs):
        """
        初始化PackagedStep对象。

        :param odb_source: 源OdbStep对象。
        :type odb_source: OdbStep
        """
        super(PackagedStep, self).__init__(*args, **kwargs)
        # 获取步骤对象
        self._odb_source = odb_source
        # 获取frames
        self._step_name = None
        self._progress_monitor.send_progress(self)
        self._field_output_type_constant = None
        self._logger.info("open odb step:'{}'".format(self.step_name))
        if self._name is None:
            self._name = self.step_name

    @property
    def step_name(self):
        """
        获取步骤名称。

        :return: 步骤名称。
        :rtype: str
        """
        if self._step_name is None:
            self._step_name = self.odb_source.name
        return self._step_name

    @property
    def packaged_frames(self):
        """
        获取封装的帧对象。
        :return: 包装的帧对象。
        :rtype: PackagedFrames
        """
        packaged_frames = self._packaged_odb_object_factory.packaged_frames_class(self.odb_source.frames)
        packaged_frames.parent_node = self
        return packaged_frames

    @property
    def field_output_type_constant(self):
        """
        获取场输出输出类型常量对象。管理当前分析步支持的场输出输出类型。

        该属性方法用于获取或初始化场输出输出类型常量对象。如果 `_field_output_type_constant` 为 None，
        则通过 `_get_field_output_types` 方法获取场输出输出类型，并初始化 `FieldOutputTypeConstant` 对象。
        否则，直接返回已缓存的 `_field_output_type_constant` 对象。

        :return: 包含有效节点类型和单元类型的场输出输出类型常量对象。
        :rtype: FieldOutputTypeConstant
        """
        if self._field_output_type_constant is None:
            # 获取场输出输出类型，并初始化 FieldOutputTypeConstant 对象
            field_output_types = self._get_field_output_types()
            self._field_output_type_constant = FieldOutputTypeConstant(
                valid_node_types=field_output_types["node"], valid_element_types=field_output_types["element"])
        return self._field_output_type_constant

    def _get_field_output_types(self):
        """
        获取场输出输出类型，并将其分类为节点类型和单元类型。

        该函数通过获取第一帧数据中的场输出输出类型，并根据这些类型对应的场输出输出值中的节点标签，
        判断这些场输出输出类型是属于节点类型还是单元类型。最终返回分类后的字典。

        :return: 包含两个键 'node' 和 'element' 的字典，分别存储节点类型和单元类型的场输出输出。
        :rtype: dict
        """
        # 初始化场输出输出类型字典，包含节点和单元两个空列表
        field_output_types = {"node": [], "element": []}
        # 获取第一帧数据
        frame_0 = self.packaged_frames.get_frame_by_index(0)
        # 遍历第一帧数据中的所有场输出输出类型
        for field_output_type in frame_0.field_output_types:
            # 获取当前场输出输出类型的场输出输出值
            field_output_values = frame_0.get_field_output_values(field_output_type)
            # 获取第一个场输出输出值的节点标签
            node_label = field_output_values.get_field_value_by_index(0).node_label
            # 根据节点标签的存在与否，将场输出输出类型分类到节点或单元列表中
            if node_label is not None:
                field_output_types["node"].append(field_output_type)
            else:
                field_output_types["element"].append(field_output_type)
        # 返回分类后的场输出输出类型字典
        return field_output_types


class PackagedFrames(_PackageBase):
    """
    管理Abaqus帧操作的类，封装了对多个帧的访问和操作。

    """

    def get_packaged_item_by_parent(self):
        packaged_step = self.get_parent()
        return packaged_step.packaged_frames.odb_source

    def __init__(self, odb_source, *args, **kwargs):
        """
        初始化PackagedFrames实例。

        :param odb_source: 包装的odb帧对象列表。
        :type odb_source: list[OdbFrame]
        """
        super(PackagedFrames, self).__init__(*args, **kwargs)
        self._odb_source = odb_source
        self._length = None
        self.if_print_process = False
        self.print_progress_interval = 50
        self._logger.info("open odb frames:{}".format(self.length))

    @property
    def length(self):
        """
        获取帧的数量。
        :return: 帧的数量。
        :rtype: int
        """
        if self._length is None:
            self._length = len(self.odb_source)
        return self._length

    @property
    def _packaged_step(self):
        """
        获取封装的步骤对象。
        :return: 封装的步骤对象。
        :rtype: PackagedStep
        """
        return self.get_specified_type_parent(PackagedStep)

    def set_process_print(self, if_print_process, print_progress_interval=100):
        """
        设置打印进度的相关参数

        本函数用于配置当前对象在执行过程中是否打印进度信息，以及设置打印进度信息的间隔时间。
        这对于长时间运行的任务来说非常有用，可以帮助用户了解任务的执行情况。

        :param if_print_process: 是否打印进度信息。
        :type if_print_process: bool
        :param print_progress_interval: 打印进度信息的间隔帧（遍历多少帧打印一次） 默认为100。
        :type print_progress_interval: int
        :return:  None
        """
        # 设置是否打印进度信息
        self.if_print_process = if_print_process
        # 设置打印进度信息的间隔时间
        self.print_progress_interval = print_progress_interval

    def get_frames_manager(self, start=None, end=None):
        """
        获取帧管理器，用于管理指定范围内的帧。
        :param start: 起始帧的索引，默认为None，表示从第一帧开始。
        :type start:int|None
        :param end: 结束帧的索引，默认为None，表示到最后一帧结束。
        :type end:int|None
        :return: PackagedFramesManager 实例，用于管理指定范围内的帧。
        :rtype: PackagedFramesManager
        """
        # 检查 start 和 end 参数的类型是否为 int 或 None
        check_type(start, int, None)
        check_type(end, int, None)

        # 如果 start 未指定，则默认从第一帧开始
        if start is None:
            start = 0
        # 如果 end 未指定，则默认到最后一帧结束
        if end is None:
            end = self.length

        # 确保 start 和 end 在合理范围内
        if start < 0 or start > self.length:
            raise ValueError("Start index out of range")
        if end < 0 or end > self.length:
            raise ValueError("End index out of range")
        if start > end:
            raise ValueError("Start index cannot be greater than end index")

        # 创建PackagedFramesManager实例用于管理打包的帧
        packaged_frames_manager = self._packaged_odb_object_factory.packaged_frame_manager_class(self._packaged_step)
        packaged_frames_manager.set_item_generator(
            packaged_frames_manager.generate_frame_by_range(self, start, end), end - start)
        return packaged_frames_manager

    def get_frames_manager_by_id_list(self, id_list):
        """
        根据ID列表获取帧管理器。

        对给定的帧ID列表进行验证，确保每个ID都在有效范围内，然后创建一个帧管理器实例，
        并将这些帧ID添加到帧管理器中。

        :param id_list: 帧的ID列表。
        :type id_list: list
        :return: 一个帧管理器实例，包含所提供的帧ID。
        :rtype: PackagedFramesManager
        :raises ValueError: 如果id_list中的任何ID不在有效范围内。
        """
        # 验证id_list是否为整数序列
        check_sequence_type(id_list, int)
        # 检查id_list中的值的范围
        for i, id in enumerate(id_list):
            if id < 0 or id >= self.length:
                raise ValueError("Frame ID:‘{}’ at index:'{}' in id_list out of range".format(id, i))
        # 创建一个新的帧管理器实例
        packaged_frames_manager = self._packaged_odb_object_factory.packaged_frame_manager_class(self._packaged_step)
        packaged_frames_manager.set_item_generator(packaged_frames_manager.generate_frame_by_frame_ids(
            self, id_list), len(id_list))
        # 返回新的帧管理器实例
        return packaged_frames_manager

    def get_every_frame(self):
        """
        生成器方法，用于逐个返回步骤中的每一帧。

        该方法通过遍历self.frames中的所有帧，使用yield语句逐个返回，
        使得调用者可以按需处理每一帧，而不需要一次性加载所有帧到内存中，
        从而节省了内存资源并提高了处理效率。

        :return: 生成器，每次迭代返回下一帧的PackagedFrame实例。
        :rtype: Generator[PackagedFrame]
        """
        if self.if_print_process:
            print("class'{}' Read all frames, total frame count: '{}'".format(PackagedFrames.__name__, self.length))
        for i in range(self.length):
            if self.if_print_process and i % self.print_progress_interval == 0:
                print("class'{}' Read frame: '{}'".format(PackagedFrames.__name__, i))
            yield self.get_frame_by_index(i)

    def get_frame_by_index(self, index):
        """
        根据索引返回特定帧。

        :param index: 帧的索引位置。
        :type index: int
        :return: 指定索引位置的帧的PackagedFrame实例。
        :rtype: PackagedFrame
        """
        packaged_frame = self._packaged_odb_object_factory.packaged_frame_class(self.odb_source[index], index)
        # 设置父节点
        packaged_frame.parent_node = self
        return packaged_frame

    def get_every_field_values(self, field_output_type):
        """
        生成器方法，用于逐个返回特定类型的场输出。

        :param field_output_type: 字符串，指定要获取的场输出类型。可输入”U“或”S“或”A“
        :type field_output_type: str
        :return: 生成器，每次迭代返回下一帧的指定类型场输出。
        :rtype: Generator[FieldOutputValues]
        """
        for frame in self.get_every_frame():
            yield frame.get_field_output_values(field_output_type)

    def get_filed_values_by_index(self, field_output_type, index):
        """
        根据索引获取特定场输出输出。

        本函数通过索引访问帧对象，并从该帧中提取特定类型的场输出输出。
        这对于需要按顺序处理多个场输出输出的场景非常有用。

        :param field_output_type: (str): 指定的场输出数据类型。可输入”U“或”S“或”A“
        :type field_output_type: str
        :param index: (int): 帧的索引，用于定位特定的帧。
        :type index: int
        :return: 特定场输出数据类型的对象，包含该类型的所有场输出输出。
        :rtype: FieldOutputValues
        """
        # 通过索引获取帧对象
        frame = self.get_frame_by_index(index)
        # 返回指定类型的场输出输出
        return frame.get_field_output_values(field_output_type)

    def __getitem__(self, index):
        """
        重写索引获取操作。

        当使用方括号语法从类实例中获取单元时，将调用此方法。

        :param index: 要获取的单元的索引位置。
        :type index: int
        :return: 指定索引位置的单元。
        :rtype: PackagedFrame
        """
        return self.get_frame_by_index(index)


class _PackagedFieldOutputManagerBase(AbqPostExtensionBase):
    """
    场输出项管理基类，用于管理一组打包的场输出项（如场输出值）。

    提供对场输出项的遍历、加载、索引访问和属性提取等功能。支持进度监控和资源管理。

    :param packaged_step: 关联的打包分析步对象
    :type packaged_step: PackagedStep
    :param item_generator: 场输出项的生成器（可选）
    :type item_generator: Iterable[PackagedFieldValueBase]
    :param argus: 额外位置参数
    :param kwargs: 额外关键字参数
    """

    def __init__(self, packaged_step, item_generator=None, *argus, **kwargs):
        """
        初始化场输出项管理器

        :param packaged_step: 关联的打包分析步对象
        :type packaged_step: PackagedStep
        :param item_generator: 场输出项的生成器（可选）
        :type item_generator: Iterable[PackagedFieldValueBase]
        """
        super(_PackagedFieldOutputManagerBase, self).__init__(*argus, **kwargs)
        check_type(packaged_step, PackagedStep)
        self._packaged_step = packaged_step
        self._if_send_progress = None
        self._packaged_items = []
        self._packaged_items_set = set()
        self._item_generator = None
        self._item_generator_length = None
        if item_generator:
            self._item_generator = item_generator
        self._if_load_packaged_items = False

    def get_item_generator(self):
        """
        获取item_generator属性的方法，item_generator为生成当前管理其对象管理的对象的迭代器。
        :return: item_generator
        :rtype: Generator
        """
        return self._item_generator

    def get_item_generator_length(self):
        """
        获取item_generator长度的属性方法
        :return: item_generator的长度
        :rtype: int
        """
        return self._item_generator_length

    def set_item_generator(self, item_generator, length):
        """
        设置item_generator属性的方法

        验证输入是否为可迭代对象，并检查其第一个单元的类型。
        会创建两个生成器副本分别用于验证和存储。

        :param length: 迭代器长度，用于生成遍历时打印进度
        :type length: int
        :param item_generator: 要设置为item生成器的可迭代对象
        :type item_generator: Iterable[PackagedFieldValueBase]
        :return: 生成器副本和迭代器长度
        :rtype: Generator, int
        :raises TypeError: 当输入不是可迭代对象时抛出
        :raises ValueError: 当输入可迭代对象为空时抛出
        """
        check_type(length, int)
        # 验证输入是否为可迭代对象
        try:
            iter(item_generator)
        except TypeError:
            raise TypeError(
                "The item_generator must be an iterable object. Rather than {}".format(type(item_generator)))
        # try:
        #     # 尝试从第一个副本获取第一个单元
        #     first_item = next(item_generator)
        # except StopIteration:
        #     raise ValueError("The item_generator cannot be empty")
        # item_generator = chain([first_item], item_generator)
        # 存储验证后的生成器副本
        self._item_generator = item_generator
        self._item_generator_length = length
        return item_generator, length

    @property
    def _field_output_type_constant(self):
        """
        从分析步对象中，获取场输出输出类型常量对象。管理当前分析步支持的场输出输出类型。

        :return: FieldOutputTypeConstant对象
        :rtype: FieldOutputTypeConstant
        """
        return self._packaged_step.field_output_type_constant

    def set_if_send_progress(self, value):
        """
        设置是否发送进度。为None时根据第一次执行的时间乘以管理项目的总数得到的总时间是否大于0.2秒确定是否发送进度信息。

        :param value: 是否发送进度。
        :type value:bool|None
        :return: None
        """
        check_type(value, bool, None)
        self._if_send_progress = value

    @property
    def packaged_items(self):
        return self._packaged_items

    @property
    def length(self):
        """
        获取项的长度。
        :return: 项的长度。
        :rtype: int
        """
        return len(self._packaged_items)

    def generate_every_managed_item(self, start=None, end=None):
        """
        生成每个被管理的项目。

        根据指定的起始索引和结束索引，生成器函数会产出在这个范围内的每个项目。
        如果未指定起始索引和结束索引，函数将从第一个项目开始产出，直到最后一个项目。

        :param start: 指定开始生成的索引位置。默认为None，表示从第一个项目开始，前包含。
        :type start: int|None
        :param end: 指定停止生成的索引位置。默认为None，表示直到最后一个项目，后不包含。
        :type end: int|None
        :return: 产出每个在指定索引范围内的项目。
        :rtype: Generator
        :raises ValueError: 当item_generator为空时抛出此异常。
        """
        # 初始化起始和结束索引，确保它们在有效范围内
        start, end = self._init_start_and_end(start, end, float('inf'))
        # 检查item_generator是否为空，如果为空，则抛出异常
        if not self._item_generator:
            raise ValueError("item_generator is empty")
        # 遍历item_generator中的每个项目
        for index, item in enumerate(self._item_generator):
            # 如果当前索引达到或超过结束索引，则停止生成
            if index >= end:
                break
            # 如果当前索引在起始索引之后或等于起始索引，则产出该项目
            if index >= start:
                yield item

    @staticmethod
    def _check_range_by_length(start, end, length=None):
        """
        检查指定的起始和结束索引是否在给定长度范围内。

        :param start: 起始索引。
        :param end: 结束索引。
        :param length: 序列的长度。默认为 None，表示结束索引不受限制。
        :return: 检查结果。
        :raises ValueError: 当起始或结束索引超出范围时抛出此异常。
        """
        # 如果未指定长度，则将其设置为无穷大
        if length is None:
            length = float('inf')
        elif length == float('inf'):
            pass
        else:
            check_type(length, int)
        # 检查起始索引是否在有效范围内
        if start < 0 or start > length:
            raise ValueError("Start index out of range")
        # 检查结束索引是否在有效范围内
        if end < 0 or end > length:
            raise ValueError("End index out of range")
        # 确保起始索引不大于结束索引
        if start > end:
            raise ValueError("Start index cannot be greater than end index")

    def _check_range(self, start, end, length=None):
        """
        检查给定的start和end索引是否在有效范围内

        :param start: 起始索引
        :type start: int
        :param end: 结束索引
        :type end: int
        :param length: 可选参数，数据总长度。若为None则使用self.length
        :type length: int/float
        :return:  None
        :raises ValueError: 当start或end超出有效范围[0, length]或start大于end时，抛出此异常。
        """
        if length is None:
            length = self.length
        self._check_range_by_length(start, end, length)

    def _init_start_and_end(self, start=None, end=None, length=None):
        """
        初始化起始和结束索引。

        该方法主要用于初始化或重置查询范围的起始和结束索引。它会根据传入的参数检查类型，
        并设置默认值，然后检查范围是否有效。

        :param start: 查询范围的起始索引。如果未提供，则默认为0。
        :type start: int|None
        :param end: 查询范围的结束索引。如果未提供，则默认为当前长度。
        :type end: int|None
        :param length: 数据总长度。若为None则使用self.length。如果为无穷大（float('inf')或math.inf），则不检查长度限制。
        :type length: int/float|None
        :return: 返回一个包含起始和结束索引的元组。
        :rtype: tuple
        """
        # 验证参数类型
        check_type(start, int, None)
        check_type(end, int, None)
        if length is None:
            length = self.length
        elif length == float('inf'):
            pass
        else:
            check_type(length, int)
        # 设置默认的起始和结束索引
        if start is None:
            start = 0
        if end is None:
            end = length
        # 检查并设置起始和结束索引的范围
        self._check_range(start, end, length)
        return start, end

    def get_every_managed_item(
            self, start=None, end=None, if_delete_odb_source=True, if_add_packaged_items=False, attribute_names=None):
        """
        获取所有托管项的生成器。

        如果使用load_packaged_items将所有管理项加载到内存中，已打包项的数量等于预定义的长度，则直接返回这些已打包项的生成器。
        否则，调用 `generate_every_managed_item` 方法生成托管项的生成器。
        并根据_if_send_progress的设定或由第一次遍历时间计算的到的总执行时间大于0.02秒时向从所管理的对象中获取的进度管理器中发送进度信息。

        设置打包项manager_index属性值为其在本对象中的索引后生成。

        :param start: 托管项的起始索引，默认为None，表示从第一个托管项开始
        :type start: int|None
        :param end: 托管项的结束索引，默认为None，表示到所有托管项结束
        :type end: int|None
        :return: 托管项的生成器
        :param if_delete_odb_source: 是否生成管理的对象后，下一次迭代前释放上一次生成的对象持有的odb资源，默认为True
        :type if_delete_odb_source: bool
        :param if_add_packaged_items: (bool, 可选): 是否在生成每个包装帧之后添加额外的包装项。
        :type if_add_packaged_items: bool
        :param attribute_names: 属性名称列表，指定需要从包装项目中缓存的属性。
        :type attribute_names: list[str]
        :param reference_length: 参考长度，用于计算是否需要发送进度信息。
        :type reference_length: int
        """
        # 如果已打包项的数量等于预定义的长度
        if self._packaged_items:
            start, end = self._init_start_and_end(start, end)
            traverse_item = self._packaged_items[start:end]
        else:
            # 否则，调用方法生成托管项
            start, end = self._init_start_and_end(start, end, self._item_generator_length)
            traverse_item = self.generate_every_managed_item(start, end)
        if_send_progress = False
        time_0 = time.time()
        for index, item in enumerate(traverse_item):
            item.manager_index = index
            # 生成器，返回当前项
            yield item
            # 检查是否需要发送进度信息
            if index == 0 and (not if_send_progress):
                # 如果需要发送进度信息，或者当前项的处理时间超过阈值，则设置标志为True
                if self._if_send_progress is None:
                    if_send_progress = (time.time() - time_0) * (end - start) > 0.2
                else:
                    if_send_progress = self._if_send_progress
            # 如果需要发送进度信息，则发送当前项的进度信息
            if if_send_progress:
                self._progress_monitor.send_progress(
                    self, managed_item=item, start=start, end=end, traverse_index=index)
            # 如果需要添加包装项，对当前包装帧执行该操作
            if if_add_packaged_items:
                self.add_packaged_items(item, attribute_names, if_delete_odb_source)

    def get_packaged_item_by_index(self, index):
        """
        根据索引获取打包后的项。

        在尝试访问打包项列表时，此方法首先检查已打包项的数量是否符合预期长度。
        如果是，它直接返回请求的项；如果不是，则调用另一个方法根据索引生成托管项。

        设置打包项manager_index属性值为其在本对象中的索引后返回。

        :param index: 要获取的打包项的索引。
        :return: 根据索引获取的打包项实例。
        """
        # 检查已打包项的数量是否等于预定义的长度
        if index > self.length or index < 0:
            raise IndexError("Index out of range")
        return self._packaged_items[index]

    def add_packaged_items(self, packaged_item, attribute_names=None, if_delete_odb_source=True):
        """
        添加包装后的项目到集合中，并根据需求处理属性和源数据。

        使用一个集合保存添加情况，如果packaged_item已被添加过，则什么都不做。

        :param packaged_item:  包装的项目，准备添加到集合中。
        :param attribute_names: 属性名称列表，指定需要从包装项目中缓存的属性。
        :type attribute_names: list[str]
        :param if_delete_odb_source: 布尔值，指示是否在添加项目后释放其ODB资源。默认为True。
        :type if_delete_odb_source: bool
        :return:
        """
        if packaged_item not in self._packaged_items_set:
            # 使用packaged_field_value懒加载功能，访问并缓存需要的属性备用
            if attribute_names is not None:
                check_sequence_type(attribute_names, str)
            for name in attribute_names:
                _ = getattr(packaged_item, name)

            # 根据参数决定是否删除ODB源数据
            if if_delete_odb_source:
                packaged_item.delete_odb_source()
            self._packaged_items_set.add(packaged_item)
            # 将包装后的项目添加到集合中
            self._packaged_items.append(packaged_item)

    def load_generated_packaged_items(
            self, start=None, end=None, attribute_names=None, if_delete_odb_source=True, force_load=False):
        """
        加载生成的打包项目。如已调用过此方法加载过，则不再加载，可强制加载。

        该方法用于加载在指定范围内生成的打包项目，并根据需要删除ODB源文件。

        :param start: 开始（可选）。
        :param end: 结束（可选）。
        :param attribute_names: 需要加载的属性名称列表（可选）。
        :param if_delete_odb_source: 是否删除ODB源文件，默认为True。
        :param force_load: 强制加载，默认为False。
        :return: None
        """
        if force_load or not self._if_load_packaged_items:
            check_type(if_delete_odb_source, bool)
            if attribute_names is not None:
                check_sequence_type(attribute_names, str)
            # 遍历当前已有的场输出值到预期长度的范围，逐个加载新的场输出值
            for item in self.generate_every_managed_item(start, end):
                self.add_packaged_items(item, attribute_names, if_delete_odb_source)
            self._if_load_packaged_items = True

    def delete_packaged_items(self):
        """
        删除加载到管理的项目列表中的所有项。
        """
        # 检查是否有包装后的项目存在
        if self._packaged_items:
            # 调用方法删除数据库中的包装项目源码
            self.delete_packaged_items_odb_source()
            # 清空包装后的项目列表
            self._packaged_items.clear()
            self._packaged_items_set.clear()

    def delete_packaged_items_odb_source(self):
        """
        删除所有打包项目的ODB源。

        此方法遍历内部维护的打包项目列表，并调用每个项目的delete_odb_source方法来删除它们的ODB源。
        如果没有打包项目，则此方法不执行任何操作。

        :return: 无返回值。
        """
        if self._packaged_items:
            for packaged_item in self._packaged_items:
                packaged_item.delete_odb_source()

    def get_specified_attribute_list(self, attribute_name, if_delete_odb_source=True):
        """
        根据指定的属性名称，获取所有管理项中的该属性值列表。

        遍历每一个管理项，提取其指定的属性值，并将这些值收集到一个列表中。
        同时，为了优化内存，每次提取属性值后，都会删除管理项的ODB源。

        :param attribute_name: 指定的属性名称，用于提取每个管理项的相应属性值。
        :type attribute_name: str
        :param if_delete_odb_source: 是否在获取属性值后删除管理项的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :return: 包含所有管理项中指定属性值的列表。
        :rtype: list
        """
        # 初始化一个空列表，用于存储所有管理项的指定属性值
        datas = []
        # 遍历每一个管理项
        for field_value in self.get_every_managed_item():
            # 提取并记录管理项的指定属性值
            datas.append(get_nested_attribute(field_value, attribute_name))
            # 删除管理项的ODB源
            if if_delete_odb_source:
                field_value.delete_odb_source()
        # 返回包含所有指定属性值的列表
        return datas

    def generate_every_specified_attribute_dict(
            self, attribute_names, if_delete_odb_source=True):
        """
        生成一个包含指定属性的字典序列。

        本函数根据提供的属性名称列表，为每个被管理的项生成一个字典，字典中包含这些属性及其对应的值。
        可以通过参数选择是否获取相对数据以及是否删除ODB源。

        :param attribute_names: (list[str]): 包含所需属性名称的列表。
        :type attribute_names: list[str]
        :param if_delete_odb_source: (bool): 是否在生成字典后删除管理项的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :return: 返回一个生成器，每个单元都是一个OrderedDict，包含每个被管理项目中指定的属性。
        :rtype: Generator[OrderedDict[str, Any]]
        """
        # 检查attribute_names是否为字符串序列
        check_sequence_type(attribute_names, str)
        # 遍历每个被管理的项
        for item in self.get_every_managed_item():
            result_dict = OrderedDict((name, get_nested_attribute(item, name)) for name in attribute_names)
            # 如果if_delete_odb_source为True，则删除item的ODB源
            if if_delete_odb_source:
                item.delete_odb_source()
            # 生成并返回result_dict
            yield result_dict

    def get_specified_attributes_list_dict(self, attribute_names, if_delete_odb_source=True):
        """
        根据指定的属性名列表，从管理的所有项中提取这些属性的值，并以字典形式返回。

        :param attribute_names: 包含需提取属性名的列表。
        :type attribute_names: list[str]
        :param if_delete_odb_source: 是否在获取属性值后删除管理项的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :return: 包含每个属性名及其对应值列表的有序字典。
        :rtype: OrderedDict[str, list]
        """
        # 检查attribute_names是否为字符串序列，确保输入类型正确
        check_sequence_type(attribute_names, str)
        # 初始化有序字典，用于存储属性名对应的值列表
        field_values_dict = OrderedDict()
        # 初始化字典键，确保所有指定的属性名都被初始化为空列表
        for name in attribute_names:
            field_values_dict[name] = []
        for field_value in self.get_every_managed_item(if_delete_odb_source):
            for name in attribute_names:
                field_values_dict[name].append(get_nested_attribute(field_value, name))
        # 返回填充了属性值的字典
        return field_values_dict


class PackagedFramesManager(_PackagedFieldOutputManagerBase):
    """
    该类用于管理复数的帧对象。主要功能包括添加打包的帧对象、
    根据节点索引获取特定场输出的值集合等。
    """
    frame_data_attribute_names = ["step_time", "frame_id"]

    @staticmethod
    def generate_frame_by_range(packaged_frames, start=None, end=None, step=None):
        """
        根据指定的范围生成帧。

        :param packaged_frames: 包装后的帧集合，类型为PackagedFrames。
        :type  packaged_frames: PackagedFrames
        :param start: 起始索引，默认为None，如果为None则从0开始。
        :param end: 结束索引，默认为None，如果为None则到集合的末尾。
        :param step: 步长，默认为None，如果为None则默认步长为1。
        :return: 生成的帧序列。
        """
        # 检查start, end, step参数的类型是否正确
        check_type(start, int, None)
        check_type(end, int, None)
        length = packaged_frames.length
        # 设置默认的起始和结束索引
        if start is None:
            start = 0
        if end is None:
            end = length
        if step is None:
            step = 1
        else:
            check_type(step, int)
        # 检查指定的范围是否超出集合的长度
        PackagedFramesManager._check_range_by_length(start, end, length)
        # 在指定范围内生成帧ID
        for index in range(start, end, step):
            yield packaged_frames.get_frame_by_index(index)

    @staticmethod
    def generate_frame_by_frame_ids(packaged_frames, frame_ids):
        """
        根据帧ID生成帧序列。

        本函数通过检查给定的帧ID是否在指定的帧集合范围内，来过滤并生成对应的帧序列。
        使用生成器模式，每次只返回一个帧，适用于处理大量帧数据的场景。

        :param packaged_frames: 封装好的帧集合对象，包含了一系列帧。
        :type  packaged_frames: PackagedFrames
        :param frame_ids: 帧ID序列，指定了需要提取的帧的索引。
        :type  frame_ids: list[int] or tuple[int]
        :return: 生成指定帧ID对应的帧序列。
        :rtype: Generator
        """
        # 检查frame_ids是否为int类型的序列
        check_sequence_type(frame_ids, int)
        # 获取封装帧集合的长度
        length = packaged_frames.length
        # 遍历帧ID，检查每个ID是否在有效范围内
        for frame_id in frame_ids:
            if frame_id < 0 or frame_id >= length:
                raise ValueError("frame_id:{} is out of range".format(frame_id))
        # 生成并返回每个指定ID的帧
        for frame_id in frame_ids:
            yield packaged_frames.get_frame_by_index(frame_id)

    def __init__(self, packaged_step, *argus, **keyword):
        """
        初始化FramesManager对象，设置初始状态。
        """
        super(PackagedFramesManager, self).__init__(packaged_step, *argus, **keyword)

    # def set_item_generator(self, item_generator, length):
    #     item_generator, length=super(PackagedFramesManager, self).set_item_generator(item_generator, length)
    #     # 尝试从第一个副本获取第一个单元
    #     first_item = next(item_generator)
    #     check_type(first_item, PackagedFrame)
    #     item_generator=chain([first_item], item_generator)
    #     self._item_generator = item_generator

    def add_packaged_items(self, packaged_item, attribute_names=None, if_delete_odb_source=True):
        """
        添加封装帧对象到当前对象中，并根据需求处理属性和源数据。

        :param packaged_item: 封装帧对象，准备添加到当前对象中。
        :type packaged_item: PackagedFrame
        :param attribute_names: 属性名称列表，指定需要从封装帧对象中缓存的属性。默认为类属性frame_data_attribute_names的值。
        :type attribute_names: list[str]
        :param if_delete_odb_source: 布尔值，指示是否在添加项目后释放其ODB资源。默认为True。
        :type if_delete_odb_source: bool
        :return:

        此方法利用包装项目的懒加载机制，提前访问和缓存所需的属性，以优化后续的使用效率。
        """
        # 如果未提供attribute_names，则使用类的默认属性名称列表
        if attribute_names is None:
            attribute_names = self.frame_data_attribute_names
        else:
            # 如果提供了attribute_names，确保其为字符串序列
            check_sequence_type(attribute_names, str)

        # 调用父类方法以执行实际的加载操作
        super(PackagedFramesManager, self).add_packaged_items(packaged_item, attribute_names, if_delete_odb_source)

    def load_generated_packaged_items(
            self, start=None, end=None, attribute_names=None, if_delete_odb_source=True, force_load=False):
        # 如果未提供attribute_names，则使用类的默认属性名称列表
        if attribute_names is None:
            attribute_names = self.frame_data_attribute_names
        else:
            # 如果提供了attribute_names，确保其为字符串序列
            check_sequence_type(attribute_names, str)
        # 调用父类方法以执行实际的加载操作
        super(PackagedFramesManager, self).load_generated_packaged_items(
            start, end, attribute_names, if_delete_odb_source)

    @property
    def step_time_list(self):
        """
        获取每个打包帧的分析步时间列表。

        :return: list: 包含所有打包帧分析步时间的列表。
        :rtype: list[int]
        """
        return [packaged_frame.step_time for packaged_frame in self.get_every_managed_item()]

    def _get_packaged_mesh_by_field_output_type(self, field_output_type, packaged_nodes=None, packaged_elements=None):
        """
        根据场输出数据类型获取打包的网格数据。

        该方法用于根据指定的场输出数据类型，从打包的节点数据或单元数据中选择并返回相应的网格数据。

        :param field_output_type: 场输出数据类型，用于决定返回哪种类型的网格数据。
        :type field_output_type: str
        :param packaged_nodes: 打包的节点数据，可选参数。
        :type packaged_nodes: PackagedNodes
        :param packaged_elements: 打包的单元数据，可选参数。
        :type packaged_elements: PackagedElements
        :return:- 如果场输出数据类型匹配节点类型且提供了打包的节点数据，则返回打包的节点数据。
                - 如果场输出数据类型不匹配节点类型且提供了打包的单元数据，则返回打包的单元数据。
                - 如果未提供节点数据和单元数据，或场输出数据类型与提供的数据不匹配，则抛出异常。
        :rtype: PackagedNodes or PackagedElements
        :raises ValueError: 如果未提供节点数据和单元数据，或场输出数据类型与提供的数据不匹配。
        """
        # 检查是否提供了打包的节点数据
        if packaged_nodes:
            # 验证提供的场输出数据类型是否为节点类型
            if self._field_output_type_constant.determine_node_field_output_type(field_output_type):
                return packaged_nodes
        # 如果场输出数据类型不是节点类型，且提供了打包的单元数据，则返回单元数据
        if packaged_elements:
            if not self._field_output_type_constant.determine_node_field_output_type(field_output_type):
                return packaged_elements
        # 如果未提供节点数据和单元数据，则抛出异常
        raise ValueError(
            "Neither packaged_nodes nor packaged_elements are provided, or the field output type: '{}' "
            "does not match the provided list of packaged odb mesh objects".format(field_output_type))

    @staticmethod
    def _verify_packaged_nodes_and_packaged_elements(packaged_nodes=None, packaged_elements=None):
        """
        验证提供的打包节点和单元是否为正确的类型。

        :param packaged_nodes: 包装节点列表，默认为 None。
        :type packaged_nodes: list[PackagedNode]
        :param packaged_elements: 包装单元列表，默认为 None。
        :type packaged_elements: list[PackagedElement]
        :return:  None
        :raises TypeError: 如果 packaged_nodes 或 packaged_elements 中的单元类型不匹配。
        :raises ValueError: 如果 packaged_nodes 或 packaged_elements 未提供。
        """
        if not packaged_nodes and not packaged_elements:
            raise ValueError("Neither packaged_nodes nor packaged_elements are provided.")
        if packaged_nodes:
            check_sequence_type(packaged_nodes, PackagedNode)
        if packaged_elements:
            check_sequence_type(packaged_elements, PackagedElement)


class PackagedFrame(_PackageBase):
    """
    管理abaqus frame 操作的类
    """

    def get_packaged_item_by_parent(self):
        packaged_frames = self.get_parent()
        return packaged_frames.get_frame_by_index(self.index).odb_source

    def __init__(self, odb_source, index, *args, **kwargs):
        """
        初始化PackagedFrame对象。

        :param odb_source: 要封装的Frame对象。
        :type odb_source: OdbFrame
        :param index: 帧在父节点PackagedFrames对象中的索引位置
        :type index: int
        :param args:
        :param kwargs:
        """
        super(PackagedFrame, self).__init__(*args, **kwargs)
        self._odb_source = odb_source
        self.index = index
        # 缓存特定类型的场输出
        self._step_time = None
        self._frame_id = None
        self._manager_index = None
        self._field_output_types = None

    @property
    def field_output_types(self):
        """
        获取场输出数据类型

        该属性用于获取与odb源相关的场输出数据类型如果之前没有缓存这些类型，
        它会从odb源中提取并缓存起来这个过程确保了对场输出数据类型的高效访问

        :return: 一个包含场输出数据类型的列表
        :rtype: list[str]
        """
        # 检查是否已经缓存了场输出数据类型
        if self._field_output_types is None:
            # 如果没有缓存，则从odb源中提取场输出数据类型并缓存
            self._field_output_types = list(self.odb_source.fieldOutputs.keys())
        # 返回场输出数据类型
        return self._field_output_types

    @property
    def manager_index(self):
        """
        从PackagedFramesManager对象中获取此帧时，会设置此项，代表该帧在获取此帧PackagedFramesManager中的索引位置。
        由此索引，可以通过PackagedFramesManager对象再次获取此帧。

        :return: 帧在PackagedFramesManager中的索引位置
        :rtype: int
        """
        if self._manager_index is None:
            raise AttributeError("manager_index is not set")
        return self._manager_index

    @manager_index.setter
    def manager_index(self, value):
        """
        设置帧在PackagedFramesManager中的索引位置
        :param value: 帧在PackagedFramesManager中的索引位置
        :return: None
        """
        check_type(value, int)
        self._manager_index = value

    @property
    def step_time(self):
        """
        获取当前帧的分析步时间。
        :return: 分析步时间
        :rtype: float
        """
        if self._step_time is None:
            self._step_time = self.odb_source.frameValue
        return self._step_time

    @property
    def frame_id(self):
        """
        获取当前帧的帧号。
        :return: 帧号
        :rtype: int
        """
        if self._frame_id is None:
            self._frame_id = self.odb_source.frameId
        return self._frame_id

    def get_field_outputs(self, field_output_type):
        """
        返回特定类型的封装场输出对象

        :param field_output_type: 字符串，指定要获取的场输出类型。可输入”U“或”S“或”A“等
        :type field_output_type: str
        :param packaged_set: 包装的PackagedOdbSet对象，默认为None。
            选取获取的场输出对象的范围，None时全选（输出数据库中的所有场输出数据）。
        :type packaged_set: PackagedOdbSet|None
        :return: 指定场输出类型的PackagedFieldOutputs对象
        :rtype: PackagedFieldOutputs
        """
        check_type(field_output_type, str)
        try:
            packaged_field_values = \
                self._packaged_odb_object_factory.packaged_field_output_class(
                    self.odb_source.fieldOutputs[field_output_type], field_output_type)
        except KeyError:
            raise KeyError(
                "field_output_type '{}' is not valid."
                "The supported field output types for the current analysis step are:'{}'".format(
                    field_output_type, list(self.odb_source.fieldOutputs.keys())))
        # 设置packaged_field_values的父节点为当前实例
        packaged_field_values.parent_node = self
        return packaged_field_values

    def get_field_output_values(self, field_output_type):
        """
        返回特定类型的封装场输出数据对象

        :param field_output_type: 字符串，指定要获取的场输出类型。可输入”U“或”S“或”A“等
        :type field_output_type: str
        :return: 指定场输出类型的PackagedFieldOutputValues对象
        :rtype: PackagedFieldOutputValues
        """
        return self.get_field_outputs(field_output_type).get_field_output_values()


class PackagedFieldOutputs(_PackageBase):
    """
    包装后的场输出数据类，继承自_PackageBase。

    该类用于封装和管理场输出数据，提供对特定类型场输出数据的访问和操作功能。
    """

    def get_packaged_item_by_parent(self):
        """
        通过父节点获取包装后的场输出数据对象。
        :return: 通过父节点获取包装后的场输出数据对象。
        :rtype: PackagedFieldOutputs
        """
        packaged_frame = self.get_parent()
        return packaged_frame.get_field_outputs(self.field_output_type).odb_source

    def __init__(self, odb_source, field_output_type, if_sub=False, *args, **kwargs):
        """
        通过父节点获取包装后的场输出数据对象。
        :param odb_source: 原始场输出数据对象
        :param field_output_type: 场输出数据类型
        :type field_output_type: str
        :param if_sub: 是否为子场输出标志，默认为False
        :type if_sub: bool
        :param args: 可变位置参数
        :param kwargs: 可变关键字参数
        """
        super(PackagedFieldOutputs, self).__init__(*args, **kwargs)
        check_type(if_sub, bool)
        self._odb_source = odb_source
        self._field_output_type = field_output_type
        self._packaged_set = None
        self._if_sub = if_sub

    @property
    def field_output_type(self):
        """
        获取场输出数据类型
        :return: 场输出数据类型
        :rtype: str
        """
        return self._field_output_type

    def get_field_output_values(self):
        """
        获取场输出值对象。

        创建并返回一个包装后的场输出值对象。
        :return: 包装后的场输出值对象
        :rtype: PackagedFieldOutputValues
        """
        field_output_values = self._packaged_odb_object_factory.packaged_field_output_values_class(
            self.odb_source.values, self._field_output_type)
        field_output_values.parent_node = self
        return field_output_values


class PackagedFieldOutputValues(_PackageBase):
    """
    用于封装一组场输出值的类，继承自PackageBase。

    该类提供了对场输出值集合的访问和包装功能。
    """

    @property
    def node_instance_label_index_dict(self):
        """
        获取节点实例标签索引字典

        该属性方法用于构建和返回一个字典，字典中的键是实例名称，值是另一个字典，
        这个字典的键是节点标签，值是该节点在场输出值列表中的索引位置。

        :return: 包含节点实例标签索引的有序字典
        :rtype: OrderedDict[str, OrderedDict[int, int]]
        """
        # 获取PackagedOdb类型的父对象
        packaged_odb = self.get_specified_type_parent(PackagedOdb)
        # 尝试获取已存在的节点实例标签索引字典
        node_dict = packaged_odb.field_outputs_node_instance_label_index_dict
        # 如果字典不存在，则创建它
        if node_dict is None:
            if not self.if_node_type:
                raise ValueError(
                    "node_instance_label_index_dict can be only set when the field_output_type is 'node'")
            node_dict = OrderedDict()
            # 遍历场输出值，为每个节点创建实例名称到节点标签的索引映射
            for index, value in enumerate(self.get_every_field_value()):
                instance = value.instance
                # 根据实例是否为None，确定实例名称
                if instance is None:
                    instance_name = PackagedRootAssembly.rootAssembly_name
                else:
                    instance_name = instance.name
                # 在字典中为当前实例名称和节点标签设置索引
                node_dict.setdefault(instance_name, OrderedDict())[value.node_label] = index
            # 更新PackagedOdb对象的节点实例标签索引字典
            packaged_odb.field_outputs_node_instance_label_index_dict = node_dict
        # 返回构建好的节点实例标签索引字典
        return node_dict

    @property
    def element_instance_label_index_dict(self):
        """
        构建并返回一个字典，用于索引单元实例名称和单元标签到其对应场输出值索引的映射。

        该属性方法首先尝试从其父类PackagedOdb中获取一个已存在的场输出值字典。
        如果该字典不存在，则创建一个新的有序字典，并通过遍历所有场输出值来填充该字典。
        对于每个场输出值，方法确定其所属的实例名称和单元标签，并记录下该值在场输出值列表中的索引。
        这样做是为了优化后续对特定实例名称和单元标签的场输出值查询操作。
        :return: 包含单元实例标签索引的有序字典
        """
        # 获取PackagedOdb类型的父对象
        packaged_odb = self.get_specified_type_parent(PackagedOdb)
        # 尝试获取已存在的节点实例标签索引字典
        element_dict = packaged_odb.field_outputs_element_instance_label_index_dict
        # 如果字典不存在，则创建它
        if element_dict is None:
            if not self.if_element_type:
                raise ValueError(
                    "element_instance_label_index_dict can be only set when the field_output_type is 'element'")
            element_dict = OrderedDict()
            # 遍历场输出值，为每个节点创建实例名称到节点标签的索引映射
            for index, value in enumerate(self.get_every_field_value()):
                instance = value.instance
                # 根据实例是否为None，确定实例名称
                if instance is None:
                    instance_name = PackagedRootAssembly.rootAssembly_name
                else:
                    instance_name = instance.name
                label = value.element_label
                # 初始化或获取实例名称对应的字典
                instance_dict = element_dict.setdefault(instance_name, OrderedDict())
                # 初始化或获取标签对应的索引列表，并将当前索引添加到列表中
                label_list = instance_dict.setdefault(label, [])
                label_list.append(index)
            # 更新PackagedOdb对象的节点实例标签索引字典
            packaged_odb.field_outputs_element_instance_label_index_dict = element_dict
        # 返回构建好的节点实例标签索引字典
        return element_dict

    def get_packaged_item_by_parent(self):
        packaged_frame = self.get_specified_type_parent(PackagedFrame)
        return packaged_frame.get_field_output_values(self.field_output_type).odb_source

    def __init__(self, odb_source, field_output_type=None, *args, **kwargs):
        """
        初始化PackagedFieldOutputValues实例。
        :param odb_source: 被封装的odb对象
        :type odb_source: list[FieldValue]
        :param field_output_type: 场输出类型，指定要获取的场输出类型。可输入”U“或”S“或”A“
        :type field_output_type: str
        :param args:
        :param kwargs:
        """
        super(PackagedFieldOutputValues, self).__init__(*args, **kwargs)
        self._odb_source = odb_source
        self._length = None
        self.field_output_type = field_output_type
        self._instance_label_index_dict = None
        self._packaged_frame = None
        self._label_index_dict = None
        self._packaged_set = None
        # self._logger.info("Open field output values at type:'{}' with field values:'{}'".format
        #                   (self.field_output_type, self.length))
        self._field_output_type_constant_ = None
        self._if_node_type = None
        self._if_element_type = None

    @property
    def _field_output_type_constant(self):
        """
        获取当前对象对应的FieldOutputTypeConstant对象
        :return: FieldOutputTypeConstant对象
        :rtype: FieldOutputTypeConstant
        """
        if self._field_output_type_constant_ is None:
            self._field_output_type_constant_ = self.get_specified_type_parent(PackagedStep).field_output_type_constant
        return self._field_output_type_constant_

    @property
    def if_node_type(self):
        """
        当前对象的场输出数据是否是节点类型

        :return: 场输出数据类型，True 表示是节点类型，False 表示是单元类型
        :rtype: bool
        """
        if self._if_node_type is None:
            self._if_node_type = self._field_output_type_constant.determine_node_field_output_type(
                self.field_output_type)
        return self._if_node_type

    @property
    def if_element_type(self):
        """
        当前对象的场输出数据是否是单元类型

        :return: 场输出数据类型,  True 表示是单元类型，False 表示是节点类型
        :rtype: bool
        """
        if self._if_element_type is None:
            self._if_element_type = self._field_output_type_constant.determine_element_field_output_type(
                self.field_output_type)
        return self._if_element_type

    @property
    def packaged_frame(self):
        """
        获取父节点PackagedFrame对象
        :return: 父节点PackagedFrame对象
        :rtype: PackagedFrame
        """
        if self._packaged_frame is None:
            self._packaged_frame = self.get_specified_type_parent(PackagedFrame)
        return self._packaged_frame

    @property
    def length(self):
        """
        获取场输出数据库中所有单元或节点的数量
        :return: 场输出数据库中所有节点的数量
        :rtype: int
        """
        if self._length is None:
            self._length = len(self.odb_source)
        return self._length

    def odb_source_length(self):
        """
        用于获取odb_source的长度
        :return: odb_source的长度
        :rtype: int
        """
        return len(self.odb_source)

    def get_every_field_value(self, packaged_root_assembly=None):
        """
        生成每场输出数据节点的封装对象。

        通过遍历field_values中的每个单元，并将每个单元包装为PackagedFieldValue对象进行生成。
        :param packaged_root_assembly: 包装的根组件，如指定则将获取的场输出数据与其对应的几何节点对象绑定。
        :return: 每个场输出数据节点的封装对象
        :rtype: Generator[PackagedFieldValue]
        """
        if packaged_root_assembly:
            for instance_name, label_dict in self.node_instance_label_index_dict.items():
                for label, index in label_dict.items():
                    yield self.get_field_value_by_label(instance_name, label, packaged_root_assembly)
        else:
            for i in range(self.odb_source_length()):
                field_value = self.get_field_value_by_index(i)
                yield field_value

    def get_every_element_field_value(self, packaged_root_assembly=None):
        """
        获取 PackagedSet 中每个单元的场输出值。
        该方法会遍历 `PackagedSet` 中的所有单元，并逐个获取其场输出值。如果 `PackagedSet` 为空，则会抛出异常。
        
        :param packaged_root_assembly: 包装的根组件，如指定则将获取的场输出数据与其对应的几何节点对象绑定。
        :type packaged_root_assembly: PackagedRootAssembly
        :return: 一个生成器，每次迭代返回包含场输出值的对象，该对象与指定的单元和父节点关联。
        :rtype: Generator[PackagedElementFieldValue]
        :raises ValueError: 如果 `PackagedSet` 为空，则抛出此异常。
        """
        for instance_name, label_dict in self.element_instance_label_index_dict.items():
            for label in label_dict.keys():
                yield self.get_element_field_value_by_label(instance_name, label, packaged_root_assembly)

    def get_element_field_value_by_label(self, instance_name, label, packaged_root_assembly=None):
        """
        根据实例名称和标签获取单元场输出值。
        该方法首先验证`instance_name`和`label`的类型，确保它们分别是字符串和整数。
        然后，它尝试从一个内部字典中检索与给定实例名称和标签对应的索引列表。
        如果找到索引列表，它将使用这些索引从场输出值集合中提取相应的值，并将这些值封装到一个[PackagedElementFieldValue]对象中。
        如果提供了[packaged_root_assembly]参数，该方法还将尝试获取对应的包装单元，并将其附加到返回的[PackagedElementFieldValue]对象上。
        
        :param instance_name: 单元实例的名称。
        :type instance_name: str
        :param label: 单元的标签。
        :type label: int
        :param packaged_root_assembly: 包装的根组件实例。
        :type packaged_root_assembly: PackagedRootAssembly
        :return: 包装的单元场输出值对象。
        :rtype: PackagedElementFieldValue
        :raises KeyError: 如果[instance_name]未找到。
        """
        # 检查instance_name和label的类型，确保它们分别是字符串和整数
        check_type(instance_name, str)
        check_type(label, int)
        check_type(packaged_root_assembly, None, PackagedRootAssembly)
        if packaged_root_assembly:
            try:
                # 如果提供了packaged_root_assembly，尝试获取对应的包装节点
                packaged_element = packaged_root_assembly.get_element_by_instance_name_and_label(instance_name, label)
                # 将获取到的包装节点赋值给场输出值对象的packaged_node属性
                return self.get_element_field_value_by_packaged_element(packaged_element)
            except KeyError:
                # 如果找不到，抛出KeyError异常，说明instance_name或label未找到
                raise KeyError("instance_name or label not found in packaged_root_assembly")
        # 返回场输出值对象
        return self._get_element_field_value_by_label(instance_name, label)

    def _get_element_field_value_by_label(self, instance_name, label):
        """
        根据给定的实例名称和标签获取对应的元素场输出值
        
        :param instance_name: 元素实例名称
        :type instance_name: str
        :param label: 场输出标签名称
        :type label: str
        :return: 封装后的元素场输出值对象
        :rtype: PackagedElementFieldValue
        :raises KeyError: 如果instance_name或label未找到
        """
        try:
            # 尝试从字典中获取与instance_name和label对应的索引
            indexes = self.element_instance_label_index_dict[instance_name][label]
        except KeyError:
            # 如果找不到，抛出KeyError异常，说明instance_name或label未找到
            raise KeyError("instance_name or label not found in field_values")
        # 通过索引列表获取每个索引对应的场输出值，并封装为PackagedElementFieldValue对象
        packaged_element_field_value = \
            self._packaged_odb_object_factory.packaged_element_field_value_class([
                self.get_field_value_by_index(index) for index in indexes])
        packaged_element_field_value.parent_node = self
        return packaged_element_field_value

    def get_element_field_value_by_packaged_element(self, packaged_element):
        """
        根据封装的单元获取单元场输出值。

        该方法首先验证输入的packaged_element是否为PackagedElement类型，然后从该单元中提取实例名称和标签，
        并调用内部方法获取与这些信息对应的单元场输出值对象。最后，将原始的封装单元链接到这个场输出值对象上，并返回该对象。
        
        :param packaged_element: 一个封装的单元实例，包含必要的信息以检索特定的单元场输出值。
        :type packaged_element: PackagedElement
        :return: 一个单元场输出值对象，包含与提供的封装单元相关联的数据，并且该对象已链接回原始的封装单元。
        :rtype: PackagedElementFieldValue
        """
        # 验证输入类型以确保数据完整性
        check_type(packaged_element, PackagedElement)
        # 提取封装单元的实例名称和标签，这些信息用于检索特定的单元场输出值
        instance_name, label = packaged_element.instance_name, packaged_element.label
        # 调用内部方法以获取与指定实例名称和标签对应的单元场输出值
        packaged_element_field_value = self._get_element_field_value_by_label(instance_name, label)
        # 将检索到的场输出值对象链接回原始的封装单元，以便于后续可能的引用或操作
        packaged_element_field_value.packaged_element = packaged_element
        # 返回已链接的单元场输出值对象
        return packaged_element_field_value

    def get_field_value_by_index(self, index):
        """
        根据索引获取场输出值的包装对象。

        :param index: 场输出值的索引。
        :type index: int
        :return: 包含指定索引处场输出值的PackagedFieldValue对象。
        :rtype: PackagedFieldValue
        """
        packaged_field_value = \
            self._packaged_odb_object_factory.packaged_field_value_class(self.odb_source[index], index)
        # 设置父节点
        packaged_field_value.parent_node = self
        return packaged_field_value

    def get_field_value_by_label(self, instance_name, label, packaged_root_assembly=None):
        """
        根据实例名称和标签获取场输出值。
        
        :param instance_name: 节点实例的名称。
        :param label: 节点的标签。
        :param packaged_root_assembly: 包装的根组件实例。
            如设置，会使用该组件来获取几何节点添加到获取的场输出数据点上。
        :return: 场输出值对象，包含通过索引获取的场输出值和可选的包装节点信息。
        """
        """
        
        参数:
        - instance_name (str): 
        - label (int): 
        - packaged_root_assembly (PackagedRootAssembly, 可选): 
        返回:
        - field_value: 
        抛出:
        - KeyError: 如果instance_name或label未找到。
        """
        # 检查instance_name和label的类型，确保它们分别是字符串和整数
        check_type(instance_name, str)
        check_type(label, int)
        check_type(packaged_root_assembly, None, PackagedRootAssembly)
        if packaged_root_assembly:
            try:
                # 如果提供了packaged_root_assembly，尝试获取对应的包装节点
                packaged_node = packaged_root_assembly.get_node_by_instance_name_and_label(instance_name, label)
                return self.get_field_value_by_packaged_node(packaged_node)
            except KeyError:
                # 如果找不到，抛出KeyError异常，说明instance_name或label未找到
                raise KeyError("instance_name or label not found")
        # 返回场输出值对象
        return self._get_field_value_by_label(instance_name, label)

    def _get_field_value_by_label(self, instance_name, label):
        """
        根据实例名称和标签获取场输出值。

        该方法首先尝试从节点实例标签索引字典中获取与实例名称和标签对应的索引。
        如果找不到对应的索引，将抛出KeyError异常，提示实例名称或标签未找到。
        找到索引后，调用另一个方法根据索引获取并返回场输出值。

        参数:
        - instance_name (str): 节点实例的名称。
        - label (str): 节点实例的标签。

        返回:
        - field_value: 场输出值，具体类型取决于get_field_value_by_index方法的返回值。

        异常:
        - KeyError: 如果instance_name或label在索引字典中未找到。
        """
        try:
            # 尝试从字典中获取与instance_name和label对应的索引
            index = self.node_instance_label_index_dict[instance_name][label]
        except KeyError:
            # 如果找不到，抛出KeyError异常，说明instance_name或label未找到
            raise KeyError("instance_name or label not found")
        # 使用获取到的索引，调用另一个方法来返回场输出值
        return self.get_field_value_by_index(index)

    def get_field_value_by_packaged_node(self, packaged_node):
        """
        根据封装节点获取场输出值。

        该方法首先检查输入的packaged_node是否为PackagedNode类型，然后从packaged_node中提取instance_name和label，
        并调用私有方法_get_field_value_by_label来获取对应的场输出值。最后，将packaged_node信息附加到返回的场输出值上。
        参数:
        packaged_node (PackagedNode): 封装节点对象，包含instance_name和label信息。
        返回:
        field_value: 场输出值对象，包含与label对应的场输出值及封装节点信息。
        """
        # 检查packaged_node是否为PackagedNode类型，以确保类型安全。
        check_type(packaged_node, PackagedNode)
        # 从packaged_node中提取instance_name和label，用于后续获取场输出值。
        instance_name, label = packaged_node.instance_name, packaged_node.label
        # 调用私有方法_get_field_value_by_label，根据instance_name和label获取场输出值。
        field_value = self._get_field_value_by_label(instance_name, label)
        # 将packaged_node信息附加到返回的场输出值上，以便于后续可能的追溯或处理。
        field_value.packaged_node = packaged_node
        # 返回包含封装节点信息的场输出值。
        return field_value

    def get_packaged_field_values_manager_by_set(self, packaged_set, if_delete_odb_source=False):
        """
        获取打包场输出值管理器

        :param packaged_set:(Union[PackagedOdbSet, List[PackagedOdbSet]]):
                封装集合对象，可以是单个PackagedOdbSet或PackagedOdbSet列表，
                表示节点集或单元集
        :type packaged_set: PackagedOdbSet or List[PackagedOdbSet]
        :param if_delete_odb_source: 是否删除原始odb数据源，默认为False
        :type if_delete_odb_source: bool
        :return: 包含所有打包网格场输出输出值的场输出值管理器
        :rtype: FieldValuesManager
        :raises TypeError: 如果 `packaged_meshes` 不是列表或其中单元不是 `PackagedNode` 或 `PackagedElement` 类型
        """
        # 创建场输出值管理器实例
        check_type(packaged_set, PackagedOdbSet)
        packaged_step = self.get_specified_type_parent(PackagedStep)
        packaged_field_values_manager = None
        if isinstance(packaged_step, PackagedStep):
            manager_class = self._packaged_odb_object_factory.field_values_manager
            item_generator = manager_class.generate_item_by_set(self, packaged_set)
            item_generator_length = manager_class.get_generate_item_by_set_length(packaged_set)
            packaged_field_values_manager = self._packaged_odb_object_factory.field_values_manager(
                packaged_step, field_output_type=self.field_output_type)
            packaged_field_values_manager.set_item_generator(item_generator, item_generator_length)
        if if_delete_odb_source:
            self.delete_odb_source()
        return packaged_field_values_manager

    def get_packaged_field_values_manager_for_all(self, packaged_root_assembly=None, if_delete_odb_source=False):
        """
        获取打包后的场输出值管理器。

        功能说明:
        1. 获取当前对象的打包步骤实例。
        2. 根据节点类型或单元类型生成场输出值生成器。
        3. 使用工厂方法创建场输出值管理器实例。
        4. 根据参数决定是否删除ODB源文件。

        :param packaged_root_assembly: 可选参数，指定根装配体。如果未提供，则使用默认值None。
        :type packaged_root_assembly: PackagedRootAssembly or None
        :param if_delete_odb_source: 布尔值，指示是否删除ODB源文件。默认为False。
        :type if_delete_odb_source: bool
        :return: 打包后的场输出值管理器实例。如果未找到打包步骤或创建失败，则返回None。
        :rtype: FieldValuesManager or None
        """
        check_type(packaged_root_assembly, PackagedRootAssembly, None)
        # 获取当前对象的打包步骤实例
        packaged_step = self.get_specified_type_parent(PackagedStep)
        packaged_field_values_manager = None
        # 如果当前对象属于打包步骤类型，则创建场输出值管理器
        if isinstance(packaged_step, PackagedStep):
            # 根据节点类型选择不同的场输出值生成方式
            if self.if_node_type:
                item_generator = self.get_every_field_value(packaged_root_assembly)
            else:
                item_generator = self.get_every_element_field_value(packaged_root_assembly)
            # 使用工厂方法创建场输出值管理器实例
            packaged_field_values_manager = self._packaged_odb_object_factory.field_values_manager(
                packaged_step, item_generator=item_generator, field_output_type=self.field_output_type)
        # 根据参数决定是否删除ODB源文件
        if if_delete_odb_source:
            self.delete_odb_source()
        return packaged_field_values_manager

    def __getitem__(self, index):
        """
        获取指定索引对应的场输出值。

        :param index: 场输出值的索引。
        :type index: int
        :return: 场输出节点对象
        :rtype: PackagedFieldValue
        """
        return self.get_field_value_by_index(index)


class FieldValuesManager(_PackagedFieldOutputManagerBase):
    """
    FieldValuesManager 类用于管理复数的场数值，提供对管理的场数值的各种形式的访问和操作的功能。
    """

    node_datas_attribute_names = ['x_data', 'y_data', 'z_data', 'magnitude_data']
    element_datas_attribute_names = ['average_mises_data']

    @staticmethod
    def get_generate_item_by_set_length(packaged_set):
        """
        获取generate_item_by_set方法的迭代长度

        :param packaged_set: 包装的集合对象
        :return: 生成器迭代长度
        """
        if isinstance(packaged_set, PackagedOdbSet):
            return packaged_set.length
        elif isinstance(packaged_set, list):
            check_sequence_type(packaged_set, PackagedOdbSet)
            return sum(s.length for s in packaged_set)
        else:
            raise TypeError('packaged_set must be PackagedOdbSet or list of PackagedOdbSet')

    @staticmethod
    def generate_item_by_set(packaged_field_output_values, packaged_set):
        """
        根据给定的场输出值对象和封装集合，生成对应的场输出值项

        这是一个静态方法，用于根据场输出值类型(节点或单元)和给定的封装集合(节点集或单元集)，
        生成对应的场输出值项。使用生成器(yield)方式返回结果，提高内存效率。

        :param packaged_field_output_values: 包装的场输出值对象，包含场输出数据的类型(节点或单元)和具体值
        :type packaged_field_output_values: PackagedFieldOutputValues
        :param packaged_set: 封装集合对象，可以是单个PackagedOdbSet或PackagedOdbSet列表，
        :type packaged_set: PackagedOdbSet or list of PackagedOdbSet
        表示节点集或单元集
        :return: 生成器，每次迭代产生一个场输出值项(节点或单元对应的场输出值)
        :rtype: Generator
        :raises TypeError: 如果输入参数类型不符合要求
        """
        # 检查场输出值对象类型是否正确
        check_type(packaged_field_output_values, PackagedFieldOutputValues)
        # 准备集合列表，统一处理单个集合和集合列表的情况
        packaged_sets = []
        # 处理不同类型的输入集合:
        if isinstance(packaged_set, PackagedOdbSet):
            # 1. 如果是单个PackagedOdbSet对象，放入列表
            packaged_sets.append(packaged_set)
        elif isinstance(packaged_set, list):
            # 2. 如果是列表，检查是否为空并验证列表单元类型
            if not packaged_set:
                raise TypeError("packaged_set must be not empty")
            check_sequence_type(packaged_set, PackagedOdbSet)
            packaged_sets.extend(packaged_set)
        else:
            # 3. 无效输入类型，抛出异常
            raise TypeError("packaged_set must be PackagedOdbSet or list of PackagedOdbSet")
        # 遍历所有集合，生成场输出值项
        for packaged_set in packaged_sets:
            if packaged_field_output_values.if_node_type:
                # 如果是节点类型的场输出，遍历集合中的所有节点
                for packaged_node in packaged_set.get_packaged_nodes():
                    # 获取节点对应的场输出值并生成
                    yield packaged_field_output_values.get_field_value_by_packaged_node(packaged_node)
            else:
                # 如果是单元类型的场输出，遍历集合中的所有单元
                for packaged_element in packaged_set.get_packaged_elements():
                    # 获取单元对应的场输出值并生成
                    yield packaged_field_output_values.get_element_field_value_by_packaged_element(packaged_element)

    def __init__(self, packaged_step, item_generator=None, field_output_type=None, *argus, **keyword):
        """
        初始化类的实例变量。
        """
        super(FieldValuesManager, self).__init__(packaged_step, item_generator, *argus, **keyword)
        self._field_output_type = None
        if field_output_type:
            self.field_output_type = field_output_type
        self._pairs_index_ranges = None
        self._if_send_progress = False
        self._managed_relative_data = None
        self._if_get_relative_datas = True

    @property
    def field_output_type(self):
        """
        获取场输出数据类型
        :return: 场输出数据类型
        :rtype: str
        """
        if self._field_output_type is None:
            raise TypeError("field_output_type must be set")
        return self._field_output_type

    @field_output_type.setter
    def field_output_type(self, field_output_type):
        """
        设置场输出数据类型
        :param field_output_type: 场输出数据类型
        :type field_output_type: str
        :return:  None
        :rtype: None
        :raises TypeError: 如果场输出数据类型无效
        """
        self._field_output_type_constant.verify_all_field_output_type(field_output_type)
        self._field_output_type = field_output_type

    def set_item_generator(self, item_generator, length, field_output_type=None):
        """
        设置场输出值管理器的项目生成器并进行验证

        :param item_generator: 生成场输出值的迭代器，不能为空
        :param length: 迭代器的预期长度(此方法中未使用，但传递给父类)
        :param field_output_type: 场输出数据类型
        :return:  None
        :raises TypeError: 如果项目生成器为空或生成的项目类型不正确
        """
        if self.field_output_type is None:
            if field_output_type is None:
                raise TypeError("Either self.field_output_type or field_output_type argument must be set")
            self.field_output_type = field_output_type
        super(FieldValuesManager, self).set_item_generator(item_generator, length)

    def extend_item_generator(self, generator_for_extending):
        """
        扩展当前对象的item_generator，将新的生成器连接到原有生成器后面。
        如果当前没有item_generator，则直接使用新的生成器。

        :param generator_for_extending: 用于扩展的生成器对象
        :type generator_for_extending: generator
        :return: None
        :rtype: None
        """
        if self.item_generator:
            # 使用生成器表达式将两个生成器连接起来，创建一个新的生成器
            # 该生成器会先迭代原有生成器的所有单元，再迭代新生成器的所有单元
            self.item_generator = (item for gen in (self.item_generator, generator_for_extending) for item in gen)
        else:
            # 如果当前没有item_generator，则直接使用新的生成器
            self.item_generator = generator_for_extending

    def _set_packaged_item_relative_data(self, packaged_item, index=None):
        """
        设置打包项目的相对数据。

        根据self._managed_relative_data的类型和index（如果需要）来设置打包项目的相对数据。
        此函数旨在为打包项目添加相关的相对数据，这些数据可以是单个场输出值或通过索引生成的场输出值集合。

        :param packaged_item: 要设置相对数据的打包项目。
        :type packaged_item: PackagedFieldValue|PackagedElementFieldValue
        :param index: 用于生成相对数据的索引（仅当self._managed_relative_data是FieldValuesManager实例时需要）。
        :type index: int|None
        :return: 设置了相对数据的打包项目实例。
        :rtype: PackagedFieldValue|PackagedElementFieldValue

        :raises TypeError: 如果index未设置且self._managed_relative_data是FieldValuesManager实例。
        """
        # 遍历所有管理的相对数据
        if self._managed_relative_data:
            # 如果相对数据是PackagedFieldValueBase实例
            if isinstance(self._managed_relative_data, PackagedFieldValueBase):
                # 直接设置打包项目的相对数据
                packaged_item.relative_packaged_field_value = self._managed_relative_data
            # 如果相对数据是FieldValuesManager实例
            elif isinstance(self._managed_relative_data, FieldValuesManager):
                # 如果索引未设置，抛出异常
                if index is None:
                    raise TypeError("index must be set")
                # 判断当前实例是否与_managed_relative_data相同
                if self._managed_relative_data is self:
                    # 如果相同，则直接将当前处理的项赋值给relative_packaged_field_value，
                    # 避免与get_packaged_item_by_index()方法间的循环调用。
                    relative_packaged_field_value = packaged_item
                else:
                    # 如果不同，则通过索引从_managed_relative_data中获取对应的项
                    relative_packaged_field_value = self._managed_relative_data.get_packaged_item_by_index(index)
                # 通过项的索引生成相对数据
                packaged_item.relative_packaged_field_value = relative_packaged_field_value
        return packaged_item

    def add_packaged_items(self, packaged_item, attribute_names=None, if_delete_odb_source=True):
        if self._field_output_type is None:
            self.field_output_type = packaged_item.field_output_type
        if attribute_names is None:
            is_node_type = self._field_output_type_constant.determine_node_type(packaged_item.field_output_type)
            # 根据类型选择相应的属性名称
            attribute_names = self.node_datas_attribute_names if is_node_type \
                else self.element_datas_attribute_names
        else:
            # 检查提供的属性名称序列是否有效
            check_sequence_type(attribute_names, str)
        super(FieldValuesManager, self).add_packaged_items(packaged_item, attribute_names, if_delete_odb_source)

    def load_generated_packaged_items(
            self, start=None, end=None, attribute_names=None, if_delete_odb_source=True, force_load=False):
        # 确定是否为节点类型
        if attribute_names is None:
            is_node_type = self._field_output_type_constant.determine_node_type(self.field_output_type)
            # 根据类型选择相应的属性名称
            attribute_names = self.node_datas_attribute_names if is_node_type \
                else self.element_datas_attribute_names
        else:
            # 检查提供的属性名称序列是否有效
            check_sequence_type(attribute_names, str)
        # 调用父类方法加载打包的项目
        super(FieldValuesManager, self).load_generated_packaged_items(start, end, attribute_names, if_delete_odb_source)

    def all_field_values_list(self):
        """
        获取所有场输出值的包装列表。此方法会将当前对象管理的所有场输出节点对象的引用都加载进内存，若节点过多会有内存溢出的风险，注意管理内存。
        如要获取每一个PackagedFieldValueBase对象进行处理，建议使用get_every_field_value迭代器访问一个处理一个

        :return: 包含所有场输出值的包装列表。
        :rtype: list[PackagedFieldValueBase]
        """
        # 使用列表推导式，对每个值对进行处理，收集所有场输出值的包装结果
        return [item for item in self.get_every_managed_item()]

    def set_managed_relative_data(self, relative_data):
        """
        设置管理项的相对数据引用。设置后，当前管理器对象在获取被管理对象时会为其设置此方法中指定的相对数据。

        - 如果 `relative_data` 为 `None`，则不执行任何操作。
        - 如果 `relative_data` 是 `PackagedFieldValueBase` 的单个实例，则为所有被管理项设置相同的相对数据引用。
        - 如果 `relative_data` 是 `FieldValuesManager` 实例，则其长度必须与当前管理器中的被管理项数量相同，
            并且每个被管理项将使用 `relative_data` 中对应位置的相对数据引用。

        :param relative_data: 包含相对数据的对象，可以是 `PackagedFieldValueBase`、`FieldValuesManager` 或 `None`。
        :type relative_data: PackagedFieldValueBase | FieldValuesManager | None
        :raises ValueError: 如果 `relative_data` 是 `FieldValuesManager` 且其长度与当前管理器的长度不匹配。
        """
        # 检查relative_data是否为FieldValuesManager实例
        if isinstance(relative_data, FieldValuesManager):
            # 如果是，检查两个field_values_manager的长度是否相等
            if self.length != relative_data.length:
                raise ValueError(
                    "The length of the two field_values_manager must be the same,"
                    "not self.length:'{}' relative_data.length:'{}'".format(self.length, relative_data.length))
        else:
            # 长度相等时，检查relative_data中单元的类型
            check_type(relative_data, PackagedFieldValueBase, None)
        self._managed_relative_data = relative_data

    def get_max_data(self, attribute_names, relative_data=None, if_compare_abs=True, if_get_relative_datas=True):
        """
        根据指定的属性名称列表，获取每个属性的最大值对应的封装场输出单元或节点对象。

        此函数通过比较每个属性的值（或绝对值）与参考数据的差值，来确定最大值。
        通过调用封装场输出节点或单元对象的get_relative_data()获取属性值，当管理的是设置了相对值的对象时，获取相对值比较，否则获取绝对值比较。
        如果没有提供参考数据，则默认使用0作为参考值。如果提供的参考数据类型不正确，则会抛出TypeError。
        如果指定的属性名称列表中包含无效的属性名称，则会抛出ValueError。

        :param if_get_relative_datas: （bool）获管理项的值后，对比其的真实或相对值，此项设置开始时是否获取管理项的相对值，默认为True
        :type if_get_relative_datas: bool
        :param attribute_names: （list[str]）:属性名称列表，用于指定需要比较的数据。
        :type attribute_names: list[str]
        :param relative_data: 参考数据，可以是PackagedFieldValueBase实例或FieldValuesManager实例，默认为None。
                为FieldValuesManager时需与当前对象管理的数据数量相同，将计算当前对象管理的所有数据减去此项对应索引位置的相对值的最大值。
                为PackagedFieldValueBase时将计算当前对象管理的所有数据减去此项的相对值的最大值。
                为None时，计算每项真实值的最大值。
        :type relative_data: PackagedFieldValueBase | FieldValuesManager | None
        :param if_compare_abs: （bool）是否比较绝对值，默认为True。
        :type if_compare_abs: bool
        :return: 一个OrderedDict，包含每个属性的最大值的PackagedFieldValue或PackagedElementFieldValue对象。
        :rtype: OrderedDict[str, PackagedFieldValue | PackagedElementFieldValue]
        """
        # 检查attribute_names是否为字符串序列
        check_sequence_type(attribute_names, str)
        # 验证所有属性名称是否有效
        for attribute_name in attribute_names:
            if attribute_name not in self.node_datas_attribute_names + self.element_datas_attribute_names:
                raise ValueError("{} is not a valid attribute name".format(attribute_name))

        try:
            # 获取指定属性的数据字典
            datas = self.generate_every_specified_attribute_dict(attribute_names, if_get_relative_datas)
            # 获取初始数据
            initial_data = next(datas)
        except StopIteration:
            # 如果没有数据可用，则抛出ValueError
            raise ValueError("No data available for the specified attributes")

        # 初始化最大数据索引字典
        max_data_index_dict = OrderedDict((key, {"index": 0, "data": initial_data[key]}) for key in attribute_names)

        def get_max_data_at_single_relative_data(relative):
            """
            根据单个相对数据，更新最大数据索引字典。

            参数:
            - relative: 相对数据字典，包含每个属性的参考值。

            返回:
            - 一个OrderedDict，包含每个属性的最大值及其索引信息。
            """
            for index, data_dict in enumerate(datas, start=1):
                for key in attribute_names:
                    last_value = max_data_index_dict[key]["data"]
                    current_value = data_dict[key] - relative[key]
                    # 根据是否比较绝对值，更新最大数据索引字典
                    if if_compare_abs:
                        if abs(current_value) > abs(last_value):
                            max_data_index_dict[key].update({"data": current_value, "index": index})
                    else:
                        if current_value > last_value:
                            max_data_index_dict[key].update({"data": current_value, "index": index})
            return OrderedDict((key, self.get_packaged_item_by_index(max_data_index_dict[key]["index"]))
                               for key in attribute_names)

        # 根据relative_data的类型，执行不同的逻辑
        if relative_data is None:
            relative = {key: 0 for key in attribute_names}
            return get_max_data_at_single_relative_data(relative)

        elif isinstance(relative_data, PackagedFieldValueBase):
            relative = {key: get_nested_attribute(relative_data, key) for key in attribute_names}
            relative_data.delete_odb_source()
            return OrderedDict((key, value.set_relative_packaged_field_value(relative_data)) for key, value in
                               get_max_data_at_single_relative_data(relative).items())

        elif isinstance(relative_data, FieldValuesManager):
            # 检查两个FieldValuesManager的长度是否相同
            if self.length != relative_data.length:
                raise ValueError(
                    "The length of the two field_values_manager must be the same,"
                    "not self.length:'{}' relative_data.length:'{}'".format(self.length, relative_data.length))
            try:
                # 获取相对数据
                relative_datas = relative_data.generate_every_specified_attribute_dict(attribute_names)
                relative_initial_data = next(relative_datas)
            except StopIteration:
                raise ValueError("No data available for the specified attributes")

            # 更新最大数据索引字典，使用相对数据差值
            max_data_index_dict = OrderedDict(
                (key, {"index": 0, "data": value["data"] - relative_initial_data[key]})
                for key, value in max_data_index_dict.items())

            for index, (data_dict, relative_data_dict) in enumerate(zip(datas, relative_datas), start=1):
                for key in attribute_names:
                    last_value = max_data_index_dict[key]["data"]
                    current_value = data_dict[key] - relative_data_dict[key]
                    # 根据是否比较绝对值，更新最大数据索引字典
                    if if_compare_abs:
                        if abs(current_value) > abs(last_value):
                            max_data_index_dict[key].update({"data": current_value, "index": index})
                    else:
                        if current_value > last_value:
                            max_data_index_dict[key].update({"data": current_value, "index": index})

            results = OrderedDict()
            for attribute_name in attribute_names:
                max_data_ = self.get_packaged_item_by_index(max_data_index_dict[attribute_name]["index"])
                relative_data_ = relative_data.get_packaged_item_by_index(max_data_index_dict[attribute_name]["index"])
                max_data_.set_relative_packaged_field_value(relative_data_)
                results[attribute_name] = max_data_
            return results
        else:
            # 如果relative_data的类型不正确，则抛出TypeError
            raise TypeError("The relative_data must be of type {} or {} but not {}".format(
                PackagedFieldValueBase, FieldValuesManager, relative_data.__class__))

    def get_every_managed_item(
            self, start=None, end=None, if_delete_odb_source=True, if_add_packaged_items=False, attribute_names=None):
        for i, item in enumerate(super(FieldValuesManager, self).get_every_managed_item(
                start, end, if_delete_odb_source, if_add_packaged_items, attribute_names)):
            yield self._set_packaged_item_relative_data(item, i)

    def get_packaged_item_by_index(self, index):
        packaged_item = super(FieldValuesManager, self).get_packaged_item_by_index(index)
        return self._set_packaged_item_relative_data(packaged_item, index)

    def set_if_get_relative_datas(self, if_get_relative_datas):
        """
        设置在获取被管理项的属性值时，默认是否获取其相对数据。

        此方法用于控制访问被管理项的属性时，是否自动包含相对数据：

        - 如果设置为 `True`（默认值）：
            - 如果被管理项设置了相对数据引用，则获取相对值；
            - 如果未设置相对数据引用，则仍获取真实值。
        - 如果设置为 `False`：
            - 不管是否设置了相对数据引用，始终只获取真实值。

        当被管理项设置了相对数据引用后，可以通过此方法选择获取其相对值或真实值。此设置影响当前管理器获取被管理项值的行为。

        :param if_get_relative_datas: 是否在获取属性值时默认获取相对数据。默认为True
        :type if_get_relative_datas: bool|None
        :return: None
        :raises TypeError: 如果参数类型不是布尔值。
        """
        check_type(if_get_relative_datas, bool)
        if if_get_relative_datas is None:
            self._if_get_relative_datas = True
        self._if_get_relative_datas = if_get_relative_datas

    @property
    def index_list(self):
        """
        获取所有索引的列表。

        :return: 包含所有索引的列表。
        :rtype: list
        """
        return self.get_specified_attribute_list("index")

    @property
    def x_data_list(self):
        """
        返回所有场数值对象的 x 数据组成的列表。
        """
        return self.get_specified_attribute_list("x_data")

    @property
    def y_data_list(self):
        """
        返回所有场数值对象的 y 数据组成的列表。
        """
        return self.get_specified_attribute_list("y_data")

    @property
    def z_data_list(self):
        """
        返回所有场数值对象的 z 数据组成的列表。
        """
        return self.get_specified_attribute_list("z_data")

    @property
    def magnitude_data_list(self):
        """
        返回所有场数值对象的大小（幅度）组成的列表。
        """
        return self.get_specified_attribute_list("magnitude_data")

    @property
    def mises_list(self):
        """
        返回所有场数值对象的Mises值组成的列表。
        """
        return self.get_specified_attribute_list("mises")

    @property
    def average_mises_data_list(self):
        """
        获取平均Mises应力数据列表

        该属性用于计算并返回所有打包场输出值的平均Mises应力列表。如果未预先计算，
        则会根据当前的_field_values进行计算，并缓存结果以优化性能。

        :return: 包含所有打包场输出值的平均Mises应力的列表
        """
        return self.get_specified_attribute_list("average_mises_data")

    def get_specified_attribute_list(self, attribute_name, if_get_relative_datas=None, if_delete_odb_source=True):
        """
        根据指定的属性名称，获取所有管理项中的该属性值列表。

        :param attribute_name: 指定的属性名称，用于提取每个管理项的相应属性值。
        :type attribute_name: str
        :param if_get_relative_datas: (bool): 是否获取相对数据，默认为False。
        :type if_get_relative_datas: bool
        :param if_delete_odb_source: 是否在获取属性值后删除管理项的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :return: 包含所有管理项中指定属性值的列表。
        :rtype: list
        """
        if if_get_relative_datas is None:
            if_get_relative_datas = self._if_get_relative_datas
        if if_get_relative_datas:
            # 初始化一个空列表，用于存储所有管理项的指定属性值
            datas = []
            # 遍历每一个管理项
            for field_value in self.get_every_managed_item():
                # 提取并记录管理项的指定属性值
                datas.append(field_value.get_relative_data(attribute_name))
                # 删除管理项的ODB源
                if if_delete_odb_source:
                    field_value.delete_odb_source()
            # 返回包含所有指定属性值的列表
            return datas
        return super(FieldValuesManager, self).get_specified_attribute_list(attribute_name, if_delete_odb_source)

    def generate_every_specified_attribute_dict(
            self, attribute_names, if_get_relative_datas=None, if_delete_odb_source=True):
        """
        生成一个包含指定属性的字典序列。

        本函数根据提供的属性名称列表，为每个被管理的项生成一个字典，字典中包含这些属性及其对应的值。
        可以通过参数选择是否获取相对数据以及是否删除ODB源。

        :param attribute_names: (list[str]): 包含所需属性名称的列表。
        :type attribute_names: list[str]
        :param if_get_relative_datas: (bool): 是否获取相对数据，默认为True。
        :type if_get_relative_datas: bool
        :param if_delete_odb_source: (bool): 是否在生成字典后删除管理项的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :return: 返回一个生成器，每个单元都是一个OrderedDict，包含每个被管理项目中指定的属性。
        :rtype: Generator[OrderedDict[str, Any]]
        """
        if if_get_relative_datas is None:
            if_get_relative_datas = self._if_get_relative_datas
        if if_get_relative_datas:
            # 检查attribute_names是否为字符串序列
            check_sequence_type(attribute_names, str)
            # 遍历每个被管理的项
            for item in self.get_every_managed_item():
                result_dict = OrderedDict((name, item.get_relative_data(name)) for name in attribute_names)
                # 如果if_delete_odb_source为True，则删除item的ODB源
                if if_delete_odb_source:
                    item.delete_odb_source()
                # 生成并返回result_dict
                yield result_dict
        else:
            for item in super(FieldValuesManager, self).generate_every_specified_attribute_dict(
                    attribute_names, if_delete_odb_source):
                yield item

    def get_specified_attributes_list_dict(
            self, attribute_names, if_get_relative_datas=None, if_delete_odb_source=True):
        """
        根据指定的属性名列表，从管理的所有项中提取这些属性的值，并以字典形式返回。

        :param attribute_names: 包含需提取属性名的列表。
        :type attribute_names: list[str]
        :param if_get_relative_datas: (bool): 是否获取相对数据，默认为False。
        :type if_get_relative_datas: bool
        :param if_delete_odb_source: 是否在获取属性值后删除管理项的ODB源，默认为True。
        :type if_delete_odb_source: bool
        :return: 包含每个属性名及其对应值列表的有序字典。
        :rtype: OrderedDict[str, list]
        """
        if if_get_relative_datas is None:
            if_get_relative_datas = self._if_get_relative_datas
        if if_get_relative_datas:
            # 检查attribute_names是否为字符串序列，确保输入类型正确
            check_sequence_type(attribute_names, str)
            # 初始化有序字典，用于存储属性名对应的值列表
            field_values_dict = OrderedDict()
            # 初始化字典键，确保所有指定的属性名都被初始化为空列表
            for name in attribute_names:
                field_values_dict[name] = []
            for field_value in self.get_every_managed_item(if_delete_odb_source):
                for name in attribute_names:
                    field_values_dict[name].append(field_value.get_relative_data(name))
            # 返回填充了属性值的字典
            return field_values_dict
        return super(FieldValuesManager, self).get_specified_attributes_list_dict(
            attribute_names, if_delete_odb_source)


class PackagedFieldValueBase(_PackageBase):

    def get_packaged_item_by_parent(self):
        return super(PackagedFieldValueBase, self).get_packaged_item_by_parent()

    def get_packaged_item(self):
        pass

    def __init__(self, field_output_type=None, *args, **kwargs):
        super(PackagedFieldValueBase, self).__init__(*args, **kwargs)
        self._packaged_field_values = None
        self._field_output_type = field_output_type
        self._relative_packaged_field_value = None
        self._manager_index = None
        self._instance = None
        self._packaged_instance = None

    @property
    def instance(self):
        if self._instance is None:
            self._instance = self.odb_source.instance
        return self._instance

    @property
    def packaged_instance(self):
        """
        获取封装后的实例，单元输出数据（如 S ）类型的场输出数据库有此变量
        结点输出数据（如U）无此变量时，从packaged_node属性（如有设置）中获取

        该方法会返回一个封装后的实例对象，如果该实例尚未被封装，则会先进行封装
        :return: 封装实例对象
        :rtype: PackagedInstance
        """

        # 检查是否已经存在封装后的实例，如果不存在，则进行封装
        if self._packaged_instance is None:
            instance = self.instance
            packaged_odb = self.get_specified_type_parent(PackagedOdb)
            packaged_root_assembly = packaged_odb.get_packaged_root_assembly()
            if instance is not None:
                self._packaged_instance = packaged_root_assembly.get_instance_by_name(instance.name)
            else:
                self._packaged_instance = packaged_root_assembly
        return self._packaged_instance

    @property
    def instance_name(self):
        """
        获取封装实例名称。
        :return: 封装实例名称
        :rtype: str
        """
        if isinstance(self.packaged_instance, PackagedInstance):
            name = self.packaged_instance.name
        else:
            name = PackagedRootAssembly.rootAssembly_name
        return name

    @property
    def manager_index(self):
        """
        从FieldValuesManager对象中获取此场输出数据点时，会设置此项，代表该场输出数据点在获取此场输出数据点FieldValuesManager中的索引位置。
        由此索引，可以通过FieldValuesManager对象再次获取此场输出数据点。

        :return: 帧在FieldValuesManager中的索引位置
        :rtype: int
        """
        if self._manager_index is None:
            raise AttributeError("manager_index is not set")
        return self._manager_index

    @manager_index.setter
    def manager_index(self, value):
        """
        设置场输出数据点在FieldValuesManager中的索引位置
        :param value: 场输出数据点在FieldValuesManager中的索引位置
        :return: None
        """
        check_type(value, int)
        self._manager_index = value

    @property
    def if_set_relative_packaged_field_value(self):
        """
        判断_relative_packaged_field_value是否已被设置

        :return: 如果_relative_packaged_field_value被设置，则返回True，否则返回False
        :rtype: bool
        """
        return self._relative_packaged_field_value is not None

    @property
    def relative_packaged_field_value(self):
        if self._relative_packaged_field_value is None:
            raise ValueError("The relative_packaged_field_value is not set")
        return self._relative_packaged_field_value

    @relative_packaged_field_value.setter
    def relative_packaged_field_value(self, relative_packaged_field_value):
        check_type(relative_packaged_field_value, self.__class__)
        self._relative_packaged_field_value = relative_packaged_field_value

    def set_relative_packaged_field_value(self, relative_packaged_field_value):
        check_type(relative_packaged_field_value, self.__class__)
        self._relative_packaged_field_value = relative_packaged_field_value
        return self

    def get_relative_data(self, attribute_name):
        """
        获取相对于_relative_packaged_field_value的属性数据。

        本方法旨在计算并返回指定属性相对于_relative_packaged_field_value的差异值。
        如果_relative_packaged_field_value未定义，则直接返回当前对象的属性值。

        :param attribute_name: 属性名称，用于获取当前对象及_relative_packaged_field_value的对应属性。
        :type attribute_name: str
        :return: 属性值的差异或当前对象的属性值（如果_relative_packaged_field_value未定义）。

        :raises AttributeError: 如果指定的属性在当前对象中不存在。
        :raises TypeError: 如果attribute_name不是字符串类型。
        """
        # 检查attribute_name是否为字符串类型
        check_type(attribute_name, str)
        # 如果_relative_packaged_field_value存在，计算并返回属性值的差
        result = None
        if self._relative_packaged_field_value:
            try:
                result = getattr(self, attribute_name) - getattr(self._relative_packaged_field_value, attribute_name)
            except AttributeError:
                result = get_nested_attribute(self, attribute_name)
        else:
            # 如果_relative_packaged_field_value不存在，直接返回当前对象的属性值
            result = get_nested_attribute(self, attribute_name)
        return result

    @property
    def packaged_field_values(self):
        if self._packaged_field_values is None:
            self._packaged_field_values = self.get_specified_type_parent(PackagedFieldOutputValues)
        return self._packaged_field_values

    @property
    def field_output_type(self):
        if self._field_output_type is None:
            self._field_output_type = self.packaged_field_values.field_output_type
        return self._field_output_type


class PackagedFieldValue(PackagedFieldValueBase):
    """
    该类用于封装场输出值及相关属性，继承自PackageBase类。

    Attributes:
        field_value: 原始场输出值对象，包含各种属性如nodeLabel、data、magnitude等。
        index: 场输出值的索引，用于标识特定的场输出值。
        node_label: 节点标签，表示场输出值所属的节点。
        data: 场输出值的数据内容。
        magnitude: 场输出值的量级。
        element_label: 单元标签，表示场输出值所属的单元。
        mises: 弥散值，一种材料力学属性。
    """

    def get_packaged_item_by_parent(self):
        packaged_field_value_values = self.get_parent()
        return packaged_field_value_values.get_field_value_by_index(self.index).odb_source

    def __init__(self, odb_source=None, index=None, *args, **kwargs):
        """
        初始化PackagedFieldValue对象。

        :param odb_source: 当前对象封装的odb场输出数据节点对象
        :type odb_source: FieldValue
        :param index: 当前场输出数据在父节点PackagedFieldOutputValues对象中的索引
        :type index: int
        :param args:
        :param kwargs:
        """
        super(PackagedFieldValue, self).__init__(*args, **kwargs)
        self._odb_source = odb_source
        self.index = index
        self._packaged_frame = None
        self._packaged_node = None
        self._data = None
        self._x_data = None
        self._y_data = None
        self._z_data = None
        self._magnitude_data = None
        self._element_label = None
        self._mises = None

    @property
    def packaged_node(self):
        """
        获取封装节点属性。需显示指定后使用
        :return: 包装节点对象
        :rtype: PackagedNode
        """
        if self._packaged_node is None:
            raise ValueError("The packaged_node is not set")
        return self._packaged_node

    @packaged_node.setter
    def packaged_node(self, packaged_node):
        check_type(packaged_node, PackagedNode)
        if self.node_label != packaged_node.label:
            raise ValueError(
                "The packaged_node is not match with the node_label field_node_label:{},mesh_label:{}".format(
                    self.node_label, packaged_node.label))
        self._packaged_node = packaged_node

    @property
    def packaged_frame(self):
        """
        获取封装帧属性。需显示指定后使用

        如果封装帧未设置，则抛出ValueError异常。
        """
        # 检查封装帧是否已设置，如果未设置，则抛出异常
        if self._packaged_frame is None:
            self._packaged_frame = self.get_specified_type_parent(PackagedFrame)
        # 如果封装帧已设置，则返回它
        return self._packaged_frame

    @property
    def node_label(self):
        return self.odb_source.nodeLabel

    @property
    def data(self):
        """
        x、y、z三方向值的列表
        :return:
        """
        if self._data is None:
            self._data = self.odb_source.data
        return self._data

    @property
    def data_dict(self):
        """
        返回一个包含场输出数据的字典。

        :return:dict: 包含'x'、'y'、'z'和'magnitude'键的字典，对应的值分别是场输出数据的x轴数据、
            y轴数据、z轴数据和magnitude数据。
        :rtype: dict[str, float]
        """
        return {"x": self.x_data, "y": self.y_data, "z": self.z_data, "magnitude": self.magnitude_data}

    @property
    def magnitude_data(self):
        """
        获取场输出数据的magnitude数据。
        :return: magnitude数据
        """
        if self._magnitude_data is None:
            self._magnitude_data = self.odb_source.magnitude
        return self._magnitude_data

    @property
    def element_label(self):
        """
        获取场输出数据的单元标签。
        :return: 单元标签
        """
        if self._element_label is None:
            self._element_label = self.odb_source.elementLabel
        return self._element_label

    @property
    def mises(self):
        """
        获取弥散值。
        :return: 弥散值
        """
        if self._mises is None:
            self._mises = self.odb_source.mises
        return self._mises

    @property
    def x_data(self):
        """
        获取x轴数据。

        :return: x轴数据。
        """
        if self._x_data is None:
            try:
                self._x_data = self.data[0]
            except Exception:
                self._x_data = self.data
        return self._x_data

    @property
    def y_data(self):
        """
        获取y轴数据。

        :return: y轴数据。
        """
        if self._y_data is None:
            try:
                self._y_data = self.data[1]
            except Exception:
                self._y_data = self.data
        return self._y_data

    @property
    def z_data(self):
        """
        获取z轴数据。

        :return: z轴数据。
        """
        if self._z_data is None:
            try:
                self._z_data = self.data[2]
            except Exception:
                self._z_data = self.data
        return self._z_data

    def set_datas(self, x_data=None, y_data=None, z_data=None, magnitude_data=None, mises=None, **keyword):
        """
        集中设置数据属性。当需要手动创建对象管理数据时使用。

        该方法允许通过单个方法调用来设置多个数据属性，包括x_data、y_data、z_data、
        magnitude_data和mises。任何未明确指定的属性将保持不变。

        :param x_data: X数据，默认为None。
        :param y_data: Y数据，默认为None。
        :param z_data: Z数据，默认为None。
        :param magnitude_data: 默认为None。
        :param mises:  默认为None。
        :param keyword: 其他关键字参数，允许设置额外的属性。
        :return:  None
        """
        # 创建一个包含所有可能的数据属性的字典
        keyword_ = {"x_data": x_data, "y_data": y_data, "z_data": z_data, "magnitude_data": magnitude_data,
                    "mises": mises}

        # 更新字典，以包含任何额外的关键字参数
        keyword.update(keyword_)

        # 使用更新后的字典设置私有属性
        self.set_attributes(**keyword)


class PackagedElementFieldValue(PackagedFieldValueBase):
    """
    包装单元场输出数据。
    """

    def __init__(self, field_values_list=None, *args, **kwargs):
        """
        初始化方法

        :param field_values_list: 包含 PackagedFieldValue 对象的列表,每个对象代表一个单元的积分点
        """
        super(PackagedElementFieldValue, self).__init__(*args, **kwargs)
        self._field_values_list = None
        self.field_values_list = field_values_list
        self._average_mises_data = None
        self._packaged_element = None

    @property
    def instance(self):
        if self._instance is None:
            self._instance = self.odb_source[0].instance
        return self._instance

    @property
    def field_values_list(self):
        """
        获取单元的所有积分点场输出数据列表。
        :return:
        """
        if self._field_values_list is None:
            raise RuntimeError(
                "field_values_list is not set.Before using field-values_list, please set it first, "
                "or directly set the property value")
        return self._field_values_list

    @field_values_list.setter
    def field_values_list(self, field_values_list):
        """
        设置单元的所有积分点场输出数据列表。
        :param field_values_list: 包含 PackagedFieldValue 对象的列表,每个对象代表一个单元的积分点
        :return:  None
        """
        if field_values_list is not None:
            # 检查 field_values 是否是 PackagedFieldValue 的列表
            check_sequence_type(field_values_list, PackagedFieldValue)
            self._field_values_list = self.ChildFieldValuesList()
            for field_value in field_values_list:
                self._field_values_list.append(field_value)

    def delete_odb_source(self):
        """
        递归删除场输出值列表中的每个场输出值的ODB值。

        遍历场输出值列表，对于每个场输出值，调用其delete_odb_field_value方法来递归删除其ODB值。
        这通常用于需要清理与场输出值关联的ODB值的场景。
        """
        for field_value in self.field_values_list:
            # 递归调用场输出值的delete_odb_field_value方法来删除其ODB值
            field_value.delete_odb_source()

    @property
    def packaged_element(self):
        """
        获取封装后的单元

        此属性用于获取当前实例的封装后的单元。如果封装后的单元未设置，将抛出ValueError异常。

        :return: 封装后的单元
        :rtype: PackagedElement
        :raises ValueError: 如果封装后的单元未设置
        """
        if self._packaged_element is None:
            # 如果封装后的单元未设置，抛出ValueError异常
            raise ValueError("The packaged_element is not set")
        return self._packaged_element

    @packaged_element.setter
    def packaged_element(self, packaged_element):
        """
        设置封装单元的属性。

        :param packaged_element: 要设置为封装单元的对象
        :return: 无返回值
        """
        # 验证packaged_element参数的类型是否为PackagedElement，如果不是则抛出TypeError异常
        if not isinstance(packaged_element, PackagedElement):
            raise TypeError("The packaged_element must be of type {} but not {}".
                            format(PackagedElement, packaged_element.__class__))
        # 如果类型验证通过，则将packaged_element赋值给实例变量_packaged_element
        self._packaged_element = packaged_element

    class ChildFieldValuesList(list):
        """
        该类继承自list，用于管理一组PackagedFieldValue对象的列表。
        它确保列表中所有的单元都是PackagedFieldValue的实例。
        """

        def append(self, __object):
            """
            向列表中添加一个PackagedFieldValue对象。

            参数:
            __object -- 要添加到列表中的对象

            返回:
            无返回值

            异常:
            TypeError -- 如果__object不是FieldValuesManager的实例，则抛出此异常
            """
            # 检查要添加的对象是否为PackagedFieldValue类型，如果不是则抛出TypeError
            if not isinstance(__object, PackagedFieldValue):
                raise TypeError(
                    "The child_field_values must be of type {} but not {}".format(
                        PackagedFieldValue, __object.__class__))
            # 调用父类的append方法来添加对象
            super(PackagedElementFieldValue.ChildFieldValuesList, self).append(__object)

    def get_packaged_item(self):
        return self.field_values_list[0]

    @property
    def odb_source(self):
        """
        获取所有场输出值的odb_source属性列表。

        通过遍历field_values_list中的每个项，收集它们的odb_source属性，
        并以列表形式返回。这种方式提供了一种简洁的方法来获取所有场输出的odb_source信息。

        :return: 一个包含所有场输出值的odb_source属性的列表。
        :rtype: list[FieldValue]
        """
        return [i.odb_source for i in self.field_values_list]

    @property
    def average_mises_data(self):
        """
        计算并返回位移场中所有项的平均Mises应力。

        该属性首先检查是否已缓存计算过的平均Mises应力值，如果没有，则遍历
        field_values_list中的所有项，计算它们的Mises应力的平均值，并保存该值
        以提高未来访问的效率。

        :return: 位移场中所有项的平均Mises应力。
        """
        # 检查是否存在已计算的平均Mises应力值
        if self._average_mises_data is None:
            # 如果没有计算过，从field_values_list中提取所有项的Mises应力
            mises_list = [item.mises for item in self.field_values_list]
            # 计算Mises应力的平均值
            self._average_mises_data = sum(mises_list) / len(mises_list)
        # 返回计算过的平均Mises应力值
        return self._average_mises_data

    @property
    def all_mises(self):
        return [item.mises for item in self.field_values_list]

    @property
    def indexes(self):
        """
        获取所有场输出值的索引列表

        此属性遍历场输出值列表(self.field_values_list)，并返回每个场输出值对象的索引属性组成的列表
        :return: 包含所有场输出值对象索引的列表
        :rtype: list
        """
        # 通过列表推导式，获取并返回每个场输出值对象的索引列表
        return [item._index for item in self.field_values_list]

    def set_datas(self, average_mises_data, **kwargs):
        """
        集中设置数据属性。当需要手动创建对象管理数据时使用。

        该方法允许通过单个方法调用来设置多个数据属性，任何未明确指定的属性将保持不变。
        :param average_mises_data: 平均Mises应力数据
        :type average_mises_data: float
        :param kwargs: 其他属性
        :type kwargs: dict
        :return:  无
        """
        kwargs_ = {"average_mises_data": average_mises_data}
        kwargs.update(kwargs_)
        self.set_attributes(**kwargs)


if __name__ == '__main__':
    pass
