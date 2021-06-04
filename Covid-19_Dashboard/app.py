###-----------------  Importing Libraries -------------------------###

import dash
import dash_core_components as dcc
import dash_html_components as html


import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import date
import plotly.graph_objects as go

from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import json
import dash_table
from datetime import date, timedelta


###-----------------  LOADING DATA -------------------------###

today = date.today() - timedelta(days=2)
previous_day = date.today() - timedelta(days=3)

# Month abbreviation, day and year  
today_formatted = today.strftime("%m-%d-%Y")
previous_day_formatted = previous_day.strftime("%m-%d-%Y")

today_formatted_text = today.strftime("%d %b %Y")

# DAILY CASES
df_daily_report = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" + str(today_formatted) + ".csv")
df_daily_report_previous = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/" + str(previous_day_formatted) + ".csv")

# COMPUTING CONFIRMED, RECOVERED, ACTIVE, DEATHS CASES AND PERCENTAGE INCREASE/DECREASE
confirmed_world = df_daily_report['Confirmed'].sum()
confimred_world_previous = df_daily_report_previous['Confirmed'].sum()
confirmed_world_today = confirmed_world - confimred_world_previous

recovered_world = df_daily_report['Recovered'].sum()
recovered_world_previous = df_daily_report_previous['Recovered'].sum()
active_world = df_daily_report['Active'].sum()
active_world_previous = df_daily_report_previous['Active'].sum()
active_world_today = round((active_world - active_world_previous),0)

deaths_world = df_daily_report['Deaths'].sum()
deaths_world_previous = df_daily_report_previous['Deaths'].sum()

confirmed_outcome_world = recovered_world + deaths_world
percentage_recovered = round((recovered_world / confirmed_outcome_world)*100,1)
percentage_deaths = round((deaths_world / confirmed_outcome_world)*100,1)


## VACCINATION DATA
df_vacc = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv')
df_vacc_max = df_vacc.groupby(["location"], as_index=False).max()
total_vaccinations_world = df_vacc_max['total_vaccinations']
countries_vacc = df_vacc['location'].unique()


#LOADING COUNTRY CODES

with open('cc3_cn_r.json') as json_file:
    cc3_cn_r = json.load(json_file)



#### GROUPING BY COUNTRIES 

df_group_country = df_daily_report.groupby('Country_Region')

list_countries = []
for i,g in df_group_country:
    list_countries.append({
        'Country_Region':g['Country_Region'].unique()[0],
        'Confirmed': g['Confirmed'].sum(),
        'Active': g['Active'].sum(),
        'Recovered': g['Recovered'].sum(),
        'Deaths': g['Deaths'].sum(),
        'Incident_Rate': round(g['Incident_Rate'].mean(), 3),
        'Case_Fatality_Ratio': round(g['Case_Fatality_Ratio'].mean(), 3),
    })

df_countries = pd.DataFrame(list_countries)

df_countries['CODE'] = df_countries['Country_Region'].map(cc3_cn_r)
df_countries = df_countries.dropna(subset=['CODE'])

#REARRANGING COLUMNS



# LIST OF COUNTRIES



# TIME SERIES DATA FOR CONFIRMED CASES
df_time_confirmed = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
# print(df_time_confirmed.head())

df_excluded_confirmed = df_time_confirmed.drop(['Province/State','Lat','Long'], axis=1)


df_excluded_confirmed.set_index('Country/Region', inplace=True)

# Calculate difference in each corresonding time series value along x axis.
df_excluded_confirmed = df_excluded_confirmed.diff(axis=1)

df_excluded_confirmed.reset_index(inplace=True)

df_time_confirmed = pd.melt(df_excluded_confirmed, id_vars=['Country/Region'], var_name='date', value_name='value')
# print(df_time_confirmed.head())


# TIME SERIES DATA FOR RECOVERED CASES
df_time_recovered = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

# print(df_time_recovered.head())

df_excluded_recovered = df_time_recovered.drop(['Province/State','Lat','Long'], axis=1)

df_excluded_recovered.set_index('Country/Region', inplace=True)

# Calculate difference in each corresonding time series value along x axis.
df_excluded_recovered = df_excluded_recovered.diff(axis=1)

df_excluded_recovered.reset_index(inplace=True)

df_time_recovered = pd.melt(df_excluded_recovered, id_vars=['Country/Region'], var_name='date', value_name='value')
# print(df_time_recovered.head())

countries = df_time_recovered['Country/Region'].unique()

## LOADING NEWS ARTICLES

