#!/usr/bin/env python3
"""
LibreOffice PDF转Word服务启动脚本
"""

import os
import sys
import uvicorn

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入应用
from api.render_app_libreoffice import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 启动LibreOffice PDF转Word服务...")
    print(f"📍 端口: {port}")
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"💾 工作目录: {current_dir}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
 