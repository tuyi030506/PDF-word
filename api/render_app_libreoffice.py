"""
LibreOffice PDF转Word服务 - Render部署版
免费、高质量的PDF到Word转换服务
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
from typing import Dict, Any
import uvicorn

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api.libreoffice_converter import LibreOfficeConverter
except ImportError as e:
    logging.error(f"Import error: {e}")
    # 创建一个占位转换器
    class LibreHybridConverter:
        def convert_pdf_to_docx(self, pdf_content, filename):
            return False, b"", "LibreHybridConverter import failed"
        def get_status(self):
            return {"error": "Import failed"}
        def get_installation_guide(self):
            return {"error": "Import failed"}

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="LibreOffice PDF转Word服务",
    description="免费、高质量的PDF到Word转换服务，使用LibreOffice引擎",
    version="3.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化转换器
converter = LibreHybridConverter()

@app.get("/")
async def root():
    """主页 - 提供Web界面"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LibreOffice PDF转Word - 免费高质量转换</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval';">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
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
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 60px 40px;
            text-align: center;
            background: #fafafa;
            transition: all 0.3s ease;
            cursor: pointer;
            margin-bottom: 30px;
        }
        
        .upload-area:hover, .upload-area.dragover {
            border-color: #4facfe;
            background: #f0f8ff;
            transform: translateY(-2px);
        }
        
        .upload-icon {
            font-size: 4em;
            color: #ccc;
            margin-bottom: 20px;
        }
        
        .upload-area.dragover .upload-icon {
            color: #4facfe;
        }
        
        .upload-text {
            font-size: 1.3em;
            color: #666;
            margin-bottom: 15px;
        }
        
        .file-input {
            display: none;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
            text-decoration: none;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .progress {
            width: 100%;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
            display: none;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #4facfe, #00f2fe);
            border-radius: 4px;
            transition: width 0.3s ease;
            width: 0%;
        }
        
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            display: none;
        }
        
        .result.success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .result.error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .result.info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .feature {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
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
            line-height: 1.5;
        }
        
        .status-info {
            background: #e9ecef;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .status-title {
            font-weight: bold;
            color: #495057;
            margin-bottom: 10px;
        }
        
        .method-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .method-libreoffice {
            background: #28a745;
            color: white;
        }
        
        .method-pypdf2 {
            background: #ffc107;
            color: #212529;
        }
        
        @media (max-width: 768px) {
            .container { margin: 10px; border-radius: 15px; }
            .header { padding: 30px 20px; }
            .header h1 { font-size: 2em; }
            .content { padding: 30px 20px; }
            .upload-area { padding: 40px 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄➡️📝 LibreOffice PDF转Word</h1>
            <p>免费、高质量、本地处理的PDF到Word转换服务</p>
        </div>
        
        <div class="content">
            <div id="statusInfo" class="status-info">
                <div class="status-title">🔄 检查转换引擎状态...</div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🆓</div>
                    <h3>完全免费</h3>
                    <p>无使用限制，无需注册</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🔒</div>
                    <h3>隐私安全</h3>
                    <p>本地处理，文件不上传第三方</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <h3>智能转换</h3>
                    <p>LibreOffice高质量+PyPDF2备用</p>
                </div>
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <h3>格式保真</h3>
                    <p>保持原始布局和格式</p>
                </div>
            </div>
            
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📁</div>
                <div class="upload-text">点击选择PDF文件或拖拽文件到此处</div>
                <p style="color: #999; margin-top: 10px;">支持最大50MB的PDF文件</p>
                <input type="file" id="fileInput" class="file-input" accept=".pdf" />
            </div>
            
            <div class="progress" id="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            
            <div class="result" id="result"></div>
        </div>
    </div>

    <script>
        let converterStatus = null;
        
        // 页面加载时获取状态
        document.addEventListener('DOMContentLoaded', function() {
            fetchConverterStatus();
        });
        
        async function fetchConverterStatus() {
            try {
                const response = await fetch('/api/status');
                converterStatus = await response.json();
                updateStatusDisplay();
            } catch (error) {
                console.error('获取状态失败:', error);
                document.getElementById('statusInfo').innerHTML = 
                    '<div class="status-title">❌ 无法获取转换器状态</div>';
            }
        }
        
        function updateStatusDisplay() {
            const statusDiv = document.getElementById('statusInfo');
            
            if (converterStatus.libreoffice && converterStatus.libreoffice.installed) {
                const method = 'LibreOffice';
                const badge = '<span class="method-badge method-libreoffice">推荐</span>';
                statusDiv.innerHTML = \`
                    <div class="status-title">✅ 转换引擎就绪: \${method} \${badge}</div>
                    <div style="font-size: 0.9em; color: #6c757d; margin-top: 5px;">
                        版本: \${converterStatus.libreoffice.version || 'Unknown'}
                    </div>
                \`;
            } else {
                const method = 'PyPDF2';
                const badge = '<span class="method-badge method-pypdf2">基础</span>';
                statusDiv.innerHTML = \`
                    <div class="status-title">⚠️  转换引擎: \${method} \${badge}</div>
                    <div style="font-size: 0.9em; color: #6c757d; margin-top: 5px;">
                        建议安装LibreOffice以获得最佳转换质量
                    </div>
                \`;
            }
        }
        
        // 文件上传处理
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const progress = document.getElementById('progress');
        const progressBar = document.getElementById('progressBar');
        const result = document.getElementById('result');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
        
        async function handleFile(file) {
            if (!file.type === 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
                showResult('error', '请选择PDF文件！');
                return;
            }
            
            if (file.size > 50 * 1024 * 1024) {
                showResult('error', '文件大小不能超过50MB！');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                showProgress(true);
                updateProgress(10);
                
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    body: formData
                });
                
                updateProgress(50);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    let errorData;
                    try {
                        errorData = JSON.parse(errorText);
                    } catch (e) {
                        errorData = { detail: errorText || \`HTTP \${response.status}\` };
                    }
                    throw new Error(errorData.detail || '转换失败');
                }
                
                updateProgress(90);
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = file.name.replace('.pdf', '.docx');
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                updateProgress(100);
                showResult('success', '转换完成！文件已开始下载。');
                
            } catch (error) {
                console.error('转换错误:', error);
                showResult('error', \`转换失败: \${error.message}\`);
            } finally {
                setTimeout(() => {
                    showProgress(false);
                    updateProgress(0);
                }, 2000);
            }
        }
        
        function showProgress(show) {
            progress.style.display = show ? 'block' : 'none';
        }
        
        function updateProgress(percent) {
            progressBar.style.width = percent + '%';
        }
        
        function showResult(type, message) {
            result.className = \`result \${type}\`;
            result.innerHTML = message;
            result.style.display = 'block';
            
            setTimeout(() => {
                result.style.display = 'none';
            }, 5000);
        }
    </script>
</body>
</html>
    """
    return Response(content=html_content, media_type="text/html")

@app.get("/api/status")
async def get_status():
    """获取转换器状态"""
    try:
        status = converter.get_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"获取状态失败: {str(e)}"}
        )

@app.get("/api/guide")
async def get_installation_guide():
    """获取安装指南"""
    try:
        guide = converter.get_installation_guide()
        return JSONResponse(content=guide)
    except Exception as e:
        logger.error(f"获取安装指南失败: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"获取安装指南失败: {str(e)}"}
        )

@app.post("/api/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """PDF转DOCX转换接口"""
    
    # 验证文件类型
    if not file.content_type == "application/pdf" and not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    # 验证文件大小 (50MB限制)
    max_size = 50 * 1024 * 1024  # 50MB
    
    try:
        # 读取文件内容
        pdf_content = await file.read()
        
        if len(pdf_content) > max_size:
            raise HTTPException(status_code=400, detail="文件大小不能超过50MB")
        
        if len(pdf_content) == 0:
            raise HTTPException(status_code=400, detail="文件为空")
        
        logger.info(f"开始转换文件: {file.filename}, 大小: {len(pdf_content)} bytes")
        
        # 执行转换
        success, docx_content, message = converter.convert_pdf_to_docx(pdf_content, file.filename)
        
        if not success:
            logger.error(f"转换失败: {message}")
            raise HTTPException(status_code=500, detail=f"转换失败: {message}")
        
        logger.info(f"转换成功: {message}, 输出大小: {len(docx_content)} bytes")
        
        # 生成输出文件名
        output_filename = file.filename.rsplit('.', 1)[0] + '.docx'
        
        # 返回DOCX文件
        return Response(
            content=docx_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=\"{output_filename}\"",
                "Content-Length": str(len(docx_content))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@app.get("/healthz")
async def health_check():
    """健康检查"""
    status = converter.get_status()
    
    return {
        "status": "healthy",
        "message": "LibreOffice PDF转Word服务运行正常",
        "version": "3.0.0",
        "environment": os.getenv("RENDER", "local"),
        "converter_status": status
    }

@app.get("/debug")
async def debug_info():
    """调试信息"""
    import platform
    
    try:
        status = converter.get_status()
        
        debug_data = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "working_directory": os.getcwd(),
            "converter_status": status,
            "environment_variables": {
                key: os.getenv(key) for key in [
                    "RENDER", "RENDER_SERVICE_NAME", "RENDER_EXTERNAL_URL",
                    "PATH", "PYTHON_VERSION"
                ] if os.getenv(key)
            }
        }
        
        return JSONResponse(content=debug_data)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Debug info error: {str(e)}",
                "python_version": sys.version,
                "platform": platform.platform()
            }
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )