import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
import math
import time
from datetime import datetime
from collections import deque

st.set_page_config(page_title="NetViz", page_icon="🌐", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0d1117; }
[data-testid="stSidebar"] { background-color: #161b22; }
* { color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

# --- Veri ---
if "tick" not in st.session_state:
    st.session_state.tick = 0
    st.session_state.lat_history = [12 + math.sin(i*0.3)*4 + random.uniform(0,3) for i in range(60)]
    st.session_state.anomalies = []
    st.session_state.devices = {
        "10.0.0.1":  {"name": "Core-R1",      "type": "router",   "load": 0.45},
        "10.0.1.1":  {"name": "FW-01",         "type": "firewall", "load": 0.62},
        "10.1.0.1":  {"name": "SW-Access-A",   "type": "switch",   "load": 0.28},
        "10.1.0.2":  {"name": "SW-Access-B",   "type": "switch",   "load": 0.81},
        "10.2.0.1":  {"name": "Web-SRV-01",    "type": "server",   "load": 0.35},
        "10.2.0.2":  {"name": "DB-SRV-01",     "type": "server",   "load": 0.74},
        "10.2.1.1":  {"name": "App-SRV-01",    "type": "server",   "load": 0.58},
        "10.2.1.2":  {"name": "App-SRV-02",    "type": "server",   "load": 0.91},
    }
    st.session_state.links = [
        ("10.0.0.1","10.0.1.1"), ("10.0.1.1","10.1.0.1"),
        ("10.0.1.1","10.1.0.2"), ("10.1.0.1","10.2.0.1"),
        ("10.1.0.1","10.2.0.2"), ("10.1.0.2","10.2.1.1"),
        ("10.1.0.2","10.2.1.2"),
    ]

devices = st.session_state.devices
links   = st.session_state.links

def load_color(load):
    if load < 0.3: return "#3fb950"
    if load < 0.7: return "#d29922"
    return "#f85149"

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🌐 NetViz")
    st.markdown("---")
    mode = st.radio("Görünüm", ["Topoloji", "Isı Haritası"])
    threshold = st.slider("Kritik eşik (%)", 50, 95, 80) / 100
    auto = st.toggle("Canlı yenileme", value=True)
    st.markdown("---")
    st.markdown("🟢 Normal  🟡 Uyarı  🔴 Kritik")

# --- Metrikler ---
st.markdown("### 📊 Ağ Durumu")
c1,c2,c3,c4 = st.columns(4)
crit = sum(1 for d in devices.values() if d["load"] > threshold)
lats = st.session_state.lat_history
avg_lat = round(sum(lats[-10:])/10, 1)
c1.metric("Aktif Cihaz", len(devices))
c2.metric("Kritik Anomali", crit, delta=None)
c3.metric("Ort. Gecikme", f"{avg_lat} ms")
c4.metric("Uptime", "99.2%")

st.markdown("---")

# --- Topoloji ---
G = nx.Graph()
for ip, d in devices.items():
    G.add_node(ip, **d)
for a, b in links:
    G.add_edge(a, b)

pos = nx.spring_layout(G, seed=42, k=2)

edge_x, edge_y, edge_colors = [], [], []
traces = []
for a, b in G.edges():
    x0,y0 = pos[a]; x1,y1 = pos[b]
    avg = (devices[a]["load"] + devices[b]["load"]) / 2
    w = 2 if mode == "Topoloji" else max(2, avg*10)
    traces.append(go.Scatter(
        x=[x0,x1,None], y=[y0,y1,None],
        mode="lines",
        line=dict(width=w, color=load_color(avg)),
        hoverinfo="none", opacity=0.6
    ))

node_x,node_y,node_color,node_size,node_text,node_hover = [],[],[],[],[],[]
for ip in G.nodes():
    x,y = pos[ip]
    d = devices[ip]
    node_x.append(x); node_y.append(y)
    node_color.append(load_color(d["load"]))
    node_size.append(30 if d["type"] in ("router","firewall") else 20)
    node_text.append(d["name"])
    node_hover.append(f"{d['name']}<br>IP: {ip}<br>Yük: {d['load']*100:.0f}%<br>Tür: {d['type']}")

traces.append(go.Scatter(
    x=node_x, y=node_y,
    mode="markers+text",
    marker=dict(size=node_size, color=node_color, line=dict(width=2, color="#30363d")),
    text=node_text, textposition="bottom center",
    textfont=dict(size=9, color="#e6edf3"),
    hovertext=node_hover, hoverinfo="text"
))

fig = go.Figure(data=traces, layout=go.Layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3"),
    showlegend=False, hovermode="closest",
    margin=dict(b=20,l=5,r=5,t=20), height=450,
    xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
    yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
))

col1, col2 = st.columns([3,1])
with col1:
    st.markdown("#### 🗺 Ağ Topolojisi")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 🚨 Anomaliler")
    for ip, d in devices.items():
        if d["load"] > threshold:
            st.error(f"🔴 {d['name']}: %{d['load']*100:.0f}")
        elif d["load"] > 0.5:
            st.warning(f"🟡 {d['name']}: %{d['load']*100:.0f}")

    st.markdown("#### 📋 Cihazlar")
    for ip, d in devices.items():
        icon = "🔴" if d["load"]>threshold else ("🟡" if d["load"]>0.5 else "🟢")
        st.markdown(f"{icon} `{d['name']}` **{d['load']*100:.0f}%**")

# --- Gecikme Tahmini ---
st.markdown("---")
st.markdown("#### 📈 Gecikme Tahmini")
hist = st.session_state.lat_history[-40:]
slope = (hist[-1]-hist[0]) / len(hist)
forecast = [hist[-1] + slope*(i+1) + math.sin(i*0.4)*1.5 for i in range(20)]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(y=hist, mode="lines", line=dict(color="#3fb950",width=2), name="Geçmiş"))
fig2.add_trace(go.Scatter(
    x=list(range(len(hist)-1, len(hist)+len(forecast))),
    y=[hist[-1]]+forecast,
    mode="lines", line=dict(color="#378ADD",width=1.5,dash="dash"), name="Tahmin"
))
fig2.update_layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
    font=dict(color="#e6edf3"), height=200,
    margin=dict(l=40,r=10,t=10,b=30), hovermode="x unified",
    xaxis=dict(showgrid=True,gridcolor="#21262d"),
    yaxis=dict(showgrid=True,gridcolor="#21262d",title="ms"),
)
st.plotly_chart(fig2, use_container_width=True)

# --- Canlı yenileme ---
if auto:
    for ip in devices:
        devices[ip]["load"] = max(0.05, min(0.98, devices[ip]["load"] + random.uniform(-0.03, 0.03)))
    devices["10.2.1.2"]["load"] = max(0.85, devices["10.2.1.2"]["load"])
    new_lat = 12 + sum(d["load"] for d in devices.values())/len(devices)*40 + random.uniform(-2,3)
    st.session_state.lat_history.append(round(new_lat,2))
    st.session_state.tick += 1
    time.sleep(2)
    st.rerun()