import datetime
from core import *

# Dash
import dash
import dash_table
from dash.dash_table.Format import Group
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# The Web App

# Initialize the Dash app
app = dash.Dash()

# Create a list of days to populate the drop-down menu
dates = getDatesFromCSV('../result')

# Create a layout for the app
convertDate = lambda x: datetime.datetime.strptime(x, '%Y%m%d').strftime('%Y-%m-%d')
convertedDates = list(map(convertDate, dates))

# Read the JSON data from the file
with open("avg_per_year_months.json", "r") as json_file:
    averagePerYearMonthsJson = json.load(json_file)

# Convert the data back to a nested defaultdict
averagePerYearMonths = defaultdict(lambda: defaultdict(), averagePerYearMonthsJson)

# Read the JSON data from the file
with open("avg_per_month_days.json", "r") as json_file:
    averagePerMonthDaysJson = json.load(json_file)

# Convert the data back to a nested defaultdict
averagePerMonthDays = defaultdict(lambda: defaultdict(), averagePerMonthDaysJson)


app.layout = html.Div([
    html.H1('Dashboard', style={'textAlign': 'center'}),

    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Daily Line Plot', value='tab-1'),
        dcc.Tab(label='Heat Map', value='tab-2'),
        dcc.Tab(label='Histogram', value='tab-3'),
        dcc.Tab(label='Histogram Per Month', value='tab-4'),
        dcc.Tab(label='Histogram Per Year', value='tab-5'),
    ]),

    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([

            html.H1(children='Alerts'),
            html.Div(id='alert', children=''),
            dcc.Interval(id='interval-component', interval=600000, n_intervals=0),  # update every 10 min

            html.Div([

                html.H2(children='''
            Choose The Day To Visualize.
            '''),

                # Create a drop-down menu for the user to select a day
                dcc.Dropdown(
                    id='day-dropdown',
                    options=[{'label': convertedDate, 'value': date} for convertedDate, date in
                             zip(convertedDates, dates)],
                    value=dates[0]
                ),

                html.H2('Custom sampling rate (minutes):'),

                # Sampling rate input
                dcc.Input(id='sampling-rate-input', type='number', min=1, value=1),
                html.Button(id='submit-sampling-rate-button', children='Submit'),
                # Output the line plot based on the selected day
                dcc.Graph(id='line-plot')
            ]),

            html.H2(children='''
            Statistics Summary
            '''),

            html.Div(id='stats-container'),
        ])

        # Use the selected day to update the line plot

    elif tab == 'tab-2':
        # create the heatmap figure
        return html.Div([

            html.H2(children='''
                    Choose The Day To Visualize.
                    '''),

            dcc.Dropdown(
                id='day-dropdown',
                options=[{'label': convertedDate, 'value': date} for convertedDate, date in
                         zip(convertedDates, dates)],
                value=dates[0]
            ),
            dcc.Graph(id='heatmap')
        ])

    elif tab == 'tab-3':
        return html.Div([

            html.H2(children='''
                Choose The Day To Visualize.
                '''),

            dcc.Dropdown(
                id='day-dropdown',
                options=[{'label': convertedDate, 'value': date} for convertedDate, date in
                         zip(convertedDates, dates)],
                value=dates[0]
            ),
            dcc.Graph(id='histogram')
        ])

    elif tab == 'tab-4':
        return html.Div([
            html.H2('Select month'),
            dcc.Dropdown(id='month-dropdown', options=[], value=None),
            dcc.Graph(id='temperature-histogram')
        ])

    elif tab == 'tab-5':
        return html.Div([
            html.H2("Select year"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in averagePerYearMonths.keys()],
                value=next(iter(averagePerYearMonths.keys()))
            ),
            dcc.Graph(id='temp-graph')
        ])


@app.callback(
    Output(component_id='alert', component_property='children'),
    [Input(component_id='interval-component', component_property='n_intervals'),
     Input(component_id='day-dropdown', component_property='value')]
)
def update_alert(n_intervals, selected_day):
    alert_text, color = check_temperature(selected_day)
    return alert_text,


