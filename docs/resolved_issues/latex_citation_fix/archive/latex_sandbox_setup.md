# LaTeX Citation Fix Sandbox 設置指南

**目的**: 創建一個隔離環境,讓 LLM Agent 練習修復 LaTeX citation 轉義問題  
**日期**: 2025-10-16

---

## 1. Sandbox 目錄結構建議

### 方案 A: 放在 tests/ (推薦)

```
SurveyX/
├── tests/
│   ├── fixtures/
│   │   └── latex_citation_bug/           # ⭐ 新增
│   │       ├── README.md                  # 說明此測試場景
│   │       ├── survey_broken.tex          # 有問題的主檔案
│   │       ├── references.bib             # 參考文獻資料庫
│   │       ├── neurips_2024.sty           # 必要的樣式檔
│   │       ├── figs/
│   │       │   ├── tiny_tree_figure_0_broken.tex  # 含 \\cite{}
│   │       │   ├── tiny_tree_figure_1_broken.tex
│   │       │   └── structure_fig.tex
│   │       ├── expected/
│   │       │   ├── survey_fixed.tex       # 正確的結果
│   │       │   └── figs/
│   │       │       ├── tiny_tree_figure_0_fixed.tex
│   │       │       └── tiny_tree_figure_1_fixed.tex
│   │       └── scripts/
│   │           ├── verify_fix.sh          # 驗證腳本
│   │           └── run_test.py            # Python 測試
│   └── test_latex_citation_fix.py         # 測試主檔案
```

**優點**:
- ✅ 符合 Python 專案慣例
- ✅ 與現有測試框架整合
- ✅ 易於 CI/CD 自動化
- ✅ 明確標示為測試資料

**缺點**:
- ❌ 可能與單元測試混淆(這是整合測試)

---

### 方案 B: 放在 examples/

```
SurveyX/
├── examples/
│   ├── latex_debugging/                   # ⭐ 新增
│   │   ├── README.md
│   │   ├── citation_fix_challenge/
│   │   │   ├── problem/
│   │   │   │   ├── survey.tex
│   │   │   │   ├── figs/
│   │   │   │   └── references.bib
│   │   │   ├── solution/
│   │   │   │   ├── survey.tex
│   │   │   │   └── figs/
│   │   │   └── hints/
│   │   │       └── debugging_steps.md
│   │   └── other_latex_issues/
│   └── Computation_and_Language/
```

**優點**:
- ✅ 作為教學範例,文檔性強
- ✅ 可以包含多個不同的 LaTeX 問題案例
- ✅ 獨立於測試框架,更靈活

**缺點**:
- ❌ 不易自動化測試
- ❌ 可能被誤認為是使用範例

---

### 方案 C: 放在新的 sandbox/ (最靈活)

```
SurveyX/
├── sandbox/                               # ⭐ 新增
│   ├── README.md                          # 說明 sandbox 用途
│   ├── latex_citation_fix/
│   │   ├── README.md                      # 問題描述與學習目標
│   │   ├── backup/
│   │   │   ├── survey_original.tex       # 最原始版本
│   │   │   ├── figs_original/            # 原始圖表
│   │   │   └── metadata.json             # 記錄檔案來源與時間戳
│   │   ├── broken/                        # 當前有問題的版本
│   │   │   ├── survey.tex
│   │   │   ├── figs/
│   │   │   └── references.bib
│   │   ├── fixed/                         # 修復後的版本 (參考答案)
│   │   │   ├── survey.tex
│   │   │   └── figs/
│   │   ├── agent_workspace/               # Agent 工作區
│   │   │   └── .gitignore                # 忽略 agent 產生的檔案
│   │   └── tools/
│   │       ├── verify.py                  # 驗證修復是否正確
│   │       ├── reset.sh                   # 重置到初始狀態
│   │       └── compare.sh                 # 比較修改前後差異
│   └── other_challenges/                  # 未來可擴展其他練習
```

**優點**:
- ✅ 最大靈活性,專門用於 agent 練習
- ✅ 可以包含多個學習場景
- ✅ 不影響現有測試與範例結構
- ✅ 可以記錄 agent 的修改歷史

