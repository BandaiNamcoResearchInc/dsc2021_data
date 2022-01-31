[![Attribution-NonCommercial 4.0 International](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)
# データサイエンスチャレンジ2021 正解データ＆採点スクリプト

## 概要
- [データサイエンスチャレンジ2021](https://athletix.run/challenges/MQe8jPDRp)の採点スクリプトです。
- correct\_answerフォルダに正解データ(csv)が格納されており、judge.pyで採点が可能です。

## 実行方法
- 作成したZIPファイルをルートディレクトリ下に配置します。
- 実行環境について、以下を実行します。
```
pip install -r requirements.txt
```
- ZIPファイル名とスコアの種類（public, private）を引数に指定し、judge.pyを実行します。
- 以下はサンプルの実行例です。
```
# python judge.py {ファイル名} {(public, private)}

# 暫定スコア(Public Score)の計算
python judge.py sample.zip public

# 最終スコア(Private Score)の計算
python judge.py sample.zip private 
``` 