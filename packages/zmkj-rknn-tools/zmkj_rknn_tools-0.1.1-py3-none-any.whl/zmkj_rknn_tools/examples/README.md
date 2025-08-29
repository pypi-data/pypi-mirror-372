# 示例文件说明

本目录包含 ZMKJ RKNN Tools 的使用示例。

## 示例文件

- `verify_environment.py` - 环境验证脚本
- `model_conversion.py` - 模型转换示例
- `image_inference.py` - 图像推理示例
- `video_inference.py` - 视频推理示例

## 示例数据文件

示例数据文件位于单独的数据包中，可以通过以下方式安装：

```bash
# 安装示例数据
pip install zmkj-rknn-tools[examples-data]

# 或安装完整版本
pip install zmkj-rknn-tools[full]
```

## 获取模型文件

由于模型文件较大，未包含在包中。请从以下位置下载：

### YOLOv8 模型
```bash
# 下载 YOLOv8s 模型
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt

# 或使用 ultralytics 包下载
pip install ultralytics
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
```

### 示例视频
```bash
# 下载示例视频（可选）
wget https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4 -O people-walking.mp4
```

## 运行示例

### 1. 环境验证
```bash
python verify_environment.py
# 或使用 CLI 工具
rknn-verify
```

### 2. 模型转换
```bash
# 确保有 yolov8s.pt 文件
python model_conversion.py --pt yolov8s.pt

# 或使用 CLI 工具
rknn-convert --input yolov8s.pt --output yolov8s.onnx --format onnx
rknn-convert --input yolov8s.onnx --output yolov8s.rknn --format rknn --platform rk3576
```

### 3. 图像推理
```bash
# 确保有 yolov8s.rknn 模型文件
python image_inference.py --model yolov8s.rknn --input bus.jpg

# 或使用 CLI 工具
rknn-detect --model yolov8s.rknn --input bus.jpg --output result.jpg --show
```

### 4. 视频推理
```bash
# 确保有 yolov8s.rknn 模型文件和视频文件
python video_inference.py --model yolov8s.rknn --input people-walking.mp4

# 或使用 CLI 工具
rknn-detect --model yolov8s.rknn --input people-walking.mp4 --output result.mp4
rknn-detect --model yolov8s.rknn --input 0 --show  # 摄像头
```

## 依赖安装

根据需要安装相应的依赖：

```bash
# 基础功能
pip install zmkj-rknn-tools

# RKNN 功能
pip install zmkj-rknn-tools[rknn]

# YOLOv8 支持
pip install zmkj-rknn-tools[yolo]

# 可视化功能
pip install zmkj-rknn-tools[viz]

# 所有功能
pip install zmkj-rknn-tools[all]
```

## 注意事项

1. **硬件要求**: RKNN 模型需要在瑞芯微芯片上运行
2. **模型格式**: 支持 PyTorch (.pt) -> ONNX -> RKNN 的转换流程
3. **图像格式**: 支持常见的图像格式 (JPG, PNG, BMP 等)
4. **视频格式**: 支持常见的视频格式 (MP4, AVI, MOV 等)