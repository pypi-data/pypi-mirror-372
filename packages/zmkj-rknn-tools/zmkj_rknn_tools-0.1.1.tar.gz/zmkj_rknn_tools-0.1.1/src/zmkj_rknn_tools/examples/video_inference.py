#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频/摄像头推理示例脚本

该脚本展示了如何使用rknn-tools库进行视频或摄像头推理，包括模型加载、视频处理、目标检测和结果可视化。
支持处理视频文件或摄像头输入，并可以保存检测结果。
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

# 导入supervision库进行可视化
import supervision as sv


def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="YOLOv8 RKNN视频/摄像头推理示例")
    parser.add_argument("--model", type=str, required=True, help="RKNN模型路径")
    parser.add_argument("--input", type=str, default="0", 
                        help="输入源，可以是视频文件路径或摄像头ID（默认为0）")
    parser.add_argument("--output", type=str, default="output", help="输出视频路径，为空则不保存")
    parser.add_argument("--conf-thres", type=float, default=0.25, help="置信度阈值")
    parser.add_argument("--nms-thres", type=float, default=0.45, help="NMS阈值")
    # 移除color-scheme参数，使用supervision库的默认颜色方案
    parser.add_argument("--img-size", type=int, nargs=2, default=[640, 640], 
                        help="模型输入尺寸 [宽, 高]")
    parser.add_argument("--cache-size", type=int, default=10, 
                        help="结果缓存大小，0表示禁用缓存")
    parser.add_argument("--skip-frames", type=int, default=0, 
                        help="跳帧数，0表示不跳帧")
    parser.add_argument("--fast-nms", action="store_true", help="使用快速NMS")
    parser.add_argument("--parallel", action="store_true", help="使用并行处理")
    parser.add_argument("--downscale", type=int, default=1, 
                        help="下采样因子，对于高分辨率视频可以提高性能")
    parser.add_argument("--show", action="store_true", 
                        help="显示图像，默认不显示（适用于无GUI环境）")
    
    return parser.parse_args()


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


def draw_fps(image, fps, position=(60, 30), text_scale=0.7, color=None, thickness=2):
    """
    在图像上绘制FPS信息
    
    Args:
        image: 输入图像
        fps: FPS值
        position: 文本位置，默认左上角
        text_scale: 字体大小
        color: 文本颜色，BGR格式
        thickness: 文本粗细
        
    Returns:
        绘制了FPS信息的图像
    """
    # 创建图像副本
    img_result = image.copy()
  
    # 创建文本注释器
    sv.draw_text(
        img_result,
        text=f"FPS: {fps:.1f}",
        text_anchor =sv.Point(x=position[0], y=position[1]),
        text_scale=text_scale,
        text_thickness=thickness,
        text_color=color if color is not None else sv.Color.BLACK
    )

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
    sv.save_image(image_path=output_path, image=image)


def draw_timing_info(image, timing_info, start_position=(10, 30), line_spacing=30, text_scale=0.7, color=(0, 255, 0), thickness=2):
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
    
    # 创建文本注释器
    text_annotator = sv.TextAnnotator(
        text_scale=text_scale,
        text_thickness=thickness,
        text_color=color
    )
    
    # 绘制每个时间信息
    for i, (stage, time_ms) in enumerate(timing_info.items()):
        # 计算当前行的位置
        position = (start_position[0], start_position[1] + i * line_spacing)
        
        # 格式化文本
        text = f"{stage}: {time_ms:.2f} ms"
        
        # 绘制文本
        img_result = text_annotator.annotate(scene=img_result, text=text, position=position)
    
    return img_result


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
        'skip_frames': args.skip_frames,
        'use_fast_nms': args.fast_nms,
        'use_parallel': args.parallel,
        'downscale_factor': args.downscale,
    })
    
    # 创建检测器
    detector = YOLOv8Detector(args.model)
    
    # 打开视频源
    try:
        # 尝试将输入解析为摄像头ID
        source = int(args.input)
    except ValueError:
        # 如果不是整数，则视为文件路径
        source = args.input
    
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"无法打开视频源: {args.input}")
        return
    
    # 获取视频信息
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"视频分辨率: {width}x{height}, FPS: {fps}")
    
    # 创建视频写入器
    video_writer = None
    if args.output:
        filename = os.path.basename(args.input)
        if filename.isdigit():
            filename = f"camera_{filename}.mp4"
        output_path = os.path.join(args.output, filename)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # 统计信息
    frame_count = 0
    total_inference_time = 0
    total_process_time = 0
    fps_list = []
    
    # 计时器
    start_time = time.time()
    fps_time = start_time
    
    try:
        while True:
            # 读取一帧
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 目标检测
            boxes, classes, scores, inference_time, process_time = detector.detect(
                image=frame, conf_thresh=args.conf_thres, nms_thresh=args.nms_thres)
            
            # 统计时间
            total_inference_time += inference_time
            total_process_time += process_time
            
            # 计算FPS
            current_time = time.time()
            if current_time - fps_time >= 1.0:  # 每秒更新一次FPS
                current_fps = frame_count / (current_time - start_time)
                fps_list.append(current_fps)
                fps_time = current_time
            
            # 绘制检测结果
            result_frame = visualize_detections(frame, boxes, classes, scores)
            
            # 绘制FPS
            current_fps = frame_count / (time.time() - start_time)
            result_frame = draw_fps(result_frame, current_fps)
            
            # 显示结果（如果指定了显示模式）
            if args.show:
                cv2.imshow("YOLOv8 RKNN", result_frame)
                # 按ESC键退出
                key = cv2.waitKey(1)
                if key == 27:
                    break
            
            # 保存视频
            if video_writer is not None:
                video_writer.write(result_frame)
    
    except KeyboardInterrupt:
        print("用户中断")
    
    finally:
        # 计算平均时间和FPS
        if frame_count > 0:
            avg_inference_time = total_inference_time / frame_count
            avg_process_time = total_process_time / frame_count
            avg_fps = frame_count / (time.time() - start_time)
            
            print(f"\n处理完成 {frame_count} 帧")
            print(f"平均推理时间: {avg_inference_time:.2f}ms")
            print(f"平均后处理时间: {avg_process_time:.2f}ms")
            print(f"平均总时间: {avg_inference_time + avg_process_time:.2f}ms")
            print(f"平均FPS: {avg_fps:.2f}")
        
        # 释放资源
        cap.release()
        if video_writer is not None:
            video_writer.release()
        detector.release()
        if args.show:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()