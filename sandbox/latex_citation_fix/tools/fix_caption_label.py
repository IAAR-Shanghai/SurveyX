#!/usr/bin/env python3
"""
修復 LaTeX 圖檔中 caption 和 label 的格式問題
確保 label 與 caption 之間有換行
"""

import re
import sys
from pathlib import Path

def fix_caption_label_spacing(tex_file: Path) -> bool:
    """
    修復 caption 和 label 之間的空格/換行問題
    
    Args:
        tex_file: LaTeX 圖檔路徑
        
    Returns:
        是否有進行修改
    """
    content = tex_file.read_text(encoding='utf-8')
    original = content
    
    # Pattern: \caption{...} 後面有任意空白字符，然後是 \label{...}
    # 將它們之間的空白替換為單一換行
    pattern = r'(\\caption\{[^}]*\})\s+(\\label\{[^}]+\})'
    
    def replace_func(match):
        caption = match.group(1)
        label = match.group(2)
        return f'{caption}\n{label}'
    
    content = re.sub(pattern, replace_func, content)
    
    if content != original:
        tex_file.write_text(content, encoding='utf-8')
        print(f"✅ 已修復: {tex_file.name}")
        return True
    else:
        print(f"⏭️  無需修改: {tex_file.name}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_caption_label.py <tex_file1> [tex_file2] ...")
        sys.exit(1)
    
    fixed_count = 0
    for filepath in sys.argv[1:]:
        tex_file = Path(filepath)
        if not tex_file.exists():
            print(f"❌ 檔案不存在: {filepath}")
            continue
        
        if fix_caption_label_spacing(tex_file):
            fixed_count += 1
    
    print(f"\n🎉 總共修復 {fixed_count} 個檔案")

if __name__ == "__main__":
    main()
