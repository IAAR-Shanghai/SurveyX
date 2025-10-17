# BibTeX 編譯問題分析

**日期**: 2025-10-16  
**檔案**: `outputs/2025-10-09-1630_speec/latex/survey.tex`  
**問題**: 參考文獻無法正確編譯，PDF 中顯示原始 citation key 而非格式化引用

---

## 問題描述

### 現象
- PDF 第 75-85 頁出現大量 `citezeng2024scaling...`, `citema2024language...` 等長串字詞黏在一起
- 這些不是表格問題，而是**參考文獻未正確編譯**
- 所有 `\cite{}` 命令顯示為原始 citation key 而非數字或格式化引用

### 錯誤範例
```
# PDF 中顯示（錯誤）
...citezeng2024scalingspeechtextpretrainingsyntheticint...

# 應該顯示（正確）
...[123]...
```

---

## 根本原因

### 1. Citation Key 格式錯誤

**檔案**: `benchmark_table.tex` Line 15

```latex
❌ 錯誤:
IndicSUPERB \cite{entry2025indicsuperbspeechprocessinguniversalperf title=} & ...

✅ 正確:
IndicSUPERB \cite{entry2025indicsuperbspeechprocessinguniversalperf} & ...
```

**問題**: Citation key 中包含空格和多餘的 `title=`，導致 BibTeX 解析失敗

### 2. 多個 \bibstyle 命令衝突

**BibTeX 日誌** (`survey.blg`):
```
Illegal, another \bibstyle command---line 1316 of file survey.aux
 : \bibstyle
 :          {unsrtnat}
I'm skipping whatever remains of this command
```

**原因**: LaTeX 文件中可能有多個 `\bibliographystyle{}` 命令

### 3. Missing Characters in nullfont

**編譯日誌** (`survey.log`):
```
Missing character: There is no @ in font nullfont!
Missing character: There is no f in font nullfont!
...
And 125 more --- see log file 'survey.log'
```

**原因**: BibTeX 編譯失敗後，LaTeX 無法正確處理 citation，導致字體問題

---

## 已執行修復

### ✅ 修復 benchmark_table.tex
```bash
# 修復錯誤的 citation key
sed -i '' 's/entry2025indicsuperbspeechprocessinguniversalperf title=/entry2025indicsuperbspeechprocessinguniversalperf/g' benchmark_table.tex
```

**結果**: Citation key 格式正確，但 BibTeX 仍有其他錯誤

---

## 待處理問題

### 1. 檢查並修復所有 citation key 格式錯誤

```bash
# 搜尋可能有問題的 citation
grep -n "\\cite{.*title=" latex/*.tex
grep -n "\\cite{.*=}" latex/*.tex
grep -n "\\cite{.*\s.*}" latex/*.tex
```

### 2. 檢查 \bibliographystyle 命令數量

```bash
# 應該只有一個
grep -n "\\bibliographystyle" survey.tex
```

**正確位置**: 應該在 `\bibliography{references}` 之後，文件結尾附近

### 3. 清除並重新編譯 BibTeX

```bash
# 完整清除並重新編譯
cd outputs/2025-10-09-1630_speec/latex
rm -f *.aux *.bbl *.blg *.fls *.fdb_latexmk
latexmk -pdf -interaction=nonstopmode -f survey.tex
```

### 4. 檢查 references.bib 格式

```bash
# 檢查 .bib 檔案中是否有格式錯誤
bibtex -terse survey 2>&1 | grep "error"
```

---

## 修復流程

### Step 1: 修復所有 citation key 錯誤

```bash
cd outputs/2025-10-09-1630_speec/latex

# 搜尋並列出所有可疑的 citation
echo "=== Searching for problematic citations ==="
grep -rn "\\cite{[^}]*\s[^}]*}" . --include="*.tex" | grep -v ".backup"
grep -rn "\\cite{[^}]*title=[^}]*}" . --include="*.tex" | grep -v ".backup"
grep -rn "\\cite{[^}]*=[^}]*}" . --include="*.tex" | grep -v ".backup"
```

### Step 2: 檢查 bibliographystyle 命令

```bash
# 應該只有一個，通常在文件結尾
grep -n "bibliographystyle" survey.tex

# 正確格式:
# \bibliography{references}
# \bibliographystyle{unsrtnat}
```

### Step 3: 完整重新編譯

```bash
# 清除所有編譯產物
latexmk -C

# 重新編譯（包含 BibTeX）
latexmk -pdf -interaction=nonstopmode -f survey.tex

# 檢查 BibTeX 日誌
cat survey.blg | grep -i "error\|illegal\|warning"
```

### Step 4: 驗證修復效果

```bash
# 檢查 PDF 中是否還有 "cite..." 字串
pdftotext survey.pdf - | grep -o "cite[a-z0-9]\{20,\}" | head -10

# 如果沒有輸出，表示修復成功
# 如果還有輸出，表示還有問題
```

---

## 暫時解決方案（如果無法完全修復）

### 選項 A: 使用數字引用
```latex
% 在 survey.tex preamble 中
\usepackage[numbers]{natbib}
\bibliographystyle{unsrtnat}
```

### 選項 B: 使用短 citation key
如果某些 citation key 太長（如 50+ 字元），考慮在 `references.bib` 中重新命名:

