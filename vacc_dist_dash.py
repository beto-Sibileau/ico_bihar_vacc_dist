#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import base64
from dash import Dash, dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date, datetime
import io
import pandas as pd
import plotly.express as px
import requests


# In[ ]:


# geo-json file transformed from justinelliotmeyers github
url_geo = "https://github.com/beto-Sibileau/ico_bihar_vacc_dist/raw/main/India_District_10_BR.geojson"
response_geo = requests.get(url_geo)
geofile = response_geo.json()

# district names geo-json/df mapping
data_2_map_district = {
    "ARARIA": "Araria",
    "ARWAL": "Arwal",
    "AURANGABAD": "Aurangabad",
    "BANKA": "Banka",
    "BEGUSARAI": "Begusarai",
    "BHAGALPUR": "Bhagalpur",
    "BHOJPUR": "Bhojpur",
    "BUXAR": "Buxar",
    "CHAMPARANE EAST": "Purba Champaran",
    "CHAMPARANE WEST": "Pashchim Champaran",
    "DARBHANGA": "Darbhanga",
    "GAYA": "Gaya",
    "GOPALGANJ": "Gopalganj",
    "JAMUI": "Jamui",
    "JEHANABAD": "Jehanabad",
    "KAIMUR": "Kaimur (bhabua)",
    "KATIHAR": "Katihar",
    "KHAGARIA": "Khagaria",
    "KISHANGANJ": "Kishanganj",
    "LAKHISARAI": "Lakhisarai",
    "MADHEPURA": "Madhepura",
    "MADHUBANI": "Madhubani",
    "MUNGER": "Munger",
    "MUZAFFARPUR": "Muzaffarpur",
    "NALANDA": "Nalanda",
    "NAWADA": "Nawada",
    "PATNA": "Patna",
    "PURNIA": "Purnia",
    "ROHTAS": "Rohtas",
    "SAHARSA": "Saharsa",
    "SAMASTIPUR": "Samastipur",
    "SARAN": "Saran",
    "SHEIKHPURA": "Sheikhpura",
    "SHEOHAR": "Sheohar",
    "SITAMARHI": "Sitamarhi",
    "SIWAN": "Siwan",
    "SUPAUL": "Supaul",
    "VAISHALI": "Vaishali",
}


# In[ ]:


# dbc button: upload csv
bt_up = dcc.Upload(
    dbc.Button(
        html.P(
            ["Click to Upload ", html.Code("csv"), " File"],
            style={"margin-top": "12px", "fontWeight": "bold",},
        ),
        id="btn",
        class_name="me-1",
        outline=True,
        color="info",
    ),
    id="upload-data",
)

# dash date picker
date_picker = dcc.DatePickerRange(
    id="my-date-picker-range",
    min_date_allowed=date(2021, 10, 26),
    max_date_allowed=date(2022, 2, 27),
    # initial_visible_month=date(2022, 1, 1),
    start_date=date(2021, 10, 26),  # date(2022, 1, 1), #
    end_date=date(2022, 2, 27),  # date(2022, 1, 31), #
    display_format="Do MMM YYYY",
    style={"fontSize": 20},
)

# dbc data upload row
upload_row = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.P(
                            "Load Vaccine Distribution",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "18px",
                                "marginBottom": "10px",
                                "textAlign": "center",
                            },
                        ),
                        bt_up,
                        html.Div(
                            id="uploading-state",
                            className="output-uploading-state",
                            style={"color": "DarkGreen", "textAlign": "center",},
                        ),
                    ]
                ),
                width="auto",
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P(
                            "Click to Select Dates",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "18px",
                                "marginBottom": "20px",
                                "textAlign": "center",
                            },
                        ),
                        date_picker,
                    ]
                ),
                width="auto",
            ),
        ],
        justify="evenly",
        align="start",
    ),
    fluid=True,
)


# In[ ]:


# function to return cards layout
# dbc kpi card: https://www.nelsontang.com/blog/2020-07-02-dash-bootstrap-kpi-card/
def create_card(card_title, card_num):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(card_title, className="card-title"),
                    html.P(
                        children="N/A",
                        className="card-text",
                        id=f"card-top-list-{card_num}",
                    ),
                    # note there's card-text bootstrap class ...
                    # html.P(
                    #     "Target: $10.0 M",
                    #     className="card-target",
                    # ),
                    # html.Span([
                    #     html.I(className="fas fa-arrow-circle-up up"),
                    #     html.Span(" 5.5% vs Last Year",
                    #     className="up")
                    # ])
                ]
            )
        ],
        color="info",
        outline=True,
    )
    return card


