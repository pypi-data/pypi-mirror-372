# -*- coding: utf-8 -*-
"""
后处理模块 - 处理模型输出并生成最终的检测结果

该模块包含YOLOv8模型输出的后处理功能，包括：
1. 分布式焦点损失(DFL)解码
2. 边界框坐标处理
3. 非极大值抑制(NMS)
4. 并行处理优化

这些功能被优化以提高处理速度和内存效率。
"""

import numpy as np
import logging
import traceback
import concurrent.futures
import time
from .config import get_config

# 移除性能分析工具导入

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def dfl(position):
    """
    分布式焦点损失 (Distribution Focal Loss) 后处理
    
    高度优化版本：使用预分配数组、就地操作和数值稳定的softmax
    
    将离散的分布转换为连续值，用于边界框回归
    
    Args:
        position: 模型输出的位置编码
        
    Returns:
        numpy数组: 解码后的位置值
    """
    # 提前检查输入数据有效性
    if position is None or position.size == 0:
        return np.array([])
    
    n, c, h, w = position.shape
    p_num = 4  # 位置参数数量
    mc = c // p_num  # 每个位置参数的分布数量
    
    # 使用缓存避免重复创建加权矩阵和预分配数组
    if not hasattr(dfl, "cache"):
        dfl.cache = {}
    
    cache_key = (mc, n, h, w)
    if cache_key not in dfl.cache:
        # 创建加权矩阵
        weight_matrix = np.arange(mc, dtype=np.float32).reshape(1, 1, mc, 1, 1)
        # 预分配工作数组
        y_reshaped = np.empty((n, p_num, mc, h, w), dtype=np.float32)
        y_max = np.empty((n, p_num, 1, h, w), dtype=np.float32)
        y_exp = np.empty((n, p_num, mc, h, w), dtype=np.float32)
        y_sum = np.empty((n, p_num, 1, h, w), dtype=np.float32)
        result = np.empty((n, p_num, h, w), dtype=np.float32)
        
        dfl.cache[cache_key] = (weight_matrix, y_reshaped, y_max, y_exp, y_sum, result)
    
    weight_matrix, y_reshaped, y_max, y_exp, y_sum, result = dfl.cache[cache_key]
    
    # 重塑数组 - 使用预分配的数组
    y_reshaped[:] = position.reshape(n, p_num, mc, h, w)
    
    # 数值稳定的softmax实现 - 使用就地操作
    np.max(y_reshaped, axis=2, keepdims=True, out=y_max)
    np.subtract(y_reshaped, y_max, out=y_exp)
    np.exp(y_exp, out=y_exp)
    np.sum(y_exp, axis=2, keepdims=True, out=y_sum)
    np.divide(y_exp, y_sum, out=y_exp)  # y_exp现在是softmax结果
    
    # 计算加权和 - 使用就地操作
    np.multiply(y_exp, weight_matrix, out=y_exp)
    np.sum(y_exp, axis=2, out=result)
    
    return result.copy()  # 返回副本以避免缓存污染


