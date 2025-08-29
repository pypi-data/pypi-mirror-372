# -*- coding: utf-8 -*-
"""
可视化模块 - 用于处理检测结果的可视化展示

该模块提供了多种可视化函数，用于在图像上绘制检测框、标签和置信度得分。
支持自定义颜色、线宽、字体大小等参数，并提供了多种预设的颜色方案。
"""

import cv2
import numpy as np
import random
from typing import List, Tuple, Dict, Optional, Union
import logging


from .config import get_config

# COCO数据集类别
from .detector import CLASSES
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 预设颜色方案
COLOR_SCHEMES = {
    'default': {
        'box_color': (0, 255, 0),  # 绿色
        'text_color': (255, 255, 255),  # 白色
        'text_bg_color': (0, 0, 0),  # 黑色
    },
    'random': None,  # 随机颜色，每个类别一个颜色
    'rainbow': None,  # 彩虹色，根据类别ID生成颜色
    'dark': {
        'box_color': (66, 66, 66),  # 深灰色
        'text_color': (255, 255, 255),  # 白色
        'text_bg_color': (0, 0, 0),  # 黑色
    },
    'light': {
        'box_color': (200, 200, 200),  # 浅灰色
        'text_color': (0, 0, 0),  # 黑色
        'text_bg_color': (255, 255, 255),  # 白色
    },
}

# 为每个类别生成固定的随机颜色
RANDOM_COLORS = {}
for i, cls in enumerate(CLASSES):
    random.seed(i)  # 使用类别索引作为随机种子，确保颜色固定
    RANDOM_COLORS[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# 彩虹色方案 - 根据类别ID生成颜色
RAINBOW_COLORS = {}
for i, cls in enumerate(CLASSES):
    hue = i / len(CLASSES) * 180  # 色调范围0-180
    saturation = 255  # 饱和度最大
    value = 255  # 亮度最大
    # 将HSV转换为BGR
    hsv = np.array([[[hue, saturation, value]]], dtype=np.uint8)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    RAINBOW_COLORS[i] = tuple(map(int, bgr[0, 0]))

# 更新颜色方案
COLOR_SCHEMES['random'] = RANDOM_COLORS
COLOR_SCHEMES['rainbow'] = RAINBOW_COLORS


def draw_detection(image: np.ndarray, 
                  boxes: np.ndarray, 
                  classes: np.ndarray, 
                  scores: np.ndarray, 
                  color_scheme: str = 'default',
                  line_thickness: int = 2,
                  font_scale: float = 0.5,
                  font_thickness: int = 1,
                  show_score: bool = True,
                  score_format: str = '.2f',
                  custom_colors: Dict = None) -> np.ndarray:
    """
    在图像上绘制检测结果
    
    Args:
        image: 输入图像，BGR格式
        boxes: 边界框坐标，格式为[x1, y1, x2, y2]
        classes: 类别ID
        scores: 置信度得分
        color_scheme: 颜色方案，可选值：'default', 'random', 'rainbow', 'dark', 'light'
        line_thickness: 边界框线宽
        font_scale: 字体大小
        font_thickness: 字体粗细
        show_score: 是否显示置信度得分
        score_format: 置信度得分格式化字符串
        custom_colors: 自定义颜色方案，格式为{class_id: (B,G,R)}
        
    Returns:
        绘制了检测结果的图像
    """
    # 创建图像副本，避免修改原始图像
    img_result = image.copy()
    
    # 获取颜色方案
    if custom_colors is not None:
        colors = custom_colors
    elif color_scheme in COLOR_SCHEMES:
        colors = COLOR_SCHEMES[color_scheme]
    else:
        colors = COLOR_SCHEMES['default']
    
    # 绘制每个检测框
    for i in range(len(boxes)):
        # 获取边界框坐标
        x1, y1, x2, y2 = map(int, boxes[i])
        
        # 获取类别ID和置信度
        class_id = int(classes[i])
        score = scores[i]
        
        # 获取类别名称
        class_name = CLASSES[class_id] if class_id < len(CLASSES) else f"未知类别({class_id})"
        
        # 确定颜色
        if color_scheme in ['random', 'rainbow']:
            box_color = colors.get(class_id, (0, 255, 0))  # 默认绿色
            text_bg_color = (0, 0, 0)  # 黑色背景
            text_color = (255, 255, 255)  # 白色文字
        else:
            box_color = colors.get('box_color', (0, 255, 0))
            text_bg_color = colors.get('text_bg_color', (0, 0, 0))
            text_color = colors.get('text_color', (255, 255, 255))
        
        # 绘制边界框
        cv2.rectangle(img_result, (x1, y1), (x2, y2), box_color, line_thickness)
        
        # 准备标签文本
        if show_score:
            label = f"{class_name} {score:{score_format}}"
        else:
            label = class_name
        
        # 获取文本大小
        (text_width, text_height), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
        
        # 绘制标签背景
        cv2.rectangle(
            img_result, 
            (x1, y1 - text_height - baseline), 
            (x1 + text_width, y1), 
            text_bg_color, 
            -1  # 填充矩形
        )
        
        # 绘制标签文本
        cv2.putText(
            img_result, 
            label, 
            (x1, y1 - baseline), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            font_scale, 
            text_color, 
            font_thickness
        )
    
    return img_result


def draw_detection_supervision(image: np.ndarray, 
                             boxes: np.ndarray, 
                             classes: np.ndarray, 
                             scores: np.ndarray) -> np.ndarray:
    """
    使用supervision库绘制检测结果（如果已安装）
    
    Args:
        image: 输入图像，BGR格式
        boxes: 边界框坐标，格式为[x1, y1, x2, y2]
        classes: 类别ID
        scores: 置信度得分
        
    Returns:
        绘制了检测结果的图像
    """
    try:
        import supervision as sv
        
        # 创建图像副本
        img_result = image.copy()
        
        # 如果没有检测到目标，直接返回原图
        if len(boxes) == 0:
            return img_result
        
        # 转换为supervision格式的检测结果
        detections = sv.Detections(
            xyxy=boxes,
            class_id=classes.astype(int),
            confidence=scores
        )
        
        # 创建标签注释器
        label_annotator = sv.LabelAnnotator(
            text_position=sv.Position.TOP_LEFT,
            text_scale=0.5,
            text_thickness=1,
            text_padding=5,
            color_lookup=sv.ColorLookup.CLASS
        )
        
        # 创建边界框注释器
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            color_lookup=sv.ColorLookup.CLASS
        )
        
        # 生成标签
        labels = [f"{CLASSES[class_id]} {confidence:.2f}" 
                 for class_id, confidence in zip(detections.class_id, detections.confidence)]
        
        # 绘制边界框和标签
        img_result = box_annotator.annotate(scene=img_result, detections=detections)
        img_result = label_annotator.annotate(scene=img_result, detections=detections, labels=labels)
        
        return img_result
    except ImportError:
        # 如果supervision库未安装，使用默认绘制方法
        return draw_detection(image, boxes, classes, scores)


