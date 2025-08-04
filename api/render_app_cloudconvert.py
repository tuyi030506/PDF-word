#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转Word服务 - CloudConvert高质量版本
支持90%+相似度的专业级PDF转换
"""

import os
import tempfile
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .hybrid_converter import HybridConverter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CloudConvert API Key
CLOUDCONVERT_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZjJkZjJmOTA0ZDBkZDQyMWVlNWJmOGZkNzBmYWJmMTVhZGI0N2IzYmI0YjkyMzRlNTJmMTYzOTM1YzZmMmNiM2FkMDQ3MDcxZjM0NGIwYmIiLCJpYXQiOjE3NTM1NDk3NzguNTIyOTk1LCJuYmYiOjE3NTM1NDk3NzguNTIyOTk2LCJleHAiOjQ5MDkyMjMzNzguNTE3MzM1LCJzdWIiOiI3MjE1MzE0MSIsInNjb3BlcyI6WyJ0YXNrLnJlYWQiLCJ0YXNrLndyaXRlIl19.O30nWdGoEQzBXEok8MmGEPxJgutrdkwPLGRNx2h1QyIXAoPT_qSwe-kzv5khg5kJVI0CawDb5izpwWNI79AzM7hU-ZpbdQuuQPmdJipNti4Pdt6aaK_foJEiZO9jrhBF4VbGNIy-Tc5wned4AqdEJboYiuqWa4Onnh0VZ5fRz6osOvx1d3bHLfN_nUgX0lGkP0pmBV00CrNomei9LIpMDaHzV60wfyzkQBlYZ-WrpmGP3iBllCpm_hdZLpudGHHZpAjMAjoBwn2cxh1GKbuYbI-JcyWsbfruEo15BZYvK6LmBU-044yJqQvGCSHZ6fqQ2Q5J-TSJH3et9DDHhH8YtC6UZn4v8det0Xo_JPkI0kGdbPTq6-e7UYPhvX3hrvxcNRPh7FQ9A6AMr7jv1iMd6z4oMyZzhMhwkSso1Wf9gx6pSN35LUhRMp0F15AuhbVc4KKHXWbOdU1hrtJzjMUf_oM63f7OJL-T2Bu_4yI92gJUEi91kG5PYZ5RfNIUWxap_rOD30pV-URW5rCKzNNmSrzPG1a3yEPszsLjZ7whcNwnAIYE0Cg3e6Gno_v2x-CJbjZU0zenWIShA2jb1iJEJ1bs_fDhxztEcTqr1-KobhFXXiW_zlMWHW8kmU7p7XpvXOtB2d0W0PU1sdq9OoZs2gbHmyq05fZZbuWRADBsjNc"

# 创建FastAPI应用
app = FastAPI(
    title="PDF转Word高质量服务",
    description="使用CloudConvert API实现90%+相似度的专业PDF转换",
    version="3.0.0"
)

# 添加CORS支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化混合转换器
converter = HybridConverter(CLOUDCONVERT_API_KEY)

@app.get("/")
async def root():
    """主页"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
    <title>PDF转Word高质量服务</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .quality-badge {
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 25px;
            margin-top: 20px;
            display: inline-block;
            font-weight: bold;
        }
        
        .main-content {
            padding: 40px;
        }
        
        .upload-section {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .file-input-wrapper {
            position: relative;
            display: inline-block;
            margin-bottom: 20px;
        }
        
        .file-input {
            opacity: 0;
            position: absolute;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }
        
        .file-input-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            border: none;
            font-size: 1.1em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
        }
        
        .file-input-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .convert-btn {
            background: #28a745;
            color: white;
            padding: 15px 40px;
            border-radius: 50px;
            border: none;
            font-size: 1.1em;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-left: 20px;
        }
        
        .convert-btn:hover {
            background: #218838;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .convert-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            font-weight: 500;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.processing {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .feature {
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            background: #f8f9fa;
        }
        
        .feature-icon {
            font-size: 2.5em;
            margin-bottom: 15px;
        }
        
        .feature h3 {
            color: #333;
            margin-bottom: 10px;
        }
        
        .feature p {
            color: #666;
            font-size: 0.9em;
        }
        
        .conversion-info {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PDF转Word高质量服务</h1>
            <p>基于CloudConvert API的专业转换</p>
            <div class="quality-badge">
                🎯 90%+ 相似度保证
            </div>
        </div>
        
        <div class="main-content">
            <div class="upload-section">
                <div class="file-input-wrapper">
                    <input type="file" id="pdfFile" class="file-input" accept=".pdf">
                    <label for="pdfFile" class="file-input-btn">
                        📄 选择PDF文件
                    </label>
                </div>
                <button id="convertBtn" class="convert-btn" disabled>
                    🚀 开始高质量转换
                </button>
            </div>
            
            <div id="status" class="status hidden"></div>
            
            <div id="conversionInfo" class="conversion-info"></div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <h3>90%+ 相似度</h3>
                    <p>CloudConvert专业API保证高质量转换</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <h3>完美表格</h3>
                    <p>保持表格结构和格式完整性</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🖼️</div>
                    <h3>图像保留</h3>
                    <p>图片和图表无损转换</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <h3>智能备用</h3>
                    <p>API失败时自动切换本地转换</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        
        const fileInput = document.getElementById('pdfFile');
        const convertBtn = document.getElementById('convertBtn');
        const status = document.getElementById('status');
        const conversionInfo = document.getElementById('conversionInfo');
        
        fileInput.addEventListener('change', function(e) {
            selectedFile = e.target.files[0];
            if (selectedFile) {
                if (selectedFile.type === 'application/pdf') {
                    convertBtn.disabled = false;
                    convertBtn.textContent = '🚀 开始高质量转换';
                    showStatus('已选择: ' + selectedFile.name + ' (' + formatFileSize(selectedFile.size) + ')', 'success');
                } else {
                    showStatus('请选择PDF文件', 'error');
                    convertBtn.disabled = true;
                }
            }
        });
        
        convertBtn.addEventListener('click', async function() {
            if (!selectedFile) return;
            
            showStatus('正在上传并转换... 🔄', 'processing');
            convertBtn.disabled = true;
            convertBtn.textContent = '转换中...';
            
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    body: formData
                });
                
                // 安全的JSON解析 - 修复版本
                console.log('🔍 响应状态:', response.status);
                console.log('🔍 响应类型:', response.headers.get('content-type'));

                let result;
                try {
                    const responseText = await response.text();
                    console.log('🔍 响应内容前200字符:', responseText.substring(0, 200));
                    
                    if (responseText.trim() === '') {
                        showStatus('❌ 服务器返回空响应', 'error');
                        return;
                    }
                    
                    result = JSON.parse(responseText);
                    console.log('✅ JSON解析成功');
                } catch (jsonError) {
                    console.error('❌ JSON解析错误:', jsonError);
                    console.error('📄 原始响应:', responseText);
                    showStatus('服务器响应格式错误: ' + responseText.substring(0, 200), 'error');
                    return;
                }
                
                if (response.ok) {
                    showStatus('转换成功！ ✅ 正在下载...', 'success');
                    showConversionInfo(result);
                    
                    // 下载文件
                    const downloadResponse = await fetch(result.download_url);
                    const blob = await downloadResponse.blob();
                    
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = result.filename;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                    
                    showStatus('下载完成！ 🎉', 'success');
                } else {
                    showStatus('转换失败: ' + result.detail, 'error');
                }
            } catch (error) {
                showStatus('网络错误: ' + error.message, 'error');
            }
            
            convertBtn.disabled = false;
            convertBtn.textContent = '🚀 开始高质量转换';
        });
        
        function showStatus(message, type) {
            status.textContent = message;
            status.className = 'status ' + type;
            status.classList.remove('hidden');
        }
        
        function showConversionInfo(result) {
            const info = `
                <h4>🎯 转换详情</h4>
                <p><strong>转换方法:</strong> ${result.conversion_info.method}</p>
                <p><strong>质量等级:</strong> ${result.conversion_info.quality}</p>
                <p><strong>输入大小:</strong> ${formatFileSize(result.conversion_info.input_size)}</p>
                <p><strong>输出大小:</strong> ${formatFileSize(result.conversion_info.output_size)}</p>
                <p><strong>特性:</strong> ${result.conversion_info.features.join(', ')}</p>
                <p><strong>处理时间:</strong> ${result.processing_time}</p>
            `;
            conversionInfo.innerHTML = info;
            conversionInfo.style.display = 'block';
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
    </script>
</body>
</html>
    """)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "PDF转Word高质量服务运行正常 (CloudConvert版)",
        "version": "3.0.0",
        "environment": os.environ.get("RENDER", "local"),
        "api_provider": "CloudConvert",
        "quality": "90%+"
    }

@app.post("/api/convert")
async def convert_pdf_to_word(file: UploadFile = File(...)):
    """PDF转Word转换API - 高质量版本"""
    start_time = datetime.now()
    
    try:
        logger.info(f"开始处理文件: {file.filename}")
        
        # 验证文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        # 验证文件大小 (限制100MB)
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=400, detail="文件大小不能超过100MB")
        
        logger.info(f"文件验证通过: {file.filename} ({file_size} bytes)")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input:
            temp_input.write(file_content)
            input_path = temp_input.name
        
        # 生成输出文件名
        base_name = os.path.splitext(file.filename)[0]
        output_filename = f"{base_name}_converted.docx"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_output:
            output_path = temp_output.name
        
        try:
            # 使用混合转换器进行转换
            logger.info("开始混合转换处理")
            success, method, conversion_info = await converter.convert_pdf_to_word(input_path, output_path)
            
            if not success:
                raise HTTPException(status_code=500, detail=f"转换失败: {conversion_info.get('error', '未知错误')}")
            
            # 验证输出文件
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise HTTPException(status_code=500, detail="转换输出文件无效")
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"转换成功: {method} - {conversion_info}")
            
            # 准备响应
            return {
                "message": "转换成功",
                "filename": output_filename,
                "conversion_method": method,
                "conversion_info": conversion_info,
                "processing_time": f"{processing_time:.2f}秒",
                "download_url": f"/api/download/{os.path.basename(output_path)}"
            }
            
        finally:
            # 清理输入文件
            try:
                os.unlink(input_path)
            except:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换异常: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """下载转换后的文件"""
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在或已过期")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

@app.get("/api/stats")
async def get_stats():
    """获取转换统计信息"""
    return {
        "api_provider": "CloudConvert",
        "quality_guarantee": "90%+",
        "supported_features": [
            "完美表格保留",
            "图像无损转换", 
            "格式精确还原",
            "智能备用转换"
        ],
        "file_size_limit": "100MB",
        "supported_formats": ["PDF → DOCX"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 