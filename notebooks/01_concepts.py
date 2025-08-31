import marimo

__generated_with = "0.15.2"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Geospatial Network Concepts""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    Geospatial network data (such as streets, paths, rail, canals, etc) are useful for modeling mobility and access to resources.

    This notebook is an introduction to common concepts and operations related to geospatial network analysis.
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    import osmnx as ox
    import networkx as nx
    import geopandas as gpd
    import numpy as np

    ox.__version__
    return gpd, mo, np, nx, ox


@app.cell
def _(ox):
    city = ox.geocoder.geocode_to_gdf('Piedmont, California, USA')
    city_proj = ox.projection.project_gdf(city)
    _ax = city_proj.plot(fc='gray', ec='none')
    _ = _ax.axis('off')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Street network graphs""")
    return


@app.cell
def _(ox):
    piedmont_graph = ox.graph.graph_from_place('Piedmont, California, USA', network_type='drive')
    _fig, _ax = ox.plot.plot_graph(piedmont_graph)
    return (piedmont_graph,)


@app.cell
def _():
    # This example of a larger network takes multiple minutes to download
    # place = {"city": "San Francisco", "state": "California", "country": "USA"}
    # san_francisco_graph = ox.graph.graph_from_place(place, network_type="walk", truncate_by_edge=True)
    # fig, ax = ox.plot.plot_graph(san_francisco_graph, figsize=(10, 10), node_size=0, edge_color="y", edge_linewidth=0.2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Edges and nodes""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Graphs can be converted to node and edge GeoPandas GeoDataFrames""")
    return


@app.cell
def _(ox, piedmont_graph):
    # you can convert your graph to node and edge GeoPandas GeoDataFrames
    gdf_nodes, gdf_edges = ox.convert.graph_to_gdfs(piedmont_graph)
    gdf_nodes.head()
    return gdf_edges, gdf_nodes


@app.cell
def _(gdf_edges):
    gdf_edges.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Exporting and importing graph files""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""(Add note about file formats, motivations, issues. GraphML, Geopackage, Geodatabase?)""")
    return


@app.cell
def _():
    geopackage_path = "./data/piedmont_drive_network.gpkg"
    graphml_path = "./data/piedmont_drive_network.graphml"
    return geopackage_path, graphml_path


@app.cell
def _(geopackage_path, graphml_path, ox, piedmont_graph):
    # save network as geopackage file (for GIS)
    ox.io.save_graph_geopackage(piedmont_graph, filepath=geopackage_path, directed=True)
    # save network as GraphML file to work with later in OSMnx or networkx or gephi
    ox.io.save_graphml(piedmont_graph, filepath=graphml_path)
    return


@app.cell
def _(geopackage_path, gpd, np, ox, piedmont_graph):
    # load GeoPackage file
    # must ensure node/edge layers are indexed as described in OSMnx docs
    geopackage_nodes = gpd.read_file(geopackage_path, layer='nodes').replace('', np.nan).set_index('osmid')
    geopackage_nodes.index = geopackage_nodes.index.astype(int)
    geopackage_edges = gpd.read_file(geopackage_path, layer='edges').replace('', np.nan).set_index(['u', 'v', 'key'])
    # geopackage_edges["osmid"] = geopackage_edges["osmid"].astype(int)
    geopackage_edges["reversed"] = geopackage_edges["reversed"].astype(bool)
    geopackage_edges.index = geopackage_edges.index.set_levels(
        [level.astype(int) for level in geopackage_edges.index.levels]
    )
    # geopackage_edges["length"] = geopackage_edges["length"].astype(np.float64)
    assert geopackage_nodes.index.is_unique and geopackage_edges.index.is_unique

    # convert the node/edge GeoDataFrames to a MultiDiGraph
    # graph_attributes = {'crs': 'epsg:4326', 'simplified': True}
    graph_attributes = piedmont_graph.graph
    geopackage_piedmont_graph = ox.graph_from_gdfs(geopackage_nodes.sort_values(by="osmid"), geopackage_edges, graph_attrs=graph_attributes)
    geopackage_piedmont_graph = ox.graph_from_gdfs(geopackage_nodes.sort_values(by="osmid"), geopackage_edges, graph_attrs=graph_attributes, )
    return geopackage_edges, geopackage_piedmont_graph, graph_attributes


@app.cell
def _(geopackage_edges):
    geopackage_edges.dtypes
    return


@app.cell
def _(graph_attributes):
    graph_attributes
    return


@app.cell
def _(graphml_path, ox):
    # load GraphML file
    graphml_piedmont_graph = ox.io.load_graphml(graphml_path)
    return (graphml_piedmont_graph,)


@app.cell
def _(graphml_piedmont_graph, nx, piedmont_graph):
    nx.utils.misc.graphs_equal(piedmont_graph, graphml_piedmont_graph)
    return


@app.cell
def _(geopackage_piedmont_graph, nx, piedmont_graph):
    nx.utils.misc.graphs_equal(piedmont_graph, geopackage_piedmont_graph)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Investigate lack of equality after exporting/importing GeoPackage""")
    return


