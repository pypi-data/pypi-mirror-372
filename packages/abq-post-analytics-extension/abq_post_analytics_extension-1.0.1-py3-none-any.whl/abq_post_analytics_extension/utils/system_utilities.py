# -*- coding: UTF-8 -*-
import json
import os
from collections import OrderedDict

from ..default_config import default_config_dict
from .file_operations import ExtendedFile
from .logger_and_print import CommandLinePostExtensionProgressMonitor, PostExtensionProgressMonitor, \
    configurate_a_logger
from .misc_utils import check_type, Singleton


class AbqPostExtensionManager(Singleton):
    """
    AbqPostExtensionManager类是一个单例类，用于管理ABQ Post Extension库的配置、进度监控和日志等。
    """

    def _initialize(self, *args, **kwargs):
        super(AbqPostExtensionManager, self).__init__(*args, **kwargs)
        self._progress_monitor = None
        self._logger = None
        self._packaged_object_factory = None
        self._field_output_type_constant = None
        self._objects_to_be_closed = set()

    def get_config_manager(self, user_config_path=None):
        """
        获取配置管理器实例。

        该方法用于创建并返回一个配置管理器（ConfigManager）实例。通过接受一个可选的用户配置路径参数，
        将该路径设置到配置管理器中，以便配置管理器能够根据用户提供的配置路径进行初始化。

        :param user_config_path: 用户配置文件的路径。默认为None。
        :type user_config_path: str|None
        :return: 返回一个配置管理器实例，用于管理和访问配置信息（单例）。
        :rtype: ConfigManager
        """
        # 创建一个配置管理器实例
        config_manager = ConfigManager()
        # 设置用户配置路径
        config_manager.set_user_config_path(user_config_path)
        # 返回配置管理器实例
        return config_manager

    def get_packaged_object_factory(self, packaged_object_factory_type=None):
        """
        获取封装对象工厂实例。

        该方法是类方法，用于根据提供的封装对象工厂类型返回一个封装对象工厂实例。
        如果未提供封装对象工厂类型，则使用默认的PackagedObjectFactory。

        :param packaged_object_factory_type: 指定的封装对象工厂类型，必须是PackagedObjectFactory的子类(仅在第一次设置时有效)。
        :type packaged_object_factory_type: type|None
        :return: PackagedObjectFactory的实例（单例）。
        :rtype: PackagedObjectFactory
        """
        # 检查当前类是否已经有一个封装对象工厂实例
        if self._packaged_object_factory is None:
            # 从extended_odb_access模块导入PackagedObjectFactory类
            from ..core.access import PackagedObjectFactory
            # 如果没有指定封装对象工厂类型，则使用默认的PackagedObjectFactory
            if packaged_object_factory_type is None:
                packaged_object_factory_type = PackagedObjectFactory
            # 验证提供的封装对象工厂类型是否正确
            check_type(packaged_object_factory_type, PackagedObjectFactory)
            # 创建并保存封装对象工厂实例
            self._packaged_object_factory = packaged_object_factory_type()
        # 返回封装对象工厂实例
        return self._packaged_object_factory

    def get_progress_monitor(self, monitor_type=None):
        """
        获取进度监控器实例（单例，monitor_type类型一致时都获取同一个对象）。

        根据提供的监控器类型，返回该类型的进度监控器实例。如果未提供类型或类型为None，
        则使用默认的CommandLinePostExtensionProgressMonitor类型。

        :param monitor_type: 进度监控器的类型。必须是PostExtensionProgressMonitor的子类（仅首次设置时有效）。
        :type monitor_type: type|None
        :return: 进度监控器的实例（单例）。
        :rtype: CommandLinePostExtensionProgressMonitor|PostExtensionProgressMonitor
        """
        # 如果类中尚未创建进度监控器实例，则创建一个指定类型的实例
        if self._progress_monitor is None:
            # 如果未指定监控器类型，则使用默认的CommandLinePostExtensionProgressMonitor类型
            if monitor_type is None:
                monitor_type = CommandLinePostExtensionProgressMonitor
            # 如果指定了监控器类型，确保它确实是PostExtensionProgressMonitor的子类
            else:
                check_type(monitor_type, PostExtensionProgressMonitor)
            self._progress_monitor = monitor_type()
            # 如果当前进度监控器是CommandLinePostExtensionProgressMonitor类型的实例
            if isinstance(self._progress_monitor, CommandLinePostExtensionProgressMonitor):
                # 获取命令行进度监控器的配置
                monitor_config = self.get_config_manager().get_config("command_line_progress_monitor")
                # 设置进度监控器的进度更新间隔
                self._progress_monitor.set_progress_interval(monitor_config["progress_interval"])
                # 设置进度监控器的内容宽度
                self._progress_monitor.content_width = monitor_config["content_width"]
            self._progress_monitor.packaged_odb_object_factory = self.get_packaged_object_factory()
            self._progress_monitor.send_progress(self, message_type="init")
        # 返回进度监控器实例
        return self._progress_monitor

    @staticmethod
    def _default_configurate_a_logger(
            logger_name=None, logger_path=None, general_level=None, stream_level=None, file_level=None,
            logger_formatter=None):
        """
        使用默认参数配置一个日志记录器。

        此函数用于创建并配置一个日志记录器，包括日志的名称、路径、日志级别和格式等。
        如果未提供特定参数，函数将使用预定义的默认值。

        :param logger_name: 日志记录器的名称。如果未提供，默认为"abq_post_analytics_extension"。
        :param logger_path: 日志文件的路径。如果未提供，默认为当前目录下的"abq_post_analytics_extension.log"。
        :param general_level: 总体日志级别。如果未提供，默认为"debug"。
        :param stream_level: 控制台输出日志级别。如果未提供，默认为"warning"。
        :param file_level: 文件输出日志级别。如果未提供，默认为"info"。
        :param logger_formatter: 日志的格式。如果未提供，默认包含时间、名称、级别、文件名、行号和消息。
        :return: configurate_a_logger函数返回配置后的日志记录器。
        """
        # 设置默认日志记录器名称
        if logger_name is None:
            logger_name = "abq_post_analytics_extension"
        # 设置默认日志文件路径
        if logger_path is None:
            logger_path = os.path.join(os.getcwd(), "abq_post_analytics_extension.log")
        # 设置默认总体日志级别
        if general_level is None:
            general_level = "debug"
        # 设置默认控制台输出日志级别
        if stream_level is None:
            stream_level = "warning"
        # 设置默认文件输出日志级别
        if file_level is None:
            file_level = "info"
        # 设置默认日志格式
        if logger_formatter is None:
            logger_formatter = "%(asctime)s\t%(name)s\t%(levelname)s\t%(filename)s at line %(lineno)d\t%(message)s"
        # 调用configurate_a_logger函数进行实际配置并返回配置好的日志记录器
        return configurate_a_logger(
            logger_name, logger_path, general_level, stream_level, file_level, logger_formatter)

    def get_logger(self):
        """
        类方法，用于获取日志记录器实例。

        如果日志记录器尚未初始化，则根据配置文件进行初始化。
        该方法确保日志记录器在整个应用程序中是单例的，即只有一个实例会被创建和使用。
        :return: 初始化后的日志记录器实例（单例）。
        :rtype: logging.Logger
        """
        # 检查日志记录器是否已经初始化
        if self._logger is None:
            # 从配置管理器中获取日志配置
            logger_config = self.get_config_manager().get_config("logging")
            logger_name = logger_config["logger_name"]
            logger_path = logger_config["logger_path"]
            # 如果未配置日志路径，则使用当前工作目录和日志名称构建路径
            if logger_path is None:
                logger_path = os.path.join(os.getcwd(), logger_name + ".log")
            # 从配置中获取日志级别和格式化方式
            general_level = logger_config["general_level"]
            stream_level = logger_config["stream_level"]
            file_level = logger_config["file_level"]
            logger_formatter = logger_config["logger_formatter"]
            # 使用上述配置初始化日志记录器
            self._logger = self._default_configurate_a_logger(
                logger_name, logger_path, general_level, stream_level, file_level, logger_formatter)
        # 返回初始化后的日志记录器实例
        return self._logger

    def add_objects_to_be_closed(self, obj):
        """
        添加待关闭对象到类的集合中。

        该方法用于跟踪需要在会话结束或特定清理操作中关闭的对象。
        通过将对象添加到类级别的集合中，可以方便地在单一位置管理所有待关闭资源。

        :param obj: 待添加到待关闭集合中的对象。这通常是打开了文件、网络连接等需要显式关闭的资源对象。
        :return: 无返回值。
        """
        # 将给定的对象添加到待关闭对象的集合中
        self._objects_to_be_closed.add(obj)

    def close(self):
        """
        关闭所有需要关闭的对象，并通知进度监控器关闭。

        遍历所有需要关闭的对象，如果对象有close方法，则调用该方法。
        之后，发送关闭消息给进度监控器，并关闭进度监控器。
        """
        # 遍历所有需要关闭的对象
        for obj in self._objects_to_be_closed:
            # 检查对象是否有close方法
            if hasattr(obj, 'close'):
                # 关闭每个对象
                obj.close()
        # 通知进度监控器本模块已关闭
        self.get_progress_monitor().send_progress(self, message_type="close")
        # 关闭进度监控器
        self.get_progress_monitor().close()


