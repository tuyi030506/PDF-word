#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CloudConvert高质量转换服务
完整的端到端测试
"""

import requests
import os
import time
import json

def test_cloudconvert_service():
    """测试CloudConvert服务的完整流程"""
    print("🎯 CloudConvert高质量转换服务测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. 测试健康检查
    print("1️⃣ 测试服务健康状态...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 服务健康状态：")
            print(f"   状态: {health_data['status']}")
            print(f"   版本: {health_data['version']}")
            print(f"   API提供商: {health_data['api_provider']}")
            print(f"   质量: {health_data['quality']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接服务: {e}")
        return False
    
    print()
    
    # 2. 测试统计接口
    print("2️⃣ 测试服务统计信息...")
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ 服务统计：")
            print(f"   质量保证: {stats['quality_guarantee']}")
            print(f"   支持特性: {', '.join(stats['supported_features'])}")
            print(f"   文件大小限制: {stats['file_size_limit']}")
        else:
            print(f"❌ 统计信息获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计信息请求异常: {e}")
    
    print()
    
    # 3. 准备测试文件
    print("3️⃣ 准备测试PDF文件...")
    test_pdf_path = None
    
    # 检查现有的测试文件
    test_files = ["test.pdf", "test_cloudconvert.pdf"]
    for file in test_files:
        if os.path.exists(file):
            test_pdf_path = file
            print(f"✅ 找到测试文件: {test_pdf_path}")
            break
    
    if not test_pdf_path:
        print("❌ 未找到测试PDF文件")
        print("   请运行 python3 test_cloudconvert.py 创建测试文件")
        return False
    
    print()
    
    # 4. 测试PDF转换
    print("4️⃣ 测试PDF转Word转换...")
    try:
        with open(test_pdf_path, 'rb') as f:
            files = {'file': (test_pdf_path, f, 'application/pdf')}
            
            print(f"🚀 上传文件: {test_pdf_path} ({os.path.getsize(test_pdf_path)} bytes)")
            
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/convert",
                files=files,
                timeout=120  # 2分钟超时
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ 转换成功！")
                print(f"   处理时间: {end_time - start_time:.2f}秒")
                print(f"   转换方法: {result['conversion_method']}")
                print(f"   输出文件: {result['filename']}")
                print(f"   服务器处理时间: {result['processing_time']}")
                
                # 显示转换详情
                if 'conversion_info' in result:
                    info = result['conversion_info']
                    print("🎯 转换详情:")
                    print(f"   方法: {info['method']}")
                    print(f"   质量: {info['quality']}")
                    print(f"   输入大小: {info['input_size']} bytes")
                    print(f"   输出大小: {info['output_size']} bytes")
                    print(f"   特性: {', '.join(info['features'])}")
                
                # 测试下载
                print("\n5️⃣ 测试文件下载...")
                download_url = f"{base_url}{result['download_url']}"
                download_response = requests.get(download_url, timeout=30)
                
                if download_response.status_code == 200:
                    output_filename = f"test_output_{int(time.time())}.docx"
                    with open(output_filename, 'wb') as f:
                        f.write(download_response.content)
                    
                    print(f"✅ 文件下载成功: {output_filename}")
                    print(f"   下载大小: {len(download_response.content)} bytes")
                    
                    return True
                else:
                    print(f"❌ 文件下载失败: {download_response.status_code}")
                    return False
                    
            else:
                print(f"❌ 转换失败: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   错误详情: {error_data.get('detail', '未知错误')}")
                except:
                    print(f"   错误内容: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 转换测试异常: {e}")
        return False

def main():
    """主测试函数"""
    success = test_cloudconvert_service()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 CloudConvert服务测试完全成功！")
        print("💡 系统已准备好进行高质量PDF转换！")
        print("\n🌐 在浏览器中访问：http://localhost:8000")
    else:
        print("❌ 测试失败，请检查服务配置")

if __name__ == "__main__":
    main() 