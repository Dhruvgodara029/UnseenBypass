import sumolib
import xml.etree.ElementTree as ET
import pandas as pd

# --- 1. Read the network: per-edge static properties + graph structure ---
net = sumolib.net.readNet("grid.net.xml")

rows = {}
for edge in net.getEdges():
    if edge.isSpecial():          # skip internal junction edges
        continue
    eid = edge.getID()
    from_node = edge.getFromNode()
    to_node = edge.getToNode()
    length = edge.getLength()
    speed = edge.getSpeed()       # m/s
    lanes = edge.getLaneNumber()
    rows[eid] = {
        "edge_id": eid,
        "from_node_id": from_node.getID(),
        "to_node_id": to_node.getID(),
        "length_m": round(length, 2),
        "speed_limit_mps": round(speed, 2),
        "num_lanes": lanes,
        "priority": edge.getPriority(),
        "road_type": edge.getType() or "grid.road",
        "free_flow_travel_time_s": round(length / speed, 4) if speed > 0 else 0,
        "from_junction_degree": len(from_node.getIncoming()) + len(from_node.getOutgoing()),
        "to_junction_degree": len(to_node.getIncoming()) + len(to_node.getOutgoing()),
    }

# --- 2. Read the edge-output XML: per-edge traffic statistics ---
tree = ET.parse("edge_output.xml")
for interval in tree.getroot().findall("interval"):
    for edge in interval.findall("edge"):
        eid = edge.get("id")
        if eid not in rows:
            continue
        def g(attr, default=0.0):
            v = edge.get(attr)
            return float(v) if v is not None else default
        rows[eid].update({
            "baseline_traveltime_s": round(g("traveltime"), 2),
            "baseline_density_vpm": round(g("density"), 2),
            "baseline_lane_density_vpmpl": round(g("laneDensity"), 2),
            "baseline_occupancy_perc": round(g("occupancy"), 2),
            "baseline_waiting_time_s": round(g("waitingTime"), 2),
            "baseline_time_loss_s": round(g("timeLoss"), 2),
            "baseline_speed_mps": round(g("speed"), 2),
            "baseline_departed_count": int(g("departed")),
            "baseline_arrived_count": int(g("arrived")),
            "baseline_entered_count": int(g("entered")),
            "baseline_left_count": int(g("left")),
        })

# --- 3. Build DataFrame; fill edges that saw no traffic with zeros ---
df = pd.DataFrame(list(rows.values()))
traffic_cols = [
    "baseline_traveltime_s", "baseline_density_vpm", "baseline_lane_density_vpmpl",
    "baseline_occupancy_perc", "baseline_waiting_time_s", "baseline_time_loss_s",
    "baseline_speed_mps", "baseline_departed_count", "baseline_arrived_count",
    "baseline_entered_count", "baseline_left_count",
]
for c in traffic_cols:
    if c not in df.columns:
        df[c] = 0
df[traffic_cols] = df[traffic_cols].fillna(0)

df.to_csv("features.csv", index=False)
print(f"Wrote features.csv with {len(df)} rows and {len(df.columns)} columns")
print(df.head())