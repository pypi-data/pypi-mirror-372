# -*- coding: UTF-8 -*-
import threading
import time
from datetime import timedelta
import logging.handlers
import logging

try:
    from typing import Generator
except ImportError:
    pass

try:
    import queue
except ImportError:
    import Queue as queue
from .misc_utils import check_type, omit_representation_sequence


class CommandLineProgramInterface(object):
    """
    命令行程序界面
    """
    chinese_english_character_length_ratio = 29 / 18

    @staticmethod
    def format_time(seconds, show_milliseconds=True):
        """
        将给定的秒数格式化为一个易读的字符串，包括年、天、小时、分钟和秒（可选地包括毫秒）。

        :param seconds: 要格式化的总秒数。可以是整数或小数。
        :type seconds: float|int
        :param show_milliseconds: 是否在输出中包含毫秒部分。默认为True。
        :type show_milliseconds: bool
        :return: 格式化后的时间字符串。
        :rtype: str
        """
        parts = []
        if seconds < 0.001:
            parts.append("{:.2e} s".format(seconds))
        else:
            # 将秒数转换为 timedelta 对象
            delta = timedelta(seconds=seconds)

            # 计算年、天、小时、分钟和秒数
            years = delta.days // 365
            days = delta.days % 365
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            seconds_part = delta.seconds % 60
            milliseconds = int(delta.microseconds / 1000)
            # 构建格式化字符串
            if years > 0:
                parts.append("{0} yr".format(years))
            if days > 0:
                parts.append("{0} d".format(days))
            if hours > 0:
                parts.append("{0} hr".format(hours))
            if minutes > 0:
                parts.append("{0} min".format(minutes))
            # 处理秒部分
            if show_milliseconds:
                total_seconds = seconds_part + float(milliseconds) / 1000
                parts.append("{:.3f} s".format(total_seconds))
            else:
                if seconds_part > 0:  # 如果没有其他部分，则至少显示秒
                    parts.append("{0} s".format(seconds_part))
        format_str = ' '.join(parts)
        return format_str

    def time_line(self, seconds, content=None, show_milliseconds=True):
        """
        格式化时间并生成时间表格行。

        该方法用于将给定的秒数格式化为人类可读的时间字符串，并与给定的内容字符串一起生成时间表格行。

        :param seconds: 需要格式化的秒数。
        :type seconds: float|int
        :param content: 在时间前面的内容，默认为"Time taken: "。
        :type content: str
        :param show_milliseconds: 是否在时间字符串中显示毫秒部分。
        :type show_milliseconds: bool
        :return: 格式化后的时间表格行字符串。
        :rtype: str
        """
        # 检查seconds参数是否为float或int类型
        check_type(seconds, float, int)
        # 如果content参数未提供，则使用默认值"Time taken: "
        if content is None:
            content = "Time taken: "
        else:
            # 检查content参数是否为str类型
            check_type(content, str)
        # 检查show_milliseconds参数是否为bool类型
        check_type(show_milliseconds, bool)
        # 格式化时间，根据show_milliseconds参数决定是否显示毫秒
        time_str = self.format_time(seconds, show_milliseconds)
        # 将内容字符串与格式化后的时间字符串拼接，并生成时间表格行
        return self.get_table_line_by_str(content + time_str, 1)

    @staticmethod
    def truncate_string(s, length):
        """
        将字符串按指定长度截断成多行。

        :param s: 待处理的字符串
        :type s: str
        :param length: 每行的最大长度
        :type length: int
        :return: 一个列表，包含截断后的字符串的每一行，字符串中换行符表示的多余的空行用一个空字符串表示。
        :rtype: list[str]
        """
        check_type(s, str)
        check_type(length, int)
        # 初始化存储截断后字符串的列表
        lines = []
        # 初始化当前行的字符串
        current_line = ""

        # 遍历字符串中的每个字符
        for char in s:
            # 如果遇到换行符，将当前行添加到结果列表中，并重置当前行
            if char == "\n":
                lines.append(current_line)
                current_line = ""
            # 如果当前行长度未达到最大长度，将字符添加到当前行
            elif len(current_line) < length:
                current_line += char
            # 如果当前行达到最大长度，将当前行添加到结果列表中，并用当前字符作为下一行的开始
            else:
                lines.append(current_line)
                current_line = char

        # 如果最后一行不为空，将其添加到结果列表中
        if current_line:
            lines.append(current_line)

        # 返回截断后的字符串列表
        return lines

    def __init__(self, content_width=118):
        """
        创建一个命令行程序界面对象。
        :param content_width: 界面内容宽度，默认为118。
        :type content_width: int
        """
        super(CommandLineProgramInterface, self).__init__()
        self._content_width = content_width
        self._automatic_line_break_length_ratio = 1

    @property
    def content_width(self):
        """
        获取内容宽度

        该属性用于获取当前对象的内容宽度，以适应特定的显示需求或计算布局

        :return: 返回内容的宽度，存储在私有变量_content_width中
        :rtype: int
        """
        return self._content_width

    @content_width.setter
    def content_width(self, value):
        """
        设置content_width的值。

        :param value: 要设置的content_width的值，应为非负整数。
        :type value: int
        :return: None
        :raises ValueError: 如果value小于0，则抛出ValueError。
        """
        # 检查value是否为整数类型
        if value:
            check_type(value, int)
            # 确保content_width的值大于等于0
            if value < 0:
                raise ValueError("content_width must be greater than or equal to 0.")
            self._content_width = value

    @property
    def automatic_line_break_length_ratio(self):
        """
        对于长字符串，在设定长度的表格中显示时的自动换行长度相对于表格长度的比例，默认为1

        :return: 换行的长度比例
        :rtype: float
        """
        return self._automatic_line_break_length_ratio

    @automatic_line_break_length_ratio.setter
    def automatic_line_break_length_ratio(self, value):
        """
        设置自动换行的长度比例。

        对于长字符串，在设定长度的表格中显示时的自动换行长度相对于表格长度的比例，默认为1

        :param value: 换行的长度比例
        :type value: float
        :return: 无
        :rtype: None
        :raises ValueError: 如果value小于0或大于1，则抛出ValueError。
        """
        check_type(value, float)
        if value < 0 or value > 1:
            raise ValueError("automatic_line_break_length_ratio must be between 0 and 1.")
        self._automatic_line_break_length_ratio = value

    @property
    def _automatic_line_break_length(self):
        """
        获取自动换行的长度。

        :return: 自动换行的长度。
        :rtype: int
        """
        return int(round(self.content_width * self.automatic_line_break_length_ratio))

    def get_table_line_by_str(self, string, justification=0, segment_length=None):
        """
        根据给定的字符串生成一个表格格式的字符串。

        提供对齐与识别换行符添加空行的功能
        :param string: 需要格式化成表格的字符串。
        :type string: str
        :param justification: 文本对齐方式。0表示左对齐，1表示右对齐，其他值表示居中对齐。
        :type justification: int
        :param segment_length: 每一行的最大长度。默认为设定的content_width的四分之三
        :type segment_length: int|None
        :return: 生成的表格格式字符串。
        :rtype: str
        """
        # 检查输入参数类型
        check_type(string, str)
        check_type(justification, int)

        # 根据内容宽度计算默认的段长，如果未提供段长
        if segment_length is None:
            segment_length = self._automatic_line_break_length
        else:
            check_type(segment_length, int)
            # 确保段长不超过内容宽度
            if segment_length > self.content_width:
                segment_length = self.content_width

        table_str = ""
        # 将字符串截断为指定长度的段落
        segments = self.truncate_string(string, segment_length)

        # 遍历每个段落并根据对齐方式格式化
        for segment in segments:
            if segment == "":
                table_str += self.blank_line
            else:
                # 根据不同的对齐方式格式化段落
                if justification == 0:
                    table_str += "|{:<{}}|\n".format(segment, self.content_width)
                elif justification == 1:
                    table_str += "|{:>{}}|\n".format(segment, self.content_width)
                else:
                    table_str += "|{:^{}}|\n".format(segment, self.content_width)

        return table_str

    @property
    def frame_line(self):
        """
        获取表格的边框行。

        :return: 表格边框行。
        """
        return '+{}+\n'.format('-' * self.content_width)

    @property
    def separate_line(self):
        """
        获取表格的分隔行。

        :return: 表格分隔行。
        """
        return '|{}|\n'.format('-' * self.content_width)

    @property
    def blank_line(self):
        """
        获取一个空行。

        :return: 一个空行。
        """
        return '|{}|\n'.format(' ' * self.content_width)

    def progress_bar_table_line(self, progress, content="", bar_length=40):
        """
        生成一个表示进度的表格行。

        :param progress: 进度值，必须在0到1之间。
        :type progress: float
        :param bar_length: 进度条的长度，默认为40。
        :type bar_length: int
        :param content: 表格行的内容，默认为空字符串。
        :type content: str
        :return: 表示进度条和内容的表格行。
        :rtype: str
        """
        # 检查progress参数是否为float类型
        check_type(progress, float, int)
        # 检查progress值是否在0到1之间
        if not 0 <= progress <= 1:
            raise ValueError("progress must be between 0 and 1.")
        # 检查bar_length参数是否为int类型
        check_type(bar_length, int)
        # 检查bar_length值是否大于等于0
        if bar_length < 0:
            raise ValueError("bar_length must be greater than or equal to 0.")
        # 检查content参数是否为str类型
        check_type(content, str)
        # 将进度转换为百分比并四舍五入为整数
        progress_num = int(round(bar_length * progress))
        # 生成进度条字符串
        progress_bar_str = "Progress:" + ">" * progress_num + "{:>3}%".format(int(progress * 100))
        # 通过格式化字符串将进度条和内容组合成一个表格行，并返回
        return self.get_table_line_by_str("{:<53}{}".format(progress_bar_str, content))