# cards to display top districts and blocks
cards_row = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                create_card("Vaccine Distribution Top 10 Districts", 1), width="auto"
            ),
            dbc.Col(create_card("Vaccine Distribution Top 10 Blocks", 2), width="auto"),
        ],
        justify="evenly",
    ),
    fluid=True,
)


# In[ ]:


# dictionary for plotly: label with no figure
label_no_fig = {
    "layout": {
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [
            {
                "text": "No matching data",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 28},
            }
        ],
    }
}


# In[ ]:


# dbc select: KPI map
dd_kpi_map = dbc.Select(id="my-map-dd", options=[], value="",)

# hard-coded columns: presence of officials
col_officials = ["MOIC_pres", "MO_pres", "BHM_pres", "BCM_pres", "CCM_pres"]

# hard-coded options for map
kpi_map_value = ["Sess_plan", "Sess_with_vacc", "Sess_with_vacc_ratio", *col_officials]
kpi_map_label = [
    "Total number of planned sessions",
    "Total number of sessions where the vaccine distribution was done by 8.00 am",
    "Proportion of sessions where the vaccine distribution was done by 8.00 am [%]",
    "Proportion of sessions with presence of MOIC officials during the vaccine distribution [%]",
    "Proportion of sessions with presence of MO officials during the vaccine distribution [%]",
    "Proportion of sessions with presence of BHM officials during the vaccine distribution [%]",
    "Proportion of sessions with presence of BCM officials during the vaccine distribution [%]",
    "Proportion of sessions with presence of CCM officials during the vaccine distribution [%]",
]
map_options = [{"label": l, "value": v} for l, v in zip(kpi_map_label, kpi_map_value)]

# dbc map/maps row
map_row = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                "Key Performance Indicators: District-wise map",
                                style={
                                    "fontWeight": "bold",  # 'normal', #
                                    "textAlign": "left",  # 'center', #
                                    # 'paddingTop': '25px',
                                    "color": "DeepSkyBlue",
                                    "fontSize": "18px",
                                    "marginBottom": "10px",
                                },
                            ),
                            dd_kpi_map,
                        ]
                    ),
                    width="auto",
                ),
            ],
            justify="start",
            align="start",
            style={"paddingLeft": "25px", "marginBottom": "30px",},
        ),
        dbc.Row(
            [dbc.Col(dcc.Graph(id="district-plot", figure=label_no_fig), width=7),],
            justify="evenly",
            align="start",
        ),
    ],
    fluid=True,
)


# In[ ]:


# # dbc select: trends
# dd_kpi_trends = dbc.Select(
#     id="my-trends-dd",
#     options=[],
#     value="",
# )

# dcc dropdown: trends --> dcc allows multi, styling not as dbc
dd_kpi_trends = dcc.Dropdown(id="my-trends-dd", options=[], value="", multi=True,)

# hard-coded options for trends
kpi_with_trend_value = ["Sess_plan", "Sess_with_vacc", *col_officials]
kpi_with_trend_label = [
    "Trend in the total number of planned sessions",
    "Trend in the total number of sessions where the vaccine distribution was done by 8.00 am",
    "Trend in the presence of MOIC officials during the vaccine distribution",
    "Trend in the presence of MO officials during the vaccine distribution",
    "Trend in the presence of BHM officials during the vaccine distribution",
    "Trend in the presence of BCM officials during the vaccine distribution",
    "Trend in the presence of CCM officials during the vaccine distribution",
]
trend_options = [
    {"label": l, "value": v} for l, v in zip(kpi_with_trend_label, kpi_with_trend_value)
]

# # dbc select: districts
# dd_districts = dbc.Select(
#     id="my-districts-dd",
#     options=[],
#     value="",
# )

# dcc dropdown: districts --> dcc allows multi, styling not as dbc
dd_districts = dcc.Dropdown(id="my-districts-dd", options=[], value="", multi=True,)

# hard-coded options for districts
district_options = [{"label": k, "value": k} for k in data_2_map_district]

