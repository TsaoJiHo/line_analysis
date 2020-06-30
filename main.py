import streamlit as st
import pandas as pd
import line_to_dataframe as line
import plotly.express as px
import plotly.graph_objects as go
import jieba
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def main():
    # load dataframe
    dfs = load_dataframe()
    choice = st.sidebar.selectbox('Select Dataset', [x for x in dfs])
    df = dfs[choice]

    # text filter
    text = st.sidebar.text_input('Word Filter')
    if text:
        df = df[df['text'].str.contains(text, na = False)]

    # part filter
    x = st.sidebar.slider('Show Partial Data', 0.0, 1.0, (0.0, 1.0), 0.1)
    start = int(x[0] * len(df))
    end = int(x[1] * len(df))
    df = df[start:end]

    # names selection
    names = list(df.groupby('name').groups)
    if len(names) > 2:
        is_group = True
    else:
        is_group = False
    if is_group:
        st.title(f'{choice} (群組)')
    else:
        st.title(choice)
    selected_names = st.sidebar.multiselect('Members', names, names)
    df = df[df['name'].isin(selected_names)]
    df = df.reset_index(drop=True)

    # show total time
    if not df.empty:
        # duration time
        start_date = df['date'][0].split('/')
        end_date = df['date'][len(df)-1].split('/')
        year = int(end_date[0]) - int(start_date[0])
        month = int(end_date[1]) - int(start_date[1])
        day = int(end_date[2][:2]) - int(start_date[2][:2])
        if day < 0:
            day += 30
            month -= 1
        if month < 0:
            month += 12
            year -= 1
        days = len(list(df.groupby('date').groups))
        st.subheader(f'📆 聊天持續 : {year} 年{month} 月{day} 天')
        st.subheader(f'📆 聊天天數 : {days} 天')
        st.title('訊息統計')
        st.subheader(f'💬 訊息總數 : {len(df)} 則')

    # plot message count by name
    d = {'name': [], '訊息數': []}
    names = df.groupby('name').groups
    for name in names:
        d['name'].append(name)
        d['訊息數'].append(len(df[df['name'] == name]))
    plot_df = pd.DataFrame(d)
    plot_df = plot_df.sort_values(by=['訊息數'], ascending=False)
    fig = px.bar(plot_df, y='訊息數', x='name', text='訊息數')
    fig.update_layout(title_text='訊息總數分佈')
    st.write(fig)

    # plot pie
    labels = ['訊息', '語音訊息', '貼圖', '照片', '影片', '通話']
    sound_text = len(df[df['text'].str.contains('[語音訊息]', na = False)])
    sticker = len(df[df['text'].str.contains('[貼圖]', na = False)])
    image = len(df[df['text'].str.contains('[照片]', na = False)])
    video = len(df[df['text'].str.contains('[影片]', na = False)])
    phone_call = len(df[df['text'].str.contains('☎', na = False)])
    text = len(df) - sound_text - sticker - image - video - phone_call
    values = [text, sound_text, sticker, image, video, phone_call]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout(title_text='訊息比例')
    st.write(fig)

    # plot message count by date
    d = {'name':[], 'date': [], '訊息數': []}
    dates = df.groupby('date').groups
    for date in dates:
        for name in names:
            d['name'].append(name)
            d['date'].append(date)
            filter1 = df['date'] == date
            filter2 = df['name'] == name
            d['訊息數'].append(len(df[filter1][filter2]))
    plot_df = pd.DataFrame(d)
    if not plot_df.empty:
        fig = px.line(plot_df, x='date', y='訊息數', color='name')
        fig.update_layout(title_text='每日訊息總數 by Members')
        st.write(fig)

    d = {'date': [], '訊息數': []}
    dates = df.groupby('date').groups
    for date in dates:
        d['date'].append(date)
        filter = df['date'] == date
        d['訊息數'].append(len(df[filter]))
    plot_df = pd.DataFrame(d)
    fig = px.line(plot_df, x='date', y='訊息數')
    fig.update_layout(title_text='每日訊息總數 in Total')
    st.write(fig)
    
    # talk time
    if not df.empty:
        talk_df = df[df['text'].str.contains('☎ 通話時間', na = False)]
        hour = 0
        minute = 0
        second = 0
        for time in talk_df['text']:
            time = time.replace('☎ 通話時間', '').split(':')
            if len(time) == 2:
                minute += int(time[0])
                second += int(time[1])
            elif len(time) == 3:
                hour += int(time[0])
                minute += int(time[1])
                second += int(time[2])
        if second >= 60:
            minute += int(second / 60)
            second %= 60
        if minute >= 60:
            hour += int(minute / 60)
            minute %= 60
        st.title('通話統計')
        st.subheader(f'☎ 通話次數 : {len(talk_df)} 次')
        st.subheader(f'☎ 通話總長 : {hour} 時 {minute} 分 {second} 秒')
        # talk time plot
        d = {'name': [], '打給對方次數': [], '分鐘': []}
        names = talk_df.groupby('name').groups
        for name in names:
            d['name'].append(name)
            d['打給對方次數'].append(len(talk_df[talk_df['name'] == name]))
            hour = 0
            minute = 0
            second = 0
            for time in talk_df[talk_df['name'] == name]['text']:
                time = time.replace('☎ 通話時間', '').split(':')
                if len(time) == 2:
                    minute += int(time[0])
                    second += int(time[1])
                elif len(time) == 3:
                    hour += int(time[0])
                    minute += int(time[1])
                    second += int(time[2])
            minute += hour * 60 + int(second / 60)
            d['分鐘'].append(minute)
        plot_df = pd.DataFrame(d)
        fig = px.bar(plot_df, x='name', y='打給對方次數', text='打給對方次數')
        fig.update_layout(title_text='通話次數分佈')
        st.write(fig)
        fig = px.bar(plot_df, x='name', y='分鐘', text='分鐘')
        fig.update_layout(title_text='通話分鐘分佈')
        st.write(fig)
    d = {'date': [], '通話分鐘': []}
    dates = df.groupby('date').groups
    for date in dates:
        d['date'].append(date)
        filter = df['date'] == date
        hour = 0
        minute = 0
        second = 0
        for time in talk_df[talk_df['date'] == date]['text']:
            time = time.replace('☎ 通話時間', '').split(':')
            if len(time) == 2:
                minute += int(time[0])
                second += int(time[1])
            elif len(time) == 3:
                hour += int(time[0])
                minute += int(time[1])
                second += int(time[2])
        minute += hour * 60 + int(second / 60)
        d['通話分鐘'].append(minute)
    plot_df = pd.DataFrame(d)
    fig = px.line(plot_df, x='date', y='通話分鐘')
    fig.update_layout(title_text='每日通話分鐘')
    st.write(fig)

    # text plot
    def is_text(text):
        word_filter = ('[照片]', '[影片]', '[貼圖]', '[語音訊息]', '☎')
        for word in word_filter:
            if word in text:
                return False
        return True

    st.title('文字統計')
    for name in df.groupby('name').groups:
        word_count_2w = defaultdict(int)
        word_count_3w = defaultdict(int)
        df_groupby_name = df[df['name'] == name]
        for text in df_groupby_name['text']:
            text = str(text)
            if not is_text(text):
                continue
            seg_list = jieba.cut(text)
            for word in seg_list:
                if len(word) >= 2:
                    word_count_2w[word] += 1
                if len(word) >= 3:
                    word_count_3w[word] += 1
        sorted_word_count_2w = sorted(list(word_count_2w.items()), key=lambda x: -x[1])
        sorted_word_count_3w = sorted(list(word_count_3w.items()), key=lambda x: -x[1])
        words = set()
        for word in sorted_word_count_2w[:35]:
            words.add(word[0])
        for word in sorted_word_count_3w[:15]:
            words.add(word[0])
        font = 'SourceHanSansTW-Regular.otf'
        wordcloud = WordCloud(font_path=font).generate(' '.join(list(words)))
        plt.figure(figsize=(20,10), facecolor='k')
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.show()
        st.subheader(name)
        st.pyplot()

    # show data
    st.title('Data')
    st.write(df)

@st.cache
def load_dataframe():
    return line.load_dataframe()

if __name__ == '__main__':
    main()
