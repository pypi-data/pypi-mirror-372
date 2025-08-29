"""
数据文件管理模块

提供示例数据文件的访问和下载功能。
"""


import os
from pathlib import Path
from typing import Optional, Union
import warnings
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging._nameToLevel["WARNING"] = 30  # 强行注册

def get_example_data_path(filename: str) -> Optional[Path]:
    """
    获取示例数据文件路径
    
    Args:
        filename: 文件名
        
    Returns:
        文件路径，如果文件不存在则返回 None
    """
    try:
        # 尝试从数据包获取
        from zmkj_rknn_examples_data import get_data_path
        path = get_data_path(filename)
        if path.exists():
            return path
    except ImportError:
        pass
    
    # 尝试从当前目录获取
    current_dir = Path.cwd()
    local_path = current_dir / filename
    if local_path.exists():
        return local_path
    
    # 尝试从示例目录获取
    examples_dir = Path(__file__).parent / "examples"
    example_path = examples_dir / filename
    if example_path.exists():
        return example_path
    
    return None


def get_bus_image() -> Optional[Path]:
    """获取公交车示例图像路径"""
    return get_example_data_path("bus.jpg")


def get_people_walking_image() -> Optional[Path]:
    """获取行人示例图像路径"""
    return get_example_data_path("people-walking.jpg")


def check_examples_data_available() -> bool:
    """检查示例数据是否可用"""
    try:
        import zmkj_rknn_examples_data
        return True
    except ImportError:
        return False


def suggest_data_installation():
    """提示用户安装示例数据"""
    if not check_examples_data_available():
        warnings.warn(
            "示例数据包未安装。请运行以下命令安装：\n"
            "pip install zmkj-rknn-tools[examples-data]\n"
            "或者手动下载示例文件到当前目录。",
            UserWarning
        )


def download_sample_model(model_name: str = "yolov8s.pt", output_dir: Union[str, Path] = ".") -> Path:
    """
    下载示例模型文件
    
    Args:
        model_name: 模型名称
        output_dir: 输出目录
        
    Returns:
        下载的文件路径
    """
    output_dir = Path(output_dir)
    output_path = output_dir / model_name
    
    if output_path.exists():
        logging.info(f"模型文件已存在: {output_path}")
        return output_path
    
    logging.info(f"正在下载 {model_name}...")
    
    if model_name.startswith("yolov8"):
        try:
            from ultralytics import YOLO
            # 使用 ultralytics 下载模型
            model = YOLO(model_name)
            # 模型会自动下载到 ultralytics 缓存目录
            # 我们需要复制到指定位置
            import shutil
            cache_path = Path.home() / ".ultralytics" / "models" / model_name
            if cache_path.exists():
                shutil.copy2(cache_path, output_path)
                logging.info(f"模型已下载到: {output_path}")
                return output_path
        except ImportError:
            logging.info("需要安装 ultralytics: pip install zmkj-rknn-tools[yolo]")
        except Exception as e:
            logging.info(f"下载失败: {e}")
    
    # 提供手动下载链接
    urls = {
        "yolov8s.pt": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt",
        "yolov8n.pt": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
        "yolov8m.pt": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8m.pt",
    }
    
    if model_name in urls:
        logging.info(f"请手动下载模型文件:")
        logging.info(f"wget {urls[model_name]} -O {output_path}")
    
    return output_path