def check_temperature(day):
    csvDF = dataFrameBasedOnTime(f'../result/temp_{day}_metrics.csv')
    csvDF.readCSVFile()
    csvDF.convertToDateTime()
    csvDF.groupByKMinute('10')
    temperature = csvDF.dfGroupedKMinute['data_value']
    avg_temp = temperature[-1]
    print(avg_temp)
    if avg_temp > 35:
        return 'Temperature is too high!', 'red'
    elif avg_temp < 0:
        return 'Temperature is too low!', 'blue'
    elif 15 < avg_temp < 27:
        return 'Temperature is normal', 'green'


@app.callback(Output('temp-graph', 'figure'), [Input('year-dropdown', 'value')])
def update_graph(year):
    months = list(averagePerYearMonths[year].keys())
    avg_temps_per_months = list(averagePerYearMonths[year].values())
    return {
        'data': [{'x': months, 'y': avg_temps_per_months, 'type': 'bar'}],
        'layout': {'title': f'Average temperature per month in {year}'}
    }


@app.callback(Output('month-dropdown', 'options'),
              [Input('month-dropdown', 'value')])
def update_month_options(value):
    # Extract the available months from the group_files_by_month function
    available_months = list(group_files_by_month('../result').keys())
    # Create a list of options for the dropdown
    options = [{'label': month, 'value': month} for month in available_months]
    return options


# Tab-4
@app.callback(Output('temperature-histogram', 'figure'),
              [Input('month-dropdown', 'value')])
def update_temperature_histogram(month):
    days = list(averagePerMonthDays[month].keys())
    avg_temps_per_days = list(averagePerMonthDays[month].values())
    if month is None:
        return {}

    # Create a histogram figure
    return {
        'data': [{'x': days, 'y': avg_temps_per_days, 'type': 'bar'}],
        'layout': {'title': f'Average temperature per day in {month}'}
    }


# Tab-2
@app.callback(Output(component_id='heatmap', component_property='figure'),
              [Input(component_id='day-dropdown', component_property='value')])
def update_heatmap(selected_day):
    csvDF = dataFrameBasedOnTime(f'../result/temp_{selected_day}_metrics.csv')
    csvDF.readCSVFile()
    csvDF.convertToDateTime()
    csvDF.groupByKMinute('60')
    fig = go.Figure(data=[
        go.Heatmap(x=csvDF.dfGroupedKMinute.index, y=csvDF.dfGroupedKMinute.index,
                   z=csvDF.dfGroupedKMinute['data_value'])])
    fig.update_layout(title='Temperature over Time')
    return fig


# Tab-3
# Histogram callback function
# Histogram for each day
@app.callback(Output(component_id='histogram', component_property='figure'),
              [Input(component_id='day-dropdown', component_property='value')])
def update_histogram(selected_day):
    csvDF = dataFrameBasedOnTime(f'../result/temp_{selected_day}_metrics.csv')
    csvDF.readCSVFile()
    csvDF.convertToDateTime()
    csvDF.groupByKMinute('60')

    fig = go.Figure(data=[go.Histogram(x=csvDF.dfGroupedKMinute['data_value'], nbinsx=50)])
    fig.update_layout(title='Temperature Distribution')
    return fig


# Tab-1
# Time series line plot
@app.callback(Output(component_id='line-plot', component_property='figure'),
              [Input(component_id='day-dropdown', component_property='value'),
               Input(component_id='sampling-rate-input', component_property='value'),
               Input(component_id='submit-sampling-rate-button', component_property='n_clicks')])
