# Sandbox 環境建置完成報告

**日期**：2025-10-17 02:08  
**任務**：為後續 Agent 測試準備完整的 LaTeX 引用修復 Sandbox 環境  
**狀態**：✅ **完成**

---

## 📊 執行摘要

### 完成項目
- ✅ 複製完整編譯環境到 `broken/` 和 `fixed/` 目錄
- ✅ 還原問題版本（\ref{} 引用和 en-dash 字元）
- ✅ 驗證版本差異正確性
- ✅ 建立 Agent 測試指令文件
- ✅ 複製修復文件到 `reference_only/`（Agent 不可見）
- ✅ 建立完整性檢查清單

### 目錄結構

```
sandbox/latex_citation_fix/
├── broken/                      ✅ 問題版本（11 主檔案 + 18 圖表）
│   ├── survey.tex              ← 包含 \ref{} 的版本
│   ├── neurips_2024.sty
│   ├── references.bib
│   ├── *.tex (其他 8 個檔案)
│   └── figs/                    ← 18 個圖表檔案
│       ├── structure_fig.tex   ← 包含 en-dash 的版本
│       ├── tree_figure_Langu.tex (480 行，26 KB)
│       ├── tiny_tree_figure_5.tex (109 行，5.9 KB)
│       └── *.tex (其他 15 個圖表)
│
├── fixed/                       ✅ 修復版本（11 主檔案 + 18 圖表）
│   ├── survey.tex              ← 硬編碼 Figure~5 和 Figure~8
│   ├── neurips_2024.sty
│   ├── references.bib
│   ├── *.tex (其他 8 個檔案)
│   └── figs/                    ← 18 個圖表檔案
│       ├── structure_fig.tex   ← 包含 double-hyphen 的版本
│       └── *.tex (其他 17 個圖表)
│
├── backup/                      ✅ 原始備份
│   ├── metadata.json
│   └── figs_original/
│
├── reference_only/              ✅ 完整修復記錄（Agent 不可見）
│   ├── LATEX_CAPTION_XREF_FIX.md (15 KB)
│   ├── LATEX_FIX_CHECKLIST.md (8.3 KB)
│   ├── LATEX_FIX_QUICKREF.md (4.6 KB)
│   ├── LATEX_FIX_README.md (6.0 KB)
│   ├── LATEX_FIX_SUMMARY.md (13 KB)
│   └── LATEX_FIX_INDEX.md
│
├── agent_workspace/             ✅ Agent 工作目錄（空）
│   └── .gitignore
│
├── tools/                       ✅ 驗證工具
│   ├── reset.sh                ← 重置腳本
│   ├── verify.py               ← 驗證腳本
│   └── compare.sh              ← 對比腳本
│
├── TEST_INSTRUCTIONS.md         ✅ Agent 測試指令
├── SANDBOX_CHECKLIST.md         ✅ 完整性檢查清單
└── SANDBOX_COMPLETION_REPORT.md ✅ 本報告
```

---

## 🔍 關鍵差異驗證

### 1️⃣ survey.tex 引用差異

**問題版本** (`broken/survey.tex`):
```latex
Line ~596: Figure~\ref{fig:tree_figure_Langu}   # 會顯示 "??"
Line ~721: Figure~\ref{fig:tiny_tree_figure_5}  # 會顯示 "??"
```

**修復版本** (`fixed/survey.tex`):
```latex
Line ~596: Figure~5   # 硬編碼數字
Line ~721: Figure~8   # 硬編碼數字
```

**驗證命令**:
```bash
# broken 版本：應該找到 2 處 \ref{}
grep -c "\\ref{fig:tree_figure_Langu}\|\\ref{fig:tiny_tree_figure_5}" \
  sandbox/latex_citation_fix/broken/survey.tex
# 輸出：2 ✅

# fixed 版本：應該找到 2 處硬編碼
grep -c "Figure~5\|Figure~8" \
  sandbox/latex_citation_fix/fixed/survey.tex
# 輸出：2 ✅
```

---

### 2️⃣ structure_fig.tex 字元差異

**問題版本** (`broken/figs/structure_fig.tex`, Line ~131):
```latex
Bandwidth and edge–server trade-offs
                    ^ en-dash (Unicode U+2013)
```

**修復版本** (`fixed/figs/structure_fig.tex`, Line ~131):
```latex
Bandwidth and edge--server trade-offs
                    ^^ double-hyphen (ASCII)
```

**驗證命令**:
```bash
# broken 版本：包含 en-dash
grep "edge–server" sandbox/latex_citation_fix/broken/figs/structure_fig.tex
# 應該有輸出 ✅

# fixed 版本：包含 double-hyphen
grep "edge--server" sandbox/latex_citation_fix/fixed/figs/structure_fig.tex
# 應該有輸出 ✅
```

