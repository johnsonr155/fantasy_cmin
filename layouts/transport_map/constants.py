import pandas as pd
import pydeck as pdk
from layouts.functions.prep_data import import_data
from layouts.functions.maps import get_striped_geojson, pdk_geojson_layer

# corresponds to dash mantine colors (https://mantine.dev/theming/colors/)
# The primary color used is 6 e.g. for a pink button they use ##e64980
line_colors_dict = {
    "modern_railway": [250, 82, 82],  # red
    "hs2_baseline": [34, 139, 230],  # blue
    "rump": [18, 184, 134],  # teal
    "rump-high-speed": [64, 192, 87],  # green
    "midlands-rail-hub": [190, 75, 219],  # grape
    "lichfield": [253, 126, 20],  # yellow
    "northern_crossrail": [250, 176, 5],  # yellow
    "north_wales_electrification": [21, 170, 191],  # cyan
    "west_yorkshire": [230, 73, 128],
    "beeching": [134, 142, 150],  # gray
    "northern_gateway_road": [190, 75, 219],  # grape
    "western_gateway_road": [21, 170, 191],  # cyan
    "a50_a500_corridor": [253, 126, 20],  # orange
    "a5_corridor": [64, 192, 87],  # green
    "a1_to_a19_corridor": [250, 176, 5],  # yellow
    "stranaer_to_gretna": [34, 139, 230],  # blue
    "ely": [130, 201, 30],  # lime
    "intercity": [21, 170, 191],  # cyan
}

map_style = {
    "height": "85vh",
    "width": "75vw",
    "cursor": "default",
    "left": "none",
    "top": "100",
    "display": "block",
}

# Philip Peter's mapbox token
mapbox_api_token = "pk.eyJ1IjoidHJpc2thaWRlY2FoZWRyb24iLCJhIjoiY2tkb2xrMjFyMGhmNjJxcW82d3V1dDRtOCJ9.Un-k0oanIYBPpIJ2dTZ0vQ"

# modern railways
modern_railway_pdk_layer = pdk.Layer(
    "GeoJsonLayer",
    "https://raw.githubusercontent.com/g-hannay/geojson/main/modern_rail_simplified.json",
    opacity=1,
    line_width_scale=2,
    line_width_min_pixels=0.65,
    get_line_color=line_colors_dict["modern_railway"],
    get_elevation=0,
)

# confirmed HS2
hs2_baseline = import_data("geographic-data/hs2_baseline.geojson")
hs2_pdk_layer = pdk_geojson_layer(
    hs2_baseline, width=30, min_width=3, color=line_colors_dict["hs2_baseline"]
)


# Rump HS2 (Liverpool - Hull)
rump_hs2_conventional_layer = import_data(
    "geographic-data/rump_hs2/conventional.geojson"
)
rump_conventional_pdk_layer = pdk_geojson_layer(
    rump_hs2_conventional_layer,
    color=line_colors_dict["rump"],
)

rump_high_speed_layer = import_data("geographic-data/rump_hs2/high_speed.geojson")
rump_high_speed_pdk_layer = pdk_geojson_layer(
    rump_high_speed_layer,
    color=[0, 0, 0],
)


# northern crossrail
northern_crossrail = import_data(
    "geographic-data/northern_crossrail/northern_crossrail.geojson"
)
northern_crossrail_pdk_layer = pdk_geojson_layer(
    northern_crossrail,
    color=line_colors_dict["northern_crossrail"],
)
tunnel = import_data("geographic-data/northern_crossrail/manchester_tunnel.geojson")
tunnel_pdk_layer = pdk_geojson_layer(
    tunnel,
    width=60,
    min_width=8,
    color=[161, 112, 0],
)
northern_crossrail_high_speed = import_data(
    "geographic-data/northern_crossrail/high_speed.geojson"
)
northern_crossrail_high_speed_pdk_layer = pdk_geojson_layer(
    northern_crossrail_high_speed,
    color=[0, 0, 0],
)


# midlands rail hub
midlands_rail_hub = import_data("geographic-data/midlands_railhub/conventional.geojson")
midlands_rail_hub_pdk_layer = pdk_geojson_layer(
    midlands_rail_hub,
    color=line_colors_dict["midlands-rail-hub"],
)

midlands_junctions = import_data(
    "geographic-data/midlands_railhub/railhub_junctions.geojson"
)
midlands_junctions_pdk_layer = pdk_geojson_layer(
    midlands_junctions,
    color=line_colors_dict["midlands-rail-hub"],
)

bham_to_nott_via_tamworth = import_data(
    "geographic-data/midlands_railhub/bham_to_nott_via_tamworth.geojson"
)
bham_to_nott_via_tamworth_pdk_layer = pdk_geojson_layer(
    bham_to_nott_via_tamworth, color=[180, 180, 180]
)  # to be dotted
bham_to_nott_via_tamworth_striped = get_striped_geojson(
    bham_to_nott_via_tamworth, skip=30
)
bham_to_nott_via_tamworth_pdk_layer_striped = pdk_geojson_layer(
    bham_to_nott_via_tamworth_striped,
    color=line_colors_dict["midlands-rail-hub"],
)

