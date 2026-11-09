# Campus Route Optimizer

A Python-based campus navigation system designed to help users find routes between different locations within the Graphic Era Deemed to be University campus, Dehradun.

The project uses graph-based data structures and shortest-path algorithms to calculate routes between selected campus locations. It also provides alternative route suggestions and map-based visualization through a graphical user interface.

## Project Overview

The Campus Route Optimizer represents the university campus as a weighted graph in which locations are represented as nodes and paths connecting them are represented as edges.

Users can select a starting location and destination, choose a pathfinding algorithm, and find a suitable route across the campus.

## Features

- **Campus Location Mapping:** Stores important campus locations and their geographical coordinates.
- **Graph Representation:** Represents campus locations and connections using a weighted graph.
- **Dijkstra's Algorithm:** Finds the shortest path between selected locations.
- **A* Search Algorithm:** Uses a heuristic-based approach for pathfinding.
- **Alternative Route Suggestions:** Provides alternative route options when available.
- **Interactive Graphical Interface:** Allows users to select starting points, destinations, and algorithms.
- **Map Visualization:** Displays routes using OpenStreetMap-based geographical visualization.
- **Route Information:** Displays relevant route details, including distance and estimated walking time.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CustomTkinter | Graphical user interface |
| TkinterMapView | Interactive map display |
| OpenStreetMap | Geographical map data |
| OSMnx | Campus geographical network data |
| NetworkX | Graph creation and manipulation |
| JSON | Storage of campus location information |
| GraphML | Storage of graph data |
| Heapq | Priority queue operations for pathfinding |
| Git and GitHub | Version control and collaboration |

## Algorithms Used

### 1. Dijkstra's Algorithm
Dijkstra's algorithm is used to calculate the shortest path between a starting location and a destination in a weighted graph.

### 2. A* Search Algorithm
A* is a heuristic-based search algorithm that uses the actual path cost and an estimated remaining cost to guide the search towards the destination.

### 3. Alternative Route Suggestions
The project includes an alternative route feature to provide additional route options when available.

## Project Structure

```text
Campus-Route-Optimizer/
│
├── algorithms/
│   ├── dijkstra.py
│   └── astar.py
│   └── alternative_routes.py
|   
│
├── data/
│   ├── campus_graph.graphml
│   ├── locations.json
│   ├── distances.csv
│   └── get_campus_data.py
│
├── gui/
│   └──app.py
│   
│
├── integration.py
├── map_visualization-1.py
├── campus.graphml
├── campus_route_map.html
├── calculate_distances.py
├── get_campus_data.py
├── main.py
├── setup_locations.py
├── testing.py
└── README.md
```

*Note: This is an illustrative project structure. Update it to match the actual folders and files present in your GitHub repository.*

## Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/bishtmedhavi857-cyber/Campus-Route-Optimizer.git
```

### Step 2: Open the Project Folder

```bash
cd Campus-Route-Optimizer
```

### Step 3: Create a Virtual Environment (Recommended)

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### Step 4: Install Required Libraries

Install the dependencies required by the project:

```bash
pip install customtkinter tkintermapview networkx osmnx
```

Install any additional packages required by the modules in your project.

### Step 5: Run the Application

If `main.py` is the application entry point, run:

```bash
python main.py
```

## Data Source

The project uses geographical information from **OpenStreetMap (OSM)** to represent campus locations and paths.

Campus graph data is stored in GraphML format, while location details are maintained in JSON format.

## Team Members

1. Medhavi Bisht
2. Devyanshi Sah
3. Ria Sharma
4. Sneha Pal

**Project Guide:** Ms. Rashmi Kanyal

**Institution:** Graphic Era Deemed to be University, Dehradun, Uttarakhand.

## Future Enhancements

- Improve route visualization and map interaction.
- Enhance alternative route generation.
- Improve route accuracy and campus connectivity.
- Add more campus locations.
- Optimize pathfinding performance.

## Repository

GitHub: https://github.com/bishtmedhavi857-cyber/Campus-Route-Optimizer

---

*Campus Route Optimizer – Making campus navigation easier through graph algorithms and geographical data.*