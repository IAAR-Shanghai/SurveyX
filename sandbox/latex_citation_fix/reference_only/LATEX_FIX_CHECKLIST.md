# LaTeX 引用問題修復檢查清單

**快速參考**：供 AI Agent 在 Sandbox 環境中驗證修復流程

---

## 📋 修復前檢查清單

### ✅ 環境驗證

- [ ] 確認工作目錄：`outputs/*/latex/`
- [ ] 確認 LaTeX 工具鏈可用：`which pdflatex`
- [ ] 確認 PDF 閱讀器可用（驗證結果）

### ✅ 問題診斷

- [ ] 編譯 PDF：`pdflatex survey.tex`
- [ ] 打開 PDF 尋找 "??" 引用
- [ ] 檢查 aux 檔案：`grep "\\caption@xref" survey.aux`
- [ ] 記錄問題圖表的 label 名稱
- [ ] 檢查圖表檔案大小：`wc -l figs/*.tex` 和 `ls -lh figs/*.tex`
- [ ] 確認問題類型：
  - [ ] 字元不匹配（如 en-dash vs double-hyphen）
  - [ ] 超大型 TikZ 內容（>400 行或 >20KB）
  - [ ] 其他

### ✅ 備份建立

- [ ] 備份問題圖表檔案：`cp fig.tex fig.tex.BEFORE_FIX`
- [ ] 備份主文件（可選）：`cp survey.tex survey.tex.BACKUP`
- [ ] 記錄備份位置和時間戳

---

## 🔧 修復步驟（方案 A：硬編碼編號）

### Step 1：確定圖表實際編號

```bash
# 編譯並檢查 PDF
pdflatex survey.tex

# 記錄圖表編號
# 例如：Figure 5 在第 25 頁，Figure 8 在第 32 頁
```

**記錄**：
- Figure \_\_\_\_\_ (`fig:tree_figure_Langu`) → 編號 \_\_\_\_\_，頁 \_\_\_\_\_
- Figure \_\_\_\_\_ (`fig:tiny_tree_figure_5`) → 編號 \_\_\_\_\_，頁 \_\_\_\_\_

### Step 2：找出引用位置

```bash
# 搜尋引用
grep -n "\\ref{fig:tree_figure_Langu}" survey.tex
grep -n "\\ref{fig:tiny_tree_figure_5}" survey.tex
```

**記錄**：
- Line \_\_\_\_\_：`\ref{fig:tree_figure_Langu}`
- Line \_\_\_\_\_：`\ref{fig:tiny_tree_figure_5}`

### Step 3：執行替換

```bash
# 方法 1：使用 sed（macOS）
sed -i '' 's/Figure~\\ref{fig:tree_figure_Langu}/Figure~5/g' survey.tex
sed -i '' 's/Figure~\\ref{fig:tiny_tree_figure_5}/Figure~8/g' survey.tex

# 方法 2：使用 AI Agent 的 replace_string_in_file 工具
# 參考 docs/LATEX_CAPTION_XREF_FIX.md 第 596 和 721 行的範例
```

### Step 4：清理並重新編譯

```bash
# 清理臨時檔案
rm -f survey.aux survey.log survey.out survey.pdf survey.toc

# 重新編譯
pdflatex -interaction=nonstopmode survey.tex
```

**預期輸出**：
```
Output written on survey.pdf (XX pages, XXXXXX bytes).
```

### Step 5：驗證結果

- [ ] 打開 `survey.pdf`
- [ ] 檢查第 \_\_\_\_\_ 頁：圖表 5 是否完整顯示
- [ ] 檢查第 \_\_\_\_\_ 頁：圖表 8 是否完整顯示
- [ ] 檢查引用處：是否顯示 "Figure 5" 和 "Figure 8" 而非 "??"
- [ ] 檢查 aux 檔案：`grep "caption@xref" survey.aux`（應該仍存在但不影響）

---

## 🔍 驗證測試用例

### Test Case 1：字元匹配問題

