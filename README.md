# langchain-text-splitters

PDF, DOCX, XLSXのそれぞれのテキスト化についての調査結果です。

## 前提
PDF、DOCX、XLSXなどのファイルからテキストを抽出するだけであれば、使用するライブラリの選択肢も多く、比較的簡単です。しかし、今回の要件として、抽出したテキストと共に"ファイル名"、"ページ番号"、"シート名"、"行番号"（必要な場合）をセットで表示する必要があります。ただテキスト化するだけでは、この要件を満たすことはできません。

もしテキスト化の段階でこの情報を追跡できなければ、後から特定のチャンクのテキストに関連するロケーション情報を得るためには、再度元のファイル（PDF、DOCX、XLSX）を読み込み、チャンク番号を基に特定する必要があります。これは非常に非効率です。

したがって、テキスト化する際には、先に述べたロケーション情報を追跡可能な状態でファイルを読み込む必要があります。それに対応できるライブラリを事前に選定することが重要です。

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
