import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import random
import math
import time
import csv
import io
import requests
from datetime import datetime
from collections import deque

@st.cache_data(ttl=300)
def get_gateway_location():
    """Router'ın dış IP'sini çekip konumunu bulur"""
    try:
        r = requests.get("http://ip-api.com/json/", timeout=5)
        return r.json()
    except:
        return None

@st.cache_data(ttl=60)
def get_ip_location(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        return r.json()
    except:
        return None

st.set_page_config(
    page_title="NetViz Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Orbitron:wght@400;700;900&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: #020409;
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(0, 255, 136, 0.03) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 150, 255, 0.04) 0%, transparent 50%),
        linear-gradient(180deg, #020409 0%, #040810 100%);
    font-family: 'JetBrains Mono', monospace;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #040810 0%, #060d1a 100%) !important;
    border-right: 1px solid rgba(0, 255, 136, 0.15);
}

[data-testid="stSidebar"] * { color: #a0b4c0 !important; font-family: 'JetBrains Mono', monospace !important; }

.netviz-header {
    display: flex; align-items: center; gap: 16px;
    padding: 20px 0 16px;
    border-bottom: 1px solid rgba(0, 255, 136, 0.2);
    margin-bottom: 20px;
}
.netviz-logo {
    font-family: 'Orbitron', monospace;
    font-size: 2rem; font-weight: 900; letter-spacing: 4px;
    background: linear-gradient(135deg, #00ff88, #00ccff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-shadow: none;
}
.netviz-sub {
    font-size: 0.7rem; letter-spacing: 3px; color: #3a5a6a;
    font-family: 'JetBrains Mono', monospace;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,255,136,0.08); border: 1px solid rgba(0,255,136,0.3);
    border-radius: 4px; padding: 4px 10px; font-size: 0.65rem;
    color: #00ff88; letter-spacing: 2px; font-family: 'JetBrains Mono';
}
.pulse-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00ff88;
    animation: pulse 1.5s infinite;
    display: inline-block;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.3; transform: scale(0.8); }
}