news_articles_list = open("covid_news_articles.csv", "r",encoding='utf-8').readlines()

news_card_list = []

for x in news_articles_list:
    article =x.split(",")
    news_card_template = dbc.Col(
        dbc.Card([
            dbc.CardImg(
                src = article[2],
                top = True
            ),
            dbc.CardBody([
                html.H6(article[0]),
                html.P(
                    article[1],
                    style = {'fontSize':12}
                )
            ]),
            dbc.CardLink(
                'Read the article', 
                href = article[3]
            )
        ]),
        width = 2
    )
    news_card_list.append(news_card_template)

news_card_list = news_card_list[1:]

BS = "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])


############----------------------------------------- INDICATOR -------------------------###############

fig_indicator = go.Figure()

fig_indicator.add_trace(go.Indicator(
    mode ='number+delta',
    value = recovered_world,
    title={'text':'Recovered Cases'},
    domain={'x':[1,0.5], 'y':[0.8,0.9]},
    title_font_size = 25,
    number_font_size =40,
    delta={'reference': recovered_world_previous}
))


fig_indicator.add_trace(go.Indicator(
    mode ='number+delta',
    value = confirmed_world,
    title={'text':'Confirmed Cases'},
    domain={'x':[1,0.5], 'y':[0.4,0.5]},
    delta_increasing_color = '#FF4136',
    title_font_size = 25,
    number_font_size =40,
    delta={'reference': confimred_world_previous}
))


fig_indicator.add_trace(go.Indicator(
    mode ='number+delta',
    value = deaths_world,
    title={'text':'Total Deaths'},
    domain={'x':[1,0.5], 'y':[0,0.1]},
    delta_increasing_color = '#FF4136',
    title_font_size = 25,
    number_font_size =40,
    delta={'reference': deaths_world_previous}
))

#---------------------- CARDS ACTIVE AND OUTCOME CASES----------------------------#

card_active_cases = dbc.Card(
    [
        dbc.CardHeader('Active Cases'),
        dbc.CardBody([
            html.H3(html.B(active_world)),
            html.H5('Cases which are currently Active', style={'color':'blue', 'fontSize':14}),
            html.H5(html.B(confirmed_world), style={'color':'green'}),
            html.P("Total confirmed Cases till now", style={'fontSize':14}),
            html.H5(html.B(confirmed_world_today), style={'color':'red'}),
            html.P("Total confirmed Cases today", style={'fontSize':14}),
            dbc.CardLink("See more Details", href="https://github.com/CSSEGISandData/COVID-19")
        ])
    ]
)


card_closed_cases = dbc.Card(
    [
        dbc.CardHeader('Closed Cases'),
        dbc.CardBody([
            html.H3(html.B(confirmed_outcome_world)),
            html.H5('Cases which had an outcome', style={'color':'blue', 'fontSize':14}),
            html.H5(html.B(str(recovered_world)+" ("+str(percentage_recovered) + "%)"), style={'color':'green'}),
            html.P("Total recovered Cases till now", style={'fontSize':14}),
            html.H5(html.B(str(deaths_world)+" ("+str(percentage_deaths) + "%)"), style={'color':'red'}),
            html.P("Total deaths occured", style={'fontSize':14}),
            dbc.CardLink("See more Details", href="https://github.com/CSSEGISandData/COVID-19")
        ])
    ]
)

#------------------------------ DROPDOWN COUNTRIES SELECTION ------------------------------------#

dropdown_countries = dcc.Dropdown(
    id = 'dropdown',
    options = [{'label':x, 'value':x} for x in countries],
    value = ['Sri Lanka', 'New Zealand'],
    clearable = False,
    multi = True 
)

#----------------------- RADIO BUTTON WORLD MAP -------------------------------------------------------#

radio_buttons_world = dcc.RadioItems(
    id = 'radio_button_world',
    options = [
        {'label': 'Scatter Plot World', 'value':'scatter'},
        {'label':'Choropleth World Plot', 'value':'choropleth'}
    ],
    value='scatter',
    labelStyle = {'display':'inline-block'}
)

#-------------------------- WORLD MAP -----------------------------------------#

fig_world = go.Figure(
    data = go.Choropleth(
        locations = df_countries['CODE'],
        z = df_countries['Confirmed'],
        text = df_countries['Country_Region'],
        colorscale='reds',
        autocolorscale = True,
        colorbar_title = 'Number of Confirmed Cases'
    )
)

fig_world.update_layout(
    autosize = True,
    geo= dict(
        showcoastlines = True,
        projection_type = 'equirectangular'
    )
)

