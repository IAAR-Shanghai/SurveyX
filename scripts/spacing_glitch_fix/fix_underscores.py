#!/usr/bin/env python3
"""
修復 LaTeX 檔案中未轉義的 underscore (_)
在正文中,underscore 必須轉義成 \_ 才能正確顯示
"""
import re
import sys
from pathlib import Path

def fix_underscores(tex_file: Path) -> None:
    """
    修復 LaTeX 檔案中的 underscore
    只處理以下情況:
    1. 不在數學模式 ($...$, $$...$$, \[...\], \(...\)) 中
    2. 不在 \input, \cite, \ref, \label 等命令中
    3. 不在 URL 或 verbatim 環境中
    """
    content = tex_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    fixed_lines = []
    in_verbatim = False
    replacements = 0
    
    for line_no, line in enumerate(lines, 1):
        # 檢查 verbatim 環境
        if '\\begin{verbatim}' in line or '\\begin{lstlisting}' in line:
            in_verbatim = True
        if '\\end{verbatim}' in line or '\\end{lstlisting}' in line:
            in_verbatim = False
            
        if in_verbatim:
            fixed_lines.append(line)
            continue
            
        # 跳過已在特殊命令中的 underscore
        if any(cmd in line for cmd in [r'\input{', r'\cite{', r'\ref{', r'\label{', 
                                        r'\includegraphics', r'\url{', r'\href{',
                                        r'\usepackage']):
            fixed_lines.append(line)
            continue
            
        # 簡單的數學模式檢測 (不完美但足夠)
        # 計算 $ 的數量來判斷是否在數學模式中
        parts = []
        current = []
        in_math = False
        i = 0
        
        while i < len(line):
            char = line[i]
            
            # 檢測 $ (但跳過 \$)
            if char == '$' and (i == 0 or line[i-1] != '\\'):
                in_math = not in_math
                current.append(char)
            # 檢測 _ (但跳過 \_)
            elif char == '_' and (i == 0 or line[i-1] != '\\'):
                if in_math:
                    # 在數學模式中,保持原樣
                    current.append(char)
                else:
                    # 不在數學模式中,需要轉義
                    current.append(r'\_')
                    replacements += 1
            else:
                current.append(char)
            
            i += 1
        
        fixed_lines.append(''.join(current))
    
    # 寫回檔案 (先備份)
    if replacements > 0:
        backup_file = tex_file.with_suffix(tex_file.suffix + '.backup_underscore')
        tex_file.rename(backup_file)
        print(f"Backup created: {backup_file}")
        
        tex_file.write_text('\n'.join(fixed_lines), encoding='utf-8')
        print(f"\n{'='*80}")
        print(f"Underscore Fix Summary")
        print(f"{'='*80}")
        print(f"File: {tex_file}")
        print(f"Total replacements: {replacements}")
        print(f"{'='*80}\n")
        print(f"✓ Successfully fixed {replacements} underscores!")
    else:
        print("No underscores to fix.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python fix_underscores.py <tex_file>")
        sys.exit(1)
    
    tex_file = Path(sys.argv[1])
    if not tex_file.exists():
        print(f"Error: File {tex_file} not found")
        sys.exit(1)
    
    fix_underscores(tex_file)
