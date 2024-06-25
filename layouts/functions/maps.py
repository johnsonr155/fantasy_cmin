import json
import logging

import dash_deck
import geojson
import pydeck as pdk
from shapely import geometry as gm
from shapely.geometry import LineString

from layouts.functions.prep_data import import_data


def redistribute_vertices(geom, distance):
    num_vert = int(round(geom.length / distance))
    if num_vert == 0:
        num_vert = 1

    return LineString(
        [
            geom.interpolate(float(n) / num_vert, normalized=True)
            for n in range(num_vert + 1)
        ]
    )


def get_striped_geojson(data, skip=15):
    features = []
    for line in data["features"]:
        road_data = line["geometry"]
        multiline = gm.shape(road_data)
        x = redistribute_vertices(multiline, 0.0005)
        for index, number in enumerate(range(0, len(x.coords.xy[0]), skip)):
            if index % 2 == 0:
                continue

            coords = [
                [x, y]
                for x, y in zip(
                    x.coords.xy[0][number : number + skip],
                    x.coords.xy[1][number : number + skip],
                )
            ]

            try:
                features.append(
                    geojson.Feature(geometry=LineString(coords), properties={})
                )

            except:
                pass

    feature_collection = geojson.FeatureCollection(features)
    return feature_collection


def pdk_geojson_layer(
    geojson, width=40, min_width=4, color=[255, 255, 255], opacity=0.75
):
    return pdk.Layer(
        "GeoJsonLayer",
        geojson,
        opacity=opacity,
        line_width_scale=width,
        line_width_min_pixels=min_width,
        get_radius=2000,
        tooltip=True,
        stroked=True,
        extruded=True,
        get_line_color=color,
        pickable=True,
        get_elevation=50,
    )


def add_layer_to_bottom(pdk_layer, pdk_json):
    pattern = '"layers": ['
    split_pdk_json = pdk_json.split(pattern)

    return split_pdk_json[0] + pattern + str(pdk_layer) + ", " + split_pdk_json[1]


def la_pdk_layer(geojson):
    return pdk.Layer(
        "GeoJsonLayer",
        geojson,
        opacity=0.35,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        pickable=True,
        auto_highlight=True,
        get_fill_color="properties.Number_of_programmes_color_code",
        get_elevation="properties.Number_of_programmes",
        get_line_color=[255, 255, 255],
        get_line_width=100,
        line_width_min_pixels=1,
    )


def plot_la_programmes_choropleth(geojson, mapboxKey, map_style):
    geojson_fill_layer = la_pdk_layer(geojson)

    layers = [geojson_fill_layer]

    r = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=53.2, longitude=-2.1, zoom=7),
        map_style="light",
        tooltip={
            "html": "<b>Elevation Value:</b> {elevationValue}",
            "style": {"color": "white"},
        },
    ).to_json()

    logging.info("JSON of choropleth")

    map = dash_deck.DeckGL(r, style=map_style)

    return map


def build_cumulative_policy_geojson(columns):
    la_list = import_data("geographic-data/la_programmes/utla.csv")

    for sheet_name in columns:

        selected_programme_df = import_data(
            f"geographic-data/la_programmes/UTLA_mapping.xlsx", sheet_name=sheet_name
        )
        selected_programme_df[sheet_name] = 1
        selected_programme_df = selected_programme_df[["utla22cd", sheet_name]]
        la_list = la_list.merge(selected_programme_df, on="utla22cd", how="outer")
        la_list[sheet_name] = la_list[sheet_name].fillna(0).astype(int)

    la_list = la_list[["utla22cd", "utla22nm"] + columns]
    la_list["Number of programmes in UTLA"] = la_list[columns].sum(axis=1)

    # make color scale dictionary with rgb values and add to local authority programme dataframe

    number_of_programmes_color_mapping = {
        0: [166, 189, 219],
        1: [116, 169, 207],
        2: [54, 144, 192],
        3: [5, 112, 176],
        4: [3, 78, 123],
    }

    la_list["Number of programmes color code"] = la_list[
        "Number of programmes in UTLA"
    ].apply(lambda x: number_of_programmes_color_mapping[int(x)])

    # add number of programmes in LA to local authority geojson properties
    la_2022_geojson = import_data("geographic-data/la_programmes/utla_WGS.geojson")
    features = []
    for feature in la_2022_geojson["features"]:
        la_code = feature["properties"]["CTYUA22CD"]
        if la_code in la_list["utla22cd"].unique():
            row = la_list[la_list["utla22cd"] == la_code].iloc[0]
            programmes = int(row["Number of programmes in UTLA"])
            color = row["Number of programmes color code"]

            if programmes > 0:
                feature["properties"]["Number_of_programmes_in_UTLA"] = programmes
                feature["properties"]["Number_of_programmes_color_code"] = color
                features.append(feature)

    # filter out LAs with zero programmes
    la_2022_geojson["features"] = features

    return la_2022_geojson