class PostExtensionCommandLineProgramInterface(CommandLineProgramInterface):
    """
    命令行界面程序接口类
    """
    def __init__(self, content_width=118):
        """
        初始化命令行界面程序接口类

        :param content_width: 输出内容的宽度，默认为118
        """
        super(PostExtensionCommandLineProgramInterface, self).__init__(content_width)
        self._post_extension_system_name = "Abq-Post-Analytics-Extension System"
        self._post_extension_version = "1.0.0"
        self._title_content = \
            "\n\nThis system provides enhanced post-processing capabilities for Abaqus simulations.\n" \
            "For more information and usage instructions, please refer to the documentation.\n" \
            "To obtain available commands, please use the link to access the help documentation: currently unavailable"

    def system_name_line(self):
        """
        生成并返回系统名称和版本的格式化字符串

        :return: 格式化后的系统名称和版本号的表格行
        :rtype: str
        """
        # 格式化系统名称和版本号为"系统名称 v版本号"的形式
        line = "{} v{}".format(self._post_extension_system_name, self._post_extension_version)
        # 调用方法将格式化后的字符串转换为表格中的特定行格式
        return self.get_table_line_by_str(line, 2)

    def class_name_line(self, obj):
        """
        根据执行的对象生成包含类名的行。

        :param obj: 执行的对象。这个对象可以是任何类的实例，方法会获取这个类的名称。
        :return: 返回一个表格行，包含格式化后的类名字符串。
        :rtype: str
        """
        # 格式化类名字符串
        line = "Class name of the executed object:'{}'\n".format(obj.__class__.__name__)
        if hasattr(obj, "name"):
            if obj.name is not None:
                line += "Object name:'{}'".format(obj.name)
        # 调用方法将格式化后的字符串转换成表格行
        return self.get_table_line_by_str(line)

    def system_table_lines(self, content, with_bottom_border=True):
        """
        根据给定内容生成系统表线。

        该方法用于构建一个系统表的文本表示，其中包括顶部和底部边框、系统名称以及给定的内容。

        :param content: 要添加到系统表中的内容。
        :type content: str
        :param with_bottom_border: 是否在表的底部添加边框，默认为 True。
        :type with_bottom_border: bool
        :return: 构建的系统表的文本表示。
        :rtype: str
        """
        # 初始化系统表的行，开始时添加框架线
        lines = self.frame_line
        # 添加系统名称行
        lines += self.system_name_line()
        # 添加分隔线
        lines += self.separate_line
        # 添加传入的内容
        lines += content
        # 根据参数决定是否添加底部边框
        if with_bottom_border:
            lines += self.frame_line
        return lines

    def class_table_lines(self, obj, content, with_bottom_border=True):
        """
        生成类表的字符串表示。

        该方法通过连接各种组件来构建类表的字符串表示，包括框架行、系统名称行、分隔行、类名称行和附加内容。
        主要负责类表字符串表示的布局和组织。

        :param obj: 类对象，用于提取类名和其他信息。
        :type obj: object
        :param content: 附加表格行内容字符串。
        :type content: str
        :param with_bottom_border: 是否在底部添加边框，默认为 True。
        :type with_bottom_border: bool
        :return: 包含类表所有行的字符串。
        :rtype: str
        """
        class_content = self.class_name_line(obj) + content
        return self.system_table_lines(class_content, with_bottom_border)

    def title_table_lines(self):
        """
        生成标题表格的线条字符串。

        本函数负责组装一个包含系统欢迎信息和提示的字符串，该字符串用于在输出中形成一个标题表格。
        它通过格式化系统名称和版本号来创建一个欢迎标题，并结合系统功能介绍和文档访问提示，
        生成一个具有边框和分隔符的表格形式的字符串。

        :return: 包含标题表格的字符串。
        :rtype: str
        """
        # 生成系统欢迎标题，包含系统名称和版本号
        title = "Welcome to the {} v{}".format(self._post_extension_system_name, self._post_extension_version)
        # 定义系统功能介绍和文档访问提示内容
        content = self._title_content
        title_str = self.frame_line
        title_str += self.get_table_line_by_str(title, 2)
        title_str += self.separate_line
        title_str += self.get_table_line_by_str(content)
        title_str += self.frame_line
        return title_str

    def end_table_lines(self):
        """
        生成表格的结束部分表格行。

        本函数通过组合表格线条和特定的感谢信息表格行，创建并返回代表表格结束部分的字符串。
        这里没有参数，因为感谢信息是固定的，不需要外部输入。

        :return: 代表表格结束部分的字符串，包括框架线条和感谢信息表格行。
        :rtype: str
        """
        # 初始化结束表格的线条为框架线条
        end_table_lines = self.frame_line
        # 增加包含感谢信息的线条，"Thanks for using this application!"
        end_table_lines += self.get_table_line_by_str(
            "Thanks for using the {} v{}".format(self._post_extension_system_name, self._post_extension_version), 2)
        # 在感谢信息后再次增加框架线条，标志着表格的正式结束
        end_table_lines += self.frame_line
        # 返回组合完成的表格结束部分线条
        return end_table_lines


