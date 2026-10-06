import docx

doc = docx.Document('ITR.report...docx')

# Let's inspect sections between page breaks
current_block = []
block_idx = 1
for i, p in enumerate(doc.paragraphs):
    xml = p._p.xml
    current_block.append((i, p.text))
    if 'w:br' in xml and 'type="page"' in xml:
        print(f"\n--- PAGE BLOCK {block_idx} ({len(current_block)} paras) ---")
        for p_i, txt in current_block:
            if txt.strip():
                print(f"  [{p_i}] {txt[:70]}")
        current_block = []
        block_idx += 1

print(f"\n--- PAGE BLOCK {block_idx} ({len(current_block)} paras) ---")
for p_i, txt in current_block:
    if txt.strip():
        print(f"  [{p_i}] {txt[:70]}")