**缺點**:
- ❌ 新增頂層目錄,需要更新文檔

---

## 2. 推薦方案: 方案 C (sandbox/)

### 2.1 為什麼選擇 sandbox/

1. **明確的用途隔離**: 
   - `tests/` 用於自動化測試
   - `examples/` 用於使用範例
   - `sandbox/` 用於 agent 練習與實驗

2. **可擴展性**:
   - 未來可添加其他類型的練習場景
   - 可記錄不同 agent 的修復策略
   - 可作為 agent 能力評估的 benchmark

3. **安全性**:
   - 完全隔離,不影響生產代碼
   - 可以隨時重置
   - Agent 錯誤不會破壞其他部分

---

## 3. 詳細設置步驟

### 3.1 創建目錄結構

```bash
#!/bin/bash
# 在 SurveyX 根目錄執行

# 創建主結構
mkdir -p sandbox/latex_citation_fix/{backup,broken,fixed,agent_workspace,tools}
mkdir -p sandbox/latex_citation_fix/broken/figs
mkdir -p sandbox/latex_citation_fix/fixed/figs

# 創建 .gitignore for agent_workspace
cat > sandbox/latex_citation_fix/agent_workspace/.gitignore << 'EOF'
# Agent 工作區 - 忽略所有生成的檔案
*
!.gitignore
EOF

# 添加到根目錄 .gitignore
echo "" >> .gitignore
echo "# Sandbox agent workspace" >> .gitignore
echo "sandbox/*/agent_workspace/*" >> .gitignore
echo "!sandbox/*/agent_workspace/.gitignore" >> .gitignore
```

### 3.2 準備檔案

```bash
#!/bin/bash
SANDBOX_DIR="sandbox/latex_citation_fix"
SOURCE_DIR="outputs/2025-10-09-1630_speec/latex"

# === 1. 複製原始有問題的檔案到 backup/ ===
echo "=== Preparing backup files ==="

cp "$SOURCE_DIR/survey.tex.ORIGINAL_BROKEN" \
   "$SANDBOX_DIR/backup/survey_original.tex"

mkdir -p "$SANDBOX_DIR/backup/figs_original"
cp "$SOURCE_DIR/figs/tiny_tree_figure_0.tex.ORIGINAL_BROKEN" \
   "$SANDBOX_DIR/backup/figs_original/tiny_tree_figure_0.tex"
cp "$SOURCE_DIR/figs/tiny_tree_figure_1.tex.ORIGINAL_BROKEN" \
   "$SANDBOX_DIR/backup/figs_original/tiny_tree_figure_1.tex"

# 複製必要的樣式檔與資料庫
cp "$SOURCE_DIR/neurips_2024.sty" "$SANDBOX_DIR/backup/"
cp "$SOURCE_DIR/references.bib" "$SANDBOX_DIR/backup/"

# 記錄 metadata
cat > "$SANDBOX_DIR/backup/metadata.json" << EOF
{
  "source": "outputs/2025-10-09-1630_speec/latex",
  "original_date": "2025-10-16 01:26:29",
  "issues": [
    "Missing PassOptionsToPackage declarations",
    "Missing color definitions (c12-c16)",
    "Duplicate bibliographystyle command",
    "Page 58 spacing glitch",
    "Wrong bibliography command order",
    "Double-escaped citations in TikZ figures (\\\\cite)"
  ],
  "files_with_citation_bug": [
    "figs/tiny_tree_figure_0.tex",
    "figs/tiny_tree_figure_1.tex",
    "... (total 14 files)"
  ]
}
EOF

# === 2. 複製到 broken/ (agent 的起點) ===
echo "=== Preparing broken version for agent ==="

cp "$SANDBOX_DIR/backup/survey_original.tex" \
   "$SANDBOX_DIR/broken/survey.tex"

mkdir -p "$SANDBOX_DIR/broken/figs"
cp "$SANDBOX_DIR/backup/figs_original/tiny_tree_figure_0.tex" \
   "$SANDBOX_DIR/broken/figs/"
cp "$SANDBOX_DIR/backup/figs_original/tiny_tree_figure_1.tex" \
   "$SANDBOX_DIR/broken/figs/"

cp "$SANDBOX_DIR/backup/neurips_2024.sty" "$SANDBOX_DIR/broken/"
cp "$SANDBOX_DIR/backup/references.bib" "$SANDBOX_DIR/broken/"

# === 3. 複製正確版本到 fixed/ (參考答案) ===
echo "=== Preparing fixed version (reference) ==="

cp "$SOURCE_DIR/survey.tex" "$SANDBOX_DIR/fixed/survey.tex"

mkdir -p "$SANDBOX_DIR/fixed/figs"
cp "$SOURCE_DIR/figs/tiny_tree_figure_0.tex" \
   "$SANDBOX_DIR/fixed/figs/"
cp "$SOURCE_DIR/figs/tiny_tree_figure_1.tex" \
   "$SANDBOX_DIR/fixed/figs/"

cp "$SOURCE_DIR/neurips_2024.sty" "$SANDBOX_DIR/fixed/"
cp "$SOURCE_DIR/references.bib" "$SANDBOX_DIR/fixed/"

echo "=== Setup complete ==="
```

