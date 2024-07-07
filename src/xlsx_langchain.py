import os
from langchain_community.document_loaders import UnstructuredExcelLoader

input_file = "../data/docx/test.docx"
file_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = f"../data/csv/{file_name}_text.csv"

loader = UnstructuredExcelLoader(input_file)
docs = loader.load()
print(docs)
