#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境验证示例脚本

该脚本用于验证RKNN环境是否正确安装和配置，包括RKNN模块加载、运行时环境初始化等。
"""

import os
import sys
import argparse
from pathlib import Path
import logging
# 添加项目根目录到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 导入rknn-tools库
from zmkj_rknn_tools.converter import verify_rknn

import supervision as sv

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="RKNN环境验证示例")
    parser.add_argument("--verbose", action="store_true", help="显示详细日志")
    
    return parser.parse_args()


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_args()
    
    print("开始验证RKNN环境...")
    print("检查RKNN模块是否可用...")
    
    # 验证RKNN环境
    success = verify_rknn()
    
    # 检查supervision库
    print("\n检查可视化依赖...")
    if sv.__version__:
        print("✅ supervision库已安装，可以运行示例中的可视化代码。")
    else:
        print("❌ supervision库未安装，示例中的可视化代码将无法运行。")
        print("  如果需要运行示例代码，建议安装supervision库：pip install supervision")
        print("  注意：supervision库是可选的，您可以在自己的代码中实现可视化功能。")
    
    if success:
        print("\n✅ RKNN环境验证通过!")
        print("您可以使用zmkj-rknn-tools库进行模型转换和推理。")
    else:
        print("\n❌ RKNN环境验证失败!")
        print("请检查RKNN环境安装是否正确。")
        print("可能的解决方案:")
        print("1. 确保已安装rknn-toolkit2或rknnlite2")
        print("2. 检查Python版本是否兼容(推荐Python 3.10.12)")
        print("3. 确保运行在支持的RK平台上(如RK3576)")
        print("4. 尝试重新安装RKNN相关库")


if __name__ == "__main__":
    main()