### 3.3 創建驗證工具

```bash
#!/bin/bash
# sandbox/latex_citation_fix/tools/verify.py

import re
import sys
from pathlib import Path

def check_survey_tex(file_path):
    """檢查 survey.tex 是否已修復"""
    content = Path(file_path).read_text()
    issues = []
    
    # Check 1: PassOptionsToPackage
    if "\\PassOptionsToPackage{dvipsnames,usenames}{xcolor}" not in content:
        issues.append("❌ Missing: \\PassOptionsToPackage for xcolor")
    else:
        print("✅ PassOptionsToPackage for xcolor")
    
    if "\\PassOptionsToPackage{numbers}{natbib}" not in content:
        issues.append("❌ Missing: \\PassOptionsToPackage for natbib")
    else:
        print("✅ PassOptionsToPackage for natbib")
    
    # Check 2: Color definitions
    required_colors = ['c12', 'c13', 'c14', 'c15', 'c16']
    for color in required_colors:
        if f"\\definecolor{{{color}}}" not in content:
            issues.append(f"❌ Missing: color definition for {color}")
    if all(f"\\definecolor{{{c}}}" in content for c in required_colors):
        print("✅ All color definitions present")
    
    # Check 3: No duplicate bibliographystyle
    bibstyle_count = content.count("\\bibliographystyle")
    if bibstyle_count > 1:
        issues.append(f"❌ Multiple \\bibliographystyle commands ({bibstyle_count})")
    else:
        print("✅ Only one \\bibliographystyle command")
    
    # Check 4: Correct bibliography order
    bib_pos = content.rfind("\\bibliography{")
    style_pos = content.rfind("\\bibliographystyle{")
    if style_pos > bib_pos:
        issues.append("❌ Wrong order: \\bibliographystyle should come before \\bibliography")
    else:
        print("✅ Correct bibliography command order")
    
    return issues

def check_figs_dir(figs_dir):
    """檢查圖表目錄中的 citation 問題"""
    figs_path = Path(figs_dir)
    issues = []
    total_double_escapes = 0
    
    for tex_file in figs_path.glob("*.tex"):
        content = tex_file.read_text()
        double_escapes = len(re.findall(r'\\\\cite{', content))
        if double_escapes > 0:
            issues.append(f"❌ {tex_file.name}: {double_escapes} double-escaped citations")
            total_double_escapes += double_escapes
    
    if total_double_escapes == 0:
        print("✅ No double-escaped citations in figs/")
    else:
        print(f"❌ Total double-escaped citations: {total_double_escapes}")
    
    return issues

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py <directory>")
        print("Example: python verify.py ../agent_workspace")
        sys.exit(1)
    
    work_dir = Path(sys.argv[1])
    
    print("=" * 60)
    print("LaTeX Citation Fix Verification")
    print("=" * 60)
    
    all_issues = []
    
    # Check survey.tex
    survey_path = work_dir / "survey.tex"
    if survey_path.exists():
        print("\n### Checking survey.tex ###")
        all_issues.extend(check_survey_tex(survey_path))
    else:
        print(f"❌ survey.tex not found in {work_dir}")
        all_issues.append("survey.tex missing")
    
    # Check figs/
    figs_path = work_dir / "figs"
    if figs_path.exists():
        print("\n### Checking figs/ ###")
        all_issues.extend(check_figs_dir(figs_path))
    else:
        print(f"❌ figs/ directory not found in {work_dir}")
        all_issues.append("figs/ directory missing")
    
    # Summary
    print("\n" + "=" * 60)
    if not all_issues:
        print("🎉 All checks passed! The fix is correct.")
        sys.exit(0)
    else:
        print(f"❌ Found {len(all_issues)} issue(s):")
        for issue in all_issues:
            print(f"  - {issue}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3.4 創建重置工具

```bash
#!/bin/bash
# sandbox/latex_citation_fix/tools/reset.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SANDBOX_ROOT="$(dirname "$SCRIPT_DIR")"
AGENT_WS="$SANDBOX_ROOT/agent_workspace"
BROKEN_DIR="$SANDBOX_ROOT/broken"

