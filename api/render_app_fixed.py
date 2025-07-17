#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF转换工具 - Render修复版
解决依赖和错误处理问题
"""

import os
import tempfile
import logging
import time
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="PDF转换工具 - Render修复版",
    description="高质量PDF转Word转换服务 (Render优化版)",
    version="2.4.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Render环境配置
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.get("/")
async def read_root():
    """主页面 - 简化版本"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF转换工具</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
            }
            .container { 
                background: white; 
                padding: 2rem; 
                border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
                max-width: 500px; 
                width: 90%; 
            }
            h1 { text-align: center; color: #333; margin-bottom: 1rem; }
            .upload-area { 
                border: 2px dashed #ddd; 
                border-radius: 12px; 
                padding: 2rem; 
                text-align: center; 
                margin-bottom: 1.5rem; 
                cursor: pointer; 
            }
            .upload-area:hover { border-color: #667eea; background: #f8f9ff; }
            .file-input { display: none; }
            button { 
                width: 100%; 
                padding: 12px; 
                border: none; 
                border-radius: 8px; 
                font-size: 16px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                cursor: pointer; 
                font-weight: 600; 
            }
            button:disabled { opacity: 0.6; cursor: not-allowed; }
            .status { 
                margin-top: 1rem; 
                padding: 1rem; 
                border-radius: 8px; 
                text-align: center; 
                display: none; 
            }
            .status.success { background: #d4edda; color: #155724; }
            .status.error { background: #f8d7da; color: #721c24; }
            .status.info { background: #cce7ff; color: #004085; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF转换工具</h1>
            
            <form id="uploadForm">
                <div class="upload-area" id="uploadArea">
                    <p>📎 点击选择PDF文件</p>
                    <input type="file" id="fileInput" class="file-input" accept=".pdf" required>
                </div>
                
                <button type="submit" id="convertBtn">🚀 开始转换</button>
            </form>
            
            <div class="status" id="status"></div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const form = document.getElementById('uploadForm');
            const convertBtn = document.getElementById('convertBtn');
            const status = document.getElementById('status');

            uploadArea.addEventListener('click', () => fileInput.click());
            
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    uploadArea.innerHTML = `<p>✅ 已选择: ${e.target.files[0].name}</p>`;
                }
            });

            function showStatus(message, type) {
                status.textContent = message;
                status.className = `status ${type}`;
                status.style.display = 'block';
            }

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const file = fileInput.files[0];
                if (!file) {
                    showStatus('请选择PDF文件', 'error');
                    return;
                }

                if (file.size > 10 * 1024 * 1024) {
                    showStatus('文件大小不能超过10MB', 'error');
                    return;
                }

                convertBtn.disabled = true;
                convertBtn.textContent = '⏳ 转换中...';
                showStatus('正在转换文件，请稍候...', 'info');

                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/api/convert', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || '转换失败');
                    }
                    
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = file.name.replace('.pdf', '.docx');
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);

                    showStatus('✅ 转换完成，文件已下载！', 'success');

                } catch (error) {
                    console.error('转换错误:', error);
                    showStatus(`❌ 转换失败: ${error.message}`, 'error');
                } finally {
                    convertBtn.disabled = false;
                    convertBtn.textContent = '🚀 开始转换';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "PDF转换服务运行正常 (Render修复版)",
        "version": "2.4.0",
        "environment": "render"
    }

@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "service": "PDF转换工具",
        "version": "2.4.0",
        "environment": "render",
        "status": "running"
    }

@app.post("/api/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """PDF转换API - 修复版"""
    start_time = time.time()
    
    try:
        # 验证文件
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 读取文件内容
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        logger.info(f"收到转换请求: {file.filename}")
        logger.info(f"文件大小: {file_size_mb:.2f}MB")
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过10MB限制")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        try:
            input_path = os.path.join(temp_dir, "input.pdf")
            output_path = os.path.join(temp_dir, "output.docx")
            
            # 写入PDF文件
            with open(input_path, "wb") as f:
                f.write(content)
            
            logger.info("开始PDF转Word转换...")
            
            # 执行转换
            success = await convert_pdf_to_word_safe(input_path, output_path)
            
            if not success:
                raise HTTPException(status_code=500, detail="转换失败，请检查PDF文件是否完整")
            
            # 检查输出文件
            if not os.path.exists(output_path):
                logger.error(f"转换后文件不存在: {output_path}")
                raise HTTPException(status_code=500, detail="转换失败，输出文件未生成")
            
            file_size = os.path.getsize(output_path)
            if file_size == 0:
                logger.error("转换后文件大小为0")
                raise HTTPException(status_code=500, detail="转换失败，输出文件为空")
            
            # 生成下载文件名
            base_name = os.path.splitext(file.filename)[0]
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            download_filename = f"{timestamp}_{base_name}.docx"
            
            logger.info(f"转换完成，耗时: {time.time() - start_time:.2f}秒")
            logger.info(f"输出文件: {output_path}, 大小: {file_size} bytes")
            
            # 返回文件
            return FileResponse(
                path=output_path,
                filename=download_filename,
                media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        finally:
            # 延迟清理临时目录
            import threading
            def cleanup():
                import time
                time.sleep(5)
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"临时目录已清理: {temp_dir}")
                except Exception as e:
                    logger.warning(f"清理临时目录失败: {e}")
            
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换过程中出现错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

async def convert_pdf_to_word_safe(input_path: str, output_path: str) -> bool:
    """PDF转Word - 安全版本"""
    try:
        # 尝试导入pdf2docx
        try:
            from pdf2docx import Converter
        except ImportError as e:
            logger.error(f"pdf2docx导入失败: {e}")
            return False
        
        # 检查输入文件
        if not os.path.exists(input_path):
            logger.error(f"输入文件不存在: {input_path}")
            return False
        
        input_size = os.path.getsize(input_path)
        if input_size == 0:
            logger.error("输入文件大小为0")
            return False
        
        logger.info(f"开始转换，输入文件大小: {input_size} bytes")
        
        # 执行转换
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        
        # 检查输出文件
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            logger.info(f"转换成功，文件大小: {file_size} bytes")
            return file_size > 0
        else:
            logger.error(f"转换失败，输出文件不存在: {output_path}")
            return False
            
    except Exception as e:
        logger.error(f"PDF转Word失败: {str(e)}")
        return False 