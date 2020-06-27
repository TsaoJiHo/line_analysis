import streamlit as st
import pandas as pd
import line_to_dataframe as line
import plotly.express as px

def main():
    # load dataframe
    dfs = line.load_dataframe()
    choice = st.sidebar.selectbox('Select Dataset', [x for x in dfs])
    df = dfs[choice]

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
        st.header(f'聊天持續 : {year} 年{month} 月{day} 天')
        st.header(f'聊天天數 : {days} 天')
        st.header(f'訊息總數 : {len(df)}')
        # phone time
        st.write(df[df['text'].str.contains('愛愛', na = False)])

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
    if len(names) > 2:
        st.write()

    # plot message count by date
    d = {'date': [], '訊息數': []}
    dates = df.groupby('date').groups
    for date in dates:
        d['date'].append(date)
        filter = df['date'] == date
        d['訊息數'].append(len(df[filter]))
    plot_df = pd.DataFrame(d)
    fig = px.line(plot_df, x='date', y='訊息數')
    fig.update_layout(title_text='每日訊息總數')
    st.write(fig)

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
        fig.update_layout(title_text='每日訊息總數')
        st.write(fig)

    st.title('Row Data')
    st.write(df)
    

if __name__ == '__main__':
    main()
