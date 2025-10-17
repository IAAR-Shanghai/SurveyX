# LaTeX Citation 修復方案完整文檔

**日期**: 2025-10-16  
**問題**: TikZ 圖表中引用被錯誤轉義為 `\\cite{}` 導致 PDF 顯示純文本  
**修復狀態**: ✅ 已修復 (臨時方案)，待修改源碼

---

## 1. 問題根本原因分析

### 1.1 問題位置

**檔案**: `src/modules/latex_handler/latex_figure_builder.py`  
**類別**: `TinyTreeFigureBuilder`  
**方法**: `extract_architecture()` (Line ~590-610)

### 1.2 問題代碼

```python
def extract_architecture(self, paragraph: str):
    trees = self.extract_attri_tree_from_paragraph(paragraph)
    prompt = load_prompt(self.prompt_path, context=paragraph, trees=trees)
    response = self.chat_agent.remote_chat(prompt, model=ADVANCED_CHATAGENT_MODEL)
    response = response.replace("```json", "").replace("```", "")
    try:
        ans = (
            re.search(r"(?<=<answer>)(.*?)(?=</answer>)", response, re.DOTALL)
            .group(0)
            .strip()
            .replace("\\", "\\\\")  # ❌ 問題在這裡！
        )
        # ... 後續處理
```

### 1.3 問題機制

**錯誤流程**:

1. LLM 生成的 JSON 回應包含: `"list_": ["12.5 Hz sweet spot\\cite{zeng2024...}"]`
2. Python 解析 JSON 時,`\\cite` 被解析為單個反斜線: `\cite`
3. **Line 600**: `.replace("\\", "\\\\")` 將所有 `\` 替換為 `\\`
4. 結果: `\cite` → `\\cite`
5. 寫入 `.tex` 檔案時: `{12.5 Hz sweet spot\\cite{...}}`
6. LaTeX 解釋: `\\` = 換行, `cite{...}` = 純文本

**為何會這樣設計？**  
推測原因: 為了處理 LaTeX 特殊字符(如 `%`, `$`, `&` 等)需要轉義,但誤傷了 `\cite{}` 等 LaTeX 指令。

### 1.4 影響範圍

- **檔案數量**: 14 個 `tiny_tree_figure_*.tex`
- **錯誤實例**: 245 個 `\\cite{}`
- **受影響頁數**: PDF 第 75-86 頁
- **相同問題**: `TreeFigureBuilder` 可能也有類似問題

---

## 2. 修改方案

### 方案 A: 精確轉義 (推薦)

**原理**: 只轉義需要轉義的字符,保留 LaTeX 指令

```python
def extract_architecture(self, paragraph: str):
    trees = self.extract_attri_tree_from_paragraph(paragraph)
    prompt = load_prompt(self.prompt_path, context=paragraph, trees=trees)
    response = self.chat_agent.remote_chat(prompt, model=ADVANCED_CHATAGENT_MODEL)
    response = response.replace("```json", "").replace("```", "")
    try:
        ans = (
            re.search(r"(?<=<answer>)(.*?)(?=</answer>)", response, re.DOTALL)
            .group(0)
            .strip()
        )
        # ✅ 新增: 精確轉義,保護 LaTeX 指令
        ans = self._escape_latex_special_chars(ans)
        
        score = (
            re.search(r"(?<=<score>)(.*?)(?=</score>)", response, re.DOTALL)
            .group(0)
            .strip()
        )
        caption = (
            re.search(r"(?<=<caption>)(.*?)(?=</caption>)", response, re.DOTALL)
            .group(0)
            .strip()
        )
        archi = self._wrap_node(json.loads(ans))
    except (json.JSONDecodeError, AttributeError, AssertionError) as e:
        logger.error(str(e) + "\n" + response)
        raise ValueError()
    
    return archi, score, caption

def _escape_latex_special_chars(self, text: str) -> str:
    """
    轉義 LaTeX 特殊字符,但保留 LaTeX 指令
    
    需要轉義的字符: # $ % & _ { } ~ ^
    不應轉義的模式: \cite{...}, \ref{...}, \label{...}, \autoref{...} 等
    """
    # 先標記 LaTeX 指令,避免被轉義
    latex_commands = re.findall(r'\\[a-zA-Z]+\{[^}]*\}', text)
    placeholders = {}
    for i, cmd in enumerate(latex_commands):
        placeholder = f"__LATEX_CMD_{i}__"
        placeholders[placeholder] = cmd
        text = text.replace(cmd, placeholder, 1)
    
    # 轉義特殊字符
    special_chars = {
        '#': r'\#',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\~{}',
        '^': r'\^{}',
    }
    for char, escaped in special_chars.items():
        text = text.replace(char, escaped)
    
    # 恢復 LaTeX 指令
    for placeholder, cmd in placeholders.items():
        text = text.replace(placeholder, cmd)
    
    return text
