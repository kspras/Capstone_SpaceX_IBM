# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df['Payload Mass (kg)'] = pd.to_numeric(spacex_df['Payload Mass (kg)'], errors='coerce')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get unique launch sites from the dataset
launch_sites = spacex_df['Launch Site'].unique()

# Generate dropdown options dynamically
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]
# Create a dash application
app = dash.Dash(__name__)



# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                              options=dropdown_options,
                                              value='ALL',
                                              placeholder="Select a Launch site",
                                              searchable=True
                                              ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, 
                                                max=10000, 
                                                step=1000,
                                                marks={0: '0',
                                                    2500: '2500',
                                                    5000: '5000',
                                                    7500: '7500',
                                                    10000: '10000'},
                                                value=[min_payload, max_payload]
                                ),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# Callback function for pie-chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        #Show total successful launches for each site
        fig = px.pie(
            spacex_df,
            names = 'Launch Site',
            values = 'class',
            title = 'Total Successful launches by Site'
        )
        fig.update_layout(
            title={
                'font': {'size':24, 'color':'blue'}
            }
        )
        return fig
    else:
        #Show Success Vs Failure for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['Outcome', 'Count']
        counts['Outcome'] = counts['Outcome'].replace({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            counts,
            names = 'Outcome',
            values = 'Count',
            title = f'Success Vs Failure Launches for the site: {entered_site}'
        )
        fig.update_layout(
            title={
                'font': {'size':24, 'color':'blue'}
            }
        )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
    Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range

    # #Filter by Payload range
    # filtered_df = spacex_df[
    #     (spacex_df['Payload Mass (kg)' >= low]) &
    #     (spacex_df['Payload Mass (kg)' <= high])
    # ]
    # Convert payload column to numeric temporarily
    df = spacex_df.copy()
    df['Payload Mass (kg)'] = pd.to_numeric(df['Payload Mass (kg)'], errors='coerce')

    # Filter by payload range
    filtered_df = df[
        (df['Payload Mass (kg)'] >= low) &
        (df['Payload Mass (kg)'] <= high)
    ]
    #If all sites selected
    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload Mass Vs Success Rate for all sites',
            hover_data=['Launch Site']
        )
        fig.update_layout(
            xaxis_title='Payload Mass (kg)',
            yaxis_title='Launch Outcome (0 = Fail, 1 = Success)'
        )
        return fig
    else:
        #Filter by selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Payload Mass Vs Success Rate for the site: {entered_site}',
            hover_data=['Launch Site']
        )
        fig.update_layout(
            xaxis_title='Payload Mass (kg)',
            yaxis_title='Launch Outcome (0 = Fail, 1 = Success)'
        )
        return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
