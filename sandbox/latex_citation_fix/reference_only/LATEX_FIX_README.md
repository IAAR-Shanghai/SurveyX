# LaTeX `\caption@xref` 引用問題修復文件索引

**完整修復流程記錄** - 2025-10-17

---

## 📚 文件結構

### 1. **完整技術文件**（詳細版）
**檔案**：[`LATEX_CAPTION_XREF_FIX.md`](./LATEX_CAPTION_XREF_FIX.md)

**用途**：
- 完整的問題分析與根因診斷
- 所有嘗試方案的詳細記錄（包含失敗案例）
- 技術深入分析（LaTeX 機制、TikZ 座標系統）
- 方案 A、B、C 的完整實施步驟與對比

**適用對象**：
- 需要理解技術細節的維護者
- 遇到類似問題需要深入排查的開發者
- 需要評估不同解決方案的決策者

**長度**：約 600 行，包含大量程式碼範例和診斷步驟

---

### 2. **操作檢查清單**（實操版）
**檔案**：[`LATEX_FIX_CHECKLIST.md`](./LATEX_FIX_CHECKLIST.md)

**用途**：
- 逐步操作檢查清單
- 診斷與修復流程
- 驗證測試用例
- 自動化腳本範例
- 故障排除指南

**適用對象**：
- 執行修復的 AI Agent
- 需要逐步指引的操作者
- 在 Sandbox 環境中測試流程的開發者

**長度**：約 350 行，結構化檢查清單

---

### 3. **快速參考卡**（速查版）
**檔案**：[`LATEX_FIX_QUICKREF.md`](./LATEX_FIX_QUICKREF.md)

**用途**：
- 一頁式快速診斷
- 5 分鐘修復流程
- 常見問題速查
- 關鍵命令集合

**適用對象**：
- 熟悉流程需要快速回顧的操作者
- 緊急修復場景
- 需要快速驗證的測試者

**長度**：約 220 行，精簡指令

---

## 🎯 如何使用本文件集

### 場景 1：第一次遇到此問題

**推薦閱讀順序**：
1. 先讀 **快速參考卡** 了解問題概要（5 分鐘）
2. 閱讀 **完整技術文件** 理解根因（30 分鐘）
3. 參照 **操作檢查清單** 執行修復（15 分鐘）

### 場景 2：需要快速修復

**推薦閱讀順序**：
1. 直接使用 **快速參考卡**（5 分鐘完成修復）
2. 如遇問題，查閱 **操作檢查清單** 的故障排除章節

### 場景 3：在 Sandbox 測試 Agent

**推薦閱讀順序**：
1. 讓 Agent 讀取 **操作檢查清單**
2. 逐項執行檢查清單中的步驟
3. 參照 **快速參考卡** 驗證結果
4. 如需深入理解，查閱 **完整技術文件**

### 場景 4：評估長期解決方案

**推薦閱讀順序**：
1. 閱讀 **完整技術文件** 的「方案對比表」章節
2. 查看方案 C（拆分圖表）的實施步驟
3. 參考技術深入分析評估風險

---

## 📋 問題概要

### 症狀
LaTeX 編譯後的 PDF 中，3 處引用顯示為 "??"：
- ✅ 第 2 頁：Overview 圖表 subsection 13.4（已修復：字元匹配問題）
- ✅ 第 25 頁：Figure 5 引用（已修復：硬編碼為 "Figure 5"）
- ✅ 第 32 頁：Figure 8 引用（已修復：硬編碼為 "Figure 8"）

### 根本原因
LaTeX caption 機制無法處理超大型內聯 TikZ 內容（>400 行），導致 `.aux` 檔案中寫入 `\caption@xref` 佔位符而非實際編號。

### 最終採用方案
**方案 A：硬編碼圖表編號**
- 修改 `survey.tex` 中的 2 處引用
- 從 `Figure~\ref{fig:...}` 改為 `Figure~5` 和 `Figure~8`
- 優點：快速、可靠、圖表完整
- 缺點：失去自動編號和超連結

