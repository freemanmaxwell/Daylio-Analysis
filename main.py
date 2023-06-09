from daylio import Daylio
import streamlit as st

dy = Daylio('data/daylio_export_2023_06_04.csv')

st.title('Daylio Mood Tracker Analysis')

st.header('Mood Trend over Time')

st.plotly_chart(dy.mood_plot())

st.header('Activities Record')

option = st.selectbox('Select Activity', dy.get_activ())
st.plotly_chart(dy.calendar_plot('activities', phrase=option))


