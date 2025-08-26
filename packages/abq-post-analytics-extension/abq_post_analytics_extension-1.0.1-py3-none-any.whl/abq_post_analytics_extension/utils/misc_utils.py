# -*- coding: UTF-8 -*-
import copy
import math
import multiprocessing
import sys
from multiprocessing.dummy import Pool as ThreadPool

try:
    from typing import Generator
except ImportError:
    pass


# 获取对象大小
class GetSize(object):
    @staticmethod
    def convert_size(size_bytes):
        """
        将字节大小转换为合适的单位（B, KB, MB, GB）。

        :param size_bytes: 字节大小。
        :type size_bytes: int
        :return: 转换后的大小字符串。
        :rtype: str
        """
        units = ['B', 'KB', 'MB', 'GB']
        if size_bytes == 0:
            return "0B"
        index = min(int(size_bytes.bit_length() / 10), len(units) - 1)
        converted_size = size_bytes / (1024 ** index)
        return "{converted_size:.2f} {unit}".format(converted_size=converted_size, unit=units[index])

    @staticmethod
    def get_object_size(obj):
        """
        获取对象的内存大小，并转换为合适的单位。

        :param obj: 要测量内存大小的对象。
        :type obj: object
        :return: (sys_size_str, total_size_str)，其中 sys_size_str 是对象本身的内存大小字符串，total_size_str 是对象及其引用的所有子对象的总内存大小字符串。
        :rtype: (str, str)
        """
        sys_size = sys.getsizeof(obj)
        sys_size_str = GetSize.convert_size(sys_size)
        try:
            from pympler import asizeof
            total_size = asizeof.asizeof(obj)
        except ImportError:
            total_size = sys_size
        total_size_str = GetSize.convert_size(total_size)
        return sys_size_str, total_size_str

    @staticmethod
    def print_object_size(obj):
        """
        获取对象的内存大小并打印出来。

        :param obj: 要测量内存大小和打印的对象。
        :return:  None
        """
        sys_size_str, total_size_str = GetSize.get_object_size(obj)
        print("\nInstance of class:'{}' size using sys.getsizeof: {}".format(type(obj).__name__, sys_size_str))
        print("Total instance of class:'{}' size using pympler.asizeof: {}".format(type(obj).__name__, total_size_str))


# 动态创建子类。
def create_subclass(*classes):
    """
    动态创建子类。

    这个函数接收一个或多个父类作为参数，并动态地创建它们的子类。该子类会继承所有父类的特性。
    此外，函数还会为子类的所有方法添加 super() 调用，以确保在子类方法中可以初始化父类的方法。

    :param classes: 一个或多个父类。
    :type classes: tuple[type]
    :return: 新创建的子类。
    :rtype: type
    """
    # 创建一个新的类，命名为'Subclass'，父类为传入的所有类
    subclass = type('Subclass', tuple(classes), {})

    # 遍历新创建的子类的所有属性
    for name, method in subclass.__dict__.items():
        # 如果属性是一个可调用的方法
        if callable(method):
            # 定义一个新的方法来替代原有的方法
            def new_method(self, *args, **kwargs):
                # 在原有方法调用前，先调用所有父类的初始化方法
                super(subclass, self).__init__(*args, **kwargs)
                # 调用并返回原有方法的结果
                return method(self, *args, **kwargs)

            # 在子类中用新的方法替代原有的方法
            setattr(subclass, name, new_method)

    # 返回新创建的子类
    return subclass


# 单例类基类，确保派生类只有一个实例。
class Singleton(object):
    """
    单例类基类，确保派生类只有一个实例。

    与元类实现的单例模式不同，该类通过重写 `__new__` 方法来实现单例模式。
    这种方式更直观，适合不需要使用元类的场景。

    区别：
    1. 实现方式：
       - 元类实现：通过元类控制类的创建和实例化。
       - 当前实现：通过重写 `__new__` 方法控制实例的创建。
    2. 使用方式：
       - 元类实现：需要将元类传递给目标类。
       - 当前实现：直接继承 `Singleton` 类即可。
    3. 灵活性：
       - 元类实现：更适合需要动态控制类行为的场景。
       - 当前实现：更适合简单的单例需求。
    """
    _instance = None  # 一个类变量，用来存储单例对象。所有从 Singleton 类派生出的对象共享这个变量。

    def __new__(cls, *args, **kwargs):
        """
        控制 Singleton 类或其子类的实例创建过程，确保只有一个实例被创建。

        与元类实现不同，该方法通过检查类变量 `_instance` 是否为 None 来决定是否创建新实例。
        如果是第一次调用，则创建实例并调用初始化方法；否则直接返回已存在的实例。

        :param args: 传递给实例构造函数的参数。
        :param kwargs: 传递给实例构造函数的关键字参数。
        :return: 返回单例实例。
        """
        if not cls._instance:
            # 当 _instance 为 None 时，创建新实例并赋值给 _instance
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize(*args, **kwargs)
            cls._init_options(cls._instance)
        return cls._instance  # 返回单例实例

    def _initialize(self, *args, **kwargs):
        """
        初始化对象的状态或其他资源。

        该方法将初始化逻辑移到 `__new__` 方法中，确保在创建实例时只进行一次初始化。
        使用 `*args` 和 `**kwargs` 参数以提供灵活性，允许传递不定数量的位置参数和关键字参数。

        与元类实现不同，这里的初始化逻辑是显式调用的，而不是在元类的 `__call__` 方法中隐式处理。

        :param args: 不定数量的位置参数（未使用）
        :param kwargs: 不定数量的关键字参数（未使用）
        :return: None
        """
        # 初始化逻辑
        pass

    @classmethod
    def _init_options(cls, instance):
        """
        初始化选项方法。

        该方法用于初始化类的选项，确保实例在使用前完成必要的配置和设置。
        它是一个类方法，可以在不创建类实例的情况下被调用。

        与元类实现不同，这里的选项初始化是显式调用的，而不是在元类的 `__call__` 方法中隐式处理。

        :param instance: 类的实例，该方法将针对其实现初始化选项。
        :return: 无返回值。该方法主要用于其内部的副作用，即对实例的选项进行初始化。
        """
        pass


