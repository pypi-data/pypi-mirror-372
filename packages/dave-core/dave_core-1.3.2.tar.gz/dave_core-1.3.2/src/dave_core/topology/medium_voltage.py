# Copyright (c) 2022-2024 by Fraunhofer Institute for Energy Economics and Energy System Technology (IEE)
# Kassel and individual contributors (see AUTHORS file for details).
# All rights reserved.
# Copyright (c) 2024-2025 DAVE_core contributors
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.


from geopandas import GeoDataFrame
from geopandas import GeoSeries
from pandas import Series
from pandas import concat
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import Point
from shapely.ops import linemerge
from shapely.wkb import loads

from dave_core.components.substations import create_hv_mv_substations
from dave_core.components.substations import create_mv_lv_substations
from dave_core.progressbar import create_tqdm
from dave_core.settings import dave_settings
from dave_core.toolbox import intersection_with_area


def search_connection_line(bus, mv_buses):
    """
    Search connection line
    """
    nearest_bus_idx = (
        mv_buses.drop([bus.name]).geometry.apply(lambda x: bus.geometry.distance(x)).idxmin()
    )
    return LineString([bus.geometry, mv_buses.loc[nearest_bus_idx].geometry])


def create_mv_topology(grid_data):
    """
    This function creates a dictonary with all relevant parameters for the
    medium voltage level

    INPUT:
        **grid_data** (dict) - all Informations about the target area

    OUTPUT:
        Writes data in the DaVe dataset
    """
    # set progress bar
    pbar = create_tqdm(desc="create medium voltage topology")

    # --- create substations
    # create hv/mv substations
    hvmv_substations = create_hv_mv_substations(grid_data)
    # update progress
    pbar.update(5)
    # create mv/lv substations
    mvlv_substations = create_mv_lv_substations(grid_data)
    # update progress
    pbar.update(10)
    # --- create mv nodes
    # copy data for mv node creation
    mvlv_buses = mvlv_substations.copy()
    # nodes for mv/lv traofs hv side
    mvlv_buses.drop(
        columns=(
            [
                "dave_name",
                "la_id",
                "subst_id",
                "geom",
                "is_dummy",
                "subst_cnt",
                "voltage_level",
            ]
        ),
        inplace=True,
    )
    mvlv_buses["node_type"] = "mvlv_substation"
    # update progress
    pbar.update(5)
    # nodes for hv/mv trafos us side
    hvmv_buses = hvmv_substations.copy()
    if not hvmv_buses.empty:
        hvmv_buses.drop(
            columns=(
                [
                    "dave_name",
                    "lon",
                    "lat",
                    "polygon",
                    "voltage_kv",
                    "power_type",
                    "substation",
                    "osm_id",
                    "osm_www",
                    "frequency",
                    "subst_name",
                    "ref",
                    "operator",
                    "dbahn",
                    "status",
                    "otg_id",
                    "Gemeindeschluessel",
                    "geom",
                    "geometry",
                    "voltage_level",
                ]
            ),
            inplace=True,
        )
        hvmv_buses["node_type"] = "hvmv_substation"
        # change geometry to point
        hvmv_buses["geometry"] = hvmv_buses.point.apply(lambda x: loads(x, hex=True))
        # filter trafos which are within the grid area
        hvmv_buses = intersection_with_area(hvmv_buses, grid_data.area)
        hvmv_buses.drop(
            columns=(
                [
                    "point",
                ]
            ),
            inplace=True,
        )
        hvmv_buses["node_type"] = "hvmv_substation"
    # update progress
    pbar.update(10)
    # consider data only if there are more than one node in the target area
    mv_buses = concat([mvlv_buses, hvmv_buses])
    if len(mv_buses) > 1:
        # search for the substations dave name
        substations_rel = concat([hvmv_substations, mvlv_substations])
        mv_buses["subs_dave_name"] = mv_buses.ego_subst_id.apply(
            lambda x: substations_rel[substations_rel.ego_subst_id == x].iloc[0].dave_name
        )
        mv_buses["voltage_level"] = 5
        mv_buses["voltage_kv"] = dave_settings["mv_voltage"]
        # add oep as source
        mv_buses["source"] = "OEP"
        # add dave name
        mv_buses.reset_index(drop=True, inplace=True)
        mv_buses.insert(
            0,
            "dave_name",
            Series([f"node_5_{x}" for x in mv_buses.index]),
        )
        # set crs
        mv_buses.set_crs(dave_settings["crs_main"], inplace=True)
        # add mv nodes to grid data
        grid_data.mv_data.mv_nodes = concat(
            [grid_data.mv_data.mv_nodes, mv_buses], ignore_index=True
        )
        # --- create mv lines
        # lines to connect node with the nearest node
        # mv_line = mv_buses.apply(lambda x: search_connection_line(x, mv_buses), axis=1)
        # mv_line.drop_duplicates(inplace=True)
        # list(map(lambda x: search_connection_line(x, mv_buses), mv_buses))
        mv_lines = GeoSeries([])
        for i, bus in mv_buses.iterrows():
            mv_line = search_connection_line(bus, mv_buses)
            # check if line already exists
            if not mv_lines.geom_equals(mv_line).any():
                mv_lines[i] = mv_line
        # update progress
        pbar.update(10)
        mv_lines.set_crs(dave_settings["crs_main"], inplace=True)
        mv_lines.reset_index(drop=True, inplace=True)
        # connect line segments with each other
        while 1:
            # search for related lines and merge them
            mv_lines_rel = mv_lines.copy()
            for _, bus in mv_buses.iterrows():
                # check if bus is conected to more than one line
                lines_intersect = mv_lines_rel[mv_lines_rel.intersects(bus.geometry)]
                if len(lines_intersect) > 1:
                    # get list with line objects
                    lines_list = lines_intersect.tolist()
                    # search for multilines and split them
                    new_line = [
                        list(x.geoms) if isinstance(x, MultiLineString) else [x] for x in lines_list
                    ]
                    new_line = [line for sublist in new_line for line in sublist]
                    # merge found lines and add new line to line quantity
                    mv_lines_rel[len(mv_lines)] = linemerge(new_line)
                    # delete found lines from line quantity
                    mv_lines_rel.drop(lines_intersect.index.tolist(), inplace=True)
                    mv_lines_rel.reset_index(drop=True, inplace=True)
            # break loop if all lines connected
            if len(mv_lines_rel) == 1:
                break
            # create lines for connecting line segments
            for i, line in enumerate(mv_lines_rel.to_list()):
                # find nearest line to considered one
                nearest_line_idx = mv_lines_rel.drop([i]).geometry.distance(line).idxmin()
                # get line coordinates
                if isinstance(line, MultiLineString):
                    line_points = GeoSeries(
                        [Point(coords) for segment in line.geoms for coords in segment.coords[:]]
                    )
                else:
                    line_points = GeoSeries([Point(coords) for coords in line.coords[:]])
                # set crs
                line_points = line_points.set_crs(dave_settings["crs_main"])
                # get nearest line coordinates
                nearest_line = mv_lines_rel.loc[nearest_line_idx]
                if isinstance(nearest_line, MultiLineString):
                    nearest_line_points = GeoSeries(
                        [
                            Point(coords)
                            for segment in nearest_line.geoms
                            for coords in segment.coords[:]
                        ]
                    )
                else:
                    nearest_line_points = GeoSeries(
                        [
                            Point(mv_lines_rel.loc[nearest_line_idx].coords[:][j])
                            for j in range(len(nearest_line.coords[:]))
                        ]
                    )
                # set crs
                nearest_line_points.set_crs(dave_settings["crs_main"], inplace=True)
                # define minimal distance for initialize
                distance_min = 1000  # any big number
                # find pair of nearest nodes
                for point in line_points:
                    distance = nearest_line_points.geometry.apply(
                        lambda x, point=point: point.distance(x)
                    )
                    if distance_min > distance.min():
                        distance_min = distance.min()
                        nearest_point = nearest_line_points[distance.idxmin()]
                        line_point = point
                # add created connection line into mv lines
                mv_line = LineString([line_point, nearest_point])
                if not mv_lines.geom_equals(mv_line).any():
                    mv_lines[len(mv_lines)] = mv_line
        # update progress
        pbar.update(40)
        # prepare dataframe for mv lines
        mv_lines = GeoDataFrame(geometry=mv_lines)
        # project lines to crs with unit in meter for length calculation
        mv_lines.set_crs(dave_settings["crs_main"], inplace=True)
        mv_lines_3035 = mv_lines.to_crs(dave_settings["crs_meter"])
        # add parameters to lines
        for _, line in mv_lines.iterrows():
            # get from bus name
            mv_lines.at[line.name, "from_bus"] = mv_buses.loc[
                mv_buses.geometry.apply(
                    lambda x, line=line: Point(line.geometry.coords[:][0]).distance(x)
                ).idxmin()
            ].dave_name
            # get to bus name
            mv_lines.at[line.name, "to_bus"] = mv_buses.loc[
                mv_buses.geometry.apply(
                    lambda x, line=line: Point(line.geometry.coords[:][1]).distance(x)
                ).idxmin()
            ].dave_name
        # calculate length in km
        mv_lines["length_km"] = mv_lines_3035.geometry.length / 100
        # line dave name
        mv_lines.insert(
            0,
            "dave_name",
            Series([f"line_5_{x}" for x in mv_lines.index]),
        )
        # additional informations
        mv_lines["voltage_kv"] = dave_settings["mv_voltage"]
        mv_lines["voltage_level"] = 5
        mv_lines["source"] = "dave internal"
        # set crs
        mv_lines.set_crs(dave_settings["crs_main"], inplace=True)
        # add mv lines to grid data
        grid_data.mv_data.mv_lines = concat(
            [grid_data.mv_data.mv_lines, mv_lines], ignore_index=True
        )
        # update progress
        pbar.update(20)
    else:
        # update progress
        pbar.update(80)
    # close progress bar
    pbar.close()
