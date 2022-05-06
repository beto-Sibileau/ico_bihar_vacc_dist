#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import base64
from dash import Dash, dcc, html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date, datetime
import io
import numpy as np
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


# geo-json file refactor from google datameet group attach: 7f92b3f234ecf846/india%20subdists%202001.zip
url_geo_block = "https://raw.githubusercontent.com/beto-Sibileau/ico_bihar_vacc_dist/main/admin_census_bihar_blocks_refactor.json"
response_geo_block = requests.get(url_geo_block)
geofile_block = response_geo_block.json()

list_of_dict = [a_dict["properties"] for a_dict in geofile_block["features"]]
block_names = [a_polyg["NAME1_"] for a_polyg in list_of_dict]
fids = [a_polyg["FID"] for a_polyg in list_of_dict]

admin_blocks_df = pd.DataFrame({"Fid": fids, "Block_Id": block_names})


# In[ ]:


# dbc button: upload csv
bt_up = dcc.Upload(
    dbc.Button(
        html.P(
            ["Click to Upload ", html.Code("csv"), " File"],
            style={
                "margin-top": "12px",
                "fontWeight": "bold",
            },
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
                            style={
                                "color": "DarkGreen",
                                "textAlign": "center",
                            },
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
                    html.H4(
                        card_title,
                        className="card-title",
                        style={"textAlign": "center"},
                    ),
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
            dbc.Col(create_card("Vaccine Top 10 Divisions", 1), width="auto"),
            dbc.Col(create_card("Vaccine Top 10 Districts", 2), width="auto"),
            dbc.Col(create_card("Vaccine Top 10 Subdivisions", 3), width="auto"),
            dbc.Col(create_card("Vaccine Top 10 Blocks", 4), width="auto"),
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
dd_kpi_map = dbc.Select(
    id="my-map-dd",
    options=[],
    value="",
)

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
                                "Key Performance Indicators: Bihar Administrative Geolocation",
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
            style={
                "paddingLeft": "25px",
                "marginBottom": "30px",
            },
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="district-plot", figure=label_no_fig), width=5),
                dbc.Col(dcc.Graph(id="block-plot", figure=label_no_fig), width=5),
            ],
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
dd_kpi_trends = dcc.Dropdown(
    id="my-trends-dd",
    options=[],
    value="",
    multi=True,
)

# hard-coded options for trends
kpi_with_trend_value = ["Sess_plan", "Sess_with_vacc", "ALL_pres", *col_officials]
kpi_with_trend_label = [
    "Trend in the total number of planned sessions",
    "Trend in the total number of sessions where the vaccine distribution was done by 8.00 am",
    "Trend in the presence of at least one official during the vaccine distribution",
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
dd_districts = dcc.Dropdown(
    id="my-districts-dd",
    options=[],
    value="",
    multi=True,
)

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
            style={
                "paddingLeft": "25px",
                "marginBottom": "25px",
            },
        ),
        dbc.Row(
            [
                dbc.Col(button_group, width="auto"),
            ],
            justify="start",
            align="start",
            style={"paddingLeft": "25px"},
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="trends-plot", figure=label_no_fig), width=7),
            ],
            justify="evenly",
            align="start",
        ),
    ],
    fluid=True,  # className="dash-bootstrap"
)


# In[ ]:


# # dbc select: Pie charts for "presence of officials"
# dd_offic_pie = dbc.Select(
#     id="my-offic-dd",
#     options=[],
#     value="",
# )

# # hard-coded options for pie charts dropdown
# offic_value = ["ALL_pres", *col_officials]
# offic_label = [
#     "Percentage of at-least-one-official presence during the vaccine distribution",
#     "Percentage of MOIC officials presence during the vaccine distribution",
#     "Percentage of MO officials presence during the vaccine distribution",
#     "Percentage of BHM officials presence during the vaccine distribution",
#     "Percentage of BCM officials presence during the vaccine distribution",
#     "Percentage of CCM officials presence during the vaccine distribution",
# ]
# offic_options = [{"label": l, "value": v} for l, v in zip(offic_label, offic_value)]

