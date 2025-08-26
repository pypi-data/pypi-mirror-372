# -*- coding: UTF-8 -*-
import codecs
import io
import json
import locale
import os
import shutil
import subprocess
import sys

try:
    from typing import Generator
except ImportError:
    pass

from ..utils.misc_utils import PackageBase


def parse_condition(condition, mode=None):
    """
    根据提供的条件字符串生成一个函数，该函数接受一个名称参数，并根据条件字符串评估是否满足条件。

    :param condition: 字符串类型的条件表达式，使用'and'、'or'逻辑运算符连接，支持括号如
        "'png' @or 'ppt' @or 'xls' @or 'txt' @or ('str1' @and 'str2')"
        执行命令："'png' in name or 'ppt' in name or 'xls' in name or 'txt' in name or ('str1' in name and 'str2'in name)"
    :type condition: str
    :param mode: 字符串，指定条件的模式，默认为'in'，可选值为'in'或'not in'。
    :type mode: str
    :return: 如果condition为None，返回一个始终返回True的lambda函数。
        否则，返回一个lambda函数，它接受一个名称参数，并使用条件表达式评估是否满足条件。
    """
    if mode is None:
        mode = "in"
    else:
        if mode not in ['in', 'not in']:
            raise ValueError("mode must be 'in' or 'not in'")
    # 如果条件为空，则任何名称都视为满足条件
    if condition is None:
        return lambda name: True

    def evaluate_condition(name, condition):
        """
        评估名称是否满足给定的条件表达式。

        :param name: 需要评估的名称字符串。
        :type name: str
        :param condition: 条件表达式字符串。
        :type condition: str
        :return: 根据条件表达式评估的结果。
        :rtype: bool
        """
        # 替换条件中的逻辑运算符为对名称的成员运算符，以支持灵活的条件判断
        condition = condition.rstrip()
        condition = condition.replace("@and", "{} name and".format(mode))
        condition = condition.replace("@or", "{} name or".format(mode))
        condition = condition.replace(")", "{} name)".format(mode))
        if condition[-1] != ")" or " {} name ".format(mode) not in condition:
            condition += " {} name ".format(mode)
        # 使用eval执行替换后的条件表达式进行评估
        try:
            return eval(condition)
        except Exception as e:
            raise Exception(
                "Illegal conditional expression string: '{}', exception information:{}".format(condition, e))

    # 返回一个lambda函数，用于评估名称是否满足条件
    return lambda name: evaluate_condition(name, condition)


