# -*- coding: utf-8 -*-
"""
检测器模块 - 封装RKNN模型的加载、推理和后处理功能

该模块提供YOLOv8RKNN检测器类，用于加载RKNN模型并执行目标检测。
检测器类支持图像预处理、模型推理、后处理和结果缓存等功能。   
"""

import os
import cv2
import time
import logging
import traceback
import numpy as np
import collections
from pathlib import Path

# 尝试导入 rknnlite，如果失败则使用模拟模块
try:
    from rknnlite.api import RKNNLite
except ImportError:
    print("Warning: rknnlite not found, using mock implementation for testing")
    from .mock_rknnlite import RKNNLite

from .config import get_config
from .postprocess import post_process

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# COCO数据集类别
CLASSES = (
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat", "traffic light",
    "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow", "elephant",
    "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
    "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork", "knife",
    "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa",
    "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
    "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
)

# COCO数据集ID映射
COCO_ID_MAP = {
    i: cid for i, cid in enumerate([
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 31, 32, 33, 34,
        35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
        64, 65, 67, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84, 85, 86, 87, 88, 89, 90
    ])
}

# 保留原始列表以兼容现有代码
coco_id_list = list(COCO_ID_MAP.values())


class YOLOv8Detector:
    """
    YOLOv8 RKNN模型检测器
    
    提供RKNN模型的加载、推理和后处理功能，不包含可视化和业务逻辑。
    增加了缓存机制、跳帧处理和图像预处理优化。
    """
    
    def __init__(self, model_path=None):
        """
        初始化YOLOv8RKNN检测器
        
        Args:
            model_path: RKNN模型路径，如果为None则不加载模型
        """
        self.rknn = None
        self.frame_count = 0
        self.result_cache = {}
        self.last_frame_hash = None
        # 使用有序字典记录缓存顺序，便于移除最旧的缓存项
        self.cache_order = collections.deque(maxlen=get_config('cache_size')) if get_config('cache_size') > 0 else None
        if model_path is not None:
            self.load_model(model_path)
    
    def load_model(self, model_path):
        """
        加载RKNN模型
        
        Args:
            model_path: RKNN模型路径
            
        Returns:
            成功返回True，失败返回False
        """
        try:
            # 初始化RKNN模型
            self.rknn = RKNNLite()
            ret = self.rknn.load_rknn(model_path)
            if ret != 0:
                logging.error(f"加载模型失败: {model_path}")
                return False
            ret = self.rknn.init_runtime(core_mask=RKNNLite.NPU_CORE_ALL)
            if ret != 0:
                logging.error("初始化运行时环境失败")
                return False
            return True
        except Exception as e:
            logging.error(f"加载模型出错: {str(e)}")
            traceback.print_exc()
            return False
    
    def compute_image_hash(self, img):
        """
        计算图像的哈希值
        
        使用图像的下采样版本计算哈希，以便快速比较图像相似度
        
        Args:
            img: 输入图像
            
        Returns:
            hash_value: 图像哈希值
        """
        # 使用更高效的哈希算法 - 感知哈希
        # 下采样图像以加快哈希计算
        small_img = cv2.resize(img, (8, 8), interpolation=cv2.INTER_AREA)
        # 转换为灰度图以减少计算量
        gray_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY) if len(small_img.shape) == 3 else small_img
        # 计算DCT变换
        dct = cv2.dct(np.float32(gray_img))
        # 取左上角8x8的低频部分
        dct_low = dct[:8, :8]
        # 计算均值
        avg = np.mean(dct_low)
        # 生成哈希值
        hash_value = 0
        for i in range(8):
            for j in range(8):
                if dct_low[i, j] > avg:
                    hash_value |= 1 << (i * 8 + j)
        return hash_value
    
    def detect(self, image=None, conf_thresh=None, nms_thresh=None):
        """
        检测图像中的目标
        
        Args:
            image: 图像数据
            conf_thresh: 置信度阈值，如果为None则使用CONFIG['obj_thresh']
            nms_thresh: NMS阈值，如果为None则使用CONFIG['nms_thresh']
            
        Returns:
            boxes: 边界框坐标 [N, 4]，格式为[x1, y1, x2, y2]
            classes: 类别ID [N]
            scores: 置信度得分 [N]
            inference_time: 推理时间(ms)
            process_time: 后处理时间(ms)
        """
        if self.rknn is None:
            logging.error("模型未加载")
            return None, None, None, 0, 0
        
        # 帧计数器增加
        self.frame_count += 1
        
        # 跳帧处理 - 如果启用跳帧且不是关键帧，返回上一帧的结果
        if get_config('skip_frames') > 0 and self.frame_count % (get_config('skip_frames') + 1) != 0:
            if self.last_frame_hash in self.result_cache:
                cached_result = self.result_cache[self.last_frame_hash]
                # 使用缓存结果，跳过帧处理
                return cached_result[0], cached_result[1], cached_result[2], 0, 0
        
        # 读取并预处理图像
        try:
            if image is not None:
                if isinstance(image, np.ndarray):
                    img_src = image.copy()  # 创建副本避免修改原始图像
                elif isinstance(x, str):
                    img_src = cv2.imread(image)
                else:
                    raise FileNotFoundError(f"image参数类型错误: {type(image)}")
            else:
                raise ValueError("必须提供image参数")
            
            # 获取原始图像尺寸
            orig_height, orig_width = img_src.shape[:2]
            
            # 计算图像哈希用于缓存 - 在下采样前计算，以便更准确地匹配原始图像
            if get_config('cache_size') > 0:
                img_hash = self.compute_image_hash(img_src)
                
                # 检查缓存
                if img_hash in self.result_cache:
                    cached_result = self.result_cache[img_hash]
                    self.last_frame_hash = img_hash
                    # 使用缓存结果，图像哈希匹配
                    return cached_result[0], cached_result[1], cached_result[2], 0, 0
                
                self.last_frame_hash = img_hash
            
            # 对高分辨率图像进行下采样处理 - 优化处理大图像的性能
            if orig_height > 720 and get_config('downscale_factor') > 1:
                # 计算下采样后的尺寸 - 确保是8的倍数，有利于GPU处理
                ds_width = (orig_width // get_config('downscale_factor')) // 8 * 8
                ds_height = (orig_height // get_config('downscale_factor')) // 8 * 8
                
                # 下采样图像 - 使用INTER_AREA插值方法更适合缩小图像
                img_src = cv2.resize(img_src, (ds_width, ds_height), interpolation=cv2.INTER_AREA)
                
                # 更新原始尺寸为下采样后的尺寸
                orig_height, orig_width = ds_height, ds_width
                
                # 记录下采样因子用于后处理
                self.downscale_factor = get_config('downscale_factor')
                # 图像下采样处理
            else:
                self.downscale_factor = 1
            
            # 调整图像尺寸到模型输入尺寸，保持宽高比
            target_width, target_height = get_config('img_size')
            
            # 计算缩放比例
            scale = min(target_width / orig_width, target_height / orig_height)
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            
            # 调整图像尺寸 - 根据缩放方向选择最佳插值方法
            if scale < 1.0:
                resized_img = cv2.resize(img_src, (new_width, new_height), interpolation=cv2.INTER_AREA)
            else:
                resized_img = cv2.resize(img_src, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            
            # 创建填充后的图像 - 使用预分配内存
            padded_img = np.full((target_height, target_width, 3), 114, dtype=np.uint8)
            
            # 计算填充位置 - 居中填充
            pad_x = (target_width - new_width) // 2
            pad_y = (target_height - new_height) // 2
            
            # 将调整后的图像放入填充图像中 - 使用切片赋值
            padded_img[pad_y:pad_y + new_height, pad_x:pad_x + new_width] = resized_img
            
            # 转换颜色空间并扩展维度 - 直接在内存中转换
            img_rgb = cv2.cvtColor(padded_img, cv2.COLOR_BGR2RGB)
            input_data = np.expand_dims(img_rgb, axis=0)
            
            # 存储缩放和填充信息用于后处理
            self.scale = scale
            self.pad_x = pad_x
            self.pad_y = pad_y
            self.orig_width = orig_width * self.downscale_factor
            self.orig_height = orig_height * self.downscale_factor
            
        except Exception as e:
            logging.error(f"图像预处理错误: {e}")
            traceback.print_exc()
            return None, None, None, 0, 0
        
        # 模型推理
        inference_start = time.time()
        outputs = self.rknn.inference(inputs=[input_data])
        inference_time = (time.time() - inference_start) * 1000
        
        if outputs is None:
            logging.error("模型推理结果为空")
            return None, None, None, inference_time, 0
        
        # 后处理
        process_start = time.time()
        boxes, classes, scores = post_process(outputs, conf_thresh, nms_thresh)
        process_time = (time.time() - process_start) * 1000
        
        if boxes is None or len(boxes) == 0:
            # 未检测到任何目标
            result = (np.array([]), np.array([]), np.array([]))
            
            # 更新缓存
            if get_config('cache_size') > 0 and self.last_frame_hash is not None:
                self.update_cache(self.last_frame_hash, result)
                    
            return result[0], result[1], result[2], inference_time, process_time
        
        # 将检测框坐标转换回原始图像空间
        if hasattr(self, 'scale'):
            # 移除填充
            boxes[:, [0, 2]] -= self.pad_x
            boxes[:, [1, 3]] -= self.pad_y
            
            # 转换回原始尺寸
            boxes = boxes / self.scale
            
            # 如果进行了下采样，需要将坐标乘以下采样因子
            if self.downscale_factor > 1:
                boxes = boxes * self.downscale_factor
            
            # 确保坐标在原始图像范围内
            boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, self.orig_width)
            boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, self.orig_height)
        
        # 更新缓存
        result = (boxes, classes, scores)
        if get_config('cache_size') > 0 and self.last_frame_hash is not None:
            self.update_cache(self.last_frame_hash, result)
        
        return boxes, classes, scores, inference_time, process_time
    
    def update_cache(self, img_hash, result):
        """
        更新结果缓存
        
        使用LRU (Least Recently Used) 策略管理缓存
        
        Args:
            img_hash: 图像哈希值
            result: 检测结果元组 (boxes, classes, scores)
        """
        # 如果缓存已满，移除最旧的项
        if len(self.result_cache) >= get_config('cache_size'):
            if len(self.cache_order) > 0:
                oldest = self.cache_order.popleft()
                if oldest in self.result_cache:
                    del self.result_cache[oldest]
        
        # 添加新项到缓存
        self.result_cache[img_hash] = result
        self.cache_order.append(img_hash)
    
    def release(self):
        """
        释放资源
        """
        if self.rknn is not None:
            self.rknn.release()
            self.rknn = None
        
        # 清空缓存
        self.result_cache.clear()
        if self.cache_order is not None:
            self.cache_order.clear()