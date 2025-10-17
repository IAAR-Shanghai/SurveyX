# Unicode Glitch 修復快速指南

> **⚠️ 重要**: 完整文檔請參閱 `scripts/spacing_glitch_fix/README.md`  
> 本文件僅提供最快速的使用方式

## 🚀 最簡單的方式 (一鍵執行)

```bash
# 進入專案目錄
cd /Users/xjp/Desktop/Survey-with-LLMs/Survey-for-survey-review-with-LLMs/SurveyX

# 啟動環境
conda activate surveyx

# 執行一鍵修復腳本 (推薦使用 Python 版本)
python scripts/spacing_glitch_fix/fix_and_recompile.py 2025-10-09-1630_speec

# 或使用 Bash 版本
bash scripts/spacing_glitch_fix/fix_and_recompile.sh 2025-10-09-1630_speec
```

## 📋 腳本會做什麼?

1. **偵測**: 掃描 `outputs/2025-10-09-1630_speec/latex/survey.tex` 中的 Unicode 符號
2. **備份**: 自動備份原始檔案 (加上時間戳記)
3. **修復**: 將所有 Unicode 數學符號替換為 LaTeX 巨集
4. **編譯**: 重新編譯 LaTeX 生成新的 PDF
5. **浮水印**: 生成帶浮水印的版本

## 📁 輸出檔案位置

執行完成後,你會得到:

```
outputs/2025-10-09-1630_speec/
├── latex/
│   ├── survey.tex                          # 修復後的 LaTeX 源碼
│   ├── survey.tex.backup_20251016_HHMMSS  # 原始備份
│   ├── compile.log                         # 編譯日誌
│   └── compile_fixed.log                   # 新的編譯日誌 (bash 版本)
├── tmp/
│   ├── unicode_report_before.txt           # 修復前的偵測報告
│   └── unicode_report_after.txt            # 修復後的驗證報告
├── survey.pdf                              # 新生成的 PDF (無浮水印)
└── survey_wtmk.pdf                         # 新生成的 PDF (有浮水印)
```

## ✅ 驗證修復效果

執行完成後,用以下指令檢查 spacing glitch 是否消失:

```bash
# 提取 PDF 文字並搜尋之前有問題的段落
pdftotext outputs/2025-10-09-1630_speec/survey.pdf - | \
  grep -A 2 "DiffSoundStream emits semantic"

# 應該看到:
# DiffSoundStream emits semantic and acoustic tokens at 12.5 Hz with N_s ∈ {0,1}, N_a ∈ [1,8]; a common point uses 1 semantic + ...
#                                                                            ^^^^^ ^^^^^ ^^^^^ 空格都正常了!
```

## 🔍 分步驟執行 (進階用法)

如果你想逐步檢查每個步驟:

### 1. 只偵測問題 (不修改)
```bash
python scripts/spacing_glitch_fix/detect_unicode_glitches.py \
  outputs/2025-10-09-1630_speec/latex/survey.tex
```

### 2. 預覽修復 (不實際修改檔案)
```bash
python scripts/spacing_glitch_fix/fix_unicode_glitches.py \
  outputs/2025-10-09-1630_speec/latex/survey.tex --preview
```

### 3. 執行修復 (會自動備份)
```bash
python scripts/spacing_glitch_fix/fix_unicode_glitches.py \
  outputs/2025-10-09-1630_speec/latex/survey.tex
```

### 4. 手動重新編譯
```bash
python -c "
from src.models.generator import LatexGenerator
latex_gen = LatexGenerator(task_id='2025-10-09-1630_speec')
latex_gen.compile_single_survey()
"
```

## 🆘 常見問題

### Q: 如果編譯失敗怎麼辦?
A: 檢查 `outputs/2025-10-09-1630_speec/latex/compile.log` 尋找錯誤訊息。
   如果是其他 LaTeX 錯誤 (非 Unicode 問題),可能需要手動修正。

### Q: 可以恢復原始檔案嗎?
A: 可以!備份檔案在 `outputs/2025-10-09-1630_speec/latex/survey.tex.backup_*`

```bash
# 恢復原始檔案 (找到最新的備份)
cp outputs/2025-10-09-1630_speec/latex/survey.tex.backup_* \
   outputs/2025-10-09-1630_speec/latex/survey.tex
```

### Q: 修復後的 PDF 還是有問題?
A: 檢查 `tmp/unicode_report_after.txt`,確認所有 Unicode 符號都已修復 (應該顯示 0 個)。
   如果還有問題,可能是其他原因造成,請檢查 compile.log。

### Q: 可以用在其他 task_id 嗎?
A: 可以!只需替換 task_id 即可:
```bash
python scripts/spacing_glitch_fix/fix_and_recompile.py <your_task_id>
```

## 📚 更多資訊

**完整文檔**: `scripts/spacing_glitch_fix/README.md`  
**問題分析**: `docs/temporary_issues/spacing_glitch.md`  
**解決方案**: `docs/temporary_issues/spacing_glitch_solution.md`

## 📊 修復統計範例

執行後你應該會看到類似的輸出:

```
============================================================
Unicode Glitch 修復與重新編譯
============================================================

Task ID: 2025-10-09-1630_speec

[Step 1/4] 偵測 Unicode 符號...
  發現 506 個 Unicode 符號
  涉及 145 行

[Step 2/4] 備份原檔案...
✓ 備份已儲存: outputs/.../survey.tex.backup_20251016_143022

[Step 3/4] 修復 Unicode 符號...
  總行數: 1626
  修改行數: 145
  替換次數: 506
✓ 所有 Unicode 符號已成功修復!

[Step 4/4] 重新編譯 LaTeX...
  - 執行 latexmk (這可能需要幾分鐘)...
✓ PDF 編譯成功!
✓ 浮水印版本已生成!

============================================================
✓ 完成!
============================================================
```

## 🎯 預期效果

**修復前** (spacing glitch):
```
... N_s{0,1}, N_a[1,8]; acommonpointuses1semantic + ...
    ^^^^^^^^空格消失^^^^^^^^^^^^^^^^^^^^^^^^空格全部消失^^^^^^^^
```

**修復後** (正常):
```
... N_s ∈ {0,1}, N_a ∈ [1,8]; a common point uses 1 semantic + ...
    ^^^正常空格^^^   ^^^正常空格^^^   ^^^^所有空格都正常了^^^^
```
