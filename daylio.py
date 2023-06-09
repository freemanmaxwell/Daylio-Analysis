import pandas as pd
import numpy as np
import re
import csv
from plotly_calplot import calplot
import plotly.express as px

moodDict = {
    'rad': 10,
    'good': 5,
    'meh': 0,
    'bad': -5,
    'awful': -10
}


def get_activities(activities):
    word_set = set()

    for item in activities:
        words = item.split(' | ')
        for word in words:
            word = word.lower()
            word_set.update([word])

    unique_words = list(word_set)
    print(unique_words)
    return unique_words

class Daylio:
    def __init__(self, csv_file):
        self.data = {}
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for column_name in reader.fieldnames:
                self.data[column_name] = []  # Initialize an empty list for each column
            for row in reader:
                for column_name, value in row.items():
                    self.data[column_name].append(value)  # Append column data to the list

    def get_activ(self):
        get_activities(self.data['activities'])

    def calendar_plot(self, key, phrase=""):
        if key in self.data.keys():
            day_data = []
            for day in self.data[key]:
                day_data.append(int(bool(re.search(r'\b' + phrase + r'\b', day))))

            #print(str(np.sum(day_data)) + '/' + str(len(day_data)))
            dates = pd.to_datetime(self.data['full_date'])
            events = pd.Series(day_data, index=dates)
            df_log = pd.DataFrame({
                "dates": dates,
                "events": events,
            })

            fig = calplot(
                df_log,
                x="dates",
                y="events",
                name = phrase,
                title = phrase + ' (in ' +  key + ')',
                years_title = True,
                dark_theme=False
            )
            return fig

        else:
            print('Invalid key!')

    def mood_plot(self):
        day_data = []
        for day in self.data['mood']:
            day_data.append(moodDict[day])
        dates = pd.to_datetime(self.data['full_date'])
        events = pd.Series(day_data, index=dates)
        df_log = pd.DataFrame({
            "dates": dates,
            "events": events,
        })
        fig = px.line(df_log, x="dates", y="events")
        #fig.update_traces(line=dict(shape='spline'))
        fig.update_yaxes(range=[-10, 10])
        fig.update_layout(
            title="Mood vs Time",
            xaxis_title="Date",
            yaxis_title="Mood"
        )
        return fig