# dbc ButtonGroup with RadioItems
button_group = html.Div(
    [
        dbc.RadioItems(
            id="radios",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-info",
            labelCheckedClassName="active",
            options=[
                {"label": "Monthly", "value": "M"},
                {"label": "Weekly", "value": "W"},
                {"label": "Daily", "value": "D"},
            ],
            value="D",
        ),
    ],
    className="radio-group",
)

# dbc trends row
trends_row = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                "Key Performance Indicators: District-wise trends",
                                style={
                                    "fontWeight": "bold",  # 'normal', #
                                    "textAlign": "left",  # 'center', #
                                    # 'paddingTop': '25px',
                                    "color": "DeepSkyBlue",
                                    "fontSize": "18px",
                                    "marginBottom": "10px",
                                },
                            ),
                            dd_kpi_trends,
                        ],
                        style={"font-size": "85%"},
                    ),
                    width={"size": 5},  # width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [dd_districts], style={"font-size": "85%"}
                    ),  # , className="dash-bootstrap"
                    width={"size": 4, "offset": 1},
                ),
            ],
            justify="start",
            align="end",
            style={"paddingLeft": "25px", "marginBottom": "30px",},
        ),
        dbc.Row(
            [dbc.Col(button_group, width="auto"),],
            justify="start",
            align="start",
            style={"paddingLeft": "25px"},
        ),
        dbc.Row(
            [dbc.Col(dcc.Graph(id="trends-plot", figure=label_no_fig), width=7),],
            justify="evenly",
            align="start",
        ),
    ],
    fluid=True,  # className="dash-bootstrap"
)


# In[ ]:


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
fontawesome_stylesheet = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
# Build App
# app = JupyterDash(__name__)
# app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app = Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, fontawesome_stylesheet]
)

# to deploy using WSGI server
server = app.server
# app tittle for web browser
app.title = "UNICEF Bihar Vaccine Distribution"

# App Layout
app.layout = html.Div(
    [
        # title Div
        html.Div(
            [
                html.H6(
                    "UNICEF Bihar Vaccine Distribution",
                    style={
                        "fontWeight": "bold",
                        "textAlign": "center",
                        "paddingTop": "25px",
                        "color": "white",
                        "fontSize": "32px",
                    },
                ),
            ],
            style={
                "height": "100px",
                "width": "100%",
                "backgroundColor": "DeepSkyBlue",
                "margin-left": "auto",
                "margin-right": "auto",
                "margin-top": "15px",
            },
        ),
        # div upload row
        html.Div([upload_row], style={"paddingTop": "20px",},),
        html.Hr(
            style={
                "color": "DeepSkyBlue",
                "height": "3px",
                "margin-top": "30px",
                "margin-bottom": "0",
            }
        ),
        # div 2-cards row
        dcc.Loading(
            children=html.Div(
                [cards_row],
                style={
                    "paddingTop": "30px",
                    # 'paddingBottom': '30px',
                },
            ),
            id="loading-kpis",
            type="circle",
            fullscreen=True,
        ),
        html.Hr(
            style={
                "color": "DeepSkyBlue",
                "height": "3px",
                "margin-top": "30px",
                "margin-bottom": "0",
            }
        ),
        # div map row
        dcc.Loading(
            children=html.Div([map_row], style={"paddingTop": "20px",},),
            id="loading-map",
            type="circle",
            fullscreen=True,
        ),
        html.Hr(
            style={
                "color": "DeepSkyBlue",
                "height": "3px",
                "margin-top": "30px",
                "margin-bottom": "0",
            }
        ),
        # div trends row (no loading added)
        html.Div([trends_row], style={"paddingTop": "20px",},),
        # dbc Modal: output msg from load button - wraped by Spinner
        dcc.Loading(
            children=dbc.Modal(
                [
                    dbc.ModalHeader(
                        dbc.ModalTitle("Upload Message"), close_button=False
                    ),
                    dbc.ModalBody(id="my-modal-body"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="btn-close", class_name="ms-auto")
                    ),
                ],
                id="my-modal",
                is_open=False,
                keyboard=False,
                backdrop="static",
                scrollable=True,
                centered=True,
            ),
            id="loading-modal",
            type="circle",
            fullscreen=True,
        ),
        # hidden div: ouput msg from load button
        html.Div(id="output-data-upload", style={"display": "none"}),
        # hidden div: share csv-df in Dash
        html.Div(id="csv-df", style={"display": "none"}),
        # hidden div: share calculated kpis for districts
        html.Div(id="df-district-kpis", style={"display": "none"}),
        # hidden div: share calculated kpis for blocks
        html.Div(id="df-block-kpis", style={"display": "none"}),
        # hidden div: share calculated kpis for trends (districts)
        html.Div(id="df-trends-kpis", style={"display": "none"}),
    ]
)


