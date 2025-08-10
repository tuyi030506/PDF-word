#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
无Pillow版本的启动脚本
专为Render部署优化，避免Pillow依赖问题
"""

import os
import uvicorn
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """启动FastAPI应用"""
    port = int(os.environ.get("PORT", 3001))
    
    logger.info("🚀 启动PDF转换服务 (无Pillow版本)")
    logger.info(f"📍 监听端口: {port}")
    
    try:
        # 导入应用
        from server import app
        
        # 验证关键依赖
        try:
            import PyPDF2
            from docx import Document
            from pdf2docx import Converter
            logger.info("✅ 核心依赖验证通过")
        except ImportError as e:
            logger.error(f"❌ 依赖验证失败: {e}")
            raise
        
        # 启动服务
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        raise

if __name__ == "__main__":
    main()
