#!/usr/bin/env python3
"""
修復 LaTeX 檔案中的 Unicode 數學符號問題
將 Unicode 符號替換為對應的 LaTeX 巨集
"""
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, Tuple

FILE_PATH = Path(__file__).absolute()
BASE_DIR = FILE_PATH.parent.parent
sys.path.insert(0, str(BASE_DIR))


class UnicodeGlitchFixer:
    """修復 LaTeX 檔案中的 Unicode 數學符號"""
    
    # Unicode 標點符號 (不需要數學模式)
    UNICODE_PUNCTUATION = {
        '\u2011': r'-',  # NON-BREAKING HYPHEN → 普通連字號
        '\u2013': r'--',  # EN DASH → LaTeX en-dash
        '\u2014': r'---',  # EM DASH → LaTeX em-dash
        '\u2018': r"`",  # LEFT SINGLE QUOTATION MARK
        '\u2019': r"'",  # RIGHT SINGLE QUOTATION MARK
        '\u201C': r"``",  # LEFT DOUBLE QUOTATION MARK
        '\u201D': r"''",  # RIGHT DOUBLE QUOTATION MARK
        '\u2026': r'\ldots',  # HORIZONTAL ELLIPSIS
        '\u00A0': r' ',  # NO-BREAK SPACE → 普通空格
    }
    
    # Unicode 數學符號對應的 LaTeX 巨集 (需要數學模式)
    UNICODE_TO_LATEX = {
        # 數學符號
        '∈': r'\in',
        '∉': r'\notin',
        '≈': r'\approx',
        '≠': r'\neq',
        '≤': r'\le',
        '≥': r'\ge',
        '≪': r'\ll',
        '≫': r'\gg',
        '∼': r'\sim',
        '≃': r'\simeq',
        '≅': r'\cong',
        '−': r'-',  # 數學減號,在 text mode 使用 - 即可
        '×': r'\times',
        '÷': r'\div',
        '±': r'\pm',
        '∓': r'\mp',
        '∞': r'\infty',
        '∑': r'\sum',
        '∏': r'\prod',
        '∫': r'\int',
        '∂': r'\partial',
        '∇': r'\nabla',
        '√': r'\sqrt',
        '∝': r'\propto',
        '∀': r'\forall',
        '∃': r'\exists',
        '∧': r'\wedge',
        '∨': r'\vee',
        '¬': r'\neg',
        '⇒': r'\Rightarrow',
        '⇐': r'\Leftarrow',
        '⇔': r'\Leftrightarrow',
        '→': r'\rightarrow',
        '←': r'\leftarrow',
        '↔': r'\leftrightarrow',
        # 希臘字母
        'α': r'\alpha',
        'β': r'\beta',
        'γ': r'\gamma',
        'δ': r'\delta',
        'ε': r'\epsilon',
        'ζ': r'\zeta',
        'η': r'\eta',
        'θ': r'\theta',
        'ι': r'\iota',
        'κ': r'\kappa',
        'λ': r'\lambda',
        'μ': r'\mu',
        'ν': r'\nu',
        'ξ': r'\xi',
        'ο': r'o',
        'π': r'\pi',
        'ρ': r'\rho',
        'σ': r'\sigma',
        'τ': r'\tau',
        'υ': r'\upsilon',
        'φ': r'\phi',
        'χ': r'\chi',
        'ψ': r'\psi',
        'ω': r'\omega',
        'Α': r'A',
        'Β': r'B',
        'Γ': r'\Gamma',
        'Δ': r'\Delta',
        'Ε': r'E',
        'Ζ': r'Z',
        'Η': r'H',
        'Θ': r'\Theta',
        'Ι': r'I',
        'Κ': r'K',
        'Λ': r'\Lambda',
        'Μ': r'M',
        'Ν': r'N',
        'Ξ': r'\Xi',
        'Ο': r'O',
        'Π': r'\Pi',
        'Ρ': r'P',
        'Σ': r'\Sigma',
        'Τ': r'T',
        'Υ': r'\Upsilon',
        'Φ': r'\Phi',
        'Χ': r'X',
        'Ψ': r'\Psi',
        'Ω': r'\Omega',
    }
    
    def __init__(self, tex_file: Path, backup: bool = True):
        self.tex_file = Path(tex_file)
        self.backup = backup
        self.replacement_count = 0
        
    def check_if_in_math_mode(self, text_before: str) -> bool:
        """
        檢查該位置是否已在數學模式內
        這是一個簡化版本,不處理巢狀情況
        """
        # 計算 $ 的數量 (排除 escaped \$)
        dollar_count = text_before.count('$') - text_before.count(r'\$')
        if dollar_count % 2 == 1:
            return True
        
        # 檢查是否在數學環境內
        math_envs = ['equation', 'align', 'gather', 'multline', 'displaymath', 'math']
        for env in math_envs:
            begin_count = text_before.count(f'\\begin{{{env}}}')
            end_count = text_before.count(f'\\end{{{env}}}')
            if begin_count > end_count:
                return True
        
        return False
    
    def fix_line(self, line: str) -> Tuple[str, int]:
        """
        修復一行中的 Unicode 符號
        返回 (修復後的行, 替換次數)
        """
        result = []
        replacements = 0
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # 優先處理標點符號 (不需要數學模式)
            if char in self.UNICODE_PUNCTUATION:
                result.append(self.UNICODE_PUNCTUATION[char])
                replacements += 1
            # 處理數學符號 (需要數學模式)
            elif char in self.UNICODE_TO_LATEX:
                # 檢查是否已在數學模式內
                text_before = ''.join(result)
                in_math = self.check_if_in_math_mode(text_before)
                
                latex_cmd = self.UNICODE_TO_LATEX[char]
                
                if in_math:
                    # 已在數學模式內,直接使用命令
                    result.append(latex_cmd)
                else:
                    # 不在數學模式內,需要加上 $ $
                    result.append(f'${latex_cmd}$')
                
                replacements += 1
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result), replacements
    
    def fix_file(self, output_file: Path = None) -> Dict:
        """
        修復整個檔案
        返回統計資訊
        """
        # 備份原檔案
        if self.backup and not output_file:
            backup_file = self.tex_file.with_suffix(self.tex_file.suffix + '.backup')
            shutil.copy2(self.tex_file, backup_file)
            print(f"Backup created: {backup_file}")
        
        # 讀取原檔案
        content = self.tex_file.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True)
        
        # 修復每一行
        fixed_lines = []
        total_replacements = 0
        lines_modified = 0
        
        for line_num, line in enumerate(lines, start=1):
            fixed_line, replacements = self.fix_line(line)
            fixed_lines.append(fixed_line)
            
            if replacements > 0:
                total_replacements += replacements
                lines_modified += 1
        
        # 寫入結果
        output_path = output_file if output_file else self.tex_file
        output_path.write_text(''.join(fixed_lines), encoding='utf-8')
        
        stats = {
            'input_file': str(self.tex_file),
            'output_file': str(output_path),
            'total_replacements': total_replacements,
            'lines_modified': lines_modified,
            'total_lines': len(lines)
        }
        
        return stats
    
    def preview_changes(self, max_lines: int = 20) -> str:
        """
        預覽將要進行的變更 (不實際修改檔案)
        """
        content = self.tex_file.read_text(encoding='utf-8')
        lines = content.splitlines()
        
        preview = []
        preview.append("=" * 80)
        preview.append(f"Preview of changes for: {self.tex_file}")
        preview.append("=" * 80)
        preview.append("")
        
        changes_shown = 0
        for line_num, original_line in enumerate(lines, start=1):
            fixed_line, replacements = self.fix_line(original_line)
            
            if replacements > 0 and changes_shown < max_lines:
                preview.append(f"Line {line_num}:")
                preview.append(f"  BEFORE: {original_line[:100]}")
                preview.append(f"  AFTER:  {fixed_line[:100]}")
                preview.append("")
                changes_shown += 1
        
        if changes_shown == 0:
            preview.append("No changes needed!")
        elif changes_shown >= max_lines:
            preview.append(f"... (showing first {max_lines} changes)")
        
        return "\n".join(preview)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix Unicode glitches in LaTeX files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes
  python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex --preview
  
  # Fix in place (creates backup)
  python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex
  
  # Fix and save to new file
  python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex -o survey_fixed.tex
  
  # Fix without creating backup
  python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex --no-backup
        """
    )
    parser.add_argument('tex_file', type=Path, help='Path to the .tex file')
    parser.add_argument('-o', '--output', type=Path, help='Output file (default: overwrite input)')
    parser.add_argument('--no-backup', action='store_true', help='Do not create backup file')
    parser.add_argument('--preview', action='store_true', help='Preview changes without modifying file')
    
    args = parser.parse_args()
    
    if not args.tex_file.exists():
        print(f"Error: File not found: {args.tex_file}")
        sys.exit(1)
    
    fixer = UnicodeGlitchFixer(args.tex_file, backup=not args.no_backup)
    
    if args.preview:
        print(fixer.preview_changes())
    else:
        stats = fixer.fix_file(args.output)
        
        print("\n" + "=" * 80)
        print("Unicode Glitch Fix Summary")
        print("=" * 80)
        print(f"Input file:         {stats['input_file']}")
        print(f"Output file:        {stats['output_file']}")
        print(f"Total lines:        {stats['total_lines']}")
        print(f"Lines modified:     {stats['lines_modified']}")
        print(f"Total replacements: {stats['total_replacements']}")
        print("=" * 80)
        
        if stats['total_replacements'] > 0:
            print(f"\n✓ Successfully fixed {stats['total_replacements']} Unicode symbols!")
        else:
            print("\n✓ No Unicode symbols found. File is clean!")


if __name__ == '__main__':
    main()
