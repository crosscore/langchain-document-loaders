import fitz

def inspect_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Document metadata: {doc.metadata}")

    for i in range(len(doc)):
        page = doc[i]
        print(f"Page {i}:")
        print(f"  Dictionary: {page.get_text('dict')}")
    doc.close()

inspect_pdf("../data/input/pdf/page_test.pdf")
