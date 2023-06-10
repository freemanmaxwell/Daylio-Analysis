import pandas as pd
import re
import csv
from plotly_calplot import calplot
import plotly.graph_objects as go
import numpy as np
from scipy.stats import chi2, chi2_contingency

moodDict = {
    'rad': 10,
    'good': 5,
    'meh': 0,
    'bad': -5,
    'awful': -10
}

red = '#FE978E'
green = '#B0CFB0'
gray = '#d3d3d3'

def chi_square_test(boolean_values, integer_values):
    # Get unique categories and sort them
    categories = sorted(list(set(integer_values)))

    # Construct the contingency table
    contingency_table = np.zeros((2, len(categories)), dtype=np.int64)

    for boolean, integer in zip(boolean_values, integer_values):
        boolean_index = 0 if boolean else 1
        integer_index = categories.index(integer)
        contingency_table[boolean_index, integer_index] += 1

    # Perform the chi-square test
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    # Print the results
    '''
    print("Chi-square statistic:", chi2)
    print("p-value:", p_value)
    print("Degrees of freedom:", dof)
    print("Expected frequencies:")
    print(expected)
    '''

    # Return the results as a tuple
    return chi2, p_value, dof, expected


class Daylio:
    def __init__(self, csv_file):

        # Open csv, save data in a dict with keys corresponding to the column names of the csv
        self.data = {}
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for column_name in reader.fieldnames:
                self.data[column_name.lower()] = []  # Initialize an empty list for each column
            for row in reader:
                for column_name, value in row.items():
                    self.data[column_name.lower()].append(value)  # Append column data to the list

        # Reformat the 'activities' data
        # First, get a list of all phrases in 'activities' column
        self.data['activities'] = [entry.lower() for entry in self.data['activities']]
        activity_set = set()
        for item in self.data['activities']:
            activities = item.split(' | ')
            for activity in activities:
                activity_set.update([activity])
        self.activities = list(activity_set)

        # Next, add these words as keys to a dict and populate each entry, update self.data
        act_dict = {}
        for activity in self.activities:
            act_dict[activity] = []
            for day in self.data['activities']:
                act_dict[activity].append(int(bool(re.search(r'\b' + activity + r'\b', day))))
        self.data['activities'] = act_dict

        self.data['mood'] = [moodDict[day] for day in self.data['mood']]

        self.data['full_date'] = pd.to_datetime(self.data['full_date'])

    def calendar_plot(self, activity):
        dates = self.data['full_date']
        events = pd.Series(self.data['activities'][activity], index=dates)
        df_log = pd.DataFrame({
            "dates": dates,
            "events": events,
        })

        fig = calplot(
            df_log,
            x="dates",
            y="events",
            name=activity,
            title=activity,
            years_title=True,
            dark_theme=False
        )
        return fig

    def mood_plot(self):
        dates = self.data['full_date']
        events = pd.Series(self.data['mood'], index=dates)
        df_log = pd.DataFrame({
            "dates": dates,
            "events": events,
        })
        df_weekly_avg = df_log.resample('W').mean()
        df_weekly_avg['week_middle_date'] = df_weekly_avg.index + pd.offsets.DateOffset(weekday=0)
        df_weekly_avg.reset_index(drop=True, inplace=True)

        scatter_trace = go.Scatter(
            x=df_log['dates'],
            y=df_log['events'],
            mode='markers',
            marker=dict(
                symbol='circle',
                size=6,
                color=[red if event < 0 else green if event > 0 else gray for event in df_log['events']],
            )
        )

        line_trace = go.Scatter(x=df_weekly_avg['week_middle_date'], y=df_weekly_avg['events'],
                                mode='lines', name='Weekly Average')

        # Vertical lines
        line_shapes = []
        for date, event in zip(df_log['dates'], df_log['events']):
            line_shapes.append(
                dict(
                    type='line',
                    x0=date,
                    y0=0,
                    x1=date,
                    y1=event,
                    line=dict(
                        color=red if event < 0 else green,
                        width=3
                        #dash='dash'
                    )
                )
            )

        # Layout
        layout = go.Layout(
            shapes=line_shapes,
            xaxis=dict(
                title='Dates'
            ),
            yaxis=dict(
                title='Events'
            )
        )
        fig = go.Figure(data=[scatter_trace, line_trace], layout=layout)

        fig.update_yaxes(range=[-11, 11])

        fig.update_layout(
            title="Mood over Time",
            xaxis_title="Date",
            yaxis_title="Mood"
        )
        return fig

    def chi_square(self, activity, mood, significance_level=0.05):
        chi2_value, p_value, dof, expected = chi_square_test(self.data['activities'][activity], self.data[mood])
        critical_value = chi2.ppf(1 - significance_level, dof)
        judgement = "STATISTICALLY SIGNIFICANT" if chi2_value > critical_value else "NOT STATISTICALLY SIGNIFICANT"
        return chi2_value, p_value, dof, judgement




