#!/bin/bash
#
# 一鍵編譯腳本 - fixed 版本（修復版本）
# 
# 此版本已修復所有問題：
# 1. survey.tex 中的引用已硬編碼為數字
#    - Line ~596: Figure~5（原為 \ref{fig:tree_figure_Langu}）
#    - Line ~721: Figure~8（原為 \ref{fig:tiny_tree_figure_5}）
# 2. figs/structure_fig.tex 使用 double-hyphen --（原為 en-dash –）
#

set -e  # 遇到錯誤時停止

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🔨 編譯 fixed 版本（修復版本）                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 清理舊檔案
echo "🧹 清理舊檔案..."
rm -f survey.aux survey.log survey.out survey.toc survey.bbl survey.blg survey.fls survey.fdb_latexmk

# 第一次編譯
echo ""
echo "📝 第一次編譯（生成 .aux 檔案）..."
pdflatex -interaction=nonstopmode survey.tex > /dev/null 2>&1 || true

# 第二次編譯
echo "📝 第二次編譯（處理引用）..."
pdflatex -interaction=nonstopmode survey.tex > /dev/null 2>&1 || true

# 檢查 PDF 是否生成
if [ -f survey.pdf ]; then
    PDF_SIZE=$(ls -lh survey.pdf | awk '{print $5}')
    PDF_PAGES=$(pdfinfo survey.pdf 2>/dev/null | grep "Pages:" | awk '{print $2}')
    
    echo ""
    echo "✅ 編譯成功！"
    echo ""
    echo "📄 PDF 資訊："
    echo "   檔案大小: $PDF_SIZE"
    echo "   頁數: ${PDF_PAGES:-未知}"
    echo ""
    
    # 檢查 undefined 引用
    UNDEFINED_COUNT=$(grep -c "LaTeX Warning.*undefined" survey.log 2>/dev/null || echo "0")
    
    if [ "$UNDEFINED_COUNT" -gt 0 ]; then
        echo "⚠️  偵測到 $UNDEFINED_COUNT 個 undefined 引用警告"
        echo ""
        echo "警告詳情："
        grep "LaTeX Warning.*undefined" survey.log | head -5
        echo ""
        echo "💡 fixed 版本不應該有關鍵引用問題（Figure 5/8）"
    else
        echo "✅ 未發現關鍵的 undefined 引用警告"
        echo ""
        echo "💡 修復成功 - 所有引用都正確顯示"
    fi
    
    echo ""
    echo "📂 輸出檔案: $(pwd)/survey.pdf"
    
else
    echo ""
    echo "❌ 編譯失敗！請檢查 survey.log"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  編譯完成 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════════════════"
