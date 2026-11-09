import os
import sys
import json
import math
import tkinter.messagebox as messagebox

import customtkinter as ctk
import osmnx as ox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from map_visualization import draw_route_map

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from map_visualization import draw_route_map


GRAPH_FILE = os.path.join(
    PROJECT_ROOT, "data", "campus_graph.graphml"
)
LOCATIONS_FILE = os.path.join(
    PROJECT_ROOT, "data", "locations.json"
)


def load_locations(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Accept either {"Library": {...}} or [{"name": "Library", ...}]
    if isinstance(data, list):
        locations = {}

        for item in data:
            name = item.get("name")
            if name:
                locations[name] = item

        return locations

    return data


class CampusRouteOptimizer(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Campus Route Optimizer")
        self.geometry("1200x750")
        self.minsize(900, 600)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Load campus graph and building data
        try:
            self.graph = ox.load_graphml(GRAPH_FILE)
            self.locations = load_locations(LOCATIONS_FILE)

            # Convert JSON node IDs to the same type as graph node IDs
            graph_nodes = set(self.graph.nodes)

            for name, info in self.locations.items():
                node_id = info.get("node")

                if node_id is not None and node_id not in graph_nodes:
                    try:
                        converted_id = int(node_id)
                        if converted_id in graph_nodes:
                            info["node"] = converted_id
                    except (ValueError, TypeError):
                        pass

            self.locations = {
                name: info for name, info in self.locations.items()
                if info.get("node") in graph_nodes
            }

            if not self.locations:
                raise ValueError(
                    "No valid building nodes found in locations.json."
                )

        except Exception as error:
            messagebox.showerror(
                "Loading Error",
                f"Could not load campus data.\n\n{error}"
            )
            self.destroy()
            raise

        self.building_names = sorted(self.locations.keys())

        self.create_widgets()
        self.show_map()

    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left control panel
        self.panel = ctk.CTkFrame(self, width=280)
        self.panel.grid(
            row=0, column=0, sticky="ns", padx=12, pady=12
        )
        self.panel.grid_propagate(False)

        ctk.CTkLabel(
            self.panel,
            text="Campus Route Optimizer",
            font=ctk.CTkFont(size=21, weight="bold"),
            wraplength=240
        ).pack(padx=15, pady=(25, 25))

        ctk.CTkLabel(
            self.panel, text="Starting Building"
        ).pack(anchor="w", padx=18, pady=(5, 5))

        self.start_box = ctk.CTkComboBox(
            self.panel,
            values=self.building_names,
            width=235
        )
        self.start_box.pack(padx=15, pady=(0, 15))
        self.start_box.set(self.building_names[0])

        ctk.CTkLabel(
            self.panel, text="Destination Building"
        ).pack(anchor="w", padx=18, pady=(5, 5))

        self.destination_box = ctk.CTkComboBox(
            self.panel,
            values=self.building_names,
            width=235
        )
        self.destination_box.pack(padx=15, pady=(0, 15))

        default_destination = (
            self.building_names[1]
            if len(self.building_names) > 1
            else self.building_names[0]
        )
        self.destination_box.set(default_destination)

        ctk.CTkLabel(
            self.panel, text="Shortest Path Algorithm"
        ).pack(anchor="w", padx=18, pady=(5, 5))

        self.algorithm_box = ctk.CTkComboBox(
            self.panel,
            values=["Dijkstra", "A*"],
            width=235
        )
        self.algorithm_box.pack(padx=15, pady=(0, 20))
        self.algorithm_box.set("Dijkstra")

        ctk.CTkButton(
            self.panel,
            text="Find Route",
            command=self.find_route,
            height=40
        ).pack(padx=15, pady=7, fill="x")

        ctk.CTkButton(
            self.panel,
            text="Reset Map",
            command=self.reset_map,
            height=38
        ).pack(padx=15, pady=7, fill="x")

        self.distance_label = ctk.CTkLabel(
            self.panel,
            text="Distance: --",
            font=ctk.CTkFont(size=15, weight="bold"),
            wraplength=240
        )
        self.distance_label.pack(
            padx=12, pady=(25, 8), anchor="w"
        )

        self.time_label = ctk.CTkLabel(
            self.panel,
            text="Walking time: --",
            font=ctk.CTkFont(size=14),
            wraplength=240
        )
        self.time_label.pack(
            padx=12, pady=5, anchor="w"
        )

        self.status_label = ctk.CTkLabel(
            self.panel,
            text="Select two buildings to begin.",
            wraplength=240,
            justify="left"
        )
        self.status_label.pack(
            padx=12, pady=(15, 10), anchor="w"
        )

        # Right map panel
        self.map_frame = ctk.CTkFrame(self)
        self.map_frame.grid(
            row=0, column=1, sticky="nsew", padx=(0, 12), pady=12
        )
        self.map_frame.grid_rowconfigure(0, weight=1)
        self.map_frame.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(9, 7), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(
            self.figure, master=self.map_frame
        )
        self.canvas.get_tk_widget().grid(
            row=0, column=0, sticky="nsew"
        )

    def show_map(self, route=None, source_node=None,
                 destination_node=None, distance=None):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        draw_route_map(
            self.graph,
            self.locations,
            route=route,
            source_node=source_node,
            destination_node=destination_node,
            route_distance=distance,
            ax=self.ax
        )

        self.canvas.draw_idle()

    def find_route(self):
        start_name = self.start_box.get()
        destination_name = self.destination_box.get()
        algorithm_name = self.algorithm_box.get()

        if start_name not in self.locations:
            messagebox.showerror(
                "Invalid Start", "Select a valid starting building."
            )
            return

        if destination_name not in self.locations:
            messagebox.showerror(
                "Invalid Destination",
                "Select a valid destination building."
            )
            return

        source_node = self.locations[start_name]["node"]
        destination_node = self.locations[destination_name]["node"]

        if source_node == destination_node:
            self.distance_label.configure(text="Distance: 0 m")
            self.time_label.configure(text="Walking time: 0 minutes")
            self.status_label.configure(
                text="Both locations map to the same network node. "
                     "Check their coordinates in locations.json."
            )
            self.show_map(
                route=[source_node],
                source_node=source_node,
                destination_node=destination_node,
                distance=0
            )
            return

        try:
            if algorithm_name == "A*":
                route, distance = astar(
                    self.graph, source_node, destination_node
                )
            else:
                route, distance = dijkstra(
                    self.graph, source_node, destination_node
                )

            if not route or not math.isfinite(float(distance)):
                messagebox.showwarning(
                    "No Route",
                    "No walking route was found between these buildings."
                )
                self.distance_label.configure(text="Distance: unavailable")
                self.time_label.configure(text="Walking time: unavailable")
                self.status_label.configure(text="No route found.")
                self.show_map()
                return

            distance = float(distance)

            # Approximate walking speed: 80 metres per minute
            walking_minutes = math.ceil(distance / 80)

            self.distance_label.configure(
                text=f"Distance: {distance:.1f} m "
                     f"({distance / 1000:.3f} km)"
            )
            self.time_label.configure(
                text=f"Walking time: about {walking_minutes} min"
            )
            self.status_label.configure(
                text=f"Route: {start_name}\nto {destination_name}\n"
                     f"Algorithm: {algorithm_name}"
            )

            self.show_map(
                route=route,
                source_node=source_node,
                destination_node=destination_node,
                distance=distance
            )

        except Exception as error:
            messagebox.showerror(
                "Route Error",
                f"An error occurred while finding the route:\n{error}"
            )

    def reset_map(self):
        self.start_box.set(self.building_names[0])

        if len(self.building_names) > 1:
            self.destination_box.set(self.building_names[1])
        else:
            self.destination_box.set(self.building_names[0])

        self.algorithm_box.set("Dijkstra")
        self.distance_label.configure(text="Distance: --")
        self.time_label.configure(text="Walking time: --")
        self.status_label.configure(
            text="Select two buildings to begin."
        )
        self.show_map()


if __name__ == "__main__":
    app = CampusRouteOptimizer()
    app.mainloop()


import os
import sys
import json
import heapq
import math
import tkinter.messagebox as messagebox

import customtkinter as ctk
import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Make the main project folder accessible for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from map_visualization import draw_route_map

# Try importing your alternative route algorithm
try:
    from algorithms.alternative_routes import yen_k_shortest_paths
    ALTERNATIVE_ROUTES_AVAILABLE = True
except ImportError:
    ALTERNATIVE_ROUTES_AVAILABLE = False


# --------------------------------------------------
# APPLICATION SETTINGS
# --------------------------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_MAIN = "#0a1128"
BG_PANEL = "#0d1b3e"
BG_CARD = "#14295c"
ACCENT = "#1f6feb"
TEAL = "#1fc8c0"
TEXT = "#ffffff"
MUTED = "#aab7cf"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GRAPH_PATH = os.path.join(
    BASE_DIR, "data", "campus_graph.graphml"
)

LOCATIONS_PATH = os.path.join(
    BASE_DIR, "data", "locations.json"
)


# --------------------------------------------------
# LOAD CAMPUS DATA
# --------------------------------------------------

if not os.path.exists(GRAPH_PATH):
    raise FileNotFoundError(
        f"Campus graph not found: {GRAPH_PATH}"
    )

if not os.path.exists(LOCATIONS_PATH):
    raise FileNotFoundError(
        f"Locations file not found: {LOCATIONS_PATH}"
    )

original_graph = ox.load_graphml(GRAPH_PATH)

with open(LOCATIONS_PATH, "r", encoding="utf-8") as file:
    locations = json.load(file)


def get_node_id(value):

    try:
        node_id = int(value)
    except (ValueError, TypeError):
        node_id = value

    if node_id not in original_graph.nodes:
        raise ValueError(
            f"Node {node_id} does not exist in campus graph."
        )

    return node_id


# Prepare a simple weighted graph for routing
routing_graph = nx.DiGraph()

for u, v, data in original_graph.edges(data=True):

    distance = float(data.get("length", 1))

    if (
        not routing_graph.has_edge(u, v)
        or distance < routing_graph[u][v]["weight"]
    ):
        routing_graph.add_edge(
            u, v, weight=distance
        )


# --------------------------------------------------
# ROUTING FUNCTIONS
# --------------------------------------------------

def haversine_distance(node1, node2):

    a = original_graph.nodes[node1]
    b = original_graph.nodes[node2]

    lat1 = math.radians(float(a["y"]))
    lon1 = math.radians(float(a["x"]))

    lat2 = math.radians(float(b["y"]))
    lon2 = math.radians(float(b["x"]))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    value = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 6371000 * 2 * math.asin(
        min(1, math.sqrt(value))
    )


def find_shortest_path(source, destination, algorithm):

    if source == destination:
        return [source]

    if algorithm == "Dijkstra":

        return nx.dijkstra_path(
            routing_graph,
            source,
            destination,
            weight="weight"
        )

    if algorithm == "A*":

        return nx.astar_path(
            routing_graph,
            source,
            destination,
            heuristic=haversine_distance,
            weight="weight"
        )

    return []


def calculate_distance(path):

    total = 0

    for u, v in zip(path[:-1], path[1:]):
        total += routing_graph[u][v]["weight"]

    return total


def calculate_walking_time(distance):

    # Assumed walking speed: 5 km/hour
    speed = 5000 / 60

    return distance / speed


def get_routes(source, destination, algorithm):

    if ALTERNATIVE_ROUTES_AVAILABLE:

        routes = yen_k_shortest_paths(
            routing_graph,
            source,
            destination,
            k=3
        )

        if routes:
            return routes

    # Fallback: display the primary route
    return [
        find_shortest_path(
            source,
            destination,
            algorithm
        )
    ]


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

class CampusRouteOptimizer(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Campus Route Optimizer")
        self.geometry("1450x850")
        self.minsize(1100, 700)

        self.configure(fg_color=BG_MAIN)

        self.routes = []
        self.selected_route = None
        self.canvas = None
        self.fig = None
        self.ax = None

        self.create_interface()
        self.display_initial_map()

    # --------------------------------------------------
    # INTERFACE
    # --------------------------------------------------

    def create_interface(self):

        # Main heading
        header = ctk.CTkFrame(
            self,
            fg_color=BG_PANEL,
            corner_radius=12,
            height=65
        )

        header.pack(
            fill="x",
            padx=15,
            pady=(15, 8)
        )

        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="CAMPUS ROUTE OPTIMIZER",
            font=("Arial", 23, "bold"),
            text_color=TEAL
        ).pack(
            side="left",
            padx=20,
            pady=12
        )

        ctk.CTkLabel(
            header,
            text="Graphic Era University | Smart Campus Navigation",
            font=("Arial", 12),
            text_color=MUTED
        ).pack(
            side="right",
            padx=20
        )

        # Main content area
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=BG_MAIN
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=8
        )

        # Left sidebar
        self.sidebar = ctk.CTkFrame(
            self.main_frame,
            width=310,
            fg_color=BG_PANEL,
            corner_radius=15
        )

        self.sidebar.pack(
            side="left",
            fill="y",
            padx=(0, 10),
            pady=5
        )

        self.sidebar.pack_propagate(False)

        self.create_sidebar()

        # Right map area
        self.map_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=BG_PANEL,
            corner_radius=15
        )

        self.map_frame.pack(
            side="right",
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.map_title = ctk.CTkLabel(
            self.map_frame,
            text="Campus Map",
            font=("Arial", 18, "bold"),
            text_color=TEAL
        )

        self.map_title.pack(
            anchor="w",
            padx=15,
            pady=10
        )

        self.map_canvas_frame = ctk.CTkFrame(
            self.map_frame,
            fg_color="#e8edf2",
            corner_radius=10
        )

        self.map_canvas_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

    # --------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------

    def create_sidebar(self):

        ctk.CTkLabel(
            self.sidebar,
            text="Plan Your Journey",
            font=("Arial", 21, "bold"),
            text_color=TEXT
        ).pack(
            anchor="w",
            padx=18,
            pady=(20, 15)
        )

        # Starting location
        ctk.CTkLabel(
            self.sidebar,
            text="START LOCATION",
            font=("Arial", 11, "bold"),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=18
        )

        self.start_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=list(locations.keys()),
            height=40,
            fg_color=BG_CARD,
            button_color=ACCENT,
            button_hover_color=TEAL,
            dropdown_fg_color=BG_PANEL
        )

        self.start_menu.pack(
            fill="x",
            padx=18,
            pady=(5, 15)
        )

        # Destination
        ctk.CTkLabel(
            self.sidebar,
            text="DESTINATION",
            font=("Arial", 11, "bold"),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=18
        )

        self.destination_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=list(locations.keys()),
            height=40,
            fg_color=BG_CARD,
            button_color=ACCENT,
            button_hover_color=TEAL,
            dropdown_fg_color=BG_PANEL
        )

        self.destination_menu.pack(
            fill="x",
            padx=18,
            pady=(5, 15)
        )

        # Algorithm selection
        ctk.CTkLabel(
            self.sidebar,
            text="SELECT ALGORITHM",
            font=("Arial", 11, "bold"),
            text_color=MUTED
        ).pack(
            anchor="w",
            padx=18
        )

        self.algorithm_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dijkstra", "A*"],
            height=40,
            fg_color=BG_CARD,
            button_color=ACCENT,
            dropdown_fg_color=BG_PANEL
        )

        self.algorithm_menu.pack(
            fill="x",
            padx=18,
            pady=(5, 18)
        )

        # Find route
        ctk.CTkButton(
            self.sidebar,
            text="Find Route",
            height=43,
            fg_color=ACCENT,
            hover_color="#1558b0",
            font=("Arial", 14, "bold"),
            command=self.find_route
        ).pack(
            fill="x",
            padx=18,
            pady=5
        )

        # Reset
        ctk.CTkButton(
            self.sidebar,
            text="Reset Map",
            height=40,
            fg_color="#344563",
            hover_color="#465a78",
            command=self.reset_map
        ).pack(
            fill="x",
            padx=18,
            pady=5
        )

        # Route selection
        ctk.CTkLabel(
            self.sidebar,
            text="ALTERNATIVE ROUTES",
            font=("Arial", 12, "bold"),
            text_color=TEAL
        ).pack(
            anchor="w",
            padx=18,
            pady=(22, 5)
        )

        self.route_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["No routes available"],
            height=38,
            fg_color=BG_CARD,
            button_color=ACCENT,
            command=self.select_route
        )

        self.route_menu.pack(
            fill="x",
            padx=18,
            pady=5
        )

        # Route information
        ctk.CTkLabel(
            self.sidebar,
            text="ROUTE INFORMATION",
            font=("Arial", 12, "bold"),
            text_color=TEAL
        ).pack(
            anchor="w",
            padx=18,
            pady=(20, 8)
        )

        self.info_card = ctk.CTkFrame(
            self.sidebar,
            fg_color=BG_CARD,
            corner_radius=10
        )

        self.info_card.pack(
            fill="x",
            padx=15,
            pady=5
        )

        self.distance_label = self.create_info_label(
            "Distance: --"
        )

        self.time_label = self.create_info_label(
            "Walking Time: --"
        )

        self.algorithm_label = self.create_info_label(
            "Algorithm: --"
        )

        self.route_count_label = self.create_info_label(
            "Available Routes: --"
        )

        ctk.CTkLabel(
            self.sidebar,
            text="Choose a destination to begin navigation.",
            font=("Arial", 11),
            text_color=MUTED,
            wraplength=260
        ).pack(
            anchor="w",
            padx=18,
            pady=15
        )

    def create_info_label(self, text):

        label = ctk.CTkLabel(
            self.info_card,
            text=text,
            font=("Arial", 12),
            text_color=TEXT,
            anchor="w"
        )

        label.pack(
            fill="x",
            padx=12,
            pady=8
        )

        return label

    # --------------------------------------------------
    # INITIAL MAP
    # --------------------------------------------------

    def display_initial_map(self):

        try:

            self.fig, self.ax = draw_route_map(
                graph=original_graph,
                locations=locations
            )

            self.canvas = FigureCanvasTkAgg(
                self.fig,
                master=self.map_canvas_frame
            )

            self.canvas.draw()

            self.canvas.get_tk_widget().pack(
                fill="both",
                expand=True
            )

        except Exception as error:

            messagebox.showerror(
                "Map Error",
                str(error)
            )

    # --------------------------------------------------
    # FIND ROUTE
    # --------------------------------------------------

    def find_route(self):

        start_name = self.start_menu.get()
        destination_name = self.destination_menu.get()

        algorithm = self.algorithm_menu.get()

        if start_name == destination_name:

            messagebox.showwarning(
                "Invalid Selection",
                "Start and destination cannot be the same."
            )

            return

        try:

            source = get_node_id(
                locations[start_name]["node"]
            )

            destination = get_node_id(
                locations[destination_name]["node"]
            )

            self.routes = get_routes(
                source,
                destination,
                algorithm
            )

            if not self.routes:

                messagebox.showinfo(
                    "No Route",
                    "No available route found."
                )

                return

            self.route_menu.configure(
                values=[
                    f"Route {i + 1}"
                    for i in range(len(self.routes))
                ]
            )

            self.route_menu.set("Route 1")

            self.selected_route = 0

            self.show_selected_route(algorithm)

        except nx.NetworkXNoPath:

            messagebox.showerror(
                "No Route",
                "No walking path exists between these locations."
            )

        except nx.NodeNotFound:

            messagebox.showerror(
                "Location Error",
                "Selected location is not connected to the campus graph."
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                str(error)
            )

    # --------------------------------------------------
    # SELECT ALTERNATIVE ROUTE
    # --------------------------------------------------

    def select_route(self, selected):

        if not self.routes:
            return

        try:

            index = int(selected.split()[-1]) - 1

            if 0 <= index < len(self.routes):

                self.selected_route = index

                self.show_selected_route(
                    self.algorithm_menu.get()
                )

        except (ValueError, IndexError):
            return

    # --------------------------------------------------
    # DISPLAY SELECTED ROUTE
    # --------------------------------------------------

    def show_selected_route(self, algorithm):

        if self.selected_route is None:
            return

        route = self.routes[self.selected_route]

        distance = calculate_distance(route)

        walking_time = calculate_walking_time(
            distance
        )

        source = route[0]
        destination = route[-1]

        # Update route information
        self.distance_label.configure(
            text=f"Distance: {distance:.2f} metres"
        )

        self.time_label.configure(
            text=f"Walking Time: {walking_time:.1f} minutes"
        )

        self.algorithm_label.configure(
            text=f"Algorithm: {algorithm}"
        )

        self.route_count_label.configure(
            text=f"Available Routes: {len(self.routes)}"
        )

        # Redraw the map
        try:

            if self.fig is not None:
                plt.close(self.fig)

            self.fig, self.ax = draw_route_map(
                graph=original_graph,
                locations=locations,
                route=route,
                source_node=source,
                destination_node=destination,
                route_distance=distance
            )

            if self.canvas is not None:

                self.canvas.get_tk_widget().destroy()

            self.canvas = FigureCanvasTkAgg(
                self.fig,
                master=self.map_canvas_frame
            )

            self.canvas.draw()

            self.canvas.get_tk_widget().pack(
                fill="both",
                expand=True
            )

        except Exception as error:

            messagebox.showerror(
                "Map Error",
                str(error)
            )

    # --------------------------------------------------
    # RESET
    # --------------------------------------------------

    def reset_map(self):

        self.routes = []
        self.selected_route = None

        self.route_menu.configure(
            values=["No routes available"]
        )

        self.route_menu.set(
            "No routes available"
        )

        self.distance_label.configure(
            text="Distance: --"
        )

        self.time_label.configure(
            text="Walking Time: --"
        )

        self.algorithm_label.configure(
            text="Algorithm: --"
        )

        self.route_count_label.configure(
            text="Available Routes: --"
        )

        if self.fig is not None:
            plt.close(self.fig)

        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        self.display_initial_map()


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app = CampusRouteOptimizer()

    app.mainloop()
