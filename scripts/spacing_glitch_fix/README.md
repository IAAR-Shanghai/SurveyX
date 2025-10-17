# Spacing Glitch 修復工具集

**目的**: 修復 SurveyX 生成的 LaTeX/PDF 中的 spacing glitch 問題（字詞黏在一起）

**問題根源**: 
- LLM 生成內容時使用 Unicode 數學符號（≈, →, ×, ∈ 等）而非 LaTeX 命令
- 未轉義的 underscore (`_`) 觸發數學模式，吃掉後續空格
- 數學變數格式錯誤（如 `N_s` 而非 `$N_{s}$`）
- 表格 `\cite{}` 前缺空格

---

## 📁 工具清單

| 腳本檔案 | 功能 | 類型 |
|---------|------|------|
| `detect_unicode_glitches.py` | 偵測 Unicode 符號 | 檢測工具 |
| `fix_unicode_glitches.py` | 修復 Unicode 符號 | 自動修復 |
| `fix_underscores.py` | 修復未轉義 underscore | 自動修復 |
| `check_special_unicode.py` | 分析特殊字元分布 | 檢測工具 |
| `fix_and_recompile.py` | 一鍵修復+重新編譯 | 整合工具 (Python) |
| `fix_and_recompile.sh` | 一鍵修復+重新編譯 | 整合工具 (Bash) |

---

## 🚀 快速開始（推薦流程）

### 方案 A: 一鍵修復（適合快速處理）

```bash
# 進入專案根目錄
cd /path/to/SurveyX

# 啟動環境
conda activate surveyx

# 一鍵修復（Python 版本，推薦）
python scripts/spacing_glitch_fix/fix_and_recompile.py <task_id>

# 範例
python scripts/spacing_glitch_fix/fix_and_recompile.py 2025-10-09-1630_speec
```

**執行流程**:
1. 偵測 Unicode 符號並生成報告
2. 自動備份原始檔案（加時間戳）
3. 修復 Unicode 符號 → LaTeX 命令
4. 重新編譯 LaTeX 生成 PDF
5. 生成帶浮水印版本

**輸出檔案**:
```
outputs/<task_id>/
├── latex/
│   ├── survey.tex                         # 修復後的源碼
│   ├── survey.tex.backup_YYYYMMDD_HHMMSS # 原始備份
│   └── compile.log                        # 編譯日誌
├── tmp/
│   ├── unicode_report_before.txt          # 修復前報告
│   └── unicode_report_after.txt           # 修復後驗證
├── survey.pdf                             # 修復後 PDF
└── survey_wtmk.pdf                        # 帶浮水印版本
```

---

### 方案 B: 分步驟執行（適合深入檢查）

#### Step 1: 偵測問題

```bash
# 檢測 Unicode 符號
python scripts/spacing_glitch_fix/detect_unicode_glitches.py \
  outputs/<task_id>/latex/survey.tex

# 輸出範例:
# Total Unicode symbols found: 2334
# Unique symbol types: 18
# Affected lines: 391
#
# Frequency by Symbol:
#   ‑ (NON-BREAKING HYPHEN): 1828 occurrences
#   ≈ ($\approx$): 309 occurrences
#   → ($\rightarrow$): 96 occurrences
#   ...

# 分析特殊字元分布（可選）
python scripts/spacing_glitch_fix/check_special_unicode.py \
  outputs/<task_id>/latex/survey.tex
```

#### Step 2: 預覽修復（不實際修改）

```bash
# 預覽 Unicode 修復
python scripts/spacing_glitch_fix/fix_unicode_glitches.py \
  outputs/<task_id>/latex/survey.tex --preview

# 預覽 underscore 修復
python scripts/spacing_glitch_fix/fix_underscores.py \
  outputs/<task_id>/latex/survey.tex --preview
```

#### Step 3: 執行自動修復

```bash
# 修復 Unicode 符號（自動備份）
python scripts/spacing_glitch_fix/fix_unicode_glitches.py \
  outputs/<task_id>/latex/survey.tex

# 修復 underscore（自動備份）
python scripts/spacing_glitch_fix/fix_underscores.py \
  outputs/<task_id>/latex/survey.tex
```

#### Step 4: 手動修復數學變數

**無法用腳本自動修復的問題**:
- 數學變數格式錯誤（需要語義理解）
- 表格寬度調整（需要 LaTeX 排版知識）
- 未定義引用（需要檢查多個檔案）

