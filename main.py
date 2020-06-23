import streamlit as st
import pandas as pd
import line_extraction as line

df = pd.concat(line.load_dataframe())
st.write(df)