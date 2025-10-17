#!/bin/bash
#
# 修復 Unicode glitch 並重新編譯 LaTeX
# 
# 使用方式:
#   bash scripts/fix_and_recompile.sh <task_id>
#
# 範例:
#   bash scripts/fix_and_recompile.sh 2025-10-09-1630_speec
#

set -e  # 遇到錯誤立即停止

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查參數
if [ $# -eq 0 ]; then
    echo -e "${RED}錯誤: 請提供 task_id${NC}"
    echo "使用方式: bash scripts/fix_and_recompile.sh <task_id>"
    echo "範例:     bash scripts/fix_and_recompile.sh 2025-10-09-1630_speec"
    exit 1
fi

TASK_ID="$1"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
OUTPUT_DIR="$BASE_DIR/outputs/$TASK_ID"
LATEX_DIR="$OUTPUT_DIR/latex"
TEX_FILE="$LATEX_DIR/survey.tex"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Unicode Glitch 修復與重新編譯${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Task ID: $TASK_ID"
echo "Base Directory: $BASE_DIR"
echo ""

# 檢查目錄是否存在
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${RED}錯誤: 找不到目錄 $OUTPUT_DIR${NC}"
    exit 1
fi

if [ ! -f "$TEX_FILE" ]; then
    echo -e "${RED}錯誤: 找不到檔案 $TEX_FILE${NC}"
    exit 1
fi

# 切換到專案根目錄
cd "$BASE_DIR"

# ============================================
# Step 1: 偵測 Unicode 符號
# ============================================
echo -e "${YELLOW}[Step 1/4] 偵測 Unicode 符號...${NC}"
python scripts/detect_unicode_glitches.py "$TEX_FILE" -o "$OUTPUT_DIR/tmp/unicode_report_before.txt"

# 讀取偵測結果
UNICODE_COUNT=$(grep "Total Unicode symbols found:" "$OUTPUT_DIR/tmp/unicode_report_before.txt" | grep -o '[0-9]\+')

if [ "$UNICODE_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ 沒有發現 Unicode 符號,檔案已經是乾淨的!${NC}"
    exit 0
else
    echo -e "${YELLOW}  發現 $UNICODE_COUNT 個 Unicode 符號${NC}"
fi

# ============================================
# Step 2: 備份原檔案
# ============================================
echo ""
echo -e "${YELLOW}[Step 2/4] 備份原檔案...${NC}"
BACKUP_FILE="$TEX_FILE.backup_$(date +%Y%m%d_%H%M%S)"
cp "$TEX_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓ 備份已儲存: $BACKUP_FILE${NC}"

# ============================================
# Step 3: 修復 Unicode 符號
# ============================================
echo ""
echo -e "${YELLOW}[Step 3/4] 修復 Unicode 符號...${NC}"
python scripts/fix_unicode_glitches.py "$TEX_FILE" --no-backup

# 驗證修復結果
python scripts/detect_unicode_glitches.py "$TEX_FILE" -o "$OUTPUT_DIR/tmp/unicode_report_after.txt"
UNICODE_COUNT_AFTER=$(grep "Total Unicode symbols found:" "$OUTPUT_DIR/tmp/unicode_report_after.txt" | grep -o '[0-9]\+')

if [ "$UNICODE_COUNT_AFTER" -eq 0 ]; then
    echo -e "${GREEN}✓ 所有 Unicode 符號已成功修復!${NC}"
else
    echo -e "${RED}警告: 仍有 $UNICODE_COUNT_AFTER 個 Unicode 符號未修復${NC}"
fi

# ============================================
# Step 4: 重新編譯 LaTeX
# ============================================
echo ""
echo -e "${YELLOW}[Step 4/4] 重新編譯 LaTeX...${NC}"

# 刪除舊的 PDF (如果存在)
if [ -f "$OUTPUT_DIR/survey.pdf" ]; then
    rm "$OUTPUT_DIR/survey.pdf"
    echo "  - 已刪除舊的 survey.pdf"
fi

if [ -f "$OUTPUT_DIR/survey_wtmk.pdf" ]; then
    rm "$OUTPUT_DIR/survey_wtmk.pdf"
    echo "  - 已刪除舊的 survey_wtmk.pdf"
fi

# 進入 latex 目錄
cd "$LATEX_DIR"

# 複製 style 檔案
cp "$BASE_DIR/resources/latex/neurips_2024.sty" ./

# 編譯 LaTeX (重定向輸出到 compile.log)
echo "  - 執行 latexmk (這可能需要幾分鐘)..."
latexmk -pdf -interaction=nonstopmode -f survey.tex > compile_fixed.log 2>&1

# 檢查是否生成 PDF
if [ -f "survey.pdf" ]; then
    echo -e "${GREEN}✓ PDF 編譯成功!${NC}"
    
    # 清理中間檔案
    latexmk -c >> compile_fixed.log 2>&1
    rm -f *.bbl
    rm -f neurips_2024.sty
    
    # 移動 PDF 到上層目錄
    mv survey.pdf ../
    
    # 加上浮水印 (使用 Python)
    cd "$BASE_DIR"
    python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('$BASE_DIR')))
from src.models.generator import LatexGenerator
latex_gen = LatexGenerator(task_id='$TASK_ID')
latex_gen.add_watermark(
    Path('$OUTPUT_DIR/survey.pdf'),
    Path('$OUTPUT_DIR/survey_wtmk.pdf'),
    Path('$BASE_DIR/resources/latex/watermark.png')
)
print('✓ 浮水印已加入')
"
    
else
    echo -e "${RED}✗ PDF 編譯失敗,請檢查 $LATEX_DIR/compile_fixed.log${NC}"
    exit 1
fi

# ============================================
# 完成
# ============================================
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ 完成!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "結果檔案:"
echo "  - 修復後的 TEX: $TEX_FILE"
echo "  - 原始備份:     $BACKUP_FILE"
echo "  - 新的 PDF:     $OUTPUT_DIR/survey.pdf"
echo "  - 有浮水印版本: $OUTPUT_DIR/survey_wtmk.pdf"
echo ""
echo "檢查報告:"
echo "  - 修復前: $OUTPUT_DIR/tmp/unicode_report_before.txt"
echo "  - 修復後: $OUTPUT_DIR/tmp/unicode_report_after.txt"
echo "  - 編譯日誌: $LATEX_DIR/compile_fixed.log"
echo ""
echo -e "${YELLOW}提示: 你可以用以下指令驗證 spacing glitch 是否消失:${NC}"
echo "  pdftotext $OUTPUT_DIR/survey.pdf - | grep -E 'acommonpointuses|DiffSoundStream'"
echo ""