.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; padding: 16px 20px;
    position: relative; overflow: hidden;
    transition: all 0.3s ease;
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
}
.metric-card.green::before { background: linear-gradient(90deg, transparent, #00ff88, transparent); }
.metric-card.blue::before  { background: linear-gradient(90deg, transparent, #00ccff, transparent); }
.metric-card.amber::before { background: linear-gradient(90deg, transparent, #ffaa00, transparent); }
.metric-card.red::before   { background: linear-gradient(90deg, transparent, #ff4444, transparent); }
.metric-label { font-size: 0.6rem; letter-spacing: 2px; color: #3a5a6a; margin-bottom: 8px; }
.metric-value { font-family: 'Orbitron', monospace; font-size: 1.8rem; font-weight: 700; }
.metric-value.green { color: #00ff88; }
.metric-value.blue  { color: #00ccff; }
.metric-value.amber { color: #ffaa00; }
.metric-value.red   { color: #ff4444; }
.metric-delta { font-size: 0.65rem; color: #3a5a6a; margin-top: 4px; }

.section-title {
    font-family: 'Orbitron', monospace; font-size: 0.7rem;
    letter-spacing: 3px; color: #3a5a6a;
    border-left: 2px solid #00ff88; padding-left: 10px;
    margin-bottom: 12px;
}

.alert-card {
    border-radius: 6px; padding: 10px 14px; margin-bottom: 8px;
    border-left: 3px solid; font-size: 0.75rem;
    font-family: 'JetBrains Mono'; animation: slideIn 0.3s ease;
}
@keyframes slideIn {
    from { transform: translateX(-10px); opacity: 0; }
    to   { transform: translateX(0); opacity: 1; }
}
.alert-critical { background: rgba(255,68,68,0.08); border-color: #ff4444; color: #ff9999; }
.alert-warning  { background: rgba(255,170,0,0.08); border-color: #ffaa00; color: #ffd080; }
.alert-ok       { background: rgba(0,255,136,0.06); border-color: #00ff88; color: #80ffcc; }

.solution-card {
    background: linear-gradient(135deg, rgba(0,255,136,0.05), rgba(0,204,255,0.03));
    border: 1px solid rgba(0,255,136,0.2);
    border-radius: 8px; padding: 14px 16px; margin-bottom: 10px;
    font-size: 0.75rem; font-family: 'JetBrains Mono';
}
.solution-title { color: #00ff88; font-weight: 700; margin-bottom: 6px; font-size: 0.7rem; letter-spacing: 1px; }
.solution-body  { color: #6a9ab0; line-height: 1.6; }
.solution-cmd   {
    background: rgba(0,0,0,0.4); border: 1px solid rgba(0,255,136,0.15);
    border-radius: 4px; padding: 6px 10px; margin-top: 8px;
    color: #00ff88; font-size: 0.7rem; font-family: 'JetBrains Mono';
}

.health-ring {
    text-align: center; padding: 16px 0;
}
.health-num {
    font-family: 'Orbitron', monospace; font-size: 3rem; font-weight: 900;
    line-height: 1;
}
.health-label { font-size: 0.6rem; letter-spacing: 3px; color: #3a5a6a; margin-top: 4px; }

.device-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px; border-radius: 6px; margin-bottom: 4px;
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
    font-size: 0.7rem; font-family: 'JetBrains Mono'; color: #6a9ab0;
    cursor: pointer; transition: all 0.2s;
}
.device-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.device-name { flex: 1; color: #a0c0d0; }
.device-load { font-weight: 700; }

.stPlotlyChart { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────
if "tick" not in st.session_state:
    st.session_state.tick = 0
    st.session_state.lat_history = [12 + math.sin(i*0.3)*4 + random.uniform(0,3) for i in range(80)]
    st.session_state.devices = {
        "10.0.0.1":  {"name":"Core-R1",    "type":"router",   "load":0.45,"mac":"AA:BB:CC:DD:EE:01","ports":[22,80,443],"lat":deque([random.uniform(5,20) for _ in range(30)],maxlen=30)},
        "10.0.1.1":  {"name":"FW-01",      "type":"firewall", "load":0.62,"mac":"AA:BB:CC:DD:EE:02","ports":[443,8080],"lat":deque([random.uniform(5,20) for _ in range(30)],maxlen=30)},
        "10.1.0.1":  {"name":"SW-Access-A","type":"switch",   "load":0.28,"mac":"AA:BB:CC:DD:EE:03","ports":[22],"lat":deque([random.uniform(2,10) for _ in range(30)],maxlen=30)},
        "10.1.0.2":  {"name":"SW-Access-B","type":"switch",   "load":0.81,"mac":"AA:BB:CC:DD:EE:04","ports":[22],"lat":deque([random.uniform(5,20) for _ in range(30)],maxlen=30)},
        "10.2.0.1":  {"name":"Web-SRV-01", "type":"server",   "load":0.35,"mac":"AA:BB:CC:DD:EE:05","ports":[80,443],"lat":deque([random.uniform(5,15) for _ in range(30)],maxlen=30)},
        "10.2.0.2":  {"name":"DB-SRV-01",  "type":"server",   "load":0.74,"mac":"AA:BB:CC:DD:EE:06","ports":[3306],"lat":deque([random.uniform(8,25) for _ in range(30)],maxlen=30)},
        "10.2.1.1":  {"name":"App-SRV-01", "type":"server",   "load":0.58,"mac":"AA:BB:CC:DD:EE:07","ports":[8080],"lat":deque([random.uniform(5,20) for _ in range(30)],maxlen=30)},
        "10.2.1.2":  {"name":"App-SRV-02", "type":"server",   "load":0.93,"mac":"AA:BB:CC:DD:EE:08","ports":[8080],"lat":deque([random.uniform(20,60) for _ in range(30)],maxlen=30)},
    }
    st.session_state.links = [
        ("10.0.0.1","10.0.1.1"),("10.0.1.1","10.1.0.1"),
        ("10.0.1.1","10.1.0.2"),("10.1.0.1","10.2.0.1"),
        ("10.1.0.1","10.2.0.2"),("10.1.0.2","10.2.1.1"),
        ("10.1.0.2","10.2.1.2"),
    ]
    st.session_state.alerts = []
    st.session_state.selected = None

devices = st.session_state.devices
links   = st.session_state.links

def load_color(load):
    if load < 0.3: return "#00ff88"
    if load < 0.7: return "#ffaa00"
    return "#ff4444"

def load_glow(load):
    if load < 0.3: return "rgba(0,255,136,"
    if load < 0.7: return "rgba(255,170,0,"
    return "rgba(255,68,68,"

def health_score():
    scores = [100 if d["load"]<0.3 else (60 if d["load"]<0.7 else 15) for d in devices.values()]
    return round(sum(scores)/len(scores))

def get_solutions(devices, threshold):
    solutions = []
    for ip, d in devices.items():
        if d["load"] > threshold:
            if d["type"] == "server":
                solutions.append({
                    "device": d["name"], "ip": ip,
                    "problem": f"CPU/Bellek yükü kritik seviyede (%{d['load']*100:.0f})",
                    "solution": "Yük dengeleme (load balancing) veya yatay ölçeklendirme önerilir.",
                    "cmd": f"# Örnek: nginx upstream'e {d['name']} klonu ekle\nupstream backend {{ server {ip}; server {ip.rsplit('.',1)[0]}.{int(ip.rsplit('.',1)[1])+10}; }}"
                })
            elif d["type"] == "switch":
                solutions.append({
                    "device": d["name"], "ip": ip,
                    "problem": f"Switch port yükü aşırı (%{d['load']*100:.0f})",
                    "solution": "VLAN segmentasyonu ile trafik dağıtımı yapılmalıdır.",
                    "cmd": f"# Switch VLAN komutu\nswitch# vlan database\nswitch(vlan)# vlan 20 name OFFLOAD"
                })
    return solutions

def export_csv():
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["IP","Hostname","Tür","MAC","Yük (%)","Durum","Zaman"])
    for ip, d in devices.items():
        status = "KRİTİK" if d["load"]>0.8 else ("UYARI" if d["load"]>0.5 else "NORMAL")
        w.writerow([ip,d["name"],d["type"],d["mac"],f"{d['load']*100:.0f}",status,datetime.now().strftime("%H:%M:%S")])
    return out.getvalue()

# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px">
        <div style="font-family:'Orbitron';font-size:1.1rem;font-weight:900;
             background:linear-gradient(135deg,#00ff88,#00ccff);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;
             letter-spacing:3px">⚡ NETVIZ</div>
        <div style="font-size:0.55rem;letter-spacing:2px;color:#2a4a5a;margin-top:2px">
        NETWORK INTELLIGENCE PLATFORM</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    mode = st.radio("GÖRÜNÜM MODU", ["🌐 Topoloji", "🔥 Isı Haritası", "🔍 Yol İzleme"], label_visibility="visible")
    threshold = st.slider("KRİTİK EŞİK", 50, 95, 80) / 100
    auto = st.toggle("CANLI AKIŞ", value=True)

    st.markdown("---")

    score = health_score()
    color = "#00ff88" if score>=80 else ("#ffaa00" if score>=50 else "#ff4444")
    st.markdown(f"""
    <div class="health-ring">
        <div class="health-num" style="color:{color}">{score}</div>
        <div class="health-label">AĞ SAĞLIK SKORU / 100</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.download_button(
        "📥 RAPOR İNDİR (CSV)", data=export_csv(),
        file_name=f"netviz_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv", use_container_width=True
    )

# ── Header ───────────────────────────────────────────────────
st.markdown(f"""
<div class="netviz-header">
    <div>
        <div class="netviz-logo">NETVIZ PRO</div>
        <div class="netviz-sub">AUTONOMOUS NETWORK INTELLIGENCE</div>
    </div>
    <div class="live-badge"><span class="pulse-dot"></span> LIVE — TICK #{st.session_state.tick}</div>
    <div style="margin-left:auto;font-size:0.65rem;color:#2a4a5a;font-family:'JetBrains Mono'">
        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Metrikler ─────────────────────────────────────────────────
crit = sum(1 for d in devices.values() if d["load"] > threshold)
warn = sum(1 for d in devices.values() if 0.5 < d["load"] <= threshold)
lats = st.session_state.lat_history
avg_lat = round(sum(lats[-10:])/10, 1)
score = health_score()

st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card green">
        <div class="metric-label">AKTİF CİHAZ</div>
        <div class="metric-value green">{len(devices)}</div>
        <div class="metric-delta">↑ tümü çevrimiçi</div>
    </div>
    <div class="metric-card red">
        <div class="metric-label">KRİTİK ANOMALİ</div>
        <div class="metric-value red">{crit}</div>
        <div class="metric-delta">eşik: %{int(threshold*100)}</div>
    </div>
    <div class="metric-card blue">
        <div class="metric-label">ORT. GECİKME</div>
        <div class="metric-value blue">{avg_lat}<span style="font-size:1rem">ms</span></div>
        <div class="metric-delta">son 10 ölçüm</div>
    </div>
    <div class="metric-card {'green' if score>=80 else 'amber' if score>=50 else 'red'}">
        <div class="metric-label">SAĞLIK SKORU</div>
        <div class="metric-value {'green' if score>=80 else 'amber' if score>=50 else 'red'}">{score}<span style="font-size:1rem">/100</span></div>
        <div class="metric-delta">{'✓ sağlıklı' if score>=80 else '⚠ dikkat' if score>=50 else '✗ kritik'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Ana layout ───────────────────────────────────────────────
col_main, col_right = st.columns([2.2, 1])

with col_main:
    # Topoloji grafiği
    st.markdown('<div class="section-title">AĞ TOPOLOJİSİ</div>', unsafe_allow_html=True)

    G = nx.Graph()
    for ip, d in devices.items():
        G.add_node(ip, **{k:v for k,v in d.items() if k!="lat"})
    for a,b in links:
        G.add_edge(a,b)

    pos = nx.spring_layout(G, seed=42, k=2.5)
    traces = []

    # Bağlantılar — parlayan çizgiler
    for a,b in G.edges():
        x0,y0 = pos[a]; x1,y1 = pos[b]
        avg = (devices[a]["load"]+devices[b]["load"])/2
        color = load_color(avg)
        glow = load_glow(avg)
        width = 1.5 if "Topoloji" in mode else max(2, avg*12)

        # Glow efekti için kalın arka plan çizgisi
        traces.append(go.Scatter(
            x=[x0,x1,None], y=[y0,y1,None], mode="lines",
            line=dict(width=width*4, color=glow+"0.08)"),
            hoverinfo="none", showlegend=False
        ))
        traces.append(go.Scatter(
            x=[x0,x1,None], y=[y0,y1,None], mode="lines",
            line=dict(width=width, color=color),
            hoverinfo="none", showlegend=False, opacity=0.9
        ))

        # Bant genişliği etiketi
        mx,my = (x0+x1)/2,(y0+y1)/2
        traces.append(go.Scatter(
            x=[mx],y=[my], mode="text",
            text=[f"{round(avg*100)}%"],
            textfont=dict(size=9, color=color, family="JetBrains Mono"),
            hoverinfo="none", showlegend=False
        ))

    # Paket animasyon noktaları
    for a,b in links:
        x0,y0 = pos[a]; x1,y1 = pos[b]
        t = (st.session_state.tick * 0.07) % 1
        px = x0 + (x1-x0)*t; py = y0 + (y1-y0)*t
        avg = (devices[a]["load"]+devices[b]["load"])/2
        traces.append(go.Scatter(
            x=[px],y=[py], mode="markers",
            marker=dict(size=5, color=load_color(avg), opacity=0.9,
                       line=dict(width=1, color="white")),
            hoverinfo="none", showlegend=False
        ))

    # Düğümler
    nx_list, ny_list, nc, ns, nt, nh = [],[],[],[],[],[]
    for ip in G.nodes():
        x,y = pos[ip]; d = devices[ip]
        nx_list.append(x); ny_list.append(y)
        nc.append(load_color(d["load"]))
        ns.append(40 if d["type"] in ("router","firewall") else 30)
        nt.append(d["name"])
        lat_avg = round(sum(list(d["lat"])[-5:])/5,1) if d["lat"] else 0
        nh.append(
            f"<b style='color:white'>{d['name']}</b><br>"
            f"IP: {ip}<br>Tür: {d['type']}<br>"
            f"Yük: <b style='color:{load_color(d['load'])}'>{d['load']*100:.0f}%</b><br>"
            f"Gecikme: {lat_avg}ms<br>MAC: {d['mac']}"
        )

    traces.append(go.Scatter(
        x=nx_list, y=ny_list, mode="markers+text",
        marker=dict(
            size=ns, color=nc,
            line=dict(width=2, color="rgba(255,255,255,0.2)"),
            opacity=0.95,
        ),
        text=nt, textposition="bottom center",
        textfont=dict(size=9, color="#6a9ab0", family="JetBrains Mono"),
        hovertext=nh, hoverinfo="text",
        hoverlabel=dict(bgcolor="#040810", bordercolor="#00ff88",
                       font=dict(family="JetBrains Mono", size=11)),
        showlegend=False
    ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="rgba(2,4,9,0)",
        plot_bgcolor="rgba(2,4,9,0)",
        height=420,
        margin=dict(b=10,l=10,r=10,t=10),
        xaxis=dict(showgrid=False,zeroline=False,showticklabels=False,
                  showline=False),
        yaxis=dict(showgrid=False,zeroline=False,showticklabels=False,
                  showline=False),
        hovermode="closest",
    )
    st.plotly_chart(fig, use_container_width=True, key="topo")

    # Gecikme grafiği
    st.markdown('<div class="section-title">GECİKME TAHMİNİ — ÖNÜMÜZDEKİ 10 DAKİKA</div>', unsafe_allow_html=True)

    hist = st.session_state.lat_history[-50:]
    slope = (hist[-1]-hist[0])/max(len(hist)-1,1)
    forecast = [max(1, hist[-1]+slope*(i+1)+math.sin(i*0.5)*2+random.uniform(-1,2)) for i in range(25)]
    band_u = [v+random.uniform(2,8) for v in forecast]
    band_l = [max(0,v-random.uniform(2,8)) for v in forecast]
    fx = list(range(len(hist)-1, len(hist)+len(forecast)))

    fig2 = go.Figure()

    # Grid çizgileri
    for v in [10,20,30,40,50]:
        fig2.add_hline(y=v, line_dash="dot", line_color="rgba(255,255,255,0.05)", line_width=1)

    # Güven bandı
    fig2.add_trace(go.Scatter(
        x=fx+fx[::-1], y=band_u+band_l[::-1],
        fill="toself", fillcolor="rgba(0,204,255,0.06)",
        line=dict(color="rgba(0,0,0,0)"), hoverinfo="skip", showlegend=False
    ))

    # Geçmiş
    fig2.add_trace(go.Scatter(
        y=hist, mode="lines",
        line=dict(color="#00ff88", width=2, shape="spline", smoothing=0.8),
        fill="tozeroy", fillcolor="rgba(0,255,136,0.04)",
        name="Geçmiş Gecikme", showlegend=True,
        hovertemplate="%{y:.1f}ms<extra></extra>"
    ))

    # Tahmin
    fig2.add_trace(go.Scatter(
        x=fx, y=[hist[-1]]+forecast, mode="lines",
        line=dict(color="#00ccff", width=1.5, dash="dash", shape="spline", smoothing=0.8),
        name="Tahmin (LinReg)", showlegend=True,
        hovertemplate="%{y:.1f}ms<extra></extra>"
    ))

    # Şimdi çizgisi
    fig2.add_vline(x=len(hist)-1, line_color="rgba(255,255,255,0.2)",
                   line_width=1, line_dash="dot",
                   annotation_text="ŞİMDİ", annotation_font_color="#3a5a6a",
                   annotation_font_size=9)

    fig2.update_layout(
        paper_bgcolor="rgba(2,4,9,0)", plot_bgcolor="rgba(4,8,16,0.5)",
        height=180, font=dict(color="#6a9ab0", family="JetBrains Mono", size=10),
        margin=dict(l=40,r=10,t=10,b=30), hovermode="x unified",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                  showline=False),
        yaxis=dict(showgrid=False, zeroline=False, title="ms",
                  tickfont=dict(size=9), showline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                   font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#040810", bordercolor="#00ff88",
                       font=dict(family="JetBrains Mono"))
    )
    st.plotly_chart(fig2, use_container_width=True, key="lat")

with col_right:
    # Anomali log
    st.markdown('<div class="section-title">ANOMALİ GÜNLÜĞÜ</div>', unsafe_allow_html=True)

    for ip, d in sorted(devices.items(), key=lambda x: -x[1]["load"]):
        load = d["load"]
        if load > threshold:
            cls = "alert-critical"
            icon = "🔴"
        elif load > 0.5:
            cls = "alert-warning"
            icon = "🟡"
        else:
            continue
        st.markdown(f"""
        <div class="alert-card {cls}">
            {icon} <b>{d['name']}</b> — %{load*100:.0f}<br>
            <span style="opacity:0.6;font-size:0.65rem">{ip} · {datetime.now().strftime('%H:%M:%S')}</span>
        </div>
        """, unsafe_allow_html=True)

    # Çözüm önerileri
    st.markdown('<div class="section-title" style="margin-top:16px">ÇÖZÜM ÖNERİLERİ</div>', unsafe_allow_html=True)

    solutions = get_solutions(devices, threshold)
    if solutions:
        for sol in solutions[:3]:
            st.markdown(f"""
            <div class="solution-card">
                <div class="solution-title">⚡ {sol['device']} — ÇÖZÜM</div>
                <div class="solution-body">
                    <b>Sorun:</b> {sol['problem']}<br>
                    <b>Öneri:</b> {sol['solution']}
                </div>
                <div class="solution-cmd">{sol['cmd']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-card alert-ok">
            ✅ Tüm cihazlar normal aralıkta.<br>
            <span style="opacity:0.6;font-size:0.65rem">Aktif sorun tespit edilmedi.</span>
        </div>
        """, unsafe_allow_html=True)

    # Cihaz listesi
    st.markdown('<div class="section-title" style="margin-top:16px">CİHAZ LİSTESİ</div>', unsafe_allow_html=True)
    for ip, d in sorted(devices.items(), key=lambda x: -x[1]["load"]):
        color = load_color(d["load"])
        st.markdown(f"""
        <div class="device-row">
            <div class="device-dot" style="background:{color};
                 box-shadow:0 0 6px {color}"></div>
            <div class="device-name">{d['name']}</div>
            <div class="device-load" style="color:{color}">%{d['load']*100:.0f}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Gateway Konum + IP Sorgulama ─────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">🌍 AĞ KONUM ANALİZİ</div>', unsafe_allow_html=True)

col_gw, col_ip_search = st.columns([1, 1])

with col_gw:
    st.markdown('<div class="section-title" style="font-size:0.6rem">🔌 GATEWAY KONUMU (OTOMATİK)</div>', unsafe_allow_html=True)
    gw_data = get_gateway_location()
    if gw_data and gw_data.get("status") == "success":
        st.markdown(f"""
        <div class="solution-card">
            <div class="solution-title">📍 Bu Ağın Konumu</div>
            <div class="solution-body">
                🌍 <b>Ülke:</b> {gw_data.get('country','?')}<br>
                🏙 <b>Şehir:</b> {gw_data.get('city','?')}<br>
                🏢 <b>ISP:</b> {gw_data.get('isp','?')}<br>
                🌐 <b>Dış IP:</b> {gw_data.get('query','?')}<br>
                🕐 <b>Zaman Dilimi:</b> {gw_data.get('timezone','?')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        fig_gw = go.Figure(go.Scattergeo(
            lat=[gw_data["lat"]], lon=[gw_data["lon"]],
            mode="markers+text",
            marker=dict(size=18, color="#00ff88",
                       line=dict(width=3, color="white"),
                       symbol="circle"),
            text=[f"📡 {gw_data.get('city','')}"],
            textposition="top center",
            textfont=dict(color="#00ff88", size=13, family="JetBrains Mono"),
        ))
        fig_gw.update_layout(
            paper_bgcolor="rgba(2,4,9,0)",
            height=300, margin=dict(l=0,r=0,t=0,b=0),
            geo=dict(
                showland=True, landcolor="rgba(20,30,40,0.8)",
                showocean=True, oceancolor="rgba(4,8,16,0.9)",
                showcoastlines=True, coastlinecolor="rgba(0,255,136,0.3)",
                showframe=False, bgcolor="rgba(2,4,9,0)",
                projection_type="natural earth",
                center=dict(lat=gw_data["lat"], lon=gw_data["lon"]),
                projection_scale=4,
                showcountries=True, countrycolor="rgba(0,255,136,0.15)",
            )
        )
        st.plotly_chart(fig_gw, use_container_width=True, key="gw_map")
    else:
        st.info("Gateway konumu alınamadı.")

with col_ip_search:
    st.markdown('<div class="section-title" style="font-size:0.6rem">🔍 IP KONUM SORGULA</div>', unsafe_allow_html=True)
    ip_query = st.text_input("IP Adresi", placeholder="örn: 8.8.8.8 (Google DNS)")
    if st.button("🔍 Konumu Bul", use_container_width=True) and ip_query:
        data = get_ip_location(ip_query)
        if data and data.get("status") == "success":
            st.markdown(f"""
            <div class="solution-card">
                <div class="solution-title">📍 {ip_query}</div>
                <div class="solution-body">
                    🌍 <b>Ülke:</b> {data.get('country','?')}<br>
                    🏙 <b>Şehir:</b> {data.get('city','?')}<br>
                    🏢 <b>ISP:</b> {data.get('isp','?')}<br>
                    📡 <b>Koordinat:</b> {data.get('lat','?')}, {data.get('lon','?')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            fig_ip = go.Figure(go.Scattergeo(
                lat=[data["lat"]], lon=[data["lon"]],
                mode="markers+text",
                marker=dict(size=15, color="#ff4444",
                           line=dict(width=2, color="white")),
                text=[ip_query],
                textposition="top center",
                textfont=dict(color="#ff4444", size=11, family="JetBrains Mono"),
            ))
            fig_ip.update_layout(
                paper_bgcolor="rgba(2,4,9,0)",
                height=300, margin=dict(l=0,r=0,t=0,b=0),
                geo=dict(
                    showland=True, landcolor="rgba(20,30,40,0.8)",
                    showocean=True, oceancolor="rgba(4,8,16,0.9)",
                    showcoastlines=True, coastlinecolor="rgba(255,68,68,0.3)",
                    showframe=False, bgcolor="rgba(2,4,9,0)",
                    projection_type="natural earth",
                    center=dict(lat=data["lat"], lon=data["lon"]),
                    projection_scale=4,
                    showcountries=True, countrycolor="rgba(255,68,68,0.15)",
                )
            )
            st.plotly_chart(fig_ip, use_container_width=True, key="ip_map")
        else:
            st.error("Bu IP yerel ağ adresi veya bulunamadı. Gerçek bir IP girin (örn: 8.8.8.8)")

# ── Canlı güncelleme ─────────────────────────────────────────
if auto:
    for ip in devices:
        devices[ip]["load"] = max(0.05, min(0.98,
            devices[ip]["load"] + random.uniform(-0.025, 0.025)))
        lat_val = round(8 + devices[ip]["load"]*50 + random.uniform(-3,5), 1)
        devices[ip]["lat"].append(lat_val)
    devices["10.2.1.2"]["load"] = max(0.87, devices["10.2.1.2"]["load"])

    new_lat = 10 + sum(d["load"] for d in devices.values())/len(devices)*45 + random.uniform(-2,4)
    st.session_state.lat_history.append(round(new_lat,2))
    st.session_state.tick += 1
    time.sleep(1.5)
    st.rerun()