**輸入**：
```latex
% structure_fig.tex
\node (subsec13-4) at (15.5, -16.5) {13.4 Bandwidth and edge–server};
% survey.tex
\subsection{Bandwidth and edge--server trade-offs}
\label{subsec:Bandwidth and edge--server trade-offs}
```

**診斷**：
```bash
grep "subsec:Bandwidth" survey.aux
# 應該找到 \newlabel 但 label 中是 -- 而非 –
```

**修復**：
```latex
% 修改 structure_fig.tex 為：
\node (subsec13-4) at (15.5, -16.5) {13.4 Bandwidth and edge--server};
```

**驗證**：
```bash
pdflatex survey.tex
grep "subsec:Bandwidth and edge--server" survey.aux
# 應該找到正確的 \newlabel
```

### Test Case 2：超大型 TikZ

**輸入**：
```bash
wc -l figs/tree_figure_Langu.tex
# 輸出：480
ls -lh figs/tree_figure_Langu.tex
# 輸出：26K
```

**診斷**：
```bash
grep "fig:tree_figure_Langu" survey.aux
# 輸出：\newlabel{fig:tree_figure_Langu}{{\caption@xref ...
```

**修復**：採用方案 A（硬編碼）

**驗證**：
```bash
grep "Figure~5" survey.tex
# 應該找到替換後的硬編碼引用
```

---

## ❌ 失敗案例記錄

### 失敗方案：Externalization（方案 B）

**不要嘗試**以下步驟（已證實失敗）：

```bash
# ❌ 建立 standalone 檔案
cat > figs/fig_standalone.tex << 'EOF'
\documentclass[tikz,border=2mm]{standalone}
...
EOF

# ❌ 編譯 standalone
pdflatex figs/fig_standalone.tex

# ❌ 修改主圖表為 includegraphics
# 結果：圖表消失（PDF 高度為 0）
```

**問題診斷**：
```bash
pdfinfo figs/fig_standalone.pdf | grep "Page size"
# 輸出：Page size: 343.711 x 0 pts  ← 高度為 0！
```

**根本原因**：
- TikZ 使用絕對座標（81-153）
- Standalone 邊界框計算失敗
- 結果：圖表不可見

---

## 🚀 完整自動化腳本（方案 A）

```bash
#!/bin/bash
# fix_latex_refs.sh - 自動修復 LaTeX 引用問題

set -e

LATEX_DIR="outputs/2025-10-09-1630_speec/latex"
cd "$LATEX_DIR"

echo "🔍 診斷問題..."
# 檢查 caption@xref
if grep -q "\\caption@xref" survey.aux; then
    echo "✅ 找到 \\caption@xref 問題"
    grep "\\caption@xref" survey.aux
else
    echo "❌ 未找到 caption@xref 問題"
    exit 1
fi

echo ""
echo "📦 建立備份..."
cp figs/tree_figure_Langu.tex figs/tree_figure_Langu.tex.BEFORE_FIX
cp figs/tiny_tree_figure_5.tex figs/tiny_tree_figure_5.tex.BEFORE_FIX
echo "✅ 備份完成"

echo ""
echo "🔧 執行修復..."
# 替換引用
sed -i '' 's/Figure~\\ref{fig:tree_figure_Langu}/Figure~5/g' survey.tex
sed -i '' 's/Figure~\\ref{fig:tiny_tree_figure_5}/Figure~8/g' survey.tex
echo "✅ 引用已替換"

echo ""
echo "🧹 清理臨時檔案..."
rm -f survey.aux survey.log survey.out survey.pdf survey.toc
echo "✅ 臨時檔案已清理"

echo ""
echo "🔨 重新編譯..."
pdflatex -interaction=nonstopmode survey.tex > /dev/null 2>&1
if [ -f survey.pdf ]; then
    echo "✅ 編譯成功！"
    echo "📄 PDF 大小：$(ls -lh survey.pdf | awk '{print $5}')"
    echo "📄 總頁數：$(pdfinfo survey.pdf | grep Pages | awk '{print $2}')"
else
    echo "❌ 編譯失敗"
    exit 1
fi

echo ""
echo "🎉 修復完成！請檢查 survey.pdf"
```