```

**優點**:
- ✅ 精確控制,不會誤傷 LaTeX 指令
- ✅ 支持所有 LaTeX 指令 (`\cite`, `\ref`, `\label` 等)
- ✅ 維護性高,易於理解

**缺點**:
- ❌ 代碼較複雜
- ❌ 需要測試多種情況

### 方案 B: 移除轉義 (激進)

**原理**: 完全移除 `.replace("\\", "\\\\")`，依賴 JSON 解析正確處理

```python
def extract_architecture(self, paragraph: str):
    # ... 前面相同
    try:
        ans = (
            re.search(r"(?<=<answer>)(.*?)(?=</answer>)", response, re.DOTALL)
            .group(0)
            .strip()
            # ✅ 直接移除這行
            # .replace("\\", "\\\\")  # 移除
        )
        # ... 後續相同
```

**優點**:
- ✅ 最簡單,改動最小
- ✅ 依賴 Python JSON parser 正確處理轉義

**缺點**:
- ❌ 如果 LLM 回應包含未轉義的特殊字符,可能導致 LaTeX 編譯錯誤
- ❌ 需要確保 LLM prompt 明確要求正確轉義

### 方案 C: 後處理修正 (保守)

**原理**: 保留現有邏輯,在生成 `.tex` 檔案後修正錯誤

```python
def gen_latex_code(
    self, node: TreeFigureBuilder.Node, caption: str, file_name: str, label: str
):
    self.define_color()
    tree_node_tex = self.gen_node_latex(node)

    tree_tex = load_file_as_string(self.init_tree_tex_path)
    tree_tex = tree_tex.replace("<define_color>", self.color_tex)
    tree_tex = tree_tex.replace("<tree_code>", tree_node_tex)
    tree_tex = tree_tex.replace("<caption>", caption)
    tree_tex = tree_tex.replace("<label>", label)
    
    # ✅ 新增: 修正錯誤的雙反斜線引用
    tree_tex = re.sub(r'\\\\(cite|ref|label|autoref)\{', r'\\\1{', tree_tex)
    
    save_result(tree_tex, self.figure_dir / file_name)
```

**優點**:
- ✅ 最安全,不改動現有邏輯
- ✅ 只修正已知問題
- ✅ 易於測試

**缺點**:
- ❌ 治標不治本
- ❌ 如果有其他 LaTeX 指令也需要類似處理

---

## 3. 推薦方案: A + C 混合

### 3.1 短期修復 (立即實施)

**在 `gen_latex_code()` 中添加後處理** (方案 C):

```python
# 所有 *FigureBuilder 類別的 gen_latex_code 方法
def gen_latex_code(self, node, caption: str, file_name: str, label: str):
    # ... 原有代碼 ...
    
    # 修正錯誤的雙反斜線 LaTeX 指令
    tree_tex = re.sub(r'\\\\(cite|ref|label|autoref|textbf|textit|section|subsection)\{', 
                      r'\\\1{', tree_tex)
    
    save_result(tree_tex, self.figure_dir / file_name)
```

**影響**: 3 個類別需要修改
- `TinyTreeFigureBuilder.gen_latex_code()` (Line ~616)
- `TreeFigureBuilder.gen_latex_code()` (Line ~424)
- `MindMapTreeFigureBuilder.gen_latex_code()` (Line ~848)

### 3.2 長期修復 (下個版本)

**替換 `.replace("\\", "\\\\")` 為精確轉義** (方案 A):

1. 在 `TinyTreeFigureBuilder` 添加 `_escape_latex_special_chars()` 方法
2. 在 `extract_architecture()` 中使用該方法
3. 添加單元測試確保不影響現有功能

---

## 4. 已執行的修復操作記錄

### 4.1 survey.tex 修改

**檔案**: `outputs/2025-10-09-1630_speec/latex/survey.tex`

#### 修改 1: 添加 PassOptionsToPackage (Line 1-6)

**原始版本** (`survey.tex.ORIGINAL_BROKEN`):
```latex
% from: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh
% \documentclass[final]{article}
\documentclass{article}

\usepackage[preprint]{neurips_2024}
```

**修改後**:
```latex
% from: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh

