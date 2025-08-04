import requests
import time
import os
import logging
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)

class CloudConvertConverter:
    """CloudConvert API 高质量PDF转Word转换器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.cloudconvert.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def convert_pdf_to_word(self, input_path: str, output_path: str) -> bool:
        """
        使用CloudConvert将PDF转换为Word文档
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出Word文件路径
            
        Returns:
            bool: 转换是否成功
        """
        try:
            logger.info(f"开始CloudConvert转换: {input_path} -> {output_path}")
            
            # 步骤1: 创建任务
            job_data = await self._create_job()
            if not job_data:
                return False
            
            job_id = job_data["data"]["id"]
            import_task_id = None
            convert_task_id = None
            export_task_id = None
            
            # 解析任务ID
            for task in job_data["data"]["tasks"]:
                if task["name"] == "import-pdf":
                    import_task_id = task["id"]
                elif task["name"] == "convert-pdf-to-docx":
                    convert_task_id = task["id"]
                elif task["name"] == "export-docx":
                    export_task_id = task["id"]
            
            logger.info(f"创建任务成功: job_id={job_id}")
            
            # 步骤2: 上传文件
            upload_success = await self._upload_file(import_task_id, input_path)
            if not upload_success:
                return False
            
            # 步骤3: 等待转换完成
            success = await self._wait_for_completion(job_id)
            if not success:
                return False
            
            # 步骤4: 下载结果
            download_success = await self._download_result(export_task_id, output_path)
            return download_success
            
        except Exception as e:
            logger.error(f"CloudConvert转换失败: {str(e)}", exc_info=True)
            return False
    
    async def _create_job(self) -> Optional[Dict[str, Any]]:
        """创建转换任务"""
        try:
            job_payload = {
                "tasks": {
                    "import-pdf": {
                        "operation": "import/upload"
                    },
                    "convert-pdf-to-docx": {
                        "operation": "convert",
                        "input": "import-pdf",
                        "output_format": "docx",
                        "some_other_option": "value"
                    },
                    "export-docx": {
                        "operation": "export/url",
                        "input": "convert-pdf-to-docx"
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/jobs",
                headers=self.headers,
                json=job_payload,
                timeout=30
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"创建任务失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"创建任务异常: {str(e)}")
            return None
    
    async def _upload_file(self, task_id: str, file_path: str) -> bool:
        """上传文件到CloudConvert"""
        try:
            # 获取上传URL
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"获取上传信息失败: {response.status_code}")
                return False
            
            task_data = response.json()
            upload_url = task_data["data"]["result"]["form"]["url"]
            form_data = task_data["data"]["result"]["form"]["parameters"]
            
            # 上传文件
            with open(file_path, 'rb') as f:
                files = {'file': f}
                upload_response = requests.post(
                    upload_url,
                    data=form_data,
                    files=files,
                    timeout=120
                )
            
            if upload_response.status_code in [200, 201]:
                logger.info("文件上传成功")
                return True
            else:
                logger.error(f"文件上传失败: {upload_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"文件上传异常: {str(e)}")
            return False
    
    async def _wait_for_completion(self, job_id: str, max_wait_time: int = 300) -> bool:
        """等待转换完成"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                response = requests.get(
                    f"{self.base_url}/jobs/{job_id}",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"检查任务状态失败: {response.status_code}")
                    return False
                
                job_data = response.json()
                status = job_data["data"]["status"]
                
                logger.info(f"任务状态: {status}")
                
                if status == "finished":
                    logger.info("转换完成")
                    return True
                elif status == "error":
                    logger.error("转换失败")
                    return False
                
                # 等待5秒后再次检查
                await asyncio.sleep(5)
            
            logger.error("转换超时")
            return False
            
        except Exception as e:
            logger.error(f"等待完成异常: {str(e)}")
            return False
    
    async def _download_result(self, task_id: str, output_path: str) -> bool:
        """下载转换结果"""
        try:
            # 获取下载URL
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"获取下载信息失败: {response.status_code}")
                return False
            
            task_data = response.json()
            
            if "result" not in task_data["data"] or "files" not in task_data["data"]["result"]:
                logger.error("下载信息不完整")
                return False
            
            files = task_data["data"]["result"]["files"]
            if not files:
                logger.error("没有找到结果文件")
                return False
            
            download_url = files[0]["url"]
            
            # 下载文件
            download_response = requests.get(download_url, timeout=120)
            
            if download_response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(download_response.content)
                
                logger.info(f"文件下载成功: {output_path}")
                return True
            else:
                logger.error(f"文件下载失败: {download_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"文件下载异常: {str(e)}")
            return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            logger.info("正在测试API连接...")
            logger.info(f"API Key前20字符: {self.api_key[:20]}...")
            logger.info(f"请求URL: {self.base_url}/users/me")
            logger.info(f"请求头: {self.headers}")
            
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=10
            )
            
            logger.info(f"响应状态码: {response.status_code}")
            logger.info(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": "API连接成功",
                    "user_info": user_data["data"]
                }
            else:
                return {
                    "success": False,
                    "message": f"API连接失败: {response.status_code}",
                    "details": response.text,
                    "headers_sent": self.headers
                }
                
        except Exception as e:
            logger.error(f"API连接异常: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"API连接异常: {str(e)}"
            } 