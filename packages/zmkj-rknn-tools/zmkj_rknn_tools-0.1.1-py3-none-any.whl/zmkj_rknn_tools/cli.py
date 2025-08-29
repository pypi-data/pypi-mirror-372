#!/usr/bin/env python3
"""
ZMKJ RKNN Tools - 命令行接口 (标准模式)

该模块提供命令行接口，支持模型转换、推理检测和环境验证功能。
标准模式版本，专注于稳定性和简洁性。
"""

import sys
import argparse
import logging
import cv2
import time
from pathlib import Path

from . import __version__
from .detector import YOLOv8Detector

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_file_in_examples_data(filename):
    """
    在examples_data/zmkj_rknn_examples_data目录中查找文件
    
    Args:
        filename: 要查找的文件名
        
    Returns:
        如果找到，返回完整路径；否则返回None
    """
    # 构建可能的examples_data目录路径
    possible_paths = [
        Path("examples_data/zmkj_rknn_examples_data") / filename,
        Path(__file__).parent.parent.parent / "examples_data" / "zmkj_rknn_examples_data" / filename,
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return None

def detect_main():
    """推理检测命令行工具 (标准模式)"""
    parser = argparse.ArgumentParser(
        description="RKNN 模型推理工具 (标准模式)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 图像推理
  zmkj-rknn-detect -m model.rknn -i image.jpg -o result.jpg
  
  # 视频推理
  zmkj-rknn-detect -m model.rknn -i video.mp4 -o result.mp4
  
  # 摄像头推理
  zmkj-rknn-detect -m model.rknn -i 0 --show
        """
    )

    # 基本参数
    parser.add_argument("--version", action="version", version=f"zmkj-rknn-tools {__version__}")
    parser.add_argument("--model", "-m", required=True, help="RKNN模型文件路径")
    parser.add_argument("--input", "-i", required=True, help="输入文件路径或摄像头索引")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--conf", type=float, default=0.5, help="置信度阈值 (默认: 0.5)")
    parser.add_argument("--nms", type=float, default=0.4, help="NMS阈值 (默认: 0.4)")
    parser.add_argument("--show", action="store_true", help="显示检测结果")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # 处理模型文件路径
        model_path = Path(args.model)
        # 如果是纯文件名，检查examples_data目录
        if model_path.name == str(model_path):
            example_model_path = find_file_in_examples_data(model_path.name)
            if example_model_path:
                model_path = example_model_path
                logging.info(f"在examples_data中找到模型文件: {model_path}")
        
        if not model_path.exists():
            logging.error(f"错误: 模型文件不存在: {model_path}")
            sys.exit(1)

        # 创建检测器
        detector = YOLOv8Detector()
        detector.load_model(str(model_path))
        logging.info("使用标准模式")

        # 处理输入
        input_arg = args.input
        
        # 尝试解析为摄像头索引
        try:
            camera_idx = int(input_arg)
            cap = cv2.VideoCapture(camera_idx)
            # 强制开启MJPG格式
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            # 关闭自动曝光
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25表示手动曝光模式
            # 设置分辨率：宽 1920，高 1080
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            # 设置帧率
            cap.set(cv2.CAP_PROP_FPS, 30)
       
            is_camera = True
        except ValueError:
            # 文件路径
            input_path = Path(input_arg)
            # 如果是纯文件名，检查examples_data目录
            if input_path.name == str(input_path):
                example_input_path = find_file_in_examples_data(input_path.name)
                if example_input_path:
                    input_path = example_input_path
                    logging.info(f"在examples_data中找到输入文件: {input_path}")
            
            if not input_path.exists():
                logging.error(f"错误: 输入文件不存在: {input_path}")
                sys.exit(1)

            if input_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']:
                # 图像文件
                process_image(detector, str(input_path), args)
                return
            else:
                # 视频文件
                cap = cv2.VideoCapture(str(input_path))
                is_camera = False

        # 处理视频/摄像头
        if 'cap' in locals():
            process_video(detector, cap, is_camera, args)

    except ImportError as e:
        logging.error(f"错误: 缺少必要的依赖包。请安装相应的 extras:")
        logging.error("  pip install zmkj-rknn-tools[rknn,viz]")
        sys.exit(1)
    except Exception as e:
        logging.error(f"推理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def process_image(detector, image_path, args):
    """处理单张图像"""
    image = cv2.imread(image_path)
    if image is None:
        logging.error(f"错误: 无法读取图像文件: {image_path}")
        sys.exit(1)

    # 执行检测
    boxes, classes, scores, inf_time, proc_time = detector.detect(
        image, conf_thresh=args.conf, nms_thresh=args.nms
    )

    logging.info(f"检测到 {len(boxes)} 个目标")
    logging.info(f"推理时间: {inf_time:.2f}ms, 后处理时间: {proc_time:.2f}ms")

    # 可视化结果
    try:
        from .visualize import visualize_detections
        result_image = visualize_detections(image, boxes, classes, scores)

        if args.output:
            cv2.imwrite(args.output, result_image)
            logging.info(f"结果已保存到: {args.output}")

        if args.show:
            cv2.imshow("Detection Result", result_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    except ImportError as e:
        logging.error(f"可视化导入错误: {e}")
        logging.info("提示: 安装 zmkj-rknn-tools[viz] 以获得更好的可视化效果")

    detector.release()

def process_video(detector, cap, is_camera, args):
    """处理视频/摄像头"""
    if not cap.isOpened():
        logging.error("错误: 无法打开视频源")
        sys.exit(1)

    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS) if not is_camera else 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if not is_camera else 0

    logging.info(f"视频信息: {width}x{height}, FPS: {fps:.2f}")
    if not is_camera:
        logging.info(f"总帧数: {total_frames}")

    # 设置输出视频
    writer = None
    if args.output and not is_camera:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(args.output, fourcc, fps, (width, height))

    try:
        frame_count = 0
        start_time = time.time()
        total_inf_time = 0
        total_proc_time = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # 执行检测
            boxes, classes, scores, inf_time, proc_time = detector.detect(
                frame, conf_thresh=args.conf, nms_thresh=args.nms
            )
            total_inf_time += inf_time
            total_proc_time += proc_time

            # 可视化
            try:
                from .visualize import visualize_detections
                result_frame = visualize_detections(frame, boxes, classes, scores)
            except ImportError:
                result_frame = frame
            
            # 保存或显示
            if writer:
                writer.write(result_frame)

            if args.show:
                cv2.imshow("Detection Result", result_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # 进度显示
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                current_fps = frame_count / elapsed
                avg_inf = total_inf_time / frame_count
                avg_proc = total_proc_time / frame_count
                
                if not is_camera:
                    progress = frame_count / total_frames * 100 if total_frames > 0 else 0
                    logging.info(f"进度: {progress:.1f}% ({frame_count}/{total_frames}), "
                               f"FPS: {current_fps:.1f}, 平均推理: {avg_inf:.1f}ms, 平均后处理: {avg_proc:.1f}ms")
                else:
                    logging.info(f"帧数: {frame_count}, FPS: {current_fps:.1f}, "
                               f"平均推理: {avg_inf:.1f}ms, 平均后处理: {avg_proc:.1f}ms")

    except KeyboardInterrupt:
        logging.info("\n检测已停止")

    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        detector.release()

        # 最终统计
        elapsed = time.time() - start_time
        final_fps = frame_count / elapsed if elapsed > 0 else 0
        logging.info(f"\n处理完成:")
        logging.info(f"  处理帧数: {frame_count}")
        logging.info(f"  总时间: {elapsed:.2f}s")
        logging.info(f"  平均FPS: {final_fps:.2f}")
        if frame_count > 0:
            logging.info(f"  平均推理时间: {total_inf_time/frame_count:.2f}ms")
            logging.info(f"  平均后处理时间: {total_proc_time/frame_count:.2f}ms")

        if args.output and not is_camera:
            logging.info(f"结果已保存到: {args.output}")

if __name__ == "__main__":
    detect_main()