**使用方法**：
```bash
chmod +x fix_latex_refs.sh
./fix_latex_refs.sh
```

---

## 📊 驗證檢查清單

### ✅ 編譯驗證

- [ ] PDF 成功生成
- [ ] 無 LaTeX 錯誤
- [ ] 警告數量可接受（<10）

### ✅ 內容驗證

- [ ] 圖表 5 完整顯示
- [ ] 圖表 8 完整顯示
- [ ] 引用顯示正確數字
- [ ] 無 "??" 引用

### ✅ 文件驗證

- [ ] 備份檔案存在：`ls figs/*.BEFORE_FIX`
- [ ] 修復記錄已更新：`docs/LATEX_CAPTION_XREF_FIX.md`
- [ ] 檢查清單已填寫：本文件

---

## 🐛 常見問題排查

### Q1：編譯後仍然顯示 "??"

**可能原因**：
1. 替換未生效
2. 緩存污染

**解決方法**：
```bash
# 1. 確認替換
grep "Figure~5\|Figure~8" survey.tex

# 2. 徹底清理
rm -f survey.* texput.log
pdflatex survey.tex
```

### Q2：圖表消失（空白）

**可能原因**：
1. 誤用了 standalone PDF
2. 圖表檔案損壞

**解決方法**：
```bash
# 還原備份
cp figs/tree_figure_Langu.tex.BEFORE_FIX figs/tree_figure_Langu.tex
cp figs/tiny_tree_figure_5.tex.BEFORE_FIX figs/tiny_tree_figure_5.tex

# 清理 standalone 檔案
rm -f figs/*_standalone.*

# 重新編譯
rm -f survey.*
pdflatex survey.tex
```

### Q3：Emergency stop 錯誤

**可能原因**：
1. 語法錯誤
2. 缺少結束符號

**解決方法**：
```bash
# 1. 檢查錯誤日誌
tail -50 survey.log

# 2. 檢查括號匹配
grep -c "\\begin{adjustbox}" figs/tree_figure_Langu.tex
grep -c "\\end{adjustbox}" figs/tree_figure_Langu.tex
# 兩者應該相等

# 3. 還原備份重試
```

---

## 📝 修復記錄模板

**日期**：\_\_\_\_\_\_\_\_  
**問題 ID**：\_\_\_\_\_\_\_\_  
**執行者**：\_\_\_\_\_\_\_\_

### 診斷結果

- 問題圖表：
  - [ ] `tree_figure_Langu.tex` (\_\_\_\_\_ 行, \_\_\_\_\_ KB)
  - [ ] `tiny_tree_figure_5.tex` (\_\_\_\_\_ 行, \_\_\_\_\_ KB)
  - [ ] 其他：\_\_\_\_\_\_\_\_

- 問題類型：
  - [ ] `\caption@xref` 佔位符
  - [ ] 字元不匹配
  - [ ] 其他：\_\_\_\_\_\_\_\_

### 採用方案

- [ ] 方案 A：硬編碼圖表編號
- [ ] 方案 C：拆分大型圖表
- [ ] 其他：\_\_\_\_\_\_\_\_

### 修改內容

- `survey.tex` 第 \_\_\_\_\_ 行：`\ref{...}` → `5`
- `survey.tex` 第 \_\_\_\_\_ 行：`\ref{...}` → `8`
- 其他：\_\_\_\_\_\_\_\_

### 驗證結果

- [ ] ✅ 編譯成功
- [ ] ✅ 圖表完整顯示
- [ ] ✅ 引用顯示正確
- [ ] ✅ 無新增錯誤

### 備份位置

- `figs/tree_figure_Langu.tex.BEFORE_FIX`
- `figs/tiny_tree_figure_5.tex.BEFORE_FIX`
- 其他：\_\_\_\_\_\_\_\_

---

**文件版本**：1.0  
**最後更新**：2025-10-17  
**配套文件**：`docs/LATEX_CAPTION_XREF_FIX.md`