#------------------------ WORLD MAP 2 ----------------------------------------#

fig_world_scatter = px.scatter_geo(
    df_countries,
    locations = 'CODE',
    hover_name = 'Country_Region',
    size = 'Confirmed',
    projection = 'natural earth',
    size_max = 45
)

#---------------------------------- TABLE COVID ----------------------------------#

table_covid = dash_table.DataTable(
    id = 'datatable-interactivity',
    columns = [
        {"name":i, "id":i, "deletable":False, "selectable":True} for i in df_countries.columns
    ],
    data = df_countries.to_dict('records'),
    editable = True,
    filter_action = "native",
    sort_action = "native",
    row_deletable = False,
    page_action = "native",
    page_current = 0,
    page_size = 15,
    style_data_conditional = [
        {
            'if':{'row_index':'odd'},
            'backgroundColor':'rgb(248,248,248)'
        }
    ],
    style_header = {
        'backgrundColor' : 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
        'whiteSpace': 'normal',
        'height':'auto',
        'lineHeight': '15px'
    },
    style_data = {
        'whiteSpace': 'normal',
        'height' : 'auto'
    },
    style_table = {
        'overflowY': 'auto',
    },
    style_as_list_view = False,

)

#------------------------------------- VACCINE COUNTRIES DROPDOWN ------------------------------------#

dropdown_vaccine_timeline = dcc.Dropdown(
    id='dropdown_vaccine_timeline',
    options=[
        {'label' : x, 'value':x} for x in countries_vacc
    ],
    value = 'World',
    clearable= False,
    multi = False
)

#----------------------------- VACCINE DATA SELECTION -------------------------------------#

radio_buton_vaccine = dcc.RadioItems(
    id = "radio_button_vaccine",
    options=[
        {'label': 'Total Vaccinations', 'value':'total_vaccinations_per_hundred'},
        {'label': 'People Vaccinated Per Hundred', 'value':'people_vaccinated_per_hundred'},        
        {'label': 'People Fully Vaccinated Per Hundred', 'value':'people_fully_vaccinated_per_hundred'},        
    ],
    value =  "people_vaccinated_per_hundred",
    labelStyle = {'display':'inline-block'}
)

#------------------------ NEWS CARDS ----------------------------------------------#




PLOTLY_LOGO = "data:image/png;base64,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"

####################---------------- NAVIGATION BAR --------------------------##
navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(dbc.NavbarBrand("COVID-19 Pandemic Dashboard", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        ),
        dbc.NavbarToggler(id="navbar-toggler")
    ],
    color="success",
    dark=True,
)


