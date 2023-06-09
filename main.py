from daylio import Daylio
import streamlit as st

dy = Daylio('data/daylio_export_2023_06_04.csv')
print(dy.data.keys())
dy.get_activ()

figs = []
figs.append(dy.mood_plot())
figs.append(dy.calendar_plot('activities', phrase="Music"))
figs.append(dy.calendar_plot('activities', phrase="Skateboarding"))
figs.append(dy.calendar_plot('activities', phrase="Drugs"))
figs.append(dy.calendar_plot('activities', phrase="friends"))
figs.append(dy.calendar_plot('activities', phrase="family"))

for fig in figs:
    st.plotly_chart(fig)


