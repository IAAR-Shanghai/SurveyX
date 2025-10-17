#!/usr/bin/env python3
"""
一鍵修復 Unicode glitch 並重新編譯 LaTeX

使用方式:
    python scripts/fix_and_recompile.py <task_id>

範例:
    python scripts/fix_and_recompile.py 2025-10-09-1630_speec
"""
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 設定路徑
FILE_PATH = Path(__file__).absolute()
BASE_DIR = FILE_PATH.parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.detect_unicode_glitches import UnicodeGlitchDetector
from scripts.fix_unicode_glitches import UnicodeGlitchFixer
from src.models.generator import LatexGenerator


class Colors:
    """終端機顏色"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def print_header(text):
    """印出標題"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")


def print_step(step_num, total, text):
    """印出步驟"""
    print(f"\n{Colors.YELLOW}[Step {step_num}/{total}] {text}{Colors.NC}")


def print_success(text):
    """印出成功訊息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")


def print_error(text):
    """印出錯誤訊息"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")


def print_warning(text):
    """印出警告訊息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")


def main():
    # 檢查參數
    if len(sys.argv) < 2:
        print_error("請提供 task_id")
        print("使用方式: python scripts/fix_and_recompile.py <task_id>")
        print("範例:     python scripts/fix_and_recompile.py 2025-10-09-1630_speec")
        sys.exit(1)
    
    task_id = sys.argv[1]
    output_dir = BASE_DIR / "outputs" / task_id
    latex_dir = output_dir / "latex"
    tex_file = latex_dir / "survey.tex"
    tmp_dir = output_dir / "tmp"
    
    print_header(f"Unicode Glitch 修復與重新編譯")
    print(f"Task ID: {task_id}")
    print(f"Base Directory: {BASE_DIR}")
    
    # 檢查檔案是否存在
    if not output_dir.exists():
        print_error(f"找不到目錄: {output_dir}")
        sys.exit(1)
    
    if not tex_file.exists():
        print_error(f"找不到檔案: {tex_file}")
        sys.exit(1)
    
    # 確保 tmp 目錄存在
    tmp_dir.mkdir(exist_ok=True, parents=True)
    
    # ============================================
    # Step 1: 偵測 Unicode 符號
    # ============================================
    print_step(1, 4, "偵測 Unicode 符號...")
    
    detector_before = UnicodeGlitchDetector(tex_file)
    issues_before = detector_before.detect_unicode_symbols()
    analysis_before = detector_before.analyze_glitch_patterns(issues_before)
    
    report_before = tmp_dir / "unicode_report_before.txt"
    detector_before.generate_report(report_before)
    
    unicode_count = analysis_before['total']
    
    if unicode_count == 0:
        print_success("沒有發現 Unicode 符號,檔案已經是乾淨的!")
        sys.exit(0)
    else:
        print(f"  發現 {unicode_count} 個 Unicode 符號")
        print(f"  涉及 {analysis_before['affected_lines']} 行")
        print(f"  報告已儲存: {report_before}")
    
    # ============================================
    # Step 2: 備份原檔案
    # ============================================
    print_step(2, 4, "備份原檔案...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = tex_file.with_suffix(f".tex.backup_{timestamp}")
    shutil.copy2(tex_file, backup_file)
    print_success(f"備份已儲存: {backup_file}")
    
    # ============================================
    # Step 3: 修復 Unicode 符號
    # ============================================
    print_step(3, 4, "修復 Unicode 符號...")
    
    fixer = UnicodeGlitchFixer(tex_file, backup=False)
    fix_stats = fixer.fix_file()
    
    print(f"  總行數: {fix_stats['total_lines']}")
    print(f"  修改行數: {fix_stats['lines_modified']}")
    print(f"  替換次數: {fix_stats['total_replacements']}")
    
    # 驗證修復結果
    detector_after = UnicodeGlitchDetector(tex_file)
    issues_after = detector_after.detect_unicode_symbols()
    analysis_after = detector_after.analyze_glitch_patterns(issues_after)
    
    report_after = tmp_dir / "unicode_report_after.txt"
    detector_after.generate_report(report_after)
    
    unicode_count_after = analysis_after['total']
    
    if unicode_count_after == 0:
        print_success("所有 Unicode 符號已成功修復!")
    else:
        print_warning(f"仍有 {unicode_count_after} 個 Unicode 符號未修復")
    
    # ============================================
    # Step 4: 重新編譯 LaTeX
    # ============================================
    print_step(4, 4, "重新編譯 LaTeX...")
    
    try:
        # 刪除舊的 PDF
        old_pdf = output_dir / "survey.pdf"
        old_wtmk = output_dir / "survey_wtmk.pdf"
        
        if old_pdf.exists():
            old_pdf.unlink()
            print("  - 已刪除舊的 survey.pdf")
        
        if old_wtmk.exists():
            old_wtmk.unlink()
            print("  - 已刪除舊的 survey_wtmk.pdf")
        
        # 使用 LatexGenerator 編譯
        print("  - 執行 latexmk (這可能需要幾分鐘)...")
        latex_gen = LatexGenerator(task_id=task_id)
        latex_gen.compile_single_survey()
        
        # 檢查結果
        if old_pdf.exists():
            print_success("PDF 編譯成功!")
            
            # 檢查浮水印版本
            if old_wtmk.exists():
                print_success("浮水印版本已生成!")
        else:
            print_error("PDF 編譯失敗,請檢查 latex/compile.log")
            sys.exit(1)
    
    except Exception as e:
        print_error(f"編譯時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ============================================
    # 完成
    # ============================================
    print_header("✓ 完成!")
    
    print("結果檔案:")
    print(f"  - 修復後的 TEX: {tex_file}")
    print(f"  - 原始備份:     {backup_file}")
    print(f"  - 新的 PDF:     {output_dir / 'survey.pdf'}")
    print(f"  - 有浮水印版本: {output_dir / 'survey_wtmk.pdf'}")
    print()
    print("檢查報告:")
    print(f"  - 修復前: {report_before}")
    print(f"  - 修復後: {report_after}")
    print(f"  - 編譯日誌: {latex_dir / 'compile.log'}")
    print()
    print(f"{Colors.YELLOW}提示: 你可以用以下指令驗證 spacing glitch 是否消失:{Colors.NC}")
    print(f"  pdftotext {output_dir / 'survey.pdf'} - | grep -E 'acommonpointuses|DiffSoundStream'")
    print()


if __name__ == '__main__':
    main()