class FileOperations(object):
    """
    文件操作类，提供了一些静态方法用于查找、获取文件和文件夹信息。
    """

    # 查找指定路径（默认为当前工作目录）下包含指定字段的文件名。
    @staticmethod
    def find_files_path_with_keyword(path=None, keyword=None):
        """
        查找指定路径（默认为当前工作目录）下包含指定字段的文件路径。

        :param path: 要搜索的目录路径。如果为空，则默认为当前工作目录。
        :type path: str
        :param keyword: 要在文件名中搜索的字段。
        :type keyword: str
        :return: 包含指定字段的文件名列表。如果没有找到任何文件，则抛出异常。
        :rtype: list[str]
        :raises Exception: 如果没有找到包含指定字段的文件，则抛出异常。
        """
        # 如果路径为空，则使用当前工作目录
        if not path:
            path = os.getcwd()
        # 一种可能的解决方案是遍历所有文件，然后检查文件名中是否包含keyword。
        files_path_found = []
        for filename in os.listdir(path):
            if keyword in filename:
                files_path_found.append(os.path.join(path, filename))
        # 检查是否找到了文件
        if not files_path_found:
            raise Exception("No file containing the specified field '{}' was found.".format(keyword))
        return files_path_found

    @classmethod
    def find_files_name_with_keyword(cls, path=None, keyword=None):
        """
        查找指定路径（默认为当前工作目录）下包含指定字段的文件名。

        :param path: 要搜索的目录路径。如果为空，则默认为当前工作目录。
        :type path: str
        :param keyword: 要在文件名中搜索的字段。
        :type keyword: str
        :return: 包含指定字段的文件名列表。如果没有找到任何文件，则抛出异常。
        :rtype: list[str]
        :raises Exception: 如果没有找到包含指定字段的文件，则抛出异常。
        """
        return [os.path.basename(file_path) for file_path in cls.find_files_path_with_keyword(path, keyword)]

    @staticmethod
    def get_folder_name_and_path(folder_path):
        """
        获取指定文件夹路径下的所有子文件夹的名称和路径。

        :param folder_path: str 文件夹路径
        :type folder_path: str
        :return: 生成器，返回每个子文件夹的名称和完整路径
        :rtype: Generator[tuple[str, str], None, None]
        """
        # 使用os.walk遍历文件系统，os.walk返回一个生成器，每次迭代返回当前目录的路径（root）、当前目录下的子目录名（dirs）和当前目录下的文件名（files）
        for root, dirs, files in os.walk(folder_path):
            # 遍历当前目录下的所有子目录（dirs）
            for folder in dirs:
                # 使用os.path.join将当前子目录的名称和当前目录的路径拼接成子目录的完整路径
                # 使用生成器yield返回当前子目录的名称和完整路径
                yield folder, os.path.join(root, folder)
            # 只获取第一层目录下的子目录，所以跳出循环
            break

    @staticmethod
    def split_path(path):
        """
        将路径字符串拆分为每一级元素的字符串列表。

        :param path: 需要拆分的路径字符串
        :type path: str
        :return: 包含路径每一级元素的字符串列表
        :rtype: list[str]
        """
        # 初始化空列表用于存储路径的每一级
        parts = []
        # 使用os.path.normpath()处理路径，确保路径分隔符正确
        path = os.path.normpath(path)
        # 循环拆分路径直到只剩盘符或根目录
        while True:
            path, tail = os.path.split(path)
            if tail != "":
                parts.append(tail)
            else:
                # 当路径只剩下盘符或根目录时，将其加入列表并结束循环
                if path != "":
                    parts.append(path)
                break
        # 反转列表以保持原始顺序
        parts.reverse()
        return parts

    @staticmethod
    def get_file_path_by_name(folder_path, include_condition=None, exclude_condition=None):
        """
        根据文件名筛选条件获取文件路径生成器。递归返回当前文件夹下所有满足要求的文件的完整路径。

        :param folder_path: 文件夹路径
        :type folder_path: str
        :param include_condition: 文件名必须满足的条件字符串，例如
        "'png' @or 'ppt' @or 'xls' @or 'txt' @or ('str1' @and 'str2')"
        :type include_condition: str
        :param exclude_condition: 文件名不得满足的条件字符串，例如
        "'png' @or 'ppt' @or 'xls' @or 'txt' @or ('str1' @and 'str2')"
        :type exclude_condition: str
        :return: 生成器，返回满足要求的每个文件的文件夹路径及文件名
        :rtype:Generator[tuple[str, str]]
        """
        # 解析条件字符串
        include_func = parse_condition(include_condition)
        exclude_func = parse_condition(exclude_condition, mode='not in')
        # 使用os.walk遍历文件系统，os.walk返回一个生成器，每次迭代返回当前目录的路径（root）、当前目录下的子目录名（dirs）和当前目录下的文件名（files）
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                # 调用check_string函数检查文件名是否满足包含和不包含的条件
                if include_func(file_name) and exclude_func(file_name):
                    # 如果满足条件，生成文件的完整路径并使用yield返回
                    yield root, file_name

    @staticmethod
    def force_delete_file(file_path):
        """
        强制删除指定的文件。

        :param file_path: 文件的完整路径。
        :type file_path: str
        :return:  None
        """
        # # Linux 或 macOS
        # subprocess.run(['rm', '-f', file_path])

        # Windows
        subprocess.run(['del', '/F', file_path], shell=True)

    @staticmethod
    def recursive_delete_folder(folder_path):
        """
        递归强制删除指定的文件夹及其所有内容。

        :param folder_path: 文件夹的完整路径。
        :type folder_path: str
        :return:  None
        """
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                FileOperations.force_delete_file(file_path)

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)

        try:
            os.rmdir(folder_path)
        except Exception as e:
            print("An error occurred while deleting the folder: {}".format(e))

    @staticmethod
    def copy(source_path, destination_path):
        """
        根据路径类型复制文件或目录，并检查目标路径。

        :param source_path: 源路径
        :type source_path: str
        :param destination_path: 目标路径
        :type destination_path: str
        """
        # 检查源路径类型
        if os.path.isdir(source_path):
            # 如果是目录，使用 shutil.copytree
            if os.path.exists(destination_path):
                if os.path.isdir(destination_path):
                    FileOperations.recursive_delete_folder(destination_path)
                else:
                    raise ValueError(
                        "The destination path {} already exists and is not a directory".format(destination_path))
            shutil.copytree(source_path, destination_path)
        elif os.path.isfile(source_path):
            # 如果是文件，使用 shutil.copy
            if os.path.exists(destination_path):
                if os.path.isdir(destination_path):
                    raise ValueError(
                        "The destination path {} already exists and is a directory".format(destination_path))
                os.remove(destination_path)
            else:
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                shutil.copy(source_path, destination_path)
        else:
            print("The source path {} is neither a file nor a directory".format(source_path))

    @staticmethod
    def sanitize_filename(filename, replace_char='_', illegal_chars=r'\\/:*?"<>|.(), '):
        """
        函数名：sanitize_filename
        功能：清理文件名中的非法字符

        :param filename: 原始文件名字符串，需要被清理
        :type filename: str
        :param replace_char: 用于替换非法字符的字符，默认为下划线('_')
        :type replace_char: str
        :param illegal_chars: 包含非法字符的字符串，默认包含Windows和Unix系统中的非法文件名字符
        返回值：清理后的文件名字符串，其中所有非法字符都被替换字符取代
        :type filename: str
        :return: 清理后的文件名字符串
        :rtype: str
        """
        # 遍历非法字符列表
        for char in illegal_chars:
            # 将文件名中的非法字符替换为指定的替换字符
            filename = filename.replace(char, replace_char)
        # 返回清理后的文件名
        return filename

    @staticmethod
    def copy_files_with_complex_conditions(src_dir, dst_dir, include_condition=None, exclude_condition=None,
                                           overwrite=False, max_workers=None):
        """
        复制指定目录下符合复杂筛选条件的文件及文件夹到另一个目录，保持原有文件结构。

        此方法目前仅支持python3

        :param max_workers: 并发线程数，默认为None，表示使用默认值，即CPU核心数
        :type max_workers: int|None
        :param src_dir: 源目录路径
        :type src_dir: str
        :param dst_dir: 目标目录路径
        :type dst_dir: str
        :param include_condition: 文件名必须满足的条件字符串，例如
        "'png' @or 'ppt' @or 'xls' @or 'txt' @or ('str1' @and 'str2')"
        :type include_condition: str
        :param exclude_condition: 文件名不得满足的条件字符串，例如
        "'png' @or 'ppt' @or 'xls' @or 'txt' @or ('str1' @and 'str2')"
        :type exclude_condition: str
        :param overwrite: 是否覆盖已存在的文件，默认为 False
        :type overwrite: bool
        :return: 无返回值
        """
        from concurrent.futures import ThreadPoolExecutor
        # 确保目标目录存在
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        # 解析条件字符串
        include_func = parse_condition(include_condition)
        exclude_func = parse_condition(exclude_condition, mode='not in')

        total_files = 0
        copied_files = 0

        # 统计总文件数
        for root, dirs, files in os.walk(src_dir):
            total_files += len(files)
        print("Total files to process: {}".format(total_files))
        src_files = []
        dst_files = []
        for root, dirs, files in os.walk(src_dir):
            # 计算当前目录相对于源目录的相对路径
            rel_path = os.path.relpath(root, src_dir)
            dst_root = os.path.join(dst_dir, rel_path)

            # 遍历文件
            if_makedirs = False
            for file in files:
                if include_func(file) and exclude_func(file):
                    # 创建目标目录中的对应子目录
                    if not if_makedirs:
                        if not os.path.exists(dst_root):
                            os.makedirs(dst_root)
                            if_makedirs = True
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst_root, file)

                    # 根据overwrite参数决定是否覆盖
                    if overwrite or not os.path.exists(dst_file):
                        src_files.append(src_file)
                        dst_files.append(dst_file)
                        if len(src_files) > 800:
                            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                                executor.map(shutil.copy2, src_files, dst_files)
                            src_files[:] = []
                            dst_files[:] = []
                        copied_files += 1
                    else:
                        pass
                        # print(f"Skipped (already exists): {src_file}")

        if src_files:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                executor.map(shutil.copy2, src_files, dst_files)
            src_files[:] = []
            dst_files[:] = []
        print("Copying completed. Total files processed: {}, Copied files: {}".format(total_files, copied_files))