class Singleton2(type):
    """
    单例模式元类，确保一个类只能创建一个实例。

    原理：
    1. 使用元类 `type` 来控制类的创建和实例化过程。
    2. 通过类属性 `_instances` 来存储每个类的唯一实例。
    3. 在 `__call__` 方法中，检查类是否已经实例化，如果没有则创建并存储实例，否则直接返回已存在的实例。

    功能：
    1. 保证一个类在整个应用程序生命周期中只有一个实例。
    2. 适用于需要全局唯一对象的场景，如配置管理、数据库连接池等。

    使用：
    1. 将此类作为元类传递给需要实现单例模式的类。
    2. 例如：
        class MyClass(object):
            __metaclass__ = Singleton
            pass
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        控制类的实例化过程，确保每个类只有一个实例。

        参数：
        - cls: 当前类。
        - *args: 传递给类构造函数的参数。
        - **kwargs: 传递给类构造函数的关键字参数。

        返回值：
        - 类的唯一实例。
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton2, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# 用于包装其他对象并提供统一的属性访问接口。
class PackageBase(object):
    """
    基类，用于包装其他对象并提供统一的属性访问接口。

    子类必须实现方法 _get_packaged_item，该方法应返回被包装的对象实例。
    __getattr__ 方法将在试图访问未定义的属性时调用 _get_packaged_item 方法，
    从而允许从被包装的对象中获取属性。
    """

    def __init__(self, *args, **kwargs):
        super(PackageBase, self).__init__(*args, **kwargs)

    def get_packaged_item(self):
        """
        返回被包装的对象实例。
        子类必须实现此方法，以指定实际被包装的对象。
        :return: 被包装的对象实例
        """
        raise NotImplementedError(
            "This method needs to be overridden by subclasses to specifies the object that is actually wrapped.")

    def __getattr__(self, attr_name):
        """
        当尝试访问的属性不存在于当前对象时调用此方法，尝试从self._get_packaged_item()中获取该属性。

        本方法尝试从当前对象和包装的对象中查找属性，并添加到当前对象的属性字典中，

        参数:
        - attr_name: 尝试访问的属性名称。

        返回:
        - 返回找到的属性值。
        """
        # 尝试从当前对象中获取属性，但不使用getattr以避免递归
        if attr_name in self.__dict__:
            return self.__dict__[attr_name]
        try:
            attr_value = getattr(self.get_packaged_item(), attr_name)
        except  AttributeError as e:
            packaged_item = self.get_packaged_item()
            e.args = ("{}\n{}".format(e, "'{}'and '{}' object has no attribute '{}'".format(
                type(self).__name__ if self else self, packaged_item.__name__ if packaged_item else packaged_item,
                attr_name)),)
            raise e
        setattr(self, attr_name, attr_value)
        return attr_value
        # # 尝试从包装的对象中获取属性
        # if hasattr(self.get_packaged_item(), attr_name):
        #     attr_value = getattr(self.get_packaged_item(), attr_name)
        #     setattr(self, attr_name, attr_value)
        #     return attr_value
        # # 如果两个地方都没有该属性，则抛出异常
        # raise AttributeError(
        #     "'{}'and '{}' object has no attribute '{}'".format(
        #         type(self).__name__, self.get_packaged_item().__name__, attr_name))


# 提供验证场输出类型是否在本类中的静态属性中的功能，
class FieldOutputTypeConstant(object):
    """
    提供验证输入的场输出类型是否有效，并判断其是单元类型还是节点类型的功能。
    """
    _FieldOutput_type_U = "U"
    _FieldOutput_type_S = "S"
    _FieldOutput_type_A = "A"
    _FieldOutput_type_RT = "RT"
    _NODE_TYPES = {_FieldOutput_type_U, _FieldOutput_type_A, _FieldOutput_type_RT}
    _ELEMENT_TYPES = {_FieldOutput_type_S}
    # 将"A"和"S"和"U"定义为类的常量，避免硬编码
    _VALID_FIELD_OUTPUT_TYPES = _NODE_TYPES.union(_ELEMENT_TYPES)

    def __init__(self, valid_node_types=None, valid_element_types=None):
        """
        初始化函数，用于设置有效的节点类型和元素类型

        :param valid_node_types: 可选参数，指定有效的节点类型序列
        :type valid_node_types: list or tuple
        :param valid_element_types: 可选参数，指定有效的元素类型序列
        :type valid_element_types: list or tuple
        """
        # 使用内部默认值，避免可变参数问题
        if valid_node_types is None:
            self._valid_node_types = copy.deepcopy(self._NODE_TYPES)
        else:
            # 检查传入的节点类型序列，确保其为字符串序列以保证类型安全
            check_sequence_type(valid_node_types, str)
            self._valid_node_types = set(valid_node_types)

        # 对元素类型执行类似的逻辑
        if valid_element_types is None:
            self._valid_element_types = copy.deepcopy(self._ELEMENT_TYPES)
        else:
            # 检查传入的元素类型序列，确保其为字符串序列以保证类型安全
            check_sequence_type(valid_element_types, str)
            self._valid_element_types = set(valid_element_types)
        self._update_valid_type = False
        self._all_valid_types = None

    @property
    def valid_node_types(self):
        """
        获取节点类型的属性。
        :return: 节点类型的属性。
        :rtype: set
        """
        return self._valid_node_types

    @property
    def valid_element_types(self):
        """
        获取元素类型的属性。
        :return: 元素类型的属性。
        :rtype: set
        """
        return self._valid_element_types

    @property
    def all_valid_types(self):
        """
        获取所有有效的类型集合。

        这个属性方法用于获取当前实例的所有有效类型集合，包括节点类型和元素类型。
        它通过懒加载模式来初始化和更新类型集合，以提高性能和减少不必要的计算。

        :return: 一个包含所有有效类型的集合（set）。
        :rtype: set
        """
        # 检查是否需要初始化或更新_valid_type
        if self._all_valid_types is None or self._update_valid_type:
            # 如果需要，将节点类型和元素类型的集合合并，并存储在_all_valid_types中
            self._all_valid_types = self._valid_node_types.union(self._valid_element_types)
            # 更新完成后，将_update_valid_type标志设置为False，直到下一次需要更新
            self._update_valid_type = False
        # 返回初始化或更新后的所有有效类型集合
        return self._all_valid_types

    def add_node_type(self, *types):
        """
        更新节点类型集合，添加新的节点类型。

        该方法允许通过传递多个节点类型参数来更新类的节点类型集合。它使用可变参数列表
        来接收多个节点类型，然后将这些类型添加到节点类型集合中，以便在后续的处理中可以
        识别和使用这些类型。

        :param types: 可变参数列表，表示要添加到节点类型集合中的新节点类型。
        :return: 该方法没有返回值。它仅更新类的节点类型集合。
        """
        check_sequence_type(types, str)
        self._valid_node_types.update(types)
        self._update_valid_type = True

    def add_element_type(self, *types):
        """
        更新单元类型集合，添加新的单元类型。

        该方法允许通过传递多个单元类型参数来更新类的单元类型集合。它使用可变参数列表
        来接收多个单元类型，然后将这些类型添加到单元类型集合中，以便在后续的处理中可以
        识别和使用这些类型。

        :param types: 可变参数列表，表示要添加到单元类型集合中的新单元类型。
        :return: 该方法没有返回值。它仅更新类的单元类型集合。
        """
        check_sequence_type(types, str)
        self._ELEMENT_TYPES.update(types)
        self._update_valid_type = True

    def _determine_field_output_type(self, field_output_type, field_output_types):
        """
        判断场输出数据类型是否在指定的类型列表中。

        参数:
        field_output_type (str): 需要判断的场输出数据类型。
        field_output_types (list): 指定的场输出数据类型列表。

        返回:
        bool: 如果场输出数据类型在指定的类型列表中，则返回True，否则返回False。
        """
        # 检查field_output_type是否为字符串类型
        check_type(field_output_type, str)
        # 判断场输出数据类型是否在类型列表中
        if field_output_type in field_output_types:
            return True
        return False

    def _verify_field_output_type(self, field_output_type, field_output_types):
        """
        验证场输出数据类型是否有效。

        参数:
        - field_output_type: 当前字段的输出类型。
        - field_output_types: 有效的场输出数据类型列表。

        如果field_output_type不在field_output_types中，则抛出ValueError。
        """
        if not self._determine_field_output_type(field_output_type, field_output_types):
            # 如果field_output_type无效，抛出ValueError异常
            raise ValueError(
                "Invalid field_output_type: '{}' . Valid types are: {}".format(
                    field_output_type, field_output_types))

    def verify_all_field_output_type(self, field_output_type):
        """
        验证所有字段的输出类型是否有效。

        该方法通过调用内部方法验证给定场输出数据类型的合法性，确保其属于预期的输出类型集合。

        参数:
        field_output_type: 待验证的场输出数据类型。

        返回值:
        无直接返回值，但会通过内部方法调用进行类型验证。
        """
        # 调用内部验证方法，确保场输出数据类型在预定义的有效类型集合中
        self._verify_field_output_type(field_output_type, self.all_valid_types)

    def determine_all_field_output_type(self, field_output_type):
        """
        判断所有字段的输出类型是否有效。

        此方法用于验证给定的场输出数据类型是否属于预定义的有效类型集合。如果属于，则返回True；
        否则返回False。该方法主要用于确保字段的输出类型是被系统所接受和预期的类型之一。

        参数:
        field_output_type: 待验证的场输出数据类型。

        返回值:
        bool: 如果场输出数据类型在有效类型集合中，则返回True，否则返回False。
        """
        # 调用内部方法_judge_field_output_type来执行实际的验证逻辑
        return self._determine_field_output_type(field_output_type, self.all_valid_types)

    def verify_node_field_output_type(self, field_output_type):
        """
        验证节点字段的输出类型是否符合预期。

        该方法主要用于检查节点字段的输出类型是否属于预定义的节点类型集合。
        它通过调用`_verify_field_output_type`方法来执行实际的类型验证。

        参数:
        - field_output_type: 节点字段的输出类型，作为字符串传递。

        返回值:
        该方法没有返回值，但会在类型验证失败时抛出异常。
        """
        # 调用内部方法进行节点场输出数据类型的验证
        self._verify_field_output_type(field_output_type, self.valid_node_types)

    def determine_node_field_output_type(self, field_output_type):
        """
        根据指定的场输出数据类型和节点类型确定节点字段的输出类型。

        参数:
        - field_output_type: 指定的场输出数据类型，用于决定最终的输出类型。

        返回值:
        - 返回确定后的场输出数据类型。
        """
        return self._determine_field_output_type(field_output_type, self.valid_node_types)

    def verify_element_field_output_type(self, field_output_type):
        """
        验证元素的场输出数据类型是否符合预期

        该方法通过检查传入的场输出数据类型是否存在于预定义的元素类型集合中，
        以确保字段的输出类型是正确的。

        参数:
        - field_output_type: 场输出数据类型，这是一个字符串，表示字段期望的输出类型

        返回值:
        无直接返回值，但会通过抛出异常或记录错误的方式来指示验证失败。
        """
        # 调用内部方法进行类型验证，这封装了类型检查逻辑，提高了代码的可维护性和可重用性
        self._verify_field_output_type(field_output_type, self.valid_element_types)

    def determine_element_field_output_type(self, field_output_type):
        """
        确定元素字段的输出类型。

        该方法用于根据提供的场输出数据类型和预定义的元素类型来确定元素字段的输出类型。

        参数:
        - field_output_type: 元素字段所需的输出类型。

        返回:
        - 确定的元素字段的输出类型。
        """
        # 调用私有方法 _determine_field_output_type，传入提供的场输出数据类型和类的 ELEMENT_TYPES 属性，以确定元素字段的输出类型。
        return self._determine_field_output_type(field_output_type, self.valid_element_types)

    def determine_node_type(self, field_output_type):
        """
        判断给定的场输出数据类型是否在当前实例的节点类型列表中。

        此方法用于检查一个类型是否被识别为节点类型，通过查看它是否存在于预定义的节点类型列表中。
        这对于确定数据结构中的节点如何处理和显示非常重要。

        参数:
        - field_output_type: 字段的输出类型，作为字符串提供。例如:'U', 'S'等。

        返回值:
        - 如果给定的场输出数据类型存在于节点类型列表中，则返回True，否则返回False。
        """
        return field_output_type in self.valid_node_types

    def __call__(self, *args, **kwargs):
        """
        使实例对象可被当作函数调用。

        通过定义__call__方法，使得当前类的实例对象可以接受任意参数并返回特定值。
        这里主要是为了提供一个接口来访问实例对象的verify_field_output_type属性或方法。

        参数:
        *args: 任意数量的位置参数。
        **kwargs: 任意数量的关键字参数。

        返回:
        verify_field_output_type: 实例对象的verify_field_output_type属性或方法。

        注释:
        本方法的主要目的是提供一个灵活的调用机制，允许外部以函数调用的方式，
        访问实例的特定属性或方法，这有助于增加代码的可用性和灵活性。
        """
        return self.verify_all_field_output_type(*args, **kwargs)


# class FieldOutputTypeConstantSingleton(FieldOutputTypeConstant):
#     __metaclass__ = Singleton2
#     """
#     单例版本的FieldOutputTypeConstant，确保只有一个实例存在。
#     """
#     pass


