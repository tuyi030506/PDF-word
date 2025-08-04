#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CloudConvert API 测试脚本
测试API连接和PDF转Word转换功能
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# 添加API目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from cloudconvert_converter import CloudConvertConverter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CloudConvert API Key
CLOUDCONVERT_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZjJkZjJmOTA0ZDBkZDQyMWVlNWJmOGZkNzBmYWJmMTVhZGI0N2IzYmI0YjkyMzRlNTJmMTYzOTM1YzZmMmNiM2FkMDQ3MDcxZjM0NGIwYmIiLCJpYXQiOjE3NTM1NDk3NzguNTIyOTk1LCJuYmYiOjE3NTM1NDk3NzguNTIyOTk2LCJleHAiOjQ5MDkyMjMzNzguNTE3MzM1LCJzdWIiOiI3MjE1MzE0MSIsInNjb3BlcyI6WyJ0YXNrLnJlYWQiLCJ0YXNrLndyaXRlIl19.O30nWdGoEQzBXEok8MmGEPxJgutrdkwPLGRNx2h1QyIXAoPT_qSwe-kzv5khg5kJVI0CawDb5izpwWNI79AzM7hU-ZpbdQuuQPmdJipNti4Pdt6aaK_foJEiZO9jrhBF4VbGNIy-Tc5wned4AqdEJboYiuqWa4Onnh0VZ5fRz6osOvx1d3bHLfN_nUgX0lGkP0pmBV00CrNomei9LIpMDaHzV60wfyzkQBlYZ-WrpmGP3iBllCpm_hdZLpudGHHZpAjMAjoBwn2cxh1GKbuYbI-JcyWsbfruEo15BZYvK6LmBU-044yJqQvGCSHZ6fqQ2Q5J-TSJH3et9DDHhH8YtC6UZn4v8det0Xo_JPkI0kGdbPTq6-e7UYPhvX3hrvxcNRPh7FQ9A6AMr7jv1iMd6z4oMyZzhMhwkSso1Wf9gx6pSN35LUhRMp0F15AuhbVc4KKHXWbOdU1hrtJzjMUf_oM63f7OJL-T2Bu_4yI92gJUEi91kG5PYZ5RfNIUWxap_rOD30pV-URW5rCKzNNmSrzPG1a3yEPszsLjZ7whcNwnAIYE0Cg3e6Gno_v2x-CJbjZU0zenWIShA2jb1iJEJ1bs_fDhxztEcTqr1-KobhFXXiW_zlMWHW8kmU7p7XpvXOtB2d0W0PU1sdq9OoZs2gbHmyq05fZZbuWRADBsjNc"

async def test_api_connection():
    """测试API连接（通过创建简单任务）"""
    print("🔍 测试CloudConvert API连接...")
    
    converter = CloudConvertConverter(CLOUDCONVERT_API_KEY)
    
    # 由于权限限制，直接测试创建任务而不是访问用户信息
    try:
        job_data = await converter._create_job()
        if job_data:
            print("✅ API连接成功！")
            print(f"📊 任务创建成功，权限验证通过")
            print(f"🎯 任务ID: {job_data['data']['id']}")
            return True
        else:
            print("❌ API连接失败：无法创建任务")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {str(e)}")
        return False

async def create_test_pdf():
    """创建测试PDF文件"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        print("📄 创建测试PDF文件...")
        
        pdf_path = "test_cloudconvert.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # 添加标题
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 100, "CloudConvert 测试文档")
        
        # 添加正文
        c.setFont("Helvetica", 12)
        y_position = height - 150
        
        content = [
            "这是一个测试PDF文档，用于验证CloudConvert的转换质量。",
            "",
            "主要测试内容：",
            "• 中文字符显示",
            "• 英文字符显示 (English characters)",
            "• 数字和符号：123456789 !@#$%^&*()",
            "",
            "表格测试：",
            "姓名    年龄    城市",
            "张三    25     北京",
            "李四    30     上海",
            "王五    28     广州",
            "",
            "这个文档将被转换为Word格式，",
            "我们期望转换后能保持90%以上的格式相似性。"
        ]
        
        for line in content:
            c.drawString(100, y_position, line)
            y_position -= 20
        
        c.save()
        print(f"✅ 测试PDF创建成功: {pdf_path}")
        return pdf_path
        
    except ImportError:
        print("⚠️  reportlab未安装，请手动提供test.pdf文件")
        return None
    except Exception as e:
        print(f"❌ 创建PDF失败: {e}")
        return None

async def test_pdf_conversion():
    """测试PDF转换功能"""
    print("🔄 测试PDF转Word转换...")
    
    # 检查是否有测试PDF
    test_pdf = None
    if os.path.exists("test.pdf"):
        test_pdf = "test.pdf"
        print("📁 使用现有的test.pdf文件")
    else:
        test_pdf = await create_test_pdf()
        if not test_pdf:
            print("❌ 无法创建或找到测试PDF文件")
            return False
    
    # 执行转换
    converter = CloudConvertConverter(CLOUDCONVERT_API_KEY)
    output_path = "cloudconvert_output.docx"
    
    print(f"🚀 开始转换: {test_pdf} -> {output_path}")
    
    success = await converter.convert_pdf_to_word(test_pdf, output_path)
    
    if success:
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ 转换成功！")
            print(f"📄 输出文件: {output_path}")
            print(f"📊 文件大小: {file_size} bytes")
            return True
        else:
            print("❌ 转换报告成功但文件不存在")
            return False
    else:
        print("❌ 转换失败")
        return False

async def main():
    """主测试函数"""
    print("🎯 CloudConvert API 功能测试开始")
    print("=" * 50)
    
    # 测试1: API连接
    connection_ok = await test_api_connection()
    print()
    
    if not connection_ok:
        print("❌ API连接失败，停止后续测试")
        return
    
    # 测试2: PDF转换
    conversion_ok = await test_pdf_conversion()
    print()
    
    # 总结
    print("=" * 50)
    print("📋 测试总结:")
    print(f"API连接: {'✅ 成功' if connection_ok else '❌ 失败'}")
    print(f"PDF转换: {'✅ 成功' if conversion_ok else '❌ 失败'}")
    
    if connection_ok and conversion_ok:
        print("🎉 CloudConvert集成测试完全成功！")
        print("💡 现在可以将其集成到主系统中了！")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    asyncio.run(main()) 