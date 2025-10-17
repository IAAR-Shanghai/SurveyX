# LaTeX Citation Fix - QUICKSTART

> **一頁速查**: 最常用的指令與流程

---

## 🎯 我想...

### ✅ 修復一個 LaTeX 目錄 (Citations + Figures)

```bash
# 一鍵修復 citations (推薦)
python scripts/fix_latex_issues.py outputs/YOUR_TASK_ID/latex

# 一鍵修復 figure placement (如果 figures 都跑到最後)
python scripts/fix_figure_placement.py outputs/YOUR_TASK_ID/latex

# 先預覽變更 (不實際修改)
python scripts/fix_latex_issues.py outputs/YOUR_TASK_ID/latex --dry-run
python scripts/fix_figure_placement.py outputs/YOUR_TASK_ID/latex --dry-run
```

**範例**:
```bash
# 修復 citations 問題
python scripts/fix_latex_issues.py outputs/2025-10-09-1630_speec/latex

# 修復 figure placement 問題
python scripts/fix_figure_placement.py outputs/2025-10-09-1630_speec/latex
```

---

### ✅ 驗證是否修復成功

```bash
cd sandbox/latex_citation_fix
python tools/verify.py ../../outputs/YOUR_TASK_ID/latex
```

---

### ✅ 設置練習環境

```bash
# 快速設置
cd sandbox/latex_citation_fix
cp -r ../../outputs/2025-10-09-1630_speec/latex/* broken/
python tools/verify.py broken/  # 應該顯示多個錯誤

# 練習修復
cp -r broken/* agent_workspace/
python ../../scripts/fix_latex_issues.py agent_workspace/
python tools/verify.py agent_workspace/  # 應該全部通過

# 比較差異
./tools/compare.sh

# 重置環境
./tools/reset.sh
```

---

### ✅ 編譯 LaTeX 生成 PDF

```bash
cd outputs/YOUR_TASK_ID/latex

# 清理舊檔案
rm -f *.aux *.bbl *.blg *.log *.out

# 完整編譯流程
pdflatex survey.tex
bibtex survey
pdflatex survey.tex
pdflatex survey.tex

# 開啟 PDF
open survey.pdf  # macOS
```

---

## 📋 檢查清單

修復 LaTeX 需要處理:

- [ ] ✅ `\PassOptionsToPackage` for xcolor and natbib
- [ ] ✅ Color definitions (c12-c16)
- [ ] ✅ Remove duplicate `\bibliographystyle`
- [ ] ✅ Fix bibliography order (style → bibliography)
- [ ] ✅ Fix double-escaped citations in `figs/*.tex` (`\\cite` → `\cite`)

---

## 🔍 常用檢查指令

```bash
# 檢查是否還有 double-escaped citations
grep -r '\\\\cite' outputs/YOUR_TASK_ID/latex/figs/

# 檢查 PassOptionsToPackage
grep 'PassOptionsToPackage' outputs/YOUR_TASK_ID/latex/survey.tex

# 檢查顏色定義
grep 'definecolor{c1[2-6]}' outputs/YOUR_TASK_ID/latex/survey.tex

# 列出所有備份檔案
find outputs/YOUR_TASK_ID/latex -name "*.backup_*"
```

---

## 📚 完整文件

- **完整指南**: `docs/temporary_issues/LaTeX_Fix_Complete_Guide.md`
- **Sandbox 說明**: `sandbox/latex_citation_fix/Sandbox_Setup_Guide.md`
- **修復腳本**: `scripts/fix_latex_issues.py`

---

## 🆘 快速問題排除

### PDF 無法生成?

```bash
# 查看錯誤訊息
cd outputs/YOUR_TASK_ID/latex
pdflatex survey.tex 2>&1 | grep -i error
```

### 引用顯示為純文字?

```bash
# 檢查是否有 double-escaped
grep '\\\\cite' outputs/YOUR_TASK_ID/latex/figs/*.tex

# 如果有,執行修復
python scripts/fix_latex_issues.py outputs/YOUR_TASK_ID/latex
```

### 想回到原始狀態?

```bash
# 找到最早的備份
ls -lt outputs/YOUR_TASK_ID/latex/*.backup_* | tail -1

# 或使用 .ORIGINAL_BROKEN 備份
cp outputs/YOUR_TASK_ID/latex/survey.tex.ORIGINAL_BROKEN \
   outputs/YOUR_TASK_ID/latex/survey.tex
```

---

**更新日期**: 2025-10-16
