#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型转换示例脚本

该脚本展示了如何使用rknn-tools库进行模型转换，包括PyTorch模型转ONNX和ONNX模型转RKNN。
支持直接将PyTorch模型转换为RKNN模型，并提供了多种优化选项。
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# 导入rknn-tools库
from zmkj_rknn_tools.converter import pt_to_onnx, onnx_to_rknn, pt_to_rknn, verify_rknn


def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="YOLOv8模型转换示例")
    parser.add_argument("--pt", type=str, help="PyTorch模型路径(.pt)")
    parser.add_argument("--onnx", type=str, help="ONNX模型路径(.onnx)")
    parser.add_argument("--output", type=str, default="output", help="输出模型路径，默认使用输入模型名称")
    parser.add_argument("--img-size", type=int, nargs=2, default=[640, 640], 
                        help="模型输入尺寸 [宽, 高]")
    parser.add_argument("--target", type=str, default="rk3576", 
                        help="目标平台，如rk3566, rk3568, rk3588, rk3576等")
    parser.add_argument("--quantize", action="store_true", help="是否量化模型")
    parser.add_argument("--dataset", type=str, default="", 
                        help="量化数据集路径，为空则使用随机数据")
    parser.add_argument("--verify", action="store_true", help="验证RKNN环境")
    parser.add_argument("--direct", action="store_true", 
                        help="直接将PyTorch模型转换为RKNN模型，跳过ONNX中间步骤")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")
    
    return parser.parse_args()


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_args()
    
    # 验证RKNN环境
    if args.verify:
        print("验证RKNN环境...")
        if verify_rknn():
            print("RKNN环境验证通过")
        else:
            print("RKNN环境验证失败")
        return
    
    # 检查输入模型
    if args.pt is None and args.onnx is None:
        print("错误: 必须提供PyTorch模型(.pt)或ONNX模型(.onnx)")
        return
    
    # 设置输出路径
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    
    # 直接转换PyTorch模型到RKNN
    if args.pt and args.direct:
        print(f"直接将PyTorch模型转换为RKNN: {args.pt}")
        
        # 设置输出路径
        if not args.output:
            pt_name = os.path.basename(args.pt)
            output_rknn = os.path.splitext(pt_name)[0] + ".rknn"
        else:
            output_rknn = args.output
        
        # 转换模型
        success = pt_to_rknn(
            model_path=args.pt,
            output_path=output_rknn,
            img_size=args.img_size,
            platform=args.target,
            do_quantization=args.quantize,
            dataset_path=args.dataset if args.dataset else None,
            # verbose=args.verbose
        )
        
        if success:
            print(f"模型转换成功: {output_rknn}")
        else:
            print("模型转换失败")
        
        return
    
    # PyTorch模型转ONNX
    if args.pt:
        print(f"将PyTorch模型转换为ONNX: {args.pt}")
        
        # 设置输出路径
        if not args.output:
            # 使用默认输出路径
            output_onnx = None
        else:
            output_onnx = args.output
        
        # 转换模型
        success, onnx_file_path = pt_to_onnx(
            model_path=args.pt,
            output_path=output_onnx,
            img_size=args.img_size,
        )
        
        if success and onnx_file_path:
            print(f"PyTorch模型转换为ONNX成功: {onnx_file_path}")
            # 更新ONNX路径用于后续转换
            args.onnx = onnx_file_path
        else:
            print("PyTorch模型转换为ONNX失败")
            return
    
    # ONNX模型转RKNN
    if args.onnx:
        print(f"将ONNX模型转换为RKNN: {args.onnx}")
        
        # 设置输出路径
        if not args.output:
            onnx_name = os.path.basename(args.onnx)
            output_rknn = os.path.splitext(onnx_name)[0] + ".rknn"
        else:
            output_rknn = args.output
        
        # 转换模型
        success = onnx_to_rknn(
            model_path=args.onnx,
            output_path=output_rknn,
            # img_size=args.img_size,
            target_platform=args.target,
            do_quantization=args.quantize,
            dataset_path=args.dataset if args.dataset else None,
            # verbose=args.verbose
        )
        
        if success:
            print(f"ONNX模型转换为RKNN成功: {output_rknn}")
        else:
            print("ONNX模型转换为RKNN失败")


if __name__ == "__main__":
    main()