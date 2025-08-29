# -*- coding: utf-8 -*-
"""
模型转换模块 - 提供YOLOv8模型到RKNN模型的转换功能

该模块包含两个主要功能：
1. PyTorch模型(.pt)转ONNX模型(.onnx)
2. ONNX模型(.onnx)转RKNN模型(.rknn)

这些功能可以单独使用，也可以组合使用以完成完整的转换流程。
"""

import os
import logging
import traceback
from pathlib import Path



# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging._nameToLevel["WARNING"]= 30  # 强行注册

def pt_to_onnx(model_path, output_path=None, img_size=640, batch_size=1, opset=12, simplify=True):
    """
    将PyTorch模型转换为ONNX模型
    
    Args:
        model_path: PyTorch模型路径(.pt)
        output_path: 输出ONNX模型路径，如果为None则使用相同文件名但扩展名为.onnx
        img_size: 输入图像尺寸
        batch_size: 批处理大小
        opset: ONNX操作集版本
        simplify: 是否简化ONNX模型
        
    Returns:
        成功返回True和输出文件路径，失败返回False和None
    """
    try:
        # 导入必要的库
        from ultralytics import YOLO
        from ultralytics.utils import (DEFAULT_CFG)
        
        # 设置默认配置
        cfg = DEFAULT_CFG
        cfg.model = model_path
        cfg.format = 'rknn'
        cfg.imgsz = img_size
        cfg.batch = batch_size
        cfg.opset = opset
        cfg.simplify = simplify
        
        # 如果未指定输出路径，则使用默认路径（与pt文件同目录同名但扩展名为.onnx）
        model_dir = os.path.dirname(model_path)
        model_name = os.path.basename(model_path)
        name_without_ext = os.path.splitext(model_name)[0]
        logging.info(f"输出目录: {output_path}")
        
        # if output_path is not None:
        #     cfg.output = output_path
        # else:
        #     # 默认输出到与pt文件相同目录
        #     cfg.output = os.path.join(model_dir, name_without_ext + '.onnx')
        
        # 加载模型
        logging.info(f"加载PyTorch模型: {model_path}")
        model = YOLO(cfg.model)
        
        # 导出模型
        logging.info(f"导出ONNX模型，参数: img_size={img_size}, batch={batch_size}, opset={opset}, simplify={simplify}")
        success = model.export(**vars(cfg))
        
        if success:
            # 确定ONNX文件的实际位置
            torchscript_file = os.path.join(model_dir, name_without_ext + '_rknnopt.torchscript')
            if output_path:
                output_path= os.path.join(output_path, name_without_ext + '_rknnopt.torchscript')
                import shutil
                logging.info(f"将TorchScript模型移动到指定输出路径:{torchscript_file} 2 {output_path}")
                shutil.move(torchscript_file,output_path)
                torchscript_file = output_path
        
            logging.info(f"ONNX模型导出成功: {torchscript_file}")
            
            return True, torchscript_file
        else:
            logging.error("ONNX模型导出失败")
            return False, None
    
    except Exception as e:
        logging.error(f"PyTorch模型转ONNX出错: {str(e)}")
        traceback.print_exc()
        return False, None


def onnx_to_rknn(model_path, output_path=None, platform='rk3576', 
                 do_quantization=False, dataset_path=None, 
                 mean_values=[[0, 0, 0]], std_values=[[255, 255, 255]], 
                 target_platform=None, input_size_list=None):
    """
    将ONNX模型转换为RKNN模型
    
    Args:
        model_path: ONNX模型路径或TorchScript模型路径
        output_path: 输出RKNN模型路径，如果为None则使用相同文件名但扩展名为.rknn
        platform: 目标平台，如'rk3576'、'rk3588'等
        do_quantization: 是否进行量化
        dataset_path: 量化数据集路径，如果do_quantization为True则必须提供
        mean_values: 预处理均值
        std_values: 预处理标准差
        target_platform: 目标平台，如果为None则使用platform参数
        input_size_list: 输入尺寸列表，仅在加载TorchScript模型时需要
        
    Returns:
        成功返回True，失败返回False
    """
    try:
        # 导入必要的库
        from rknn.api import RKNN
        
        # 如果未指定输出路径，则使用默认路径
        base_path = output_path if output_path else os.path.dirname(model_path)
        if model_path.endswith('_rknnopt.torchscript'):
            name = Path(model_path).stem.split('_rknnopt')[0]
        else:
            name = Path(model_path).stem
        output_path = os.path.join(base_path,name+'.rknn')
        # 如果未指定目标平台，则使用platform参数
        if target_platform is None:
            target_platform = platform
        
        # 创建RKNN对象
        rknn = RKNN(verbose=True)
        
        # 配置模型
        logging.info(f"配置RKNN模型: platform={target_platform}")
        ret = rknn.config(mean_values=mean_values, std_values=std_values, target_platform=target_platform)
        if ret != 0:
            logging.error("配置RKNN模型失败")
            return False
        
        # 加载模型
        logging.info(f"加载模型: {model_path}")
        if model_path.endswith('.onnx') :
            ret = rknn.load_onnx(model=model_path)
        else:  # 假设是TorchScript模型
            if input_size_list is None:
                input_size_list = [[1, 3, 640, 640]]  # 默认输入尺寸
            ret = rknn.load_pytorch(model=model_path, input_size_list=input_size_list)
        
        if ret != 0:
            logging.error("加载模型失败")
            return False
        
        # 构建模型
        logging.info(f"构建RKNN模型: do_quantization={do_quantization}")
        if do_quantization and dataset_path is None:
            logging.error("进行量化时必须提供dataset_path参数")
            return False
        
        ret = rknn.build(do_quantization=do_quantization, dataset=dataset_path)
        if ret != 0:
            logging.error("构建RKNN模型失败")
            return False
        
        # 导出RKNN模型
        logging.info(f"导出RKNN模型: {output_path}")
        ret = rknn.export_rknn(output_path)
        if ret != 0:
            logging.error("导出RKNN模型失败")
            return False
        
        logging.info(f"RKNN模型导出成功: {output_path}")
        
        # 释放资源
        rknn.release()
        
        return True
    
    except Exception as e:
        logging.error(f"ONNX模型转RKNN出错: {str(e)}")
        traceback.print_exc()
        return False


