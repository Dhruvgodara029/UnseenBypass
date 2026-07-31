import os
import sys
import subprocess
import random
import pandas as pd

if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci
import sumolib

SUMO_BIN = sumolib.checkBinary("sumo")

def build_network(fast_len, slow_len, mid_len, fast_speed, slow_speed):
    """Write a randomized Braess-diamond network and convert it."""
    nodes = """<nodes>
    <node id="start" x="0"    y="0"/>
    <node id="A"     x="500"  y="200"/>
    <node id="B"     x="500"  y="-200"/>
    <node id="end"   x="1000" y="0"/>
</nodes>"""
    edges = f"""<edges>
    <edge id="start_A" from="start" to="A"   numLanes="1" speed="{fast_speed}" length="{fast_len}"/>
    <edge id="A_end"   from="A"     to="end" numLanes="1" speed="{slow_speed}" length="{slow_len}"/>
    <edge id="start_B" from="start" to="B"   numLanes="1" speed="{slow_speed}" length="{slow_len}"/>
    <edge id="B_end"   from="B"     to="end" numLanes="1" speed="{fast_speed}" length="{fast_len}"/>
    <edge id="A_B"     from="A"     to="B"   numLanes="1" speed="{fast_speed}" length="{mid_len}"/>
</edges>"""
    with open("sweep.nod.xml", "w") as f: f.write(nodes)
    with open("sweep.edg.xml", "w") as f: f.write(edges)
    subprocess.run(["netconvert", "--node-files", "sweep.nod.xml",
                    "--edge-files", "sweep.edg.xml", "--output-file", "sweep.net.xml",
                    "--no-warnings", "true"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build_routes(demand):
    routes = f"""<routes>
    <vType id="car" accel="2.6" decel="4.5" length="5" maxSpeed="13.89"/>
    <flow id="main" type="car" begin="0" end="500" number="{demand}"
          fromJunction="start" toJunction="end">
        <param key="has.rerouting.device" value="true"/>
    </flow>
</routes>"""
    with open("sweep.rou.xml", "w") as f: f.write(routes)

def total_travel_time(close_edge=None):
    cmd = [SUMO_BIN, "-n", "sweep.net.xml", "-r", "sweep.rou.xml",
           "--no-step-log", "true", "--no-warnings", "true",
           "--time-to-teleport", "300", "--ignore-route-errors", "true",
           "--device.rerouting.probability", "1.0",
           "--device.rerouting.pre-period", "10",
           "--junction-taz", "true"]
    traci.start(cmd)
    if close_edge:
        try: traci.edge.setDisallowed(close_edge, ["all"])
        except traci.TraCIException: pass
    tt, step = 0.0, 0
    try:
        while traci.simulation.getMinExpectedNumber() > 0 and step < 5000:
            traci.simulationStep()
            tt += traci.vehicle.getIDCount()
            step += 1
    except traci.TraCIException:
        pass
    finally:
        traci.close()
    return tt

# ---- The sweep ----
N_NETWORKS = 1200          # each network = 1 row (its middle edge). Raise for more data.
rows = []
random.seed(42)

for i in range(1, N_NETWORKS + 1):
    # randomize the parameters across a wide range
    fast_len   = random.randint(50, 400)
    slow_len   = random.randint(400, 1000)
    mid_len    = random.randint(20, 300)
    fast_speed = round(random.uniform(8.0, 20.0), 2)
    slow_speed = round(random.uniform(5.0, 15.0), 2)
    demand     = random.randint(400, 1600)

    build_network(fast_len, slow_len, mid_len, fast_speed, slow_speed)
    build_routes(demand)

    baseline  = total_travel_time()
    no_middle = total_travel_time(close_edge="A_B")
    delta = baseline - no_middle          # positive = removing A_B helped = Braess
    is_braess = 1 if delta > (0.01 * baseline) else 0

    rows.append({
        "network_id": i,
        "mid_length_m": mid_len,
        "mid_speed_mps": fast_speed,
        "fast_length_m": fast_len,
        "slow_length_m": slow_len,
        "slow_speed_mps": slow_speed,
        "demand": demand,
        "free_flow_mid_time_s": round(mid_len / fast_speed, 3),
        "length_ratio": round(fast_len / slow_len, 3),
        "baseline_tt": round(baseline, 1),
        "no_middle_tt": round(no_middle, 1),
        "delta": round(delta, 1),
        "is_braess_road": is_braess,
    })

    if i % 20 == 0:
        n1 = sum(r["is_braess_road"] for r in rows)
        print(f"[{i}/{N_NETWORKS}] Braess so far: {n1} ({n1/len(rows)*100:.1f}%)")

df = pd.DataFrame(rows)
df.to_csv("braess_dataset.csv", index=False)
n1 = df["is_braess_road"].sum()
print(f"\nDone. {len(df)} networks, {n1} Braess ({n1/len(df)*100:.1f}%)")
print("Wrote braess_dataset.csv")