def determine_type(value, *expected_types):
    """
    检查给定值的类型是否符合预期类型之一。

    :param value: 待检查类型的值。
    :param expected_types: 一个或多个预期的类型，作为变长参数提供。
    :return: - 如果值的类型符合预期类型之一，则返回True。
    :rtype: bool
    """
    # 将非类型对象转换为其类型，以便进行类型比较
    expected_types = tuple([
        type(expected_type) if not isinstance(expected_type, type) else expected_type
        for expected_type in expected_types])

    # 检查value的类型是否在预期类型之中
    if not isinstance(value, expected_types):
        return False
    # 类型检查通过，返回True
    return True


# 检查类型
def check_type(value, *expected_types):
    """
    检查给定值的类型是否符合预期类型之一，或者是否是预期类型的子类。

    :param value: 待检查类型的值。
    :param expected_types: 一个或多个预期的类型，作为变长参数提供。
    :raises TypeError: 如果值的类型不符合预期类型。
    """
    # 处理expected_types为空的情况
    if not expected_types:
        raise ValueError("At least one expected type must be provided.")
    # 将非类型对象转换为其类型，以便进行类型比较
    expected_types = tuple(
        type(expected_type) if not isinstance(expected_type, type) else expected_type
        for expected_type in expected_types)
    # 检查value是否为类型对象
    if isinstance(value, type):
        if not issubclass(value, expected_types):
            expected_types_str = " or ".join([t.__name__ for t in expected_types])
            raise TypeError("Expected subclass of '{}', but got '{}'".format(expected_types_str, value.__name__))
    else:
        # 检查value的类型是否在预期类型之中
        if not isinstance(value, expected_types):
            expected_types_str = " or ".join([t.__name__ for t in expected_types])
            actual_type_str = type(value).__name__
            raise TypeError("Expected type '{}', but got '{}'".format(expected_types_str, actual_type_str))


