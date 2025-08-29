#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像推理示例脚本

该脚本展示了如何使用rknn-tools库进行图像推理，包括模型加载、图像处理、目标检测和结果可视化。
支持处理单张图像或目录中的多张图像，并可以保存检测结果。
"""

import os
import sys
import time
import argparse
import cv2
import numpy as np
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# 导入rknn-tools库
from zmkj_rknn_tools.detector import YOLOv8Detector, CLASSES
from zmkj_rknn_tools.config import update_config, get_config
from zmkj_rknn_tools.data import get_bus_image, suggest_data_installation

# 导入supervision库进行可视化
try:
    import supervision as sv
    HAS_SUPERVISION = True
except ImportError:
    HAS_SUPERVISION = False
    print("提示: 安装 zmkj-rknn-tools[viz] 以获得更好的可视化效果")


def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="YOLOv8 RKNN图像推理示例")
    parser.add_argument("--model", type=str, required=True, help="RKNN模型路径")
    parser.add_argument("--input", type=str, help="输入图像路径或目录（如果不指定，将使用示例图像）")
    parser.add_argument("--output", type=str, default="output", help="输出目录")
    parser.add_argument("--conf-thres", type=float, default=0.25, help="置信度阈值")
    parser.add_argument("--nms-thres", type=float, default=0.45, help="NMS阈值")
    parser.add_argument("--show", action="store_true", help="显示结果，默认不显示（适用于无GUI环境）")
    parser.add_argument("--img-size", type=int, nargs=2, default=[640, 640], 
                        help="模型输入尺寸 [宽, 高]")
    parser.add_argument("--cache-size", type=int, default=10, 
                        help="结果缓存大小，0表示禁用缓存")
    parser.add_argument("--fast-nms", action="store_true", help="使用快速NMS")
    parser.add_argument("--parallel", action="store_true", help="使用并行处理")
    
    args = parser.parse_args()
    
    # 如果没有指定输入图像，尝试使用示例图像
    if not args.input:
        bus_image = get_bus_image()
        if bus_image and bus_image.exists():
            args.input = str(bus_image)
            print(f"使用示例图像: {args.input}")
        else:
            suggest_data_installation()
            print("错误: 未指定输入图像，且示例数据不可用")
            print("请使用 --input 参数指定图像路径，或安装示例数据:")
            print("pip install zmkj-rknn-tools[examples-data]")
            sys.exit(1)
    
    return args


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


def draw_timing_info(image, timing_info, start_position=(10, 30), line_spacing=30, 
                    text_scale=0.7, color=(0, 255, 0), thickness=2):
    """
    在图像上绘制时间信息
    
    Args:
        image: 输入图像
        timing_info: 时间信息字典，键为阶段名称，值为时间（毫秒）
        start_position: 起始文本位置
        line_spacing: 行间距
        text_scale: 字体大小
        color: 文本颜色，BGR格式
        thickness: 文本粗细
        
    Returns:
        绘制了时间信息的图像
    """
    # 创建图像副本
    img_result = image.copy()
    
    
    # 绘制每个时间信息
    for i, (stage, time_ms) in enumerate(timing_info.items()):
        # 计算当前行的位置
        position = sv.Point(x=start_position[0], y=start_position[1] + i * line_spacing)
        # 格式化文本
        text = f"{stage}: {time_ms:.2f} ms"
        # 绘制文本
        img_result = sv.draw_text(scene=img_result, text=text, text_anchor=position, text_color=sv.Color.from_bgr_tuple(color))

    return img_result


def save_image(image, output_path):
    """
    保存图像到指定路径
    
    Args:
        image: 输入图像
        output_path: 输出路径
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # 使用supervision保存图像
    cv2.imwrite(output_path, image)


def process_image(detector, image_path, conf_thres, nms_thres, show, output_dir):
    """
    处理单张图像
    
    Args:
        detector: YOLOv8RKNN检测器实例
        image_path: 图像路径
        conf_thres: 置信度阈值
        nms_thres: NMS阈值
        show: 是否显示结果
        output_dir: 输出目录
        
    Returns:
        inference_time: 推理时间(ms)
        process_time: 后处理时间(ms)
    """
    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图像: {image_path}")
        return 0, 0
    
    # 目标检测
    boxes, classes, scores, inference_time, process_time = detector.detect(
        image=img, conf_thresh=conf_thres, nms_thresh=nms_thres)
    
    # 绘制检测结果
    result_img = visualize_detections(img, boxes, classes, scores)
    
    # 绘制时间信息
    timing_info = {
        "推理时间": inference_time,
        "后处理时间": process_time,
        "总时间": inference_time + process_time
    }
    result_img = draw_timing_info(result_img, timing_info)
    
    # 保存结果
    if output_dir:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        filename = os.path.basename(image_path)
        output_path = os.path.join(output_dir, filename)
        
        # 保存图像
        save_image(result_img, output_path)
        print(f"结果已保存到: {output_path}")
    
    # 显示结果
    if show:
        cv2.imshow("YOLOv8 RKNN", result_img)
        key = cv2.waitKey(0)
        if key == 27:  # ESC键退出
            return inference_time, process_time
    
    return inference_time, process_time


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_args()
    
    # 更新配置
    update_config({
        'img_size': args.img_size,
        'obj_thresh': args.conf_thres,
        'nms_thresh': args.nms_thres,
        'cache_size': args.cache_size,
        'use_fast_nms': args.fast_nms,
        'use_parallel': args.parallel,
    })
    
    # 创建检测器
    detector = YOLOv8Detector(args.model)
    
    # 处理输入
    if os.path.isdir(args.input):
        # 处理目录中的所有图像
        image_files = [os.path.join(args.input, f) for f in os.listdir(args.input) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if not image_files:
            print(f"目录中没有找到图像文件: {args.input}")
            return
        
        # 统计时间
        total_inference_time = 0
        total_process_time = 0
        
        for image_path in image_files:
            print(f"处理图像: {image_path}")
            inference_time, process_time = process_image(
                detector, image_path, args.conf_thres, args.nms_thres, 
                args.show, args.output)
            
            total_inference_time += inference_time
            total_process_time += process_time
        
        # 计算平均时间
        avg_inference_time = total_inference_time / len(image_files)
        avg_process_time = total_process_time / len(image_files)
        
        print(f"\n处理完成 {len(image_files)} 张图像")
        print(f"平均推理时间: {avg_inference_time:.2f}ms")
        print(f"平均后处理时间: {avg_process_time:.2f}ms")
        print(f"平均总时间: {avg_inference_time + avg_process_time:.2f}ms")
        
    else:
        # 处理单张图像
        if not os.path.isfile(args.input):
            print(f"图像文件不存在: {args.input}")
            return
        
        inference_time, process_time = process_image(
            detector, args.input, args.conf_thres, args.nms_thres, 
            args.show, args.output)
        
        print(f"\n处理完成")
        print(f"推理时间: {inference_time:.2f}ms")
        print(f"后处理时间: {process_time:.2f}ms")
        print(f"总时间: {inference_time + process_time:.2f}ms")
    
    # 释放资源
    detector.release()
    if args.show:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()