class PostExtensionProgressMonitor(object):
    """
    进度监控器类，用于处理进度信息。
    """
    def __init__(self, *argus, **kwargs):
        """
        初始化进度监控器。

        :param argus: 构造函数的参数。
        :param kwargs: 构造函数的参数。
        """
        super(PostExtensionProgressMonitor, self).__init__()
        self._packaged_odb_object_factory = None
        self._last_post_ext_object = None
        self.progress_queue = queue.Queue(maxsize=100)
        self.progress_thread = threading.Thread(target=self.on_process_post_extension_objects)
        self.progress_thread.daemon = True  # 设置为守护线程，在主线程退出时自动终止
        self.progress_thread.start()
        # 以下，添加对程序退出时的处理，包括线程的终止和清理工作，在abaqus中执行时，线程信息均未正确打印出
        # atexit.register(self.stop_thread)  # atexit 模块，在程序退出时自动调用该函数，用于等待线程完成。
        # signal.signal(signal.SIGINT, self.stop_thread) # signal 模块，用于处理操作系统信号，这里用于处理Ctrl+C和kill命令
        # signal.signal(signal.SIGTERM, self.stop_thread) # 处理kill信号

    def close(self):
        """
        停止进度线程。

        本函数通过向进度队列中放入None来通知线程停止运行，并使用join方法等待线程安全停止。

        :return: 无
        """
        # print("###Stop thread###$")
        # 向进度队列中放入None，作为停止信号。
        self.progress_queue.put(None)
        # 调用join方法等待进度线程安全地停止。
        self.progress_thread.join()

    @property
    def packaged_odb_object_factory(self):
        """
        获取或设置用于创建包装对象的工厂实例。

        :return: 包装对象工厂实例
        :rtype: PackagedObjectFactory
        """
        if self._packaged_odb_object_factory is None:
            raise RuntimeError("The packaged_odb_object_factory has not been set.")
        return self._packaged_odb_object_factory

    @packaged_odb_object_factory.setter
    def packaged_odb_object_factory(self, packaged_odb_object_factory):
        """
        设置用于创建包装对象的工厂实例。

        :param packaged_odb_object_factory: 包装对象工厂实例
        :type packaged_odb_object_factory: PackagedObjectFactory
        :return: 无
        """
        self._packaged_odb_object_factory = packaged_odb_object_factory

    def send_progress(self, obj, *argus, **kwargs):
        """
        发送进度信息到进度队列。

        当进度队列满时，移除最旧的进度信息，然后将新的进度信息添加到队列中，
        以使打印进度的线程不阻塞主线程。

        :param obj: 发送进度信息的对象。
        :type obj: object
        :param argus: 可变位置参数，用于传递额外的进度信息。
        :param kwargs: 可变关键字参数，用于传递额外的进度信息。
        :return: 无返回值。
        """
        # 检查进度队列是否已满
        if self.progress_queue.full():
            # 队列已满，先从队列中移除一项旧的进度信息
            self.progress_queue.get()

        # 构造新的进度信息列表，包含对象、参数和关键字参数
        progress_information = [obj, argus, kwargs]

        # 将新的进度信息添加到队列中
        self.progress_queue.put(progress_information)

    def on_progress(self):
        """
        一个生成器函数，用于逐步获取进度信息。

        该函数会不断地从进度队列中获取信息，直到接收到None信号为止。
        None信号指示进度信息已经全部被处理完毕。

        每次从队列中获取到的进度信息都会被yield，以便调用者可以逐步处理这些信息。

        :return: 生成器对象，用于逐步获取进度信息
        :rtype: Generator[list]
        """
        while True:
            # 从进度队列中获取进度信息
            progress_information = self.progress_queue.get()
            # print("on_progress get information:'{}'".format(progress_information))
            # 如果获取到的是None，则表示所有进度信息已经处理完毕，退出循环
            if progress_information is None:
                break
            # 将获取到的进度信息yield给调用者处理
            yield progress_information

    def on_process_post_extension_objects(self):
        """
        处理来自进度队列的PostExtension对象信息

        功能：
        - 从进度队列中获取进度信息
        - 根据对象类型分发到对应的监控方法进行处理
        - 记录最后处理的对象

        流程：
        1. 延迟导入必要的类，避免循环引用
        2. 遍历进度队列中的每个进度信息
        3. 解包进度信息，获取对象、参数和关键字参数
        4. 根据对象类型调用对应的监控方法
        5. 记录最后处理的对象

        :return:  无
        """
        # 延迟导入，防止循环引用
        from abq_post_analytics_extension.core.analysis.base import PackagedMeshObjectsSelectorBase
        from .system_utilities import AbqPostExtensionManager
        for progress_information in self.on_progress():
            # print("class '{}' get information:'{}'".format(self.__class__.__name__, progress_information))
            post_ext_object, argus, keywords = progress_information
            if isinstance(post_ext_object, AbqPostExtensionManager):
                self.abq_post_extension_progress_monitor(post_ext_object, *argus, **keywords)
            elif isinstance(post_ext_object, self.packaged_odb_object_factory.packaged_odb_class):
                self.packaged_odb_progress_monitor(post_ext_object, *argus, **keywords)
            elif isinstance(post_ext_object, self.packaged_odb_object_factory.packaged_step_class):
                self.packaged_step_progress_monitor(post_ext_object, *argus, **keywords)
            elif isinstance(post_ext_object, self.packaged_odb_object_factory.packaged_frame_manager_class):
                self.packaged_frame_manager_progress_monitor(post_ext_object, *argus, **keywords)
            elif isinstance(post_ext_object, PackagedMeshObjectsSelectorBase):
                self.packaged_mesh_objects_handler_progress_monitor(post_ext_object, *argus, **keywords)
            else:
                self.other_information_monitor(post_ext_object, *argus, **keywords)
            self._last_post_ext_object = post_ext_object

    def other_information_monitor(self, obj, *argus, **kwargs):
        """
        处理传递的任意对象信息

        :param obj: 传递的PackagedOdb对象的信息
        :return:  无
        :raises NotImplementedError: 如果子类没有实现此方法
        """
        raise NotImplementedError

    def abq_post_extension_progress_monitor(self, obj, *argus, **kwargs):
        """
        处理传递的AbqPostExtensionManager对象信息

        :param obj: 传递的PackagedOdb对象的信息
        :return:  无
        :raises NotImplementedError: 如果子类没有实现此方法
        """
        raise NotImplemented

    def packaged_odb_progress_monitor(self, obj, *argus, **kwargs):
        """
        处理传递的PackagedOdb对象的信息

        此方法目前未实现任何操作，其目的是作为一个可被子类或特定实现覆盖的模板方法。

        :param obj: 传递的PackagedOdb对象的信息
        :raises NotImplementedError: 如果子类没有实现此方法
        """
        raise NotImplementedError

    def packaged_step_progress_monitor(self, obj, *argus, **kwargs):
        """
        处理传递的PackagedStep对象的信息

        此方法目前未实现任何操作，其目的是作为一个可被子类或特定实现覆盖的模板方法。

        :param obj: 传递的PackagedStep对象的信息
        :raises NotImplementedError: 如果子类没有实现此方法
        """
        raise NotImplementedError

    def packaged_frame_manager_progress_monitor(self, post_ext_object, *argus, **keywords):
        raise NotImplementedError

    def packaged_mesh_objects_handler_progress_monitor(self, obj, *argus, **kwargs):
        """
        处理传递的PackagedMeshObjectsSelectorBase对象的信息

        此方法目前未实现任何操作，其目的是作为一个可被子类或特定实现覆盖的模板方法。

        :param obj: 传递的PackagedMeshObjectsSelectorBase对象
        :raises NotImplementedError: 如果子类没有实现此方法
        """
        raise NotImplementedError