echo "=== Resetting Agent Workspace ==="
echo "This will delete all files in agent_workspace/ and copy from broken/"
echo -n "Continue? (y/N): "
read -r response

if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Clear agent workspace
echo "Clearing $AGENT_WS..."
rm -rf "$AGENT_WS"/*
touch "$AGENT_WS/.gitignore"
cat > "$AGENT_WS/.gitignore" << 'EOF'
# Agent 工作區 - 忽略所有生成的檔案
*
!.gitignore
EOF

# Copy broken files
echo "Copying files from broken/..."
cp -r "$BROKEN_DIR"/* "$AGENT_WS/"

echo "✅ Reset complete. Agent can now start fresh in:"
echo "   $AGENT_WS"
```

### 3.5 創建 README

```markdown
# LaTeX Citation Fix Challenge

## 目標

修復此 LaTeX 專案中的多個編譯問題,特別是 TikZ 圖表中的 citation 錯誤轉義問題。

## 問題描述

此專案包含一個 NeurIPS 2024 格式的學術論文,目前有以下編譯問題:

1. **Package option clashes**: `natbib` 和 `xcolor` 套件選項衝突
2. **Missing color definitions**: TikZ 圖表使用了未定義的顏色 (c12-c16)
3. **Duplicate bibliographystyle**: 重複的 `\bibliographystyle` 命令
4. **Wrong bibliography order**: `\bibliography` 和 `\bibliographystyle` 順序錯誤
5. **Double-escaped citations** (⭐主要問題): 圖表中的 `\cite{}` 被錯誤轉義為 `\\cite{}`

## 檔案結構

```
latex_citation_fix/
├── backup/              # 原始備份 (唯讀)
├── broken/              # 有問題的版本 (參考用)
├── fixed/               # 正確版本 (參考答案)
├── agent_workspace/     # ⭐ 你的工作區
└── tools/               # 驗證與重置工具
```

## 使用方式

### 1. 開始練習

```bash
# 重置工作區到初始狀態
cd sandbox/latex_citation_fix/tools
./reset.sh

# 進入工作區
cd ../agent_workspace
```

### 2. 診斷問題

```bash
# 嘗試編譯,觀察錯誤
pdflatex -interaction=nonstopmode survey.tex

# 檢查 log
less survey.log

# 檢查圖表中的 citation
grep -r "\\\\cite" figs/*.tex
```

### 3. 修復問題

參考 `docs/temporary_issues/latex_citation_fix_plan.md` 中的修復方案。

### 4. 驗證修復

```bash
cd ../tools
python verify.py ../agent_workspace
```

### 5. 比較答案

```bash
# 比較你的修復與參考答案
cd ../tools
./compare.sh
```

## 學習目標

- 理解 LaTeX 套件選項衝突的解決方法
- 學習 LaTeX 轉義規則
- 掌握批量修改檔案的技巧
- 練習系統性調試流程

## 參考文件

- `docs/temporary_issues/latex_citation_fix_plan.md` - 完整修復方案
- `docs/temporary_issues/bibtex_compilation_issue.md` - 問題追蹤歷史

## 成功標準

通過 `verify.py` 的所有檢查:

- ✅ PassOptionsToPackage 正確配置
- ✅ 所有顏色定義存在
- ✅ 只有一個 bibliographystyle 命令
- ✅ Bibliography 命令順序正確
- ✅ 圖表中沒有雙重轉義的 citations
```

---

## 4. 整合到專案

### 4.1 更新 .gitignore

```bash
# 在根目錄 .gitignore 新增
echo "" >> .gitignore
echo "# === Sandbox ===" >> .gitignore
echo "sandbox/*/agent_workspace/*" >> .gitignore
echo "!sandbox/*/agent_workspace/.gitignore" >> .gitignore
echo "sandbox/*/*.aux" >> .gitignore
echo "sandbox/*/*.log" >> .gitignore
echo "sandbox/*/*.pdf" >> .gitignore
```

### 4.2 更新根目錄 README

在 `README.md` 新增:

```markdown
## 🧪 Sandbox

