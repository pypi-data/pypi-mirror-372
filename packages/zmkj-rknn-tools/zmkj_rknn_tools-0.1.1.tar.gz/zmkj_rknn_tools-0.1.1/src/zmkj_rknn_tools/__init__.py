# RKNN-Tools: 瑞芯微端侧的辅助快速验证工具
"""
ZMKJ RKNN Tools - 瑞芯微端侧的辅助快速验证工具

这是一个专为瑞芯微（Rockchip）芯片设计的端侧推理辅助工具包，
旨在简化模型转换、部署和验证流程。

主要功能:
- 模型转换：支持 YOLOv8 模型到 RKNN 的转换流程
- 推理引擎：高效的 RKNN 模型推理实现
- 后处理优化：针对 YOLOv8 的高效后处理算法
- 可视化工具：集成 supervision 库的可视化功能
- 命令行工具：便捷的 CLI 工具

安装:
    pip install zmkj-rknn-tools[all]

基本用法:
    from zmkj_rknn_tools import YOLOv8Detector, update_config
    
    # 配置参数
    update_config({'obj_thresh': 0.25, 'nms_thresh': 0.45})
    
    # 初始化检测器
    detector = YOLOv8Detector('model.rknn')
    
    # 执行检测
    boxes, classes, scores, inf_time, proc_time = detector.detect(image)
"""

__version__ = '0.1.1'
__author__ = '壹世朱名'
__email__ = 'nx740@qq.com'
__license__ = 'MIT'

# 导入主要模块，方便用户直接使用
from zmkj_rknn_tools.config import get_config, update_config

# 条件导入，避免在没有安装相应依赖时出错
try:
    from zmkj_rknn_tools.detector import YOLOv8Detector
except ImportError:
    # 如果没有安装 RKNN 相关依赖，提供友好的错误提示
    def YOLOv8Detector(*args, **kwargs):
        raise ImportError(
            "YOLOv8Detector requires RKNN dependencies. "
            "Please install with: pip install zmkj-rknn-tools[rknn]"
        )

try:
    from zmkj_rknn_tools.converter import onnx_to_rknn, pt_to_onnx
except ImportError:
    # 如果没有安装转换相关依赖，提供友好的错误提示
    def pt_to_onnx(*args, **kwargs):
        raise ImportError(
            "Model conversion requires additional dependencies. "
            "Please install with: pip install zmkj-rknn-tools[yolo]"
        )
    
    def onnx_to_rknn(*args, **kwargs):
        raise ImportError(
            "Model conversion requires RKNN dependencies. "
            "Please install with: pip install zmkj-rknn-tools[rknn]"
        )

# 导入数据管理功能
from zmkj_rknn_tools.data import (
    get_example_data_path,
    get_bus_image,
    get_people_walking_image,
    check_examples_data_available,
    suggest_data_installation,
    download_sample_model,
)

# 公开的 API
__all__ = [
    '__version__',
    '__author__',
    '__email__',
    '__license__',
    'get_config',
    'update_config',
    'YOLOv8Detector',
    'pt_to_onnx',
    'onnx_to_rknn',
    'get_example_data_path',
    'get_bus_image',
    'get_people_walking_image',
    'check_examples_data_available',
    'suggest_data_installation',
    'download_sample_model',
]