**常見數學變數錯誤與修正**:

| 錯誤寫法 | 正確寫法 | 說明 |
|---------|---------|------|
| `N_s∈{0,1}` | `$N_{s} \in \{0,1\}$` | 整個表達式要在 `$...$` 內 |
| `2^{14}` | `$2^{14}$` | 指數要在數學模式 |
| `$\tau$_SC=5` | `$\tau_{SC}=5$` | 下標要在同一個 `$...$` 內 |
| `T_chunk$\approx$1 s` | `$T_{chunk} \approx 1$ s` | 數學部分完整包起來 |
| `frame_rate_hz` | `frame\_rate\_hz` | 技術術語的 underscore 需轉義 |

**手動修復步驟**:
1. 搜尋可疑模式: `grep -n "_[a-zA-Z]" survey.tex | grep -v "\\\\\_"`
2. 打開編輯器，逐行檢查上下文
3. 判斷是變數名（需 `$...$`）還是檔案名/技術術語（需 `\_`）
4. 修正後重新編譯驗證

#### Step 5: 重新編譯

```bash
cd outputs/<task_id>/latex

# 清除舊的編譯產物
latexmk -C

# 重新編譯
latexmk -pdf -interaction=nonstopmode -f survey.tex

# 檢查編譯日誌中的錯誤
grep -i "error\|warning" compile.log | head -20
```

#### Step 6: 驗證修復效果

```bash
# 提取 PDF 文字檢查是否還有長串黏在一起的字
pdftotext outputs/<task_id>/survey.pdf - | grep -o -E "\w{30,}"

# 如果沒有輸出或只有 URL/citation key，表示修復成功
# 如果還有類似 "avoidingadversarialtrainingand..." 的字串，表示還有問題
```

---

## 📖 各腳本詳細說明

### 1. detect_unicode_glitches.py

**功能**: 掃描 `.tex` 檔案中的 Unicode 數學符號並生成報告

**使用方式**:
```bash
# 基本用法（輸出到螢幕）
python detect_unicode_glitches.py <tex_file>

# 儲存報告到檔案
python detect_unicode_glitches.py <tex_file> -o report.txt

# 只顯示摘要（不顯示詳細位置）
python detect_unicode_glitches.py <tex_file> --summary
```

**輸出內容**:
- 總計 Unicode 符號數量
- 符號類型分布（前 10 名）
- 每個符號的行號、列號與上下文
- 建議的 LaTeX 替代命令

**範例**:
```bash
python detect_unicode_glitches.py outputs/2025-10-09-1630_speec/latex/survey.tex
```

輸出:
```
================================================================================
Unicode Glitch Detection Report
File: outputs/2025-10-09-1630_speec/latex/survey.tex
================================================================================

## Summary
Total Unicode symbols found: 2334
Unique symbol types: 18
Affected lines: 391

## Frequency by Symbol
  ‑ (NON-BREAKING HYPHEN): 1828 occurrences → Use: - (regular hyphen)
  ≈ ($\approx$): 309 occurrences → Use: $\approx$
  → ($\rightarrow$): 96 occurrences → Use: $\rightarrow$
  × ($\times$): 53 occurrences → Use: $\times$
  ...

## Detailed Locations
Line 295, Col 73: ... N_s∈{0,1}, N_a∈[1,8]; ...
                        ^^^^
  Suggestion: Replace ∈ with $\in$

...
```

---

### 2. fix_unicode_glitches.py

**功能**: 自動將 Unicode 符號替換為 LaTeX 命令

**支援的符號對應** (共 50+ 種):

| 類別 | Unicode → LaTeX |
|------|-----------------|
| **數學符號** | ≈→`$\approx$`, →→`$\rightarrow$`, ×→`$\times$`, ∈→`$\in$`, ≤→`$\le$`, ≥→`$\ge$` |
| **希臘字母** | α→`$\alpha$`, β→`$\beta$`, θ→`$\theta$`, λ→`$\lambda$`, μ→`$\mu$`, σ→`$\sigma$` |
| **標點符號** | ‑→`-`, –→`--`, —→`---`, '→`` ` ``, '→`'`, "→``` `` ```, "→`''` |

**使用方式**:
```bash
# 預覽變更（不實際修改）
python fix_unicode_glitches.py <tex_file> --preview

# 執行修復（自動備份）
python fix_unicode_glitches.py <tex_file>

# 修復並儲存到新檔案
python fix_unicode_glitches.py <tex_file> -o output.tex

# 修復但不建立備份（不建議）
python fix_unicode_glitches.py <tex_file> --no-backup
```

