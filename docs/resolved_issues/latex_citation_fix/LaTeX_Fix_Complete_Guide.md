# LaTeX Citation & Compilation Fix - 完整指南

> **統整文件**: 整合所有 LaTeX 相關問題的診斷、修復與驗證  
> **最後更新**: 2025-10-16  
> **適用對象**: 開發者、維護者、AI Agent

---

## 📋 快速導覽

- [問題總覽](#問題總覽)
- [一鍵修復](#一鍵修復)
- [手動修復步驟](#手動修復步驟)
- [根本原因分析](#根本原因分析)
- [驗證方法](#驗證方法)
- [Sandbox 練習環境](#sandbox-練習環境)

---

## 問題總覽

### 🔴 已修復的問題

| 編號 | 問題描述 | 嚴重程度 | 狀態 |
|------|---------|---------|------|
| 1 | natbib package option clash | 🔥 Critical | ✅ Fixed |
| 2 | xcolor undefined colors (c12-c16) | 🔥 Critical | ✅ Fixed |
| 3 | Duplicate `\bibliographystyle` | ⚠️ Warning | ✅ Fixed |
| 4 | Wrong bibliography order | ⚠️ Warning | ✅ Fixed |
| 5 | Pages 75-86 citations as plain text | 🔥 Critical | ✅ Fixed |
| 6 | Page 58 spacing glitch | ℹ️ Minor | ✅ Fixed |

### 🟡 已識別但需另案處理

| 編號 | 問題描述 | 位置 | 處理計畫 |
|------|---------|------|---------|
| 7 | Source code double-escape bug | `src/modules/latex_handler/latex_figure_builder.py:600` | 需新 thread 處理 |

---

## 一鍵修復

### 使用 Python 腳本 (推薦)

```bash
# 基本用法
python scripts/fix_latex_issues.py outputs/YOUR_TASK_ID/latex

# 乾跑模式 (預覽變更)
python scripts/fix_latex_issues.py outputs/YOUR_TASK_ID/latex --dry-run

# 實際案例
python scripts/fix_latex_issues.py outputs/2025-10-09-1630_speec/latex
```

**腳本會自動**:
1. ✅ 備份所有原始檔案 (加上時間戳記)
2. ✅ 修復 `survey.tex` 的所有問題
3. ✅ 批次修復 `figs/*.tex` 中的 double-escaped citations
4. ✅ 驗證修復結果
5. ✅ 輸出詳細報告

### 輸出範例

```
============================================================
LaTeX Survey Auto-Fixer
============================================================
Target: outputs/2025-10-09-1630_speec/latex
Mode: LIVE
============================================================

📝 Fixing survey.tex...
   ✅ Backup: survey.tex.backup_20251016_143022
   ✅ Added PassOptionsToPackage for xcolor and natbib
   ✅ Added color definitions (c12-c16)
   ✅ Removed 1 duplicate bibliographystyle command(s)
   ✅ Fixed bibliography command order

📊 Fixing TikZ figures...
   ✅ Fixed 245 double-escaped citation(s) in 14 file(s)
      - tiny_tree_figure_1.tex
      - tiny_tree_figure_2.tex
      - tiny_tree_figure_3.tex
      - tiny_tree_figure_4.tex
      - tiny_tree_figure_5.tex
      ... and 9 more

🔍 Verifying fixes...
   ✅ PassOptionsToPackage for xcolor
   ✅ PassOptionsToPackage for natbib
   ✅ All color definitions present
   ✅ Only one bibliographystyle command
   ✅ No double-escaped citations in figs/

============================================================
Summary
============================================================
🎉 All issues fixed successfully!

Fixed issues:
  ✅ Fixed 4 issue(s) in survey.tex
  ✅ Fixed citations in 14 figure files

💾 Backup files saved with suffix: .backup_20251016_143022
============================================================
```

---

## 手動修復步驟

如果需要手動修復或理解每個步驟:

### Step 1: 修復 survey.tex

#### 1.1 Add PassOptionsToPackage (行 1-6)

**在 `\documentclass` 之前** 加入:

```latex
% === FIX: Prevent package option clashes ===
\PassOptionsToPackage{dvipsnames,usenames}{xcolor}
\PassOptionsToPackage{numbers}{natbib}
% ===========================================

\documentclass{article}
```

#### 1.2 Define Missing Colors (行 30-42)

**在載入 xcolor 之後** 加入:

```latex
% === FIX: Define missing colors for TikZ figures ===
\definecolor{c12}{RGB}{100,149,237}  % Cornflower Blue
\definecolor{c13}{RGB}{144,238,144}  % Light Green  
\definecolor{c14}{RGB}{255,182,193}  % Light Pink
\definecolor{c15}{RGB}{255,218,185}  % Peach Puff
\definecolor{c16}{RGB}{221,160,221}  % Plum
% ====================================================
```

#### 1.3 Remove Duplicate bibliographystyle (行 35)

找到重複的 `\bibliographystyle{unsrt}` 並註解掉:

```latex
% \bibliographystyle{unsrt}  % REMOVED: Duplicate
```

#### 1.4 Fix Bibliography Order (行 1632-1633)

確保順序為 **style → bibliography**:

```latex
\bibliographystyle{unsrt}
\bibliography{references}
```

#### 1.5 Fix Page 58 Spacing (行 1454)

在密集的段落之間加入空行:

```latex
... existing paragraph text ...

% Add paragraph break here

... next paragraph ...
```

### Step 2: 批次修復 TikZ Figures

#### 問題: 所有 `figs/*.tex` 中的 citations 都是 `\\cite{}` (double-escaped)

```bash
cd outputs/YOUR_TASK_ID/latex/figs

# 備份
for f in *.tex; do cp "$f" "$f.bak"; done

# 批次修復 (使用 sed)
sed -i '' 's/\\\\cite{/\\cite{/g' *.tex

# 驗證
grep -n '\\\\cite' *.tex  # 應該找不到任何結果
```

**影響的檔案** (14 個):
- `tiny_tree_figure_1.tex` ~ `tiny_tree_figure_14.tex`

**修復數量**: 245 個 double-escaped citations

---

## 根本原因分析

### 核心問題: Python JSON 解析 + String Escaping

**問題位置**: `src/modules/latex_handler/latex_figure_builder.py` Line 600

```python
# PROBLEMATIC CODE
json_str = json_str.replace("\\", "\\\\")  # ❌ This causes \\cite{}
```

**問題鏈條**:

```
Step 1: SurveyX 生成 JSON
{
  "citations": ["\\cite{smith2020}"]  ← 正常的單一反斜線
}

Step 2: Python 讀取 JSON
json.loads(json_str)  ← 正確解析為 \cite{smith2020}

Step 3: latex_figure_builder.py Line 600
json_str.replace("\\", "\\\\")  ← ❌ 變成 \\cite{smith2020}

Step 4: 寫入 TikZ .tex 檔案
\node{\\cite{smith2020}};  ← ❌ 雙反斜線

Result: LaTeX 編譯時
TikZ 將 \\cite{smith2020} 當作純文字,而不是引用指令
→ PDF 顯示 "\\cite{smith2020}" 而不是 "[42]"
```

### 為什麼 Pages 75-86 受影響?

- Pages 75-86 包含 **TikZ tree diagrams** (圖表 1-14)
- 這些圖表由 `latex_figure_builder.py` 自動生成
- 所有圖表中的 citations 都經過這個有問題的 `.replace()` 處理
- 其他頁面的 citations 是直接寫在 survey.tex 主文中,未受影響

### 解決方案選項

**方案 A: 移除問題行** (推薦)
```python
# 直接刪除 Line 600
# json_str = json_str.replace("\\", "\\\\")  # REMOVED
```

**方案 B: 條件式處理**
```python
# 只在必要時進行 escape
if not already_escaped(json_str):
    json_str = json_str.replace("\\", "\\\\")
```

**方案 C: 使用正確的 JSON 處理**
```python
# 直接操作 Python dict,不要手動處理字串
data = json.loads(json_str)
# Process data...
return json.dumps(data, ensure_ascii=False)
```

⚠️ **注意**: 修改 source code 需在新 thread 進行完整測試,因為可能影響其他功能。

---

## 驗證方法

### 自動驗證腳本

```bash
# 使用 sandbox 驗證工具
cd sandbox/latex_citation_fix
python tools/verify.py ../agent_workspace
```

### 手動驗證檢查清單

#### ✅ survey.tex
- [ ] `\PassOptionsToPackage{dvipsnames,usenames}{xcolor}` 存在
- [ ] `\PassOptionsToPackage{numbers}{natbib}` 存在
- [ ] 所有顏色定義存在 (c12-c16)
- [ ] 只有一個 `\bibliographystyle` 指令
- [ ] Bibliography 順序正確 (style → bibliography)

#### ✅ figs/*.tex
- [ ] 沒有任何 `\\cite{` (double backslash)
- [ ] 所有 citations 都是 `\cite{` (single backslash)

#### ✅ PDF 編譯
```bash
cd outputs/YOUR_TASK_ID/latex
pdflatex survey.tex
bibtex survey
pdflatex survey.tex
pdflatex survey.tex
```

檢查:
- [ ] 編譯無錯誤
- [ ] PDF 生成成功
- [ ] Pages 75-86 citations 顯示為數字 (如 [4], [60])
- [ ] Page 58 排版正常

---

## Sandbox 練習環境

### 快速設置

```bash
# 一鍵設置 sandbox (在專案根目錄)
cd sandbox/latex_citation_fix

# 1. 從實際輸出複製檔案到 broken/
cp -r ../../outputs/2025-10-09-1630_speec/latex/* broken/

# 2. 測試修復腳本
python ../../scripts/fix_latex_issues.py broken/ --dry-run

# 3. 實際修復
python ../../scripts/fix_latex_issues.py broken/

# 4. 驗證
python tools/verify.py broken/

# 5. 與參考解法比較
./tools/compare.sh

# 6. 重置環境 (重新練習)
./tools/reset.sh
```

### Sandbox 結構

```
sandbox/latex_citation_fix/
├── README.md              # 說明文件
├── backup/               # 原始問題檔案 (已修復)
│   ├── survey.tex.ORIGINAL_BROKEN
│   ├── figs/
│   │   └── *.tex.ORIGINAL_BROKEN
│   └── metadata.json
├── broken/               # 問題檔案 (供練習)
│   ├── survey.tex
│   └── figs/*.tex
├── fixed/                # 參考解法
│   ├── survey.tex
│   └── figs/*.tex
├── agent_workspace/      # AI Agent 工作區
│   └── .gitignore
└── tools/
    ├── verify.py         # 驗證腳本
    ├── reset.sh          # 重置環境
    └── compare.sh        # 比較差異
```

### 驗證工具詳情

**verify.py** - 8 項自動檢查:
1. PassOptionsToPackage for xcolor
2. PassOptionsToPackage for natbib
3. Color definitions (c12-c16)
4. Duplicate bibliographystyle
5. Bibliography order
6. Double-escaped citations
7. File structure
8. Compilation readiness

**reset.sh** - 重置工作環境:
- 清空 `agent_workspace/`
- 從 `broken/` 複製新鮮的問題檔案

**compare.sh** - 比較修復結果:
- 對比 `agent_workspace/` vs `fixed/`
- 顯示差異摘要

---

## 常見問題 FAQ

### Q1: 修復後 PDF 仍有問題?

**檢查步驟**:
```bash
# 1. 完整清理並重新編譯
cd outputs/YOUR_TASK_ID/latex
rm -f *.aux *.bbl *.blg *.log *.out

# 2. 完整編譯流程
pdflatex survey.tex
bibtex survey
pdflatex survey.tex
pdflatex survey.tex

# 3. 檢查 log
grep -i error survey.log
grep -i warning survey.log
```

### Q2: 如何確認 citations 已正確修復?

```bash
# 檢查是否還有 double-escaped
cd outputs/YOUR_TASK_ID/latex/figs
grep '\\\\cite' *.tex

# 應該沒有任何輸出
# 如果有輸出,表示還有遺漏的檔案
```

### Q3: 備份檔案太多怎麼辦?

```bash
# 列出所有備份
find . -name "*.backup_*" -o -name "*.ORIGINAL_BROKEN"

# 保留最新的備份,刪除舊的
find . -name "*.backup_*" -mtime +7 -delete  # 刪除 7 天前的
```

### Q4: 可以在其他 task_id 上使用嗎?

✅ 可以! 腳本設計為通用解決方案:

```bash
# 適用於任何 outputs/<task_id>/latex
python scripts/fix_latex_issues.py outputs/2025-10-09-1038_speec/latex
python scripts/fix_latex_issues.py outputs/test_task/latex
python scripts/fix_latex_issues.py outputs/gpt-5-nano\(high\)/latex
```

---

## 相關資源

### 文件
- `docs/temporary_issues/LaTeX_Fix_Complete_Guide.md` (本文件)
- `sandbox/latex_citation_fix/README.md` - Sandbox 使用說明
- `scripts/fix_latex_issues.py` - 自動修復腳本

### 程式碼
- `src/modules/latex_handler/latex_figure_builder.py` - 需修復的 source code
- `tasks/workflow/06_generate_latex.py` - LaTeX 生成流程
- `src/modules/latex_handler/latex_generator.py` - LaTeX 產生器

### 外部資源
- [LaTeX Package Documentation](https://www.ctan.org/)
- [TikZ Manual](https://tikz.dev/)
- [natbib Documentation](https://ctan.org/pkg/natbib)

---

## 變更歷史

| 日期 | 版本 | 變更內容 |
|------|------|---------|
| 2025-10-16 | 1.0 | 初始版本,整合所有 LaTeX 修復文件 |

---

## 附錄: 修復前後對比

### A. survey.tex 前後對比

**修復前**:
```latex
\documentclass{article}
\usepackage{xcolor}  % ❌ 會造成 option clash
\usepackage{natbib}  % ❌ 會造成 option clash

% ❌ 缺少顏色定義

\bibliographystyle{unsrt}  % ❌ 重複定義
% ...中間內容...
\bibliography{references}  % ❌ 順序錯誤
\bibliographystyle{unsrt}
```

**修復後**:
```latex
\PassOptionsToPackage{dvipsnames,usenames}{xcolor}  % ✅
\PassOptionsToPackage{numbers}{natbib}              % ✅

\documentclass{article}
\usepackage{xcolor}
\usepackage{natbib}

\definecolor{c12}{RGB}{100,149,237}  % ✅
\definecolor{c13}{RGB}{144,238,144}  % ✅
% ... c14-c16 ...

% ...中間內容...
\bibliographystyle{unsrt}    % ✅ 順序正確
\bibliography{references}
```

### B. TikZ Figure 前後對比

**修復前** (tiny_tree_figure_3.tex):
```latex
\node[draw] at (2,3) {
    Task: \\cite{smith2020}  % ❌ 雙反斜線
    Method: \\cite{jones2021}
};
```

**PDF 顯示**: `\\cite{smith2020}` (純文字)

**修復後**:
```latex
\node[draw] at (2,3) {
    Task: \cite{smith2020}  % ✅ 單反斜線
    Method: \cite{jones2021}
};
```

**PDF 顯示**: `[42] [58]` (正確的引用編號)

---

**文件結束** | 如有問題請參考 `docs/guides/temporary_issue_maintenance.md`