# dbc select: dynamic selector for "presence of officials" Pie charts
dd_dyn_pie = dbc.Select(
    id="my-dyn-dd",
    options=[],
    value="",
)

# dbc ButtonGroup with RadioItems: drill down admin levels
admin_levels_group = html.Div(
    [
        dbc.RadioItems(
            id="admin-radios",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-info",
            labelCheckedClassName="active",
            options=[
                {"label": "Division", "value": 1},
                {"label": "District", "value": 2},
                {"label": "Subdivision", "value": 3},
                {"label": "Block", "value": 4},
            ],
            value=1,
        ),
    ],
    className="radio-group",
)

# dbc pie chart row: presence of officials
pie_row = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                "Presence of Officials across administrative levels",
                                style={
                                    "fontWeight": "bold",  # 'normal', #
                                    "textAlign": "left",  # 'center', #
                                    # 'paddingTop': '25px',
                                    "color": "DeepSkyBlue",
                                    "fontSize": "18px",
                                    "marginBottom": "10px",
                                },
                            ),
                            dd_dyn_pie,
                        ]
                    ),
                    width="auto",
                ),
                # dbc.Col(
                #     html.Div([dd_dyn_pie]), # , className="dash-bootstrap"
                #     width="auto",
                # ),
            ],
            justify="start",
            align="end",
            style={
                "paddingLeft": "25px",
                "marginBottom": "25px",
            },
        ),
        dbc.Row(
            [
                dbc.Col(admin_levels_group, width="auto"),
            ],
            justify="start",
            align="start",
            style={"paddingLeft": "25px", "marginBottom": "10px"},
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="pie-plot-1", figure=label_no_fig), width="auto"),
                dbc.Col(dcc.Graph(id="pie-plot-2", figure=label_no_fig), width="auto"),
            ],
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
# app = JupyterDash(__name__, external_stylesheets=external_stylesheets)
app = Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, fontawesome_stylesheet]
)
# app = JupyterDash(__name__)

# to deploy using WSGI server
server = app.server
# app tittle for web browser
app.title = "UNICEF Bihar Vaccine Distribution"

# title row
title_row = dbc.Container(
    dbc.Row(
        [
            dbc.Col(
                html.Img(src="assets/logo-unicef-large.svg"),
                width=3,
                # width={"size": 3, "offset": 1},
                style={"paddingLeft": "20px", "paddingTop": "20px"},
            ),
            dbc.Col(
                html.Div(
                    [
                        html.H6(
                            "ICO Bihar Vaccine Distribution",
                            style={
                                "fontWeight": "bold",
                                "textAlign": "center",
                                "paddingTop": "25px",
                                "color": "white",
                                "fontSize": "32px",
                            },
                        ),
                    ]
                ),
                # width='auto',
                width={"size": "auto", "offset": 1},
            ),
        ],
        justify="start",
        align="center",
    ),
    fluid=True,
)