# north wales electricitfication
north_wales_electrification = import_data(
    "geographic-data/north_wales_electrification/electrification.geojson"
)
north_wales_electrification_pdk_layer = pdk_geojson_layer(
    north_wales_electrification,
    color=line_colors_dict["north_wales_electrification"],
)

# west yorkshire mass transit
west_yorkshire_mass_transit = import_data(
    "geographic-data/west_yorkshire_mass_transit/leeds_routes.geojson"
)
west_yorkshire_mass_transit_pdk_layer = pdk_geojson_layer(
    west_yorkshire_mass_transit,
    color=line_colors_dict["west_yorkshire"],
)


# beeching
bishop_to_washington_beeching = import_data(
    "geographic-data/beeching/bisop_middleham_to_washington.geojson"
)
bishop_to_washington_beeching_pdk_layer = pdk_geojson_layer(
    bishop_to_washington_beeching,
    min_width=4,
    color=line_colors_dict["beeching"],
)

burton_to_leciester_beeching = import_data(
    "geographic-data/beeching/burton_to_leicester.geojson"
)
burton_to_leciester_beeching_pdk_layer = pdk_geojson_layer(
    burton_to_leciester_beeching,
    min_width=4,
    color=line_colors_dict["beeching"],
)

chesterfield_to_sheffield_beeching = import_data(
    "geographic-data/beeching/chesterfield_to_sheffield.geojson"
)
chesterfield_to_sheffield_beeching_pdk_layer = pdk_geojson_layer(
    chesterfield_to_sheffield_beeching,
    min_width=4,
    color=line_colors_dict["beeching"],
)

fleetwood_to_poulten_beeching = import_data(
    "geographic-data/beeching/fleetwood_to_poulten.geojson"
)
fleetwood_to_poulten_beeching_pdk_layer = pdk_geojson_layer(
    fleetwood_to_poulten_beeching,
    min_width=4,
    color=line_colors_dict["beeching"],
)

# ely junction
ely_junction = import_data("geographic-data/ely_junction/freight_line.geojson")
ely_junction_pdk_layer = pdk_geojson_layer(
    ely_junction,
    color=line_colors_dict["ely"],
)

# intercity options
intercity_leeds_sheffield = import_data(
    "geographic-data/further_intercity/leeds_sheffield.geojson"
)
intercity_leeds_sheffield_pdk_layer = pdk_geojson_layer(
    intercity_leeds_sheffield,
    color=line_colors_dict["intercity"],
)
intercity_sheffield_hull = import_data(
    "geographic-data/further_intercity/sheffield_hull.geojson"
)
intercity_sheffield_hull_pdk_layer = pdk_geojson_layer(
    intercity_sheffield_hull,
    color=line_colors_dict["intercity"],
)
intercity_leeds_hull = import_data(
    "geographic-data/further_intercity/leeds_hull.geojson"
)
intercity_leeds_hull_pdk_layer = pdk_geojson_layer(
    intercity_leeds_hull,
    color=line_colors_dict["intercity"],
)
intercity_manchester_sheffield = import_data(
    "geographic-data/further_intercity/manchester_sheffield.geojson"
)
intercity_manchester_sheffield_pdk_layer = pdk_geojson_layer(
    intercity_manchester_sheffield,
    color=line_colors_dict["intercity"],
)


# new stations
new_stations = import_data("geographic-data/stations/new_stations.geojson")
coords = []
for x in new_stations["features"]:
    coords.append(
        {
            "name": x["properties"]["name"],
            "coordinates": x["geometry"]["coordinates"][0],
        }
    )

df = pd.DataFrame.from_dict(coords)
df["radius"] = 5

new_stations_scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    pickable=True,
    opacity=1,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=6,
    radius_max_pixels=100,
    line_width_min_pixels=2,
    get_position="coordinates",
    get_radius="radius",
    get_fill_color=line_colors_dict["hs2_baseline"],
    get_line_color=[0, 0, 0],
)
new_station_text = pdk.Layer(
    "TextLayer",
    data=df,
    get_position="coordinates",
    get_size=16,
    get_color=[0, 0, 0],
    get_text="name",
    get_pixel_offset=[15, 0],
    getTextAnchor="'start'",
)


# new stations
station_upgrades = import_data("geographic-data/stations/station_upgrades.geojson")
coords = []
for x in station_upgrades["features"]:
    coords.append(
        {"name": x["properties"]["name"], "coordinates": x["geometry"]["coordinates"]}
    )

df = pd.DataFrame.from_dict(coords)
df["radius"] = 5
station_upgrades_scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    pickable=True,
    opacity=1,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=6,
    radius_max_pixels=100,
    line_width_min_pixels=2,
    get_position="coordinates",
    get_radius="radius",
    get_fill_color=line_colors_dict["modern_railway"],
    get_line_color=[0, 0, 0],
)
upgrade_station_text = pdk.Layer(
    "TextLayer",
    data=df,
    get_position="coordinates",
    get_size=16,
    get_color=[0, 0, 0],
    get_text="name",
    get_pixel_offset=[15, 0],
    getTextAnchor="'start'",
    fontWeight="'bold'",
)