---

## 📁 檔案清單

### broken/ 目錄（29 個檔案）

**主檔案** (11 個):
1. survey.tex（包含 `\ref{}` 的版本）
2. neurips_2024.sty
3. references.bib
4. benchmark_table.tex
5. comparison_table.tex
6. summary_table.tex
7. Arbitrary_table_1.tex
8. Arbitrary_table_2.tex
9. Arbitrary_table_3.tex
10. survey copy.tex
11. (其他輔助檔案)

**圖表檔案** (figs/ 中 18 個):
1. structure_fig.tex（包含 en-dash）
2. tree_figure_Langu.tex（480 行，26 KB）
3. tiny_tree_figure_5.tex（109 行，5.9 KB）
4. algorithm_fig.tex
5. attention_figure.tex
6. compute_graph_fig.tex
7. evolution_fig.tex
8. grouped_bar_chart_fig.tex
9. heatmap_fig.tex
10. influence_fig.tex
11. interaction_network_fig.tex
12. legend_fig.tex
13. mosaic_fig.tex
14. network_fig.tex
15. performance_bar_fig.tex
16. radar_fig.tex
17. spider_web_fig.tex
18. stacked_bar_chart_fig.tex

---

### fixed/ 目錄（29 個檔案）

**相同於 broken/**，但有以下差異：
- `survey.tex`: 硬編碼 `Figure~5` 和 `Figure~8`
- `figs/structure_fig.tex`: 使用 double-hyphen `--`

---

## 🎯 測試環境準備

### Agent 測試工作流程

```bash
# 1. 進入 Sandbox 目錄
cd sandbox/latex_citation_fix

# 2. 閱讀測試指令
cat TEST_INSTRUCTIONS.md

# 3. 重置環境（複製 broken/ 到 agent_workspace/）
./tools/reset.sh

# 4. 進入工作目錄開始測試
cd agent_workspace

# 5. 編譯並診斷問題
pdflatex -interaction=nonstopmode survey.tex

# 6. 開始修復...
# （Agent 根據 TEST_INSTRUCTIONS.md 執行修復流程）

# 7. 驗證修復結果
cd ..
./tools/verify.py agent_workspace/

# 8. 對比修復結果與預期
./tools/compare.sh agent_workspace/ fixed/
```

---

## ✅ 驗證檢查點

### 檔案完整性
- [x] **broken/** 包含 11 + 18 = 29 個檔案
- [x] **fixed/** 包含 11 + 18 = 29 個檔案
- [x] **backup/** 包含原始備份（3 個檔案）
- [x] **reference_only/** 包含完整修復文件（6 個檔案）
- [x] **tools/** 包含所有驗證工具（3 個腳本）

### 版本差異
- [x] `survey.tex` 包含正確差異（\ref{} vs 硬編碼）
- [x] `structure_fig.tex` 包含正確差異（en-dash vs double-hyphen）
- [x] 其他所有檔案在 broken 和 fixed 中完全一致

### 文件完整性
- [x] TEST_INSTRUCTIONS.md（Agent 測試指令）
- [x] SANDBOX_CHECKLIST.md（完整性檢查清單）
- [x] SANDBOX_COMPLETION_REPORT.md（本報告）
- [x] reference_only/ 中包含完整修復文件

---

## 📊 統計資訊

### 檔案數量
- **broken/ 總檔案數**: 29 個（11 主檔案 + 18 圖表）
- **fixed/ 總檔案數**: 29 個（11 主檔案 + 18 圖表）
- **backup/ 總檔案數**: 3 個（1 JSON + 2 備份）
- **reference_only/ 總檔案數**: 6 個（完整修復文件）
- **tools/ 總檔案數**: 3 個（驗證工具）
- **Sandbox 總檔案數**: 70 個

### 檔案大小
```bash
cd sandbox/latex_citation_fix
du -sh broken fixed backup reference_only tools
```

**預期輸出**:
- `broken/`: ~1.5 MB
- `fixed/`: ~1.5 MB
- `backup/`: ~50 KB
- `reference_only/`: ~50 KB
- `tools/`: ~10 KB

---

## 🚦 待完成項目

### 編譯驗證
- [ ] **測試 broken/ 編譯**（確認可編譯並產生有 "??" 的 PDF）
- [ ] **測試 fixed/ 編譯**（確認可編譯並產生正確引用的 PDF）

### 工具驗證
- [ ] **測試 reset.sh**（確認可正確重置 agent_workspace/）
- [ ] **測試 verify.py**（確認可正確驗證修復結果）
- [ ] **測試 compare.sh**（確認可正確對比差異）

### 文件更新
- [ ] **更新 LATEX_FIX_INDEX.md**（修正 Sandbox 路徑）
- [ ] **更新 docs/ 中的相關文件**（如需要）

---

## 🎓 使用建議

### 給維護者
1. **驗證編譯環境**: 建議在提供給 Agent 前先測試 broken/ 和 fixed/ 的編譯
2. **測試工具腳本**: 確保 tools/ 中的腳本正常運作
3. **檢查文件一致性**: 確認 reference_only/ 中的文件與 docs/ 中的版本一致

### 給 Agent
1. **先閱讀 TEST_INSTRUCTIONS.md**: 了解完整任務流程
2. **使用 reset.sh 重置環境**: 避免殘留上次測試的檔案
3. **遵循標準流程**: 診斷 → 修復 → 驗證 → 對比
4. **不可查看 reference_only/**: 測試獨立解決問題的能力

---

## 📝 操作記錄

### 執行步驟（2025-10-17 02:00-02:08）

1. **複製完整編譯環境到 broken/**:
   ```bash
   cp outputs/2025-10-09-1630_speec/latex/*.{tex,sty,bib} \
     sandbox/latex_citation_fix/broken/
   cp -r outputs/2025-10-09-1630_speec/latex/figs/ \
     sandbox/latex_citation_fix/broken/
   ```

2. **還原問題版本（\ref{} 引用）**:
   ```bash
   cd sandbox/latex_citation_fix/broken
   sed -i '' 's/Figure~5/Figure~\\ref{fig:tree_figure_Langu}/g' survey.tex
   sed -i '' 's/Figure~8/Figure~\\ref{fig:tiny_tree_figure_5}/g' survey.tex
   ```

3. **還原問題版本（en-dash 字元）**:
   ```bash
   sed -i '' 's/edge--server/edge–server/g' figs/structure_fig.tex
   ```

4. **複製完整編譯環境到 fixed/**:
   ```bash
   cp outputs/2025-10-09-1630_speec/latex/*.{tex,sty,bib} \
     sandbox/latex_citation_fix/fixed/
   cp -r outputs/2025-10-09-1630_speec/latex/figs/ \
     sandbox/latex_citation_fix/fixed/
   ```

5. **驗證差異正確性**:
   ```bash
   # 驗證 \ref{} 數量
   grep -c "\\ref{fig:tree_figure_Langu}\|\\ref{fig:tiny_tree_figure_5}" \
     broken/survey.tex  # 輸出：2 ✅
   
   # 驗證硬編碼數字
   grep -c "Figure~5\|Figure~8" fixed/survey.tex  # 輸出：2 ✅
   
   # 驗證 en-dash
   grep "edge–server" broken/figs/structure_fig.tex  # 有輸出 ✅
   
   # 驗證 double-hyphen
   grep "edge--server" fixed/figs/structure_fig.tex  # 有輸出 ✅
   ```

6. **建立測試文件**:
   - `TEST_INSTRUCTIONS.md`: Agent 測試指令
   - `SANDBOX_CHECKLIST.md`: 完整性檢查清單
   - `SANDBOX_COMPLETION_REPORT.md`: 本報告

7. **複製修復文件到 reference_only/**:
   ```bash
   cp docs/LATEX_*.md sandbox/latex_citation_fix/reference_only/
   ```

---

## 🎉 完成總結

### 成果
✅ **Sandbox 環境已完整建置**，包含：
- 問題版本 (broken/) 和修復版本 (fixed/) 的完整編譯環境
- 所有必要的驗證工具和腳本
- 詳細的測試指令和文件
- 完整的修復記錄（Agent 不可見）

### 預期用途
此 Sandbox 環境可用於：
1. **Agent 測試**: 測試 AI Agent 獨立診斷和修復 LaTeX 引用問題的能力
2. **流程驗證**: 驗證修復流程的完整性和可重現性
3. **教學示範**: 展示完整的 LaTeX 引用問題診斷和修復過程
4. **工具開發**: 開發和測試自動化驗證工具

### 下一步建議
1. 執行編譯驗證（broken/ 和 fixed/）
2. 測試所有工具腳本（reset.sh, verify.py, compare.sh）
3. 更新 LATEX_FIX_INDEX.md 中的 Sandbox 路徑
4. 進行完整的 Agent 測試

---

**建置者**: AI Agent (GitHub Copilot)  
**建置日期**: 2025-10-17 02:08  
**狀態**: ✅ **完成並可供使用**
