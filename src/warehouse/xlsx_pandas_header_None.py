import pandas as pd
import os

def convert_xlsx_to_dataframe(input_file, output_file):
    # エクセルファイルの全シートを読み込む
    xlsx = pd.ExcelFile(input_file)

    # 結果を格納するリスト
    results = []

    # ファイル名を取得
    file_name = os.path.basename(input_file)

    # 各シートを処理
    for sheet_name in xlsx.sheet_names:
        # シートをDataFrameとして読み込む
        df = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)

        # 各行を処理
        for index, row in df.iterrows():
            # 非空の列のみを結合してテキスト内容を作成
            text_content = ' '.join(row.dropna().astype(str))

            # 結果をリストに追加
            results.append({
                'file_name': file_name,
                'location': sheet_name,
                'line_number': index + 1,  # headerは1から始まるので+1
                'text': text_content
            })

    # 結果をDataFrameに変換
    result_df = pd.DataFrame(results)

    # CSVファイルとして保存
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"変換が完了しました。出力は {output_file} に保存されました。")
    return result_df

input_file = "../data/xlsx/animal_faq.xlsx"
file_name = os.path.splitext(os.path.basename(input_file))[0]
output_file = f"../data/csv/{file_name}_header_None.csv"

df = convert_xlsx_to_dataframe(input_file, output_file)
print(df.head())  # 結果の最初の数行を表示
