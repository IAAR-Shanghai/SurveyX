# LaTeX Figure 顯示問題診斷報告

> **發現時間**: 2025-10-16  
> **問題描述**: survey.pdf 中 figure 引用顯示為 `??`，且所有 figures 都移到 references 之後

---

## 🔴 問題現象

### 1. Figure 引用顯示為 `??`

- 在 PDF 中，原本應該顯示為 "Figure 3" 的地方顯示為 `??`
- 點擊後仍然會跳轉到正確的 figure (超連結有效)
- 表示 `\ref{}` 指令有問題，但 `\label{}` 存在

### 2. 所有 Figures 都出現在 References 之後

- 預期: Figures 應該接近引用它們的文字位置
- 實際: 所有 14 個 figures 都堆積在文件最後面 (references 之後)
- gpt-5-nano 生成的版本沒有這個問題

---

## 🔍 根本原因分析

### 原因 1: 使用了 `figure*` 環境

檢查 `figs/structure_fig.tex`:

```tex
\begin{figure*}[!th]
    \centering
    \resizebox{1\textwidth}{!}
    {
        \begin{forest}
            ...
        \end{forest}
    }
    \caption{chapter structure}
    \label{fig:chapter_structure}
\end{figure*}
```

**問題**: 
- `figure*` 在單欄文檔中可能造成放置問題
- `[!th]` placement 參數表示 "here or top"，但沒有 `p` (page of floats)
- LaTeX 無法在當前頁放置時，會一直延後直到文檔結束

### 原因 2: 文件結構問題

當前 `survey.tex` 結構:

```
...主要內容...
行 1633: \bibliographystyle{unsrtnat}
行 1634: \bibliography{references}
行 1635: \vfill\newpage
行 1636: Disclaimer
行 1641: \end{document}
```

**問題**:
- Bibliography 之後只有 disclaimer，沒有實質內容頁面
- LaTeX 的 float 演算法會將無法放置的 figures 推遲
- 一旦累積多個 floats，會在 `\end{document}` 前強制輸出
- 因為 bibliography 後只剩 1 頁，所有 figures 被推到最後

### 原因 3: 缺少 Figure 引用 (空的 `\ref{}`)

從 log 檔案:

```
LaTeX Warning: Reference `' on page 14 undefined on input line 369.
LaTeX Warning: Reference `fig:tree_figure_Langu' on page 23 undefined
LaTeX Warning: Reference `' on page 29 undefined on input line 715.
```

**問題**:
- 內文中有空的 `\ref{}` 或錯誤的引用
- 導致 PDF 中顯示 `??`
- 可能是模板生成時遺漏了 figure label

---

## 📊 對比分析

### gpt-5-nano(high) vs 2025-10-09-1630_speec

| 項目 | gpt-5-nano(high) | 2025-10-09-1630_speec |
|------|------------------|----------------------|
| Figure 數量 | 2 個 | 14 個 |
| Figure 環境 | `figure` | `figure*` |
| Float 位置 | 正常分布 | 全部在末尾 |
| 文件長度 | 較短 | 較長 (1641 行) |
| References 位置 | 中後段 | 行 1633 |
| 引用問題 | 無 | 多個 `??` |

**結論**: 
- 問題不是修復腳本造成的 (gpt-5-nano 版本使用相同腳本無此問題)
- 問題來自於 **過多的 figures** + **figure* 環境** + **文檔長度**

---

## ✅ 解決方案

### 方案 A: 修改 Figure 環境 (推薦)

將所有 `figure*` 改為 `figure`，並調整 placement 參數:

```bash
cd outputs/2025-10-09-1630_speec/latex/figs

# 備份
for f in *.tex; do cp "$f" "$f.bak_$(date +%Y%m%d)"; done

# 批次修改
sed -i '' 's/\\begin{figure\*}\[!th\]/\\begin{figure}[htbp]/g' *.tex
sed -i '' 's/\\end{figure\*}/\\end{figure}/g' *.tex
```

**說明**:
- `[htbp]` = here, top, bottom, page (更靈活的放置選項)
- 單欄 `figure` 環境更容易放置
- 允許 LaTeX 在專門的 float 頁面放置

### 方案 B: 在文中強制放置 Figures

在每個 `\input{figs/...}` 之後加入 `\clearpage` 或 `\FloatBarrier`:

```latex
\input{figs/structure_fig}
\clearpage  % 強制輸出所有 pending floats

% 或使用 placeins package
\usepackage{placeins}
\input{figs/structure_fig}
\FloatBarrier  % 防止 floats 跨越此點
```

**優點**: 確保 figures 不會漂移太遠  
**缺點**: 可能產生較多空白頁

### 方案 C: 移除 Float 環境 (最激進)

將 figures 改為直接內嵌 (非 float):

```latex
% 不使用 \begin{figure}
\begin{center}
    \resizebox{0.9\textwidth}{!}{
        \begin{forest}
            ...
        \end{forest}
    }
    \captionof{figure}{chapter structure}
    \label{fig:chapter_structure}