def update_line_plot(selected_day, sampling_rate, n_clicks):
    if n_clicks is None:
        # first call of the function
        sampling_rate = 1
    # Read the corresponding CSV file for the selected day
    csvDF = dataFrameBasedOnTime(f'../result/temp_{selected_day}_metrics.csv')
    csvDF.readCSVFile()
    csvDF.convertToDateTime()
    csvDF.groupByKMinute(str(sampling_rate))

    # Create the line plot using Plotly
    return {
        'data': [
            {'x': csvDF.dfGroupedKMinute.index, 'y': csvDF.dfGroupedKMinute['data_value'], 'type': 'line'}],
        'layout': {'title': 'Line Plot of Temperature over Time'}
    }


@app.callback(Output('stats-container', 'children'),
              [Input(component_id='day-dropdown', component_property='value'),
               Input(component_id='sampling-rate-input', component_property='value'),
               Input(component_id='submit-sampling-rate-button', component_property='n_clicks')])
def update_stats(selected_day, sampling_rate, n_clicks):
    if n_clicks is None:
        # first call of the function
        sampling_rate = 1
    df = dataFrameBasedOnTime(f'../result/temp_{selected_day}_metrics.csv')
    df.readCSVFile()
    df.convertToDateTime()
    df.groupByKMinute(str(sampling_rate))

    min_temp = round(df.dfGroupedKMinute['data_value'].min(), 2)
    max_temp = round(df.dfGroupedKMinute['data_value'].max(), 2)
    avg_temp = round(df.dfGroupedKMinute['data_value'].mean(), 2)
    median_temp = round(df.dfGroupedKMinute['data_value'].median(), 2)
    mode_temp = round(df.dfGroupedKMinute['data_value'].mode(), 2)
    percentile_10 = round(df.dfGroupedKMinute['data_value'].quantile(0.1), 2)
    percentile_25 = round(df.dfGroupedKMinute['data_value'].quantile(0.25), 2)
    percentile_50 = round(df.dfGroupedKMinute['data_value'].quantile(0.5), 2)
    percentile_75 = round(df.dfGroupedKMinute['data_value'].quantile(0.75), 2)
    percentile_90 = round(df.dfGroupedKMinute['data_value'].quantile(0.9), 2)
    q1 = round(df.dfGroupedKMinute['data_value'].quantile(0.25), 2)
    q2 = round(df.dfGroupedKMinute['data_value'].quantile(0.5), 2)
    q3 = round(df.dfGroupedKMinute['data_value'].quantile(0.75), 2)

    stats_data = [
        {'Statistic': 'Minimum temperature', 'Value': min_temp},
        {'Statistic': 'Maximum temperature', 'Value': max_temp},
        {'Statistic': 'Average temperature', 'Value': avg_temp},
        {'Statistic': 'Median temperature', 'Value': median_temp},
        {'Statistic': 'Mode temperature', 'Value': mode_temp.iloc[0]},
        {'Statistic': '10th Percentile', 'Value': percentile_10},
        {'Statistic': '25th Percentile', 'Value': percentile_25},
        {'Statistic': '50th Percentile (Median)', 'Value': percentile_50},
        {'Statistic': '75th Percentile', 'Value': percentile_75},
        {'Statistic': '90th Percentile', 'Value': percentile_90},
        {'Statistic': 'Q1 (25th Percentile)', 'Value': q1},
        {'Statistic': 'Q2 (50th Percentile)', 'Value': q2},
        {'Statistic': 'Q3 (75th Percentile)', 'Value': q3}
    ]

    return [
        dash_table.DataTable(
            id='stats-table',
            columns=[{"name": i, "id": i} for i in stats_data[0].keys()],
            data=stats_data,
            style_table={'overflowX': 'scroll'},
            style_cell={'width': '150px', 'textAlign': 'center'},
            style_as_list_view=True,
            style_header={'fontWeight': 'bold'},
            style_data_conditional=[
                {
                    'if': {'column_id': 'Statistic'},
                    'textAlign': 'left'
                }
            ]
        )
    ]


# Run the app
if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=False, dev_tools_ui=False, dev_tools_props_check=False)
    # app.run_server(dev_tools_hot_reload=False)
