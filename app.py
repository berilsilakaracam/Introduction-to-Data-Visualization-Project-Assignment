import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
import math
import time
import csv
import io
from datetime import datetime
from collections import deque

st.set_page_config(page_title="NetViz", page_icon="🌐", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0d1117; }
[data-testid="stSidebar"] { background-color: #161b22; }
* { color: #e6edf3; }
.health-score {
    font-size: 3rem; font-weight: 700; text-align: center;
    font-family: monospace; padding: 10px;
}
.detail-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 12px; margin: 4px 0;
}
</style>
""", unsafe_allow_html=True)

# --- Session state ---
if "tick" not in st.session_state:
    st.session_state.tick = 0
    st.session_state.selected_device = None
    st.session_state.lat_history = [12 + math.sin(i*0.3)*4 + random.uniform(0,3) for i in range(60)]
    st.session_state.devices = {
        "10.0.0.1":  {"name": "Core-R1",      "type": "router",   "load": 0.45, "mac": "AA:BB:CC:DD:EE:01", "ports": [22, 80, 443], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
        "10.0.1.1":  {"name": "FW-01",         "type": "firewall", "load": 0.62, "mac": "AA:BB:CC:DD:EE:02", "ports": [22, 443, 8080], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
        "10.1.0.1":  {"name": "SW-Access-A",   "type": "switch",   "load": 0.28, "mac": "AA:BB:CC:DD:EE:03", "ports": [22], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
        "10.1.0.2":  {"name": "SW-Access-B",   "type": "switch",   "load": 0.81, "mac": "AA:BB:CC:DD:EE:04", "ports": [22], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
        "10.2.0.1":  {"name": "Web-SRV-01",    "type": "server",   "load": 0.35, "mac": "AA:BB:CC:DD:EE:05", "ports": [22, 80, 443], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
        "10.2.0.2":  {"name": "DB-SRV-01",     "type": "server",   "load": 0.74, "mac": "AA:BB:CC:DD:EE:06", "ports": [22, 3306, 5432], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
        "10.2.1.1":  {"name": "App-SRV-01",    "type": "server",   "load": 0.58, "mac": "AA:BB:CC:DD:EE:07", "ports": [22, 8080, 8443], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
        "10.2.1.2":  {"name": "App-SRV-02",    "type": "server",   "load": 0.91, "mac": "AA:BB:CC:DD:EE:08", "ports": [22, 8080], "lat_hist": deque([random.uniform(5,20) for _ in range(20)], maxlen=20)},
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

def network_health_score(devices, threshold):
    scores = []
    for d in devices.values():
        load = d["load"]
        if load < 0.3:   scores.append(100)
        elif load < 0.7: scores.append(60)
        else:            scores.append(20)
    return round(sum(scores) / len(scores)) if scores else 0

def health_color(score):
    if score >= 80: return "#3fb950"
    if score >= 50: return "#d29922"
    return "#f85149"

def export_csv(devices):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["IP", "Hostname", "Tür", "MAC", "Yük (%)", "Açık Portlar", "Son Güncelleme"])
    for ip, d in devices.items():
        writer.writerow([
            ip, d["name"], d["type"], d["mac"],
            f"{d['load']*100:.0f}",
            ", ".join(str(p) for p in d["ports"]),
            datetime.now().strftime("%H:%M:%S")
        ])
    return output.getvalue()

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🌐 NetViz")
    st.markdown("---")
    mode = st.radio("Görünüm", ["Topoloji", "Isı Haritası"])
    threshold = st.slider("Kritik eşik (%)", 50, 95, 80) / 100
    auto = st.toggle("Canlı yenileme", value=True)

    st.markdown("---")

    # Ağ Sağlık Skoru
    score = network_health_score(devices, threshold)
    color = health_color(score)
    st.markdown("**🏥 Ağ Sağlık Skoru**")
    st.markdown(f'<div class="health-score" style="color:{color}">{score}/100</div>', unsafe_allow_html=True)
    if score >= 80:
        st.success("Ağ sağlıklı ✅")
    elif score >= 50:
        st.warning("Dikkat gerektiriyor ⚠️")
    else:
        st.error("Kritik durum! 🔴")

    st.markdown("---")

    # CSV Export
    csv_data = export_csv(devices)
    st.download_button(
        label="📥 Raporu CSV İndir",
        data=csv_data,
        file_name=f"netviz_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("🟢 Normal  🟡 Uyarı  🔴 Kritik")

# --- Header ---
st.markdown("### 📊 Ağ Durumu")
c1,c2,c3,c4 = st.columns(4)
crit = sum(1 for d in devices.values() if d["load"] > threshold)
lats = st.session_state.lat_history
avg_lat = round(sum(lats[-10:])/10, 1)
c1.metric("Aktif Cihaz", len(devices))
c2.metric("Kritik Anomali", crit)
c3.metric("Ort. Gecikme", f"{avg_lat} ms")
c4.metric("Sağlık Skoru", f"{score}/100")

st.markdown("---")

# --- Topoloji ---
G = nx.Graph()
for ip, d in devices.items():
    G.add_node(ip, **{k: v for k, v in d.items() if k != "lat_hist"})
for a, b in links:
    G.add_edge(a, b)

pos = nx.spring_layout(G, seed=42, k=2)

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

node_x,node_y,node_color,node_size,node_text,node_hover,node_ids = [],[],[],[],[],[],[]
for ip in G.nodes():
    x,y = pos[ip]
    d = devices[ip]
    node_x.append(x); node_y.append(y)
    node_color.append(load_color(d["load"]))
    node_size.append(30 if d["type"] in ("router","firewall") else 20)
    node_text.append(d["name"])
    node_hover.append(
        f"<b>{d['name']}</b><br>"
        f"IP: {ip}<br>"
        f"Tür: {d['type']}<br>"
        f"Yük: {d['load']*100:.0f}%<br>"
        f"MAC: {d['mac']}<br>"
        f"Portlar: {', '.join(str(p) for p in d['ports'])}"
    )
    node_ids.append(ip)

traces.append(go.Scatter(
    x=node_x, y=node_y,
    mode="markers+text",
    marker=dict(size=node_size, color=node_color, line=dict(width=2, color="#30363d")),
    text=node_text, textposition="bottom center",
    textfont=dict(size=9, color="#e6edf3"),
    hovertext=node_hover, hoverinfo="text",
    customdata=node_ids,
))

fig = go.Figure(data=traces, layout=go.Layout(
    paper_bgcolor="#0d1117", plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3"),
    showlegend=False, hovermode="closest",
    margin=dict(b=20,l=5,r=5,t=20), height=420,
    xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
    yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
))

# --- Ana layout ---
col_topo, col_detail = st.columns([3, 1])

with col_topo:
    st.markdown("#### 🗺 Ağ Topolojisi")
    st.caption("💡 Cihaza tıklayarak detayları görün")
    clicked = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="topo_chart")

    # Tıklanan cihazı al
    if clicked and clicked.get("selection") and clicked["selection"].get("points"):
        point = clicked["selection"]["points"][0]
        idx = point.get("point_index")
        if idx is not None and idx < len(node_ids):
            st.session_state.selected_device = node_ids[idx]

with col_detail:
    st.markdown("#### 🔍 Cihaz Detayı")

    sel = st.session_state.selected_device
    if sel and sel in devices:
        d = devices[sel]
        load = d["load"]
        color = load_color(load)

        st.markdown(f"""
        <div class="detail-card">
            <b style="font-size:1.1rem">{d['name']}</b><br>
            <span style="color:#8b949e">IP:</span> {sel}<br>
            <span style="color:#8b949e">MAC:</span> {d['mac']}<br>
            <span style="color:#8b949e">Tür:</span> {d['type']}<br>
            <span style="color:#8b949e">Yük:</span> <span style="color:{color}">%{load*100:.0f}</span><br>
            <span style="color:#8b949e">Portlar:</span> {', '.join(str(p) for p in d['ports'])}
        </div>
        """, unsafe_allow_html=True)

        # Gecikme mini grafiği
        lat_data = list(d["lat_hist"])
        fig_mini = go.Figure()
        fig_mini.add_trace(go.Scatter(
            y=lat_data, mode="lines",
            line=dict(color=color, width=1.5),
            fill="tozeroy", fillcolor=color+"22"
        ))
        fig_mini.update_layout(
            paper_bgcolor="#161b22", plot_bgcolor="#161b22",
            height=100, margin=dict(l=5,r=5,t=5,b=5),
            xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
            yaxis=dict(showgrid=False,zeroline=False,showticklabels=False),
            font=dict(color="#e6edf3")
        )
        st.caption("Gecikme geçmişi (ms)")
        st.plotly_chart(fig_mini, use_container_width=True, key="mini_chart")

    else:
        st.info("Topoloji haritasındaki bir cihaza tıklayın 👆")

    st.markdown("#### 🚨 Anomaliler")
    for ip, d in devices.items():
        if d["load"] > threshold:
            st.error(f"🔴 {d['name']}: %{d['load']*100:.0f}")
        elif d["load"] > 0.5:
            st.warning(f"🟡 {d['name']}: %{d['load']*100:.0f}")

# --- Gecikme Tahmini ---
st.markdown("---")
st.markdown("#### 📈 Gecikme Tahmini (önümüzdeki 10 dakika)")
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
st.plotly_chart(fig2, use_container_width=True, key="lat_chart")

# --- Canlı yenileme ---
if auto:
    for ip in devices:
        devices[ip]["load"] = max(0.05, min(0.98, devices[ip]["load"] + random.uniform(-0.03, 0.03)))
        devices[ip]["lat_hist"].append(round(random.uniform(5, 30 + devices[ip]["load"]*50), 1))
    devices["10.2.1.2"]["load"] = max(0.85, devices["10.2.1.2"]["load"])
    new_lat = 12 + sum(d["load"] for d in devices.values())/len(devices)*40 + random.uniform(-2,3)
    st.session_state.lat_history.append(round(new_lat,2))
    st.session_state.tick += 1
    time.sleep(2)
    st.rerun()
