import os, sys
if "SUMO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUMO_HOME"], "tools"))
import traci, sumolib

SUMO_BIN = sumolib.checkBinary("sumo")

def run(close_edge=None):
    cmd = [SUMO_BIN, "-n", "braess.net.xml", "-r", "braess.rou.xml",
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

baseline = run()
no_middle = run(close_edge="A_B")
print(f"With middle link A_B:    {baseline:.0f}")
print(f"Without middle link A_B: {no_middle:.0f}")
print(f"Removing A_B changed travel time by: {baseline - no_middle:+.0f}")
if no_middle < baseline:
    print(">>> PARADOX CONFIRMED: removing A_B IMPROVED traffic!")
else:
    print(">>> No paradox with these parameters (may need heavier demand)")