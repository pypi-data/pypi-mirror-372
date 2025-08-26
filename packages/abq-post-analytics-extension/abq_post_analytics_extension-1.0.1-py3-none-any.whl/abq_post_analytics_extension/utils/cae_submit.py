# -*- coding: UTF-8 -*-
"""
此模块仅限python3 使用
"""
import os
import subprocess

from ..utils.file_operations import FileOperations


def run_abaqus_script(script_path, abq="abq2020", path=os.getcwd()):
    """
    执行 Abaqus 脚本。

    该函数尝试通过 os.system 执行指定路径的 Abaqus 脚本。如果执行过程中出现错误，会捕获并打印错误信息。

    :param script_path: 脚本执行的工作目录，默认为工作目录
    :type script_path: str
    :param abq: Abaqus 脚本的路径。
    :type abq: str
    :param path: 软件的命令， 默认为 'abq2020'。
    :type path: str
    :return:  None
    """
    # 构建 Abaqus 脚本的后处理命令
    postprocessing_system_command = "call {} cae noGUI={}".format(abq, script_path)
    base_path = os.getcwd()
    os.chdir(path)
    os.system(postprocessing_system_command)
    os.chdir(base_path)


def submit_job(inp_name=None, folder_path=None, abq="abq2020", cpus=4):
    """
    提交一个ABAQUS作业。

    该函数用于在指定的文件夹路径中，通过构建和执行ABAQUS命令来提交一个作业。
    用户可以指定作业名称、文件夹路径、ABAQUS版本和CPU数量。默认情况下，
    使用abq2020作为ABAQUS版本，并使用4个CPU。

    :param inp_name: 要提交的inp文件的名称（不包含扩展名称:.inp），为空则在当前目录中自动搜索第一个.inp文件
    :type inp_name: str
    :param folder_path: 作业提交的文件夹路径。默认为None，表示在当前目录提交。
    :type folder_path: str
    :param abq: ABAQUS版本。默认为"abq2020"。
    :type abq: str
    :param cpus: 用于作业的CPU数量。默认为4。
    :type cpus: int
    :return:  None
    """
    # 获取当前工作目录
    base_path = os.getcwd()
    # 如果指定了文件夹路径并且该路径存在，则切换到该路径
    if folder_path and os.path.exists(folder_path):
        os.chdir(folder_path)
    if not inp_name:
        inp_name = FileOperations.find_files_name_with_keyword(keyword="inp")[0].split(".")[0]
    # 构建ABAQUS命令，设置作业名、CPU数量、不提示用户确认
    command = r"{} job={}".format(abq,inp_name) + r" int cpus={} ask=off".format(cpus)
    # 构建完整的命令，用于在指定文件夹下执行前面构建的ABAQUS命令
    full_command = 'cmd /c "cd /d {} && {}"'.format(folder_path,command)
    # 使用subprocess库执行构建好的命令，调用系统shell进行作业提交
    process = subprocess.Popen(full_command, shell=True)
    process.communicate()
    # 作业提交完成后，切换回初始目录
    os.chdir(base_path)


def submit_calculations_and_run_specified_post_processing_scripts(
        path, post_processing_path, abq, inp_name=None, if_delete_odb=False):
    """
    提交计算并运行指定的后处理脚本。

    该函数会切换到指定的目录，提交一个名为job_name的计算任务，
    然后运行后处理脚本。如果if_delete_odb为True，还会删除生成的odb文件。

    :param path: 计算任务所在的目录路径。
    :param post_processing_path: 后处理脚本的路径。
    :param abq: Abaqus软件的路径。
    :param inp_name: 要提交的inp文件的名称（不包含扩展名称:.inp），为空则在当前目录中自动搜索第一个.inp文件
    :param if_delete_odb: 是否删除odb文件，默认为False。
    :return:  None
    """
    # 保存当前工作目录的路径
    base_path = os.getcwd()
    # 切换工作目录到当前高度文件夹
    os.chdir(path)
    # 提交计算
    submit_job(inp_name=inp_name, folder_path=path)
    # 运行后处理程序
    run_abaqus_script(post_processing_path, abq, path)
    # 删除odb文件
    if if_delete_odb:
        # 获取odb文件路径
        odb_path = list(FileOperations.get_file_path_by_name(folder_path=path, include_condition=".odb"))[0]
        # 强制删除odb文件
        FileOperations.force_delete_file(odb_path)
    # 重置工作目录到初始路径
    os.chdir(base_path)