# App Layout
app.layout = html.Div(
    [
        # title Div
        html.Div(
            [title_row],
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
        html.Div(
            [upload_row],
            style={
                "paddingTop": "20px",
            },
        ),
        html.Hr(
            style={
                "color": "DeepSkyBlue",
                "height": "3px",
                "margin-top": "30px",
                "margin-bottom": "0",
            }
        ),
        # div 4-cards row
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
            children=html.Div(
                [map_row],
                style={
                    "paddingTop": "20px",
                },
            ),
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
        html.Div(
            [trends_row],
            style={
                "paddingTop": "20px",
            },
        ),
        html.Hr(
            style={
                "color": "DeepSkyBlue",
                "height": "3px",
                "margin-top": "30px",
                "margin-bottom": "0",
            }
        ),
        # div pies row (no loading added)
        html.Div(
            [pie_row],
            style={
                "paddingTop": "20px",
            },
        ),
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
        # hidden div: share calculations for divisions
        html.Div(id="df-div-kpis", style={"display": "none"}),
        # hidden div: share calculations for Sub_divisions
        html.Div(id="df-subdiv-kpis", style={"display": "none"}),
        # hidden div: share calculated kpis for trends (districts)
        html.Div(id="df-trends-kpis", style={"display": "none"}),
        # hidden div: share selected admin level df for pie chart
        html.Div(id="df-admin-selected", style={"display": "none"}),
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
                [
                    "Vaccine Distribution must be a ",
                    html.Code("csv"),
                    " File",
                ],
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
        "Division",
        "Sub_division",
        "Block_Id",
        "Sub_div_Id",
    ]
    col_2_check.extend(col_officials)
    col_check = [col in vacc_dist_df.columns for col in col_2_check]
    # missing columns
    miss_col = [i for (i, v) in zip(col_2_check, col_check) if not v]

    # missing columns result
    if all(col_check):
        # return ingestion message and csv data
        return (
            [
                f"Uploaded File is {filename}",
                html.Br(),
                f"Last modified datetime is {datetime.fromtimestamp(date)}",
            ],
            # csv to json: sharing data within Dash
            vacc_dist_df.to_json(orient="split"),
        )
    else:
        # return ingestion message and no dataframe
        (
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
    vacc_df = pd.read_json(
        df,
        orient="split",
        convert_dates=["Date"],
    )

    # filter `Date` within dates
    query_dates = [
        "`Date` >= @ini_date",
        "`Date` <= @end_date",
    ]
    df_in_dates = vacc_df.query("&".join(query_dates)).reset_index(drop=True)

    # no entry between dates: return empty
    if df_in_dates.empty:
        return (
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {},
            {},
            {},
            {},
            [],
            "",
            [],
            "",
            [],
            "",
            {},
        )  # , [], "", [], "", {}

    # kpi: District/Blocks sessions and vacc distribution - Count rows in Notes
    top_block_df = (
        df_in_dates.groupby("Block_Id", sort=False)
        .agg({"Sess_plan": "sum", "Sess_with_vacc": "sum", "Notes": "size"})
        .astype({"Sess_plan": "int64", "Sess_with_vacc": "int64"})
    )
    top_distr_df = (
        df_in_dates.groupby("District", sort=False)
        .agg({"Sess_plan": "sum", "Sess_with_vacc": "sum", "Notes": "size"})
        .astype({"Sess_plan": "int64", "Sess_with_vacc": "int64"})
    )
    # kpi: Div/Sub_div sessions and vacc distribution - Count rows in Notes
    top_div_df = (
        df_in_dates.groupby("Division", sort=False)
        .agg({"Sess_plan": "sum", "Sess_with_vacc": "sum", "Notes": "size"})
        .astype({"Sess_plan": "int64", "Sess_with_vacc": "int64"})
    )
    top_subdiv_df = (
        df_in_dates.groupby("Sub_div_Id", sort=False)
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
    is_present_list = []
    for off_col in col_officials:
        is_y_present = df_in_dates[off_col].str.contains(
            "y", case=False, regex=False, na=False
        )
        is_n_present = df_in_dates[off_col].str.contains(
            "n", case=False, regex=False, na=False
        )
        is_present = is_y_present & ~is_n_present
        top_block_df[off_col] = round(
            df_in_dates[is_present]
            .groupby("Block_Id", sort=False)
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

        # add distr/block absolutes
        off_col_abs = off_col + "_abs"
        top_block_df[off_col_abs] = (
            df_in_dates[is_present]
            .groupby("Block_Id", sort=False)
            .agg({"Notes": "size"})
            .Notes
        )
        top_distr_df[off_col_abs] = (
            df_in_dates[is_present]
            .groupby("District", sort=False)
            .agg({"Notes": "size"})
            .Notes
        )
        # add div/sub_div absolutes
        top_div_df[off_col_abs] = (
            df_in_dates[is_present]
            .groupby("Division", sort=False)
            .agg({"Notes": "size"})
            .Notes
        )
        top_subdiv_df[off_col_abs] = (
            df_in_dates[is_present]
            .groupby("Sub_div_Id", sort=False)
            .agg({"Notes": "size"})
            .Notes
        )

        # normalize presence of officials
        df_in_dates.loc[is_present, off_col] = "YES"
        df_in_dates.loc[~is_present, off_col] = "NO"
        # store mask for "at least one present"
        is_present_list.append(is_present)

    # "at least one official present": absolute yes
    is_one_or_more = np.logical_or.reduce(is_present_list)
    one_plus_col_y = "YES"
    top_block_df[one_plus_col_y] = (
        df_in_dates[is_one_or_more]
        .groupby("Block_Id", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )
    top_distr_df[one_plus_col_y] = (
        df_in_dates[is_one_or_more]
        .groupby("District", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )
    # add div/sub_div
    top_div_df[one_plus_col_y] = (
        df_in_dates[is_one_or_more]
        .groupby("Division", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )
    top_subdiv_df[one_plus_col_y] = (
        df_in_dates[is_one_or_more]
        .groupby("Sub_div_Id", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )
    # "at least one official present": absolute no
    one_plus_col_n = "NO"
    top_block_df[one_plus_col_n] = (
        df_in_dates[~is_one_or_more]
        .groupby("Block_Id", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )
    top_distr_df[one_plus_col_n] = (
        df_in_dates[~is_one_or_more]
        .groupby("District", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )
    # add div/sub_div
    top_div_df[one_plus_col_n] = (
        df_in_dates[~is_one_or_more]
        .groupby("Division", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )
    top_subdiv_df[one_plus_col_n] = (
        df_in_dates[~is_one_or_more]
        .groupby("Sub_div_Id", sort=False)
        .agg({"Notes": "size"})
        .Notes
    )

    # sort values for kpi TOP District/Blocks
    top_block_df.reset_index(inplace=True)
    top_block_df.sort_values(
        "Sess_with_vacc",
        ascending=False,
        ignore_index=True,
        inplace=True,
    )
    top_distr_df.reset_index(inplace=True)
    top_distr_df.sort_values(
        "Sess_with_vacc",
        ascending=False,
        ignore_index=True,
        inplace=True,
    )
    # sort values for kpi TOP Div/Sub_div
    top_div_df.reset_index(inplace=True)
    top_div_df.sort_values(
        "Sess_with_vacc",
        ascending=False,
        ignore_index=True,
        inplace=True,
    )
    top_subdiv_df.reset_index(inplace=True)
    top_subdiv_df.sort_values(
        "Sess_with_vacc",
        ascending=False,
        ignore_index=True,
        inplace=True,
    )

    # # add new aggregate for sessions: division and subdivision
    # top_div_df = (
    #     df_in_dates.groupby("Division", sort=False, as_index=False)
    #     .agg({"Sess_plan": "sum", "Sess_with_vacc": "sum"})
    #     .astype({'Sess_plan': 'int64', 'Sess_with_vacc': 'int64'})
    # ).sort_values(
    #     "Sess_with_vacc",
    #     ascending=False,
    #     ignore_index=True,
    # )
    # top_subdiv_df = (
    #     df_in_dates.groupby("Sub_div_Id", sort=False, as_index=False)
    #     .agg({"Sess_plan": "sum", "Sess_with_vacc": "sum"})
    #     .astype({'Sess_plan': 'int64', 'Sess_with_vacc': 'int64'})
    # ).sort_values(
    #     "Sess_with_vacc",
    #     ascending=False,
    #     ignore_index=True,
    # )

    # map visualization: not reported blocks
    not_report_blocks = np.setdiff1d(
        admin_blocks_df.Block_Id.values,
        top_block_df.Block_Id.values,
        assume_unique=True,
    )
    # concat not_report_blocks, replace NaNs and cast kpis to integer
    top_block_df = (
        pd.concat(
            [top_block_df, pd.DataFrame({"Block_Id": not_report_blocks})],
            ignore_index=True,
        )
        .fillna(-1)
        .astype({elem: "int64" for elem in kpi_with_trend_value if elem != "ALL_pres"})
    )

    # (note all kpi cols cast float)

    # kpi: District sessions and vacc distribution - Time-series: df_in_dates refactor
    # drop not relevant columns
    df_in_dates.drop(
        columns=[
            "S_Num",
            "Block",
            "Block_Id",
            "Notes",
            "Division",
            "Sub_division",
            "Sub_div_Id",
        ],
        inplace=True,
    )
    # transform presence of officials to numeric
    df_in_dates.replace({"YES": 1, "NO": 0}, inplace=True, regex=False)

    # "at least one official present": for percentage in districts
    df_in_dates["ALL_pres"] = 0
    df_in_dates.loc[is_one_or_more, "ALL_pres"] = 1
    # count entries for "at least one official present" percentage in districts
    df_in_dates["n_entries"] = 1

    # daily aggregate by district
    distr_daily_agg_df = (
        df_in_dates.groupby(["Date", "District"], sort=False).agg("sum").astype("int64")
    )
    # rewrite "ALL_pres" with percentages
    distr_daily_agg_df.loc[:, "ALL_pres"] = round(
        distr_daily_agg_df.ALL_pres / distr_daily_agg_df.n_entries * 100
    )
    # weekly aggregate by district
    distr_weekly_agg_df = (
        df_in_dates.set_index("Date")
        .groupby([pd.Grouper(freq="W"), "District"], sort=False)
        .agg("sum")
        .astype("int64")
    )
    # rewrite "ALL_pres" with percentages
    distr_weekly_agg_df.loc[:, "ALL_pres"] = round(
        distr_weekly_agg_df.ALL_pres / distr_weekly_agg_df.n_entries * 100
    )
    # monthly aggregate by district
    distr_monthly_agg_df = (
        df_in_dates.set_index("Date")
        .groupby([pd.Grouper(freq="M"), "District"], sort=False)
        .agg("sum")
        .astype("int64")
    )
    # rewrite "ALL_pres" with percentages
    distr_monthly_agg_df.loc[:, "ALL_pres"] = round(
        distr_monthly_agg_df.ALL_pres / distr_monthly_agg_df.n_entries * 100
    )

    # compute trends: percentage of officials presence
    for off_col in col_officials:
        # rewrite off_col with percentages
        distr_daily_agg_df.loc[:, off_col] = round(
            distr_daily_agg_df[off_col] / distr_daily_agg_df.n_entries * 100
        )
        distr_weekly_agg_df.loc[:, off_col] = round(
            distr_weekly_agg_df[off_col] / distr_weekly_agg_df.n_entries * 100
        )
        distr_monthly_agg_df.loc[:, off_col] = round(
            distr_monthly_agg_df[off_col] / distr_monthly_agg_df.n_entries * 100
        )

    # melt kpis (wide-to-long transform)
    distr_daily_df = distr_daily_agg_df.reset_index().melt(
        id_vars=["Date", "District"],
        value_vars=kpi_with_trend_value,
    )
    # assign 'daily' to new column: time frequency
    distr_daily_df["Freq"] = "D"
    # melt kpis (wide-to-long transform)
    distr_weekly_df = distr_weekly_agg_df.reset_index().melt(
        id_vars=["Date", "District"],
        value_vars=kpi_with_trend_value,
    )
    # assign 'weekly' to new column: time frequency
    distr_weekly_df["Freq"] = "W"
    # melt kpis (wide-to-long transform)
    distr_monthly_df = distr_monthly_agg_df.reset_index().melt(
        id_vars=["Date", "District"],
        value_vars=kpi_with_trend_value,
    )
    # assign 'monthly' to new column: time frequency
    distr_monthly_df["Freq"] = "M"

    # # dynamic options: divisions
    # available_div = top_div_df.Division.unique()
    # # hard-coded options for districts
    # div_options = [{"label": l, "value": l} for l in available_div]

    # return kpis calculated and dropdown options
    return (
        [
            html.Ol(
                id="top-div-list",
                children=[html.Li(div) for div in top_div_df.Division.values[:10]],
            )
        ],
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
                id="top-subdiv-list",
                children=[
                    html.Li(sub_div) for sub_div in top_subdiv_df.Sub_div_Id.values[:10]
                ],
            )
        ],
        [
            html.Ol(
                id="top-b-list",
                children=[
                    html.Li(block) for block in top_block_df.Block_Id.values[:10]
                ],
            )
        ],
        # csv to json: sharing data within Dash
        top_distr_df.to_json(orient="split"),
        # csv to json: sharing data within Dash
        top_block_df.to_json(orient="split"),
        # csv to json: sharing data within Dash
        top_div_df.to_json(orient="split"),
        # csv to json: sharing data within Dash
        top_subdiv_df.to_json(orient="split"),
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
        # offic_options,
        # "ALL_pres",
        # div_options,
        # available_div[0],
        # # csv to json: sharing data within Dash
        # top_div_df.to_json(orient='split'),
    )


# In[ ]:


@app.callback(
    Output("card-top-list-1", "children"),
    Output("card-top-list-2", "children"),
    Output("card-top-list-3", "children"),
    Output("card-top-list-4", "children"),
    Output("df-district-kpis", "children"),
    Output("df-block-kpis", "children"),
    Output("df-div-kpis", "children"),
    Output("df-subdiv-kpis", "children"),
    Output("my-map-dd", "options"),
    Output("my-map-dd", "value"),
    Output("my-trends-dd", "options"),
    Output("my-trends-dd", "value"),
    Output("my-districts-dd", "options"),
    Output("my-districts-dd", "value"),
    Output("df-trends-kpis", "children"),
    # Output('my-offic-dd', 'options'),
    # Output('my-offic-dd', 'value'),
    # Output('my-dyn-dd', 'options'),
    # Output('my-dyn-dd', 'value'),
    # Output('df-admin-selected', 'children'),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("btn-close", "n_clicks"),
    State("csv-df", "children"),
    prevent_initial_call=True,
)
def update_districts(start_date, end_date, _, vacc_df):

    # file not available or inconsistent dates
    if not vacc_df or (start_date > end_date):
        return (
            "N/A",
            "N/A",
            "N/A",
            "N/A",
            {},
            {},
            {},
            {},
            [],
            "",
            [],
            "",
            [],
            "",
            {},
        )  # , [], "", [], "", {}
    else:
        return district_calc(vacc_df, start_date, end_date)


# In[ ]:


# function to avoid figure display inline
def update_cm_fig(cm_fig):
    cm_fig.update_geos(fitbounds="locations", visible=False)
    cm_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return cm_fig


# color names for scale
color_names = ["DarkRed", "FloralWhite", "Navy"]
# customed continous scale
red_y_blue = [[0, color_names[0]], [0.5, color_names[1]], [1, color_names[2]]]
# customed continous scale: gray NaNs
color_nan = "gray"
nan_red_y_blue = [
    [0, color_nan],
    [0.001, color_nan],
    [0.001, color_names[0]],
    [0.5, color_names[1]],
    [1, color_names[2]],
]

# use dropdown value to update indicator plotted in map (district-wise)
def display_in_map(kpi_df, block_kpi_df, dd_value):

    # json to dataframe
    kpi_df = pd.read_json(kpi_df, orient="split")
    block_kpi_df = pd.read_json(block_kpi_df, orient="split")

    # min-max block kpis (filter > 0)
    kpi_is_pos = block_kpi_df[dd_value] > 0
    block_kpi_min = block_kpi_df[kpi_is_pos][dd_value].min()
    block_kpi_max = block_kpi_df[kpi_is_pos][dd_value].max()

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
        # color_continuous_scale = "RdBu",
        color_continuous_scale=red_y_blue,
        # color_discrete_map={'red':'red', 'orange':'orange', 'green':'green'},
        hover_data=[dd_value],
        projection="mercator",
    )

    # block vaccine distribution map
    block_cmap_fig = px.choropleth(
        block_kpi_df[["Block_Id", dd_value]],
        geojson=geofile_block,
        featureidkey="properties.NAME1_",  # 'properties.ST_NM', #
        locations="Block_Id",
        color=dd_value,
        # color_continuous_scale = "RdBu",
        color_continuous_scale=nan_red_y_blue,
        # color_discrete_map={'red':'red', 'orange':'orange', 'green':'green'},
        range_color=[block_kpi_min, block_kpi_max],
        hover_data=[dd_value],
        projection="mercator",
    )

    return update_cm_fig(cmap_fig), update_cm_fig(block_cmap_fig)


# In[ ]:


@app.callback(
    Output("district-plot", "figure"),
    Output("block-plot", "figure"),
    Input("my-map-dd", "value"),
    State("df-district-kpis", "children"),
    State("df-block-kpis", "children"),
    prevent_initial_call=True,
)
def update_map(dd_value, distr_kpi_df, block_kpi_df):

    # file not available or inconsistent dates
    if (not distr_kpi_df) | (not block_kpi_df) | (dd_value == ""):
        return label_no_fig, label_no_fig
    else:
        return display_in_map(distr_kpi_df, block_kpi_df, dd_value)


# In[ ]:


# use dropdown values to update trendlines (district-wise)
def display_in_line(trends_df, dd_kpi, dd_distr, freq_val):

    # json to dataframe, query by dropdown values
    query_by_dd = "District in @dd_distr & variable in @dd_kpi & Freq == @freq_val"
    distr_trends_df = (
        pd.read_json(
            trends_df,
            orient="split",
            convert_dates=["Date"],
        )
        .query(query_by_dd)
        .sort_values(
            ["Date", "District", "variable"],
            ignore_index=True,
        )
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


# switch_col for column selection
switch_col = {
    1: "Division",
    2: "District",
    3: "Sub_div_Id",
    4: "Block_Id",
}

# update dynamic dropdown based on radio clicks
@app.callback(
    Output("my-dyn-dd", "options"),
    Output("my-dyn-dd", "value"),
    Output("df-admin-selected", "children"),
    Input("admin-radios", "value"),
    Input("df-div-kpis", "children"),
    State("df-district-kpis", "children"),
    State("df-subdiv-kpis", "children"),
    State("df-block-kpis", "children"),
    prevent_initial_call=True,
)
def update_dyn_dd(
    admin_selected, div_kpi_df, distr_kpi_df, subdiv_kpi_df, block_kpi_df
):

    # file not available
    if (
        not admin_selected
        or not div_kpi_df
        or not distr_kpi_df
        or not subdiv_kpi_df
        or not block_kpi_df
    ):
        return [], "", {}
    else:
        # switcher for dataframe selection
        switcher = {
            1: div_kpi_df,
            2: distr_kpi_df,
            3: subdiv_kpi_df,
            4: block_kpi_df,
        }

        # use switchers based on admin_selected (filter not reported blocks)
        admin_df = pd.read_json(
            switcher[admin_selected],
            orient="split",
        ).query("Sess_plan >= 0")
        available_options = admin_df[switch_col[admin_selected]].dropna().unique()

        return (
            [{"label": l, "value": l} for l in available_options],
            available_options[0],
            switcher[admin_selected],
        )


# In[ ]:


col_officials_abs = [a_col + "_abs" for a_col in col_officials]


@app.callback(
    Output("pie-plot-1", "figure"),
    Output("pie-plot-2", "figure"),
    Input("my-dyn-dd", "value"),
    State("admin-radios", "value"),
    State("df-admin-selected", "children"),
    prevent_initial_call=True,
)
def update_pie(dyn_value, admin_value, admin_df):

    # file not available
    if not dyn_value or not admin_value or not admin_df:
        return label_no_fig, label_no_fig
    else:
        # json to dataframe, query by dyn_value
        query_by_dd = switch_col[admin_value] + " == @dyn_value"
        percentage = (
            pd.read_json(
                admin_df,
                orient="split",
            )
            .query(query_by_dd)[["YES", "NO", *col_officials_abs]]
            .reset_index(drop=True)
        )

        pie_fig_2 = px.pie(
            percentage[col_officials_abs]
            .T.reset_index()
            .rename(columns={0: "Days Present", "index": "Membership"}),
            values="Days Present",
            names="Membership",
        ).update_layout(
            title_text="Officials Membership among Presents",
            title_x=0.5,
            # legend_traceorder="normal",
        )

        pie_fig_1 = px.pie(
            percentage[["YES", "NO"]]
            .T.reset_index()
            .rename(columns={0: "Days Present", "index": "Presence"}),
            values="Days Present",
            names="Presence",
        ).update_layout(
            title_text="At-least-one-official Presence",
            title_x=0.5,
            # legend_traceorder="normal",
        )

        return pie_fig_1, pie_fig_2


# In[ ]:


if __name__ == "__main__":
    app.run_server(debug=True)
