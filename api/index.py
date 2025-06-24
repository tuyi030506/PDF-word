#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF转换工具 - Vercel Serverless版本
优化内存使用和执行时间，适配Serverless环境
"""

import os
import tempfile
import logging
import time
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="PDF转换工具 - Vercel版",
    description="高质量PDF转Word/Excel转换服务 (Serverless优化版)",
    version="2.1.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel环境配置
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB (Vercel限制)
MAX_PROCESSING_TIME = 45  # 45秒 (留5秒缓冲)

@app.get("/")
async def read_root():
    """主页面"""
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF转换工具 - Vercel版</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .container { background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 500px; width: 90%; }
            h1 { text-align: center; color: #333; margin-bottom: 0.5rem; font-size: 2rem; }
            .subtitle { text-align: center; color: #666; margin-bottom: 2rem; font-size: 0.9rem; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 0.85rem; }
            .upload-area { border: 2px dashed #ddd; border-radius: 12px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; transition: all 0.3s ease; cursor: pointer; }
            .upload-area:hover { border-color: #667eea; background: #f8f9ff; }
            .upload-area.drag-over { border-color: #667eea; background: #f0f4ff; }
            .file-input { display: none; }
            .options { margin-bottom: 1.5rem; }
            .option-group { margin-bottom: 1rem; }
            label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #333; }
            select, button { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; }
            select { background: white; }
            button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; cursor: pointer; font-weight: 600; transition: transform 0.2s ease; }
            button:hover { transform: translateY(-2px); }
            button:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
            .status { margin-top: 1rem; padding: 1rem; border-radius: 8px; text-align: center; display: none; }
            .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .status.info { background: #cce7ff; color: #004085; border: 1px solid #b3d7ff; }
            .progress { width: 100%; height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden; margin: 1rem 0; display: none; }
            .progress-bar { height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); width: 0%; transition: width 0.3s ease; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 PDF转换工具</h1>
            <p class="subtitle">Vercel Serverless版 - 快速在线转换</p>
            
            <div class="warning">
                <strong>⚠️ Serverless版本限制：</strong><br>
                • 文件大小: 最大10MB<br>
                • 处理时间: 最长45秒<br>
                • 建议优先处理小文件
            </div>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" id="uploadArea">
                    <p>📎 点击选择PDF文件或拖拽到此处</p>
                    <input type="file" id="fileInput" class="file-input" accept=".pdf" required>
                </div>
                
                <div class="options">
                    <div class="option-group">
                        <label for="outputFormat">输出格式:</label>
                        <select id="outputFormat" name="output_format">
                            <option value="docx">Word文档 (.docx)</option>
                            <option value="xlsx">Excel表格 (.xlsx)</option>
                        </select>
                    </div>
                </div>
                
                <button type="submit" id="convertBtn">🚀 开始转换</button>
            </form>
            
            <div class="progress" id="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            
            <div class="status" id="status"></div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const form = document.getElementById('uploadForm');
            const convertBtn = document.getElementById('convertBtn');
            const status = document.getElementById('status');
            const progress = document.getElementById('progress');
            const progressBar = document.getElementById('progressBar');

            // 文件拖拽处理
            uploadArea.addEventListener('click', () => fileInput.click());
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    updateFileName(files[0].name);
                }
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    updateFileName(e.target.files[0].name);
                }
            });

            function updateFileName(name) {
                uploadArea.innerHTML = `<p>✅ 已选择: ${name}</p>`;
            }

            function showStatus(message, type) {
                status.textContent = message;
                status.className = `status ${type}`;
                status.style.display = 'block';
            }

            function showProgress(percent) {
                progress.style.display = 'block';
                progressBar.style.width = percent + '%';
            }

            function hideProgress() {
                progress.style.display = 'none';
                progressBar.style.width = '0%';
            }

            // 表单提交处理
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
                showStatus('正在上传和转换文件，请稍候...', 'info');
                showProgress(10);

                const formData = new FormData();
                formData.append('file', file);
                formData.append('output_format', document.getElementById('outputFormat').value);
                formData.append('conversion_method', 'local');

                try {
                    showProgress(30);
                    const response = await fetch('/api/convert', {
                        method: 'POST',
                        body: formData
                    });

                    showProgress(80);

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || '转换失败');
                    }

                    showProgress(100);
                    
                    // 下载文件
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = response.headers.get('Content-Disposition')?.split('filename=')[1]?.replace(/"/g, '') || 'converted_file';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);

                    showStatus('✅ 转换完成，文件已下载！', 'success');
                    hideProgress();

                } catch (error) {
                    console.error('转换错误:', error);
                    showStatus(`❌ 转换失败: ${error.message}`, 'error');
                    hideProgress();
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
        "message": "PDF转换服务运行正常 (Vercel版)",
        "version": "2.1.0",
        "environment": "serverless",
        "limits": {
            "max_file_size": "10MB",
            "max_processing_time": "45s"
        }
    }

@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "service": "PDF转换工具",
        "version": "2.1.0",
        "environment": "vercel-serverless",
        "status": "running"
    }

@app.post("/api/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    output_format: str = Form("docx"),
    conversion_method: str = Form("local")
):
    """PDF转换API - Serverless优化版"""
    start_time = time.time()
    
    try:
        # 验证文件
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 读取文件内容
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        logger.info(f"收到转换请求: {file.filename} -> {output_format}")
        logger.info(f"文件大小: {file_size_mb:.2f}MB")
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过10MB限制")
        
        # 检查处理时间
        if time.time() - start_time > MAX_PROCESSING_TIME:
            raise HTTPException(status_code=408, detail="处理超时")
        
        # 创建临时文件
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, "input.pdf")
            output_path = os.path.join(temp_dir, f"output.{output_format}")
            
            # 写入PDF文件
            with open(input_path, "wb") as f:
                f.write(content)
            
            logger.info(f"开始PDF转{output_format.upper()}转换...")
            logger.info(f"输入文件: {input_path}")
            logger.info(f"输出路径: {output_path}")
            
            # 执行转换
            if output_format == "docx":
                success = await convert_pdf_to_word(input_path, output_path)
            elif output_format == "xlsx":
                success = await convert_pdf_to_excel(input_path, output_path)
            else:
                raise HTTPException(status_code=400, detail="不支持的输出格式")
            
            # 检查超时
            if time.time() - start_time > MAX_PROCESSING_TIME:
                raise HTTPException(status_code=408, detail="转换超时")
            
            if not success or not os.path.exists(output_path):
                raise HTTPException(status_code=500, detail="转换失败")
            
            # 检查输出文件
            output_size = os.path.getsize(output_path)
            logger.info(f"转换文件生成成功: {output_path}, 大小: {output_size} bytes")
            
            # 生成下载文件名
            base_name = os.path.splitext(file.filename)[0]
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            download_filename = f"{timestamp}_{base_name}.{output_format}"
            
            logger.info(f"转换完成，耗时: {time.time() - start_time:.2f}秒")
            
            # 返回文件
            return FileResponse(
                path=output_path,
                filename=download_filename,
                media_type='application/octet-stream'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换过程中出现错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

async def convert_pdf_to_word(input_path: str, output_path: str) -> bool:
    """PDF转Word - 轻量化版本"""
    try:
        # 导入转换库（延迟导入以节省内存）
        from pdf2docx import Converter
        
        # 使用更保守的参数以节省内存和时间
        cv = Converter(input_path)
        cv.convert(output_path, 
                  multi_processing=False,  # 禁用多进程
                  cpu_count=1)  # 单核处理
        cv.close()
        
        return True
    except Exception as e:
        logger.error(f"PDF转Word失败: {str(e)}")
        return False

async def convert_pdf_to_excel(input_path: str, output_path: str) -> bool:
    """PDF转Excel - 简化版本"""
    try:
        import tabula
        import pandas as pd
        
        # 读取PDF中的表格
        tables = tabula.read_pdf(input_path, pages='all', multiple_tables=True)
        
        if not tables:
            logger.warning("PDF中未发现表格数据")
            # 创建空的Excel文件
            pd.DataFrame().to_excel(output_path, index=False)
            return True
        
        # 保存到Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, table in enumerate(tables):
                sheet_name = f'Sheet_{i+1}' if len(tables) > 1 else 'Sheet1'
                table.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True
    except Exception as e:
        logger.error(f"PDF转Excel失败: {str(e)}")
        return False

# Vercel handler
app = app 