@app.function
def dict_compare(dict1, dict2):
    # Keys only in dict1
    only_in_dict1 = dict1.keys() - dict2.keys()

    # Keys only in dict2
    only_in_dict2 = dict2.keys() - dict1.keys()

    # Keys in both but with different values
    diff_values = {k: (dict1[k], dict2[k]) for k in dict1.keys() & dict2.keys() if dict1[k] != dict2[k]}

    print("Only in dict1:", only_in_dict1)
    print("Only in dict2:", only_in_dict2)
    print("Different values:", diff_values)
    return diff_values


@app.function
def compare_graph_adjacency_objects(grapg_adj_1, grapg_adj_2, key_a: int, key_b: int):
    print("## Top-level diff")
    diff_values = dict_compare(grapg_adj_1, grapg_adj_2)
    print("## Level 1 diff")
    diff_values_1 = dict_compare(diff_values[key_a][0], diff_values[key_a][1])
    print("## Level 2 diff")
    diff_values_2 = dict_compare(diff_values_1[key_b][0], diff_values_1[key_b][1])
    print("### Level 2 diff details")
    print(diff_values_2)
    print("### Level 3 diff")
    diff_values_3 = dict_compare(diff_values_2[0][0], diff_values_2[0][1])
    print("### Level 3 diff details")
    print(diff_values_3)


@app.cell
def _(geopackage_piedmont_graph, nx, piedmont_graph):
    nx.utils.misc.nodes_equal(piedmont_graph.nodes, geopackage_piedmont_graph.nodes)
    return


@app.cell
def _(geopackage_piedmont_graph, nx, piedmont_graph):
    nx.utils.misc.nodes_equal(piedmont_graph.edges, geopackage_piedmont_graph.edges)
    return


@app.cell
def _(geopackage_piedmont_graph, piedmont_graph):
    compare_graph_adjacency_objects(piedmont_graph.adj, geopackage_piedmont_graph.adj, 53090322, 53082634)
    return


@app.cell
def _(graph_attributes, ox, piedmont_graph):
    gdf_nodes_temp, gdf_edges_temp = ox.convert.graph_to_gdfs(piedmont_graph, fill_edge_geometry=False)
    piedmont_graph_temp = ox.graph_from_gdfs(gdf_nodes_temp, gdf_edges_temp, graph_attrs=graph_attributes)
    return gdf_edges_temp, gdf_nodes_temp, piedmont_graph_temp


@app.cell
def _(gdf_nodes_temp):
    gdf_nodes_temp
    return


@app.cell
def _(gdf_edges_temp):
    gdf_edges_temp
    return