`sandbox/` 目錄包含用於 AI Agent 練習的場景:

- `latex_citation_fix/` - LaTeX citation 轉義問題修復練習

詳見各 sandbox 目錄的 README.md。
```

### 4.3 創建 Module (可選)

如果需要程式化控制 sandbox:

```python
# src/modules/sandbox/__init__.py

from pathlib import Path
from typing import List, Dict

class LatexCitationFixSandbox:
    """
    LaTeX Citation Fix 練習環境管理
    """
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backup"
        self.broken_dir = self.base_dir / "broken"
        self.fixed_dir = self.base_dir / "fixed"
        self.workspace_dir = self.base_dir / "agent_workspace"
    
    def reset_workspace(self):
        """重置工作區到初始狀態"""
        # 實作邏輯
        pass
    
    def verify_fix(self) -> Dict[str, bool]:
        """驗證修復是否正確"""
        # 實作邏輯
        pass
    
    def get_diff(self) -> List[str]:
        """獲取修改差異"""
        # 實作邏輯
        pass
```

---

## 5. 檔案清理建議

基於前面的分析,以下備份可以刪除:

```bash
cd outputs/2025-10-09-1630_speec/latex

# 刪除重複或非關鍵的備份
rm survey.tex.backup_20251016_010602      # 早期測試版本
rm survey.tex.backup_underscore           # 特定問題嘗試
rm survey.tex.backup                      # 非特定時間點
rm benchmark_table.tex.backup             # 非關鍵問題
rm benchmark_table.tex.backup_resize      # 表格調整相關

# 刪除 sed 自動生成的 .bak (與 .ORIGINAL_BROKEN 重複)
rm figs/*.bak

# 保留的關鍵備份 (已重新命名):
# ✅ survey.tex.ORIGINAL_BROKEN              (最原始)
# ✅ survey.tex.INTERMEDIATE_page58fixed     (中間狀態)
# ✅ figs/*.ORIGINAL_BROKEN                  (含錯誤的 \\cite)
```

**注意: 以上檔案已清理完成!**

---

## 6. 總結

### 推薦配置

```
SurveyX/
├── sandbox/
│   └── latex_citation_fix/
│       ├── README.md                    # 使用說明
│       ├── backup/                      # 原始備份
│       │   ├── survey_original.tex
│       │   ├── figs_original/
│       │   ├── metadata.json
│       │   ├── neurips_2024.sty
│       │   └── references.bib
│       ├── broken/                      # 起點
│       ├── fixed/                       # 參考答案
│       ├── agent_workspace/             # Agent 工作區
│       │   └── .gitignore
│       └── tools/
│           ├── verify.py
│           ├── reset.sh
│           └── compare.sh
└── docs/
    └── temporary_issues/
        ├── latex_citation_fix_plan.md   # 已創建 ✅
        └── latex_sandbox_setup.md       # 本文檔 ✅
```

### 後續步驟

1. ✅ 執行 3.1-3.5 的設置腳本
2. ✅ 將必要檔案複製到 sandbox
3. ✅ 測試 verify.py 和 reset.sh
4. ✅ 更新 .gitignore 和 README
5. ✅ (可選) 開發 sandbox module

---

**維護者**: GitHub Copilot (AI Agent)  
**最後更新**: 2025-10-16 14:45