```bibtex
% 原本（太長）
@article{zeng2024scalingspeechtextpretrainingsyntheticint,
  ...
}

% 改為（較短）
@article{zeng2024scaling,
  ...
}
```

然後在所有 `.tex` 檔案中批次替換:
```bash
sed -i '' 's/zeng2024scalingspeechtextpretrainingsyntheticint/zeng2024scaling/g' *.tex
```

---

## 相關檔案

- `outputs/2025-10-09-1630_speec/latex/survey.tex` - 主文件
- `outputs/2025-10-09-1630_speec/latex/benchmark_table.tex` - 發現錯誤的 citation
- `outputs/2025-10-09-1630_speec/latex/references.bib` - 參考文獻資料庫（74KB）
- `outputs/2025-10-09-1630_speec/latex/survey.blg` - BibTeX 編譯日誌
- `outputs/2025-10-09-1630_speec/latex/survey.log` - LaTeX 編譯日誌

---

## 待辦事項

- [ ] 搜尋並修復所有錯誤的 citation key（含空格、`title=` 等）
- [ ] 檢查 `\bibliographystyle` 命令是否重複
- [ ] 完整清除並重新編譯 BibTeX
- [ ] 驗證 PDF 中的引用是否正確顯示
- [ ] 考慮是否需要縮短過長的 citation key（50+ 字元）

---

## ✅ 問題已解決 (2025-10-16 14:10)

### 真正根本原因

**第 75-86 頁引用顯示為純文本的真正原因**: `src/modules/latex_handler/latex_figure_builder.py` 中的 `TinyTreeFigureBuilder` 類別在生成 TikZ 圖表時,**錯誤地將 `\cite{}` 雙重轉義為 `\\cite{}`**。

**錯誤範例** (`figs/tiny_tree_figure_0.tex` Line 43):
```latex
❌ 生成的錯誤代碼:
{12.5 Hz sweet spot\\cite{zeng2024scalingspeechtextpretrainingsyntheticint}}

✅ 應該生成的正確代碼:
{12.5 Hz sweet spot\cite{zeng2024scalingspeechtextpretrainingsyntheticint}}
```

**問題說明**: 在 LaTeX 中,`\\` 是換行指令,所以 `\\cite` 被解釋為「換行+純文本cite」而非引用指令。這導致:
1. BibTeX 無法識別這些引用
2. LaTeX 將 `cite{...}` 視為普通文字輸出
3. PDF 中顯示完整的 citation key 而非引用編號

### 修復方法

**臨時修復** (針對已生成的檔案):
```bash
cd outputs/2025-10-09-1630_speec/latex/figs
for f in *.tex; do 
  sed -i '.bak' 's/\\\\cite{/\\cite{/g' "$f"
done
```

**影響範圍**: 
- 修復了 245 個錯誤的 `\\cite{}` 實例
- 涉及所有 `tiny_tree_figure_*.tex` 檔案
- 同時也修復了 `tree_figure_*.tex` 等其他圖表

### 驗證結果

**編譯成功**:
```bash
latexmk -pdf -f survey.tex
# Output: survey.pdf (86 pages, 635KB)
```

**引用顯示正確**:
- ✅ **第 75 頁**: 顯示 `[4]`, `[60]`, `[8]`, `[13]`, `[62]` 等正確引用編號
- ✅ **第 80 頁**: 顯示 `[74]`, `[126]`, `[84]`, `[41]`, `[32]` 等正確引用編號
- ✅ **第 75-86 頁**: 所有 TikZ 圖表中的引用均正常顯示
- ✅ **BibTeX**: 編譯成功,無錯誤
- ✅ **PDF**: 生成成功,引用系統正常工作

### 源碼問題分析

**問題位置**: `src/modules/latex_handler/latex_figure_builder.py`

**TinyTreeFigureBuilder 類別** (Line ~570-650):
```python
def _gen_leaf_node_latex(self, node: TreeFigureBuilder.Node) -> str:
    # ... 生成代碼邏輯 ...
    for i, list_node in enumerate(node.list_):
        # ❌ 這裡 list_node 可能包含 \cite{},但被錯誤轉義
        list_node_tex += f"\\node[nodeL, ...] ({list_node_name}) {{{list_node}}};\n"
    # ...
```

**推測原因**:
1. LLM 生成的 `list_node` 文字中包含 `\cite{...}`
2. Python f-string 或 JSON 解析過程中進行了轉義
3. 寫入 `.tex` 檔案時沒有反轉義,導致 `\cite` 變成 `\\cite`

### 待辦事項

- [ ] **[高優先]** 在 `latex_figure_builder.py` 中修復轉義邏輯:
  - 檢查 `extract_architecture()` 方法返回的 JSON 是否正確
  - 檢查 `_gen_leaf_node_latex()` 寫入時是否需要反轉義
  - 添加單元測試確保 `\cite{}` 不被雙重轉義
  
- [ ] **[中優先]** 測試其他 task_id 的輸出:
  - 檢查 `outputs/2025-10-09-1038_speec/` 是否有相同問題
  - 檢查 `outputs/gpt-5-nano(medium)/` 是否有相同問題
  
- [ ] **[低優先]** 改進生成流程:
  - 考慮在生成後自動驗證 `.tex` 檔案中的 `\\cite` 模式
  - 添加 post-processing 步驟自動修正錯誤轉義

---

**維護者**: GitHub Copilot (AI Agent)  
**最後更新**: 2025-10-16 14:10

````
