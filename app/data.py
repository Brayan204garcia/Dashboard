from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def load_df_panel():
    data_path = Path(__file__).resolve().parents[1] / "df_panel_limpio.csv"
    df = pd.read_csv(data_path, parse_dates=["fecha"])
    numeric_columns = ["channel_inv", "cust_sales", "sell_in"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


@st.cache_data(show_spinner=False)
def load_df_mensual():
    data_path = Path(__file__).resolve().parents[1] / "df_mensual_limpio.csv"
    df = pd.read_csv(data_path, parse_dates=["fecha_mes"])
    numeric_columns = ["sell_in", "cust_sales", "channel_inv_prom", "channel_inv_cierre", "channel_inv_max"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


executive_kpis = [
    ("Ventas total", "9.06M", "Ventas acumuladas", "-4.1%", "red", [72, 67, 63, 58, 54, 51, 47, 45, 42, 39, 37, 35, 34, 32, 31, 30, 32, 35, 39, 43, 47, 51, 55]),
    ("Sell-in", "8.98M", "Ingreso comercial", "-2.1%", "red", [64, 62, 60, 58, 57, 55, 53, 51, 49, 46, 44, 42, 40, 38, 36, 35, 34, 33, 32, 31, 30, 29, 28]),
    ("Inv total", "XXXM", "Inventario valorizado", "+12%", "green", [22, 24, 27, 30, 33, 35, 38, 41, 43, 46, 49, 52, 54, 57, 60, 62, 64, 67, 69, 71, 74, 77, 80]),
    ("Clientes", "91", "Clientes activos", "-8%", "yellow", [46, 48, 51, 54, 56, 59, 62, 65, 67, 70, 73, 76, 78, 79, 81, 83, 85, 86, 88, 89, 90, 91, 91]),
]

months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
sales_evolution = {
    "2023": [940, 1010, 980, 1090, 1160, 1210, 1250, 1310, 1280, 1370, 1450, 1520],
    "2024": [1120, 1180, 1240, 1300, 1360, 1420, 1510, 1580, 1620, 1710, 1780, 1860],
    "2025": [1480, 1560, 1640, 1710, 1820, 1950, 2030, 2180, 2260, 2380, 2510, 2660],
}

rfm_customers = pd.DataFrame(
    [
        ["Alkosto", "Campeones", 82, 78, 78, "green", "$3.4M", 34, "6 dias"],
        ["Falabella", "Campeones", 72, 70, 64, "green", "$2.8M", 29, "9 dias"],
        ["Exito", "Potencial", 58, 61, 58, "sky", "$2.1M", 21, "14 dias"],
        ["Claro Retail", "Fieles", 66, 48, 50, "green", "$1.5M", 24, "18 dias"],
        ["Movistar", "En riesgo", 39, 42, 70, "yellow", "$1.7M", 13, "38 dias"],
        ["Canal Empresarial", "En riesgo", 31, 55, 54, "yellow", "$980K", 11, "45 dias"],
        ["Distribuidor Norte", "Perdidos", 19, 25, 66, "red", "$920K", 6, "72 dias"],
        ["Retail Costa", "Dormidos", 25, 35, 44, "red", "$610K", 8, "64 dias"],
        ["Online B2B", "Nuevos", 48, 31, 38, "sky", "$420K", 9, "12 dias"],
    ],
    columns=["Cliente", "Segmento", "Frecuencia", "Monto", "Recencia", "Tono", "Ventas", "Pedidos", "Ultima compra"],
)

quarterly = {
    "Alkosto": {"segment": "Campeones", "cliente": [720, 840, 930, 1020], "promedio": [610, 690, 760, 820]},
    "Falabella": {"segment": "Campeones", "cliente": [640, 710, 760, 840], "promedio": [610, 690, 760, 820]},
    "Exito": {"segment": "Potencial", "cliente": [470, 520, 590, 610], "promedio": [420, 455, 500, 545]},
    "Movistar": {"segment": "En riesgo", "cliente": [540, 510, 460, 390], "promedio": [500, 480, 450, 420]},
    "Distribuidor Norte": {"segment": "Perdidos", "cliente": [360, 310, 260, 210], "promedio": [310, 285, 250, 230]},
}

product_families = pd.DataFrame(
    {
        "Familia": ["Galaxy S", "Galaxy A", "Tablets", "Wearables", "Accesorios"],
        "Ventas": [6.8, 4.9, 2.7, 2.1, 1.2],
        "Share": [36, 26, 14, 11, 6],
    }
)

inventory = pd.DataFrame(
    [
        ["Galaxy S25 Ultra 256GB", "2.1 sem", 420, "Stockout"],
        ["Galaxy A56 128GB", "4.6 sem", 1940, "Saludable"],
        ["Tab S10 FE", "8.8 sem", 860, "Sobrestock"],
        ["Galaxy Watch 7", "3.3 sem", 770, "Saludable"],
        ["Buds3 Pro", "10.4 sem", 2600, "Sobrestock"],
    ],
    columns=["Producto", "Cobertura", "Unidades", "Estado"],
)
