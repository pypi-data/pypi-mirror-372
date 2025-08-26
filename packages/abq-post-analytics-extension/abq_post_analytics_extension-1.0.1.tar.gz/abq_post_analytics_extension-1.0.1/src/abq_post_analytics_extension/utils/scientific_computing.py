# -*- coding: UTF-8 -*-
import numpy as np


def calculate_distance_numpy(point1, point2):
    """
    计算两点之间的距离
    :param point1: numpy.ndarray，表示第一个点的坐标
    :param point2: numpy.ndarray，表示第二个点的坐标
    :return: 两点之间的欧几里得距离
    """
    # 确保两个点有相同数量的维度
    if point1.shape != point2.shape:
        raise ValueError("The two points must have the same number of dimensions")

        # 使用numpy的linalg.norm函数计算两点之间的欧几里得距离
    # 这里的'ord'参数设置为2，表示计算L2范数（即欧几里得距离）
    distance = np.linalg.norm(point1 - point2)

    return distance


def calculate_midpoint(point1, point2):
    """
    计算三维空间中两点的中点。

    :param point1: 第一个点的坐标，格式为 [x1, y1, z1]
    :type point1: list or tuple or numpy.ndarray
    :param point2: 第二个点的坐标，格式为 [x2, y2, z2]
    :type point2: list or tuple or numpy.ndarray
    :return: 中点的坐标，格式为 [xm, ym, zm]
    :rtype: list
    """
    if not is_3d_vector(point1) or not is_3d_vector(point2):
        raise ValueError("Input points must be 3D vectors")
    point1 = np.array(point1)
    point2 = np.array(point2)
    midpoint = (point1 + point2) / 2
    return midpoint.tolist()


def is_3d_vector(vector):
    """
    判断给定的列表、元组或numpy数组是否表示一个3D向量。

    一个3D向量是由三个数值（整数或浮点数）组成的集合。
    该方法用于验证输入是否满足这样的结构和类型要求。

    :param vector: 可能是列表、元组或numpy数组，需要被判断是否为3D向量
    :return: 如果输入是长度为3的列表、元组或numpy数组，并且每个元素都是整数或浮点数，则返回True；
    否则，返回False。
    """
    # 检查是否为列表、元组或numpy数组，并且长度为3
    if not isinstance(vector, (list, tuple, np.ndarray)) or len(vector) != 3:
        return False
    # 检查每个元素是否为整数或浮点数
    for component in vector:
        if not isinstance(component, (int, float)):
            return False
    return True
