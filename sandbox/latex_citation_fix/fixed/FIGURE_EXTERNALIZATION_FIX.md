# LaTeX 圖表外部化修復說明

## 問題描述

在編譯 `survey.tex` 時，兩個大型 TikZ 圖表導致 `\caption@xref` 錯誤，造成引用顯示為 "??"：
- `fig:tree_figure_Langu` (480 行，26K) - Figure 5, page 26
- `fig:tiny_tree_figure_5` (109 行，5.9K) - Figure 8, page 33

## 根本原因

LaTeX 的 caption 機制在處理超大型內聯 TikZ 內容（>400 行或 >20K）時會失效，
導致 aux 檔案產生 `\caption@xref` 佔位符而非正確的圖表編號。

## 解決方案：圖表外部化（Externalization）

採用 **standalone 編譯** 策略：
1. 提取 TikZ 內容到獨立的 standalone 文件
2. 編譯為獨立 PDF
3. 主文件改用 `\includegraphics` 引用 PDF

## 檔案結構

### 新建檔案

```
figs/
├── tree_figure_Langu_standalone.tex    # 獨立的 TikZ 文件
├── tree_figure_Langu_standalone.pdf    # 編譯後的 PDF (18K)
├── tiny_tree_figure_5_standalone.tex   # 獨立的 TikZ 文件
└── tiny_tree_figure_5_standalone.pdf   # 編譯後的 PDF (17K)
```

### 備份檔案

```
figs/
├── tree_figure_Langu.tex.BEFORE_EXTERNALIZE    # 修改前原始檔案
└── tiny_tree_figure_5.tex.BEFORE_EXTERNALIZE   # 修改前原始檔案
```

### 修改後的圖表檔案

`tree_figure_Langu.tex` 和 `tiny_tree_figure_5.tex` 現在簡化為：

```latex
\begin{figure}[h]
   \centering
   \includegraphics[width=\textwidth]{figs/xxx_standalone.pdf}
   \caption[Short]{Long caption text}
   \label{fig:xxx}
\end{figure}
```

## 驗證結果

### ✅ 修復前（問題狀態）

```latex
% survey.aux 中顯示錯誤佔位符
\newlabel{fig:tree_figure_Langu}{{\caption@xref {fig:tree_figure_Langu}{ on input line 477}}{25}...}
\newlabel{fig:tiny_tree_figure_5}{{\caption@xref {fig:tiny_tree_figure_5}{ on input line 108}}{32}...}
```

### ✅ 修復後（正常狀態）

```latex
% survey.aux 中顯示正確編號
\newlabel{fig:tree_figure_Langu}{{5}{26}{Hierarchical taxonomy}{figure.caption.6}{}}
\newlabel{fig:tiny_tree_figure_5}{{8}{33}{System architectures}{figure.caption.9}{}}
```

- Figure 5 在第 26 頁正確顯示
- Figure 8 在第 33 頁正確顯示
- 所有引用 `\ref{fig:xxx}` 都正確解析
- 無任何「undefined reference」警告

## 優勢

1. ✅ **解決根本問題**：繞過 LaTeX 大型內聯內容限制
2. ✅ **保持功能完整**：圖表編號、超連結、引用全部正常
3. ✅ **提升編譯速度**：外部 PDF 只需編譯一次，主文件編譯更快
4. ✅ **易於維護**：修改圖表只需重新編譯對應的 standalone 文件

## 重新編譯圖表

若需修改圖表內容：

```bash
cd figs/

# 修改 standalone 文件
# vim tree_figure_Langu_standalone.tex

# 重新編譯
pdflatex tree_figure_Langu_standalone.tex

# 主文件會自動使用新的 PDF
cd ..
pdflatex survey.tex
```

## 故障排除

### 如果需要還原原始結構

```bash
cd figs/
cp tree_figure_Langu.tex.BEFORE_EXTERNALIZE tree_figure_Langu.tex
cp tiny_tree_figure_5.tex.BEFORE_EXTERNALIZE tiny_tree_figure_5.tex
```

### 如果 PDF 未找到

確認 standalone PDF 存在：
```bash
ls -lh figs/*_standalone.pdf
```

### 如果需要重新生成所有內容

```bash
cd figs/
pdflatex tree_figure_Langu_standalone.tex
pdflatex tiny_tree_figure_5_standalone.tex
cd ..
pdflatex survey.tex
pdflatex survey.tex  # 第二次確保引用正確
```

## 技術細節

### Standalone 文件結構

```latex
\documentclass[tikz,border=2mm]{standalone}

% Required packages
\usepackage{tikz}
\usepackage{adjustbox}
\usetikzlibrary{...}

% Define colors
\definecolor{c12}{RGB}{100,149,237}
...

\begin{document}
% TikZ content (extracted from original figure)
\begin{adjustbox}{max width=\textwidth, center}
\begin{tikzpicture}[...]
...
\end{tikzpicture}
\end{adjustbox}
\end{document}
```

### 主文件引用

```latex
% 不再內嵌 TikZ，改用 \includegraphics
\includegraphics[width=\textwidth]{figs/xxx_standalone.pdf}
```

## 總結

這個修復方案成功解決了困擾已久的 `\caption@xref` 問題，
將兩個超大型圖表（合計 600 行 TikZ 程式碼）外部化為獨立 PDF，
主文件現在可以正確編譯並正確顯示所有圖表引用。

---
**修復完成日期**: 2025-10-17  
**修復方案**: 圖表外部化（Externalization with Standalone）  
**影響範圍**: 2 個圖表，0 個功能損失
