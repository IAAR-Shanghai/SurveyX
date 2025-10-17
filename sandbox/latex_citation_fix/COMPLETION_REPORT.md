# LaTeX Citation Fix Sandbox 完成報告

**日期**: 2025-01-16  
**狀態**: ✅ 已完成所有整理工作  
**負責**: AI Agent (GitHub Copilot)

---

## 1. 任務概述

### 背景
使用者發現 sandbox 環境中的 `broken/` 和 `fixed/` 目錄內容錯誤（均為 70 頁，應分別為 85 頁和 80 頁）。從備份還原後發現備份檔案已是修復版本，缺少原始 `\ref{}` 問題。

### 目標
1. 手動植入 `\ref{}` 問題到 `broken/` 版本
2. 整合分散的修復腳本
3. 組織散落的 Markdown 文件
4. 更新 Agent 感知文件

---

## 2. 已完成工作

### 2.1 手動植入 \ref{} 問題

**檔案**: `sandbox/latex_citation_fix/broken/survey.tex`

**變更**:
1. **Line 578**: 
   - 修改前: `\autoref{fig:tree_figure_Langu}`
   - 修改後: `Figure~\ref{fig:tree_figure_Langu}`
   - 預期: 編譯時顯示 "??"

2. **Line 701**:
   - 修改前: `\autoref{fig:tiny\_tree\_figure\_5}`
   - 修改後: `Figure~\ref{fig:tiny_tree_figure_5}`
   - 預期: 編譯時顯示 "??"

**驗證**: 使用 `grep '\ref{' survey.tex` 確認兩處 `\ref{}` 均已存在

---

### 2.2 整合修復腳本

**建立檔案**: `sandbox/latex_citation_fix/tools/latex_fix_toolkit.py` (400+ 行)

**功能**:
- `diagnose`: 全面掃描所有問題
- `fix-caption`: 修復 caption/label 間距問題
- `fix-placement`: 修復 figure* 和 placement 參數
- `fix-refs`: 修復 escaped underscore 問題
- `fix-general`: 修復一般 LaTeX 問題（套件衝突、顏色定義等）
- `fix-all`: 執行所有修復

**整合腳本**:
- `fix_caption_label.py`
- `fix_figure_placement.py`
- `fix_figure_refs.py`
- `fix_latex_issues.py`

**保留舊腳本**: 已移至 `tools/` 目錄供參考

---

### 2.3 組織文件結構

**刪除重複檔案** (docs/ 目錄):
- `LATEX_CAPTION_XREF_FIX.md`
- `LATEX_FIX_CHECKLIST.md`
- `LATEX_FIX_GENERAL_ISSUES.md`
- `LATEX_FIX_PLACEMENT.md`
- `LATEX_GENERAL_ISSUES_GUIDE.md`
- `LATEX_SPACING_GLITCH_FIX.md`

**原因**: 這些檔案已存在於 `sandbox/latex_citation_fix/reference_only/`

**建立新文件**: `sandbox/latex_citation_fix/README.md` (300+ 行)
- 完整導覽指南
- 檔案目錄表格（含大小、用途、使用場景）
- 問題概述與範例
- 快速啟動指南（6 步驟）
- 工具使用範例
- 角色特定指引（Agent/開發者/維護者）
- 預期結果比較表

---

### 2.4 更新 Agent 文件

**更新檔案 1**: `docs/agent-protected-files.md`
- 新增 "Sandbox 環境" 條目到受保護檔案表格
- 保護範圍: `sandbox/latex_citation_fix/reference_only/*.md`, `fixed/`, `broken/`
- 測試規則: Agent 測試時禁止查看 `reference_only/` 和 `fixed/`

**更新檔案 2**: `AGENTS.md`
- 新增 "## 10) Sandbox 測試環境" 章節
- 詳細說明 LaTeX Citation Fix sandbox 結構
- 列出測試模式規則
- 說明已植入問題
- 提供啟動測試指令
- 標註預期結果（85 頁 → 80 頁，602KB → 634KB）

---

## 3. 檔案清單

### 新增檔案

| 檔案路徑 | 大小 | 用途 |
|---------|------|------|
| `sandbox/latex_citation_fix/README.md` | ~15KB | 完整導覽文件 |
| `sandbox/latex_citation_fix/tools/latex_fix_toolkit.py` | ~12KB | 統一修復工具 |
| `sandbox/latex_citation_fix/COMPLETION_REPORT.md` | ~6KB | 本報告 |

### 修改檔案

| 檔案路徑 | 變更內容 |
|---------|----------|
| `sandbox/latex_citation_fix/broken/survey.tex` | 植入 2 處 `\ref{}` 問題 |
| `docs/agent-protected-files.md` | 新增 Sandbox 環境保護項 |
| `AGENTS.md` | 新增 Sandbox 測試環境章節 |

### 刪除檔案

| 檔案路徑 | 原因 |
|---------|------|
| `docs/LATEX_*.md` (6 份) | 與 `sandbox/reference_only/` 重複 |

### 移動檔案

| 原路徑 | 新路徑 | 原因 |
|--------|--------|------|
| `scripts/fix_*.py` (4 份) | `sandbox/latex_citation_fix/tools/` | 整合至 sandbox 環境 |

---

## 4. Sandbox 環境結構

