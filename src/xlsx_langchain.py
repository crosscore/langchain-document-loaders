import os
import json
from langchain_community.document_loaders import UnstructuredExcelLoader

def convert_xlsx_to_txt_and_json(xlsx_path, txt_output_path, json_output_path):
    try:
        # XLSXローダーを初期化
        loader = UnstructuredExcelLoader(xlsx_path, mode="elements")

        # XLSXを読み込む
        elements = loader.load()

        # テキストファイルに書き込む
        with open(txt_output_path, 'w', encoding='utf-8') as f:
            for element in elements:
                f.write(element.page_content + '\n\n')

        print(f"テキストが {txt_output_path} に保存されました。")

        # JSONデータを作成
        json_data = {
            "file_name": os.path.basename(xlsx_path),
            "content": [
                {
                    "page_content": element.page_content,
                    "metadata": element.metadata
                } for element in elements
            ]
        }

        # JSONファイルに書き込む
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(f"JSONが {json_output_path} に保存されました。")

    except Exception as e:
        print(f"エラーが発生しました: {xlsx_path}")
        print(f"エラー詳細: {str(e)}")

def process_all_xlsx(input_folder, txt_output_folder, json_output_folder):
    if not os.path.exists(txt_output_folder):
        os.makedirs(txt_output_folder)
    if not os.path.exists(json_output_folder):
        os.makedirs(json_output_folder)

    # 入力フォルダ内のすべてのXLSXファイルを処理
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.xlsx'):
            xlsx_path = os.path.join(input_folder, filename)
            base_filename = os.path.splitext(filename)[0]
            txt_filename = base_filename + '.txt'
            json_filename = base_filename + '.json'
            txt_output_path = os.path.join(txt_output_folder, txt_filename)
            json_output_path = os.path.join(json_output_folder, json_filename)

            print(f"処理中: {filename}")
            convert_xlsx_to_txt_and_json(xlsx_path, txt_output_path, json_output_path)

if __name__ == "__main__":
    xlsx_path = "../data/input/xlsx"
    txt_output_path = "../data/output/txt/xlsx"
    json_output_path = "../data/output/json/xlsx"

    process_all_xlsx(xlsx_path, txt_output_path, json_output_path)
    print("すべてのXLSXファイルの処理が完了しました。")
