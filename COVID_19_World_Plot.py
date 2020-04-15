import urllib.request
import pandas as pd
import datetime
import pycountry
import plotly.graph_objs as go
from plotly.offline import plot

today = datetime.datetime.today().strftime("%d-%m-%Y")  # aggiungere label per i csv

# #Total Deaths
urllib.request.urlretrieve("https://covid.ourworldindata.org/data/ecdc/total_deaths.csv", "total_deaths.csv")
df_total_deaths = pd.read_csv("total_deaths.csv", parse_dates=["date"])
df_total_deaths["date"] = pd.to_datetime(df_total_deaths["date"]).dt.strftime("%d-%m-%y")
df_total_deaths = df_total_deaths.fillna(0)

# #Total Confirmed Cases
urllib.request.urlretrieve("https://covid.ourworldindata.org/data/ecdc/total_cases.csv", "total_cases.csv")
df_total_cases = pd.read_csv("total_cases.csv", parse_dates=["date"])
df_total_cases["date"] = pd.to_datetime(df_total_cases["date"]).dt.strftime("%d-%m-%y")
df_total_cases = df_total_cases.fillna(0)

# #New Confirmed Cases
urllib.request.urlretrieve("https://covid.ourworldindata.org/data/ecdc/new_cases.csv", "new_cases.csv")
df_new_cases = pd.read_csv("new_cases.csv", parse_dates=["date"])
df_new_cases["date"] = pd.to_datetime(df_new_cases["date"]).dt.strftime("%d-%m-%y")
df_new_cases = df_new_cases.fillna(0)

df_total_deaths_copy = df_total_deaths.copy()
df_total_cases_copy = df_total_cases.copy()
df_new_cases_copy = df_new_cases.copy()

df_list = [df_total_deaths_copy, df_total_cases_copy, df_new_cases_copy]

countries_to_change_name = {
    "Czech Republic": "Czechia",
    "Russia": "Russian Federation",
    "Iran": "Iran, Islamic Republic of",
    "Venezuela": "Venezuela, Bolivarian Republic of",
    "Bolivia": "Bolivia, Plurinational State of",
    "Brunei": "Brunei Darussalam",
    "Cape Verde": "Cabo Verde",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Faeroe Islands": "Faroe Islands",
    "Falkland Islands": "Falkland Islands (Malvinas)",
    "Laos": "Lao People's Democratic Republic",
    "Moldova": "Moldova, Republic of",
    "Palestine": "Palestine, State of",
    "Congo": "Democratic Republic of Congo",
    "Syria": "Syrian Arab Republic",
    "Taiwan": "Taiwan, Province of China",
    "Tanzania": "Tanzania, United Republic of",
    "Timor": "Timor-Leste",
    "United States Virgin Islands": "Virgin Islands, U.S.",
    "British Virgin Islands": "Virgin Islands, British",
    "Vietnam": "Viet Nam"
}

for i in df_list:
    i.rename(countries_to_change_name, axis="columns", inplace=True)

pycountry_list = []
for i in pycountry.countries:
    pycountry_list.append(i.name)

names_not_in_list = []
for i in list(df_total_deaths_copy.columns.values):
    if i not in pycountry_list:
        names_not_in_list.append(i)

df_total_deaths_copy.drop(names_not_in_list, axis=1, inplace=True)
df_total_cases_copy.drop(names_not_in_list, axis=1, inplace=True)
df_new_cases_copy.drop(names_not_in_list, axis=1, inplace=True)


def death_rate():
    total_deaths_list = []
    for i in df_total_deaths_copy.iloc[-1]:
        total_deaths_list.append(i)

    total_cases_list = []
    for i in df_total_cases_copy.iloc[-1]:
        total_cases_list.append(i)

    death_rate = []
    for a, b in zip(total_deaths_list, total_cases_list):
        try:
            death_rate.append(round((a / b) * 100, 2))
        except ZeroDivisionError:
            death_rate.append(0.0)

    return death_rate


def get_countries_for_world_plot():
    return df_total_deaths_copy.columns.values


def get_alpha_code():
    alpha_code_dict = {}
    for country_db in df_total_deaths_copy.columns.values:
        for country in pycountry.countries:
            if country_db == country.name:
                alpha_code_dict[country_db] = country.alpha_3

    return alpha_code_dict


def get_alpha_code_list():
    alpha_code_list = []
    for i in get_alpha_code().values():
        alpha_code_list.append(i)
    return alpha_code_list


# EXTRA INFO
total_cases_list = []
for i in df_total_cases_copy.iloc[-1]:
    total_cases_list.append(str(int(i)))

new_cases_list = []
for i in df_new_cases_copy.iloc[-1]:
    new_cases_list.append(str(int(i)))

deaths_rate = list(map(str, death_rate()))


def world_plot():
    df_text = (df_total_deaths_copy.columns.values + "<br>" +
               "Total Cases: " + total_cases_list + "<br>" +
               "New Cases Today: " + new_cases_list + "<br>" +
               "Deths Rate: " + deaths_rate + "%")

    df_title = ("COVID-19 Map @" + today + "<br>"
                + "World:" + '<br>' +
                "Total Deaths: " + str(df_total_deaths.iloc[-1][1]) + "<br>" +
                "Total Cases: " + str(df_total_cases.iloc[-1][1]) + "<br>" +
                "New Cases: " + str(df_new_cases.iloc[-1][1]))

    data = dict(type="choropleth",
                locations=get_alpha_code_list(),
                z=df_total_deaths_copy.iloc[-1],
                text=df_text,
                colorbar={"title": "Total Deaths"},
                colorscale=[[0, 'green'], [0.5, 'yellow'], [1.0, 'red']]
                )

    layout = dict(title=df_title,
                  geo=dict(showframe=False,
                           projection={"type": "orthographic"}),
                  annotations=[dict(
                      x=0.55,
                      y=0.1,
                      xref='paper',
                      yref='paper',
                      text='Source: <a href="https://ourworldindata.org/coronavirus-source-data"> Our World in Data</a>',
                      showarrow=False
                  )]
                  )

    choromap3 = go.Figure(data=[data], layout=layout)
    return plot(choromap3)


world_plot()