@app.cell
def _(nx, piedmont_graph, piedmont_graph_temp):
    nx.utils.misc.graphs_equal(piedmont_graph, piedmont_graph_temp)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""In order to reconstruct a graph from GeoDataFrames, we must set `fill_edge_geometry=False` when using `graph_to_gdfs`""")
    return


@app.cell
def _(gdf_edges_temp, gdf_nodes_temp, graph_attributes, np, ox):
    # Standardize node and edge GeoDataFrames before reconstructing the graph
    gdf_nodes_temp_clean = gdf_nodes_temp.copy()
    gdf_edges_temp_clean = gdf_edges_temp.copy()

    # Drop geometry column from edges
    if "geometry" in gdf_edges_temp_clean.columns:
        gdf_edges_temp_clean = gdf_edges_temp_clean.drop("geometry", axis="columns")

    # Replace empty strings with np.nan for consistency
    gdf_nodes_temp_clean = gdf_nodes_temp_clean.replace('', np.nan)
    gdf_edges_temp_clean = gdf_edges_temp_clean.replace('', np.nan)

    # Ensure indices are int type
    gdf_nodes_temp_clean.index = gdf_nodes_temp_clean.index.astype(int)
    gdf_edges_temp_clean.index = gdf_edges_temp_clean.index.set_levels(
        [level.astype(int) for level in gdf_edges_temp_clean.index.levels]
    )

    # Sort for consistent ordering
    gdf_nodes_temp_clean = gdf_nodes_temp_clean.sort_index()
    gdf_edges_temp_clean = gdf_edges_temp_clean.sort_index()

    # Reconstruct the graph
    piedmont_graph_temp_clean = ox.graph_from_gdfs(gdf_nodes_temp_clean, gdf_edges_temp_clean, graph_attrs=graph_attributes)
    return (
        gdf_edges_temp_clean,
        gdf_nodes_temp_clean,
        piedmont_graph_temp_clean,
    )


@app.cell
def _(
    gdf_edges,
    gdf_edges_temp_clean,
    gdf_nodes,
    gdf_nodes_temp_clean,
    graph_attributes,
    np,
    nx,
    ox,
    piedmont_graph,
):
    def nan_to_none(df):
        return df.applymap(lambda x: None if isinstance(x, float) and np.isnan(x) else x)
    gdf_nodes_temp_clean_1 = gdf_nodes_temp_clean.reindex(columns=gdf_nodes.columns)
    gdf_edges_temp_clean_1 = gdf_edges_temp_clean.reindex(columns=gdf_edges.columns)
    gdf_nodes_temp_clean_1 = nan_to_none(gdf_nodes_temp_clean_1)
    gdf_edges_temp_clean_1 = nan_to_none(gdf_edges_temp_clean_1)
    piedmont_graph_temp_cleaner = ox.graph_from_gdfs(gdf_nodes_temp_clean_1, gdf_edges_temp_clean_1, graph_attrs=graph_attributes)
    nx.utils.misc.graphs_equal(piedmont_graph, piedmont_graph_temp_cleaner)
    return


@app.cell
def _(nx, piedmont_graph, piedmont_graph_temp_clean):
    nx.utils.misc.graphs_equal(piedmont_graph, piedmont_graph_temp_clean)
    return


@app.cell
def _(gdf_edges_temp):
    gdf_edges_temp_fixed = gdf_edges_temp.drop("geometry", axis="columns")
    gdf_edges_temp_fixed
    return (gdf_edges_temp_fixed,)


@app.cell
def _(
    gdf_edges_temp_fixed,
    gdf_nodes_temp,
    graph_attributes,
    nx,
    ox,
    piedmont_graph,
):
    piedmont_graph_temp_fixed = ox.graph_from_gdfs(gdf_nodes_temp, gdf_edges_temp_fixed, graph_attrs=graph_attributes)
    nx.utils.misc.graphs_equal(piedmont_graph, piedmont_graph_temp_fixed)
    return (piedmont_graph_temp_fixed,)


@app.cell
def _(nx, piedmont_graph, piedmont_graph_temp):
    nx.utils.misc.nodes_equal(piedmont_graph.nodes, piedmont_graph_temp.nodes)
    return


@app.cell
def _(nx, piedmont_graph, piedmont_graph_temp):
    nx.utils.misc.edges_equal(piedmont_graph.edges, piedmont_graph_temp.edges)
    return


@app.cell
def _(nx, piedmont_graph, piedmont_graph_temp):
    nx.utils.misc.graphs_equal(piedmont_graph, piedmont_graph_temp)
    return


@app.cell
def _(piedmont_graph):
    piedmont_graph.adj
    return


@app.cell
def _(piedmont_graph_temp_fixed):
    piedmont_graph_temp_fixed.adj
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Deep investigation of diffs""")
    return


@app.cell
def _(piedmont_graph, piedmont_graph_temp_fixed):
    compare_graph_adjacency_objects(piedmont_graph.adj, piedmont_graph_temp_fixed.adj, 53127240, 53046249)
    return


@app.cell
def _(graphml_piedmont_graph, nx, piedmont_graph):
    piedmont_graph_diff = nx.difference(piedmont_graph, graphml_piedmont_graph)
    piedmont_graph_diff.nodes
    return


@app.cell
def _(geopackage_piedmont_graph, nx, piedmont_graph):
    piedmont_graph_diff_1 = nx.difference(piedmont_graph, geopackage_piedmont_graph)
    piedmont_graph_diff_1
    return (piedmont_graph_diff_1,)


@app.cell
def _(piedmont_graph_diff_1):
    piedmont_graph_diff_1.nodes
    return


@app.cell
def _(ox, piedmont_graph):
    # what sized area does our network cover in square meters?
    piedmont_graph_proj = ox.projection.project_graph(piedmont_graph)
    nodes_proj = ox.convert.graph_to_gdfs(piedmont_graph_proj, edges=False)
    graph_area_m = nodes_proj.union_all().convex_hull.area
    graph_area_m
    return (graph_area_m,)


@app.cell
def _(graph_area_m, ox, piedmont_graph):
    # show some basic stats about the network
    piedmont_graph_stats = ox.stats.basic_stats(piedmont_graph, area=graph_area_m, clean_int_tol=15)
    return


@app.cell
def _(geopackage_piedmont_graph, ox):
    geopackage_graph_area_m = ox.convert.graph_to_gdfs(ox.projection.project_graph(geopackage_piedmont_graph), edges=False).union_all().convex_hull.area
    geopackage_graph_area_m
    return (geopackage_graph_area_m,)


@app.cell
def _(geopackage_graph_area_m, geopackage_piedmont_graph, ox):
    geopackage_piedmont_graph_stats = ox.stats.basic_stats(geopackage_piedmont_graph, area=geopackage_graph_area_m, clean_int_tol=15)
    return


@app.cell
def _(ox, piedmont_graph):
    _fig, _ax = ox.plot.plot_graph(piedmont_graph)
    return


@app.cell
def _(geopackage_piedmont_graph, ox):
    _fig, _ax = ox.plot.plot_graph(geopackage_piedmont_graph)
    return


if __name__ == "__main__":
    app.run()
