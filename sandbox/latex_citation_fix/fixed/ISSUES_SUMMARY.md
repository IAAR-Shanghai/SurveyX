# LaTeX 引用問題總結報告

生成時間：2025-10-16

## 已發現的問題

### 1. ❌ 第25頁：Figure ?? 問題
- **位置**：survey.tex line 596
- **引用**：`\autoref{fig:tree_figure_Langu}`
- **狀態**：仍然顯示為 ??
- **aux 文件狀態**：`\caption@xref` (未正確解析)
- **已嘗試修復**：
  - ✅ 將 `\input{figs/tree_figure_Langu}` 移到引用之前
  - ✅ 修復 caption/label 之間的空格
  - ✅ 簡化 caption 文字
  - ✅ 將 `\begin{figure}[h]` 改為 `\begin{figure}[htbp]`
  - ❌ 問題持續存在

### 2. ❌ 第32頁：引用損壞 "train tiny ( 1"
- **位置**：survey.tex line 721
- **引用**：`\autoref{fig:tiny_tree_figure_5}`
- **狀態**：顯示錯誤文字 "train tiny ( 1"，後續內容消失
- **aux 文件狀態**：`\caption@xref` (未正確解析)
- **已嘗試修復**：
  - ✅ 將 `\input{figs/tiny_tree_figure_5}` 移到引用之前
  - ✅ 修復 caption/label 之間的空格
  - ✅ 簡化 caption 文字  
  - ✅ 將 `\begin{figure}[h]` 改為 `\begin{figure}[htbp]`
  - ❌ 問題持續存在

### 3. ❌ 截圖中的章節編號問題
- **顯示**：13.1, 13.2, 13.3, ??, 13.5
- **缺失**：13.4 的編號
- **可能原因**：
  - 選項A：Subsection "Bandwidth and edge--server trade-offs" (line 1262) 編號錯誤
  - 選項B：在 line 1253-1262 之間缺少一個 subsection
  - 選項C：LaTeX 交叉引用未正確解析某個 subsection

## 根本原因分析

### `\caption@xref` 問題
兩個問題圖檔的 aux 條目格式：
```latex
\newlabel{fig:tree_figure_Langu}{{\caption@xref {fig:tree_figure_Langu}{ on input line 478}}{25}...}
\newlabel{fig:tiny_tree_figure_5}{{\caption@xref {fig:tiny_tree_figure_5}{ on input line 109}}{32}...}
```

正常圖檔的 aux 條目格式（如 fig:tiny_tree_figure_0）：
```latex
\newlabel{fig:tiny_tree_figure_0}{{2}{16}{Figure: Hierarchical overview...}{figure.caption.3}{}}
```

**關鍵差異**：正常的是 `{{2}{16}...}`（數字編號），問題的是 `{{\caption@xref...}}`

### 可能的深層原因
1. **Caption 解析失敗**：即使簡化後，LaTeX 仍無法為這兩個 figure 生成編號
2. **Figure 浮動問題**：即使改為 `[htbp]`，這兩個圖可能仍被延遲處理
3. **TikZ/Adjustbox 衝突**：這兩個圖的 TikZ 內容可能導致 caption 計數器異常
4. **Subcaption 包衝突**：survey.tex 使用了 `subcaption` 包，可能與這兩個圖的結構衝突

## 建議的下一步修復方案

### 方案 A：完全重建圖檔環境
```latex
% 移除 adjustbox，直接使用 figure + resizebox
\begin{figure}[htbp]
\centering
\resizebox{\textwidth}{!}{
  \begin{tikzpicture}
    ...
  \end{tikzpicture}
}
\caption{Hierarchical taxonomy of language modeling over speech tokens}
\label{fig:tree_figure_Langu}
\end{figure}
```

### 方案 B：使用 \ref 代替 \autoref
```latex
% 在 survey.tex 中
Figure~\ref{fig:tree_figure_Langu}
```

### 方案 C：強制編號
在圖檔中加入：
```latex
\addtocounter{figure}{-1}
\refstepcounter{figure}
\caption{...}
\label{...}
```

### 方案 D：檢查是否有 label 重複
```bash
grep -r "\\label{fig:tree_figure_Langu}" figs/
grep -r "\\label{fig:tiny_tree_figure_5}" figs/
```

## 待驗證的問題

1. 是否還有其他 subsection 編號跳號？
2. 第32頁的 "train tiny ( 1" 文字來自哪裡？
3. 這兩個圖的 TikZ 代碼是否有語法錯誤？

## 下一步行動

1. **立即**：檢查 survey.log 中是否有這兩個圖相關的錯誤或警告
2. **優先**：嘗試方案 A - 重建圖檔環境
3. **備選**：使用 `\ref` 代替 `\autoref`
4. **長期**：考慮重新生成這兩個 TikZ 圖檔
