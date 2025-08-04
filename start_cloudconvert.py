#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CloudConvert高质量版本启动脚本
"""

import uvicorn
from api.render_app_cloudconvert import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 