# roads
northern_gateway_road = import_data("geographic-data/roads/northern_gateway.geojson")
northern_gateway_pdk_layer_striped = pdk_geojson_layer(
    northern_gateway_road, min_width=3, color=[255, 255, 255]
)
northern_gateway_pdk_layer = pdk_geojson_layer(
    northern_gateway_road,
    min_width=7,
    color=line_colors_dict["northern_gateway_road"],
)


western_gateway_road = import_data("geographic-data/roads/western_gateway.geojson")
western_gateway_pdk_layer = pdk_geojson_layer(
    western_gateway_road,
    min_width=7,
    color=line_colors_dict["western_gateway_road"],
)
western_gateway_pdk_layer_striped = pdk_geojson_layer(
    western_gateway_road, min_width=3, color=[255, 255, 255]
)

a50_a500_corridor = import_data("geographic-data/roads/A50_A500_corridor.geojson")
a50_a500_corridor_pdk_layer = pdk_geojson_layer(
    a50_a500_corridor,
    min_width=7,
    color=line_colors_dict["a50_a500_corridor"],
)
a50_a500_corridor_pdk_layer_striped = pdk_geojson_layer(
    a50_a500_corridor, min_width=3, color=[255, 255, 255]
)


a5_corridor = import_data("geographic-data/roads/A5_corridor.geojson")
a5_corridor_pdk_layer = pdk_geojson_layer(
    a5_corridor,
    min_width=7,
    color=line_colors_dict["a5_corridor"],
)
a5_corridor_pdk_layer_striped = pdk_geojson_layer(
    a5_corridor, min_width=3, color=[255, 255, 255]
)

a1_to_a19_corridor = import_data("geographic-data/roads/A1_to_A19_link_road.geojson")
a1_to_a19_corridor_pdk_layer = pdk_geojson_layer(
    a1_to_a19_corridor,
    min_width=7,
    color=line_colors_dict["a1_to_a19_corridor"],
)
a1_to_a19_corridor_pdk_layer_striped = pdk_geojson_layer(
    a1_to_a19_corridor, min_width=3, color=[255, 255, 255]
)

stranaer_to_gretna = import_data("geographic-data/roads/stranraer_to_gretna.geojson")
stranaer_to_gretna_pdk_layer = pdk_geojson_layer(
    stranaer_to_gretna,
    min_width=7,
    color=line_colors_dict["stranaer_to_gretna"],
)
stranaer_to_gretna_pdk_layer_striped = pdk_geojson_layer(
    stranaer_to_gretna, min_width=3, color=[255, 255, 255]
)


# Layer data
## overlaying on map is dictated by order of layers in this dict
line_layer_dict = {
    "modern-railways-checkbox": [modern_railway_pdk_layer],
    "hs2-checkbox": [hs2_pdk_layer],
    "intercity-leeds-shefield-checkbox": [intercity_leeds_sheffield_pdk_layer],
    "intercity-shefield-hull-checkbox": [intercity_sheffield_hull_pdk_layer],
    "intercity-leeds-hull-checkbox": [intercity_leeds_hull_pdk_layer],
    "intercity-manchester-shefield-checkbox": [
        intercity_manchester_sheffield_pdk_layer
    ],
    "rump-hs2-checkbox": [rump_conventional_pdk_layer, rump_high_speed_pdk_layer],
    "north-wales-electrification-checkbox": [north_wales_electrification_pdk_layer],
    "west-yorkshire-checkbox": [west_yorkshire_mass_transit_pdk_layer],
    "beeching-checkbox": [
        burton_to_leciester_beeching_pdk_layer,
        chesterfield_to_sheffield_beeching_pdk_layer,
    ],
    "ely-junction-checkbox": [ely_junction_pdk_layer],
    # road
    "a50-a500-corridor-checkbox": [
        a50_a500_corridor_pdk_layer,
        a50_a500_corridor_pdk_layer_striped,
    ],
    "a1-to-a19-corridor-checkbox": [
        a1_to_a19_corridor_pdk_layer,
        a1_to_a19_corridor_pdk_layer_striped,
    ],
    "a5-corridor-checkbox": [a5_corridor_pdk_layer, a5_corridor_pdk_layer_striped],
    "gretna-checkbox": [
        stranaer_to_gretna_pdk_layer,
        stranaer_to_gretna_pdk_layer_striped,
    ],
    # stations
    "new-station-checkbox": [new_stations_scatter_layer, new_station_text],
    "upgrade-station-checkbox": [station_upgrades_scatter_layer, upgrade_station_text],
}


funding_pots_col_dict = {
    "crsts-pot": "CRSTS",
    "lit-north-pot": "LITS (North)",
    "lit-east-mids-pot": "LITS (Midlands)",
    "bsip-north-pot": "BSIP (North)",
    "bsip-midlands-pot": "BSIP (Midlands)",
    "road-resurfacing-pot": "Road Resurfacing Programme",
}
