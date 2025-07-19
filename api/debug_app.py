#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF转换工具 - 调试版本
输出详细的错误信息用于诊断问题
"""

import os
import tempfile
import logging
import time
import sys
import traceback
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="PDF转换工具 - 调试版",
    description="用于诊断问题的调试版本",
    version="2.5.1-debug"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """简单的调试页面"""
    return HTMLResponse(content="""
    <h1>PDF转换调试版</h1>
    <p>用于诊断问题的版本</p>
    <p><a href="/debug">查看系统信息</a></p>
    <p><a href="/health">健康检查</a></p>
    """)

@app.get("/debug")
async def debug_info():
    """系统调试信息"""
    try:
        import pkg_resources
        
        # 检查已安装的包
        installed_packages = {}
        for pkg in pkg_resources.working_set:
            installed_packages[pkg.project_name] = pkg.version
        
        # 检查关键依赖
        key_packages = ['fastapi', 'uvicorn', 'pdf2docx', 'Pillow']
        package_status = {}
        for pkg in key_packages:
            try:
                __import__(pkg.replace('-', '_'))
                package_status[pkg] = f"✅ {installed_packages.get(pkg, 'unknown')}"
            except ImportError as e:
                package_status[pkg] = f"❌ {str(e)}"
        
        return {
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "temp_directory": tempfile.gettempdir(),
            "key_packages": package_status,
            "environment_variables": {
                k: v for k, v in os.environ.items() 
                if k.startswith(('PYTHON', 'PATH', 'RENDER'))
            }
        }
    except Exception as e:
        logger.error(f"调试信息获取失败: {str(e)}")
        return {"error": str(e), "traceback": traceback.format_exc()}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "PDF转换调试版运行正常",
        "version": "2.5.1-debug",
        "environment": "render"
    }

@app.post("/api/convert")
async def convert_pdf_debug(file: UploadFile = File(...)):
    """PDF转换API - 调试版本"""
    logger.info("=" * 50)
    logger.info("开始调试转换请求")
    
    try:
        # 步骤1: 验证文件
        logger.info(f"步骤1: 验证文件 - {file.filename}")
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            logger.error("文件验证失败: 不是PDF文件")
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 步骤2: 读取文件
        logger.info("步骤2: 读取文件内容")
        content = await file.read()
        file_size = len(content)
        logger.info(f"文件大小: {file_size} bytes")
        
        if file_size == 0:
            logger.error("文件为空")
            raise HTTPException(status_code=400, detail="文件为空")
        
        # 步骤3: 创建临时目录
        logger.info("步骤3: 创建临时目录")
        temp_dir = tempfile.mkdtemp()
        logger.info(f"临时目录: {temp_dir}")
        
        try:
            # 步骤4: 写入文件
            logger.info("步骤4: 写入PDF文件")
            input_path = os.path.join(temp_dir, "input.pdf")
            output_path = os.path.join(temp_dir, "output.docx")
            
            with open(input_path, "wb") as f:
                f.write(content)
            logger.info(f"PDF文件已写入: {input_path}")
            
            # 步骤5: 检查pdf2docx
            logger.info("步骤5: 检查pdf2docx导入")
            try:
                from pdf2docx import Converter
                logger.info("pdf2docx导入成功")
            except ImportError as e:
                logger.error(f"pdf2docx导入失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"pdf2docx导入失败: {str(e)}")
            
            # 步骤6: 执行转换
            logger.info("步骤6: 开始PDF转换")
            try:
                cv = Converter(input_path)
                logger.info("Converter创建成功")
                
                cv.convert(output_path, start=0, end=None)
                logger.info("转换完成")
                
                cv.close()
                logger.info("Converter已关闭")
                
            except Exception as convert_error:
                logger.error(f"转换过程出错: {str(convert_error)}")
                logger.error(f"转换错误详情: {traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"转换失败: {str(convert_error)}")
            
            # 步骤7: 验证输出
            logger.info("步骤7: 验证输出文件")
            if not os.path.exists(output_path):
                logger.error(f"输出文件不存在: {output_path}")
                raise HTTPException(status_code=500, detail="输出文件未生成")
            
            output_size = os.path.getsize(output_path)
            logger.info(f"输出文件大小: {output_size} bytes")
            
            if output_size == 0:
                logger.error("输出文件为空")
                raise HTTPException(status_code=500, detail="输出文件为空")
            
            # 步骤8: 返回文件
            logger.info("步骤8: 准备返回文件")
            download_filename = f"debug_{int(time.time())}_{file.filename.replace('.pdf', '.docx')}"
            logger.info(f"下载文件名: {download_filename}")
            
            return FileResponse(
                path=output_path,
                filename=download_filename,
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            
        finally:
            # 清理临时文件
            logger.info("清理临时文件")
            import shutil
            try:
                shutil.rmtree(temp_dir)
                logger.info("临时目录已清理")
            except Exception as cleanup_error:
                logger.warning(f"清理失败: {cleanup_error}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        logger.error(f"完整错误信息: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"系统错误: {str(e)}")
    finally:
        logger.info("调试转换请求结束")
        logger.info("=" * 50) 