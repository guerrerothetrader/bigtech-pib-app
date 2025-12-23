import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# CONFIGURACIÓN RESPONSIVE
st.set_page_config(
    layout="wide", 
    page_title="Big Tech vs PIB Mundial",
    initial_sidebar_state="expanded"
)

st.title("🗺️ Big Tech vs PIB Mundial")
st.markdown("**Compara la capitalización bursátil de las Big Tech con el PIB de 50 economías**")

# Lista de Big Five 
tickers = {
    'Apple': 'AAPL',
    'Microsoft': 'MSFT',
    'Amazon': 'AMZN',
    'Google (Alphabet)': 'GOOGL',
    'Nvidia': 'NVDA'
}

# Sidebar elegante 
with st.sidebar:
    st.header("📊 **Selección de Empresas**")
    seleccion = st.multiselect(
        "Big Tech:", 
        options=list(tickers.keys()), 
        default=list(tickers.keys()),
        format_func=lambda x: f"💼 {x}"
    )
    
    st.divider()
    st.caption("**Datos en tiempo real** vía Yahoo Finance")

# Dataset de PIB 50 países 
@st.cache_data
def cargar_pib_simplificado():
    data = {
        'Country Code': [
            'USA','CHN','JPN','DEU','IND','GBR','FRA','ITA','CAN','KOR','AUS','BRA','MEX','ESP','RUS',
            'NLD','TUR','SAU','IDN','ZAF','ARG','THA','POL','BEL','SWE','AUT','NOR','DNK','FIN','IRL',
            'SGP','CHE','ARE','PHL','COL','MYS','ROU','CHL','VNM','PER','CZE','GRC','HUN','BGD','KAZ',
            'UKR','QAT','NGA','IRN','MAR'
        ],
        'Country': [
            'United States','China','Japan','Germany','India','United Kingdom','France','Italy','Canada',
            'South Korea','Australia','Brazil','Mexico','Spain','Russia','Netherlands','Turkey','Saudi Arabia',
            'Indonesia','South Africa','Argentina','Thailand','Poland','Belgium','Sweden','Austria','Norway',
            'Denmark','Finland','Ireland','Singapore','Switzerland','UAE','Philippines','Colombia','Malaysia',
            'Romania','Chile','Vietnam','Peru','Czechia','Greece','Hungary','Bangladesh','Kazakhstan',
            'Ukraine','Qatar','Nigeria','Iran','Morocco'
        ],
        'GDP_2024': [
            28840000,18940000,4090000,4560000,3920000,3390000,3050000,2270000,2220000,1760000,
            1790000,2270000,2000000,1600000,2030000,1110000,1180000,1100000,1420000,420000,
            650000,520000,840000,630000,620000,540000,590000,410000,300000,560000,
            520000,938000,510000,450000,360000,430000,350000,344000,450000,260000,
            330000,240000,210000,460000,290000,240000,200000,347000,398000,347000
        ]
    }
    return pd.DataFrame(data)

def obtener_capitalizaciones(tickers_seleccionadas):  
    caps = {}
    for nombre in tickers_seleccionadas:
        ticker = tickers[nombre]
        try:
            stock = yf.Ticker(ticker)
            cap = stock.info.get('marketCap', 0)
            caps[nombre] = cap if cap else 0
        except:
            caps[nombre] = 0
    return caps

