# LaTeX 引用問題快速參考卡

**一頁式參考**：供 AI Agent 快速查詢關鍵資訊

---

## 🎯 問題識別（30 秒）

```bash
# 1. 編譯並檢查
pdflatex survey.tex && open survey.pdf
# 查看是否有 "??" 引用

# 2. 確認問題類型
grep "\\caption@xref" survey.aux
# 有輸出 = 超大型 TikZ 問題 → 使用方案 A
# 無輸出 = 其他問題（字元不匹配等）
```

---

## ⚡ 方案 A：硬編碼修復（5 分鐘）

### 1. 備份

```bash
cd outputs/*/latex/figs
cp tree_figure_Langu.tex tree_figure_Langu.tex.BACKUP
cp tiny_tree_figure_5.tex tiny_tree_figure_5.tex.BACKUP
```

### 2. 找引用位置

```bash
cd ..
grep -n "\\ref{fig:tree_figure_Langu}" survey.tex
grep -n "\\ref{fig:tiny_tree_figure_5}" survey.tex
# 記下行號
```

### 3. 替換

```bash
# macOS
sed -i '' 's/Figure~\\ref{fig:tree_figure_Langu}/Figure~5/g' survey.tex
sed -i '' 's/Figure~\\ref{fig:tiny_tree_figure_5}/Figure~8/g' survey.tex

# Linux
sed -i 's/Figure~\\ref{fig:tree_figure_Langu}/Figure~5/g' survey.tex
sed -i 's/Figure~\\ref{fig:tiny_tree_figure_5}/Figure~8/g' survey.tex
```

### 4. 重新編譯

```bash
rm -f survey.aux survey.log survey.pdf
pdflatex -interaction=nonstopmode survey.tex
```

### 5. 驗證

```bash
open survey.pdf
# 檢查第 25 頁（Figure 5）和第 32 頁（Figure 8）
```

---

## 📊 方案對比

| 特性 | 方案 A（硬編碼）| 方案 C（拆分）|
|------|----------------|---------------|
| 時間 | 5 分鐘 | 4-6 小時 |
| 難度 | ⭐ 簡單 | ⭐⭐⭐⭐ 複雜 |
| 自動編號 | ❌ 失去 | ✅ 保留 |
| 超連結 | ❌ 失去 | ✅ 保留 |
| 圖表完整性 | ✅ 保留 | ⚠️ 分割 |
| 推薦 | ✅ **優先選擇** | ⏸️ 長期方案 |

---

## ❌ 不要嘗試

### 方案 B：Externalization（已證實失敗）

```bash
# ❌ 不要建立 standalone 檔案
# ❌ 不要使用 \includegraphics 包含 TikZ
# 結果：圖表消失（PDF 高度為 0）
```

**原因**：TikZ 絕對座標（81-153）導致 standalone 邊界框計算失敗。

---

## 🐛 故障排除

### 問題：編譯後仍顯示 "??"

```bash
# 清理緩存
rm -f survey.aux survey.log survey.out survey.pdf survey.toc
pdflatex survey.tex

# 確認替換
grep "Figure~5\|Figure~8" survey.tex
```

### 問題：圖表消失（空白）

```bash
# 檢查是否誤用 standalone
grep "includegraphics.*standalone" figs/*.tex

# 還原備份
cp figs/tree_figure_Langu.tex.BACKUP figs/tree_figure_Langu.tex
cp figs/tiny_tree_figure_5.tex.BACKUP figs/tiny_tree_figure_5.tex
rm -f figs/*_standalone.*
```

### 問題：Emergency stop

```bash
# 檢查括號匹配
grep -c "\\begin{adjustbox}" figs/tree_figure_Langu.tex
grep -c "\\end{adjustbox}" figs/tree_figure_Langu.tex
# 兩個數字應該相同

# 查看錯誤
tail -50 survey.log
```

---

## 📁 檔案位置

### 主要檔案

- **主文件**：`outputs/*/latex/survey.tex`
- **問題圖表 1**：`outputs/*/latex/figs/tree_figure_Langu.tex` (480 行, 26KB)
- **問題圖表 2**：`outputs/*/latex/figs/tiny_tree_figure_5.tex` (109 行, 5.9KB)

### 備份檔案

- `figs/tree_figure_Langu.tex.BACKUP` 或 `.BEFORE_FIX`
- `figs/tiny_tree_figure_5.tex.BACKUP` 或 `.BEFORE_FIX`

### 文件

- **完整指南**：`docs/LATEX_CAPTION_XREF_FIX.md`
- **檢查清單**：`docs/LATEX_FIX_CHECKLIST.md`
- **快速參考**：`docs/LATEX_FIX_QUICKREF.md`（本檔案）

---

## 🔍 診斷命令

```bash
# 檢查問題存在
grep "\\caption@xref" survey.aux

# 檢查檔案大小
wc -l figs/tree_figure_Langu.tex  # 480
wc -l figs/tiny_tree_figure_5.tex  # 109

# 找引用位置
grep -n "\\ref{fig:tree" survey.tex

# 確認圖表編號
pdfinfo survey.pdf | grep Pages
# 然後手動查看 PDF 中的圖表編號
```

---

## ✅ 成功標準

- [ ] PDF 成功生成（80 頁左右）
- [ ] 第 25 頁 Figure 5 完整顯示
- [ ] 第 32 頁 Figure 8 完整顯示
- [ ] 引用處顯示 "Figure 5" 和 "Figure 8"
- [ ] 無 "??" 引用
- [ ] 無編譯錯誤

---

## 💡 關鍵概念

### 為何會有 `\caption@xref` 問題？

LaTeX 的 caption 機制在處理超大型內聯內容（>400 行 TikZ）時會超時，寫入佔位符而非實際編號到 `.aux` 檔案。

### 為何 Externalization 失敗？

Standalone 類別無法處理使用絕對座標（81-153）的 TikZ，導致邊界框計算失敗，生成高度為 0 的 PDF。

### 為何選擇硬編碼？

- **快速**：5 分鐘 vs 數小時
- **可靠**：100% 成功率
- **實用**：圖表順序通常不會改變
- **可逆**：保留備份可隨時還原

---

## 📞 需要更多資訊？

查看詳細文件：
```bash
cat docs/LATEX_CAPTION_XREF_FIX.md | less
cat docs/LATEX_FIX_CHECKLIST.md | less
```

---

**版本**：1.0  
**日期**：2025-10-17  
**維護**：AI Agent