# In[ ]:


# showing Loading trick for dcc Upload? - Also displays loaded filename
@app.callback(
    Output("uploading-state", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def upload_triggers_spinner(_, filename):
    return filename


# In[ ]:


def read_csv_file(contents, filename, date):
    # decoded as proposed in Dash Doc
    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename:
            # Assume user uploaded a csv file
            # read csv into dataframe: appointments
            vacc_dist_df = pd.read_csv(io.BytesIO(decoded), parse_dates=["Date"])
        else:
            # Warn user hasn't uploaded a csv file
            return (
                ["Vaccine Distribution must be a ", html.Code("csv"), " File",],
                {},
            )
    except Exception as e:
        print(e)
        # Warn user csv file hasn't been read
        return (
            f"There was an error processing {filename}",
            {},
        )
        
    # simple validation: col_2_check must be in dataframe
    col_2_check = [
        "Date",
        "S_Num",
        "District",
        "Block",
        "Sess_plan",
        "Sess_with_vacc",
        "Notes",
    ]
    col_2_check.extend(col_officials)
    col_check = [col in vacc_dist_df.columns for col in col_2_check]
    # missing columns
    miss_col = [i for (i, v) in zip(col_2_check, col_check) if not v]

    # return ingestion message and read csv
    return (
        (
            [
                f"Uploaded File is {filename}",
                html.Br(),
                f"Last modified datetime is {datetime.fromtimestamp(date)}",
            ],
            # csv to json: sharing data within Dash
            vacc_dist_df.to_json(orient="split"),
        )
        if all(col_check)
        else (
            [
                f"Uploaded File is {filename}",
                html.Br(),
                f"Last modified datetime is {datetime.fromtimestamp(date)}",
                html.Br(),
                f"KPIs not calculated. Missing columns: {miss_col}",
            ],
            # no dataframe return
            {},
        )
    )


# In[ ]:


@app.callback(
    Output("output-data-upload", "children"),
    Output("csv-df", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
    prevent_initial_call=True,
)
def wrap_csv_read(loaded_file, file_name, file_last_mod):

    # coded as proposed in Dash Doc
    # callback sees changes in content only (eg: not same content with different filename)
    if loaded_file is not None:
        # returned: (msg_out, app_json)
        return read_csv_file(loaded_file, file_name, file_last_mod)


# In[ ]:


@app.callback(
    Output("my-modal-body", "children"),
    Output("my-modal", "is_open"),
    Input("output-data-upload", "children"),
    Input("btn-close", "n_clicks"),
    State("my-modal", "is_open"),
    prevent_initial_call=True,
)
def update_modal(msg_in, click_close, is_open):

    # identify callback context
    triger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

    # specify action by trigger
    if "data-upload" in triger_id:
        return (
            html.P(msg_in),
            not is_open,
        )
    else:
        # button close
        return {}, not is_open


# In[ ]:


# vaccine distribution: aggregate planned sessions in dates
def district_calc(df, ini_date, end_date):

    # json to dataframe
    vacc_df = pd.read_json(df, orient="split", convert_dates=["Date"],)

    # filter `Date` within dates
    query_dates = [
        "`Date` >= @ini_date",
        "`Date` <= @end_date",
    ]
    df_in_dates = vacc_df.query("&".join(query_dates)).reset_index(drop=True)

    # no entry between dates: return empty
    if df_in_dates.empty:
        return "N/A", "N/A", {}, {}, [], "", [], "", [], "", {}

    # kpi: District/Blocks sessions and vacc distribution - Count rows in Notes
    top_block_df = (
        df_in_dates.groupby(["District", "Block"], sort=False)
        .agg({"Sess_plan": "sum", "Sess_with_vacc": "sum", "Notes": "size"})
        .astype({"Sess_plan": "int64", "Sess_with_vacc": "int64"})
    )
    top_distr_df = (
        df_in_dates.groupby("District", sort=False)
        .agg({"Sess_plan": "sum", "Sess_with_vacc": "sum", "Notes": "size"})
        .astype({"Sess_plan": "int64", "Sess_with_vacc": "int64"})
    )

    # kpi: District/Blocks % sessions with vacc distribution
    top_block_df["Sess_with_vacc_ratio"] = round(
        top_block_df.Sess_with_vacc / top_block_df.Sess_plan * 100
    )
    top_distr_df["Sess_with_vacc_ratio"] = round(
        top_distr_df.Sess_with_vacc / top_distr_df.Sess_plan * 100
    )

    # kpi: District/Blocks % sessions with presence of officials
    for off_col in col_officials:
        is_present = df_in_dates[off_col].str.contains(
            "y", case=False, regex=False, na=False
        )
        top_block_df[off_col] = round(
            df_in_dates[is_present]
            .groupby(["District", "Block"], sort=False)
            .agg({"Notes": "size"})
            .Notes
            / top_block_df.Notes
            * 100
        )
        top_distr_df[off_col] = round(
            df_in_dates[is_present]
            .groupby("District", sort=False)
            .agg({"Notes": "size"})
            .Notes
            / top_distr_df.Notes
            * 100
        )
        # normalize presence of officials
        df_in_dates.loc[is_present, off_col] = "YES"
        df_in_dates.loc[~is_present, off_col] = "NO"

    # sort values for kpi TOP District/Blocks
    top_block_df.reset_index(inplace=True)
    top_block_df.sort_values(
        "Sess_with_vacc", ascending=False, ignore_index=True, inplace=True,
    )
    top_distr_df.reset_index(inplace=True)
    top_distr_df.sort_values(
        "Sess_with_vacc", ascending=False, ignore_index=True, inplace=True,
    )

    # kpi: District sessions and vacc distribution - Time-series: df_in_dates refactor
    # drop not relevant columns
    df_in_dates.drop(columns=["S_Num", "Block", "Notes"], inplace=True)
    # transform presence of officials to numeric
    df_in_dates.replace({"YES": 1, "NO": 0}, inplace=True, regex=False)

    # daily aggregate by district and melt kpis (wide-to-long transform)
    distr_daily_df = (
        (
            df_in_dates.groupby(["Date", "District"], sort=False)
            .agg("sum")
            .astype("int64")
        )
        .reset_index()
        .melt(id_vars=["Date", "District"], value_vars=kpi_with_trend_value,)
    )
    # assign 'daily' to new column: time frequency
    distr_daily_df["Freq"] = "D"

    # weekly aggregate by district and melt kpis (wide-to-long transform)
    distr_weekly_df = (
        (
            df_in_dates.set_index("Date")
            .groupby([pd.Grouper(freq="W"), "District"], sort=False)
            .agg("sum")
            .astype("int64")
        )
        .reset_index()
        .melt(id_vars=["Date", "District"], value_vars=kpi_with_trend_value,)
    )
    # assign 'weekly' to new column: time frequency
    distr_weekly_df["Freq"] = "W"

    # monthly aggregate by district and melt kpis (wide-to-long transform)
    distr_monthly_df = (
        (
            df_in_dates.set_index("Date")
            .groupby([pd.Grouper(freq="M"), "District"], sort=False)
            .agg("sum")
            .astype("int64")
        )
        .reset_index()
        .melt(id_vars=["Date", "District"], value_vars=kpi_with_trend_value,)
    )
    # assign 'monthly' to new column: time frequency
    distr_monthly_df["Freq"] = "M"

    # return kpis calculated and dropdown options
    return (
        [
            html.Ol(
                id="top-d-list",
                children=[
                    html.Li(distr) for distr in top_distr_df.District.values[:10]
                ],
            )
        ],
        [
            html.Ol(
                id="top-b-list",
                children=[
                    html.Li("-".join([distr, block]))
                    for distr, block in zip(
                        top_block_df.District.values[:10],
                        top_block_df.Block.values[:10],
                    )
                ],
            )
        ],
        # csv to json: sharing data within Dash
        top_distr_df.to_json(orient="split"),
        # csv to json: sharing data within Dash
        top_block_df.to_json(orient="split"),
        map_options,
        "Sess_plan",
        trend_options,
        "Sess_plan",
        district_options,
        "ARARIA",
        # csv to json: sharing data within Dash
        pd.concat(
            [distr_daily_df, distr_weekly_df, distr_monthly_df], ignore_index=True
        ).to_json(orient="split"),
    )


# In[ ]:


@app.callback(
    Output("card-top-list-1", "children"),
    Output("card-top-list-2", "children"),
    Output("df-district-kpis", "children"),
    Output("df-block-kpis", "children"),
    Output("my-map-dd", "options"),
    Output("my-map-dd", "value"),
    Output("my-trends-dd", "options"),
    Output("my-trends-dd", "value"),
    Output("my-districts-dd", "options"),
    Output("my-districts-dd", "value"),
    Output("df-trends-kpis", "children"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("btn-close", "n_clicks"),
    State("csv-df", "children"),
    prevent_initial_call=True,
)
def update_districts(start_date, end_date, _, vacc_df):

    # file not available or inconsistent dates
    if not vacc_df or (start_date > end_date):
        return "N/A", "N/A", {}, {}, [], "", [], "", [], "", {}
    else:
        return district_calc(vacc_df, start_date, end_date)


# In[ ]:


# function to avoid figure display inline
def update_cm_fig(cm_fig):
    cm_fig.update_geos(fitbounds="locations", visible=False)
    cm_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return cm_fig


# use dropdown value to update indicator plotted in map (district-wise)
def display_in_map(kpi_df, dd_value):

    # json to dataframe
    kpi_df = pd.read_json(kpi_df, orient="split")

    # district vaccine distribution map
    cmap_fig = px.choropleth(
        kpi_df[["District", dd_value]].merge(
            pd.DataFrame.from_dict(data_2_map_district, orient="index")
            .reset_index()
            .rename(columns={"index": "District", 0: "distr_geo_label"}),
            on="District",
            how="left",
            sort=False,
        ),
        geojson=geofile,
        featureidkey="properties.dtname",  # 'properties.ST_NM', #
        locations="distr_geo_label",
        color=dd_value,
        color_continuous_scale="RdBu",
        # color_discrete_map={'red':'red', 'orange':'orange', 'green':'green'},
        hover_data=[dd_value],
        projection="mercator",
    )

    return update_cm_fig(cmap_fig)


# In[ ]:


@app.callback(
    Output("district-plot", "figure"),
    Input("my-map-dd", "value"),
    State("df-district-kpis", "children"),
    prevent_initial_call=True,
)
def update_map(dd_value, distr_kpi_df):

    # file not available or inconsistent dates
    if not distr_kpi_df or (dd_value == ""):
        return label_no_fig
    else:
        return display_in_map(distr_kpi_df, dd_value)


# In[ ]:


# use dropdown values to update trendlines (district-wise)
def display_in_line(trends_df, dd_kpi, dd_distr, freq_val):

    # json to dataframe, query by dropdown values
    query_by_dd = "District in @dd_distr & variable in @dd_kpi & Freq == @freq_val"
    distr_trends_df = (
        pd.read_json(trends_df, orient="split", convert_dates=["Date"],)
        .query(query_by_dd)
        .sort_values(["Date", "District", "variable"], ignore_index=True,)
        .set_index(["District", "variable"])
    )

    if distr_trends_df.empty:
        return label_no_fig
    else:
        return px.line(
            distr_trends_df,
            x="Date",
            y="value",
            color=list(distr_trends_df.index),
            line_shape="spline",
            render_mode="svg,",
            hover_data=["value"],
        ).update_traces(mode="lines+markers")


# In[ ]:


@app.callback(
    Output("trends-plot", "figure"),
    Input("my-trends-dd", "value"),
    Input("my-districts-dd", "value"),
    Input("radios", "value"),
    State("df-trends-kpis", "children"),
    prevent_initial_call=True,
)
def update_trends(dd_kpi, dd_distr, freq_value, distr_trends_df):

    # file not available
    if not distr_trends_df or not dd_kpi or not dd_distr:
        return label_no_fig
    else:
        return display_in_line(distr_trends_df, dd_kpi, dd_distr, freq_value)


# In[ ]:


if __name__ == "__main__":
    app.run_server(debug=True)