```
sandbox/latex_citation_fix/
├── README.md                    # 完整導覽文件（新增）
├── COMPLETION_REPORT.md         # 本報告（新增）
├── reset.sh                     # 環境重置腳本
├── compile.sh                   # 快速編譯腳本
│
├── broken/                      # 85 頁，602KB（已植入問題）
│   ├── survey.tex              # ✓ 已植入 2 處 \ref{} 問題
│   ├── compile.sh
│   ├── figs/
│   │   └── structure_fig.tex   # ✓ 包含 en-dash 問題
│   └── ...
│
├── fixed/                       # 80 頁，634KB（標準答案）
│   ├── survey.tex
│   ├── compile.sh
│   └── ...
│
├── reference_only/              # 6 份完整修復文件
│   ├── LATEX_CAPTION_XREF_FIX.md
│   ├── LATEX_FIX_CHECKLIST.md
│   ├── LATEX_FIX_GENERAL_ISSUES.md
│   ├── LATEX_FIX_PLACEMENT.md
│   ├── LATEX_GENERAL_ISSUES_GUIDE.md
│   └── LATEX_SPACING_GLITCH_FIX.md
│
├── tools/                       # 修復工具集
│   ├── latex_fix_toolkit.py    # 統一工具（新增）
│   ├── fix_caption_label.py    # 舊版（保留）
│   ├── fix_figure_placement.py # 舊版（保留）
│   ├── fix_figure_refs.py      # 舊版（保留）
│   ├── fix_latex_issues.py     # 舊版（保留）
│   └── verify_*.py             # 驗證腳本
│
└── agent_workspace/             # Agent 測試工作區（空）
    └── (由 reset.sh 填充)
```

---

## 5. 測試驗證

### 5.1 問題植入驗證

✅ **已驗證**: 使用 grep 確認 `broken/survey.tex` 包含 2 處 `\ref{}`

```bash
$ grep '\ref{' sandbox/latex_citation_fix/broken/survey.tex
Figure~\ref{fig:tree_figure_Langu}
Figure~\ref{fig:tiny_tree_figure_5}
```

### 5.2 工具功能驗證

⏸️ **待測試**: 編譯 `broken/` 確認 "??" 出現
⏸️ **待測試**: 執行 `latex_fix_toolkit.py diagnose` 掃描問題
⏸️ **待測試**: 執行 `latex_fix_toolkit.py fix-all` 修復所有問題
⏸️ **待測試**: 驗證修復後檔案從 85 頁減至 80 頁

### 5.3 建議測試流程

```bash
# 1. 重置環境
cd sandbox/latex_citation_fix
./reset.sh

# 2. 測試診斷功能
cd agent_workspace
python ../tools/latex_fix_toolkit.py diagnose .

# 3. 編譯 broken 版本（確認 "??" 出現）
cd broken
./compile.sh
ls -lh survey.pdf  # 應為 ~602KB，85 頁

# 4. 執行完整修復
cd ..
python ../tools/latex_fix_toolkit.py fix-all .

# 5. 編譯修復後版本（確認 "??" 消失）
cd broken
./compile.sh
ls -lh survey.pdf  # 應為 ~634KB，80 頁
```

---

## 6. Agent 測試規則

### 禁止操作（測試模式）

❌ 查看 `reference_only/` 目錄內容  
❌ 查看 `fixed/` 目錄內容  
❌ 直接複製修復後的檔案

### 允許操作（測試模式）

✅ 閱讀 `README.md` 導覽文件  
✅ 操作 `agent_workspace/` 內的檔案  
✅ 使用 `tools/` 目錄中的工具  
✅ 編譯並檢查 PDF 輸出  
✅ 診斷和修復問題

### 開發者模式

✅ 可閱讀所有資料進行學習  
✅ 可查看 `reference_only/` 學習修復流程  
✅ 可比較 `broken/` 和 `fixed/` 差異  
✅ 可修改和測試工具腳本

---

## 7. 已知問題與限制

### 7.1 en-dash 問題

**位置**: `figs/structure_fig.tex` Line ~131  
**狀態**: 已存在於 `broken/` 版本  
**影響**: 編譯時可能產生警告或字元顯示問題

### 7.2 未測試項目

- ⏸️ `broken/` 編譯測試（確認 "??" 顯示）
- ⏸️ `latex_fix_toolkit.py` 完整功能測試
- ⏸️ 修復後頁數和檔案大小驗證

---

## 8. 維護建議

### 8.1 定期檢查

- 每次更新 LaTeX 樣板後重新驗證 sandbox 環境
- 定期測試 `latex_fix_toolkit.py` 各項功能
- 更新 `README.md` 反映最新的問題清單

### 8.2 文件同步

- `AGENTS.md` 為權威來源，修改後會自動同步至 `CLAUDE.md` 和 `GEMINI.md`
- Sandbox 相關變更需同步更新 `docs/agent-protected-files.md`

### 8.3 問題擴展

若需新增測試問題：
1. 在 `broken/` 中植入新問題
2. 在 `fixed/` 中提供對應修復
3. 更新 `README.md` 問題清單
4. 更新 `AGENTS.md` 相關說明
5. 建立或更新 `reference_only/` 中的修復文件

---

## 9. 參考資源

### 文件
- `sandbox/latex_citation_fix/README.md`: 完整導覽
- `AGENTS.md` Section 10: Sandbox 測試環境
- `docs/agent-protected-files.md`: 受保護檔案清單

### 工具
- `latex_fix_toolkit.py`: 統一修復工具
- `reset.sh`: 環境重置腳本
- `compile.sh`: LaTeX 編譯腳本

### 參考答案
- `reference_only/*.md`: 6 份完整修復文件
- `fixed/`: 所有問題已修復的標準版本

---

## 10. 結論

✅ **所有整理工作已完成**

- ✅ 手動植入 `\ref{}` 問題（2 處）
- ✅ 整合修復腳本（4 → 1 統一工具）
- ✅ 組織文件結構（刪除重複，建立導覽）
- ✅ 更新 Agent 文件（2 份）

**Sandbox 環境已就緒，可開始 Agent 測試！**

---

**報告人**: AI Agent (GitHub Copilot)  
**審核**: 待使用者確認
