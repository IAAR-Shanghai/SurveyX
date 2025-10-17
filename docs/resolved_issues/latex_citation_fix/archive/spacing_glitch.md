# Spacing Glitch in Generated Survey PDF

## 摘要
目前在 `outputs/2025-10-09-1630_speec/survey.pdf` 中觀察到大量文字黏在一起的 spacing glitch，尤其在介紹「Mixed and scheduling-aware interfaces」的段落中特別明顯。該問題會影響整份文件的可讀性，且呈現出非預期的排版。

## 觀察與影響
- 受影響的段落會出現字詞之間沒有空格，例如 `acommonpointuses1semantic`。
- 同樣的情況遍布整份文件，推測是在 LaTeX 組版時因為無法處理特定符號而觸發的 fallback 行為。
- 這種黏字現象會降低人工審閱效率，也可能影響使用者對內容專業度的印象。

## 根因分析
- 在 `outputs/2025-10-09-1630_speec/latex/survey.tex:295` 等行可看到直接使用了 Unicode 字元（例如 `∈`, `≈`）。
- 使用的 pdfLaTeX 流程只載入 `inputenc` 與 `fontenc`，未額外宣告這些 Unicode 符號。TeX 在遇到陌生字元時會丟出 `! LaTeX Error: Unicode character ∈ (U+2208) not set up for use with LaTeX.` 等錯誤。
- LaTeX 會嘗試恢復排版並忽略相關空格，導致後續字詞被黏在一起而形成 spacing glitch。

## 建議處理流程
1. **輸出前清理文本**：在產生 LaTeX 檔之前，用腳本將常見 Unicode 符號對應到 TeX 巨集（例如 `∈ → $\in$`, `≈ → $\approx$`, `≥ → $\ge$`）。
2. **編譯選項調整**：改用 XeLaTeX 或 LuaLaTeX，並確保字型支援目標符號，或在 preamble 加入 `\usepackage{newunicodechar}` 並定義 `\newunicodechar{∈}{\in}`。
3. **建立驗證步驟**：在工作流程中加入檢查腳本（解析 `compile.log` 或 `pdftotext` 結果）以偵測 `Unicode character ... not set up`、`Missing character` 等訊息。

## 待辦事項
- 決定要採用的修復策略（文字替換 vs. 改用 Unicode-aware 編譯流程）。
- 於自動化流程中加入對 `compile.log` 的解析，若偵測到未處理的 Unicode 字元則觸發警示或中止。
- 覆蓋現有產線，驗證修復後是否能消除 PDF 中的 spacing glitch。

## 相關參考
- LaTeX `compile.log` 中的錯誤片段：`outputs/2025-10-09-1630_speec/latex/compile.log:2910`
- 原始 LaTeX 段落：`outputs/2025-10-09-1630_speec/latex/survey.tex:295`
- 受影響的 PDF 頁面：`outputs/2025-10-09-1630_speec/survey.pdf` 第 11 頁