# 检查序列中元素的类型是否一致。
def check_sequence_type(sequence, *element_type):
    """
    检查序列中元素的类型是否符合给定的类型要求。

    :param sequence: 待检查的序列，可以是列表或元组。
    :param element_type: 一个或多个序列元素应该具有的类型。
    :return: 如果所有元素都符合给定的类型要求，则返回 True；
            如果有元素不符合要求且 if_raise 设置为 False，则返回 False。
    :rtype: bool
    :raises TypeError: 如果值的类型不符合预期
    """
    # 检查序列是否为列表或元组
    check_type(sequence, list, tuple)
    # 检查列表中的每个元素是否为指定类型
    for index, element in enumerate(sequence):
        if not isinstance(element, element_type):
            expected_types_str = " or ".join([t.__name__ for t in element_type])
            raise TypeError(
                "List elements must be of type '{}', but found element of type '{}' at index '{}'".format(
                    expected_types_str, type(element), index))
    return True


# 将列表按照指定的切片大小分割成多个子列表
def split_list(lst, slice_size):
    """
    将列表按照指定的切片大小分割成多个子列表。

    此函数使用生成器表达式，按指定的切片大小遍历并分割输入列表。使用生成器的好处是节省内存，
    因为它只在需要时才生成下一个切片，而不是一次性将所有切片生成并存储在内存中。

    参数:
    lst (list): 要分割的列表。
    slice_size (int): 每个子列表的大小。

    返回:
    generator: 返回一个生成器，生成按指定大小分割的子列表。
    """
    return (lst[i:i + slice_size] for i in range(0, len(lst), slice_size))


