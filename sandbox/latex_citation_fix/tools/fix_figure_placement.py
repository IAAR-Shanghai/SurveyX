#!/usr/bin/env python3
"""
修復 LaTeX Figure 放置問題

問題:
1. 所有 figures 都跑到 references 之後
2. Figure 引用顯示為 ??

原因:
1. 使用 figure* 環境在單欄文檔中造成放置困難
2. [!th] placement 參數缺少 p (page of floats)
3. 14 個 figures 累積無法放置，被推到文檔末尾

解決方案:
1. 將 figure* 改為 figure
2. 調整 placement 為 [htbp]
3. 在 bibliography 前加入 \clearpage 強制輸出所有 pending floats

Usage:
    python fix_figure_placement.py <latex_dir>
    python fix_figure_placement.py outputs/2025-10-09-1630_speec/latex
"""

import re
import shutil
from pathlib import Path
from datetime import datetime
import argparse


def fix_figure_files(figs_dir: Path, dry_run: bool = False) -> int:
    """修復所有 figure 檔案"""
    fixed_count = 0
    
    for tex_file in figs_dir.glob("*.tex"):
        content = tex_file.read_text()
        original_content = content
        
        # 1. figure* -> figure
        content = re.sub(
            r'\\begin{figure\*}',
            r'\\begin{figure}',
            content
        )
        content = re.sub(
            r'\\end{figure\*}',
            r'\\end{figure}',
            content
        )
        
        # 2. [!th] -> [htbp] (更靈活的放置)
        content = re.sub(
            r'\[!th\]',
            r'[htbp]',
            content
        )
        
        # 3. [!t] -> [htbp]
        content = re.sub(
            r'\[!t\]',
            r'[htbp]',
            content
        )
        
        if content != original_content:
            if not dry_run:
                # 備份
                backup_path = tex_file.parent / (tex_file.name + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy2(tex_file, backup_path)
                
                # 寫入修改
                tex_file.write_text(content)
            
            print(f"   ✅ Fixed {tex_file.name}")
            fixed_count += 1
        else:
            print(f"   ℹ️  {tex_file.name} already correct")
    
    return fixed_count


def fix_survey_file(survey_file: Path, dry_run: bool = False) -> bool:
    """在 bibliography 前加入 \clearpage"""
    content = survey_file.read_text()
    original_content = content
    changes = []
    
    # 檢查是否已經有 \clearpage
    if re.search(r'\\clearpage\s*\\bibliographystyle', content):
        print("   ℹ️  \\clearpage already present before bibliography")
        return False
    
    # 在 \bibliographystyle 前加入 \clearpage
    content = re.sub(
        r'(\\bibliographystyle)',
        r'\\clearpage\n\n\1',
        content
    )
    changes.append("Added \\clearpage before bibliography")
    
    # 可選: 在每個大 section 後加入 \FloatBarrier (如果有 placeins package)
    # 這需要在 preamble 中加入 \usepackage{placeins}
    
    if content != original_content:
        if not dry_run:
            # 備份
            backup_path = survey_file.parent / (survey_file.name + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(survey_file, backup_path)
            
            # 寫入修改
            survey_file.write_text(content)
        
        for change in changes:
            print(f"   ✅ {change}")
        return True
    
    return False


def verify_fixes(latex_dir: Path) -> list:
    """驗證修復結果"""
    issues = []
    
    figs_dir = latex_dir / "figs"
    
    # 檢查是否還有 figure*
    for tex_file in figs_dir.glob("*.tex"):
        content = tex_file.read_text()
        if 'figure*' in content:
            issues.append(f"❌ {tex_file.name} still contains figure*")
    
    if not issues:
        print("   ✅ No figure* environments found")
    
    # 檢查 survey.tex
    survey_file = latex_dir / "survey.tex"
    content = survey_file.read_text()
    
    if '\\clearpage' in content and '\\bibliographystyle' in content:
        # 檢查順序
        clearpage_pos = content.find('\\clearpage')
        bib_pos = content.find('\\bibliographystyle')
        
        if clearpage_pos < bib_pos and (bib_pos - clearpage_pos) < 100:
            print("   ✅ \\clearpage correctly placed before bibliography")
        else:
            issues.append("❌ \\clearpage not immediately before bibliography")
    else:
        issues.append("❌ \\clearpage not found before bibliography")
    
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="修復 LaTeX Figure 放置問題",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 修復特定輸出目錄
  python fix_figure_placement.py outputs/2025-10-09-1630_speec/latex
  
  # 乾跑模式
  python fix_figure_placement.py outputs/2025-10-09-1630_speec/latex --dry-run
        """
    )
    
    parser.add_argument(
        'latex_dir',
        type=str,
        help='LaTeX 目錄路徑'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='乾跑模式,不實際修改檔案'
    )
    
    args = parser.parse_args()
    
    latex_dir = Path(args.latex_dir)
    
    if not latex_dir.exists():
        print(f"❌ Error: Directory '{latex_dir}' does not exist")
        return 1
    
    figs_dir = latex_dir / "figs"
    if not figs_dir.exists():
        print(f"❌ Error: figs/ directory not found in '{latex_dir}'")
        return 1
    
    survey_file = latex_dir / "survey.tex"
    if not survey_file.exists():
        print(f"❌ Error: survey.tex not found in '{latex_dir}'")
        return 1
    
    print("=" * 60)
    print("LaTeX Figure Placement Fixer")
    print("=" * 60)
    print(f"Target: {latex_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    
    # 修復 figure 檔案
    print("\n📊 Fixing figure files...")
    fixed_count = fix_figure_files(figs_dir, args.dry_run)
    
    # 修復 survey.tex
    print("\n📝 Fixing survey.tex...")
    survey_fixed = fix_survey_file(survey_file, args.dry_run)
    
    # 驗證
    if not args.dry_run:
        print("\n🔍 Verifying fixes...")
        issues = verify_fixes(latex_dir)
        
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        
        if not issues:
            print("🎉 All fixes applied successfully!")
            print(f"\nFixed:")
            print(f"  ✅ {fixed_count} figure files")
            if survey_fixed:
                print(f"  ✅ Added \\clearpage in survey.tex")
            
            print(f"\n📋 Next steps:")
            print(f"  1. cd {latex_dir}")
            print(f"  2. rm -f *.aux *.bbl *.blg *.log *.out")
            print(f"  3. pdflatex survey.tex")
            print(f"  4. bibtex survey")
            print(f"  5. pdflatex survey.tex")
            print(f"  6. pdflatex survey.tex")
        else:
            print("⚠️  Some issues remain:")
            for issue in issues:
                print(f"  {issue}")
        
        print("=" * 60)
        
        return 0 if not issues else 1
    else:
        print("\n" + "=" * 60)
        print("DRY RUN - No changes made")
        print("=" * 60)
        print(f"\nWould fix:")
        print(f"  • {fixed_count} figure files")
        if re.search(r'\\bibliographystyle', survey_file.read_text()) and \
           not re.search(r'\\clearpage\s*\\bibliographystyle', survey_file.read_text()):
            print(f"  • Add \\clearpage in survey.tex")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    exit(main())
