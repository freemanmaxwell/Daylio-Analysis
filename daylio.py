import pandas as pd
import re
import csv
from plotly_calplot import calplot
import plotly.graph_objects as go

moodDict = {
    'rad': 10,
    'good': 5,
    'meh': 0,
    'bad': -5,
    'awful': -10
}

class Daylio:
    def __init__(self, csv_file):
        self.data = {}
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for column_name in reader.fieldnames:
                self.data[column_name.lower()] = []  # Initialize an empty list for each column
            for row in reader:
                for column_name, value in row.items():
                    self.data[column_name.lower()].append(value)  # Append column data to the list
        self.data['activities'] = [entry.lower() for entry in self.data['activities']]

    def get_activ(self):
        word_set = set()

        for item in self.data['activities']:
            words = item.split(' | ')
            for word in words:
                word = word.lower()
                word_set.update([word])

        unique_words = list(word_set)
        return unique_words


    def calendar_plot(self, key, phrase=""):
        if key in self.data.keys():
            day_data = []
            for day in self.data[key]:
                day_data.append(int(bool(re.search(r'\b' + phrase + r'\b', day))))

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
        df_weekly_avg = df_log.resample('W').mean()
        df_weekly_avg['week_middle_date'] = df_weekly_avg.index + pd.offsets.DateOffset(weekday=3)
        df_weekly_avg.reset_index(drop=True, inplace=True)

        scatter_trace = go.Scatter(
            x=df_log['dates'],
            y=df_log['events'],
            mode='markers',
            marker=dict(
                symbol='circle',
                size=8
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
                        color='red' if event < 0 else 'green',
                        width=1,
                        dash='dash'
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

        fig.update_yaxes(range=[-10, 10])

        fig.update_layout(
            title="Mood over Time",
            xaxis_title="Date",
            yaxis_title="Mood"
        )
        return fig


