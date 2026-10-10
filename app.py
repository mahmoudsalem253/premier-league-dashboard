

from dash import (
    Dash,
    Input,
    Output,
    dcc,
    html,
    dash_table
)
import plotly.express as px

from data_cleaning import (
    clean_standings,
    clean_scorers
)



standings = clean_standings()
scorers = clean_scorers()

app = Dash(__name__)
app.title = "Premier League Analytics"




table_columns = [
    "Position",
    "Team",
    "Played",
    "Won",
    "Drawn",
    "Lost",
    "Goals For",
    "Goals Against",
    "Goal Difference",
    "Points"
]

teams = standings["Team"].dropna().tolist()

team_options = [
    {"label": "All Teams", "value": "All Teams"}
]

team_options.extend([
    {"label": team, "value": team}
    for team in teams
])

total_teams = int(standings["Team"].nunique())

# Each match normally contributes two team appearances.
total_matches = int(standings["Played"].sum() // 2)

total_goals = int(standings["Goals For"].sum())

average_goals = (
    round(total_goals / total_matches, 2)
    if total_matches > 0
    else 0
)



def summary_card(title, value):
    return html.Div(
        [
            html.P(title, className="card-title"),
            html.H2(
                f"{value:,}",
                className="card-value"
            )
        ],
        className="summary-card"
    )


table_style = {
    "overflowX": "auto"
}

header_style = {
    "backgroundColor": "#142D4E",
    "color": "white",
    "fontWeight": "bold",
    "textAlign": "center",
    "padding": "10px"
}

cell_style = {
    "textAlign": "center",
    "padding": "10px",
    "minWidth": "65px",
    "whiteSpace": "normal",
    "height": "auto"
}



app.layout = html.Div(
    [

      
        html.H1(
            "Premier League Analytics Dashboard",
            className="main-title"
        ),

        html.P(
            "Football statistics collected from BBC Sport",
            className="subtitle"
        ),

       
        html.Div(
            [
                summary_card(
                    "Teams",
                    total_teams
                ),
                summary_card(
                    "Matches Played",
                    total_matches
                ),
                summary_card(
                    "Goals Scored",
                    total_goals
                ),
                summary_card(
                    "Avg. Goals / Match",
                    average_goals
                )
            ],
            className="summary-container"
        ),

        html.H2("Explore Teams"),

        html.Label(
            "Select a team:",
            className="filter-label"
        ),

        dcc.Dropdown(
            id="team-dropdown",
            options=team_options,
            value="All Teams",
            clearable=False,
            className="team-dropdown"
        ),

        # League standings table
        html.H2("Premier League Table"),

        dash_table.DataTable(
            id="league-table",
            columns=[
                {"name": column, "id": column}
                for column in table_columns
            ],
            data=standings[
                table_columns
            ].to_dict("records"),
            sort_action="native",
            filter_action="native",
            page_size=10,
            style_table=table_style,
            style_header=header_style,
            style_cell=cell_style,
            style_data_conditional=[
                {
                    "if": {
                        "filter_query": "{Position} = 1"
                    },
                    "backgroundColor": "#D4EDDA",
                    "fontWeight": "bold"
                }
            ]
        ),

      
        html.Div(
            [
                dcc.Graph(id="points-chart"),
                dcc.Graph(id="goals-chart")
            ],
            className="charts-container"
        ),

   
        html.H2("Premier League Top Scorers"),

        dash_table.DataTable(
            id="scorers-table",
            columns=[
                {"name": column, "id": column}
                for column in scorers.columns
                if column in [
                    "Player",
                    "Goals",
                    "Assists",
                    "Played"
                ]
            ],
            data=scorers.head(10).to_dict("records"),
            sort_action="native",
            page_size=10,
            style_table=table_style,
            style_header=header_style,
            style_cell=cell_style
        ),

        # Footer
        html.P(
            "Educational project | Data sourced from BBC Sport. "
            "Statistics reflect the last successful scrape.",
            className="footer"
        )

    ],
    className="dashboard"
)


@app.callback(
    Output("league-table", "data"),
    Output("points-chart", "figure"),
    Output("goals-chart", "figure"),
    Input("team-dropdown", "value")
)
def update_dashboard(selected_team):

    # Filter the league table and goals chart.
    if selected_team == "All Teams":
        filtered = standings.copy()
    else:
        filtered = standings[
            standings["Team"] == selected_team
        ].copy()

    points_data = standings.sort_values(
        "Points",
        ascending=True
    )

    points_fig = px.bar(
        points_data,
        x="Points",
        y="Team",
        orientation="h",
        title="Points by Team",
        color="Points",
        color_continuous_scale="Blues",
        hover_data=[
            "Played",
            "Won",
            "Drawn",
            "Lost"
        ]
    )

    points_fig.update_layout(
        template="plotly_white",
        xaxis_title="Points",
        yaxis_title="Team",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=60, b=30)
    )

    goals_data = filtered.sort_values(
        "Goals For",
        ascending=True
    )

    goals_fig = px.bar(
        goals_data,
        x="Goals For",
        y="Team",
        orientation="h",
        title="Goals Scored by Team",
        color="Goals For",
        color_continuous_scale="Greens",
        hover_data=[
            "Goals Against",
            "Goal Difference"
        ]
    )

    goals_fig.update_layout(
        template="plotly_white",
        xaxis_title="Goals Scored",
        yaxis_title="Team",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=60, b=30)
    )

    return (
        filtered[table_columns].to_dict("records"),
        points_fig,
        goals_fig
    )




if __name__ == "__main__":
    app.run(debug=True)