**智慧偵測**:
- 檢查符號是否已在數學模式內（`$ $`, `\( \)`, `\begin{equation}` 等）
- 如果已在數學模式，只替換符號本身，不加 `$...$`
- 如果在正文中，自動加上 `$...$`

**範例**:
```bash
# 執行修復
python fix_unicode_glitches.py outputs/2025-10-09-1630_speec/latex/survey.tex
```

輸出:
```
================================================================================
Unicode Glitch Fix Summary
================================================================================
Input file:         outputs/2025-10-09-1630_speec/latex/survey.tex
Output file:        outputs/2025-10-09-1630_speec/latex/survey.tex
Backup file:        outputs/2025-10-09-1630_speec/latex/survey.tex.backup_20251016_140530
Total lines:        1626
Lines modified:     391
Total replacements: 2334
================================================================================
✓ Successfully fixed 2334 Unicode symbols!
```

**修復前後對比**:
```latex
# 修復前
DiffSoundStream emits semantic and acoustic tokens at 12.5 Hz with N_s∈{0,1}, N_a∈[1,8]

# 修復後
DiffSoundStream emits semantic and acoustic tokens at 12.5 Hz with N_s$\in${0,1}, N_a$\in$[1,8]
```

---

### 3. fix_underscores.py

**功能**: 轉義正文中的 underscore (`_` → `\_`)

**問題說明**:
- LaTeX 中 `_` 只能在數學模式使用（如 `$x_i$`）
- 正文中的 `_` 會觸發數學模式，吃掉後續所有空格
- 導致 `tiny_tree_figure_0` 變成 spacing glitch

**使用方式**:
```bash
# 預覽變更
python fix_underscores.py <tex_file> --preview

# 執行修復（自動備份）
python fix_underscores.py <tex_file>

# 指定輸出檔案
python fix_underscores.py <tex_file> -o output.tex

# 不建立備份
python fix_underscores.py <tex_file> --no-backup
```

**處理邏輯**:
1. 簡單的數學模式檢測（計算 `$` 數量）
2. 跳過特殊命令中的 underscore:
   - `\cite{...}`, `\input{...}`, `\label{...}`, `\ref{...}`, `\autoref{...}`
   - `\begin{...}`, `\end{...}`
3. 正文中的 `_` 轉義為 `\_`

**限制**:
- 無法 100% 準確判斷數學模式（嵌套、跨行等）
- 可能誤轉義某些應該在數學模式的 underscore
- 建議執行後手動檢查關鍵區域

**範例**:
```bash
python fix_underscores.py outputs/2025-10-09-1630_speec/latex/survey.tex
```

輸出:
```
================================================================================
Underscore Fix Summary
================================================================================
Input file:         outputs/2025-10-09-1630_speec/latex/survey.tex
Output file:        outputs/2025-10-09-1630_speec/latex/survey.tex
Backup file:        outputs/2025-10-09-1630_speec/latex/survey.tex.backup_underscore
Total lines:        1626
Lines modified:     47
Total replacements: 58
================================================================================
✓ Successfully fixed 58 underscores!
```

**修復前後對比**:
```latex
# 修復前
\autoref{fig:tiny_tree_figure_0} shows the architecture.
The frame_rate_hz and bitrate_kbps are important metrics.

# 修復後
\autoref{fig:tiny\_tree\_figure\_0} shows the architecture.
The frame\_rate\_hz and bitrate\_kbps are important metrics.
```

---

### 4. check_special_unicode.py

**功能**: 詳細分析檔案中的所有 Unicode 字元分布

**使用方式**:
```bash
# 分析單一檔案
python check_special_unicode.py <tex_file>

# 分析並儲存報告
python check_special_unicode.py <tex_file> -o analysis.txt

# 只顯示非 ASCII 字元
python check_special_unicode.py <tex_file> --non-ascii-only
```

**輸出內容**:
- 字元範圍統計（ASCII, Latin-1, Unicode 等）
- 每種字元的數量與位置
- 潛在問題字元列表（數學符號、特殊標點等）

**範例**:
```bash
python check_special_unicode.py outputs/2025-10-09-1630_speec/latex/survey.tex
```

