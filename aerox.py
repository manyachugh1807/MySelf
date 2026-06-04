import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import datetime
import time

# ==========================================
# 1. PAGE CONFIG & PREMIUM DARK THEME INJECTION
# ==========================================
st.set_page_config(
    page_title="AEROX // Hyperlocal AQI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cyberpunk / Glassmorphism CSS injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&family=Orbitron:wght@500;800&display=swap');
    
    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #111827 0%, #030712 100%);
        color: #F3F4F6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Glassmorphism Card Wrapper */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
    }
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
        transform: translateY(-4px);
    }
    
    /* Glowing AQI Badges */
    .aqi-glow {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        text-shadow: 0 0 20px currentColor;
    }
    
    /* Micro-copy and Labels */
    .hero-title {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(135deg, #FFFFFF 0%, #9CA3AF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.05em;
    }
    .accent-text {
        color: #6366F1;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-size: 0.75rem;
        font-weight: 700;
    }
</style>
""", unsafe_gradient_hide_to_save_space=True, unsafe_allow_html=True)

# ==========================================
# 2. MOCK DATA GENERATION ENGINE
# ==========================================
@st.cache_data(ttl=60)
def generate_mock_data():
    # Setup coordinates around a city center (e.g., Tech Hub Hubtown)
    base_lat, base_lon = 40.7128, -74.0060
    zones = ['Downtown Core', 'Innovation District', 'Green Belt Park', 'Industrial Bay', 'Residential South']
    
    data = []
    for i, zone in enumerate(zones):
        np.random.seed(i + int(datetime.datetime.now().minute))
        aqi = int(np.random.choice([32, 58, 142, 185, 45], p=[0.2, 0.3, 0.2, 0.1, 0.2]) + np.random.randint(-10, 10))
        aqi = max(10, min(500, aqi)) # bounds
        
        data.append({
            'Zone': zone,
            'Lat': base_lat + np.random.uniform(-0.04, 0.04),
            'Lon': base_lon + np.random.uniform(-0.04, 0.04),
            'AQI': aqi,
            'PM25': round(aqi * 0.35 + np.random.uniform(0, 5), 1),
            'PM10': round(aqi * 0.65 + np.random.uniform(0, 10), 1),
            'NO2': round(np.random.uniform(10, 45), 1),
            'Temp': round(np.random.uniform(18, 24), 1),
            'Humidity': np.random.randint(45, 70)
        })
    return pd.DataFrame(data)

df_live = generate_mock_data()

# Helper for Dynamic Color Coding
def get_aqi_status(aqi):
    if aqi <= 50: return "Good", "#10B981", "rgba(16, 185, 129, 0.15)", "Clear atmospheric matrix. No actions required."
    elif aqi <= 100: return "Moderate", "#F59E0B", "rgba(245, 158, 11, 0.15)", "Acceptable air quality. Sensitive individuals should monitor symptoms."
    elif aqi <= 150: return "Unhealthy for Sensitive Groups", "#F97316", "rgba(249, 115, 22, 0.15)", "Micro-particles elevated. Wear filter masks if respiratory issues exist."
    else: return "Hazardous", "#EF4444", "rgba(239, 68, 68, 0.15)", "Atmospheric danger zone. Minimize outdoor exposures; active HVAC scrubbing advised."

# ==========================================
# 3. SIDEBAR NAVIGATION CONTROLLER
# ==========================================
with st.sidebar:
    st.markdown("<div style='padding: 20px 0;'><span class='accent-text'>⚡ DEEP ATMOS MATRIX</span><h1 style='font-family:\"Orbitron\"; font-size:1.8rem; margin:0;'>AEROX</h1></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    navigation = st.radio(
        "NAVIGATION NODE",
        ["🌐 Operational Overview", "📊 Real-Time Metrics", "🗺️ Hyperlocal Heatmap", "🔮 Predictive Forecast", "🛡️ Bio-Defense Guide"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("<div class='glass-card' style='padding:15px; text-align:center;'><small style='color:#9CA3AF;'>Network Status</small><br><span style='color:#10B981; font-weight:bold;'>● LIVE QUANTUM FEED</span></div>", unsafe_allow_html=True)

# ==========================================
# PAGE 1: HOME / OPERATIONAL OVERVIEW
# ==========================================
if navigation == "🌐 Operational Overview":
    # Hero Title Section
    st.markdown("<p class='accent-text'>Next-Gen Air Intelligence Platform</p>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title' style='font-size: 3.5rem; margin-bottom:10px;'>Atmospheric Reality,<br>Decoded in Real-Time.</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9CA3AF; max-width:600px; margin-bottom:40px;'>Aerox leverages decentralized sensor arrays and neural-network filtering to present micro-climate atmospheric metrics with zero latency.</p>", unsafe_allow_html=True)
    
    # Grid of Top level Stats
    col1, col2, col3 = st.columns(3)
    
    mean_aqi = int(df_live['AQI'].mean())
    status, color, bg, check = get_aqi_status(mean_aqi)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <span class="accent-text">CITY-WIDE AGGREGATE AQI</span>
            <div class="aqi-glow" style="color: {color}; margin: 15px 0;">{mean_aqi}</div>
            <span style="background: {bg}; color: {color}; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size:0.85rem;">{status}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Mini plotly trend line
        x_trend = list(range(10))
        y_trend = [mean_aqi + np.random.randint(-15, 15) for _ in x_trend]
        fig_mini = go.Figure()
        fig_mini.add_trace(go.Scatter(x=x_trend, y=y_trend, mode='lines', line=dict(color='#6366F1', width=3), fill='tozeroy', fillcolor='rgba(99, 102, 241, 0.05)'))
        fig_mini.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=110, xaxis=dict(visible=False), yaxis=dict(visible=False), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        
        st.markdown(f"""
        <div class="glass-card" style="height: 100%;">
            <span class="accent-text">24H VELOCITY VECTOR</span>
            <div style="margin-top:15px;"></div>
        """, unsafe_allow_html=True)
        st.plotly_chart(fig_mini, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="glass-card" style="height: 100%;">
            <span class="accent-text">ACTIVE IOT NODES</span>
            <div style="font-family: 'Orbitron'; font-size: 2.5rem; font-weight:800; color:#FFF; margin:15px 0;">1,429 / 1,430</div>
            <p style="color:#9CA3AF; margin:0; font-size:0.85rem;">99.93% Network Operational Fidelity across 5 hyper-zones.</p>
        </div>
        """, unsafe_allow_html=True)

    # Sub-dashboard section
    st.markdown("<h3 style='font-family:\"Orbitron\"; font-weight:600; margin: 40px 0 20px 0;'>Critical Node Discrepancies</h3>", unsafe_allow_html=True)
    
    # Styled Table
    st.dataframe(
        df_live[['Zone', 'AQI', 'PM25', 'Temp', 'Humidity']].style.background_gradient(cmap='YlOrRd', subset=['AQI']),
        use_container_width=True
    )