if seleccion:
    caps = obtener_capitalizaciones(seleccion)
    total_market_cap = sum(caps.values())
    
    # Header 
    col1, col2, col3 = st.columns([1, 1, 1])  
    with col1:
        st.metric("💰 **Market Cap Total**", f"${total_market_cap/1e12:.2f}T")
    with col2:
        st.metric("📈 **Empresas**", f"{len(seleccion)} / 50 países")  
    with col3:
        st.metric("⚡ **Actualizado**", "2024")

    
    # Tabla de empresas 
    st.subheader("💼 **Capitalización por Empresa**")
    cap_df = pd.DataFrame(list(caps.items()), columns=['Empresa', 'MarketCap (USD)'])
    cap_df['MarketCap (USD)'] = cap_df['MarketCap (USD)']/1e12
    cap_df = cap_df.round(2).sort_values('MarketCap (USD)', ascending=False)
    
    st.dataframe(
        cap_df,
        column_config={
            "Empresa": st.column_config.TextColumn("Empresa"),
            "MarketCap (USD)": st.column_config.NumberColumn(
                "Market Cap (Trillones USD)",
                format="$%.2fT"
            )
        },
        use_container_width=True,
        hide_index=True,
        height=220 if st.columns(1)[0].empty else None  # Responsive height
    )

    # Procesar datos PIB 
    pib_df = cargar_pib_simplificado()
    pib_df_copy = pib_df.copy()
    pib_df_copy['MarketCap_Total'] = total_market_cap / 1e6
    pib_df_copy['Diferencia'] = pib_df_copy['GDP_2024'] - pib_df_copy['MarketCap_Total']
    pib_df_copy['Color_Value'] = pib_df_copy['Diferencia'].apply(lambda x: -1 if x < 0 else 1)
    pib_df_copy['Estado'] = pib_df_copy['Diferencia'].apply(lambda x: '🔴 Empresas > PIB' if x < 0 else '🔵 PIB > Empresas')
    
    # TABLA COMPARATIVA 
    st.subheader("🌍 **Comparativa Completa**")
    
    pib_df_copy_display = pib_df_copy.sort_values('GDP_2024', ascending=False).copy()
    pib_df_copy_display['GDP_2024'] = pib_df_copy_display['GDP_2024']/1000
    pib_df_copy_display['MarketCap_Total'] = pib_df_copy_display['MarketCap_Total']/1000
    pib_df_display = pib_df_copy_display[['Country', 'GDP_2024', 'MarketCap_Total', 'Diferencia', 'Estado']]
    
    st.dataframe(
        pib_df_display,
        column_config={
            "Country": st.column_config.TextColumn("País", width="medium"),
            "GDP_2024": st.column_config.NumberColumn(
                "PIB 2024", 
                format="%.1fT USD",
                help="PIB en billones de USD"
            ),
            "MarketCap_Total": st.column_config.NumberColumn(
                "Big Tech", 
                format="%.2fT USD"
            ),
            "Diferencia": st.column_config.NumberColumn(
                "Diferencia",
                format="%,.0fM USD",
                help="PIB - Big Tech (millones USD)"
            ),
            "Estado": st.column_config.TextColumn(
                "Resultado",
                width="medium"
            )
        },
        use_container_width=True,
        hide_index=True,
        height=350 if st.columns(1)[0].empty else None  # Responsive height
    )

    # MAPA RESPONSIVE 
    custom_data = pib_df_copy[['MarketCap_Total', 'GDP_2024', 'Diferencia']].values / 1000
    
    fig = go.Figure(data=go.Choropleth(
        locations=pib_df_copy['Country Code'],
        z=pib_df_copy['Color_Value'],
        text=pib_df_copy['Country'],
        hovertemplate="""
        <b style='font-size:14px;'>%{text}</b><br>
        💰 Big Tech: $%{customdata[0]:.1f}T<br>
        🌍 PIB 2024: $%{customdata[1]:.1f}T<br>
        📊 Diferencia: <b>%{customdata[2]:+,d}M USD</b><br>
        <extra></extra>
        """,
        customdata=custom_data,
        colorscale='RdBu_r',
        zmid=0,
        zmin=-1,
        zmax=1
    ))

    map_height = 450 if st.columns(1)[0].empty else 650  # Móvil:450px, Desktop:650px
    
    fig.update_layout(
        title=f"🗺️ PIB vs {' + '.join(seleccion)} (${total_market_cap/1e12:.1f}T USD)",
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            center=dict(lat=20, lon=0),
            scope='world',
            bgcolor='rgba(36, 35, 40, 1)',
            lakecolor='rgba(100,150,255,0.4)',
            landcolor='rgba(118, 118, 119, 1)',
            coastlinecolor='rgba(120,140,180,0.8)',
            countrycolor='rgba(80,100,140,0.3)'
        ),
        height=map_height,
        margin={"r":0,"t":60,"l":0,"b":0},
        dragmode='zoom',
        paper_bgcolor='rgba(36, 35, 40, 1)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
        
    # KPIs finales
    paises_rojos = len(pib_df_copy[pib_df_copy['Diferencia'] < 0])
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🔴 **Empresas > PIB**", f"{paises_rojos}/50", delta=f"+{paises_rojos}")
    with col2:
        st.metric("🔵 **PIB > Empresas**", f"{50-paises_rojos}/50")


else:
    st.warning("👈 **Selecciona al menos una empresa** en el sidebar")
