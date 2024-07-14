import fitz

TEXT_BLOCK = 0
IMAGE_BLOCK = 1

def get_page_numbers(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Document has {len(doc)} pages")

    for i in range(len(doc)):
        page = doc[i]
        page_dict = page.get_text('dict')

        logical_num = None
        for block in reversed(page_dict['blocks']):
            if block['type'] == TEXT_BLOCK:
                for line in reversed(block['lines']):
                    for span in reversed(line['spans']):
                        text = span['text'].strip()
                        if text.isdigit():
                            logical_num = text
                            break
                    if logical_num:
                        break
            if logical_num:
                break

        print(f"物理ページ: {i}, 論理ページ: {logical_num if logical_num else '不明'}")
    doc.close()

get_page_numbers("../data/input/pdf/page_test.pdf")