# ==========================================
# PAGE 2: REAL-TIME METRICS
# ==========================================
elif navigation == "📊 Real-Time Metrics":
    st.markdown("<span class='accent-text'>Live Telematic Feeds</span>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family:\"Orbitron\"; font-weight:800;'>Quantum Pollutant Analytics</h2>", unsafe_allow_html=True)
    
    # Selector Zone
    selected_zone = st.selectbox("🎯 TARGET SENSOR METROPOLIS", df_live['Zone'].tolist())
    zone_data = df_live[df_live['Zone'] == selected_zone].iloc[0]
    
    status, color, bg, advice = get_aqi_status(zone_data['AQI'])
    
    # Metrics Hero Block
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 40px 20px;">
            <span class="accent-text">{selected_zone} AQI</span>
            <div class="aqi-glow" style="color: {color}; margin: 25px 0; font-size: 5rem;">{zone_data['AQI']}</div>
            <div style="background: {bg}; color: {color}; padding: 8px 20px; border-radius: 20px; font-weight: bold; display:inline-block; margin-bottom: 20px;">
                {status}
            </div>
            <p style="color: #9CA3AF; font-size:0.85rem; padding: 0 10px;">{advice}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        # Radial / Bar layout for molecular specs
        pollutants = ['PM2.5', 'PM10', 'NO2']
        values = [zone_data['PM25'], zone_data['PM10'], zone_data['NO2']]
        max_bounds = [150, 200, 100] # for normalizing visual presentation
        
        fig_poll = go.Figure()
        fig_poll.add_trace(go.Bar(
            y=pollutants,
            x=values,
            orientation='h',
            marker=dict(
                color=color,
                line=dict(color='rgba(255,255,255,0.1)', width=1)
            ),
            text=values,
            textposition='auto',
        ))
        fig_poll.update_layout(
            title=dict(text="Molecular Breakdown (µg/m³)", font=dict(color='#FFF', family='Orbitron')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', textfont=dict(color='#FFF')),
            yaxis=dict(textfont=dict(color='#FFF')),
            height=320,
            margin=dict(l=50, r=20, t=50, b=20)
        )
        
        st.markdown("<div class='glass-card' style='height: 100%;'>", unsafe_allow_html=True)
        st.plotly_chart(fig_poll, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 3: HYPERLOCAL HEATMAP
# ==========================================
elif navigation == "🗺️ Hyperlocal Heatmap":
    st.markdown("<span class='accent-text'>Spatial Cartography Layer</span>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family:\"Orbitron\"; font-weight:800; margin-bottom:20px;'>Micro-Climate Atmospheric Topography</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    # Folium Map instantiation
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12, tiles="cartodbpositron")
    
    # Custom Dark Theme Tiles inject via Folium configuration mapping overrides
    # To keep it robust without extra keys, we use CartoDB DarkMatter
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12, tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', attr='&copy; OpenStreetMap contributors &copy; CARTO')
    
    # Compile list for heatmap layer array layout
    heat_data = [[row['Lat'], row['Lon'], row['AQI']] for index, row in df_live.iterrows()]
    HeatMap(heat_data, radius=35, blur=25, min_opacity=0.4).add_to(m)
    
    # Custom HTML Markers configuration inside canvas layout
    for index, row in df_live.iterrows():
        _, p_color, _, _ = get_aqi_status(row['AQI'])
        
        popup_html = f"""
        <div style="font-family:'Inter', sans-serif; background-color:#1e293b; color:#fff; padding:10px; border-radius:8px; border:1px solid rgba(255,255,255,0.1); width:150px;">
            <b style="color:#6366F1;">{row['Zone']}</b><br/>
            <hr style="border:0.5px solid rgba(255,255,255,0.1); margin:4px 0;"/>
            AQI Index: <span style="color:{p_color};font-weight:bold;">{row['AQI']}</span><br/>
            Temp: {row['Temp']}°C
        </div>
        """
        
        folium.CircleMarker(
            location=[row['Lat'], row['Lon']],
            radius=8,
            color=p_color,
            fill=True,
            fill_color=p_color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=200)
        ).add_to(m)
        
    st_folium(m, width="100%", height=550)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE 4: PREDICTIVE FORECAST
# ==========================================
elif navigation == "🔮 Predictive Forecast":
    st.markdown("<span class='accent-text'>Temporal Engine Vector</span>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family:\"Orbitron\"; font-weight:800;'>Neural Network 7-Day Atmospheric Horizon</h2>", unsafe_allow_html=True)
    
    # Generate predictive time series data arrays
    days = [datetime.date.today() + datetime.timedelta(days=i) for i in range(7)]
    base_aqi_forecast = [int(df_live['AQI'].mean() + np.sin(i)*15 + np.random.randint(-10, 10)) for i in range(7)]
    
    # Line chart layout using standard modern engineering theme vectors
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(
        x=[d.strftime('%A, %b %d') for d in days],
        y=base_aqi_forecast,
        mode='lines+markers',
        line=dict(color='#10B981', width=4, shape='spline'),
        marker=dict(size=10, color='#6366F1', borderwidth=2, line=dict(color='#FFF', width=1)),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.03)'
    ))
    
    fig_fc.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', titlefont=dict(color='#FFF'), tickfont=dict(color='#9CA3AF')),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Projected Baseline AQI Value", titlefont=dict(color='#FFF'), tickfont=dict(color='#9CA3AF')),
        height=400,
        margin=dict(l=40, r=20, t=20, b=40)
    )
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig_fc, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Forecast Cards grid
    st.markdown("<h4 style='font-family:\"Orbitron\"; margin: 30px 0 15px 0;'>Microclimatic Timeline Insights</h4>", unsafe_allow_html=True)
    cols = st.columns(7)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="padding:15px; text-align:center; margin-bottom:0;">
                <small style="color:#9CA3AF;">{days[i].strftime('%a')}</small>
                <div style="font-size:1.4rem; font-weight:700; margin:8px 0; color:#FFF;">{base_aqi_forecast[i]}</div>
                <div style="width:8px; height:8px; background:#10B981; border-radius:50%; display:inline-block;"></div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# PAGE 5: BIO-DEFENSE / HEALTH TIPS
