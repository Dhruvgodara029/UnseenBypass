import os
import subprocess

def build_network(out_prefix="braess", fast_speed=13.89, slow_speed=13.89, mid_len=50):
    nodes = f"""<nodes>
    <node id="start" x="0"    y="0"/>
    <node id="A"     x="500"  y="200"/>
    <node id="B"     x="500"  y="-200"/>
    <node id="end"   x="1000" y="0"/>
</nodes>"""

    edges = f"""<edges>
    <edge id="start_A" from="start" to="A"   numLanes="1" speed="{fast_speed}" length="100"/>
    <edge id="A_end"   from="A"     to="end" numLanes="1" speed="{slow_speed}" length="800"/>
    <edge id="start_B" from="start" to="B"   numLanes="1" speed="{slow_speed}" length="800"/>
    <edge id="B_end"   from="B"     to="end" numLanes="1" speed="{fast_speed}" length="100"/>
    <edge id="A_B"     from="A"     to="B"   numLanes="1" speed="{fast_speed}" length="{mid_len}"/>
</edges>"""

    with open(f"{out_prefix}.nod.xml", "w") as f:
        f.write(nodes)
    with open(f"{out_prefix}.edg.xml", "w") as f:
        f.write(edges)

    subprocess.run([
        "netconvert",
        "--node-files", f"{out_prefix}.nod.xml",
        "--edge-files", f"{out_prefix}.edg.xml",
        "--output-file", f"{out_prefix}.net.xml"
    ], check=True)
    print(f"Built {out_prefix}.net.xml")

if __name__ == "__main__":
    build_network()