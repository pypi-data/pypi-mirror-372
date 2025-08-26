# -*- coding: UTF-8 -*-
import os.path
import re
import time

from ..utils.misc_utils import check_sequence_type, check_type
from ..utils.file_operations import FileOperations, ExtendedFile


class TextManager:
    """
    文本文件管理类
    """
    MERGE_FILE_NUM = None

    @staticmethod
    def split_string_with_delimiters(target_str, delimiters):
        """
        根据给定的分隔符列表将目标字符串拆分为一个字符串列表。

        :param target_str: 目标字符串
        :param delimiters: 分隔符列表
        :return: 拆分后的字符串列表
        """
        # 初始化结果列表
        result = []

        # 将所有分隔符添加到正则表达式中
        delimiter_pattern = '|'.join(map(re.escape, delimiters))

        # 使用正则表达式拆分字符串
        parts = re.split(delimiter_pattern, target_str)

        # 过滤掉空字符串
        result = [part for part in parts if part]

        return result

    @staticmethod
    def merge_all_text(
            origin_folder_path, target_folder_path, target_file_name, title_list=None, include_condition=None,
            exclude_condition=None, separator=None, line_range_start=None, line_range_end=None):
        """
        将源文件夹中的所有文本文件合并到目标文件夹中的一个文件中。

        :param line_range_end:每个文本文件要合并的行范围的开始序号
        :type line_range_end:int
        :param line_range_start:每个文本文件要合并的行范围的结束序号
        :type line_range_start:int
        :param origin_folder_path: 原始文件夹路径
        :param target_file_name: 目标文件名
        :param target_folder_path: 目标文件夹路径
        :type target_folder_path:str
        :param target_file_name: 目标文件名
        :type target_file_name:str
        :param title_list: 标题列表，如果提供，将在合并的文件前插入
        :type title_list:list[str]|None
        :param include_condition: 文件名必须满足的条件字符串，例如
        "'png' @or 'ppt' @or 'xls' @or 'txt' @or ('str1' @and 'str2')"
        :param exclude_condition: 文件名不得满足的条件字符串，例如
        "'png' @or 'ppt' @or 'xls' @or 'txt' @or ('str1' @and 'str2')"
        :param separator: 用于拆分文件名的分隔符，默认为 ['-']
        :return: 无
        """
        check_type(origin_folder_path, str)
        check_type(target_folder_path, str)
        check_type(target_file_name, str)
        check_type(include_condition, str, None)
        check_type(exclude_condition, str, None)
        check_type(line_range_start, int, None)
        check_type(line_range_end, int, None)
        # 检查各字符串列表参数的有效性
        for str_list in [title_list, separator]:
            if str_list is not None:
                check_sequence_type(str_list, str)

        # 设置默认分隔符
        if separator is None:
            separator = ['-']

        # 获取原始文件夹路径列表
        origin_path_list = FileOperations.split_path(origin_folder_path)

        # 遍历原始文件夹中的文件
        for i, (root, file_name) in enumerate(FileOperations.get_file_path_by_name(
                origin_folder_path, include_condition, exclude_condition)):
            # 获取当前文件路径列表
            file_path = os.path.join(root, file_name)
            file_path_list = FileOperations.split_path(file_path)

            # 提取前缀路径列表
            prefix_path_list = file_path_list[len(origin_path_list) - 1:]
            prefix_list = []
            # 使用分隔符拆裂每个前缀，生成前缀列表
            for prefix in prefix_path_list:
                prefix_list.extend(TextManager.split_string_with_delimiters(prefix, separator))

            # 打开原始文件，读取多维列表内容
            origin_file = ExtendedFile("r", os.path.basename(file_path), os.path.dirname(file_path))
            origin_text_list = origin_file.read_multidimensional_list()
            origin_file.close()

            # 为原始文本列表的每一行添加前缀列表
            target_text_list = [prefix_list + line for line in origin_text_list]

            # 根据是否是第一个文件，设置文件操作模式为写入或追加
            target_text_list = target_text_list[line_range_start:line_range_end]
            if i == 0:
                # 如果提供了标题列表，则在文本前插入标题列表
                if title_list is not None:
                    target_text_list.insert(0, title_list)
                mode = "w"
            else:
                mode = "a"
            # 打开目标文件，写入处理后的文本列表
            target_file = ExtendedFile(mode, target_file_name, target_folder_path)
            target_file.write_multidimensional_list(target_text_list)
            target_file.close()
        TextManager.MERGE_FILE_NUM = i


if __name__ == "__main__":
    print("execute text_files_organization.py ..................................................")
    print("TextManager.merge_all_text(...)")
    tim1 = time.time()
    TextManager.merge_all_text(
        origin_folder_path=r"G:\working\yaliecang\analyse\parameter_analysis_of_working_condition_combination",
        target_folder_path=r"G:\working\yaliecang\analyse\parameter_analysis_of_working_condition_combination\数据汇总",
        target_file_name="all_text.txt",
        include_condition="'txt' @and 'max_data'",
        exclude_condition="'history'",
        separator=['-', "_"])
    print("{} files have been merged..".format(TextManager.MERGE_FILE_NUM))
    print("spend time: {} s".format(time.time() - tim1))