class ExtendedFile(PackageBase):
    """
    一个用于处理文件操作的类。
    """
    ENCODINGS = ['utf-8', 'gbk', 'gb18030', 'big5', 'latin1']
    READ_ENCODING = None

    def __init__(self, mode, file_name=None, folder_path=None, file_path=None, *args, **kwargs):
        """
        初始化方法，用于设置文件处理类的属性。

        :param mode: 文件打开模式。
        :type mode: str
        :param file_name: 文件名。
        :type file_name: str
        :param folder_path: 文件夹路径，默认为当前工作目录。
        :type folder_path: str
        :param file_path: 文件路径，默认为None。当指定了此项后会覆盖file_name和folder_path的设置。
        :type file_path: str
        """
        super(ExtendedFile, self).__init__(*args, **kwargs)
        # 提高路径安全性
        self._validate_path(folder_path)
        self._validate_file_name(file_name)
        if file_path:
            self._validate_path(file_path)
            file_name = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)
        self.file_name = file_name
        self.mode = mode
        self.folder_path = folder_path if folder_path else os.getcwd()
        self.file = None
        # 获取系统编码方式
        self.encoding = self.get_system_encoding()
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        try:
            self.file_path = os.path.join(self.folder_path, file_name)
            self.file = io.open(self.file_path, mode, encoding=self.encoding)  # 修正了open函数的调用方式
        except IOError as e:
            print("Error opening file {folder_path}: {e}".format(folder_path=folder_path, e=e))
            additional_info = ""
            if len(file_name) > 88:
                additional_info += "Possible file name: '{}' Length: '{}' exceeds maximum length: '88'". \
                    format(file_name, len(file_name))
            raise IOError("{}\n{}".format(e, additional_info))
        self._last_bytes = None
        self._last_list_line_number = None
        self._last_list_column_number = None

    @property
    def last_bytes(self):
        """
        获取上次操作的内容的字节数。

        :return: 上次操作的内容的字节数。
        :rtype: bytes
        """
        return self._last_bytes

    @property
    def last_list_line_number(self):
        """
        获取上次操作的二维列表行号。

        :return: 上次操作的列表行号。
        :rtype: int
        """
        # 返回已设置的last_list_line_number
        return self._last_list_line_number

    @property
    def last_list_column_number(self):
        """
        获取上次操作的二维列表列的列号。

        :return: 上次操作的列表列的列号。
        :rtype: int
        """
        # 返回最后一个列表列的列号
        return self._last_list_column_number

    @staticmethod
    def get_system_encoding():
        """
        获取系统默认编码

        1. 首先使用 `locale.getpreferredencoding()` 获取系统区域设置的默认编码
        2. 如果获取到的编码是 'ANSI_X3.4-1968' (ASCII 别名)，则将其设为 None
        3. 最后返回系统编码，如果为 None 则返回 Python 默认编码 `sys.getdefaultencoding()`

        :return: 系统当前使用的编码名称 (如 'utf-8', 'gbk' 等)
        :rtype: str
        """
        # 获取系统默认编码
        encoding = locale.getpreferredencoding()
        # 如果默认编码是ANSI_X3.4-1968，这是ASCII的别名，那么使用环境变量获取编码
        if encoding == 'ANSI_X3.4-1968':
            encoding = None
        return encoding or sys.getdefaultencoding()

    def _validate_path(self, folder_path):
        """
        验证文件夹路径是否为绝对路径

        功能：
        - 检查传入的文件夹路径是否为绝对路径
        - 如果不是绝对路径则抛出 ValueError 异常

        :param folder_path: 要验证的文件夹路径字符串
        :return:  None
        :raises ValueError: 如果文件夹路径不是绝对路径
        """
        # 这里可以进一步完善路径验证，确保路径的安全性
        if folder_path and not os.path.isabs(folder_path):
            raise ValueError("Folder path must be an absolute path.")

    def _validate_file_name(self, file_name):
        """
        验证文件名是否合法
        :param file_name: 要验证的文件名字符串
        :return:  None
        :raises ValueError: 如果文件名包含路径分隔符
        """
        if file_name and os.path.sep in file_name:
            raise ValueError("File name cannot contain path separators.")
        # 这里可以添加更多的文件名验证逻辑，以确保安全性

    @staticmethod
    def _remove_last_char_if_match(s, char):
        """
        如果字符串s以指定的char字符结尾，则移除s中的最后一个字符。

        :param s: 待处理的字符串。
        :type s: str
        :param char: 需要匹配的字符。
        :type char: str
        :return: 处理后的字符串。
        :rtype: str
        """
        # 检查字符串s是否以char字符结尾
        if s.endswith(char):
            # 如果是，返回s中移除最后一个字符后的部分
            return s[:-1]
        # 如果不是，直接返回s
        return s

    def flatten_and_join(self, data, separator='\t', newline='\n', transpose=False):
        """
        递归地处理多维列表并将其转换为字符串。

        :param data: 多维列表数据
        :type data: list
        :param separator: 字符串元素之间的分隔符，默认为制表符
        :type separator: str
        :param newline: 行之间的换行符，默认为换行符
        :type newline: str
        :param transpose: 是否对数据进行转置
        :type transpose: bool
        :return: 转换后的字符串
        :rtype: str
        """
        if transpose and data and isinstance(data[0], list):
            data = list(map(list, zip(*data)))
        result_str = ""
        for item in data:
            if isinstance(item, list):
                result_str += self.flatten_and_join(item, separator, newline) + newline
            else:
                result_str += str(item) + separator
        return self._remove_last_char_if_match(result_str, separator)

    def write_multidimensional_list(self, data, transpose=False, separator='\t', newline='\n'):
        """
        将多维列表的数据写入到文件中。
        如果transpose参数为True，则会先对数据进行转置再写入。

        :param separator: 字符串元素之间的分隔符，默认为制表符
        :type separator: str
        :param newline: 行之间的换行符，默认为换行符
        :type newline: str
        :param data: 待写入的多维列表数据
        :type data: list
        :param transpose: 是否对数据进行转置
        :type transpose: bool
        :return: None
        :raise ValueError: 如果文件未正确初始化或数据不是多维列表格式，则抛出此异常
        """
        if not self.file:
            raise ValueError("File is not properly initialized.")

        # 检查数据是否为多维列表
        if not isinstance(data, list):
            raise ValueError("Data must be a multidimensional list.")

        # 使用辅助函数将多维列表转换为字符串
        string_data = self.flatten_and_join(data, transpose=transpose, separator=separator, newline=newline)
        string_data = string_data.rstrip(newline) + newline
        # 获取字符串中第一个换行符的位置，并计算行数和列数
        first_newline_index = string_data.find(newline)
        if first_newline_index != -1:
            self._last_list_line_number = string_data.count(newline) - 1
            self._last_list_column_number = string_data[:first_newline_index].count(separator)
        # 将数据写入文件
        self.write_str(string_data)

    def write_str(self, content):
        """
        将给定的内容写入文件。

        :param content: 要写入文件的内容。
        :type content: str
        :return: 无返回值。
        """
        if not isinstance(content, str):
            raise TypeError("Content must be a string.")
        # 将数据写入文件
        try:
            self.file.write(content)
            # 计算并记录最后一次写入的字节数
            self._last_bytes = len(content.encode(self.encoding))
        # 在python2中运行时执行如下过程
        except TypeError:
            # 编码为Unicode字符串写出
            bytes_data = content.decode(self.encoding)
            self.file.write(bytes_data)
            # 记录最后一次写入的字节数
            self._last_bytes = len(bytes_data)
        # 刷新文件缓冲区以确保数据写入磁盘
        self.file.flush()

    def dumps_and_write_json_str(self, content):
        """
        将内容转换为JSON字符串并写入。

        :param content: 要转换为JSON字符串并写入的内容。
        :type content: object
        :return:
        """
        self.write_str(json.dumps(content, ensure_ascii=False))

    @staticmethod
    def convert_encoding(input, source_encoding, target_encoding):
        """
        转换字符串或字节串的编码格式。

        此函数旨在将给定字符串或字节串从一种编码格式转换到另一种编码格式。
        它首先检查输入是否为字符串，如果是，则将其转换为Latin-1编码的字节串。
        然后，将字节串从其原始编码格式解码，再重新编码为目标编码格式。
        最后，根据需要将结果转换回字符串格式。

        :param input: 待转换编码的字符串或字节串。
        :type input: str or bytes
        :param source_encoding: 输入的原始编码格式。
        :type source_encoding: str
        :param target_encoding: 需要转换到的目标编码格式。
        :type target_encoding: str
        :return: 返回以目标编码格式编码的字符串或字节串。
        :rtype: str or bytes
        """
        # 检查输入是否为字符串，如果是，则将其转换为Latin-1编码的字节串
        if isinstance(input, str):
            input = codecs.latin_1_encode(input)[0]

        # 将输入从原始编码格式解码，再编码为目标编码格式
        string = codecs.decode(input, source_encoding).encode(target_encoding)

        # 检查结果是否为字符串，如果不是，则将其解码为目标编码格式
        if not isinstance(string, str):
            return string.decode(target_encoding)

        # 返回结果字符串
        return string

    @staticmethod
    def convert_unicode_to_bytes(data, encoding):
        """
        递归地将数据结构中的Unicode字符串转换为字节字符串。

        此函数旨在处理嵌套的数据结构（如字典和列表）以及非字符串对象，
        将其中的Unicode字符串转换为指定编码的字节字符串，而不影响其他类型的数据。

        :param data: 要转换的数据，可以是字典、列表或字符串。
        :type data: dict or list or str
        :param encoding: 用于转换Unicode字符串的编码方式（如'utf-8'）。
        :type encoding: str
        :return: 转换后的数据结构，其中的Unicode字符串被转换为字节字符串。
        :rtype: dict or list or str
        """
        # 如果数据是字典类型，则递归转换键和值
        if isinstance(data, dict):
            return {ExtendedFile.convert_unicode_to_bytes(key, encoding):
                        ExtendedFile.convert_unicode_to_bytes(value, encoding) for key, value in data.items()}
        # 如果数据是列表类型，则递归转换列表中的每个元素
        elif isinstance(data, list):
            return [ExtendedFile.convert_unicode_to_bytes(element, encoding) for element in data]
        # 如果数据不是字符串类型，则尝试将其编码为字节字符串
        elif not isinstance(data, str):
            try:
                return data.encode(encoding)
            except Exception:
                return data
        else:
            return data

    def read_and_load_json_str(self, encoding=None, **kwargs):
        """
        读取字符串并解析为JSON对象。

        本函数旨在从某种数据源（如文件或网络流）读取字符串，然后将其解析为JSON对象。
        它允许用户指定编码方式以及其他JSON解析参数。

        :param encoding: 指定读取字符串时使用的编码，如'utf-8'或'latin1'。
        :type encoding: str
        :param kwargs: 其他传递给json.loads函数的参数，用于控制JSON解析的行为。
        :type kwargs: dict
        :return: 转换后的JSON对象，其中的Unicode字符串被转换为字节字符串。
        :rtype: object
        """
        # 读取字符串并解析为JSON对象
        json_str = json.loads(self.read_str(encoding), **kwargs)

        # 将JSON对象中的Unicode字符转换为字节字符串
        return self.convert_unicode_to_bytes(json_str, self.encoding)

    def read_str(self, encoding=None):
        """
        读取文件为字符串。

        该方法使用指定或默认的编码读取文件内容。如果给定的编码无法解码文件，
        它将尝试使用其他支持的编码。如果所有编码都失败，则抛出异常。

        :param encoding: 要使用的编码。如果未提供，则使用READ_ENCODING或encoding的默认值。
        :type encoding: str
        :return: 文件内容的字符串。
        :rtype: str
        :raises ValueError: 如果无法使用任何支持的编码解码文件。
        """
        # 确定要使用的编码
        if encoding is None:
            if self.READ_ENCODING is not None:
                encoding = self.READ_ENCODING
            else:
                encoding = self.encoding
                ExtendedFile.READ_ENCODING = encoding
        # 尝试按照指定编码读取文件
        try:
            with io.open(self.file_path, self.mode, encoding=encoding) as file:
                return self.convert_encoding(file.read(), self.READ_ENCODING, self.encoding)
        except UnicodeDecodeError:
            # 如果出现Unicode解码错误，尝试使用其他支持的编码读取文件
            for encoding in self.ENCODINGS:
                try:
                    with io.open(self.file_path, self.mode, encoding=encoding) as file:
                        ExtendedFile.READ_ENCODING = encoding
                        return self.convert_encoding(file.read(), self.READ_ENCODING, self.encoding)
                except UnicodeDecodeError:
                    pass

            # 如果所有编码都无法解码文件，抛出ValueError异常
            raise ValueError("Unable to decode the file with any supported encoding: {}.".format(self.ENCODINGS))

    @staticmethod
    def _convert_to_number(s):
        """
        将字符串转换为整数或浮点数。

        :param s: 待转换的字符串。
        :type s: str
        :return: 转换后的数字。如果无法转换，则返回原字符串。
        :rtype: int|float|str
        """
        try:
            # 尝试将字符串转换为整数
            return int(s)
        except ValueError:
            try:
                # 如果转换为整数失败，尝试将字符串转换为浮点数
                return float(s)
            except ValueError:
                # 如果转换为浮点数也失败，返回原字符串
                return s

    def read_multidimensional_list(
            self, row_delimiter='\n', column_delimiter='\t', transpose=False, convert_to_number=True, encoding=None):
        """
        从文件中读取数据，并根据指定的行分隔符和列分隔符转换成二维列表。

        :param convert_to_number: 是否将可转为数字的字符串转换为数字，默认为True
        :param transpose: 是否转置数据，默认为False
        :type transpose: bool
        :param encoding: 读取的文件的编码方式，默认为None，自动确定
        :type encoding: str|None
        :param row_delimiter: 行分隔符，默认为换行符 '\n'
        :type row_delimiter: str
        :param column_delimiter: 列分隔符，默认为逗号 ','
        :type column_delimiter: str
        :return: 二维列表
        :rtype: list
        """

        lines_string = self.convert_unicode_to_bytes(self.read_str(encoding), self.encoding)
        lines_list = lines_string.split(row_delimiter)

        # 使用列表推导式将每一行按照列分隔符分割，并去除空行
        data = []
        for line in lines_list:
            stripped_line = line.strip()
            if stripped_line:
                data_line = []
                items = stripped_line.split(column_delimiter)
                for item in items:
                    if convert_to_number:
                        item = self._convert_to_number(item)
                    data_line.append(item)
                data.append(data_line)
        if transpose:
            data = list(map(list, zip(*data)))
        return data

    def generate_file_information_str(self):
        """
        生成文件信息字符串。
        :return: 文件信息字符串
        :rtype: str
        """
        return "file name: '{}', mode: '{}', ".format(self.file_name, self.mode)
        # return "file name: '{}', mode: '{}', file path: '{}', ".format(self.file_name, self.mode, self.file_path)

    def generate_list_output_information_str(self):
        """
        生成列表输出信息字符串。
        :return: 列表输出信息字符串
        :rtype: str
        """
        return self.generate_file_information_str() + "line number: {}, column number: {}, bytes: '{}B' accomplished" \
            .format(self.last_list_line_number, self.last_list_column_number, self._last_bytes)

    def close(self):
        """
        关闭文件。
        :return:  None
        """
        if self.file:
            self.file.close()
            self.file = None

    def get_packaged_item(self):
        return self.file

    def __enter__(self):
        """
        创建文件对象时，将文件对象作为上下文管理器的入口。

        :return: 文件对象
        :rtype: FileOperations
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出文件对象时，将文件对象作为上下文管理器的出口。
        :param exc_type: 抛出的异常类型
        :param exc_val: 抛出的异常对象
        :param exc_tb: 抛出的异常的追踪信息
        :return:  None
        """
        self.close()

    def __del__(self):
        """
        析构函数，用于关闭文件。

        :return:  None
        """
        self.close()


if __name__ == '__main__':
    # 示例-复制指定名称的文件
    FileOperations.copy_files_with_complex_conditions(
        src_dir=r"G:\working\yaliecang\analyse\parameter_analysis_of_different_inclination_angles",
        dst_dir=r"F:\test",
        include_condition="'png' @or 'ppt' @or 'xls' @or 'txt'",
        exclude_condition=None,
        overwrite=False
    )
