#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Render配置测试脚本
验证所有必要的文件和配置是否正确
"""

import os
import sys
from pathlib import Path

def test_file_exists(file_path, description):
    """测试文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (文件不存在)")
        return False

def test_import_module(module_name, description):
    """测试模块是否可以导入"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} (导入失败: {e})")
        return False

def main():
    print("🔍 Render配置测试")
    print("=" * 50)
    
    # 测试必要文件
    required_files = [
        ("start.py", "启动脚本"),
        ("api/render_app.py", "Render应用文件"),
        ("requirements-render.txt", "Render依赖文件"),
        ("runtime.txt", "Python版本配置"),
        ("render.yaml", "Render部署配置"),
    ]
    
    file_ok = True
    for file_path, description in required_files:
        if not test_file_exists(file_path, description):
            file_ok = False
    
    print("\n📦 测试依赖导入")
    print("-" * 30)
    
    # 测试核心依赖
    core_deps = [
        ("fastapi", "FastAPI框架"),
        ("uvicorn", "ASGI服务器"),
        ("python-multipart", "文件上传支持"),
        ("pdf2docx", "PDF转Word库"),
    ]
    
    dep_ok = True
    for module, description in core_deps:
        if not test_import_module(module, description):
            dep_ok = False
    
    print("\n🔧 测试应用启动")
    print("-" * 30)
    
    try:
        # 测试应用导入
        from api.render_app import app
        print("✅ 应用导入成功")
        
        # 测试健康检查端点
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ 健康检查端点正常")
        else:
            print(f"❌ 健康检查端点异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 应用启动测试失败: {e}")
    
    print("\n📋 总结")
    print("=" * 50)
    
    if file_ok and dep_ok:
        print("🎉 所有测试通过！配置正确，可以部署到Render")
    else:
        print("⚠️  发现问题，请修复后再部署")
        print("\n建议修复步骤:")
        print("1. 确保所有必要文件存在")
        print("2. 安装缺失的依赖: pip install -r requirements-render.txt")
        print("3. 检查Python版本是否为3.11.9")
        print("4. 验证应用可以正常启动")

if __name__ == "__main__":
    main() 