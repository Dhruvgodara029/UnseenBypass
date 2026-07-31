import os
import sys
import pandas as pd

# Make SUMO's python tools importable
if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
import sumolib

SUMO_BIN = sumolib.checkBinary("sumo")   # headless
NET_FILE = "grid.net.xml"
ROUTES   = "routes.rou.xml"

def total_travel_time(closed_edge=None):
    """Run one simulation; return total time all vehicles spend in the network.
    If closed_edge is given, that edge is closed to traffic (simulating removal)."""
    cmd = [SUMO_BIN, "-n", NET_FILE, "-r", ROUTES,
           "--no-step-log", "true", "--no-warnings", "true",
           "--time-to-teleport", "300",
           "--ignore-route-errors", "true",
           "--device.rerouting.probability", "0.3"]
    traci.start(cmd)

    if closed_edge is not None:
        try:
            traci.edge.setDisallowed(closed_edge, ["all"])
        except traci.TraCIException:
            pass

    total_time = 0.0
    step = 0
    try:
        while traci.simulation.getMinExpectedNumber() > 0 and step < 3000:
            traci.simulationStep()
            total_time += traci.vehicle.getIDCount()
            step += 1
    except traci.TraCIException:
        pass
    finally:
        traci.close()
    return total_time

# --- 1. Baseline: no edges removed ---
print("Running baseline...")
baseline = total_travel_time()
print(f"Baseline total travel time: {baseline:.0f} vehicle-seconds")

# --- 2. Load the edges we built features for ---
df = pd.read_csv("features.csv")
edge_ids = df["edge_id"].tolist()

# --- 3. Remove each edge, re-run, compare ---
labels = {}
deltas = []
for i, eid in enumerate(edge_ids, 1):
    tt = total_travel_time(closed_edge=eid)
    delta = baseline - tt          # positive = removal HELPED (Braess-like)
    deltas.append((eid, delta))
    # Braess road: removal improves travel time by more than a small tolerance
    labels[eid] = 1 if delta > (0.01 * baseline) else 0
    print(f"[{i}/{len(edge_ids)}] {eid}: tt={tt:.0f}  delta={delta:+.0f}")

# --- 4. Attach labels and save ---
df["is_braess_road"] = df["edge_id"].map(labels)
df.to_csv("data.csv", index=False)

n_braess = df["is_braess_road"].sum()
print(f"\nDone. {n_braess} Braess roads out of {len(df)} ({n_braess/len(df)*100:.1f}%)")

# Show the most impactful removals so we can sanity-check the metric
deltas.sort(key=lambda x: x[1], reverse=True)
print("\nTop 5 removals that helped most (highest positive delta):")
for eid, d in deltas[:5]:
    print(f"  {eid}: {d:+.0f}")
print("Bottom 5 (removal hurt most):")
for eid, d in deltas[-5:]:
    print(f"  {eid}: {d:+.0f}")