# 按指定密度对列表进行均匀采样。
def sample_list(input_list, density=None):
    """
    按指定密度对列表进行均匀采样。

    :param input_list: 原始列表，包含待采样的元素。
    :type input_list: list
    :param density: 采样密度，一个介于0到1之间的浮点数，表示采样后的列表长度与原列表长度的比例。默认为1。
    :type density: float|None
    :return: 采样后的列表。
    """
    if density is None:
        density = 1
    if not 0 <= density <= 1:
        raise ValueError("density 必须在 0 到 1 之间")

    if density == 0:
        return []  # 如果密度为0，返回空列表

    if len(input_list) == 0:
        return []  # 如果输入列表为空，返回空列表
    if density == 1:
        return input_list
    # 计算采样间隔
    step = int(1.0 / density)

    sampled_list = input_list[::step]

    return sampled_list


# 格式化序列以简化其字符串表示形式
def omit_representation_sequence(input_sequence, delimiter="...", num_elements=3, start_bracket="[", end_bracket="]",
                                 separator=", "):
    """
    格式化序列以简化其字符串表示形式。

    如果序列的长度超过2 * num_elements + 1，那么仅显示前 num_elements 个元素和后 num_elements 个元素，
    中间用省略号表示。如果序列长度不超过2 * num_elements + 1，则直接返回序列的字符串表示。

    支持的序列类型包括列表、元组和字符串。

    :param delimiter: 省略号替换符，默认为"..."。
    :type delimiter: str
    :param input_sequence: 需要格式化的序列。
    :type input_sequence: list, tuple, str
    :param num_elements: 在省略号前后显示的元素数量，默认为3。
    :type num_elements: int
    :param start_bracket: 序列字符串表示的起始边界符号，默认为"["。
    :type start_bracket: str
    :param end_bracket: 序列字符串表示的结束边界符号，默认为"]"。
    :type end_bracket: str
    :param separator: 元素之间的分隔符，默认为", "。
    :type separator: str
    :return: 格式化后的序列字符串表示。
    :rtype: str
    """
    if len(input_sequence) > 2 * num_elements + 1:
        # 当序列长度大于2 * num_elements + 1时，采用省略格式输出
        start_elements = [str(input_sequence[i]) for i in range(num_elements)]
        end_elements = [str(input_sequence[-i - 1]) for i in range(num_elements)]
        return "{}{}{}{}".format(start_bracket, separator.join(start_elements), delimiter,
                                 separator.join(end_elements[::-1]) + end_bracket)
    else:
        # 当序列长度不超过2 * num_elements + 1时，直接返回序列的字符串表示
        return start_bracket + separator.join(map(str, input_sequence)) + end_bracket


