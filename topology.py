import networkx as nx
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation

# Define a function to update the status of a node or edge
def update_status(obj, status):
    obj["status"] = status
  
# Get the status of a node
def get_status(obj):
    return obj["status"]

# Define a function to transmit a packet through the network
def transmit_packet(G, packet, source, target):
    # Find the shortest path from the source to the target
    path = nx.dijkstra_path(G, source, target, weight='time_taken')

    # Update the status of the source node
    update_status(G.nodes[source], "transmitting")

    # Transmit the packet along the path
    for i in range(len(path) - 1):
        # Update the status of the current edge
        update_status(G[path[i]][path[i+1]], "transmitting")

        # Update the status of the next node
        update_status(G.nodes[path[i+1]], "receiving")

    # Update the status of the target node
    update_status(G.nodes[target], "received")

packet = "Hello, World!"

# Create an empty graph
G = nx.Graph()

# Set the initial status of the nodes and edges
nx.set_node_attributes(G, "idle", "status")
nx.set_edge_attributes(G, "idle", "status")

# Add 50 nodes to the graph
for i in range(1, 51):
    if i == 50:  # Define destination_node
        G.add_node(i, size=10, color='red', interfaces=['eth0', 'eth1', 'eth2'])
        destination_node = i
    elif i == 1:  # Define source_node
        G.add_node(i, size=10, color='red', interfaces=['eth0', 'eth1', 'eth2'])
        source_node = i
    elif i == 2:  # Define bs1
        G.add_node(i, size=10, color='green', interfaces=['eth0', 'eth1', 'eth2', 'eth3', 'eth4'])
        bs1 = i
    elif i == 3:  # Define bs2
        G.add_node(i, size=10, color='green', interfaces=['eth0', 'eth1', 'eth2', 'eth3', 'eth4'])
        bs2 = i
    else:
        G.add_node(i, interfaces=['eth0', 'eth1', 'eth2', 'eth3', 'eth4'])

# Define a dictionary that maps each node to the number of free interfaces it has
free_interfaces = {}

# Iterate through all of the nodes in the graph
for i in G.nodes():
    # Assume that all of the interfaces are free
    free_interfaces[i] = len(G.nodes[i]['interfaces'])

# Connect nodes based on proximity
for i in G.nodes():
    for j in G.nodes():
        if i == j:
            continue
        distance = abs(i - j)  # Modify this based on your proximity criteria
        if distance <= 5 and free_interfaces[i] > 0 and free_interfaces[j] > 0:
            G.add_edge(i, j, weight=random.uniform(1, 15))
            free_interfaces[i] -= 1
            free_interfaces[j] -= 1

# Connect base stations with each other
G.add_edge(bs1, bs2, weight=1 / 15)

# Define the shortest path
shortest_path = nx.dijkstra_path(G, source_node, destination_node, weight='time_taken')
path_edges = list(zip(shortest_path, shortest_path[1:]))

# Set initial positions of nodes
pos = nx.random_layout(G)

# Animation
fig, ax = plt.subplots(figsize=(10, 8))

def update(frame):
    ax.clear()

    # Move nodes randomly
    for node in G.nodes():
        pos[node] = (pos[node][0] + random.uniform(-0.02, 0.02), pos[node][1] + random.uniform(-0.02, 0.02))

    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edges(G, pos, edgelist=path_edges[:frame + 1], edge_color='r', width=3)
    nx.draw_networkx_nodes(G, pos, nodelist=[source_node, destination_node], node_color='red')
    nx.draw_networkx_nodes(G, pos, nodelist=[bs1, bs2], node_color='yellow')
    ax.set_title(f'Frame {frame + 1}/{len(path_edges)}')

ani = FuncAnimation(fig, update, frames=len(path_edges), repeat=False)
plt.show()

# Wait for the animation to finish before displaying other details
plt.pause(5)

send = []
receive = []
delivered_packets = 0

# Send 5 packets along the path and save the state of source and destination in each list
for i in range(5):
    transmit_packet(G, packet, source_node, destination_node)
    send.append(get_status(G.nodes[source_node]))
    receive.append(get_status(G.nodes[destination_node]))

# Print details
print("-----------Details---------")
print(f"Shortest path: {shortest_path}")
print("Node status:")
print(nx.get_node_attributes(G, "status"))
print("Edge status:")
print(nx.get_edge_attributes(G, "status"))
print(f"Number of Hops: {len(shortest_path) - 1}")
print(f"Number of Hello packets sent: {5}")
plt.show()