class CommandLinePostExtensionProgressMonitor(PostExtensionProgressMonitor, PostExtensionCommandLineProgramInterface):
    """
    命令行进度监控器
    """
    @staticmethod
    def _round_down_to_nearest_step(value, step=0.1):
        """
        将给定的值向下取整到最接近的 step 的倍数。

        :param value: 要取整的值。
        :type value: float
        :param step: 取整的步长。默认为 0.1。
        :type step: float
        :return: 向下取整到最接近的 step 的倍数的值。
        :rtype: float
        """
        return int(value / step) * step

    def __init__(self, content_width=118, *argus, **kwargs):
        """
        创建命令行进度监控器的实例。

        :param content_width: 命令行进度条的宽度，默认为118个字符。
        :type content_width: int
        :param argus: 父类PostExtensionProgressMonitor的参数。
        :param kwargs: 父类PostExtensionProgressMonitor的参数。
        """
        super(CommandLinePostExtensionProgressMonitor, self).__init__(content_width=content_width, *argus, **kwargs)
        self._odb_init_time = time.time()
        self._progress_interval = 0.1

    def set_progress_interval(self, value):
        """
        设置百分百进度条更新的百分比间距，0.01表示每百分之一更新一次，0.1表示每百分之十更新一次。

        :param value: float类型，表示进度条更新的百分比间距，必须大于0且小于1
        :type value: float
        :return: 无返回值
        """
        if value:
            # 检查value参数是否为float类型
            check_type(value, float)
            # 如果value的值不在(0, 1)范围内，则抛出ValueError异常
            if value <= 0 or value >= 1:
                raise ValueError("The value must be greater than 0 and less than 1.")
            # 设置进度条更新的百分比间距
            self._progress_interval = value

    def other_information_monitor(self, obj, *argus, **kwargs):
        """
        收集并打印对象的其他信息，包括额外的位置参数和关键字参数。

        :param obj: 主要对象信息。
        :type obj: object
        :param argus: 可变数量的位置参数。
        :type argus: tuple
        :param kwargs: 可变数量的关键字参数。
        :type kwargs: dict
        :return: 无返回值。
        :rtype: None
        """
        # 将主要对象信息格式化为字符串，并初始化内容变量
        content = "{}\n".format(obj)
        # 遍历位置参数并将其添加到内容中
        for argue in argus:
            content += "{}\n".format(argue)
        # 遍历关键字参数并将其键值对格式化后添加到内容中
        for keyword, value in kwargs.items():
            content += "{}: {}\n".format(keyword, value)
        # 调用方法将内容转换为表格行
        table_lines = self.get_table_line_by_str(content)
        # 打印系统表格行
        print(self.system_table_lines(table_lines)[:-1])

    def abq_post_extension_progress_monitor(self, abq_post_extension, message_type=None, *argus, **kwargs):
        """
        处理 Abaqus 后处理扩展系统的进度监控信息

        根据消息类型（message_type）执行不同的操作：
        1. 当收到 'init' 消息时，打印系统欢迎标题表格
        2. 当收到 'close' 消息时，打印系统结束表格

        :param abq_post_extension: Abaqus 后处理扩展系统对象
        :type abq_post_extension: AbaqusPostExtension
        :param message_type: 消息类型，可选 'init' 或 'close'
        :type message_type: str
        :return: 无返回值
        """
        if message_type == 'init':
            print(self.title_table_lines()[:-1])
        elif message_type == 'close':
            print(self.end_table_lines()[:-1])

    def _packaged_odb_init_table_lines(self, packaged_odb):
        """
        生成包装ODB对象初始化时的表格行信息

        该方法创建并返回一个格式化的字符串，用于显示Abaqus输出数据库(ODB)的加载信息，
        包括ODB名称和文件路径，并以表格形式呈现。

        :param packaged_odb: 已包装的ODB对象，包含ODB相关信息
        :type packaged_odb: PackagedOdbObject
        :return: 格式化后的表格行字符串，包含ODB加载信息
        :rtype: str
        """
        process_str = "\n\nThe abaqus output database named '{}' has been loaded.\nWith address: '{}'".format(
            packaged_odb.odb_name, packaged_odb.odb_path)
        process_lines = self.get_table_line_by_str(process_str)
        return self.class_table_lines(packaged_odb, process_lines)

    def _packaged_odb_end_table_lines(self, packaged_odb, seconds):
        """
        生成包装ODB对象处理完成时的结束表格行信息

        该方法创建并返回一个格式化的字符串，用于显示Abaqus输出数据库(ODB)处理完成的总结信息，
        包括ODB名称和总耗时，并以表格形式呈现。

        :param packaged_odb: 已处理的包装ODB对象，包含ODB相关信息
        :type packaged_odb: PackagedOdbObject
        :param seconds: 处理ODB所花费的总时间(秒)
        :type seconds: float
        :return: 格式化后的表格行字符串，包含处理完成信息和耗时
        :rtype: str
        """
        process_str = "\nProcessing of abaqus output database: '{}' has been completed\n\n".format(
            packaged_odb.odb_name)
        process_lines = self.get_table_line_by_str(process_str)
        process_lines += self.time_line(seconds, content="Total time taken: ")
        return self.class_table_lines(packaged_odb, process_lines)


    def packaged_odb_progress_monitor(self, packaged_odb, message_type=None, *argus, **kwargs):
        """
        ODB处理进度监控器

        根据不同的消息类型执行ODB处理过程的初始化和结束操作，并打印相应的进度信息表格。

        :param packaged_odb: 包装后的ODB对象，包含待处理的ODB数据
        :type packaged_odb: PackagedOdbObject
        :param message_type: 消息类型，标识是初始化('init')还是结束('end')消息
        :type message_type: str
        :param argus: 可变位置参数，用于传递额外的进度信息
        :param kwargs: 可变关键字参数，用于传递额外的进度信息

        功能说明:
        - 当message_type为'init'时:
          1. 记录当前时间作为处理开始时间
          2. 调用[_packaged_odb_init_table_lines]方法生成初始化信息表格并打印

        - 当message_type为'end'时:
          1. 计算从初始化到当前的总耗时
          2. 调用[_packaged_odb_end_table_lines]方法生成结束信息表格并打印
        """
        if message_type == 'init':
            self._odb_init_time = time.time()
            print(self._packaged_odb_init_table_lines(packaged_odb)[:-1])
        elif message_type == 'end':
            print(self._packaged_odb_end_table_lines(packaged_odb, time.time() - self._odb_init_time)[:-1])

    def packaged_step_table_lines(self, packaged_step):
        """
        生成包装步骤(Step)对象的表格行信息

        该方法创建并返回一个格式化的字符串，用于显示Abaqus分析步骤(Step)的加载信息，
        包括步骤名称和支持的场输出类型(节点和单元)，并以表格形式呈现。

        :param packaged_step: 包装后的步骤对象，包含步骤相关信息
        :type packaged_step: PackagedStepObject
        :return: 格式化后的表格行字符串，包含步骤信息和支持的场输出类型
        :rtype: str

        实现细节:
        1. 构建步骤加载的基本信息字符串
        2. 从步骤对象获取场输出类型常量(field_output_type_constant)
        3. 添加支持的节点和单元场输出类型信息
        4. 将完整信息字符串转换为表格行格式
        5. 返回包含类名和内容的完整表格行
        """
        process_str = "\n\nThe OdbStep named '{}' has been loaded.".format(
            packaged_step.step_name)
        type_constant = packaged_step.field_output_type_constant
        process_str += "\nCurrent OdbStep supported field output types: \nnode:{}\nelement:{}".format(
            type_constant.valid_node_types, type_constant.valid_element_types)
        process_lines = self.get_table_line_by_str(process_str)
        return self.class_table_lines(packaged_step, process_lines)

    def packaged_step_progress_monitor(self, packaged_step, *argus, **kwargs):
        """
        步骤(Step)处理进度监控器

        该方法用于监控和显示Abaqus分析步骤(Step)的处理进度信息。
        它会调用[packaged_step_table_lines]方法生成格式化的步骤信息表格，
        并打印到标准输出(去除末尾换行符)。

        :param packaged_step: 包装后的步骤对象，包含步骤相关信息
        :type packaged_step: PackagedStepObject
        :param argus: 可变位置参数，用于传递额外的进度信息
        :param kwargs: 可变关键字参数，用于传递额外的进度信息

        功能说明:
        1. 调用[packaged_step_table_lines]方法获取格式化的步骤信息表格
        2. 使用[:-1]切片去除表格末尾的换行符
        3. 打印处理后的表格到标准输出

        注意:
        - 该方法主要用于实时显示步骤处理进度信息
        - 表格格式由父类的表格生成方法控制
        """
        print(self.packaged_step_table_lines(packaged_step)[:-1])

    def packaged_frame_manager_progress_monitor(
            self, packaged_frame_manager, managed_item=None, start=None, end=None, traverse_index=None, *argus,
            **keywords):
        """
        帧管理器进度监控方法

        该方法用于监控和管理帧处理进度，显示处理进度条和相关信息。
        主要功能包括：
        - 计算当前处理进度
        - 显示帧处理范围和当前帧ID
        - 更新进度条显示
        - 处理完成时显示总耗时

        :param packaged_frame_manager: 帧管理器对象，负责管理帧处理流程
        :type packaged_frame_manager: PackagedFramesManager
        :param managed_item: 当前处理的帧对象
        :type managed_item: PackagedFrame
        :param start: 起始帧索引
        :type start: int
        :param end: 结束帧索引
        :type end: int
        :param traverse_index: 当前遍历索引
        :type traverse_index: int
        :param argus: 额外位置参数
        :param keywords: 额外关键字参数

        处理流程:
        1. 计算总帧数和当前进度百分比
        2. 如果是首次处理该manager，显示初始信息(帧范围和数量)
        3. 当进度变化超过设定间隔时，更新进度条显示
        4. 处理完成时(进度=1)，显示总耗时并清理状态
        """
        # packaged_frame_manager: PackagedFramesManager
        # managed_item: PackagedFrame
        frame_num = end - start
        frame_progress = self._round_down_to_nearest_step(
            float(traverse_index) / (float(frame_num - 1)), self._progress_interval)
        # print("rate:'{}',frame_progress:'{}'".format(float(traverse_index) / (float(frame_num - 1)), frame_progress))
        # frame_progress = int(float(traverse_index) / (float(frame_num) - 1) * 10) / 10.0
        current_frame_id_str = "  Current frame id:'{}'".format(managed_item.frame_id)
        if packaged_frame_manager is not self._last_post_ext_object:
            frame_ids_list = [i for i in range(start, end)]
            frame_range_str = omit_representation_sequence(frame_ids_list)
            content = "\n\nNumber of frames to be processed:'{}'\nFrame ids range:'{}'\n\n".format(
                frame_num, frame_range_str)
            content = self.get_table_line_by_str(content)
            print(self.class_table_lines(packaged_frame_manager, content, False)[:-1])
            print(self.progress_bar_table_line(0, current_frame_id_str)[:-1])
            self._last_post_ext_object = packaged_frame_manager
            self._last_frame_progress = frame_progress
            self._frame_0_time = time.time()
        else:
            if frame_progress != self._last_frame_progress:
                print(self.progress_bar_table_line(frame_progress, current_frame_id_str)[:-1])
                self._last_frame_progress = frame_progress
            if frame_progress == 1:
                print(self.time_line(
                    time.time() - self._frame_0_time, content="\nProcessing all frames takes time:")[:-1])
                print(self.frame_line[:-1])
                del self._last_frame_progress
                del self._frame_0_time

    def packaged_mesh_objects_handler_progress_monitor(
            self, packaged_mesh_objects_handler, taken_time=None, info=None, *argus, **kwargs):
        """
        网格对象处理器进度监控方法

        该方法用于显示网格对象处理的进度信息，包括处理信息和耗时，并以表格形式输出。

        :param packaged_mesh_objects_handler: 网格对象处理器实例
        :type packaged_mesh_objects_handler: PackagedMeshObjectsSelectorBase
        :param taken_time: 处理耗时(秒)
        :type taken_time: float
        :param info: 处理信息描述
        :type info: str
        :param argus: 额外位置参数
        :param kwargs: 额外关键字参数

        处理流程:
        1. 将info信息格式化为表格行(开头添加换行符)
        2. 添加耗时信息行
        3. 组合类名和内容生成完整表格
        4. 打印表格(去除末尾换行符)
        """
        process_lines = self.get_table_line_by_str("\n" + info)
        process_lines += self.time_line(taken_time)
        print(self.class_table_lines(packaged_mesh_objects_handler, process_lines)[:-1])