def box_process(position):
    """
    处理模型输出的位置编码，转换为边界框坐标
    
    高度优化版本：使用预分配数组、就地操作和缓存机制
    
    Args:
        position: 模型输出的位置编码
        
    Returns:
        numpy数组: 格式为[x1, y1, x2, y2]的边界框坐标
    """
    # 提前检查输入数据有效性
    if position is None or position.size == 0:
        return np.array([])
    
    # 获取特征图尺寸
    n, c, grid_h, grid_w = position.shape
    
    # 使用缓存避免重复计算网格和预分配工作数组
    # 缓存管理
    if not hasattr(box_process, "cache"):
        box_process.cache = {}
    
    cache_key = (n, grid_h, grid_w)
    if cache_key not in box_process.cache:
        # 创建网格 - 只在第一次调用或尺寸变化时计算
        col, row = np.meshgrid(np.arange(0, grid_w, dtype=np.float32), 
                             np.arange(0, grid_h, dtype=np.float32))
        col = col.reshape(1, 1, grid_h, grid_w)
        row = row.reshape(1, 1, grid_h, grid_w)
        grid = np.concatenate((col, row), axis=1)
        
        # 计算步长
        img_height, img_width = get_config('img_size')[1], get_config('img_size')[0]
        stride = np.array([img_width//grid_w, img_height//grid_h], dtype=np.float32).reshape(1, 2, 1, 1)
        
        # 预分配工作数组
        box_xy = np.empty((n, 2, grid_h, grid_w), dtype=np.float32)
        box_xy2 = np.empty((n, 2, grid_h, grid_w), dtype=np.float32)
        result = np.empty((n, 4, grid_h, grid_w), dtype=np.float32)
        
        # 缓存所有数据
        box_process.cache[cache_key] = (grid, stride, box_xy, box_xy2, result)
    
    grid, stride, box_xy, box_xy2, result = box_process.cache[cache_key]
    
    # 应用DFL解码
    position_decoded = dfl(position)
    
    # 计算边界框坐标 - 使用就地操作
    # box_xy = grid + 0.5 - position_decoded[:, 0:2, :, :]
    np.add(grid, 0.5, out=box_xy)
    np.subtract(box_xy, position_decoded[:, 0:2, :, :], out=box_xy)
    
    # box_xy2 = grid + 0.5 + position_decoded[:, 2:4, :, :]
    np.add(grid, 0.5, out=box_xy2)
    np.add(box_xy2, position_decoded[:, 2:4, :, :], out=box_xy2)
    
    # 应用步长并合并坐标 - 使用就地操作
    # 应用步长
    np.multiply(box_xy, stride, out=result[:, 0:2, :, :])
    np.multiply(box_xy2, stride, out=result[:, 2:4, :, :])
    
    return result.copy()  # 返回副本以避免缓存污染


def filter_boxes(boxes, box_confidences, box_class_probs):
    """
    根据置信度阈值过滤检测框
    
    高度优化版本：使用高效数据类型、预分配数组和就地操作
    
    Args:
        boxes: 边界框坐标
        box_confidences: 边界框置信度
        box_class_probs: 类别概率
        
    Returns:
        boxes: 过滤后的边界框 (float32)
        classes: 过滤后的类别 (int32)
        scores: 过滤后的得分 (float32)
    """
    # 提前检查输入数据有效性
    if boxes.size == 0 or box_confidences.size == 0 or box_class_probs.size == 0:
        return (np.array([], dtype=np.float32), 
                np.array([], dtype=np.int32), 
                np.array([], dtype=np.float32))
    
    # 确保输入数据类型一致性
    if boxes.dtype != np.float32:
        boxes = boxes.astype(np.float32, copy=False)
    if box_confidences.dtype != np.float32:
        box_confidences = box_confidences.astype(np.float32, copy=False)
    if box_class_probs.dtype != np.float32:
        box_class_probs = box_class_probs.astype(np.float32, copy=False)
    
    # 重塑置信度数组 - 使用视图而不是复制
    box_confidences = box_confidences.reshape(-1)
    
    # 使用缓存预分配工作数组
    total_boxes = len(box_confidences)
    if not hasattr(filter_boxes, "cache"):
        filter_boxes.cache = {}
    
    cache_key = total_boxes
    if cache_key not in filter_boxes.cache:
        # 预分配工作数组
        class_max_score = np.empty(total_boxes, dtype=np.float32)
        classes = np.empty(total_boxes, dtype=np.int32)
        final_scores = np.empty(total_boxes, dtype=np.float32)
        mask = np.empty(total_boxes, dtype=bool)
        
        filter_boxes.cache[cache_key] = (class_max_score, classes, final_scores, mask)
    
    class_max_score, classes, final_scores, mask = filter_boxes.cache[cache_key]
    
    # 使用NumPy的向量化操作获取每个框的最高类别得分和对应的类别 - 就地操作
    np.max(box_class_probs, axis=-1, out=class_max_score)
    np.argmax(box_class_probs, axis=-1, out=classes)
    
    # 计算最终得分并根据阈值过滤 - 使用就地操作
    np.multiply(class_max_score, box_confidences, out=final_scores)
    np.greater_equal(final_scores, get_config('obj_thresh'), out=mask)
    
    # 如果没有框通过过滤，返回空数组
    if not np.any(mask):
        return (np.array([], dtype=np.float32), 
                np.array([], dtype=np.int32), 
                np.array([], dtype=np.float32))
    
    # 应用过滤 - 直接返回过滤后的结果，确保数据类型
    filtered_boxes = boxes[mask].astype(np.float32, copy=False)
    filtered_classes = classes[mask].astype(np.int32, copy=False)
    filtered_scores = final_scores[mask].astype(np.float32, copy=False)
    
    return filtered_boxes, filtered_classes, filtered_scores


def fast_nms(boxes, scores, iou_threshold=None):
    """
    高度优化的快速非极大值抑制算法
    
    使用高效数据类型、预分配数组和就地操作，减少内存分配和数据拷贝
    
    Args:
        boxes: 边界框坐标，格式为 [x1, y1, x2, y2]
        scores: 对应的置信度得分
        iou_threshold: IoU阈值，如果为None则使用CONFIG['nms_thresh']
        
    Returns:
        keep: 保留的边界框索引数组 (int32)
    """
    if iou_threshold is None:
        iou_threshold = np.float32(get_config('nms_thresh'))
    else:
        iou_threshold = np.float32(iou_threshold)
        
    # 提前检查输入数据有效性
    if len(boxes) == 0 or len(scores) == 0:
        return np.array([], dtype=np.int32)
    
    # 如果只有一个框，直接返回其索引
    if len(boxes) == 1:
        return np.array([0], dtype=np.int32)
    
    # 确保输入数据类型一致性
    if boxes.dtype != np.float32:
        boxes = boxes.astype(np.float32, copy=False)
    if scores.dtype != np.float32:
        scores = scores.astype(np.float32, copy=False)
    
    # 限制处理的框数量，避免过度计算
    max_boxes = get_config('max_nms_boxes', 1000)
    if len(boxes) > max_boxes:
        # 只保留得分最高的框
        top_indices = np.argpartition(scores, -max_boxes)[-max_boxes:].astype(np.int32)
        boxes = boxes[top_indices]
        scores = scores[top_indices]
        order_mapping = top_indices
    else:
        order_mapping = np.arange(len(boxes), dtype=np.int32)
    
    # 按得分降序排序
    order = scores.argsort()[::-1].astype(np.int32)
    
    # 预分配工作数组
    num_boxes = len(order)
    if not hasattr(fast_nms, "cache"):
        fast_nms.cache = {}
    
    cache_key = num_boxes
    if cache_key not in fast_nms.cache:
        # 预分配工作数组
        xx1 = np.empty(num_boxes, dtype=np.float32)
        yy1 = np.empty(num_boxes, dtype=np.float32)
        xx2 = np.empty(num_boxes, dtype=np.float32)
        yy2 = np.empty(num_boxes, dtype=np.float32)
        w = np.empty(num_boxes, dtype=np.float32)
        h = np.empty(num_boxes, dtype=np.float32)
        inter = np.empty(num_boxes, dtype=np.float32)
        remaining_areas = np.empty(num_boxes, dtype=np.float32)
        iou = np.empty(num_boxes, dtype=np.float32)
        keep_mask = np.empty(num_boxes, dtype=bool)
        
        fast_nms.cache[cache_key] = (xx1, yy1, xx2, yy2, w, h, inter, remaining_areas, iou, keep_mask)
    
    xx1, yy1, xx2, yy2, w, h, inter, remaining_areas, iou, keep_mask = fast_nms.cache[cache_key]
    
    # 预分配keep数组
    keep = []
    
    # 使用更高效的逐步NMS
    while len(order) > 0:
        # 选择得分最高的框
        i = order[0]
        keep.append(i)
        
        if len(order) == 1:
            break
            
        # 计算当前框与剩余框的IoU - 使用就地操作
        current_box = boxes[i]
        remaining_boxes = boxes[order[1:]]
        remaining_count = len(remaining_boxes)
        
        # 使用预分配数组进行计算
        np.maximum(current_box[0], remaining_boxes[:, 0], out=xx1[:remaining_count])
        np.maximum(current_box[1], remaining_boxes[:, 1], out=yy1[:remaining_count])
        np.minimum(current_box[2], remaining_boxes[:, 2], out=xx2[:remaining_count])
        np.minimum(current_box[3], remaining_boxes[:, 3], out=yy2[:remaining_count])
        
        np.subtract(xx2[:remaining_count], xx1[:remaining_count], out=w[:remaining_count])
        np.subtract(yy2[:remaining_count], yy1[:remaining_count], out=h[:remaining_count])
        np.maximum(0.0, w[:remaining_count], out=w[:remaining_count])
        np.maximum(0.0, h[:remaining_count], out=h[:remaining_count])
        np.multiply(w[:remaining_count], h[:remaining_count], out=inter[:remaining_count])
        
        # 计算面积
        current_area = np.float32((current_box[2] - current_box[0]) * (current_box[3] - current_box[1]))
        np.subtract(remaining_boxes[:, 2], remaining_boxes[:, 0], out=w[:remaining_count])
        np.subtract(remaining_boxes[:, 3], remaining_boxes[:, 1], out=h[:remaining_count])
        np.multiply(w[:remaining_count], h[:remaining_count], out=remaining_areas[:remaining_count])
        
        # 计算IoU
        np.add(current_area, remaining_areas[:remaining_count], out=iou[:remaining_count])
        np.subtract(iou[:remaining_count], inter[:remaining_count], out=iou[:remaining_count])
        np.add(iou[:remaining_count], 1e-10, out=iou[:remaining_count])
        np.divide(inter[:remaining_count], iou[:remaining_count], out=iou[:remaining_count])
        
        # 保留IoU小于阈值的框
        np.less_equal(iou[:remaining_count], iou_threshold, out=keep_mask[:remaining_count])
        keep_indices = np.where(keep_mask[:remaining_count])[0]
        order = order[keep_indices + 1]
    
    # 映射回原始索引
    keep = order_mapping[keep].astype(np.int32)
    
    return keep


def nms_boxes(boxes, scores):
    """
    非极大值抑制 (NMS) 算法实现
    
    优化版本：提高计算效率，减少内存使用，处理边界情况
    根据配置选择标准NMS或快速NMS
    
    Args:
        boxes: 边界框坐标，格式为 [x1, y1, x2, y2]
        scores: 对应的置信度得分
        
    Returns:
        keep: 保留的边界框索引数组
    """
    # 使用快速NMS
    if get_config('use_fast_nms'):
        return fast_nms(boxes, scores)
    
    # 提前检查输入数据有效性
    if len(boxes) == 0 or len(scores) == 0:
        return np.array([], dtype=np.int32)
    
    # 如果只有一个框，直接返回其索引
    if len(boxes) == 1:
        return np.array([0], dtype=np.int32)
    
    # 确保boxes是float类型，避免整数溢出
    if boxes.dtype != np.float32 and boxes.dtype != np.float64:
        boxes = boxes.astype(np.float32)
    
    # 按得分降序排序
    order = scores.argsort()[::-1]
    boxes = boxes[order]
    
    # 计算所有框的面积
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    
    # 预分配keep数组
    keep = []
    
    # 标准NMS实现
    while order.size > 0:
        i = order[0]
        keep.append(i)
        
        # 计算当前框与剩余框的IoU
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        
        ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-10)
        
        # 获取IoU小于阈值的框的索引
        inds = np.where(ovr <= get_config('nms_thresh'))[0]
        
        # 更新order
        order = order[inds + 1]
    
    return np.array(keep)


def post_process_parallel(input_data, conf_thresh=None, nms_thresh=None):
    """
    高度优化的并行处理模型输出，生成最终的检测结果
    
    使用线程池并行处理不同分支的输出，采用高效数据类型和预分配数组
    
    Args:
        input_data: 模型的原始输出
        conf_thresh: 置信度阈值，如果为None则使用CONFIG['obj_thresh']
        nms_thresh: NMS阈值，如果为None则使用CONFIG['nms_thresh']
        
    Returns:
        boxes: 边界框坐标 [x1, y1, x2, y2] (float32)
        classes: 类别索引 (int32)
        scores: 置信度得分 (float32)
    """
    # 提前检查输入数据有效性
    if not input_data or len(input_data) == 0:
        return None, None, None
    
    # 如果提供了自定义阈值，临时更新CONFIG
    from .config import update_config, get_config
    original_config = get_config()
    if conf_thresh is not None or nms_thresh is not None:
        new_config = {}
        if conf_thresh is not None:
            new_config['obj_thresh'] = np.float32(conf_thresh)  # 使用float32
        if nms_thresh is not None:
            new_config['nms_thresh'] = np.float32(nms_thresh)  # 使用float32
        update_config(new_config)
    
    try:
        start_time = time.time()  # 记录整个函数开始时间
        # YOLOv8输出处理参数
        default_branch = 3
        pair_per_branch = len(input_data) // default_branch
        
        # 预估总数据量，预分配工作数组
        estimated_total = default_branch * 8400  # 估算总检测框数量
        
        # 使用缓存预分配大数组
        if not hasattr(post_process_parallel, "cache"):
            post_process_parallel.cache = {}
        
        cache_key = estimated_total
        if cache_key not in post_process_parallel.cache:
            # 预分配工作数组，使用高效数据类型
            temp_boxes = np.empty((estimated_total, 4), dtype=np.float32)
            temp_classes_conf = np.empty((estimated_total, 80), dtype=np.float32)  # 假设80类
            temp_scores = np.empty((estimated_total, 1), dtype=np.float32)
            valid_mask = np.empty(estimated_total, dtype=bool)
            
            post_process_parallel.cache[cache_key] = (temp_boxes, temp_classes_conf, temp_scores, valid_mask)
        
        temp_boxes, temp_classes_conf, temp_scores, valid_mask = post_process_parallel.cache[cache_key]
        
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 提交任务处理每个分支
            futures = []
            for i in range(default_branch):
                box_data = input_data[pair_per_branch * i]
                cls_data = input_data[pair_per_branch * i + 1]
                futures.append(executor.submit(process_branch, box_data, cls_data))
            
            # 收集结果到预分配数组
            current_idx = 0
            for future in concurrent.futures.as_completed(futures):
                box_flat, cls_flat, score_flat = future.result()
                if len(box_flat) > 0:
                    end_idx = current_idx + len(box_flat)
                    if end_idx <= estimated_total:
                        # 确保数据类型一致性
                        temp_boxes[current_idx:end_idx] = box_flat.astype(np.float32, copy=False)
                        temp_classes_conf[current_idx:end_idx] = cls_flat.astype(np.float32, copy=False)
                        temp_scores[current_idx:end_idx] = score_flat.astype(np.float32, copy=False)
                        current_idx = end_idx
        
        # 合并所有分支的结果
        if current_idx == 0:
            # 恢复原始配置
            if conf_thresh is not None or nms_thresh is not None:
                update_config(original_config)
            return None, None, None
        
        # 使用实际数据切片，避免复制
        boxes = temp_boxes[:current_idx]
        classes_conf = temp_classes_conf[:current_idx]
        scores = temp_scores[:current_idx]
        # 根据阈值过滤检测框
        boxes, classes, scores = filter_boxes(boxes, scores, classes_conf)
        
        # 如果没有检测到物体，直接返回
        if len(classes) == 0 or len(boxes) == 0:
            # 恢复原始配置
            if conf_thresh is not None or nms_thresh is not None:
                update_config(original_config)
            return None, None, None
        
        # 使用NumPy的unique获取唯一类别，比set()更高效
        unique_classes = np.unique(classes.astype(np.int32, copy=False))
        
        # 预分配结果数组的估计大小，使用高效数据类型
        est_size = min(len(boxes), len(unique_classes) * 10)  # 假设每个类别平均保留10个框
        result_boxes = np.empty((est_size, 4), dtype=np.float32)
        result_classes = np.empty(est_size, dtype=np.int32)
        result_scores = np.empty(est_size, dtype=np.float32)
        
        # 对每个类别应用NMS
        idx = 0
        for c in unique_classes:
            # 使用布尔索引获取当前类别的所有检测框
            mask = (classes == c)
            if not np.any(mask):
                continue
                
            b = boxes[mask].astype(np.float32, copy=False)
            s = scores[mask].astype(np.float32, copy=False)
            
            # 应用NMS
            keep = nms_boxes(b, s)
            keep_count = len(keep)
            
            if keep_count > 0:
                # 直接写入预分配的结果数组
                if idx + keep_count > est_size:
                    # 如果预分配空间不足，扩展数组
                    new_size = idx + keep_count
                    result_boxes.resize((new_size, 4), refcheck=False)
                    result_classes.resize(new_size, refcheck=False)
                    result_scores.resize(new_size, refcheck=False)
                
                result_boxes[idx:idx+keep_count] = b[keep]
                result_classes[idx:idx+keep_count] = np.int32(c)
                result_scores[idx:idx+keep_count] = s[keep]
                idx += keep_count
        
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        # 如果没有检测结果
        if idx == 0:
            return None, None, None
        
        # 裁剪结果数组到实际大小，确保数据类型
        return (result_boxes[:idx].astype(np.float32, copy=False), 
                result_classes[:idx].astype(np.int32, copy=False), 
                result_scores[:idx].astype(np.float32, copy=False))
        
    except Exception as e:
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        logging.error(f"并行后处理错误: {e}")
        traceback.print_exc()
        return None, None, None


def process_branch(box_data, cls_data):
    """
    高度优化的单个分支输出处理
    
    使用预分配数组和就地操作，减少内存分配和数据拷贝
    
    Args:
        box_data: 边界框数据
        cls_data: 类别数据
        
    Returns:
        box_flat: 展平的边界框坐标
        cls_flat: 展平的类别概率
        score_flat: 展平的置信度得分
    """
    # 处理边界框坐标
    box_processed = box_process(box_data)
    
    # 获取形状信息
    n, ch_box, h, w = box_processed.shape
    _, ch_cls, _, _ = cls_data.shape
    total_elements = n * h * w
    
    # 使用缓存预分配输出数组
    if not hasattr(process_branch, "cache"):
        process_branch.cache = {}
    
    cache_key = (total_elements, ch_box, ch_cls)
    if cache_key not in process_branch.cache:
        # 预分配输出数组
        box_flat = np.empty((total_elements, ch_box), dtype=np.float32)
        cls_flat = np.empty((total_elements, ch_cls), dtype=np.float32)
        score_flat = np.ones((total_elements, 1), dtype=np.float32)
        
        process_branch.cache[cache_key] = (box_flat, cls_flat, score_flat)
    
    box_flat, cls_flat, score_flat = process_branch.cache[cache_key]
    
    # 高效的数组重塑操作 - 使用连续内存布局
    # 直接重塑到预分配的数组，减少transpose操作
    box_reshaped = box_processed.reshape(n, ch_box, h * w).transpose(0, 2, 1).reshape(-1, ch_box)
    cls_reshaped = cls_data.reshape(n, ch_cls, h * w).transpose(0, 2, 1).reshape(-1, ch_cls)
    
    # 就地复制到缓存数组
    box_flat[:] = box_reshaped
    cls_flat[:] = cls_reshaped
    
    # 返回副本以避免缓存污染
    return box_flat.copy(), cls_flat.copy(), score_flat.copy()


def post_process(input_data, conf_thresh=None, nms_thresh=None):
    """
    处理模型输出，生成最终的检测结果
    
    高度优化版本：专注于只返回boxes、classes和scores三个值，
    减少内存分配和复制，提高处理速度
    根据配置选择并行或串行处理
    
    Args:
        input_data: 模型的原始输出
        conf_thresh: 置信度阈值，如果为None则使用CONFIG['obj_thresh']
        nms_thresh: NMS阈值，如果为None则使用CONFIG['nms_thresh']
        
    Returns:
        boxes: 边界框坐标 [x1, y1, x2, y2]
        classes: 类别索引
        scores: 置信度得分
    """
    
    # 如果提供了自定义阈值，临时更新CONFIG
    from .config import update_config, get_config
    original_config = get_config()
    
    # 使用并行处理
    if get_config('use_parallel'):
        result = post_process_parallel(input_data, conf_thresh, nms_thresh)
        return result
    
    # 提前检查输入数据有效性
    if not input_data or len(input_data) == 0:
        return None, None, None
    if conf_thresh is not None or nms_thresh is not None:
        new_config = {}
        if conf_thresh is not None:
            new_config['obj_thresh'] = conf_thresh
        if nms_thresh is not None:
            new_config['nms_thresh'] = nms_thresh
        update_config(new_config)
        
    # YOLOv8输出处理参数
    default_branch = 3
    pair_per_branch = len(input_data) // default_branch
    
    # 使用NumPy的向量化操作处理数据
    try:
        # 预分配内存并直接处理每个分支的输出
        branch_start = time.time()
        boxes_list = []
        classes_conf_list = []
        scores_list = []
        
        for i in range(default_branch):
            # 处理边界框坐标
            box_start = time.time()
            box_data = input_data[pair_per_branch * i]
            box_processed = box_process(box_data)
            box_time = time.time() - box_start
            logging.debug(f"分支{i}边界框处理耗时: {box_time*1000:.2f}ms")
            
            # 处理类别概率和置信度
            cls_data = input_data[pair_per_branch * i + 1]
            
            # 转换和展平数据 - 内联以减少函数调用
            ch_box = box_processed.shape[1]
            box_flat = box_processed.transpose(0, 2, 3, 1).reshape(-1, ch_box)
            boxes_list.append(box_flat)
            
            ch_cls = cls_data.shape[1]
            cls_flat = cls_data.transpose(0, 2, 3, 1).reshape(-1, ch_cls)
            classes_conf_list.append(cls_flat)
            
            # 创建置信度得分并展平 (使用ones_like的切片视图避免额外内存分配)
            score_flat = np.ones((cls_flat.shape[0], 1), dtype=np.float32)
            scores_list.append(score_flat)
        
        # 合并所有分支的结果
        boxes = np.concatenate(boxes_list)
        classes_conf = np.concatenate(classes_conf_list)
        scores = np.concatenate(scores_list)
        
        # 清理不再需要的变量以释放内存
        del boxes_list, classes_conf_list, scores_list, box_processed, cls_data
        
        # 根据阈值过滤检测框
        boxes, classes, scores = filter_boxes(boxes, scores, classes_conf)
        del classes_conf  # 立即释放不再需要的大数组
        
        # 如果没有检测到物体，直接返回
        if len(classes) == 0 or len(boxes) == 0:
            # 恢复原始配置
            if conf_thresh is not None or nms_thresh is not None:
                update_config(original_config)
            return None, None, None
        
        # 使用NumPy的unique获取唯一类别，比set()更高效
        unique_classes = np.unique(classes)
        
        # 预分配结果数组的估计大小
        est_size = min(len(boxes), len(unique_classes) * 10)  # 假设每个类别平均保留10个框
        result_boxes = np.zeros((est_size, 4), dtype=boxes.dtype)
        result_classes = np.zeros(est_size, dtype=classes.dtype)
        result_scores = np.zeros(est_size, dtype=scores.dtype)
        
        # 对每个类别应用NMS
        idx = 0
        for c in unique_classes:
            # 使用布尔索引获取当前类别的所有检测框
            mask = (classes == c)
            if not np.any(mask):
                continue
                
            b = boxes[mask]
            s = scores[mask]
            
            # 应用NMS
            keep = nms_boxes(b, s)
            keep_count = len(keep)
            
            if keep_count > 0:
                # 直接写入预分配的结果数组
                if idx + keep_count > est_size:
                    # 如果预分配空间不足，扩展数组
                    new_size = idx + keep_count
                    result_boxes.resize((new_size, 4), refcheck=False)
                    result_classes.resize(new_size, refcheck=False)
                    result_scores.resize(new_size, refcheck=False)
                
                result_boxes[idx:idx+keep_count] = b[keep]
                result_classes[idx:idx+keep_count] = c
                result_scores[idx:idx+keep_count] = s[keep]
                idx += keep_count
        
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        # 如果没有检测结果
        if idx == 0:
            return None, None, None
        
        # 裁剪结果数组到实际大小
        return result_boxes[:idx], result_classes[:idx], result_scores[:idx]
        
    except Exception as e:
        # 恢复原始配置
        if conf_thresh is not None or nms_thresh is not None:
            update_config(original_config)
            
        logging.error(f"后处理错误: {e}")
        traceback.print_exc()
        return None, None, None