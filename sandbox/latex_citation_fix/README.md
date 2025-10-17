# LaTeX Citation Fix - Agent 測試環境完整指南

**版本**：1.0  
**日期**：2025-10-17  
**目的**：為 AI Agent 提供 LaTeX 引用問題的完整測試環境與學習資源

---

## 🎯 快速導航

- **新手入門** → 閱讀本檔案 + [TEST_INSTRUCTIONS.md](./TEST_INSTRUCTIONS.md)
- **開始測試** → 執行 `./tools/reset.sh` 然後進入 `agent_workspace/`
- **學習參考** → 查看 [reference_only/](./reference_only/) 中的完整文件（測試時禁止！）
- **驗證結果** → 使用 `./tools/latex_fix_toolkit.py` 或 `./tools/verify.py`

---

## 📚 核心文件導讀（reference_only/）

> ⚠️ **Agent 測試規則**: 測試時**不可查看** `reference_only/` 中的文件！  
> 這些文件記錄了完整修復過程，僅供測試後學習或人類維護者參考。

| 文件 | 大小 | 用途 | 適用場景 |
|------|------|------|----------|
| **[LATEX_CAPTION_XREF_FIX.md](./reference_only/LATEX_CAPTION_XREF_FIX.md)** | 15 KB | 📋 完整技術文件<br>• 問題根因分析<br>• 修復方案對比<br>• 詳細 diff 記錄 | 需要深入了解問題本質 |
| **[LATEX_FIX_CHECKLIST.md](./reference_only/LATEX_FIX_CHECKLIST.md)** | 8.3 KB | ✅ 操作檢查清單<br>• 分階段修復步驟<br>• 具體命令與輸出 | 執行修復的逐步指南 |
| **[LATEX_FIX_QUICKREF.md](./reference_only/LATEX_FIX_QUICKREF.md)** | 4.6 KB | 🚀 快速參考卡<br>• 常用命令速查<br>• 關鍵檔案索引 | 經驗豐富者速查 |
| **[LATEX_FIX_SUMMARY.md](./reference_only/LATEX_FIX_SUMMARY.md)** | 13 KB | 📊 執行總結<br>• 修復前後對比<br>• 經驗教訓 | 了解修復成果 |
| **[LATEX_FIX_README.md](./reference_only/LATEX_FIX_README.md)** | 6.0 KB | 📚 文件索引<br>• 推薦閱讀順序 | 第一次接觸的入口 |

---

## 📂 目錄結構

```
sandbox/latex_citation_fix/
├── README.md                ← 📖 你在這裡！完整導航指南
├── TEST_INSTRUCTIONS.md     ← 🎯 Agent 測試任務說明
├── SANDBOX_CHECKLIST.md     ← ✅ 完整性檢查清單
├── SANDBOX_COMPLETION_REPORT.md  ← 📊 環境建置報告
├── COMPILATION_VERIFICATION.md   ← 🔍 編譯驗證報告
│
├── broken/                  ← ⚠️ 問題版本（85 頁）
│   ├── survey.tex          ← 包含 2 處 \ref{} 引用問題
│   ├── figs/               ← 18 個圖表（含 en-dash 問題）
│   └── compile.sh          ← 一鍵編譯
│
├── fixed/                   ← ✅ 修復版本（80 頁）
│   ├── survey.tex          ← 硬編碼 Figure~5 和 Figure~8
│   ├── figs/               ← 18 個圖表（已修復）
│   └── compile.sh          ← 一鍵編譯
│
├── reference_only/          ← 📚 完整修復文件（測試時禁止查看！）
│   ├── LATEX_CAPTION_XREF_FIX.md
│   ├── LATEX_FIX_CHECKLIST.md
│   ├── LATEX_FIX_QUICKREF.md
│   ├── LATEX_FIX_SUMMARY.md
│   ├── LATEX_FIX_README.md
│   └── LATEX_FIX_INDEX.md
│
├── agent_workspace/         ← 🛠️ Agent 工作區（測試用）
│   └── (執行 reset.sh 後複製 broken/ 內容)
│
├── backup/                  ← 💾 原始備份
│   └── figs_original/
│
└── tools/                   ← 🔧 修復與驗證工具
    ├── latex_fix_toolkit.py     ← ⭐ 統一修復工具（推薦）
    ├── fix_latex_issues.py      ← 一般 LaTeX 問題修復
    ├── fix_figure_placement.py  ← Figure 放置修復
    ├── fix_figure_refs.py       ← Figure 引用修復
    ├── fix_caption_label.py     ← Caption/Label 格式修復
    ├── reset.sh                 ← 重置 agent_workspace
    ├── verify.py                ← 驗證修復結果
    └── compare.sh               ← 對比差異
```

