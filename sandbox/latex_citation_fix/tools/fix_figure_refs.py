#!/usr/bin/env python3
"""
修復 LaTeX 中的錯誤 figure 引用

問題:
1. \autoref{fig:tiny\_tree\_figure_X} 應該是 \autoref{fig:tiny_tree_figure_X}
   (下劃線不應該轉義)
2. Label 名稱中的空格問題

Usage:
    python fix_figure_refs.py <latex_dir>
"""

import re
import shutil
from pathlib import Path
from datetime import datetime
import argparse


def fix_figure_references(survey_file: Path, dry_run: bool = False) -> dict:
    """修復 survey.tex 中的 figure 引用"""
    content = survey_file.read_text()
    original_content = content
    
    fixes = {
        'escaped_underscores': 0,
        'details': []
    }
    
    # 修復 1: 將 fig:tiny\_tree\_figure_ 改為 fig:tiny_tree_figure_
    # 注意: 在 Python 字串中 \\\\ 表示一個反斜線
    # LaTeX 中的 \_ 在檔案中實際是兩個字元: \ 和 _
    pattern = r'\\autoref\{fig:tiny\\_tree\\_figure\\_(\d+)\}'
    
    def replace_func(match):
        fig_num = match.group(1)
        fixes['escaped_underscores'] += 1
        fixes['details'].append(f"tiny_tree_figure_{fig_num}")
        return f'\\autoref{{fig:tiny_tree_figure_{fig_num}}}'
    
    content = re.sub(pattern, replace_func, content)
    
    # 檢查是否有其他轉義下劃線的 figure 引用
    other_escaped = re.findall(r'\\autoref\{fig:[^}]*\\\\_[^}]*\}', content)
    if other_escaped:
        print(f"   ⚠️  Found {len(other_escaped)} other escaped underscores:")
        for ref in other_escaped[:5]:
            print(f"      {ref}")
    
    if content != original_content:
        if not dry_run:
            # 備份
            backup_path = survey_file.parent / (survey_file.name + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(survey_file, backup_path)
            
            # 寫入修改
            survey_file.write_text(content)
        
        return fixes
    
    return None


def check_label_consistency(latex_dir: Path):
    """檢查 label 和引用的一致性"""
    print("\n🔍 Checking label consistency...")
    
    # 收集所有 figure labels
    figs_dir = latex_dir / "figs"
    labels = set()
    
    for tex_file in figs_dir.glob("*.tex"):
        content = tex_file.read_text()
        found_labels = re.findall(r'\\label\{fig:([^}]+)\}', content)
        labels.update(found_labels)
    
    print(f"   Found {len(labels)} figure labels in figs/")
    
    # 檢查 survey.tex 中的引用
    survey_file = latex_dir / "survey.tex"
    content = survey_file.read_text()
    
    refs = re.findall(r'\\(?:autoref|ref)\{fig:([^}]+)\}', content)
    unique_refs = set(refs)
    
    print(f"   Found {len(refs)} figure references in survey.tex ({len(unique_refs)} unique)")
    
    # 找出未定義的引用
    undefined = unique_refs - labels
    if undefined:
        print(f"\n   ⚠️  Undefined references:")
        for ref in sorted(undefined):
            print(f"      fig:{ref}")
            # 嘗試找出最接近的 label
            close_matches = [l for l in labels if ref.replace('_', ' ') in l or l.replace(' ', '_') in ref]
            if close_matches:
                print(f"         → Possible match: {close_matches[0]}")
    else:
        print(f"   ✅ All references are defined")
    
    return undefined


def verify_fixes(survey_file: Path) -> bool:
    """驗證修復結果"""
    content = survey_file.read_text()
    
    # 檢查是否還有轉義的下劃線
    escaped = re.findall(r'\\autoref\{fig:[^}]*\\\\_[^}]*\}', content)
    
    if not escaped:
        print("   ✅ No escaped underscores in figure references")
        return True
    else:
        print(f"   ❌ Still found {len(escaped)} escaped underscores")
        for ref in escaped[:5]:
            print(f"      {ref}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="修復 LaTeX figure 引用問題",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fix_figure_refs.py outputs/2025-10-09-1630_speec/latex
  python fix_figure_refs.py outputs/2025-10-09-1630_speec/latex --dry-run
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
    survey_file = latex_dir / "survey.tex"
    
    if not survey_file.exists():
        print(f"❌ Error: survey.tex not found in '{latex_dir}'")
        return 1
    
    print("=" * 60)
    print("LaTeX Figure Reference Fixer")
    print("=" * 60)
    print(f"Target: {latex_dir}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    
    # 修復引用
    print("\n📝 Fixing figure references...")
    fixes = fix_figure_references(survey_file, args.dry_run)
    
    if fixes:
        print(f"   ✅ Fixed {fixes['escaped_underscores']} escaped underscores")
        if fixes['details']:
            print(f"   Modified figures:")
            for detail in fixes['details'][:10]:
                print(f"      - {detail}")
            if len(fixes['details']) > 10:
                print(f"      ... and {len(fixes['details']) - 10} more")
    else:
        print("   ℹ️  No fixes needed")
    
    # 檢查一致性
    undefined = check_label_consistency(latex_dir)
    
    # 驗證
    if not args.dry_run and fixes:
        print("\n🔍 Verifying fixes...")
        success = verify_fixes(survey_file)
        
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        
        if success and not undefined:
            print("🎉 All figure references fixed!")
            print(f"\nFixed:")
            print(f"  ✅ {fixes['escaped_underscores']} escaped underscores")
            print(f"  ✅ All references are now defined")
            
            print(f"\n📋 Next steps:")
            print(f"  1. cd {latex_dir}")
            print(f"  2. pdflatex survey.tex")
            print(f"  3. pdflatex survey.tex")
            print(f"  4. Check that ?? marks are gone")
        else:
            if undefined:
                print("⚠️  Some references are still undefined")
                print("    These may need manual fixing")
            if not success:
                print("⚠️  Some escaped underscores remain")
        
        print("=" * 60)
        
        return 0 if (success and not undefined) else 1
    else:
        print("\n" + "=" * 60)
        if args.dry_run:
            print("DRY RUN - No changes made")
            if fixes:
                print(f"\nWould fix:")
                print(f"  • {fixes['escaped_underscores']} escaped underscores")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    exit(main())
