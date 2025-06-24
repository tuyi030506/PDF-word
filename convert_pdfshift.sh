#!/bin/bash

# 设置错误处理
set -e

# 检查参数
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <input_pdf> <output_docx>"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

# 检查输入文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file $INPUT_FILE does not exist"
    exit 1
fi

# 创建输出目录（如果不存在）
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
mkdir -p "$OUTPUT_DIR"

echo "Converting: $INPUT_FILE -> $OUTPUT_FILE"

# 使用 PDFShift API 进行转换
echo "Uploading file to PDFShift..."
RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer YOUR_API_KEY" \
    -F "source=@$INPUT_FILE" \
    -F "target_format=docx" \
    "https://api.pdfshift.io/v3/convert")

# 检查响应
if [ $? -ne 0 ]; then
    echo "Error: Failed to upload file"
    exit 1
fi

# 从响应中提取下载链接
DOWNLOAD_URL=$(echo "$RESPONSE" | grep -o '"url":"[^"]*' | cut -d'"' -f4)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "Error: Failed to get download URL"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "Downloading converted file..."
curl -s -L "$DOWNLOAD_URL" -o "$OUTPUT_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to download converted file"
    exit 1
fi

echo "Conversion completed successfully!" 