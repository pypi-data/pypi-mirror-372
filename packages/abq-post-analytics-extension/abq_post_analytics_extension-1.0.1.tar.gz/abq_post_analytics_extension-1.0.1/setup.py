# -*-coding:utf-8-*-
import io
from setuptools import setup, find_packages

setup(
    name="abq_post_analytics_extension",
    version="1.0.01",
    description="ABQ 后处理扩展",
    author="FeiI8",
    author_email="2286528584@qq.com",
    # 这个函数会自动查找 src 目录下的所有包。where='src' 参数指定了包的根目录。
    packages=find_packages(where='src'),  # 指定包的位置
    package_dir={'': 'src'},  # 指定包的根目录
    py_modules=[],  # 如果有单独的 Python 模块，可以在这里列出
    long_description=io.open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/FeiI8/abq_postprocessings.git",
    install_requires=[],
    license="GPL-3.0",
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)",],
    package_data={'abq_post_analytics_extension': ['default_config.py','LICENSE']},
)