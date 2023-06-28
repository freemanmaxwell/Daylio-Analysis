import pandas as pd
import re
import csv
from plotly_calplot import calplot
import plotly.graph_objects as go
import numpy as np
from scipy.stats import chi2, chi2_contingency
import json

json_file_path = "activity_groups.json"

moodDict = {
    'rad': 10,
    'good': 5,
    'meh': 0,
    'bad': -5,
    'awful': -10
}

red = '#FE978E'
green = '#95d195' #'#B0CFB0'
dark_green = '#1b4a1b'
gray = '#d3d3d3'
yellow = '#FFFACD'

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
        self.activities_culled = self.activities

        # Next, remove grouped entries, replacing with a single entry for each group
        with open(json_file_path, "r") as file:
            json_data = json.load(file)
        entries_to_remove = [element for sublist in list(json_data.values()) for element in sublist]
        entries_to_add = list(json_data.keys())
        for entry in entries_to_remove:
            if entry in self.activities:
                self.activities_culled.remove(entry)
        for entry in entries_to_add:
            self.activities_culled.append(entry)
        self.activities_culled.reverse()
        self.activity_groups = list(json_data.keys())

        # Next, add these words as keys to a dict and populate each entry, update self.data
        act_dict = {}
        for activity in self.activities:
            act_dict[activity] = []
            for day in self.data['activities']:
                act_dict[activity].append(int(bool(re.search(r'\b' + activity + r'\b', day))))

        act_culled_dict = {}
        for activity in self.activities_culled:
            act_culled_dict[activity] = []
            if activity in json_data.keys():
                all_ranks_list = []
                for i, rank in enumerate(json_data[activity]):
                    rank_list = []
                    for day in self.data['activities']:
                        rank_list.append((i + 1) * int(bool(re.search(r'\b' + rank + r'\b', day))))
                    all_ranks_list.append(rank_list)
                final_ranked_list = [sum(sublist) for sublist in zip(*all_ranks_list)]
                for i, entry in enumerate(final_ranked_list):
                    if entry == 0:
                        final_ranked_list[i] = float('NaN')
                    else:
                        final_ranked_list[i] = entry - 1
                act_culled_dict[activity].extend(final_ranked_list)
            else:
                for day in self.data['activities']:
                    act_culled_dict[activity].append(int(bool(re.search(r'\b' + activity + r'\b', day))))

        self.data['activities'] = act_dict

        self.data['activities_culled'] = act_culled_dict

        self.data['mood'] = [moodDict[day] for day in self.data['mood']]

        self.data['full_date'] = pd.to_datetime(self.data['full_date'])

    def calendar_plot(self, activity):
        dates = self.data['full_date']
        events = pd.Series(self.data['activities_culled'][activity], index=dates)
        df_log = pd.DataFrame({
            "dates": dates,
            "events": events,
        })

        #colorscale
        if activity in self.activity_groups:
            color_scale = [(0.00, red),   (0.33, gray),
                (0.33, gray), (0.66, gray),
                (0.66, green),  (1.00, green)]
        else:
            color_scale = [(0.00, gray), (0.33, gray),
                           (0.33, gray), (0.66, green),
                           (0.66, green), (1.00, green)]

        # noinspection PyTypeChecker
        fig = calplot(
            df_log,
            x="dates",
            y="events",
            name=activity,
            years_title=True,
            dark_theme=False,
            colorscale=color_scale
        )
        return fig

    def mood_plot(self):
        dates = self.data['full_date']
        events = pd.Series(self.data['mood'], index=dates)
        df_log = pd.DataFrame({
            "dates": dates,
            "events": events,
        })

        df_log["dates"] = pd.to_datetime(
            df_log["dates"])  # Convert 'dates' column to datetime if not already in datetime format
        df_log.sort_values("dates", inplace=True)  # Sort the DataFrame by 'dates' column in ascending order

        rolling_avg = []
        avg_dates = []

        for i in range(len(df_log['events'])):
            if i < 6:
                rolling_avg.append(np.nan)  # Assign NaN to initial rows
                avg_dates.append(np.nan)
            else:
                avg = np.mean(df_log['events'][i - 6:i + 1])
                rolling_avg.append(avg)
                avg_dates.append(df_log['dates'].iloc[i])

        df_log['rolling_avg'] = rolling_avg
        df_log['avg_dates'] = avg_dates

        scatter_trace = go.Scatter(
            x=df_log['dates'],
            y=df_log['events'],
            mode='markers',
            name='Daily Value',
            marker=dict(
                symbol='circle',
                size=6,
                color=[red if event < 0 else green if event > 0 else gray for event in df_log['events']],
            )
        )

        line_trace = go.Scatter(x=df_log['avg_dates'], y=df_log["rolling_avg"],
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
                #title='Dates'
            ),
            yaxis=dict(
                title='Events',
                tickvals=[-10, -5, 0, 5, 10],
                ticktext=['awful', 'bad', 'meh', 'good', 'rad']
            )
        )
        fig = go.Figure(data=[scatter_trace, line_trace], layout=layout)

        fig.update_yaxes(range=[-11, 11])

        fig.update_layout(
            #title="Mood over Time",
            #xaxis_title="Date",
            yaxis_title="Mood"
        )
        tick_labels = ['awful', 'bad', 'meh', 'good', 'rad']
        fig.update_yaxes(ticktext=tick_labels)
        return fig

    def chi_square(self, activity, mood, significance_level=0.05):
        chi2_value, p_value, dof, expected = chi_square_test(self.data['activities'][activity], self.data[mood])
        critical_value = chi2.ppf(1 - significance_level, dof)
        judgement = "STATISTICALLY SIGNIFICANT" if chi2_value > critical_value else "NOT STATISTICALLY SIGNIFICANT"
        return chi2_value, p_value, dof, judgement