---

## 🔧 修復步驟摘要

### 1. 備份
```bash
cd outputs/*/latex/figs
cp tree_figure_Langu.tex tree_figure_Langu.tex.BACKUP
cp tiny_tree_figure_5.tex tiny_tree_figure_5.tex.BACKUP
```

### 2. 替換引用
```bash
cd ..
sed -i '' 's/Figure~\\ref{fig:tree_figure_Langu}/Figure~5/g' survey.tex
sed -i '' 's/Figure~\\ref{fig:tiny_tree_figure_5}/Figure~8/g' survey.tex
```

### 3. 重新編譯
```bash
rm -f survey.aux survey.log survey.pdf
pdflatex -interaction=nonstopmode survey.tex
```

### 4. 驗證
打開 `survey.pdf` 檢查：
- 第 25 頁 Figure 5 完整顯示
- 第 32 頁 Figure 8 完整顯示
- 引用處顯示正確數字

---

## 📊 涉及檔案清單

### 主要檔案
- `outputs/2025-10-09-1630_speec/latex/survey.tex`（第 596、721 行）
- `outputs/2025-10-09-1630_speec/latex/figs/tree_figure_Langu.tex`（480 行，26KB）
- `outputs/2025-10-09-1630_speec/latex/figs/tiny_tree_figure_5.tex`（109 行，5.9KB）
- `outputs/2025-10-09-1630_speec/latex/figs/structure_fig.tex`（第 128 行）

### 備份檔案
- `figs/tree_figure_Langu.tex.BEFORE_EXTERNALIZE`
- `figs/tiny_tree_figure_5.tex.BEFORE_EXTERNALIZE`

### 失敗嘗試檔案（可刪除）
- `figs/*_standalone.tex`
- `figs/*_standalone.pdf`
- `figs/*_standalone.aux`
- `figs/*_standalone.log`

---

## ⚠️ 重要警告

### ❌ 不要嘗試 Externalization（方案 B）

**原因**：已證實失敗
- Standalone 類別無法處理 TikZ 絕對座標（81-153）
- 生成的 PDF 高度為 0（343.711 x 0 pts）
- 結果：圖表在主文件中完全不可見

**識別方法**：
```bash
pdfinfo figs/*_standalone.pdf | grep "Page size"
# 如果輸出包含 "x 0 pts"，表示 PDF 已損壞
```

---

## 🚀 自動化腳本

**檔案位置**：`LATEX_FIX_CHECKLIST.md` 中的「完整自動化腳本」章節

**使用方法**：
```bash
# 複製腳本內容到 fix_latex_refs.sh
chmod +x fix_latex_refs.sh
./fix_latex_refs.sh
```

**功能**：
- 自動診斷問題
- 建立備份
- 執行替換
- 重新編譯
- 驗證結果

---

## 📞 需要協助？

### 查看詳細文件
```bash
# 完整技術分析
cat docs/LATEX_CAPTION_XREF_FIX.md | less

# 操作檢查清單
cat docs/LATEX_FIX_CHECKLIST.md | less

# 快速參考卡
cat docs/LATEX_FIX_QUICKREF.md | less
```

### 常見問題排查
參見 **快速參考卡** 的「故障排除」章節或 **操作檢查清單** 的「常見問題排查」章節。

---

## 🔄 更新記錄

| 日期 | 版本 | 變更內容 |
|------|------|---------|
| 2025-10-17 | 1.0 | 初始版本，完整記錄方案 A 實施過程 |

---

## 📝 相關文件

- `docs/agent-protected-files.md`：受保護檔案清單
- `docs/temporary_issues/spacing_glitch.md`：PDF spacing 問題
- `AGENTS.md`：Agent 操作準則
- `pipeline&modules.md`：Pipeline 流程文件

---

**維護者**：AI Agent (GitHub Copilot)  
**專案**：SurveyX  
**狀態**：✅ 已完成並驗證