% === FIX: Prevent package option clashes ===
\PassOptionsToPackage{dvipsnames,usenames}{xcolor}
\PassOptionsToPackage{numbers}{natbib}
% ===========================================

% \documentclass[final]{article}
\documentclass{article}

\usepackage[preprint]{neurips_2024}
```

**命令**: 手動修改

---

#### 修改 2: 添加顏色定義 (Line 30-42)

**位置**: 在 `\usepackage{xcolor}` 之後

**新增內容**:
```latex
% === FIX: Define missing colors for TikZ figures ===
\definecolor{c12}{RGB}{100,149,237}  % Cornflower Blue
\definecolor{c13}{RGB}{144,238,144}  % Light Green  
\definecolor{c14}{RGB}{255,182,193}  % Light Pink
\definecolor{c15}{RGB}{255,218,185}  % Peach Puff
\definecolor{c16}{RGB}{221,160,221}  % Plum
% ====================================================
```

**命令**: `replace_string_in_file` tool

---

#### 修改 3: 移除重複的 bibliographystyle (Line 35)

**原始**:
```latex
\bibliographystyle{unsrt}
```

**修改後**:
```latex
% \bibliographystyle{unsrt}  % REMOVED: Duplicate - will use unsrtnat at end
```

**命令**: `replace_string_in_file` tool

---

#### 修改 4: 修復第 58 頁 spacing glitch (Line 1454)

**原始**: 密集的段落無換行

**修改後**: 添加段落分隔

**命令**: `replace_string_in_file` tool  
**備份**: `survey.tex.INTERMEDIATE_page58fixed`

---

#### 修改 5: 修正 bibliography 順序 (Line 1632-1633)

**原始**:
```latex
\bibliography{references}
\bibliographystyle{unsrtnat}
```

**修改後**:
```latex
\bibliographystyle{unsrtnat}
\bibliography{references}
```

**命令**: `replace_string_in_file` tool

---

### 4.2 TikZ 圖表批量修改

**目錄**: `outputs/2025-10-09-1630_speec/latex/figs/`

#### 批量修正 `\\cite{}` → `\cite{}`

**影響檔案**: 所有 `*.tex` (共 17 個圖表檔案)

**命令**:
```bash
cd outputs/2025-10-09-1630_speec/latex/figs
for f in *.tex; do 
  sed -i '.bak' 's/\\\\cite{/\\cite{/g' "$f"
