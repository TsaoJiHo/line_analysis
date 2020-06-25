import streamlit as st
import pandas as pd
import line_to_dataframe as line

def main():
    # load dataframe
    dfs = line.load_dataframe()
    choice = st.sidebar.selectbox("select", [x for x in dfs])
    df = dfs[choice]

    # show total time
    st.write(df['date'][0])
    st.write(df['date'][len(df)-1])

    st.write(df)

if __name__ == '__main__':
    main()