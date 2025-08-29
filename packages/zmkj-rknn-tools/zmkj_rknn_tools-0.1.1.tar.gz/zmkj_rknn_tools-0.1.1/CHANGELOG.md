# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 重构项目结构，遵循 PEP 508 "extras" + PEP 621 规范
- 添加 `pyproject.toml` 配置文件
- 添加命令行工具：`rknn-convert`, `rknn-detect`, `rknn-verify`
- 添加可选依赖组：`rknn`, `yolo`, `viz`, `dev`, `docs`, `all`, `full`
- 添加类型注解支持 (`py.typed`)
- 添加测试框架和 CI/CD 配置
- 添加代码格式化和质量检查工具配置

### Changed
- 更新 Python 最低版本要求为 3.8+
- 重新组织依赖关系，使用可选依赖组
- 改进项目文档和示例

### Deprecated
- `setup.py` 将在未来版本中移除，请使用 `pyproject.toml`

## [0.1.1] - 2024-XX-XX

### Added
- 初始版本发布
- 支持 YOLOv8 模型转换（PyTorch -> ONNX -> RKNN）
- 支持图像和视频推理
- 集成 supervision 库进行可视化
- 提供配置管理功能

### Features
- 模型转换：PyTorch (.pt) -> ONNX -> RKNN
- 推理引擎：支持图像和视频输入
- 后处理优化：DFL 解码和快速 NMS
- 可视化工具：基于 supervision 库
- 性能优化：下采样、缓存、跳帧处理
- 中文文档和注释