# 省略表示字符串
def omit_representation_str(string, delimiter="__", num_elements=4):
    """
    省略表示字符串。

    该函数将给定的字符串按照指定的格式进行格式化。它主要用于长字符串的省略表示。
    通过调用omit_representation_sequence函数来实现具体的格式化逻辑，参数start_bracket和end_bracket以及separator的默认值为空字符串。

    :param string: 需要格省略表示的字符串。
    :type string: str
    :param delimiter: 用于表示省略的省略号，默认为双下划线"__"。
    :type delimiter: str
    :param num_elements: 省略表示的字符串省略号两端的字符数量，默认为4。
    :type num_elements: int
    :return: 省略表示的字符串。
    """
    return omit_representation_sequence(
        string, delimiter, num_elements, start_bracket="", end_bracket="", separator="")


# 深度遍历一个可迭代对象。
def iterate_deep(iterable):
    """
    深度遍历一个可迭代对象。

    该函数接受一个可迭代对象（如列表、元组等），并递归地遍历其中的每一个元素。
    对于不可迭代的元素，直接返回该元素；对于可迭代的元素，继续递归遍历其内部的元素。

    :param iterable: 需要深度遍历的可迭代对象
    :return: 生成器，逐个返回深度遍历的元素
    """

    # 遍历可迭代对象中的每一个元素
    for item in iterable:
        # 尝试将当前元素转为可迭代对象
        try:
            iter(item)
        except TypeError:
            # 如果当前元素不可迭代，则直接返回该元素
            yield item
        else:
            # 如果当前元素可迭代，则继续递归遍历
            for sub_item in iterate_deep(item):
                yield sub_item


def get_element_from_2d_list(matrix, index):
    """
    从二维列表中获取指定索引的元素，将二维列表视为一个大列表。
    支持子列表长度不一致的情况。

    :param matrix: 二维列表
    :param index: 要获取的元素在大列表中的索引
    :return: 对应索引的元素
    :raises IndexError: 如果索引超出范围
    """
    cumulative_length = 0
    for row in matrix:
        row_length = len(row)
        if index < cumulative_length + row_length:
            return row[index - cumulative_length]
        cumulative_length += row_length

    raise IndexError("Index out of range")


# 使用多线程执行任务。
def execute_tasks_in_multi_thread_process(worker_task, task_params, num_threads=None):
    """
    使用多线程执行任务。

    参数:
    - worker_task: 一个函数，代表要执行的任务。
    - task_params: 一个列表或迭代器，包含每个任务的参数。
    - num_threads: 可选参数，指定要使用的线程数。如果未提供，则根据CPU核心数自动设置。

    返回:
    - 一个列表，包含每个任务的结果。
    """
    # 确保num_threads参数是整数类型，或者为None（表示未指定）
    check_type(num_threads, int, None)
    # 如果未指定线程数，则根据CPU核心数自动设置
    if num_threads is None:
        # 获取CPU核心数
        num_cpus = multiprocessing.cpu_count()
        # 根据CPU核心数计算默认线程数，最多不超过32
        num_threads = min(32, (num_cpus or 1) + 4)  # 默认线程数
    # 创建线程池
    pool = ThreadPool(num_threads)
    # 使用线程池执行任务，并获取结果
    results = pool.map(worker_task, task_params)
    # 关闭线程池（不再接受新的任务）
    pool.close()
    # 等待所有线程完成
    pool.join()
    # 返回所有任务的结果
    return results


