#!/usr/bin/env python3
"""檢查 LaTeX 檔案中的特殊 Unicode 字元"""

import sys
from pathlib import Path

tex_file = Path('outputs/2025-10-09-1630_speec/latex/survey.tex')
content = tex_file.read_text(encoding='utf-8')

# 檢查各種特殊字元
special_chars = {
    '\u2011': 'NON-BREAKING HYPHEN (U+2011)',
    '\u2013': 'EN DASH (U+2013)', 
    '\u2014': 'EM DASH (U+2014)',
    '\u2018': 'LEFT SINGLE QUOTATION MARK (U+2018)',
    '\u2019': 'RIGHT SINGLE QUOTATION MARK (U+2019)',
    '\u201C': 'LEFT DOUBLE QUOTATION MARK (U+201C)',
    '\u201D': 'RIGHT DOUBLE QUOTATION MARK (U+201D)',
    '\u2026': 'HORIZONTAL ELLIPSIS (U+2026)',
    '\u00A0': 'NO-BREAK SPACE (U+00A0)',
}

print('特殊 Unicode 字元統計:')
print('=' * 70)
for char, name in special_chars.items():
    count = content.count(char)
    if count > 0:
        print(f'{repr(char)} {name}: {count} 次')
        # 顯示前 5 個出現位置的行號
        lines = content.split('\n')
        occurrences = []
        for i, line in enumerate(lines, 1):
            if char in line:
                occurrences.append(i)
                if len(occurrences) >= 5:
                    break
        print(f'  出現在行: {occurrences[:5]}')
        print()

print('=' * 70)
print(f'總計發現問題字元: {sum(1 for c in special_chars if content.count(c) > 0)} 種')