輸出:
```
================================================================================
Unicode Character Analysis Report
File: outputs/2025-10-09-1630_speec/latex/survey.tex
================================================================================

## Character Range Statistics
ASCII (0-127):           99.2%  (161,245 chars)
Latin-1 Supplement:       0.0%  (0 chars)
Mathematical Operators:   0.5%  (815 chars)
Greek Letters:            0.1%  (163 chars)
Special Punctuation:      0.2%  (325 chars)

## Potentially Problematic Characters
‑ (U+2011, NON-BREAKING HYPHEN): 1828 occurrences
  → Should use: - (regular hyphen)

≈ (U+2248, ALMOST EQUAL TO): 309 occurrences
  → Should use: $\approx$

...
```

---

### 5. fix_and_recompile.py (推薦)

**功能**: 整合所有修復步驟的一鍵腳本（Python 版本）

**執行流程**:
1. 偵測 Unicode 符號
2. 備份原始檔案
3. 修復 Unicode 符號
4. 修復 underscore
5. 重新編譯 LaTeX
6. 生成浮水印版本
7. 驗證修復效果

**使用方式**:
```bash
# 基本用法
python fix_and_recompile.py <task_id>

# 範例
python fix_and_recompile.py 2025-10-09-1630_speec

# 只修復不編譯
python fix_and_recompile.py <task_id> --skip-compile

# 只編譯不修復（假設已手動修復）
python fix_and_recompile.py <task_id> --skip-fix
```

**輸出範例**:
```
============================================================
Unicode Glitch 修復與重新編譯
============================================================

Task ID: 2025-10-09-1630_speec

[Step 1/6] 偵測 Unicode 符號...
  發現 2334 個 Unicode 符號
  涉及 391 行
✓ 報告已儲存: outputs/.../tmp/unicode_report_before.txt

[Step 2/6] 備份原檔案...
✓ 備份已儲存: outputs/.../survey.tex.backup_20251016_143022

[Step 3/6] 修復 Unicode 符號...
  總行數: 1626
  修改行數: 391
  替換次數: 2334
✓ 所有 Unicode 符號已成功修復!

[Step 4/6] 修復 underscore...
  總行數: 1626
  修改行數: 47
  替換次數: 58
✓ 所有 underscore 已成功修復!

[Step 5/6] 重新編譯 LaTeX...
  - 清除舊的編譯產物...
  - 執行 latexmk (這可能需要幾分鐘)...
✓ PDF 編譯成功!

[Step 6/6] 生成浮水印版本...
✓ 浮水印版本已生成!

============================================================
✓ 完成! 所有問題已修復並重新編譯完成
============================================================

修復後檔案:
  - LaTeX 源碼: outputs/2025-10-09-1630_speec/latex/survey.tex
  - PDF (無浮水印): outputs/2025-10-09-1630_speec/survey.pdf
  - PDF (有浮水印): outputs/2025-10-09-1630_speec/survey_wtmk.pdf

備份檔案:
  - outputs/2025-10-09-1630_speec/latex/survey.tex.backup_20251016_143022

驗證報告:
  - 修復前: outputs/2025-10-09-1630_speec/tmp/unicode_report_before.txt
  - 修復後: outputs/2025-10-09-1630_speec/tmp/unicode_report_after.txt
```

---

### 6. fix_and_recompile.sh

**功能**: 整合所有修復步驟的一鍵腳本（Bash 版本）

**使用方式**:
```bash
# 基本用法
bash fix_and_recompile.sh <task_id>

# 範例
bash fix_and_recompile.sh 2025-10-09-1630_speec
```

**說明**: 功能與 `fix_and_recompile.py` 相同，但使用 Bash 腳本實現。建議優先使用 Python 版本（更好的錯誤處理與進度顯示）。

---

## 🛠️ 修復流程最佳實踐

### 完整修復流程

