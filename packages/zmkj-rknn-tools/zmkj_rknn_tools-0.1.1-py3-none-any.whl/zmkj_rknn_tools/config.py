# -*- coding: utf-8 -*-
"""
配置模块 - 管理全局配置参数

该模块提供了一个统一的配置管理接口，用于设置和获取RKNN-Tools的全局配置参数。
这些参数影响模型转换、推理、后处理和可视化等功能的行为。
"""

# 默认配置参数
_CONFIG = {
    'obj_thresh': 0.25,       # 目标检测阈值（模型后处理使用）
    'nms_thresh': 0.45,        # 非极大值抑制阈值
    'img_size': (640, 640),    # 输入图像尺寸 (width, height)
    'map_test': False,         # 是否为map测试模式
    'vis_thresh': 0.25,        # 可视化置信度阈值
    'use_fast_nms': True,      # 使用快速NMS算法
    'use_parallel': True,      # 使用并行处理
    'downscale_factor': 2,     # 高分辨率图像下采样因子
    'skip_frames': 0,          # 跳帧处理（0表示不跳帧）
    'cache_size': 10,          # 缓存大小
    'max_nms_boxes': 1000,     # NMS处理的最大框数量
    'verbose': True,           # 是否输出详细日志
    'log_level': 'INFO',       # 日志级别
}

# 如果是map测试模式，使用不同的阈值
if _CONFIG['map_test']:
    _CONFIG['obj_thresh'] = 0.001  # 使用非常低的阈值以获取更多检测框
    _CONFIG['nms_thresh'] = 0.65   # 使用较高的NMS阈值以保留更多重叠框
    _CONFIG['vis_thresh'] = 0.001  # 可视化阈值也设为相同的低值


def update_config(config_dict):
    """
    更新配置参数
    
    Args:
        config_dict: 包含配置参数的字典
        
    Returns:
        更新后的配置字典
    """
    global _CONFIG
    
    # 验证配置参数
    for key, value in config_dict.items():
        if key not in _CONFIG:
            raise ValueError(f"未知的配置参数: {key}")
    
    # 更新配置
    _CONFIG.update(config_dict)
    
    # 如果是map测试模式，自动调整相关阈值
    if config_dict.get('map_test', False):
        _CONFIG['obj_thresh'] = 0.001
        _CONFIG['nms_thresh'] = 0.65
        _CONFIG['vis_thresh'] = 0.001
    
    return _CONFIG


def get_config(key=None, default=None):
    """
    获取配置参数
    
    Args:
        key: 配置参数名称，如果为None则返回所有配置
        default: 默认值，当key不存在时返回此值
        
    Returns:
        配置参数值或所有配置字典
    """
    if key is None:
        return _CONFIG.copy()
    
    if key not in _CONFIG:
        if default is not None:
            return default
        raise ValueError(f"未知的配置参数: {key}")
    
    return _CONFIG[key]