def draw_fps(image: np.ndarray, 
            fps: float, 
            position: Tuple[int, int] = (10, 30),
            font_scale: float = 0.7,
            color: Tuple[int, int, int] = (0, 255, 0),
            thickness: int = 2) -> np.ndarray:
    """
    在图像上绘制FPS信息
    
    Args:
        image: 输入图像
        fps: FPS值
        position: 文本位置，默认左上角
        font_scale: 字体大小
        color: 文本颜色，BGR格式
        thickness: 文本粗细
        
    Returns:
        绘制了FPS信息的图像
    """
    # 创建图像副本
    img_result = image.copy()
    
    # 格式化FPS文本
    fps_text = f"FPS: {fps:.1f}"
    
    # 绘制文本
    cv2.putText(
        img_result,
        fps_text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness
    )
    
    return img_result


def draw_timing_info(image: np.ndarray,
                    inference_time: float,
                    process_time: float,
                    position: Tuple[int, int] = (10, 30),
                    line_spacing: int = 30,
                    font_scale: float = 0.7,
                    color: Tuple[int, int, int] = (0, 255, 0),
                    thickness: int = 2) -> np.ndarray:
    """
    在图像上绘制推理和处理时间信息
    
    Args:
        image: 输入图像
        inference_time: 推理时间(ms)
        process_time: 后处理时间(ms)
        position: 起始文本位置
        line_spacing: 行间距
        font_scale: 字体大小
        color: 文本颜色，BGR格式
        thickness: 文本粗细
        
    Returns:
        绘制了时间信息的图像
    """
    # 创建图像副本
    img_result = image.copy()
    
    # 格式化时间文本
    inference_text = f"推理时间: {inference_time:.1f}ms"
    process_text = f"后处理时间: {process_time:.1f}ms"
    total_text = f"总时间: {inference_time + process_time:.1f}ms"
    
    # 绘制文本
    x, y = position
    cv2.putText(img_result, inference_text, (x, y), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    cv2.putText(img_result, process_text, (x, y + line_spacing), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    cv2.putText(img_result, total_text, (x, y + 2 * line_spacing), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    
    return img_result


def save_image(image: np.ndarray, output_path: str) -> bool:


    """
    保存图像到指定路径
    
    Args:
        image: 输入图像
        output_path: 输出路径
        
    Returns:
        保存成功返回True，否则返回False
    """
    try:
        # 确保输出目录存在
        import os
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 保存图像
        cv2.imwrite(output_path, image)
        return True
    except Exception as e:
        logging.info(f"保存图像失败: {e}")
        return False

# 自定义可视化函数
def visualize_detections(image, boxes, classes, scores):
    """
    使用supervision库在图像上绘制检测结果
    
    Args:
        image: 输入图像，BGR格式
        boxes: 边界框坐标，格式为[x1, y1, x2, y2]
        classes: 类别ID
        scores: 置信度得分
        
    Returns:
        绘制了检测结果的图像
    """
    try:
        import supervision as sv
        HAS_SUPERVISION = True
    except ImportError:
        HAS_SUPERVISION = False
        print("提示: 安装 zmkj-rknn-tools[viz] 以获得更好的可视化效果")

    # 创建图像副本
    img_result = image.copy()
    
    # 如果没有检测到目标，直接返回原图
    if len(boxes) == 0:
        return img_result
    
    # 转换为supervision格式的检测结果
    detections = sv.Detections(
        xyxy=boxes,
        class_id=classes.astype(int),
        confidence=scores
    )
    
    # 创建标签注释器
    label_annotator = sv.LabelAnnotator(
        text_position=sv.Position.TOP_LEFT,
        text_scale=0.5,
        text_thickness=1,
        text_padding=5,
        color_lookup=sv.ColorLookup.CLASS
    )
    
    # 创建边界框注释器
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        color_lookup=sv.ColorLookup.CLASS
    )
    
    # 生成标签
    labels = [f"{CLASSES[class_id]} {confidence:.2f}" 
             for class_id, confidence in zip(detections.class_id, detections.confidence)]
    
    # 绘制边界框和标签
    img_result = box_annotator.annotate(scene=img_result, detections=detections)
    img_result = label_annotator.annotate(scene=img_result, detections=detections, labels=labels)
    
    return img_result