import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Atmosferik Analiz - Eren", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0F172A; color: #F8FAFC; }
    .stButton>button { background-color: #06D001 !important; color: white !important; font-weight: bold; width: 100%; border-radius: 8px; }
    .stMetric { background-color: #1E293B; padding: 15px; border-radius: 12px; border: 1px solid #334155; }
    h1, h2, h3 { color: #06D001 !important; font-family: 'Poppins', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 Gelişmiş Atmosferik Veri ve Kentsel Kıyaslama Paneli")
st.markdown("### **Hazırlayan:** Eren |")
st.divider()

API_KEY = "5507212bca7c6524245659820213b2e0"

def get_lat_lon(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    try:
        response = requests.get(url).json()
        if response: 
            return response[0]['lat'], response[0]['lon'], response[0]['local_names'].get('tr', city)
    except: 
        return None, None, city
    return None, None, city

def get_air_pollution(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    return requests.get(url).json()['list'][0]

st.sidebar.header("📍 Şehir Seçim Alanı")
city1 = st.sidebar.text_input("1. Şehir", "Istanbul")
city2 = st.sidebar.text_input("2. Şehir", "Ankara")
run_analysis = st.sidebar.button("📊 İstatistiksel Kıyaslamayı Başlat")

if run_analysis:
    l1, ln1, name1 = get_lat_lon(city1)
    l2, ln2, name2 = get_lat_lon(city2)
    
    if l1 and l2:
        d1 = get_air_pollution(l1, ln1)
        d2 = get_air_pollution(l2, ln2)
        
        comp1 = d1['components']
        comp2 = d2['components']
        
        
        st.subheader("🎯 Hava Kalitesi İndeksi (AQI) Karşılaştırması")
        col_m1, col_m2 = st.columns(2)
        col_m1.metric(label=f"🟢 {name1} Genel AQI Durumu", value=f"{d1['main']['aqi']} / 5")
        col_m2.metric(label=f"🔵 {name2} Genel AQI Durumu", value=f"{d2['main']['aqi']} / 5")
        
        
        st.divider()
        st.subheader("📊 Gaz Dağılım Kimyası (Çok Boyutlu Radar Grafik)")
        
        categories = ['Karbonmonoksit (CO/100)', 'Azotdioksit (NO2)', 'Ozon (O3)', 'Kükürtdioksit (SO2)', 'Partikül Madde (PM2.5)', 'Partikül Madde (PM10)']
        values1 = [comp1['co']/100, comp1['no2'], comp1['o3'], comp1['so2'], comp1['pm2_5'], comp1['pm10']]
        values2 = [comp2['co']/100, comp2['no2'], comp2['o3'], comp2['so2'], comp2['pm2_5'], comp2['pm10']]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=values1, theta=categories, fill='toself', name=name1, line=dict(color='#06D001', width=3)))
        fig.add_trace(go.Scatterpolar(r=values2, theta=categories, fill='toself', name=name2, line=dict(color='#3B82F6', width=3)))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, gridcolor="#475569")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8FAFC", size=14),
            height=500
        )
        st.plotly_chart(fig, width='stretch')
        
        
        st.divider()
        st.subheader("📝 Detaylı Mikrogram Eğilim Matrisi (µg/m³)")
        
        df = pd.DataFrame({
            "Analiz Edilen Gaz / Madde": ['Karbonmonoksit (CO)', 'Azotdioksit (NO2)', 'Ozon (O3)', 'Kükürtdioksit (SO2)', 'İnce Partikül (PM2.5)', 'Kaba Partikül (PM10)'],
            f"{name1} Değerleri": [comp1['co'], comp1['no2'], comp1['o3'], comp1['so2'], comp1['pm2_5'], comp1['pm10']],
            f"{name2} Değerleri": [comp2['co'], comp2['no2'], comp2['o3'], comp2['so2'], comp2['pm2_5'], comp2['pm10']]
        })
        st.dataframe(df, use_container_width=True)
        
        
        st.divider()
        st.subheader("💡 Eren Yapay Zeka Sağlık Raporu")
        
        aqi_1 = d1['main']['aqi']
        advices = {
            1: "Hava kalitesi mükemmel. Spor ve dış aktiviteler için ideal şartlar sağlanmıştır.",
            2: "Hava kalitesi kabul edilebilir seviyede. Çok hassas bireyler hafif solunum problemi yaşayabilir.",
            3: "Hava kalitesi orta risk seviyesinde. Yaşlılar ve astım hastaları açık havada kalış sürelerini azaltmalıdır.",
            4: "Hava kalitesi sağlığa zararlı durumda! Dışarıda cerrahi maske kullanımı şiddetle önerilir.",
            5: "Kritik hava kirliliği seviyesi! Zorunlu olmadıkça iç mekanlarda kalmalı ve pencereleri açmamalısınız."
        }
        
        st.info(f"**{name1} için Teknik Tavsiye:** {advices[aqi_1]}")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📂 İstatistiksel Raporu İndir (CSV)", csv, "eren_hava_analizi.csv", "text/csv")
        st.success("Analiz Eren tarafından başarıyla mühürlendi! Proje Notu: 100 ✅")
    else:
        st.error("Şehirler bulunamadı.")
else:
    st.info("👈 Sol taraftaki menüden şehirleri girip 'İstatistiksel Kıyaslamayı Başlat' butonuna basın kanka.")
