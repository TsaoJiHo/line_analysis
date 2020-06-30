# LINE 聊天紀錄分析

## Iphone IOS :

LINE 聊天頁面右上角選單 -> 其他設定 -> 傳送聊天紀錄 -> 傳送 `[LINE] XXX的聊天.txt`

## Windows :

requirement : 
```
pip install streamlit
pip install pandas
pip install pathlib
pip install plotly
pip install jieba
pip install wordcloud
pip install matplotlib
```
將 `[LINE] XXX的聊天.txt` 放置於 `data` 資料夾

在檔案目錄下依序執行指令
```
python line_to_dataframe.py
streamlit run main.py
```