---

## 🔍 問題概覽

### 已植入的 3 個問題（broken/）

| # | 位置 | 問題類型 | 檔案 | 症狀 |
|---|------|----------|------|------|
| 1 | 第 2 頁 | 字元不匹配 | `figs/structure_fig.tex` L131 | subsection 13.4 顯示 "??" |
| 2 | 第 25 頁 | 超大 TikZ | `survey.tex` L578 | Figure 5 顯示 "??" |
| 3 | 第 32 頁 | 超大 TikZ | `survey.tex` L701 | Figure 8 顯示 "??" |

#### 問題 1 - 字元不匹配
```latex
# figs/structure_fig.tex Line ~131
# 問題: en-dash (–) vs double-hyphen (--)
edge–server    ← 錯誤（U+2013）
edge--server   ← 正確（ASCII）
```

#### 問題 2 & 3 - 超大 TikZ 圖表
```latex
# survey.tex
Line 578:  Figure~\ref{fig:tree_figure_Langu}        ← 會顯示 "??"
Line 701:  Figure~\ref{fig:tiny_tree_figure_5}       ← 會顯示 "??"

# 根因: TikZ 檔案過大導致 caption 計數器失效
tree_figure_Langu.tex:     480 行, 26 KB
tiny_tree_figure_5.tex:    109 行, 5.9 KB
```

---

## 🎓 Agent 測試快速開始

### 1️⃣ 閱讀任務
```bash
cat TEST_INSTRUCTIONS.md
```

### 2️⃣ 重置環境
```bash
./tools/reset.sh
```

### 3️⃣ 開始測試
```bash
cd agent_workspace
pdflatex -interaction=nonstopmode survey.tex
```

### 4️⃣ 診斷問題
```bash
# 檢查編譯警告
grep "LaTeX Warning.*undefined" survey.log

# 檢查 .aux 檔案異常
grep "caption@xref" survey.aux

# 使用診斷工具
python ../tools/latex_fix_toolkit.py diagnose .
```

### 5️⃣ 實施修復
```bash
# 方式 1: 使用統一工具
python ../tools/latex_fix_toolkit.py fix-all .

# 方式 2: 手動修復
# - 編輯 figs/structure_fig.tex
# - 編輯 survey.tex
```

### 6️⃣ 驗證結果
```bash
pdflatex survey.tex  # 第二次編譯
../tools/verify.py .
../tools/compare.sh . ../fixed
```

---

## 🛠️ 可用工具詳解

### ⭐ 統一修復工具（推薦）

```bash
# 完整診斷
python ../tools/latex_fix_toolkit.py diagnose .

# 修復特定類型
python ../tools/latex_fix_toolkit.py fix-caption .      # Caption/Label 格式
python ../tools/latex_fix_toolkit.py fix-placement .    # Figure 放置
python ../tools/latex_fix_toolkit.py fix-refs .         # Figure 引用
python ../tools/latex_fix_toolkit.py fix-general .      # 一般問題

# 修復所有問題
python ../tools/latex_fix_toolkit.py fix-all .

# Dry-run 模式（預覽變更）
python ../tools/latex_fix_toolkit.py --dry-run fix-all .

# 查看幫助
python ../tools/latex_fix_toolkit.py --help
```

### 🔧 獨立工具（舊版，已整合）

- `fix_latex_issues.py` - 一般 LaTeX 問題
- `fix_figure_placement.py` - Figure 放置問題
- `fix_figure_refs.py` - Figure 引用問題
- `fix_caption_label.py` - Caption/Label 格式

### ✅ 驗證工具

```bash
# 重置測試環境
./tools/reset.sh

# 驗證修復是否成功
./tools/verify.py agent_workspace/

# 對比與正確答案的差異
./tools/compare.sh agent_workspace/ fixed/
```

---

## 📊 預期成果

| 指標 | broken/ | fixed/ | 變化 |
|------|---------|--------|------|
| PDF 頁數 | 85 | 80 | -5 頁 |
| 檔案大小 | 602 KB | 634 KB | +32 KB |
| undefined 引用 | 3 個 | 0 個 | ✅ 全部修復 |

### 關鍵修復差異