done
```

**修改前** (`tiny_tree_figure_0.tex.ORIGINAL_BROKEN`):
```latex
\node[nodeL, on chain, fill=color_list!15, xshift=6mm, yshift=-5mm] (l420) {12.5 Hz sweet spot\\cite{zeng2024scalingspeechtextpretrainingsyntheticint}};
```

**修改後** (`tiny_tree_figure_0.tex`):
```latex
\node[nodeL, on chain, fill=color_list!15, xshift=6mm, yshift=-5mm] (l420) {12.5 Hz sweet spot\cite{zeng2024scalingspeechtextpretrainingsyntheticint}};
```

**執行日期**: 2025-10-16 14:07

**備份**: 每個檔案產生 `.bak` 副本 (已清理)

**驗證**:
```bash
# 修改前
grep -r "\\\\cite" figs/*.tex | wc -l
# Output: 245

# 修改後
grep -r "\\\\cite" figs/*.tex | wc -l
# Output: 0
```

---

### 4.3 其他修改 (早期嘗試)

#### benchmark_table.tex 修改

**問題**: Citation key 包含空格和多餘的 `title=`

**命令**:
```bash
sed -i '.backup' 's/entry2025indicsuperbspeechprocessinguniversalperf title=/entry2025indicsuperbspeechprocessinguniversalperf/g' benchmark_table.tex
```

**備份**: `benchmark_table.tex.backup`

**狀態**: 已修復但非主要問題

---

## 5. 完整修改腳本 (可重現)

```bash
#!/bin/bash
# LaTeX Citation Fix - Complete Reproduction Script
# Date: 2025-10-16
# Description: 從有問題的備份恢復並應用所有修復

set -e  # Exit on error

LATEX_DIR="outputs/2025-10-09-1630_speec/latex"
cd "$LATEX_DIR"

echo "=== Step 1: 恢復原始有問題的檔案 (用於測試) ==="
# 注意: 這會覆蓋現有檔案,請先備份！
cp survey.tex.backup_20251016_012629 survey_original.tex
cp figs/tiny_tree_figure_0.tex.backup_citation figs/tiny_tree_figure_0_original.tex

echo "=== Step 2: 修改 survey.tex ==="

# 2.1: 添加 PassOptionsToPackage
sed -i '.step2_1' '1i\
% === FIX: Prevent package option clashes ===\
\\PassOptionsToPackage{dvipsnames,usenames}{xcolor}\
\\PassOptionsToPackage{numbers}{natbib}\
% ===========================================\
' survey.tex

# 2.2: 添加顏色定義 (需要找到正確位置,這裡簡化)
# 實際使用時需要用 replace_string_in_file

# 2.3: 註解掉重複的 bibliographystyle
sed -i '.step2_3' 's/^\\bibliographystyle{unsrt}/% \\bibliographystyle{unsrt}  % REMOVED: Duplicate/g' survey.tex

# 2.4: 修正 bibliography 順序 (需要精確定位)
# 實際使用時需要用 replace_string_in_file

echo "=== Step 3: 批量修正圖表檔案 ==="
cd figs
for f in *.tex; do 
  echo "Processing $f..."
  sed -i '.fix_citation' 's/\\\\cite{/\\cite{/g' "$f"
  sed -i '.fix_ref' 's/\\\\ref{/\\ref{/g' "$f"
  sed -i '.fix_label' 's/\\\\label{/\\label{/g' "$f"
done
cd ..

echo "=== Step 4: 清理並重新編譯 ==="
latexmk -C
latexmk -pdf -interaction=nonstopmode -f survey.tex

echo "=== Step 5: 驗證 ==="
pdftotext -f 75 -l 75 survey.pdf - | grep -o "cite[a-z0-9]\{20,\}" || echo "✅ 沒有找到錯誤的 citation 顯示"
pdftotext -f 75 -l 75 survey.pdf - | grep -o "\[[0-9]\+\]" | head -5 && echo "✅ 找到正確的引用編號"

echo "=== 完成 ==="
```

**注意**: 此腳本僅為示意,實際執行需要更精確的 sed 模式匹配或使用 Python 腳本。

---

## 6. 測試驗證清單

### 6.1 修改前檢查

- [ ] 備份所有檔案
- [ ] 記錄 Git commit hash
- [ ] 確認當前 PDF 編譯狀態

### 6.2 修改後驗證

#### LaTeX 編譯測試
```bash
cd outputs/2025-10-09-1630_speec/latex

# 清理編譯產物
latexmk -C

# 完整編譯
pdflatex -interaction=nonstopmode survey.tex
bibtex survey
pdflatex -interaction=nonstopmode survey.tex
pdflatex -interaction=nonstopmode survey.tex

# 檢查錯誤
echo "=== Checking compilation errors ==="
grep -i "error" survey.log | head -10
echo "=== Checking undefined references ==="
grep -i "undefined" survey.log | head -10
```

#### PDF 內容驗證
```bash
# 檢查第 75-86 頁沒有純文本 citation
pdftotext -f 75 -l 86 survey.pdf - | grep -o "cite[a-z0-9]\{20,\}" | wc -l
# Expected: 0

# 檢查引用編號正確顯示
pdftotext -f 75 -l 86 survey.pdf - | grep -o "\[[0-9]\+\]" | wc -l
# Expected: > 100
```

#### 源碼驗證
```bash
# 檢查沒有雙反斜線引用
grep -r "\\\\cite{" . --include="*.tex" | wc -l
# Expected: 0

# 檢查有正確的單反斜線引用
grep -r "\\cite{" . --include="*.tex" | wc -l
# Expected: > 500
```

### 6.3 回歸測試

- [ ] 其他章節的引用是否正常
- [ ] 參考文獻列表是否完整
- [ ] 圖表編號是否正確
- [ ] 交叉引用 (`\ref`, `\autoref`) 是否正常

---

## 7. 相關檔案清單

### 7.1 核心原始碼
- `src/modules/latex_handler/latex_figure_builder.py` (933 lines)
  - `TreeFigureBuilder` class (Line ~228-467)
  - `TinyTreeFigureBuilder` class (Line ~469-730)
  - `MindMapTreeFigureBuilder` class (Line ~732-858)

### 7.2 修改的檔案
- `outputs/2025-10-09-1630_speec/latex/survey.tex` (1642 lines)
- `outputs/2025-10-09-1630_speec/latex/figs/*.tex` (17 files)

### 7.3 備份檔案 (按時間順序)

#### survey.tex 備份
1. `survey.tex.backup_20251016_012629` (最早,修改前原始檔案) ⭐
2. `survey.tex.backup_20251016_010602` (早期版本)
3. `survey.tex.backup_underscore` (嘗試修復 underscore)
4. `survey.tex.backup` (一般備份)
5. `survey.tex.backup_page58_fix_20251016_122422` (修復第 58 頁後) ⭐

#### 圖表備份
- `figs/tiny_tree_figure_*.tex.ORIGINAL_BROKEN` (修改前,含 `\\cite`) ⭐
- `figs/tree_figure_*.tex.bak` (已清理)
- `figs/structure_fig.tex.bak` (已清理)

### 7.4 文檔
- `docs/temporary_issues/bibtex_compilation_issue.md` (問題追蹤)
- `docs/temporary_issues/spacing_glitch.md` (Spacing 問題)
- `docs/temporary_issues/latex_citation_fix_plan.md` (本文檔) ⭐

---

## 8. 未來改進建議

### 8.1 預防機制

1. **添加 CI/CD 檢查**:
   ```bash
   # 在 generate 階段自動檢查
   grep -r "\\\\cite{" outputs/*/latex/figs/*.tex && exit 1
   ```

2. **添加單元測試**:
   ```python
   def test_latex_command_not_double_escaped():
       builder = TinyTreeFigureBuilder("test_task")
       node = builder._wrap_node({
           "title": "Test",
           "list_": ["Item with \\cite{test2024}"]
       })
       tex = builder._gen_leaf_node_latex(node)
       assert "\\\\cite" not in tex
       assert "\\cite{test2024}" in tex
   ```

3. **添加 LLM prompt 約束**:
   在 `resources/LLM/prompts/latex_figure_builder/extract_tiny_tree_architect.md` 中明確要求:
   ```markdown
   IMPORTANT: When including LaTeX commands in the output:
   - Use single backslash: \cite{key}, NOT \\cite{key}
   - Use single backslash: \ref{key}, NOT \\ref{key}
   ```

### 8.2 工具改進

1. **創建 LaTeX 驗證腳本**:
   ```bash
   scripts/validate_latex.sh outputs/<task_id>/latex/
   ```

2. **創建自動修復工具**:
   ```bash
   scripts/fix_latex_escaping.py --dir outputs/<task_id>/latex/figs/
   ```

### 8.3 文檔改進

1. 在 `pipeline&modules.md` 中記錄此問題
2. 在 `README.md` 中添加常見問題章節
3. 創建開發者指南說明 LaTeX 轉義規則

---

## 附錄 A: 所有修改命令摘要

```bash
# === survey.tex 修改 ===

# 1. 添加 PassOptionsToPackage (手動修改 Line 1-6)
# 2. 添加顏色定義 (手動修改 Line 30-42)
# 3. 註解重複的 bibliographystyle (手動修改 Line 35)
# 4. 修復第 58 頁 spacing (手動修改 Line 1454)
# 5. 修正 bibliography 順序 (手動修改 Line 1632-1633)

# === 圖表批量修改 ===

cd outputs/2025-10-09-1630_speec/latex/figs
for f in *.tex; do 
  sed -i '.bak' 's/\\\\cite{/\\cite{/g' "$f"
done

# === 驗證 ===

# 檢查修復效果
grep -r "\\\\cite" figs/*.tex | wc -l  # Expected: 0

# 重新編譯
cd ..
latexmk -pdf -f survey.tex

# 驗證 PDF
pdftotext -f 75 -l 75 survey.pdf - | head -30
```

---

## 附錄 B: 備份檔案價值評估

### 必須保留 (用於 Sandbox)

1. ✅ `survey.tex.ORIGINAL_BROKEN` - 最原始版本,未修改
2. ✅ `figs/tiny_tree_figure_0.tex.ORIGINAL_BROKEN` - 含錯誤的 `\\cite`
3. ✅ `survey.tex.INTERMEDIATE_page58fixed` - 中間狀態,已修復 page58

### 已刪除

1. ✅ `survey.tex.backup_20251016_010602` - 早期測試版本
2. ✅ `survey.tex.backup_underscore` - 特定問題的嘗試
3. ✅ `survey.tex.backup` - 非特定時間點的備份
4. ✅ `benchmark_table.tex.backup` - 非關鍵問題
5. ✅ `benchmark_table.tex.backup_resize` - 表格調整相關
6. ✅ `figs/*.tex.bak` - sed 自動生成,已清理
7. ✅ `figs/tree_figure_*.tex.bak` - 已清理

---

**維護者**: GitHub Copilot (AI Agent)  
**最後更新**: 2025-10-16 14:30