```bash
# === 階段 1: 自動修復 (可腳本化) ===

# 1. 一鍵執行自動修復
python scripts/spacing_glitch_fix/fix_and_recompile.py <task_id>

# 或分步驟執行:
# 1a. 偵測問題
python scripts/spacing_glitch_fix/detect_unicode_glitches.py \
  outputs/<task_id>/latex/survey.tex

# 1b. 修復 Unicode
python scripts/spacing_glitch_fix/fix_unicode_glitches.py \
  outputs/<task_id>/latex/survey.tex

# 1c. 修復 underscore
python scripts/spacing_glitch_fix/fix_underscores.py \
  outputs/<task_id>/latex/survey.tex

# === 階段 2: 手動修復 (需要人工/AI) ===

# 2. 搜尋並修復數學變數格式錯誤
cd outputs/<task_id>/latex

# 2a. 找出所有包含 underscore 的可疑行
grep -n "[^\\\\]_[a-zA-Z]" survey.tex | less

# 2b. 手動檢查每一行，判斷是否需要修正:
#   - 變數名: N_s → $N_{s}$
#   - 檔案名: tiny_tree_0 → tiny\_tree\_0 (已由腳本處理)
#   - 技術術語: frame_rate_hz → frame\_rate\_hz

# 2c. 搜尋可能缺少 $ 的數學表達式
grep -n "\^{" survey.tex | grep -v "\$.*\^.*\$"

# 3. 修復表格問題 (如果有)
# 3a. 檢查 \cite 前是否有空格
grep -n "\\cite{" benchmark_table.tex | grep -v " \\cite"

# 3b. 批次添加空格
sed -i '' 's/\\cite{/ \\cite{/g' benchmark_table.tex

# === 階段 3: 驗證 ===

# 4. 重新編譯並檢查
cd outputs/<task_id>/latex
latexmk -C && latexmk -pdf -interaction=nonstopmode -f survey.tex

# 5. 檢查編譯日誌中的錯誤
grep -i "error" compile.log

# 6. 提取 PDF 文字驗證 spacing glitch 是否消失
pdftotext ../survey.pdf - | grep -o -E "\w{30,}"

# 如果沒有輸出（或只有 URL/citation），表示修復成功！
```

---

## 📊 常見問題與解決方案

### Q1: 執行 fix_unicode_glitches.py 後還有 spacing glitch

**可能原因**:
1. 還有其他類型的問題（underscore, 數學變數格式）
2. 表格寬度問題導致強制壓縮

**解決方案**:
```bash
# 1. 執行 underscore 修復
python scripts/spacing_glitch_fix/fix_underscores.py outputs/<task_id>/latex/survey.tex

# 2. 手動檢查數學變數
grep -n "_[a-zA-Z]" outputs/<task_id>/latex/survey.tex | less

# 3. 檢查表格
pdftotext outputs/<task_id>/survey.pdf - | grep -E "cite[a-z]{20,}"
```

---

### Q2: 腳本把不該轉義的 underscore 也轉義了

**範例**: `\cite{author_2024}` 被錯誤轉義為 `\cite{author\_2024}`

**原因**: `fix_underscores.py` 的數學模式檢測有限

**解決方案**:
```bash
# 1. 恢復備份
cp outputs/<task_id>/latex/survey.tex.backup_underscore \
   outputs/<task_id>/latex/survey.tex

# 2. 只修復圖表引用（更保守的方式）
sed -i '' 's/\(\\autoref{fig:[^}]*\)_\([^}]*}\)/\1\\_\2/g' survey.tex
sed -i '' 's/\(\\ref{fig:[^}]*\)_\([^}]*}\)/\1\\_\2/g' survey.tex
```

---

### Q3: 編譯時出現 "Missing $ inserted" 錯誤

**原因**: 有些 underscore 在正文中但未轉義，或數學變數格式錯誤

**解決方案**:
```bash
# 1. 查看錯誤行號
grep "Missing \$ inserted" outputs/<task_id>/latex/compile.log

# 2. 檢查該行附近的 underscore 或上標/下標
vim +<line_number> outputs/<task_id>/latex/survey.tex

# 3. 修正格式:
#   - 如果是變數: N_s → $N_{s}$
#   - 如果是檔案名: file_name → file\_name
```

---

### Q4: 表格中的 citation 還是黏在一起

**範例**: PDF 中顯示 `citezeng2024scaling...`

**原因**: LaTeX 表格 `\resizebox` 強制壓縮文字

**解決方案**:
```latex
% 方案 A: 加寬表格
\resizebox{1.2\textwidth}{!}{  % 從 1.0 改成 1.2
  \begin{tabular}{...}
  ...
  \end{tabular}
}

% 方案 B: 改用 longtable 跨頁
\begin{longtable}{p{0.3\textwidth} ...}
...
\end{longtable}

% 方案 C: 縮短 citation key 或使用數字引用
VoxEval~\cite{cui2025} % 而非 \cite{cui2025voxevalbenchmarking...}
```

---

### Q5: 如何恢復到修復前的版本