```diff
# survey.tex Line 578
- (see Figure~\ref{fig:tree_figure_Langu}):
+ (see Figure~5):

# survey.tex Line 701
- in Figure~\ref{fig:tiny_tree_figure_5}, three
+ in Figure~8, three

# figs/structure_fig.tex Line ~131
- Bandwidth and edge–server trade-offs
+ Bandwidth and edge--server trade-offs
```

---

## 🎯 不同角色的使用指南

### 🤖 AI Agent（測試模式）

**可以做的**:
- ✅ 閱讀 `README.md`（本檔案）
- ✅ 閱讀 `TEST_INSTRUCTIONS.md`
- ✅ 使用 `tools/` 中的所有工具
- ✅ 編譯、診斷、修復 `agent_workspace/`

**不可以做的**:
- ❌ 查看 `reference_only/` 中的任何文件
- ❌ 直接複製 `fixed/` 的內容

**測試目標**:
獨立診斷並修復 3 個引用問題，最終結果應與 `fixed/` 目錄一致。

---

### 👨‍💻 人類開發者

**快速入門**:
1. 閱讀本檔案
2. 閱讀 `TEST_INSTRUCTIONS.md`
3. 執行一次完整流程

**深入學習**:
1. 閱讀 `reference_only/LATEX_CAPTION_XREF_FIX.md` - 理解問題根因
2. 閱讀 `reference_only/LATEX_FIX_CHECKLIST.md` - 學習修復流程
3. 查閱 `reference_only/LATEX_FIX_QUICKREF.md` - 快速參考

**工具使用**:
- 優先使用 `latex_fix_toolkit.py`（統一介面）
- 需要時使用獨立工具進行精細控制

---

### 🔧 環境維護者

**理解結構**:
1. 本檔案 - 整體導航
2. `SANDBOX_COMPLETION_REPORT.md` - 建置過程
3. `SANDBOX_CHECKLIST.md` - 完整性驗證

**更新流程**:
1. 修改 `reference_only/` 中的對應文件
2. 更新本檔案的導航連結
3. 執行 `SANDBOX_CHECKLIST.md` 驗證完整性

**測試流程**:
```bash
# 1. 重置環境
./tools/reset.sh

# 2. 模擬 Agent 測試
cd agent_workspace
python ../tools/latex_fix_toolkit.py diagnose .
python ../tools/latex_fix_toolkit.py fix-all .

# 3. 驗證結果
../tools/verify.py .
../tools/compare.sh . ../fixed

# 4. 清理
cd .. && rm -rf agent_workspace/*
```

---

## 📝 重要注意事項

### 環境要求
- LaTeX 完整安裝（pdflatex, bibtex 等）
- Python 3.6+
- 磁碟空間約 5 MB

### 測試規則
1. ❌ Agent 測試時禁止查看 `reference_only/`
2. ✅ 應獨立診斷並解決問題
3. ✅ 可以使用提供的工具
4. ✅ 最終結果應與 `fixed/` 一致

### 常見問題

**Q: 為什麼 broken 是 85 頁，fixed 是 80 頁？**  
A: 修復後 LaTeX 重新調整了頁面佈局，減少了一些空白頁。

**Q: 可以直接複製 fixed 的內容嗎？**  
A: 測試時不可以！目的是訓練 Agent 的診斷和修復能力。

**Q: 工具會自動解決所有問題嗎？**  
A: `latex_fix_toolkit.py` 可以解決大部分問題，但仍需驗證結果。

---

## 🔗 相關文件

- **測試任務**: [TEST_INSTRUCTIONS.md](./TEST_INSTRUCTIONS.md)
- **完整技術文件**: [reference_only/LATEX_CAPTION_XREF_FIX.md](./reference_only/LATEX_CAPTION_XREF_FIX.md)
- **操作檢查清單**: [reference_only/LATEX_FIX_CHECKLIST.md](./reference_only/LATEX_FIX_CHECKLIST.md)
- **快速參考**: [reference_only/LATEX_FIX_QUICKREF.md](./reference_only/LATEX_FIX_QUICKREF.md)
- **環境建置報告**: [SANDBOX_COMPLETION_REPORT.md](./SANDBOX_COMPLETION_REPORT.md)
- **完整性檢查**: [SANDBOX_CHECKLIST.md](./SANDBOX_CHECKLIST.md)

---

**版本**: 1.0  
**最後更新**: 2025-10-17  
**維護者**: AI Agent (GitHub Copilot)  
**狀態**: ✅ 完整且可用

---

**開始測試**: `./tools/reset.sh` → `cd agent_workspace` → `pdflatex survey.tex`  
**獲取幫助**: `python tools/latex_fix_toolkit.py --help`
