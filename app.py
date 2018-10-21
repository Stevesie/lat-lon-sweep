import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from dash.dependencies import Input, Output, State

INITIAL_LATITUDE = '38.13591366397597'
INITIAL_LONGITUDE = '-96.72647129706326'
INITIAL_ZOOM = 3
LAT_LON_STEP = 0.75

PUBLIC_MAPBOX_TOKEN = 'YOUR_MAPBOX_TOKEN'

app = dash.Dash()

server = app.server

app.layout = html.Div([dcc.Graph(id='map'), 
    dcc.Textarea(
        id='out',
        placeholder='Select a bounding box in the map for a list of coordinates',
        style={'width': '100%', 'height': '200px'}
    )])

def __generate_coordinates(bounding_box):
    latitudes = []
    longitudes = []

    northwest = bounding_box[0]
    southeast = bounding_box[1]

    lat = northwest[1]
    while lat > southeast[1]:
        lon = northwest[0]
        while lon < southeast[0]:
            latitudes.append(lat)
            longitudes.append(lon)
            lon += LAT_LON_STEP
        lat -= LAT_LON_STEP

    return (latitudes, longitudes)

@app.callback(
    Output('out', 'value'),
    [Input('map', 'selectedData')])
def add_csv(select_data):
    if not select_data:
        return ''

    bounding_box = select_data['range']['mapbox']
    latitudes, longitudes = __generate_coordinates(bounding_box)

    coords = 'latitude,longitude\n'
    for i, lat in enumerate(latitudes):
        coords += '{},{}\n'.format(lat, longitudes[i])

    return coords

@app.callback(
    Output('map', 'figure'),
    [Input('map', 'selectedData')],
    [State('map', 'figure')])
def draw_circles(select_data, existing_figure):
    latitudes = []
    longitudes = []

    if select_data:
        bounding_box = select_data['range']['mapbox']
        latitudes, longitudes = __generate_coordinates(bounding_box)
        
        northwest = bounding_box[0]
        southeast = bounding_box[1]

        center_lat = (southeast[1] - northwest[1]) / 2 + northwest[1]
        center_lon = (southeast[0] - northwest[0]) / 2 + northwest[0]
    else:
        center_lat = INITIAL_LATITUDE
        center_lon = INITIAL_LONGITUDE

    data = [
        go.Scattermapbox(
            lat=latitudes,
            lon=longitudes,
            mode='markers',
            marker=dict(
                opacity=0.75,
                size=7
            ),
            text=[])]

    layout = go.Layout(
        autosize=True,
        height=300,
        margin=go.Margin(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0
        ),
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=PUBLIC_MAPBOX_TOKEN,
            bearing=0,
            center=dict(
                lat=center_lat,
                lon=center_lon
            ),
            pitch=0,
            zoom=existing_figure['layout']['mapbox']['zoom'] if existing_figure else INITIAL_ZOOM
        )
    )

    return dict(data=data, layout=layout)

external_css = [
    # Normalize the CSS
    'https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css',
    # # Fonts
    'https://fonts.googleapis.com/css?family=Open+Sans|Roboto',
    'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    # Bootstrap
    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
    # Dash Layout
    'https://cdn.rawgit.com/xhlulu/0acba79000a3fd1e6f552ed82edb8a64/raw/dash_template.css',
    'https://stevesie-assets.nyc3.digitaloceanspaces.com/dash-styles.css'
]

for css in external_css:
    app.css.append_css({'external_url': css})

if __name__ == '__main__':
    app.run_server(debug=True)
