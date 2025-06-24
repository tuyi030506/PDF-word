from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/convert")
async def convert_pdf(file: UploadFile = File(...), output_format: str = Form(default="docx")):
    logger.info(f"收到文件: {file.filename}")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail={"message": "只支持PDF文件"})
    
    # 目前返回演示文件
    content = f"""转换完成！

原始文件: {file.filename}
目标格式: {output_format}
处理时间: {__import__('datetime').datetime.now()}

这是一个演示结果。
实际转换功能正在完善中。
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        return FileResponse(
            path=f.name,
            filename=f"converted_{file.filename.replace('.pdf', '.txt')}",
            media_type="text/plain"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server_simple:app", host="0.0.0.0", port=3001, reload=True) 