class ConfigManager(Singleton):
    """
    配置管理器类，用于管理应用程序的配置信息。
    """
    _config = OrderedDict()  # 存储配置信息的字典
    _default_user_config_path = None
    _user_config_path = None

    @classmethod
    def _init_options(cls, instance):
        """
        初始化配置管理器的选项。

        :param instance: 当前实例对象。
        :return: 初始化选项后的实例对象。
        """
        cls._init_default_user_config_path()
        cls._config.update(default_config_dict)
        cls.load_config()

    @classmethod
    def _init_default_user_config_path(cls):
        """
        初始化默认用户配置路径。

        如果尚未设置默认用户配置路径，则将其设置为当前工作目录下的
        'abq_post_extension_config.json' 文件。

        :return: 无返回值。
        """
        if cls._default_user_config_path is None:
            # 将默认用户配置路径设置为当前工作目录下的指定文件
            cls._default_user_config_path = os.path.join(os.getcwd(), 'abq_post_extension_config.json')

    @classmethod
    def set_user_config_path(cls, user_config_path):
        """
        设置用户配置路径并加载配置。

        如果提供的用户配置路径为None，则使用默认的用户配置路径。
        如果提供了用户配置路径，则首先验证其类型是否为字符串。
        之后，将用户配置路径设置为类属性，并调用类的load_config方法来加载配置。

        :param user_config_path: 用户配置路径，如果为None，则使用默认路径。
        :type user_config_path: str|None
        :return: 无返回值。
        """
        if user_config_path is None:
            user_config_path = cls._default_user_config_path
        else:
            check_type(user_config_path, str)
        # 设置用户配置路径为类属性
        cls._user_config_path = user_config_path
        # 调用类的load_config方法，传入用户配置路径以加载配置
        cls.load_config(user_config_path)

    @classmethod
    def get_user_config_path(cls):
        """
        获取用户配置路径。

        如果类属性_user_config_path已设置，则返回该路径。
        否则，返回默认的配置路径。

        :return: 用户配置路径或默认配置路径。
        :rtype: str
        """
        # 检查是否已经设置了用户配置路径
        if cls._user_config_path is not None:
            return cls._user_config_path
        else:
            # 如果未设置用户配置路径，则返回默认配置路径
            return cls._default_user_config_path

    @classmethod
    def load_config(cls, config_path=None):
        """
        加载配置文件。

        如果没有提供配置文件路径，将使用用户配置路径。
        如果提供了配置文件路径，将检查其类型是否正确。

        :param config_path: 配置文件的路径，默认为None。
        :type config_path: str|None
        :return:
        """
        # 确定配置文件路径
        if config_path is None:
            config_path = cls.get_user_config_path()
        else:
            check_type(config_path, str)
        if os.path.exists(config_path):
            with ExtendedFile("r", file_path=config_path) as f:
                cls._config.update(f.read_and_load_json_str(object_pairs_hook=OrderedDict))
            cls._user_config_path = config_path

    @classmethod
    def get_config(cls, key, default=None):
        """
        获取配置值，如果不存在则返回默认值

        :param key: 配置项的键，可以是单个键或键的列表（用于嵌套字典）
        :type key: str or list
        :param default: 如果键不存在时返回的默认值，默认为None
        :type default: any
        :return: 配置项的值或默认值
        """
        if isinstance(key, str):
            key = [key]
        config = cls._config
        for k in key:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
        return config

    @classmethod
    def set_config(cls, key, value):
        """
        设置配置项

        该方法允许通过键值对的方式更新类的配置信息，支持多维字典的更新

        :param key: 配置项的键，可以是单个字符串或字符串列表（用于多维字典）
        :type key: str or list of str
        :param value: 配置项的值，用于更新或添加到配置中的值
        :type value: any
        """
        # 如果键是字符串，则转换为单元素列表
        if isinstance(key, str):
            key = [key]
        # 获取当前配置字典
        config = cls._config
        # 遍历键列表，逐层更新字典
        for k in key[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        # 设置最终键的值
        config[key[-1]] = value
        # 这里可以添加保存配置到文件的逻辑
        cls.save_config()

    @classmethod
    def save_config(cls, config_path=None):
        """
        保存配置到指定路径。

        如果未提供配置路径，则使用用户配置路径。如果提供的配置路径与默认配置路径不相同，
        则将当前配置保存到该路径，并更新用户配置路径。

        :param config_path: 配置文件的保存路径。
        :type config_path: str|None
        """
        # 如果未提供配置路径，则使用用户配置路径
        if config_path is None:
            config_path = cls.get_user_config_path()
        # 如果提供了配置路径，确保其为字符串类型
        else:
            check_type(config_path, str)
        # 如果配置路径与默认配置路径不相同，则将配置保存到该路径
        with ExtendedFile("w", file_path=config_path) as f:
            f.write_str(json.dumps(cls._config, indent=4, ensure_ascii=False, sort_keys=False))
        # 更新类的用户配置路径
        cls._user_config_path = config_path


class AbqPostExtensionBase(object):
    """
    AbqPostExtensionBase 是一个基类，用于管理 AbqPost 扩展。

    该类提供对 AbqPostExtensionManager 单例系统管理器的访问，从而可以方便地获取和管理其他单例资源，如配置、日志等。
    """

    @property
    def name(self):
        """
        获取实例的名称属性值。

        :return: 实例的名称。
        :rtype: str|None
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        设置实例的名称属性值。

        :param value: 要设置的名称值。如果提供的是None，则名称属性将被设置为None。
        :type value: str|None
        :return: None
        :raises TypeError: 如果提供的值不是字符串类型且不为None，则抛出类型错误。
        """
        # 验证输入值的类型，确保其为字符串或None
        check_type(value, str, None)
        if value is None:
            self._name = None
        else:
            self._name = str(value)

    def __init__(self, name=None):
        """
        初始化AbqPostExtensionBase实例。

        :param name: 实例的名称，默认为None。
        """
        super(AbqPostExtensionBase, self).__init__()
        check_type(name, str, None)
        self._name = None
        self.name = name

    @property
    def _abq_ext_manager(self):
        """
        属性函数，返回一个AbqPostExtensionManager实例。

        :return: 一个AbqPostExtensionManager实例，用于管理AbqPost的扩展。
        :rtype: AbqPostExtensionManager
        """
        return AbqPostExtensionManager()

    @property
    def _config_manager(self):
        """
        获取配置管理器

        :return: 配置管理器对象
        :rtype: ConfigManager
        """
        return self._abq_ext_manager.get_config_manager()

    @property
    def _progress_monitor(self):
        """
        获取进度监控器实例。

        :return: 一个进度监控器实例，用于监控任务进度。
        :rtype: PostExtensionProgressMonitor
        """
        # 调用扩展管理器的get_progress_monitor方法获取进度监控器实例
        return self._abq_ext_manager.get_progress_monitor()

    @property
    def _logger(self):
        """
        获取日志记录器实例。

        :return: 日志记录器实例，用于记录日志信息。
        :rtype: logging.Logger
        """
        return self._abq_ext_manager.get_logger()

    # @property
    # def _field_output_type_constant(self):
    #     """
    #     获取管理场输出类型的对象，提供验证输入的场输出类型是否有效，
    #     并判断其是单元类型还是节点类型的功能。
    #
    #     :return: 管理场输出类型的对象，用于验证输入的场输出类型是否有效，并判断其是单元类型还是节点类型。
    #     :rtype: FieldOutputTypeConstantSingleton
    #     """
    #     return self._abq_ext_manager.get_field_output_type_constant()


# 使用示例
if __name__ == "__main__":
    pass