def _get_logger_level_by_str(logger_level_str):
    """
    根据字符串返回对应的日志级别

    这个函数接受一个字符串参数，表示日志的级别，然后返回对应的logging模块中的日志级别值
    它提供了一种简单的方法来获取日志级别，避免了直接与logging模块的直接交互
    如果传入的日志级别字符串不匹配预定义的任何一个日志级别，将抛出KeyError异常

    :param logger_level_str: 日志级别的字符串表示，如'debug', 'info'等
    :type logger_level_str: str
    :return: 对应的日志级别值，如logging.DEBUG, logging.INFO等
    :rtype: int
    """
    return {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }[logger_level_str]


def configurate_a_logger(logger_name, logger_path, general_level, stream_level, file_level, logger_formatter):
    """
    配置日志记录器。

    此函数用于根据指定参数配置日志记录器，包括设置日志记录器名称、日志文件路径、日志级别及日志格式。
    同时支持控制台输出和文件记录两种方式，并可分别设置不同的日志级别。

    :param logger_name: 日志记录器的名称，用于标识日志记录器。
    :type logger_name: str
    :param logger_path: 存储日志的文件路径。
    :type logger_path: str
    :param general_level: 日志记录器的整体日志级别，决定处理的消息类型。
    :type general_level: str
    :param stream_level: 控制台输出的日志级别，决定控制台输出的消息类型。
    :type stream_level: str
    :param file_level: 文件输出的日志级别，决定写入日志文件的消息类型。
    :type file_level: str
    :param logger_formatter: 日志消息的格式，定义日志消息的显示和记录方式。
    :type logger_formatter: str
    :return: 配置好的日志记录器对象。
    """
    general_level, stream_level, file_level = map(_get_logger_level_by_str, [general_level, stream_level, file_level])
    # 创建一个具有指定名称的日志记录器对象
    logger = logging.getLogger(logger_name)
    # 创建一个控制台处理器以将日志输出到控制台
    stream_handler = logging.StreamHandler()
    # 创建一个文件处理器以将日志写入文件，指定文件路径、追加模式、最大文件大小和编码方式
    file_handler = logging.handlers.RotatingFileHandler(logger_path, mode="a", maxBytes=1000, encoding="utf-8")
    # 设置日志记录器及其处理器的日志级别
    logger.setLevel(general_level)
    stream_handler.setLevel(stream_level)
    file_handler.setLevel(file_level)
    # 创建日志格式化器并应用于处理器
    formatter = logging.Formatter(logger_formatter)
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    # 将处理器添加到日志记录器
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    # 返回配置好的日志记录器
    return logger


if __name__ == "__main__":
    pass
