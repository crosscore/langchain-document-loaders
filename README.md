# langchain-text-splitters

PDF, DOCX, XLSXのそれぞれのテキスト化についての調査結果です。

## 前提
PDF, DOCX, XLSX, それぞれの拡張子からテキストを抽出することだけを目標とする場合、ライブラリの制約なども比較的自由度が高く簡単です。ただし、テキスト化するだけでは、今回の要件（チャンクに対応する"ファイル名"、"ページ番号"、"シート名"、"行番号"(必要な場合)のセット表示が必要）を満たすことができないことに留意する必要があります。

なぜなら、抽出したテキスト情報のみが存在する場合、そのテキストがどのロケーション(ページ番号、シート名)に存在したかを後から追跡できなくなるためです。

テキスト化の時点で、この情報を追跡できなかった場合、後から特定のチャンクのテキストに関連するロケーション情報を得るには、再度元のファイル(PDF, DOCX, XLSX)を読み込み、チャンク番号から特定する必要があります。これは極めて非効率です。

そのため、テキスト化の際には、先に述べたロケーション情報を追跡可能な状態で、それぞれのファイルを読み込む必要があり、それに対応可能なライブラリを事前に特定する必要があります。

## docxのテキスト化
python-docx: 直接的にページ区切りを検出する機能を提供していないためページの特定が不可能

docx2txt:

## xlsxのテキスト化

結論：langchainのライブラリ(UnstructuredExcelLoader)とpandasを試し、UnstructuredExcelLoader内でpandasが利用されていることが判りました。最終的にpandasのみで目的の出力が得られました。

### from langchain_community.document_loaders import UnstructuredExcelLoaderの検証

単独では動作せず、以下のライブラリの追加インストールが求められました。
```
unstructured
networkx
psutil
```

インストール後、以下のエラーが発生しました。
```
raise OptionError(f"No such keys(s): {repr(pat)}")
pandas._config.config.OptionError: No such keys(s): 'io.excel.zip.reader'
```
バージョン関連のエラーの可能性があります。また、UnstructuredExcelLoaderの内部でPandasを利用していることが判明しました。

### pandas(2.2.2)の検証
追加ライブラリのインストールが不要です。

XLSXから、"ファイル名、"シート名"、"行番号"、"テキスト"、全てが取得できました。

```
file_name,location,line_number,text
animal_faq.xlsx,犬のFAQ,1,質問 回答
animal_faq.xlsx,犬のFAQ,2,小型犬の代表的な種類は何ですか？ 小型犬の代表的な種類には、チワワ、ポメラニアン、ダックスフントなどがあります。
animal_faq.xlsx,犬のFAQ,3,中型犬の特徴は何ですか？ 中型犬には、ビーグル、柴犬、コッカースパニエルなどがあります。
animal_faq.xlsx,犬のFAQ,4,大型犬の代表的な種類と特徴は？ 大型犬には、ゴールデンレトリバー、ラブラドールレトリバー、ジャーマンシェパードなどがあります。
animal_faq.xlsx,猫のFAQ,1,質問 回答
animal_faq.xlsx,猫のFAQ,2,短毛種の猫の特徴は何ですか？ 短い被毛のため毛玉ができにくく、グルーミングが比較的容易です。
animal_faq.xlsx,猫のFAQ,3,長毛種の猫の代表的な種類は？ 代表的な長毛種には、ペルシャ、メインクーン、ラグドールなどがあります。
animal_faq.xlsx,猫のFAQ,4,特殊な被毛を持つ猫の例を教えてください。 特殊被毛の猫には、スフィンクス（無毛）、レックス（波状毛）、スコティッシュフォールド（折れ耳）などがあります。
```
