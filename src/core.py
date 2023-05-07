import os
import re
import json
from collections import defaultdict
import argparse
import pandas as pd

# Bokeh
from bokeh.plotting import figure, show
from bokeh.io import output_file


# Check if the directory provided by the user exist and contains csv files
def isResultDirectory(dirName):
    if os.path.isdir(dirName):
        # check that directory contains csv files
        csv_files = [f for f in os.listdir(dirName) if f.endswith('.csv')]
        if len(csv_files) > 0:
            # Directory exists and contains CSV files
            return True
        else:
            # Directory exists but does not contain any CSV files
            return False
    else:
        # Directory does not exist
        return False


def print_usage(parser):
    parser.print_usage()


# Command line arguments
def getArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", dest="dir_name", help="Name of the directory", required=True)
    args = parser.parse_args()

    directoryCheckResult = isResultDirectory(args.dir_name)

    if directoryCheckResult:
        return args
    else:
        print("[+] Please make sure that the result directory exist and contains the .csv files")
        print_usage(parser)
        exit(1)


def group_files_by_month(directory):
    # Create an empty dictionary to store the filenames grouped by month
    files_by_month = defaultdict(list)

    # Loop through the files in the directory
    for filename in os.listdir(directory):
        # Check if the file is a CSV
        if filename.endswith('.csv'):
            # Extract the month from the filename
            month = filename.split('_')[1][4:6]

            # Add the filename to the dictionary under the corresponding month
            files_by_month[month].append(filename)

    return files_by_month


def group_files_by_year_month(directory):
    files_by_year_month = defaultdict(lambda: defaultdict(list))
    for file_name in os.listdir(directory):
        if file_name.endswith('.csv'):
            year = file_name[5:9]
            month = file_name[9:11]
            files_by_year_month[year][month].append(file_name)
    return files_by_year_month


def average_per_month(directory):
    averagePerMonth = defaultdict()
    files_by_month = group_files_by_month(directory)
    for month in files_by_month.keys():
        averagePerMonth[month] = 0
        for file_by_day in files_by_month[month]:
            csvDF = dataFrameBasedOnTime(f'{directory}/{file_by_day}')
            csvDF.readCSVFile()
            csvDF.convertToDateTime()
            csvDF.groupByKMinute('10')
            averagePerMonth[month] += csvDF.averageTemperature()
        averagePerMonth[month] = averagePerMonth[month] / len(files_by_month[month])

    return averagePerMonth


def getDatesFromCSV(directory):
    dates = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            match = re.search(r'temp_(\d+)_metrics.csv', filename)
            if match:
                date = match.group(1)
                dates.append(date)
    return dates


def average_per_year_months(directory):
    averagePerYearMonths = defaultdict(lambda: defaultdict())
    files_by_year_month = group_files_by_year_month('../result')
    for year, months in files_by_year_month.items():
        for month, files in months.items():
            averagePerYearMonths[year][month] = 0
            for file in files:
                csvDF = dataFrameBasedOnTime(f'{directory}/{file}')
                csvDF.readCSVFile()
                csvDF.convertToDateTime()
                csvDF.groupByKMinute('10')
                averagePerYearMonths[year][month] += csvDF.averageTemperature()
            averagePerYearMonths[year][month] = averagePerYearMonths[year][month] / len(files)

    averagePerYearMonthsJson = json.dumps(dict(averagePerYearMonths))

    # Save the JSON data to a file
    with open("avg_per_year_months.json", "w") as json_file:
        json_file.write(averagePerYearMonthsJson)

    return "avg_per_year_months.json"


def average_per_month_days(directory, year):
    avgPerMonthDays = defaultdict(lambda: defaultdict())
    files_by_months = group_files_by_year_month('../result')[year]

    # Extract day from file name
    extract_day_from_file_name = lambda file_name: file_name.split('_')[1][-2:]

    for month in files_by_months.keys():
        for file in files_by_months[month]:
            csvDF = dataFrameBasedOnTime(f'{directory}/{file}')
            csvDF.readCSVFile()
            csvDF.convertToDateTime()
            csvDF.groupByKMinute('10')
            avgPerMonthDays[month][extract_day_from_file_name(file)] = csvDF.averageTemperature()

    avgPerMonthDaysJson = json.dumps(dict(avgPerMonthDays))

    # Save the JSON data to a file
    with open("avg_per_month_days.json", "w") as json_file:
        json_file.write(avgPerMonthDaysJson)

    return "avg_per_month_days.json"


# Class that performs most of the actions needed on a given csv file
class dataFrameBasedOnTime:
    def __init__(self, csvFileName):
        self.csvFileName = csvFileName
        self.df = None
        self.dfGroupedSecond = None
        self.dfGroupedMinute = None
        self.dfGroupedKMinute = None
        self.samplingRate = '1'

    def readCSVFile(self):
        self.df = pd.read_csv(self.csvFileName)

    # Convert timestamp to datetime
    def convertToDateTime(self):
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], unit='ns')

    def groupBySecond(self):
        # Group data by timestamp rounded to the second
        self.dfGroupedSecond = self.df.groupby(self.df['timestamp'].dt.round('s')).mean(numeric_only=True)

    def groupByMinute(self):
        self.dfGroupedMinute = self.df.set_index('timestamp').resample('1min').mean(numeric_only=True)

    def groupByKMinute(self, k):
        firstDatetime = self.df['timestamp'].iloc[0]
        self.dfGroupedKMinute = self.df.set_index('timestamp').resample(k + 'T', origin=firstDatetime).mean(
            numeric_only=True)

    def createLinePlotBokeh(self):
        # Create a figure
        p = figure(x_axis_type="datetime", title="Line Plot of Data Value over Time")

        # Add a line renderer
        p.line(self.dfGroupedKMinute.index, self.dfGroupedKMinute['data_value'], line_width=2)

        # Show the plot
        output_file("line_plot.html")
        show(p)
        p.save("line_plot.html")

    def averageTemperature(self):
        return self.dfGroupedKMinute['data_value'].mean()


def main():
    args = getArguments()
    average_per_year_months(args.dir_name)
    average_per_month_days(args.dir_name, '2022')
    # average_per_year_months('../result')
    # average_per_month_days('../result', '2022')
    # csvTest = dataFrameBasedOnTime(chosenDay)
    # csvTest.readCSVFile()
    # csvTest.convertToDateTime()
    # csvTest.groupBySecond()
    # csvTest.groupByMinute()
    # csvTest.groupByKMinute(args.sampling_rate)


if __name__ == '__main__':
    main()
