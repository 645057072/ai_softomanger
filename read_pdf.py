# -*- coding: utf-8 -*-
import pdfplumber

pdf_path = r"g:\AI_CASE\ai_softomanger\生成式AI工程师（高级）理论模拟题.pdf"

pages_to_read = [2, 3, 78, 79, 157, 158]

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"PDF总页数: {total_pages}")
    print("=" * 80)
    
    for page_num in pages_to_read:
        if page_num <= total_pages and page_num >= 1:
            page = pdf.pages[page_num - 1]
            text = page.extract_text()
            
            print(f"\n{'=' * 80}")
            print(f"第 {page_num} 页内容:")
            print("=" * 80)
            if text:
                print(text)
            else:
                print("[此页无法提取文本内容]")
            print("=" * 80)
        else:
            print(f"\n第 {page_num} 页不存在 (PDF总页数: {total_pages})")
