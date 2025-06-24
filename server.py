from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF转换工具", description="PDF格式转换服务")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建静态文件目录
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """主页"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        logger.error(f"读取首页失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"无法读取首页: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "PDF转换服务运行正常"}

@app.get("/api/formats")
async def get_supported_formats():
    """获取支持的转换格式"""
    return {
        "supported_formats": [
            {
                "format": "docx",
                "name": "Word文档",
                "description": "Microsoft Word文档格式，保持文本格式和布局"
            },
            {
                "format": "xlsx", 
                "name": "Excel表格",
                "description": "Microsoft Excel表格格式，适合数据分析"
            }
        ]
    }

@app.post("/api/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    output_format: str = Form(default="docx")
):
    """PDF转换API"""
    logger.info(f"收到转换请求: {file.filename} -> {output_format}")
    
    # 验证文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail={"error": "INVALID_FILE_TYPE", "message": "只支持PDF文件"}
        )
    
    # 验证输出格式
    if output_format not in ["docx", "xlsx"]:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_FORMAT", "message": "只支持docx和xlsx格式"}
        )
    
    try:
        # 读取文件内容
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        # 文件大小限制
        if file_size_mb > 50:
            raise HTTPException(
                status_code=400,
                detail={"error": "FILE_TOO_LARGE", "message": f"文件过大({file_size_mb:.1f}MB)，请上传小于50MB的文件"}
            )
        
        logger.info(f"文件大小: {file_size_mb:.2f}MB")
        
        # 使用临时目录进行转换
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存上传的PDF文件
            pdf_path = Path(temp_dir) / "input.pdf"
            with pdf_path.open("wb") as buffer:
                buffer.write(content)
            
            # 尝试使用iLovePDF API转换
            try:
                result_file = await convert_with_ilovepdf_fixed(pdf_path, temp_dir, output_format)
            except Exception as e:
                logger.warning(f"iLovePDF转换失败，尝试其他方法: {str(e)}")
                # 如果API失败，提供备用方案
                return await fallback_conversion(file, output_format)
            
            # 生成下载文件名
            output_filename = file.filename.replace('.pdf', f'.{output_format}')
            
            # 返回转换后的文件
            media_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if output_format == "docx"
                else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            return FileResponse(
                path=str(result_file),
                filename=output_filename,
                media_type=media_type
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"转换失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "CONVERSION_FAILED", "message": f"转换失败: {str(e)}"}
        )

async def convert_with_ilovepdf_fixed(pdf_path: Path, temp_dir: str, output_format: str) -> Path:
    """修复版iLovePDF转换"""
    try:
        # 动态导入，避免启动时错误
        from pylovepdf.ilovepdf import ILovePdf
        
        logger.info("开始iLovePDF转换")
        
        # iLovePDF API凭据
        ILOVEPDF_PUBLIC_KEY = "project_public_9cf5f6497d2b1edd65b94e6543430bb2_t5EuN6a01487e167e3e908ca46ff1803171fb"
        
        # 初始化客户端
        ilovepdf = ILovePdf(ILOVEPDF_PUBLIC_KEY, verify_ssl=True)
        
        # 创建任务 - 使用修复的方法
        if output_format == "docx":
            task = ilovepdf.new_task('pdfdocx')
        else:
            task = ilovepdf.new_task('pdfexcel')
        
        logger.info(f"任务创建成功，类型: {task}")
        
        # 添加文件
        task.add_file(str(pdf_path))
        logger.info("文件添加成功")
        
        # 执行转换
        task.execute()
        logger.info("转换执行完成")
        
        # 下载结果
        task.download()
        logger.info("文件下载完成")
        
        # 查找转换后的文件
        for filename in os.listdir(temp_dir):
            if filename.endswith(f'.{output_format}') and filename != "input.pdf":
                result_path = Path(temp_dir) / filename
                logger.info(f"找到转换结果: {result_path}")
                return result_path
        
        raise Exception("未找到转换后的文件")
        
    except ImportError as e:
        logger.error(f"pylovepdf导入失败: {str(e)}")
        raise Exception(f"转换库未正确安装: {str(e)}")
    except Exception as e:
        logger.error(f"iLovePDF转换详细错误: {str(e)}")
        raise Exception(f"在线转换失败: {str(e)}")

async def fallback_conversion(file: UploadFile, output_format: str):
    """备用转换方案 - 生成说明文件"""
    logger.info("使用备用转换方案")
    
    # 创建说明文件
    content = f"""PDF转换说明

文件名: {file.filename}
请求格式: {output_format}
处理时间: {__import__('datetime').datetime.now()}

转换状态:
❌ 在线API暂时不可用
⚠️  当前返回此说明文件

解决方案:
1. 检查网络连接
2. 稍后重试
3. 联系技术支持

技术信息:
- 服务端已接收文件
- 文件格式验证通过
- 等待转换服务恢复

"""
    
    # 保存为临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_file = f.name
    
    return FileResponse(
        path=temp_file,
        filename=f"conversion_info_{file.filename.replace('.pdf', '.txt')}",
        media_type="text/plain"
    )

# 测试依赖接口
@app.get("/api/test-dependencies")
async def test_dependencies():
    """测试依赖是否正常"""
    results = {}
    
    # 测试PyMuPDF
    try:
        import fitz
        results["fitz"] = "✅ PyMuPDF导入成功"
    except ImportError as e:
        results["fitz"] = f"❌ PyMuPDF导入失败: {str(e)}"
    
    # 测试pylovepdf
    try:
        from pylovepdf.ilovepdf import ILovePdf
        results["pylovepdf"] = "✅ pylovepdf导入成功"
    except ImportError as e:
        results["pylovepdf"] = f"❌ pylovepdf导入失败: {str(e)}"
    
    # 测试任务创建
    try:
        from pylovepdf.ilovepdf import ILovePdf
        ILOVEPDF_PUBLIC_KEY = "project_public_9cf5f6497d2b1edd65b94e6543430bb2_t5EuN6a01487e167e3e908ca46ff1803171fb"
        ilovepdf = ILovePdf(ILOVEPDF_PUBLIC_KEY, verify_ssl=True)
        task = ilovepdf.new_task('pdfdocx')
        results["task_creation"] = "✅ 任务创建成功"
    except Exception as e:
        results["task_creation"] = f"❌ 任务创建失败: {str(e)}"
    
    return {"dependency_status": results}

if __name__ == "__main__":
    import uvicorn
    logger.info("启动PDF转换服务...")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=3001,
        log_level="info",
        reload=True
    )