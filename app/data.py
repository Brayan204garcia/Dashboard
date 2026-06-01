from pathlib import Path

import pandas as pd
import streamlit as st


DATA_ROOT = Path(__file__).resolve().parents[1]
MAX_PREDICTION_FILE_SIZE = 25 * 1024 * 1024


def _safe_data_path(filename):
    root = DATA_ROOT.resolve()
    path = (root / filename).resolve()
    if root not in path.parents and path != root:
        raise ValueError("Ruta de datos fuera del directorio permitido.")
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"No se encontro el archivo requerido: {filename}")
    if path.stat().st_size > MAX_PREDICTION_FILE_SIZE:
        raise ValueError(f"El archivo {filename} excede el tamano maximo permitido.")
    return path


def _read_prediction_csv(filename, required_columns, parse_dates=None):
    path = _safe_data_path(filename)
    try:
        df = pd.read_csv(path, parse_dates=parse_dates or [], encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, parse_dates=parse_dates or [], encoding="cp1252")
    missing = sorted(set(required_columns) - set(df.columns))
    if missing:
        raise ValueError(f"El archivo {filename} no tiene columnas requeridas: {', '.join(missing)}")
    return df


@st.cache_data(show_spinner=False)
def load_df_panel():
    data_path = DATA_ROOT / "df_panel_limpio.csv"
    df = pd.read_csv(data_path, parse_dates=["fecha"])
    numeric_columns = ["channel_inv", "cust_sales", "sell_in"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


@st.cache_data(show_spinner=False)
def load_df_mensual():
    data_path = DATA_ROOT / "df_mensual_limpio.csv"
    df = pd.read_csv(data_path, parse_dates=["fecha_mes"])
    numeric_columns = ["sell_in", "cust_sales", "channel_inv_prom", "channel_inv_cierre", "channel_inv_max"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


@st.cache_data(show_spinner=False)
def load_predicciones_agregado_mes():
    required_columns = [
        "fecha_mes",
        "horizonte_label",
        "n_pares",
        "demanda_total",
        "demanda_promedio",
        "demanda_mediana",
        "pct_pares_activos",
        "P_promedio",
        "stack_total",
    ]
    df = _read_prediction_csv("predicciones_agregado_mes.csv", required_columns, parse_dates=["fecha_mes"])
    numeric_columns = [column for column in required_columns if column not in {"fecha_mes", "horizonte_label"}]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    df["P_promedio"] = df["P_promedio"].clip(0, 1)
    df["pct_pares_activos"] = df["pct_pares_activos"].clip(0, 100)
    for column in ["n_pares", "demanda_total", "demanda_promedio", "demanda_mediana", "stack_total"]:
        df[column] = df[column].clip(lower=0)
    return df.sort_values("fecha_mes").reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_predicciones_largo():
    required_columns = [
        "Channel",
        "Material Description",
        "fecha_mes",
        "horizonte",
        "horizonte_label",
        "P_Y_positiva",
        "E_Y_condicional",
        "pred_hurdle",
        "pred_stack",
        "dem_promedio_hist",
        "dem_total_hist",
        "n_meses_hist",
        "longitud",
        "patron",
        "celda_eda",
    ]
    df = _read_prediction_csv("predicciones_largo.csv", required_columns, parse_dates=["fecha_mes"])
    text_columns = ["Channel", "Material Description", "horizonte_label", "longitud", "patron", "celda_eda"]
    numeric_columns = [
        "horizonte",
        "P_Y_positiva",
        "E_Y_condicional",
        "pred_hurdle",
        "pred_stack",
        "dem_promedio_hist",
        "dem_total_hist",
        "n_meses_hist",
    ]
    df[text_columns] = df[text_columns].fillna("").astype(str).apply(lambda col: col.str.strip())
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    df["P_Y_positiva"] = df["P_Y_positiva"].clip(0, 1)
    for column in ["E_Y_condicional", "pred_hurdle", "pred_stack"]:
        df[column] = df[column].clip(lower=0)
    return df.sort_values(["fecha_mes", "Channel", "Material Description"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_predicciones_ancho():
    stack_aliases = {
        "Stack_h+1 (Ago 2025)": "Baseline_h+1 (Ago 2025)",
        "Stack_h+2 (Sep 2025)": "Baseline_h+2 (Sep 2025)",
        "Stack_h+3 (Oct 2025)": "Baseline_h+3 (Oct 2025)",
    }
    required_columns = [
        "Channel",
        "Material Description",
        "Hurdle_h+1 (Ago 2025)",
        "Hurdle_h+2 (Sep 2025)",
        "Hurdle_h+3 (Oct 2025)",
        "P_h+1 (Ago 2025)",
        "P_h+2 (Sep 2025)",
        "P_h+3 (Oct 2025)",
        "Hurdle_total_3m",
        "P_promedio_3m",
        "longitud",
        "patron",
        "celda_eda",
        "dem_promedio_hist",
    ]
    df = _read_prediction_csv("predicciones_ancho.csv", required_columns)
    missing_stack_columns = []
    for stack_column, baseline_column in stack_aliases.items():
        if stack_column not in df.columns:
            if baseline_column in df.columns:
                df[stack_column] = df[baseline_column]
            else:
                missing_stack_columns.append(stack_column)
    if missing_stack_columns:
        raise ValueError(
            "El archivo predicciones_ancho.csv no tiene columnas de proyeccion requeridas: "
            + ", ".join(missing_stack_columns)
        )
    text_columns = ["Channel", "Material Description", "longitud", "patron", "celda_eda"]
    numeric_columns = [
        "Hurdle_h+1 (Ago 2025)",
        "Hurdle_h+2 (Sep 2025)",
        "Hurdle_h+3 (Oct 2025)",
        "P_h+1 (Ago 2025)",
        "P_h+2 (Sep 2025)",
        "P_h+3 (Oct 2025)",
        "Stack_h+1 (Ago 2025)",
        "Stack_h+2 (Sep 2025)",
        "Stack_h+3 (Oct 2025)",
        "Hurdle_total_3m",
        "P_promedio_3m",
        "dem_promedio_hist",
    ]
    df[text_columns] = df[text_columns].fillna("").astype(str).apply(lambda col: col.str.strip())
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    probability_columns = ["P_h+1 (Ago 2025)", "P_h+2 (Sep 2025)", "P_h+3 (Oct 2025)", "P_promedio_3m"]
    df[probability_columns] = df[probability_columns].clip(0, 1)
    value_columns = [column for column in numeric_columns if column not in probability_columns]
    df[value_columns] = df[value_columns].clip(lower=0)
    return df.sort_values("Hurdle_total_3m", ascending=False).reset_index(drop=True)


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
