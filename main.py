from daylio import Daylio
import streamlit as st

dy = Daylio('data/daylio_export_2023_06_30.csv')

st.title('Daylio Mood Tracker Analysis')

st.header('Mood Trend over Time')
st.radio('Timescale', ['Month', 'Year', 'All'], horizontal=True, label_visibility='hidden')
activity_groups = list(dy.activity_groups)
activity_groups.append('mood')
activity_groups.reverse()
selected_group = st.selectbox('Select Activity', activity_groups)
st.plotly_chart(dy.time_plot(selected_group))

st.header('Activities Record')
cal_option = st.selectbox('Select Activity', dy.activities_culled)
st.plotly_chart(dy.calendar_plot(cal_option))

st.header('Chi-Square Significance Test')
col5, col1, col2, col3, col4 = st.columns([0.1, 0.25, 0.2, 0.05, 0.2])
with col1:
    st.write('')
    st.write('')
    st.write('Find the significance between ')
with col2:
    option_a1 = st.selectbox('First Activity', dy.activities, label_visibility='hidden')
with col3:
    st.write('')
    st.write('')
    st.write(' and ')
with col4:
    option_a2 = st.selectbox('Second Activity', ['mood'], label_visibility='hidden')

chi2, p_value, dof, judgement = dy.chi_square(option_a1, option_a2)
st.write('$\chi^2$ value: ' + str(round(chi2, 2)) )
st.write('p value: ' + str(round(p_value, 2)))
st.write('degrees of freedom: ' + str(dof))
st.write('The correlation between ' + option_a1 +' and ' + option_a2 + ' is ' + judgement + '.')