**解決方案**:
```bash
# 找到備份檔案
ls -lt outputs/<task_id>/latex/survey.tex.backup*

# 選擇要恢復的版本（最新的備份通常是最近一次修復前的）
cp outputs/<task_id>/latex/survey.tex.backup_20251016_HHMMSS \
   outputs/<task_id>/latex/survey.tex

# 重新編譯
cd outputs/<task_id>/latex
latexmk -pdf survey.tex
```

---

## 🔧 進階用法

### 批次處理多個 task

```bash
# 批次修復所有輸出
for task in outputs/*/latex/survey.tex; do
  task_id=$(echo $task | cut -d'/' -f2)
  echo "Processing: $task_id"
  python scripts/spacing_glitch_fix/fix_and_recompile.py $task_id
done
```

---

### 整合到 Pipeline

在 `src/models/generator/latex_generator.py` 的 `compile_single_survey()` 前加入:

```python
from pathlib import Path
import subprocess

def compile_single_survey(self):
    latex_dir = self.output_dir / "latex"
    survey_tex = latex_dir / "survey.tex"
    
    # 自動修復 Unicode glitch
    fix_script = Path("scripts/spacing_glitch_fix/fix_unicode_glitches.py")
    if fix_script.exists():
        logger.info("Auto-fixing Unicode symbols...")
        subprocess.run(
            ["python", str(fix_script), str(survey_tex), "--no-backup"],
            check=True
        )
    
    # 原有編譯流程
    ...
```

---

### 自訂符號對應表

編輯 `fix_unicode_glitches.py` 中的 `UNICODE_TO_LATEX` 字典:

```python
UNICODE_TO_LATEX = {
    # 新增自訂符號
    '∞': r'\infty',
    '∑': r'\sum',
    '∏': r'\prod',
    '√': r'\sqrt',
    # ... 其他符號
}
```

---

## 📚 相關文件

### 問題分析文件
- `docs/temporary_issues/spacing_glitch.md` - 原始問題分析
- `docs/temporary_issues/spacing_glitch_solution.md` - 詳細解決方案
- `docs/temporary_issues/QUICKSTART_fix_unicode.md` - 快速開始指南
- `outputs/<task_id>/SPACING_GLITCH_FIX_REPORT.md` - 修復完成報告（自動生成）

### 源碼相關
- `src/models/generator/content_generator.py` - 內容生成（問題源頭）
- `src/models/generator/latex_generator.py` - LaTeX 編譯流程
- `resources/LLM/prompts/content_generator/*.md` - LLM prompt 模板

---

## 🎯 修復成功的指標

### 1. 偵測報告顯示 0 個問題
```bash
python scripts/spacing_glitch_fix/detect_unicode_glitches.py \
  outputs/<task_id>/latex/survey.tex

# 輸出應該是:
# Total Unicode symbols found: 0
# ✓ No Unicode glitches detected!
```

### 2. PDF 文字提取沒有長串字詞
```bash
pdftotext outputs/<task_id>/survey.pdf - | grep -o -E "\w{30,}"

# 沒有輸出或只有 URL/citation key = 成功
# 有類似 "avoidingadversarialtraining..." = 失敗，還有問題
```

### 3. LaTeX 編譯無錯誤
```bash
grep -i "error" outputs/<task_id>/latex/compile.log

# 沒有 "Missing $" 或 "Unicode character not set up" = 成功
```

### 4. 目視檢查 PDF 關鍵頁面
- 打開 PDF 檢查之前有問題的頁面（如頁 13, 35, 37 等）
- 字詞間距正常，沒有黏在一起的文字
- 數學公式顯示正確

---

## 📝 備註

### 腳本限制
1. **無法處理嵌套數學模式**: 如 `$a_{b_c}$`
2. **無法理解語義**: 無法區分變數名 vs 檔案名 vs 技術術語
3. **簡單的上下文檢測**: 可能誤轉義某些 underscore

### 建議
1. **執行前先預覽**: 使用 `--preview` 檢查變更
2. **保留備份**: 腳本會自動備份，但建議額外手動備份重要檔案
3. **分階段驗證**: 每個步驟後重新編譯檢查
4. **手動檢查關鍵區域**: 數學公式、表格、引用等

### 預防措施
1. **改進 LLM prompt**: 要求直接輸出 LaTeX 命令而非 Unicode
2. **後處理驗證**: 在生成流程中加入自動檢測
3. **編譯前修復**: 整合到 pipeline 自動執行

---

**維護者**: GitHub Copilot (AI Agent)  
**最後更新**: 2025-10-16  
**版本**: 1.0.0