def pt_to_rknn(model_path, output_path=None, platform='rk3576', 
               do_quantization=False, dataset_path=None, 
               img_size=640, batch_size=1, opset=12, simplify=True,
               mean_values=[[0, 0, 0]], std_values=[[255, 255, 255]]):
    """
    将PyTorch模型直接转换为RKNN模型（一步到位）
    
    Args:
        model_path: PyTorch模型路径(.pt)
        output_path: 输出RKNN模型路径，如果为None则使用相同文件名但扩展名为.rknn
        platform: 目标平台，如'rk3576'、'rk3588'等
        do_quantization: 是否进行量化
        dataset_path: 量化数据集路径，如果do_quantization为True则必须提供
        img_size: 输入图像尺寸
        batch_size: 批处理大小
        opset: ONNX操作集版本
        simplify: 是否简化ONNX模型
        mean_values: 预处理均值
        std_values: 预处理标准差
        
    Returns:
        成功返回True，失败返回False
    """
    try:
        # 第一步：PyTorch模型转ONNX
        logging.info("第一步：PyTorch模型转ONNX")
        success, onnx_file_path = pt_to_onnx(
            model_path=model_path,
            output_path=None,  # 使用默认输出路径
            img_size=img_size,
            batch_size=batch_size,
            opset=opset,
            simplify=simplify
        )
        
        if not success or onnx_file_path is None:
            logging.error("PyTorch模型转ONNX失败，中止转换流程")
            return False
        
        # 第二步：ONNX模型转RKNN
        logging.info("第二步：ONNX模型转RKNN")
        success = onnx_to_rknn(
            model_path=onnx_file_path,  # 使用pt_to_onnx返回的文件路径
            output_path=output_path,
            platform=platform,
            do_quantization=do_quantization,
            dataset_path=dataset_path,
            mean_values=mean_values,
            std_values=std_values
        )
        
        # 删除临时ONNX文件（包括原始onnx和带torchscript后缀的文件）
        original_onnx = onnx_file_path.replace('.torchscript', '')
        if os.path.exists(original_onnx):
            os.remove(original_onnx)
            logging.info(f"已删除ONNX文件: {original_onnx}")
        
        if os.path.exists(onnx_file_path):
            os.remove(onnx_file_path)
            logging.info(f"已删除带torchscript后缀的ONNX文件: {onnx_file_path}")
        
        if not success:
            logging.error("ONNX模型转RKNN失败")
            return False
        
        logging.info("PyTorch模型成功转换为RKNN模型")
        return True
    
    except Exception as e:
        logging.error(f"PyTorch模型转RKNN出错: {str(e)}")
        traceback.print_exc()
        return False


def verify_rknn():
    """
    验证RKNN环境是否正确安装
    
    Returns:
        成功返回True，失败返回False
    """
    try:
        from rknn.api import RKNN
        rknn = RKNN()
        if rknn:
            logging.info("RKNN环境验证成功")
            return True
        else:
            logging.error("RKNN初始化失败")
            return False
    except ImportError:
        logging.error("RKNN模块未安装或安装失败")
        return False
    except Exception as e:
        logging.error(f"RKNN环境验证出错: {str(e)}")
        traceback.print_exc()
        return False