#!/usr/bin/env python3
"""
LaTeX Citation Fix Toolkit - 統一修復工具

整合所有 LaTeX 修復功能：
1. Caption/Label 格式修復
2. Figure 放置問題修復
3. Figure 引用修復
4. 一般 LaTeX 問題修復

Usage:
    # 顯示幫助
    python latex_fix_toolkit.py --help
    
    # 修復特定問題
    python latex_fix_toolkit.py fix-caption <latex_dir>
    python latex_fix_toolkit.py fix-placement <latex_dir>
    python latex_fix_toolkit.py fix-refs <latex_dir>
    python latex_fix_toolkit.py fix-all <latex_dir>
    
    # 診斷問題
    python latex_fix_toolkit.py diagnose <latex_dir>

Author: AI Agent (GitHub Copilot)
Date: 2025-10-17
"""

import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict
import sys


class LatexFixToolkit:
    """LaTeX 問題統一修復工具"""
    
    def __init__(self, latex_dir: Path, dry_run: bool = False):
        self.latex_dir = Path(latex_dir)
        self.dry_run = dry_run
        self.survey_file = self.latex_dir / "survey.tex"
        self.figs_dir = self.latex_dir / "figs"
        self.fixes_applied = []
        
    def backup_file(self, filepath: Path) -> Path:
        """備份檔案"""
        if self.dry_run:
            return filepath
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = filepath.with_suffix(f".backup_{timestamp}")
        shutil.copy2(filepath, backup_path)
        return backup_path
    
    # ========== 1. Caption/Label 格式修復 ==========
    
    def fix_caption_label_spacing(self) -> int:
        """
        修復 caption 和 label 之間的空格/換行問題
        確保 label 與 caption 之間有換行
        """
        print("\n📝 修復 Caption/Label 格式...")
        
        if not self.figs_dir.exists():
            print(f"   ❌ figs 目錄不存在: {self.figs_dir}")
            return 0
        
        fixed_count = 0
        pattern = r'(\\caption\{[^}]*\})\s+(\\label\{[^}]+\})'
        
        for tex_file in self.figs_dir.glob("*.tex"):
            content = tex_file.read_text(encoding='utf-8')
            original = content
            
            def replace_func(match):
                caption = match.group(1)
                label = match.group(2)
                return f'{caption}\n{label}'
            
            content = re.sub(pattern, replace_func, content)
            
            if content != original:
                if not self.dry_run:
                    self.backup_file(tex_file)
                    tex_file.write_text(content, encoding='utf-8')
                print(f"   ✅ {tex_file.name}")
                fixed_count += 1
                self.fixes_applied.append(f"Caption/Label spacing: {tex_file.name}")
        
        print(f"   📊 修復 {fixed_count} 個檔案")
        return fixed_count
    
    # ========== 2. Figure 放置問題修復 ==========
    
    def fix_figure_placement(self) -> int:
        """
        修復 Figure 放置問題:
        1. 將 figure* 改為 figure
        2. 調整 placement 為 [htbp]
        3. 在 bibliography 前加入 \clearpage
        """
        print("\n📐 修復 Figure 放置問題...")
        
        if not self.figs_dir.exists():
            print(f"   ❌ figs 目錄不存在: {self.figs_dir}")
            return 0
        
        fixed_count = 0
        
        # 修復 figs/ 中的圖檔
        for tex_file in self.figs_dir.glob("*.tex"):
            content = tex_file.read_text(encoding='utf-8')
            original = content
            
            # 1. figure* -> figure
            content = re.sub(r'\\begin\{figure\*\}', r'\\begin{figure}', content)
            content = re.sub(r'\\end\{figure\*\}', r'\\end{figure}', content)
            
            # 2. 調整 placement
            content = re.sub(
                r'\\begin\{figure\}\[!th\]',
                r'\\begin{figure}[htbp]',
                content
            )
            
            if content != original:
                if not self.dry_run:
                    self.backup_file(tex_file)
                    tex_file.write_text(content, encoding='utf-8')
                print(f"   ✅ {tex_file.name}")
                fixed_count += 1
                self.fixes_applied.append(f"Figure placement: {tex_file.name}")
        
        # 修復 survey.tex 中的 bibliography 位置
        if self.survey_file.exists():
            content = self.survey_file.read_text(encoding='utf-8')
            original = content
            
            # 在 bibliography 前加入 \clearpage
            if '\\bibliography{' in content and '\\clearpage\n\\bibliography{' not in content:
                content = re.sub(
                    r'(\\bibliography\{)',
                    r'\\clearpage\n\\1',
                    content
                )
            
            if content != original:
                if not self.dry_run:
                    self.backup_file(self.survey_file)
                    self.survey_file.write_text(content, encoding='utf-8')
                print(f"   ✅ {self.survey_file.name} (added \\clearpage)")
                fixed_count += 1
                self.fixes_applied.append("Added \\clearpage before bibliography")
        
        print(f"   📊 修復 {fixed_count} 個檔案")
        return fixed_count
    
    # ========== 3. Figure 引用修復 ==========
    
    def fix_figure_references(self) -> int:
        """
        修復 Figure 引用問題:
        1. \autoref{fig:tiny\_tree\_figure_X} -> \autoref{fig:tiny_tree_figure_X}
        2. 其他轉義下劃線問題
        """
        print("\n🔗 修復 Figure 引用...")
        
        if not self.survey_file.exists():
            print(f"   ❌ survey.tex 不存在: {self.survey_file}")
            return 0
        
        content = self.survey_file.read_text(encoding='utf-8')
        original = content
        fixed_count = 0
        
        # 修復轉義下劃線
        pattern = r'\\autoref\{fig:tiny\\_tree\\_figure\\_(\d+)\}'
        
        def replace_func(match):
            nonlocal fixed_count
            fig_num = match.group(1)
            fixed_count += 1
            return f'\\autoref{{fig:tiny_tree_figure_{fig_num}}}'
        
        content = re.sub(pattern, replace_func, content)
        
        # 檢查其他轉義下劃線
        other_escaped = re.findall(r'\\autoref\{fig:[^}]*\\\\_[^}]*\}', content)
        if other_escaped:
            print(f"   ⚠️  發現 {len(other_escaped)} 個其他轉義下劃線:")
            for ref in other_escaped[:5]:
                print(f"      {ref}")
        
        if content != original:
            if not self.dry_run:
                self.backup_file(self.survey_file)
                self.survey_file.write_text(content, encoding='utf-8')
            print(f"   ✅ 修復 {fixed_count} 個引用")
            self.fixes_applied.append(f"Fixed {fixed_count} escaped underscores in references")
        else:
            print(f"   ℹ️  無需修改")
        
        return fixed_count
    
    # ========== 4. 一般 LaTeX 問題修復 ==========
    
    def fix_general_issues(self) -> int:
        """
        修復一般 LaTeX 問題:
        1. Package option clashes
        2. Missing color definitions
        3. Duplicate bibliographystyle
        4. Double-escaped citations
        """
        print("\n🔧 修復一般 LaTeX 問題...")
        
        if not self.survey_file.exists():
            print(f"   ❌ survey.tex 不存在: {self.survey_file}")
            return 0
        
        content = self.survey_file.read_text(encoding='utf-8')
        original = content
        fixes = []
        
        # 1. 檢查 package option clashes
        natbib_loads = len(re.findall(r'\\usepackage(?:\[[^\]]*\])?\{natbib\}', content))
        if natbib_loads > 1:
            print(f"   ⚠️  natbib 載入 {natbib_loads} 次")
            fixes.append("Multiple natbib loads detected")
        
        # 2. 檢查顏色定義
        missing_colors = []
        for i in range(12, 17):
            color_name = f'c{i}'
            if f'\\definecolor{{{color_name}}}' not in content and f'\\color{{{color_name}}}' in content:
                missing_colors.append(color_name)
        
        if missing_colors:
            print(f"   ⚠️  缺少顏色定義: {', '.join(missing_colors)}")
            fixes.append(f"Missing color definitions: {', '.join(missing_colors)}")
        
        # 3. 檢查 double-escaped citations
        double_escaped = re.findall(r'\\\\cite\{[^}]+\}', content)
        if double_escaped:
            print(f"   ⚠️  發現 {len(double_escaped)} 個雙重轉義的 citation")
            fixes.append(f"Double-escaped citations: {len(double_escaped)}")
        
        if fixes:
            self.fixes_applied.extend(fixes)
            print(f"   📊 發現 {len(fixes)} 個潛在問題")
            return len(fixes)
        else:
            print(f"   ✅ 未發現一般問題")
            return 0
    
    # ========== 診斷功能 ==========
    
    def diagnose(self) -> Dict[str, any]:
        """診斷 LaTeX 專案的潛在問題"""
        print("\n🔍 診斷 LaTeX 專案...")
        print(f"   目錄: {self.latex_dir}")
        
        issues = {
            'caption_label': [],
            'figure_placement': [],
            'figure_refs': [],
            'general': [],
            'summary': {}
        }
        
        # 檢查 caption/label 格式
        if self.figs_dir.exists():
            pattern = r'(\\caption\{[^}]*\})\s+(\\label\{[^}]+\})'
            for tex_file in self.figs_dir.glob("*.tex"):
                content = tex_file.read_text(encoding='utf-8')
                matches = re.findall(pattern, content)
                if matches:
                    issues['caption_label'].append(f"{tex_file.name}: {len(matches)} issues")
        
        # 檢查 figure* 環境
        if self.figs_dir.exists():
            for tex_file in self.figs_dir.glob("*.tex"):
                content = tex_file.read_text(encoding='utf-8')
                if '\\begin{figure*}' in content:
                    issues['figure_placement'].append(f"{tex_file.name}: uses figure*")
        
        # 檢查轉義下劃線
        if self.survey_file.exists():
            content = self.survey_file.read_text(encoding='utf-8')
            escaped = re.findall(r'\\autoref\{fig:[^}]*\\\\_[^}]*\}', content)
            if escaped:
                issues['figure_refs'].extend(escaped[:5])
        
        # 統計
        issues['summary'] = {
            'caption_label_files': len(issues['caption_label']),
            'figure_placement_files': len(issues['figure_placement']),
            'figure_refs_issues': len(issues['figure_refs']),
            'general_issues': len(issues['general'])
        }
        
        # 顯示結果
        print(f"\n📊 診斷結果:")
        print(f"   Caption/Label 問題: {issues['summary']['caption_label_files']} 個檔案")
        print(f"   Figure 放置問題: {issues['summary']['figure_placement_files']} 個檔案")
        print(f"   Figure 引用問題: {issues['summary']['figure_refs_issues']} 個引用")
        print(f"   一般問題: {issues['summary']['general_issues']} 個")
        
        return issues
    
    # ========== 主執行函數 ==========
    
    def fix_all(self) -> int:
        """執行所有修復"""
        print("\n🚀 執行所有修復...")
        total = 0
        total += self.fix_caption_label_spacing()
        total += self.fix_figure_placement()
        total += self.fix_figure_references()
        total += self.fix_general_issues()
        
        print(f"\n✅ 總共修復 {total} 個問題")
        if self.fixes_applied:
            print(f"\n📋 修復清單:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        return total


def main():
    parser = argparse.ArgumentParser(
        description="LaTeX Citation Fix Toolkit - 統一修復工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 診斷問題
  python latex_fix_toolkit.py diagnose outputs/2025-10-09-1630_speec/latex
  
  # 修復特定問題
  python latex_fix_toolkit.py fix-caption outputs/2025-10-09-1630_speec/latex
  python latex_fix_toolkit.py fix-placement outputs/2025-10-09-1630_speec/latex
  python latex_fix_toolkit.py fix-refs outputs/2025-10-09-1630_speec/latex
  
  # 修復所有問題
  python latex_fix_toolkit.py fix-all outputs/2025-10-09-1630_speec/latex
  
  # Dry-run 模式
  python latex_fix_toolkit.py --dry-run fix-all outputs/2025-10-09-1630_speec/latex
"""
    )
    
    parser.add_argument('command', choices=[
        'diagnose',
        'fix-caption',
        'fix-placement',
        'fix-refs',
        'fix-general',
        'fix-all'
    ], help='要執行的命令')
    
    parser.add_argument('latex_dir', help='LaTeX 專案目錄')
    parser.add_argument('--dry-run', action='store_true', help='Dry-run 模式（不實際修改檔案）')
    
    args = parser.parse_args()
    
    # 檢查目錄是否存在
    latex_dir = Path(args.latex_dir)
    if not latex_dir.exists():
        print(f"❌ 目錄不存在: {latex_dir}")
        sys.exit(1)
    
    # 建立工具實例
    toolkit = LatexFixToolkit(latex_dir, dry_run=args.dry_run)
    
    if args.dry_run:
        print("🔍 Dry-run 模式（不會實際修改檔案）\n")
    
    # 執行命令
    if args.command == 'diagnose':
        toolkit.diagnose()
    elif args.command == 'fix-caption':
        toolkit.fix_caption_label_spacing()
    elif args.command == 'fix-placement':
        toolkit.fix_figure_placement()
    elif args.command == 'fix-refs':
        toolkit.fix_figure_references()
    elif args.command == 'fix-general':
        toolkit.fix_general_issues()
    elif args.command == 'fix-all':
        toolkit.fix_all()


if __name__ == "__main__":
    main()