\end{center}
```

**需要**: `\usepackage{caption}` (提供 `\captionof` 指令)

**優點**: Figures 固定在插入位置  
**缺點**: 可能造成分頁問題

### 方案 D: 調整文檔結構

在 bibliography 前插入 `\clearpage`:

```latex
...主要內容...

\clearpage  % 強制輸出所有 pending floats
\bibliographystyle{unsrtnat}
\bibliography{references}
```

**優點**: 最小修改  
**缺點**: Figures 仍可能集中在某幾頁

---

## 🛠️ 修復 `\ref{}` 空引用

### 步驟 1: 找出所有空引用

```bash
cd outputs/2025-10-09-1630_speec/latex

# 檢查 LaTeX warning
grep "Reference.*undefined" survey.log

# 找出問題行
grep -n "\\ref{fig:" survey.tex | grep "\\ref{fig:}$"
```

### 步驟 2: 找出對應的 label

```bash
# 列出所有 figure labels
grep "\\label{fig:" figs/*.tex
```

### 步驟 3: 手動補上正確的引用

根據上下文，將空的 `\ref{}` 或錯誤的引用改為正確的 `\ref{fig:xxx}`

---

## 🚀 一鍵修復腳本

創建 `scripts/fix_figure_placement.py`:

```python
#!/usr/bin/env python3
"""
修復 LaTeX Figure 放置問題

1. 將 figure* 改為 figure
2. 調整 placement 參數
3. 在 bibliography 前加入 \clearpage
"""

import re
from pathlib import Path

def fix_figures(latex_dir):
    figs_dir = Path(latex_dir) / "figs"
    
    # 修復所有 figure 檔案
    for tex_file in figs_dir.glob("*.tex"):
        content = tex_file.read_text()
        
        # figure* -> figure, [!th] -> [htbp]
        content = re.sub(
            r'\\begin{figure\*}\[!th\]',
            r'\\begin{figure}[htbp]',
            content
        )
        content = re.sub(
            r'\\end{figure\*}',
            r'\\end{figure}',
            content
        )
        
        tex_file.write_text(content)
        print(f"✅ Fixed {tex_file.name}")
    
    # 在 bibliography 前加入 \clearpage
    survey_file = Path(latex_dir) / "survey.tex"
    content = survey_file.read_text()
    
    if "\\clearpage\n\\bibliographystyle" not in content:
        content = re.sub(
            r'\\bibliographystyle',
            r'\\clearpage\n\\bibliographystyle',
            content
        )
        survey_file.write_text(content)
        print("✅ Added \\clearpage before bibliography")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fix_figure_placement.py <latex_dir>")
        sys.exit(1)
    
    fix_figures(sys.argv[1])
    print("\n🎉 Figure placement fixed!")
    print("   Re-compile: pdflatex survey.tex (x2)")
```

---

## 📋 執行步驟

### 1. 備份

```bash
cd outputs/2025-10-09-1630_speec/latex
cp survey.tex survey.tex.before_figure_fix
cp -r figs figs.before_figure_fix
```

### 2. 執行修復

```bash
# 使用方案 A + D
python ../../scripts/fix_figure_placement.py .
```

### 3. 重新編譯

```bash
pdflatex survey.tex
bibtex survey
pdflatex survey.tex
pdflatex survey.tex
```

### 4. 驗證結果

- [ ] Figures 不再全部在文檔末尾
- [ ] `??` 引用已修復
- [ ] PDF 總頁數合理 (應該增加,因為 figures 分散了)

---

## 📝 技術細節

### LaTeX Float 放置演算法

1. LaTeX 嘗試按 placement 參數放置 float:
   - `h` = here (當前位置)
   - `t` = top of page
   - `b` = bottom of page  
   - `p` = page of floats only
   - `!` = override internal parameters

2. 如果無法放置:
   - Float 被加入 pending queue
   - 在下一頁重新嘗試
   - 如果累積太多，LaTeX 可能強制輸出所有 pending floats

3. `\clearpage` 的作用:
   - 強制開始新頁
   - 輸出所有 pending floats
   - 確保 floats 不會跨越此點

### `figure` vs `figure*`

- `figure`: 單欄 float (article 預設)
- `figure*`: 雙欄 float (用於 twocolumn 文檔)
- 在單欄文檔中，`figure*` 可能造成放置困難

---

## 🔗 相關資源

- [LaTeX Float Placement](https://www.overleaf.com/learn/latex/Positioning_of_Figures)
- [LaTeX figure* in single column](https://tex.stackexchange.com/questions/39017/)
- [Preventing floats from moving](https://www.overleaf.com/learn/latex/Errors/LaTeX_Error:_Too_many_unprocessed_floats)

---

**診斷完成時間**: 2025-10-16  
**狀態**: ⚠️ 問題已識別，待用戶確認修復方案
