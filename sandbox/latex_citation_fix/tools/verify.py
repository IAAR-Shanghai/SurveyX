#!/usr/bin/env python3
"""
LaTeX Citation Fix - 驗證腳本

檢查 agent workspace 中的修復是否正確
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def check_survey_tex(file_path: Path) -> Tuple[List[str], List[str]]:
    """檢查 survey.tex 是否已修復
    
    Returns:
        (passed_checks, failed_checks)
    """
    content = file_path.read_text()
    passed = []
    failed = []
    
    # Check 1: PassOptionsToPackage for xcolor
    if "\\PassOptionsToPackage{dvipsnames,usenames}{xcolor}" in content:
        passed.append("✅ PassOptionsToPackage for xcolor")
    else:
        failed.append("❌ Missing: \\PassOptionsToPackage{dvipsnames,usenames}{xcolor}")
    
    # Check 2: PassOptionsToPackage for natbib
    if "\\PassOptionsToPackage{numbers}{natbib}" in content:
        passed.append("✅ PassOptionsToPackage for natbib")
    else:
        failed.append("❌ Missing: \\PassOptionsToPackage{numbers}{natbib}")
    
    # Check 3: Color definitions
    required_colors = ['c12', 'c13', 'c14', 'c15', 'c16']
    missing_colors = []
    for color in required_colors:
        if f"\\definecolor{{{color}}}" not in content:
            missing_colors.append(color)
    
    if not missing_colors:
        passed.append("✅ All color definitions present (c12-c16)")
    else:
        failed.append(f"❌ Missing color definitions: {', '.join(missing_colors)}")
    
    # Check 4: No duplicate bibliographystyle
    bibstyle_count = content.count("\\bibliographystyle")
    if bibstyle_count == 0:
        failed.append("❌ No \\bibliographystyle command found")
    elif bibstyle_count == 1:
        passed.append("✅ Only one \\bibliographystyle command")
    else:
        failed.append(f"❌ Multiple \\bibliographystyle commands ({bibstyle_count})")
    
    # Check 5: Correct bibliography order
    bib_pos = content.rfind("\\bibliography{")
    style_pos = content.rfind("\\bibliographystyle{")
    
    if bib_pos == -1 or style_pos == -1:
        failed.append("❌ Missing \\bibliography or \\bibliographystyle command")
    elif style_pos < bib_pos:
        passed.append("✅ Correct bibliography command order (style before bibliography)")
    else:
        failed.append("❌ Wrong order: \\bibliographystyle should come before \\bibliography")
    
    return passed, failed


def check_figs_dir(figs_dir: Path) -> Tuple[List[str], List[str]]:
    """檢查圖表目錄中的 citation 問題
    
    Returns:
        (passed_checks, failed_checks)
    """
    passed = []
    failed = []
    
    if not figs_dir.exists():
        failed.append("❌ figs/ directory not found")
        return passed, failed
    
    total_double_escapes = 0
    problematic_files = []
    
    for tex_file in figs_dir.glob("*.tex"):
        content = tex_file.read_text()
        double_escapes = len(re.findall(r'\\\\cite\{', content))
        if double_escapes > 0:
            total_double_escapes += double_escapes
            problematic_files.append(f"{tex_file.name} ({double_escapes})")
    
    if total_double_escapes == 0:
        passed.append("✅ No double-escaped citations in figs/")
    else:
        failed.append(f"❌ Found {total_double_escapes} double-escaped citations in {len(problematic_files)} files")
        for pf in problematic_files[:5]:  # Show first 5
            failed.append(f"   - {pf}")
        if len(problematic_files) > 5:
            failed.append(f"   ... and {len(problematic_files) - 5} more files")
    
    return passed, failed


def print_section(title: str):
    """印出章節標題"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify.py <directory>")
        print("Example: python verify.py ../agent_workspace")
        sys.exit(1)
    
    work_dir = Path(sys.argv[1])
    
    if not work_dir.exists():
        print(f"❌ Error: Directory '{work_dir}' does not exist")
        sys.exit(1)
    
    print_section("LaTeX Citation Fix - Verification")
    print(f"Checking: {work_dir.absolute()}")
    
    all_passed = []
    all_failed = []
    
    # Check survey.tex
    survey_path = work_dir / "survey.tex"
    if survey_path.exists():
        print("\n### Checking survey.tex ###\n")
        passed, failed = check_survey_tex(survey_path)
        all_passed.extend(passed)
        all_failed.extend(failed)
        
        for check in passed:
            print(check)
        for check in failed:
            print(check)
    else:
        print("\n### survey.tex ###")
        print(f"❌ survey.tex not found in {work_dir}")
        all_failed.append("survey.tex missing")
    
    # Check figs/
    figs_path = work_dir / "figs"
    print("\n### Checking figs/ ###\n")
    passed, failed = check_figs_dir(figs_path)
    all_passed.extend(passed)
    all_failed.extend(failed)
    
    for check in passed:
        print(check)
    for check in failed:
        print(check)
    
    # Summary
    print_section("Summary")
    print(f"Passed: {len(all_passed)}")
    print(f"Failed: {len(all_failed)}")
    
    if not all_failed:
        print("\n🎉 All checks passed! The fix is correct.")
        sys.exit(0)
    else:
        print(f"\n❌ {len(all_failed)} issue(s) found. Please review the failed checks above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
