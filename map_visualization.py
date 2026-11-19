import os
import osmnx as ox
import geopandas as gpd
import contextily as cx
import matplotlib.pyplot as plt

from shapely.geometry import Point, LineString


def draw_route_map(graph, locations, route=None,
                   source_node=None, destination_node=None,
                   route_distance=None, ax=None):

    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 8))
    else:
        fig = ax.figure

    # Project the walking graph to the coordinate system used by map tiles
    projected_graph = ox.project_graph(graph, to_crs="EPSG:3857")

    # Draw walking paths
    nodes, edges = ox.convert.graph_to_gdfs(
        projected_graph, nodes=True, edges=True
    )
    edges.plot(ax=ax, color="gray", linewidth=0.8, alpha=0.7, zorder=2)

    # Convert building coordinates to map coordinates
    building_rows = []

    for name, info in locations.items():
        node_id = info.get("node")

        if node_id not in projected_graph.nodes:
            continue

        node_data = projected_graph.nodes[node_id]

        building_rows.append({
            "name": name,
            "node": node_id,
            "geometry": Point(node_data["x"], node_data["y"])
        })

    if building_rows:
        buildings = gpd.GeoDataFrame(
            building_rows, geometry="geometry", crs="EPSG:3857"
        )

        buildings.plot(
            ax=ax, color="royalblue", markersize=35,
            edgecolor="white", linewidth=0.7, zorder=6
        )

        # Label each building
        for _, building in buildings.iterrows():
            ax.annotate(
                building["name"],
                (building.geometry.x, building.geometry.y),
                xytext=(5, 7),
                textcoords="offset points",
                fontsize=8,
                fontweight="bold",
                color="black",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="white",
                    edgecolor="gray",
                    alpha=0.85
                ),
                zorder=7
            )

    # Draw the selected route and display its distance
    if route and len(route) > 1:
        route_points = []

        for node_id in route:
            node = projected_graph.nodes[node_id]
            route_points.append((node["x"], node["y"]))

        route_line = LineString(route_points)

        route_gdf = gpd.GeoSeries(
            [route_line], crs="EPSG:3857"
        )

        route_gdf.plot(
            ax=ax, color="red", linewidth=4, zorder=10
        )

        # Mark the start and destination
        for node_id, color, label in [
            (source_node, "green", "Start"),
            (destination_node, "orange", "Destination")
        ]:
            if node_id in projected_graph.nodes:
                node = projected_graph.nodes[node_id]
                ax.scatter(
                    node["x"], node["y"],
                    color=color, s=100,
                    edgecolors="white", linewidths=1.5,
                    zorder=12, label=label
                )

        # Calculate distance from the original graph's edge lengths
        if route_distance is None:
            route_distance = 0.0

            for u, v in zip(route[:-1], route[1:]):
                edge_data = graph.get_edge_data(u, v)

                if edge_data:
                    route_distance += min(
                        float(edge.get("length", 0))
                        for edge in edge_data.values()
                    )

        # Put the distance label near the middle of the route
        middle_point = route_line.interpolate(0.5, normalized=True)

        ax.annotate(
            f"Distance: {route_distance:.1f} m "
            f"({route_distance / 1000:.3f} km)",
            xy=(middle_point.x, middle_point.y),
            xytext=(0, 25),
            textcoords="offset points",
            ha="center",
            fontsize=10,
            fontweight="bold",
            color="black",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor="white",
                edgecolor="red",
                alpha=0.95
            ),
            zorder=15
        )

        ax.legend(loc="best")

    # Load a different map background
    try:
        cx.add_basemap(
            ax,
            source=cx.providers.Esri.WorldGrauCanvas,
            attribution=True,
            zorder=1
        )
    except Exception as error:
        print("Unable to load map background:", error)

    ax.set_axis_off()
    ax.set_title("Campus Route Optimizer", fontsize=14, fontweight="bold")
    fig.tight_layout()

    return fig, ax

