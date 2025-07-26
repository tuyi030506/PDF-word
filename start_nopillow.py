#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Render 部署启动脚本 - 无Pillow版本
使用PyPDF2方案，避免Pillow依赖问题
"""

import os
import uvicorn
from api.render_app_nopillow import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info"
    ) 