# 使用多线程处理列表数据。
def multi_thread_process(lst, process_slice, num_threads=None, chunk_size=None, min_chunk_size=None,
                         if_multi_thread=True):
    """
    使用多线程处理列表中的元素。

    参数:
    - lst: 要处理的列表。
    - process_slice: 处理列表切片的函数。
    - num_threads: 要使用的线程数，默认为None，此时将根据CPU核心数自动设置。
    - chunk_size: 列表切片的大小，默认为None，将根据列表长度和线程数自动计算。
    - min_chunk_size: 列表切片的最小大小，默认为None。
    - if_multi_thread: 是否使用多线程，默认为True。

    返回:
    - 处理结果的列表。
    """

    # 如果未指定线程数，则根据CPU核心数自动设置
    if num_threads is None:
        num_cpus = multiprocessing.cpu_count()
        num_threads = min(32, (num_cpus or 1) + 4)  # 默认线程数

    # 如果未指定切片大小，则根据列表长度和线程数自动计算
    if chunk_size is None:
        chunk_size = math.ceil(len(lst) / float(num_threads))  # Python 2 中除法需要显式转换为浮点数
    else:
        chunk_size = min(chunk_size, math.ceil(len(lst) / float(num_threads)))

    # 如果指定了最小切片大小，则确保切片大小不小于该值
    if min_chunk_size is not None:
        chunk_size = max(chunk_size, min_chunk_size)

    # 将列表分割成多个切片
    slices = split_list(lst, int(chunk_size))

    # 初始化结果列表
    # results = []

    # 如果使用多线程处理
    if if_multi_thread:
        # 使用 ThreadPool 替代 ThreadPoolExecutor
        pool = ThreadPool(num_threads)
        try:
            # map 方法会自动分配任务给线程池，并收集结果
            results = pool.map(process_slice, slices)
        except Exception as e:
            # 异常处理，打印错误信息并重新抛出异常
            print("An error occurred: {}".format(e))
            raise e
        finally:
            # 关闭线程池并等待所有线程完成
            pool.close()
            pool.join()

        # 返回处理结果
        return results
    else:
        # 如果不使用多线程，则在单线程中处理所有切片
        return [process_slice(s) for s in slices]


# 以下两个多进程函数没用，cae在执行多进程任务时直接卡住

# 多进程执行任务。
# 在 Python2 的 multiprocessing 模块中，不是所有的对象都可以被 pickle 序列化，这是用于在进程间传递数据的机制。
# 特别是，实例方法（即绑定到类实例的函数）通常不能被直接序列化，因为它们在底层实现上依赖于一些难以序列化的 Python 内部结构。
def execute_tasks_in_multi_process_use_pool(worker_task, task_params, processes=4):
    """
    进程池管理，使用多个进程执行任务。

    python2中，实例方法的多进程执行，不可用此方法，由于：
    在 Python2 的 multiprocessing 模块中，不是所有的对象都可以被 pickle 序列化，这是用于在进程间传递数据的机制。
    特别是，实例方法（即绑定到类实例的函数）通常不能被直接序列化，因为它们在底层实现上依赖于一些难以序列化的 Python 内部结构。

    参数:
    worker_task: 一个函数，表示需要执行的任务。
    task_params: 一个列表，包含每个任务的参数。
    processes: 一个整数，表示要使用的进程数量，默认为4。

    返回:
    一个列表，包含每个任务的执行结果。
    """
    # 确保processes参数是整数类型
    check_type(processes, int)
    # 获取系统CPU核心数量
    num_cpus = multiprocessing.cpu_count()
    # 如果指定的进程数大于CPU核心数量，则使用CPU核心数量作为进程数
    if processes > num_cpus:
        processes = num_cpus
    # 创建一个进程池，指定进程数量
    pool = multiprocessing.Pool(processes=processes)
    # 使用进程池执行任务，并获取结果
    results = pool.map(worker_task, task_params)
    # 关闭进程池（不再接受新的任务）
    pool.close()
    # 等待所有进程完成
    pool.join()
    return results


