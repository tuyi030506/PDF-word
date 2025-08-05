"""
LibreOffice PDF转Word转换器
支持免费、本地、高质量的PDF到Word转换
"""

import os
import subprocess
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import platform

logger = logging.getLogger(__name__)

class LibreOfficeConverter:
    """LibreOffice命令行转换器"""
    
    def __init__(self):
        self.libreoffice_path = self._find_libreoffice()
        self.is_available = self.libreoffice_path is not None
        
    def _find_libreoffice(self) -> Optional[str]:
        """查找LibreOffice可执行文件路径"""
        possible_paths = []
        
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            possible_paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "/usr/local/bin/soffice",
                "/opt/homebrew/bin/soffice"
            ]
        elif system == "linux":  # Linux
            possible_paths = [
                "/usr/bin/libreoffice",
                "/usr/bin/soffice",
                "/snap/bin/libreoffice",
                "/usr/local/bin/soffice"
            ]
        elif system == "windows":  # Windows
            possible_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
            ]
        
        # 检查PATH中的命令
        for cmd in ["libreoffice", "soffice"]:
            try:
                result = subprocess.run(
                    ["which", cmd] if system != "windows" else ["where", cmd],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    possible_paths.insert(0, result.stdout.strip())
            except:
                pass
        
        # 测试每个可能的路径
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    # 测试是否可以执行
                    result = subprocess.run(
                        [path, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        logger.info(f"Found LibreOffice at: {path}")
                        return path
                except Exception as e:
                    logger.debug(f"Failed to test LibreOffice at {path}: {e}")
                    continue
        
        logger.warning("LibreOffice not found on system")
        return None
    
    def check_installation(self) -> Dict[str, Any]:
        """检查LibreOffice安装状态"""
        if not self.is_available:
            return {
                "installed": False,
                "path": None,
                "version": None,
                "error": "LibreOffice not found"
            }
        
        try:
            result = subprocess.run(
                [self.libreoffice_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            version = result.stdout.strip() if result.returncode == 0 else "Unknown"
            
            return {
                "installed": True,
                "path": self.libreoffice_path,
                "version": version,
                "error": None
            }
        except Exception as e:
            return {
                "installed": False,
                "path": self.libreoffice_path,
                "version": None,
                "error": str(e)
            }
    
    def convert_pdf_to_docx(self, pdf_content: bytes, filename: str = "document.pdf") -> Tuple[bool, bytes, str]:
        """
        使用LibreOffice将PDF转换为DOCX
        
        Args:
            pdf_content: PDF文件的字节内容
            filename: 原始文件名
            
        Returns:
            (success, docx_content, message)
        """
        if not self.is_available:
            return False, b"", "LibreOffice not available on system"
        
        temp_dir = None
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix="pdf2word_")
            
            # 保存PDF文件
            pdf_path = os.path.join(temp_dir, "input.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_content)
            
            # 输出目录
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # LibreOffice转换命令
            cmd = [
                self.libreoffice_path,
                "--headless",  # 无界面模式
                "--convert-to", "docx",  # 转换为docx格式
                "--outdir", output_dir,  # 输出目录
                pdf_path  # 输入文件
            ]
            
            logger.info(f"Running LibreOffice command: {' '.join(cmd)}")
            
            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=temp_dir
            )
            
            if result.returncode != 0:
                error_msg = f"LibreOffice conversion failed: {result.stderr}"
                logger.error(error_msg)
                return False, b"", error_msg
            
            # 查找输出的docx文件
            expected_docx = os.path.join(output_dir, "input.docx")
            
            if not os.path.exists(expected_docx):
                # 查找任何.docx文件
                docx_files = [f for f in os.listdir(output_dir) if f.endswith('.docx')]
                if not docx_files:
                    return False, b"", "No DOCX file generated by LibreOffice"
                expected_docx = os.path.join(output_dir, docx_files[0])
            
            # 读取转换后的docx文件
            with open(expected_docx, "rb") as f:
                docx_content = f.read()
            
            logger.info(f"LibreOffice conversion successful. Output size: {len(docx_content)} bytes")
            return True, docx_content, "LibreOffice conversion successful"
            
        except subprocess.TimeoutExpired:
            return False, b"", "LibreOffice conversion timeout (5 minutes)"
        except Exception as e:
            error_msg = f"LibreOffice conversion error: {str(e)}"
            logger.error(error_msg)
            return False, b"", error_msg
        finally:
            # 清理临时文件
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp directory: {e}")

    def get_installation_instructions(self) -> Dict[str, str]:
        """获取不同平台的LibreOffice安装说明"""
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return {
                "platform": "macOS",
                "method1": "官网下载: https://www.libreoffice.org/download/download/",
                "method2": "Homebrew: brew install --cask libreoffice",
                "note": "安装后重启应用"
            }
        elif system == "linux":  # Linux
            return {
                "platform": "Linux",
                "method1": "Ubuntu/Debian: sudo apt-get install libreoffice",
                "method2": "CentOS/RHEL: sudo yum install libreoffice",
                "method3": "Snap: sudo snap install libreoffice",
                "note": "Docker部署时需要在Dockerfile中添加安装命令"
            }
        elif system == "windows":  # Windows
            return {
                "platform": "Windows",
                "method1": "官网下载: https://www.libreoffice.org/download/download/",
                "method2": "Chocolatey: choco install libreoffice",
                "note": "安装后重启应用"
            }
        else:
            return {
                "platform": "Unknown",
                "method1": "请访问 https://www.libreoffice.org/ 下载适合您系统的版本",
                "note": "安装后重启应用"
            }