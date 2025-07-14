#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF转换功能测试脚本
"""

import requests
import os
import time

def test_pdf_conversion():
    """测试PDF转换功能"""
    
    # 测试文件路径
    test_pdf = "test.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"❌ 测试文件不存在: {test_pdf}")
        return False
    
    print(f"📄 开始测试PDF转换: {test_pdf}")
    
    # 准备文件上传
    with open(test_pdf, 'rb') as f:
        files = {'file': (test_pdf, f, 'application/pdf')}
        
        try:
            print("🔄 发送转换请求...")
            start_time = time.time()
            
            response = requests.post(
                'http://localhost:8000/api/convert',
                files=files,
                timeout=60  # 60秒超时
            )
            
            end_time = time.time()
            print(f"⏱️  请求耗时: {end_time - start_time:.2f}秒")
            
            if response.status_code == 200:
                print("✅ 转换成功!")
                
                # 保存转换结果
                output_filename = f"converted_{int(time.time())}.docx"
                with open(output_filename, 'wb') as f:
                    f.write(response.content)
                
                print(f"📁 转换结果已保存: {output_filename}")
                print(f"📊 文件大小: {len(response.content)} bytes")
                return True
                
            else:
                print(f"❌ 转换失败: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"🔍 错误详情: {error_detail}")
                except:
                    print(f"🔍 错误内容: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ 请求超时")
            return False
        except requests.exceptions.ConnectionError:
            print("🔌 连接错误，请确保服务器正在运行")
            return False
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务器健康: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 开始PDF转换功能测试")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health_check():
        print("❌ 服务器不健康，退出测试")
        exit(1)
    
    print()
    
    # 测试PDF转换
    if test_pdf_conversion():
        print("\n🎉 所有测试通过!")
    else:
        print("\n💥 测试失败!") 