# -------------------------------------- APP LAYOUT ---------------------------------------------------#
app.layout = html.Div(children=[navbar,

    dbc.Row([dbc.Col(html.P('Last updated on: ' + str(today_formatted_text), \
        style={"fontSize":14, 'color':'grey'}),width=10)],justify='center'),

    #INDICATOR
    
    dbc.Row([dbc.Col(
        dcc.Graph(figure = fig_indicator)
    ,width=10)],justify='center'),

    #ACTIVE & CLOSED CASES CARDS

    dbc.Row([
        dbc.Col(
            card_active_cases,
            width = {"size": 4, "offset":2}
        ),
        dbc.Col(
            card_closed_cases,
            width = {"size": 4}
        )
    ]),

    html.Br(),
    html.Br(),

    dbc.Row([dbc.Col(html.H5('COVID Situation by Countries'),width=10)],justify='center'),
    html.Br(),

    #DROPDOWN COUNTRIES

    dbc.Row([
        dbc.Col(
            dropdown_countries,
            width = 8        
        )
    ], justify = 'center'),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dcc.Graph(id='line-chart-confirmed')       
            )
        ),
        dbc.Col(
            dbc.Card(
                dcc.Graph(id='line-chart-recovered')       
            )
        )
    ], justify = 'center'),

 
 
    #RECOVERED AND CONFIRMED CASES GRAPHS

    html.Br(),
    html.Br(),

    dbc.Row([dbc.Col(html.H5('Coronavirus Tracker: Find latest updates!'),\
        width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("The coronavirus COVID-19 is affecting 219 countries \
        and territories. The day is reset after midnight GMT+0."),width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("The list of countries and their regional \
        classification is based on the United Nations Geoscheme."),width=10)],justify='center'),
    

    #TABLE

    dbc.Row([
        dbc.Col(
            table_covid,
            width = 10
        )
    ],justify='center'),


    html.Br(),
    dbc.Row([dbc.Col(html.H5('World Map with Confirmed COVID-19 Cases'),width=10)],justify='center'),
    html.Br(),

    # RADIO BUTTONS

    dbc.Row([
        dbc.Col(
            radio_buttons_world,
            width = 10
        )
    ],justify='center'),

    html.Br(),
    
    # WORLD GRAPH

    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id = 'update-world-graph'
            ),
            width = 10
        )
    ],justify='center'),

   
    html.Br(),
    dbc.Row([dbc.Col(html.H5('Vaccination timeline '),\
                        width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("Vaccination has started all over the world with countries providing vaccine to their citizens.")\
                        ,width=10)],justify='center'),
    dbc.Row([dbc.Col(html.P("The rollout was done on phase wise basis based on the age and health condition of the people.")\
                        ,width=10)],justify='center'),
    
    #DROPDOWN VACCINE TIMELINE 
    
    dbc.Row([
        dbc.Col(
            dropdown_vaccine_timeline,
            width = 10
        )
    ],justify='center'),


    #VACCINE TIMELINE GRAPH

    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id='vaccine-timeline'
            ),
            width = 10
        )
    ],justify='center'),


    dbc.Row([dbc.Col(html.H5('Current Vaccination Status for Different Countries'),\
        width=10)],justify='center'),
    
    #RADTIO BUTTON VACCINE
    
    dbc.Row([
        dbc.Col(
            radio_buton_vaccine,
            width = 10
        )
    ],justify='center'),
    
    #BAR GRAPH VACCINES

    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id = "update-vaccine"
            ),
            width = 10
        )
    ],justify='center'),

    html.Br(),
    dbc.Row([dbc.Col(html.H5('Find latest updates related to the COVID-19 Pandemic'),\
        width=10)],justify='center'),
    html.Br(),

    #NEWS CARDS

    dbc.Row(
        news_card_list
    ,justify='center'
    ),

    ]
    )




#------------------------- DEFINING CALL BACKS ------------------------------#


# LINE CHART CONFIRMED 

@app.callback(
    Output("line-chart-confirmed", "figure"),
    [Input('dropdown', 'value')]
)
def update_line_chart_confirmed(countries):
    df_filtered_date = df_time_confirmed[df_time_confirmed['Country/Region'].isin(countries)]
    fig = px.line(df_filtered_date, x='date', y='value', color='Country/Region',
        title='Confirmed Cases', line_shape = 'hv' )
    return fig

# LINE CHART RECOVERED

@app.callback(
    Output("line-chart-recovered", "figure"),
    [Input('dropdown', 'value')]
)
def update_line_chart_recovered(countries):
    df_filtered_date = df_time_recovered[df_time_recovered['Country/Region'].isin(countries)]
    fig = px.line(df_filtered_date, x='date', y='value', color='Country/Region',
        title='Recovered Cases', line_shape = 'hv' )
    return fig


# WORLD GRAPH

@app.callback(
    Output("update-world-graph", "figure"),
    [Input('radio_button_world', 'value')]
)
def update_world_graph(plot_type):
    if plot_type == 'scatter':
        return fig_world_scatter
    elif plot_type == 'choropleth':
        return fig_world

# VACCINE TIMELINE

@app.callback(
    Output("vaccine-timeline", "figure"),
    [Input('dropdown_vaccine_timeline', 'value')]
)
def vaccine_timeline(country):
    df_vacc_filtered = df_vacc[df_vacc['location'] == country]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x = df_vacc_filtered['date'],
            y = df_vacc_filtered['total_vaccinations'],
            fill = 'tonexty',
            name = 'Total Vaccinations'
        )
    )

    fig.add_trace(
        go.Scatter(
            x = df_vacc_filtered['date'],
            y = df_vacc_filtered['people_fully_vaccinated'],
            fill = 'tozeroy',
            name = 'People Fully Vaccinated'
        )
    )

    fig.update_layout(
        xaxis_title = 'Date',
        yaxis_title = 'Total Count'
    )

    return fig


# VACCINATION STATUS


@app.callback(
    Output("update-vaccine", "figure"),
    [Input('radio_button_vaccine', 'value')]
)
def vaccination_status(parameter):
    fig = px.bar(
        df_vacc_max,
        x = 'location',
        y = parameter,
        color_discrete_sequence = ['green'],
        height = 650
    )
    return fig

#------------------------------ RUNNING THE SERVER --------------------------------#
app.run_server(debug=True)


