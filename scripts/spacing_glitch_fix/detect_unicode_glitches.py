#!/usr/bin/env python3
"""
偵測 PDF 中的 spacing glitch 以及對應的 LaTeX 原始碼位置
"""
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

FILE_PATH = Path(__file__).absolute()
BASE_DIR = FILE_PATH.parent.parent
sys.path.insert(0, str(BASE_DIR))


class UnicodeGlitchDetector:
    """偵測 LaTeX 檔案中的 Unicode 數學符號問題"""
    
    # Unicode 數學符號對應的 LaTeX 巨集
    UNICODE_TO_LATEX = {
        # 特殊標點符號 (會導致 spacing glitch)
        '\u2011': r'-',  # NON-BREAKING HYPHEN → 普通連字號
        '\u2013': r'--',  # EN DASH → LaTeX en-dash
        '\u2014': r'---',  # EM DASH → LaTeX em-dash
        '\u2018': r"`",  # LEFT SINGLE QUOTATION MARK
        '\u2019': r"'",  # RIGHT SINGLE QUOTATION MARK
        '\u201C': r"``",  # LEFT DOUBLE QUOTATION MARK
        '\u201D': r"''",  # RIGHT DOUBLE QUOTATION MARK
        '\u2026': r'\ldots',  # HORIZONTAL ELLIPSIS
        '\u00A0': r' ',  # NO-BREAK SPACE → 普通空格
        # 數學符號
        '∈': r'$\in$',
        '∉': r'$\notin$',
        '≈': r'$\approx$',
        '≠': r'$\neq$',
        '≤': r'$\le$',
        '≥': r'$\ge$',
        '≪': r'$\ll$',
        '≫': r'$\gg$',
        '∼': r'$\sim$',
        '≃': r'$\simeq$',
        '≅': r'$\cong$',
        '−': r'$-$',
        '×': r'$\times$',
        '÷': r'$\div$',
        '±': r'$\pm$',
        '∓': r'$\mp$',
        '∞': r'$\infty$',
        '∑': r'$\sum$',
        '∏': r'$\prod$',
        '∫': r'$\int$',
        '∂': r'$\partial$',
        '∇': r'$\nabla$',
        '√': r'$\sqrt{}$',
        '∝': r'$\propto$',
        '∀': r'$\forall$',
        '∃': r'$\exists$',
        '∧': r'$\wedge$',
        '∨': r'$\vee$',
        '¬': r'$\neg$',
        '⇒': r'$\Rightarrow$',
        '⇐': r'$\Leftarrow$',
        '⇔': r'$\Leftrightarrow$',
        '→': r'$\rightarrow$',
        '←': r'$\leftarrow$',
        '↔': r'$\leftrightarrow$',
        # 希臘字母
        'α': r'$\alpha$',
        'β': r'$\beta$',
        'γ': r'$\gamma$',
        'δ': r'$\delta$',
        'ε': r'$\epsilon$',
        'ζ': r'$\zeta$',
        'η': r'$\eta$',
        'θ': r'$\theta$',
        'ι': r'$\iota$',
        'κ': r'$\kappa$',
        'λ': r'$\lambda$',
        'μ': r'$\mu$',
        'ν': r'$\nu$',
        'ξ': r'$\xi$',
        'ο': r'$o$',
        'π': r'$\pi$',
        'ρ': r'$\rho$',
        'σ': r'$\sigma$',
        'τ': r'$\tau$',
        'υ': r'$\upsilon$',
        'φ': r'$\phi$',
        'χ': r'$\chi$',
        'ψ': r'$\psi$',
        'ω': r'$\omega$',
        'Α': r'$A$',
        'Β': r'$B$',
        'Γ': r'$\Gamma$',
        'Δ': r'$\Delta$',
        'Ε': r'$E$',
        'Ζ': r'$Z$',
        'Η': r'$H$',
        'Θ': r'$\Theta$',
        'Ι': r'$I$',
        'Κ': r'$K$',
        'Λ': r'$\Lambda$',
        'Μ': r'$M$',
        'Ν': r'$N$',
        'Ξ': r'$\Xi$',
        'Ο': r'$O$',
        'Π': r'$\Pi$',
        'Ρ': r'$P$',
        'Σ': r'$\Sigma$',
        'Τ': r'$T$',
        'Υ': r'$\Upsilon$',
        'Φ': r'$\Phi$',
        'Χ': r'$X$',
        'Ψ': r'$\Psi$',
        'Ω': r'$\Omega$',
    }
    
    def __init__(self, tex_file: Path):
        self.tex_file = Path(tex_file)
        self.content = self.tex_file.read_text(encoding='utf-8')
        self.lines = self.content.splitlines()
        
    def detect_unicode_symbols(self) -> List[Dict]:
        """偵測所有 Unicode 數學符號及其位置"""
        issues = []
        
        for line_num, line in enumerate(self.lines, start=1):
            for char in line:
                if char in self.UNICODE_TO_LATEX:
                    # 找出該字元在行中的所有位置
                    col_positions = [i for i, c in enumerate(line) if c == char]
                    for col_pos in col_positions:
                        # 取得上下文 (前後 40 字元)
                        start = max(0, col_pos - 40)
                        end = min(len(line), col_pos + 40)
                        context = line[start:end]
                        
                        issues.append({
                            'line': line_num,
                            'column': col_pos,
                            'char': char,
                            'latex_replacement': self.UNICODE_TO_LATEX[char],
                            'context': context,
                            'full_line': line
                        })
        
        return issues
    
    def analyze_glitch_patterns(self, issues: List[Dict]) -> Dict:
        """分析 glitch 模式"""
        if not issues:
            return {
                'total': 0, 
                'by_symbol': {}, 
                'by_line': {},
                'unique_symbols': 0,
                'affected_lines': 0
            }
        
        by_symbol = {}
        by_line = {}
        
        for issue in issues:
            char = issue['char']
            line = issue['line']
            
            by_symbol[char] = by_symbol.get(char, 0) + 1
            by_line[line] = by_line.get(line, 0) + 1
        
        return {
            'total': len(issues),
            'by_symbol': dict(sorted(by_symbol.items(), key=lambda x: x[1], reverse=True)),
            'by_line': dict(sorted(by_line.items(), key=lambda x: x[1], reverse=True)),
            'unique_symbols': len(by_symbol),
            'affected_lines': len(by_line)
        }
    
    def check_if_in_math_mode(self, line: str, col_pos: int) -> bool:
        """檢查該位置是否已在數學模式內 (簡單檢查)"""
        before = line[:col_pos]
        
        # 檢查是否在 $ ... $ 或 \( ... \) 或 equation 環境內
        dollar_count = before.count('$') - before.count(r'\$')
        if dollar_count % 2 == 1:
            return True
        
        # 檢查是否在 \begin{equation} 等環境內
        math_envs = ['equation', 'align', 'gather', 'multline', 'displaymath']
        for env in math_envs:
            begin_count = before.count(f'\\begin{{{env}}}')
            end_count = before.count(f'\\end{{{env}}}')
            if begin_count > end_count:
                return True
        
        return False
    
    def generate_report(self, output_file: Path = None) -> str:
        """生成完整報告"""
        issues = self.detect_unicode_symbols()
        analysis = self.analyze_glitch_patterns(issues)
        
        report = []
        report.append("=" * 80)
        report.append(f"Unicode Glitch Detection Report")
        report.append(f"File: {self.tex_file}")
        report.append("=" * 80)
        report.append("")
        
        # 摘要
        report.append("## Summary")
        report.append(f"Total Unicode symbols found: {analysis['total']}")
        report.append(f"Unique symbol types: {analysis['unique_symbols']}")
        report.append(f"Affected lines: {analysis['affected_lines']}")
        report.append("")
        
        # 按符號統計
        if analysis['by_symbol']:
            report.append("## Frequency by Symbol")
            for symbol, count in list(analysis['by_symbol'].items())[:20]:
                latex_rep = self.UNICODE_TO_LATEX.get(symbol, '?')
                report.append(f"  {symbol} ({latex_rep}): {count} occurrences")
            report.append("")
        
        # 列出前 50 個問題位置
        if issues:
            report.append("## Detected Issues (first 50)")
            for i, issue in enumerate(issues[:50], start=1):
                in_math = self.check_if_in_math_mode(issue['full_line'], issue['column'])
                math_status = " [ALREADY IN MATH MODE]" if in_math else ""
                report.append(f"\n{i}. Line {issue['line']}, Column {issue['column']}{math_status}")
                report.append(f"   Symbol: {issue['char']} → {issue['latex_replacement']}")
                report.append(f"   Context: ...{issue['context']}...")
        
        report_text = "\n".join(report)
        
        if output_file:
            output_file.write_text(report_text, encoding='utf-8')
            print(f"Report saved to: {output_file}")
        
        return report_text


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Detect Unicode glitches in LaTeX files')
    parser.add_argument('tex_file', type=Path, help='Path to the .tex file')
    parser.add_argument('-o', '--output', type=Path, help='Output report file')
    
    args = parser.parse_args()
    
    if not args.tex_file.exists():
        print(f"Error: File not found: {args.tex_file}")
        sys.exit(1)
    
    detector = UnicodeGlitchDetector(args.tex_file)
    report = detector.generate_report(args.output)
    
    if not args.output:
        print(report)


if __name__ == '__main__':
    main()