# ==========================================
elif navigation == "🛡️ Bio-Defense Guide":
    st.markdown("<span class='accent-text'>Somatic Protection Layer</span>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-family:\"Orbitron\"; font-weight:800;'>Dynamic Physiological Defense Vector</h2>", unsafe_allow_html=True)
    
    # Trigger contextual advice mapping based on whole city average levels
    current_agg = df_live['AQI'].mean()
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%); border: 1px solid rgba(99, 102, 241, 0.2); border-radius:24px; padding:30px; margin-bottom:30px;">
        <h4 style="margin-top:0; font-family:'Orbitron'; color:#FFF;">SYSTEM ADVICE MATRIX IN EFFECT</h4>
        <p style="color:#D1D5DB; margin-bottom:0;">The aggregate atmospheric toxicity vector stands at <b>{int(current_agg)} AQI</b>. Cellular defense models suggest optimization protocols mapped out below.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-size:2rem; margin-bottom:10px;">🫁</div>
            <h4 style="font-family:'Orbitron'; margin:0 0 10px 0; color:#FFF;">Respiratory Protocol</h4>
            <p style="color:#9CA3AF; font-size:0.9rem; margin:0;">HEPA ventilation scrubbing systems should operate at optimal performance metrics. Mask implementations required for outdoor training runs.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-size:2rem; margin-bottom:10px;">🏃‍♂️</div>
            <h4 style="font-family:'Orbitron'; margin:0 0 10px 0; color:#FFF;">Kinetic Exertion Vector</h4>
            <p style="color:#9CA3AF; font-size:0.9rem; margin:0;">Switch systemic physical development programs to internal high-filtration zones. Avoid aerobic operations near critical zones.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="glass-card" style="height:100%;">
            <div style="font-size:2rem; margin-bottom:10px;">🏡</div>
            <h4 style="font-family:'Orbitron'; margin:0 0 10px 0; color:#FFF;">HVAC Structural Scrubbing</h4>
            <p style="color:#9CA3AF; font-size:0.9rem; margin:0;">Engage deep atmospheric inner recycling loop. Ionizers are recommended to settle particulate heavy elements.</p>
        </div>
        """, unsafe_allow_html=True)