# 使用 multiprocessing.Process 可以更灵活地管理并行任务，需要传递不可序列化的对象（如实例方法或包含复杂状态的类实例）时。
# 每个 Process 对象都会创建一个新的 Python 解释器进程，并且你可以在这个新进程中运行任何可调用对象。
def execute_tasks_in_multi_process(worker_task, task_params, processes=4):
    """
    使用 multiprocessing.Process管理，使用多个进程执行任务。

    解决python2使用pool管理多进程任务时实例方法（即绑定到类实例的函数）通常不能被直接序列化的问题：
    使用 multiprocessing.Process 可以更灵活地管理并行任务，需要传递不可序列化的对象（如实例方法或包含复杂状态的类实例）时。
    每个 Process 对象都会创建一个新的 Python 解释器进程，并且你可以在这个新进程中运行任何可调用对象。

    参数:
    worker_task: 一个函数，表示需要执行的任务。
    task_params: 一个列表，包含每个任务的参数。
    processes: 一个整数，表示要使用的进程数量，默认为4。

    返回:
    一个列表，包含每个任务的执行结果。
    """
    # 创建一个队列用于进程间通信
    result_queue = multiprocessing.Queue()

    # 创建进程列表
    process_list = []

    # 分配任务到各个进程
    for i in range(processes):
        start = i * len(task_params) // processes
        end = (i + 1) * len(task_params) // processes
        params_chunk = task_params[start:end]
        process = multiprocessing.Process(target=_worker, args=(worker_task, params_chunk, result_queue))
        process_list.append(process)
        process.start()

    # 收集结果
    results = []
    for _ in range(len(task_params)):
        results.append(result_queue.get())

    # 等待所有进程完成
    for process in process_list:
        process.join()

    return results


def _worker(worker_task, params_chunk, result_queue):
    """
    工作进程的任务函数。

    参数:
    worker_task: 一个函数，表示需要执行的任务。
    params_chunk: 一个列表，包含当前进程需要处理的任务参数。
    result_queue: 一个队列，用于存储任务结果。
    """
    for param in params_chunk:
        result = worker_task(param)
        result_queue.put(result)


# 根据给定的段数，将列表的索引划分成几个区间。
def divide_list_indices(length, segments):
    """
    根据给定的段数，将列表的索引划分成几个区间。

    :param length: 列表的长度
    :param segments: 段数
    :return: 区间列表，每个区间是一个元组 (start, end)
    """
    # 计算每个区间的平均长度
    avg_length = length // segments
    # 多出来的元素数量
    remainder = length % segments

    intervals = []
    start = 0

    for i in range(segments):
        # 如果还有多出来的元素，当前区间的长度加1
        end = start + avg_length + (1 if i < remainder else 0)
        intervals.append((start, end))
        start = end

    return intervals


# 递归获取对象的嵌套属性，扩展getattr()。
def get_nested_attribute(obj, attr_string):
    """
    递归获取对象的嵌套属性值。

    本函数通过属性字符串（包含嵌套的属性名称），递归地获取对象的嵌套属性值。
    如果属性字符串为空，则直接返回对象本身。

    :param obj: 需要获取属性的对象。
    :param attr_string: 嵌套的属性名称字符串，使用点号分隔。
    :return: 返回最终获取的属性值，如果无法获取则抛出AttributeError。
    """
    if not attr_string:
        return obj
    # 分割属性名称
    parts = attr_string.split('.', 1)
    current_attr = parts[0]
    remaining_attr = parts[1] if len(parts) > 1 else None
    # 获取当前属性
    value = getattr(obj, current_attr)
    # 如果有剩余的属性，继续递归
    if remaining_attr:
        return get_nested_attribute(value, remaining_attr)
    else:
        return value


# 用于记录实例数量的基类
class InstanceCounterBase(object):
    """
    用于记录实例数量，并在实例数量为0时执行释放资源（比如释放一些类属性中的资源）操作的基类。
    """
    _instance_count = 0  # 类变量，用于记录实例数量

    def __init__(self):
        """初始化方法，增加实例计数"""
        self.__class__._instance_count += 1
        # print(f"Instance created, total instances: {self.__class__._instance_count}")

    def __del__(self):
        """析构方法，减少实例计数并检查是否需要释放资源"""
        self.__class__._instance_count -= 1
        # print(f"Instance deleted, total instances: {self.__class__._instance_count}")
        if self.__class__._instance_count == 0:
            self.release_resources()

    @classmethod
    def release_resources(cls):
        raise NotImplementedError("Subclasses must implement the release_resources method.")


def has_at_least_one_value(generator):
    """
    检查生成器是否至少产生一个值。

    此函数接收一个生成器作为输入，尝试获取其第一个值，以此判断生成器是否至少有一个值。
    如果生成器有值，返回 True 和一个包含第一个值及后续值的生成器。
    如果生成器没有值，返回 False 和一个空的生成器。

    :param generator: 需要检查的生成器。
    :type generator: Generator
    :return: 包含一个布尔值和一个生成器。布尔值指示生成器是否至少有一个值。
    :rtype: tuple[bool, Generator]
    """
    from itertools import chain, islice
    try:
        # 尝试获取生成器的第一个值
        first_value = next(generator)
        # 创建一个新的生成器，首先包含第一个值，然后是原始生成器的剩余值
        remaining_generator = chain([first_value], islice(generator, 1, None))
        return True, remaining_generator
    except StopIteration:
        # 如果生成器为空，则捕获 StopIteration 异常并返回一个空的生成器
        return False, iter([])


if __name__ == '__main__':
    pass
