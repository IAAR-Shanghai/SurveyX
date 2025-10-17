#!/bin/bash
#
# 一鍵編譯腳本 - broken 版本（問題版本）
# 
# 此版本包含以下問題：
# 1. survey.tex 中有 2 處 \ref{} 引用會顯示 "??"
#    - Line ~596: \ref{fig:tree_figure_Langu}
#    - Line ~721: \ref{fig:tiny_tree_figure_5}
# 2. figs/structure_fig.tex 包含 en-dash 字元（U+2013）
#

set -e  # 遇到錯誤時停止

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🔨 編譯 broken 版本（問題版本）                          ║"
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
        echo "關鍵問題引用："
        grep "LaTeX Warning.*undefined" survey.log | grep -E "tree_figure_Langu|tiny_tree_figure_5" || true
        echo ""
        echo "💡 這是預期行為 - broken 版本應該包含這些問題"
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
