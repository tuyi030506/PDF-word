# PDF to Word 转换工具

高保真 PDF 转 Word 转换工具，保持原始格式不变。

## 功能特点

- 保持原始排版格式
- 支持表格转换
- 支持图片提取
- 保持页眉页脚
- 支持目录生成
- 详细的转换日志

## 系统要求

- Python 3.7 或更高版本
- LibreOffice（用于初步转换）
- 足够的系统内存（建议 4GB 以上）

## 安装

1. 安装 LibreOffice：

   - macOS:
     ```bash
     brew install libreoffice
     ```
   
   - Linux:
     ```bash
     sudo apt-get install libreoffice
     ```
   
   - Windows:
     从 [LibreOffice 官网](https://www.libreoffice.org/download/download/) 下载安装

2. 安装 Python 依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 基本用法：

   ```bash
   python src/pdf2word.py input.pdf [output_dir]
   ```

2. 参数说明：
   - `input.pdf`: 输入的 PDF 文件路径
   - `output_dir`: （可选）输出目录，默认为 "output"

## 注意事项

1. 确保 PDF 文件没有加密保护
2. 对于特别大的 PDF 文件，建议确保有足够的系统内存
3. 转换过程中请勿关闭程序
4. 如果出现格式问题，请查看转换日志了解详情

## 常见问题

1. LibreOffice 未找到
   - 确保 LibreOffice 已正确安装
   - 确保 `soffice` 命令可在终端中运行

2. 内存不足
   - 关闭其他占用内存的程序
   - 对于大文件，建议使用更多内存的机器

3. 表格识别问题
   - 确保 PDF 中的表格边框清晰
   - 检查转换日志中的警告信息

## 开发计划

- [ ] 改进表格识别算法
- [ ] 添加批量转换功能
- [ ] 支持更多 PDF 特性
- [ ] 添加 GUI 界面

## 许可证

MIT License 