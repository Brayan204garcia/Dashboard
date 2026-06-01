import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.config import COLORS
from app.data import load_df_mensual, load_predicciones_ancho


HORIZONS = {
    "Agosto 2025": {
        "label": "h+1 (Ago 2025)",
        "fecha_mes": "2025-08-01",
        "proyeccion": "Stack_h+1 (Ago 2025)",
        "compromiso": "Hurdle_h+1 (Ago 2025)",
        "probabilidad": "P_h+1 (Ago 2025)",
    },
    "Septiembre 2025": {
        "label": "h+2 (Sep 2025)",
        "fecha_mes": "2025-09-01",
        "proyeccion": "Stack_h+2 (Sep 2025)",
        "compromiso": "Hurdle_h+2 (Sep 2025)",
        "probabilidad": "P_h+2 (Sep 2025)",
    },
    "Octubre 2025": {
        "label": "h+3 (Oct 2025)",
        "fecha_mes": "2025-10-01",
        "proyeccion": "Stack_h+3 (Oct 2025)",
        "compromiso": "Hurdle_h+3 (Oct 2025)",
        "probabilidad": "P_h+3 (Oct 2025)",
    },
}


def _format_units(value):
    if pd.isna(value):
        return "0"
    return f"{float(value):,.0f}".replace(",", ".")


def _format_percent(value):
    if pd.isna(value):
        return "0%"
    return f"{float(value):.0%}"


def _shorten(value, limit=58):
    text = str(value)
    return text if len(text) <= limit else f"{text[:limit - 3]}..."


def _inject_prediction_styles():
    st.markdown(
        """
        <style>
        .prediction-filter-title {
            color: #111827;
            font-size: 1.05rem;
            font-weight: 850;
            margin: .25rem 0 .35rem;
        }
        .prediction-filter-help {
            color: #4b5563;
            font-size: .82rem;
            margin: 0 0 .55rem;
        }
        .prediction-kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .9rem;
            margin: .4rem 0 .25rem;
        }
        .prediction-kpi-card {
            min-height: 118px;
            padding: 1rem 1.05rem;
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, .26);
            background: #ffffff;
            box-shadow: 0 12px 28px rgba(15, 23, 42, .08);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: .7rem;
        }
        .prediction-kpi-label {
            color: #475569;
            font-size: .78rem;
            line-height: 1.15;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .prediction-kpi-value {
            color: #0f172a;
            font-size: 1.72rem;
            line-height: 1;
            font-weight: 950;
        }
        .prediction-kpi-meta {
            color: #64748b;
            font-size: .76rem;
            line-height: 1.25;
            font-weight: 700;
        }
        .answer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: .9rem;
            align-items: stretch;
            margin: .85rem 0 1.1rem;
        }
        .answer-card {
            min-height: 210px;
            height: 100%;
            padding: 1rem 1rem .95rem;
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, .26);
            background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
            box-shadow: 0 16px 34px rgba(15, 23, 42, .22);
            display: flex;
            flex-direction: column;
            gap: .65rem;
            overflow: hidden;
        }
        .answer-card-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .65rem;
            min-height: 26px;
        }
        .answer-question {
            color: #cbd5e1;
            font-size: .72rem;
            line-height: 1.15;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .answer-badge {
            color: #f8fafc;
            border: 1px solid rgba(255, 255, 255, .12);
            background: rgba(255, 255, 255, .08);
            border-radius: 999px;
            padding: .25rem .48rem;
            font-size: .68rem;
            line-height: 1;
            font-weight: 850;
            white-space: nowrap;
        }
        .answer-main {
            color: #f8fafc;
            font-size: 1.08rem;
            line-height: 1.15;
            font-weight: 950;
            overflow-wrap: anywhere;
            min-height: 2.5rem;
        }
        .answer-copy {
            color: #cbd5e1;
            font-size: .78rem;
            line-height: 1.25;
            min-height: 3rem;
        }
        .answer-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .4rem;
            margin-top: auto;
        }
        .answer-chip {
            color: #e5e7eb;
            background: rgba(148, 163, 184, .14);
            border: 1px solid rgba(148, 163, 184, .18);
            border-radius: 999px;
            padding: .28rem .48rem;
            font-size: .72rem;
            font-weight: 780;
            line-height: 1;
        }
        .answer-violet { --accent: #8b5cf6; }
        .answer-sky { --accent: #38bdf8; }
        .answer-green { --accent: #22c55e; }
        .answer-yellow { --accent: #eab308; }
        .answer-red { --accent: #f43f5e; }
        .answer-backup-panel {
            margin: .35rem 0 .7rem;
            padding: 1rem 1.1rem;
            border-radius: 10px;
            border: 1px solid rgba(14, 165, 233, .34);
            border-left: 5px solid #38bdf8;
            background: linear-gradient(135deg, rgba(15, 23, 42, .98), rgba(30, 41, 59, .94));
            box-shadow: 0 16px 36px rgba(15, 23, 42, .24);
        }
        .answer-backup-kicker {
            color: #7dd3fc;
            font-size: .74rem;
            line-height: 1.1;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .answer-backup-title {
            color: #f8fafc;
            font-size: 1.22rem;
            line-height: 1.15;
            font-weight: 950;
            margin-top: .35rem;
        }
        .answer-backup-copy {
            color: #cbd5e1;
            font-size: .86rem;
            line-height: 1.35;
            margin-top: .35rem;
            max-width: 920px;
        }
        div[data-testid="stTabs"] button[data-baseweb="tab"] p {
            font-size: .98rem;
            font-weight: 900;
        }
        .answer-detail-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .75rem;
            padding: .9rem 1rem;
            margin: 0 0 .85rem;
            border-radius: 10px;
            background: linear-gradient(135deg, #0f172a, #1f2937);
            border: 1px solid rgba(148, 163, 184, .22);
            box-shadow: 0 12px 28px rgba(15, 23, 42, .18);
        }
        .answer-detail-title {
            color: #f8fafc;
            font-size: 1.02rem;
            line-height: 1.2;
            font-weight: 950;
        }
        .answer-detail-copy {
            color: #cbd5e1;
            font-size: .78rem;
            line-height: 1.3;
            margin-top: .22rem;
        }
        .answer-detail-pill {
            color: #082f49;
            background: #bae6fd;
            border-radius: 999px;
            padding: .34rem .62rem;
            font-size: .72rem;
            line-height: 1;
            font-weight: 900;
            white-space: nowrap;
        }
        .answer-kpi-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: .75rem;
            margin: .2rem 0 .9rem;
        }
        .answer-kpi-card {
            min-height: 92px;
            padding: .85rem .9rem;
            border-radius: 10px;
            border: 1px solid rgba(148, 163, 184, .24);
            background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
            box-shadow: 0 12px 26px rgba(15, 23, 42, .16);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: .55rem;
        }
        .answer-kpi-label {
            color: #cbd5e1;
            font-size: .76rem;
            line-height: 1.16;
            font-weight: 850;
        }
        .answer-kpi-value {
            color: #f8fafc;
            font-size: 1.58rem;
            line-height: 1;
            font-weight: 950;
        }
        @media (max-width: 1200px) {
            .prediction-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .answer-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .answer-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 680px) {
            .prediction-kpi-grid { grid-template-columns: 1fr; }
            .answer-grid { grid-template-columns: 1fr; }
            .answer-kpi-grid { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _prepare_ancho(df):
    df = df.copy()
    text_columns = ["Channel", "Material Description", "longitud", "patron", "celda_eda"]
    numeric_columns = ["Hurdle_total_3m", "P_promedio_3m", "dem_promedio_hist"]
    for config in HORIZONS.values():
        numeric_columns.extend([config["proyeccion"], config["compromiso"], config["probabilidad"]])

    df[text_columns] = df[text_columns].fillna("").astype(str).apply(lambda column: column.str.strip())
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    probability_columns = ["P_promedio_3m"] + [config["probabilidad"] for config in HORIZONS.values()]
    df[probability_columns] = df[probability_columns].clip(0, 1)
    value_columns = ["Hurdle_total_3m", "dem_promedio_hist"]
    value_columns.extend([config["proyeccion"] for config in HORIZONS.values()])
    value_columns.extend([config["compromiso"] for config in HORIZONS.values()])
    df[value_columns] = df[value_columns].clip(lower=0)
    return df


def _validate_sources(agregado, ancho):
    errors = []
    for config in HORIZONS.values():
        row = agregado[agregado["horizonte_label"].eq(config["label"])]
        if row.empty:
            errors.append(f"Falta {config['label']} en predicciones_agregado_mes.csv")
            continue
        row = row.iloc[0]
        base_gap = abs(float(row["demanda_total"]) - float(ancho[config["compromiso"]].sum()))
        projection_gap = abs(float(row["stack_total"]) - float(ancho[config["proyeccion"]].sum()))
        if base_gap > 0.01:
            errors.append(f"Compromiso Base no cuadra para {config['label']}: diferencia {base_gap:,.2f}")
        if projection_gap > 0.01:
            errors.append(f"Proyeccion no cuadra para {config['label']}: diferencia {projection_gap:,.2f}")
    return errors


def _build_agregado_from_ancho(ancho):
    rows = []
    for config in HORIZONS.values():
        compromiso = ancho[config["compromiso"]]
        proyeccion = ancho[config["proyeccion"]]
        probabilidad = ancho[config["probabilidad"]]
        rows.append(
            {
                "fecha_mes": pd.Timestamp(config["fecha_mes"]),
                "horizonte_label": config["label"],
                "n_pares": len(ancho),
                "demanda_total": compromiso.sum(),
                "demanda_promedio": compromiso.mean(),
                "demanda_mediana": compromiso.median(),
                "pct_pares_activos": (compromiso.gt(0).mean() * 100) if len(ancho) else 0,
                "P_promedio": probabilidad.mean(),
                "stack_total": proyeccion.sum(),
            }
        )
    return pd.DataFrame(rows)


def _page_filters(ancho):
    channels = sorted(ancho["Channel"].dropna().unique().tolist())
    min_probability = 0.55

    st.markdown('<div class="prediction-filter-title">Filtros de Predicciones</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="prediction-filter-help">Ajusta el mes y los canales para revisar la proyeccion comercial.</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        with c1:
            horizon = st.selectbox("Horizonte", list(HORIZONS.keys()))
        with c2:
            selected_channels = st.multiselect("Canal", channels, default=[])

    filtered = ancho.copy()
    if selected_channels:
        filtered = filtered[filtered["Channel"].isin(selected_channels)].copy()
    return horizon, selected_channels, min_probability, filtered


def _metric_row(agregado_row):
    items = [
        (
            "Proyeccion",
            _format_units(agregado_row["stack_total"]),
            "Unidades esperadas para el mes seleccionado.",
        ),
        (
            "Compromiso Base",
            _format_units(agregado_row["demanda_total"]),
            "Escenario conservador para gestionar ventas.",
        ),
        (
            "Probabilidad de Pedido",
            _format_percent(agregado_row["P_promedio"]),
            "Confianza promedio de las oportunidades del mes.",
        ),
    ]
    cards = "".join(
        f"""
        <div class="prediction-kpi-card">
            <div class="prediction-kpi-label">{label}</div>
            <div class="prediction-kpi-value">{value}</div>
            <div class="prediction-kpi-meta">{meta}</div>
        </div>
        """
        for label, value, meta in items
    )
    st.html(f'<div class="prediction-kpi-grid">{cards}</div>')


def _total_sales_forecast_chart(mensual, agregado, filtered, selected_channels):
    st.subheader("Forecast de ventas totales")
    if mensual.empty or agregado.empty or filtered.empty:
        st.info("No hay datos suficientes para graficar el forecast de ventas totales.")
        return

    history_source = mensual.copy()
    if selected_channels:
        history_source = history_source[history_source["Channel"].isin(selected_channels)].copy()
    forecast = pd.DataFrame(
        {
            "fecha_mes": agregado["fecha_mes"],
            "Forecast": [
                filtered["Stack_h+1 (Ago 2025)"].sum(),
                filtered["Stack_h+2 (Sep 2025)"].sum(),
                filtered["Stack_h+3 (Oct 2025)"].sum(),
            ],
            "Compromiso Base": [
                filtered["Hurdle_h+1 (Ago 2025)"].sum(),
                filtered["Hurdle_h+2 (Sep 2025)"].sum(),
                filtered["Hurdle_h+3 (Oct 2025)"].sum(),
            ],
        }
    ).sort_values("fecha_mes")
    first_forecast_month = forecast["fecha_mes"].min()
    forecast_year = first_forecast_month.year
    history = history_source.groupby("fecha_mes", as_index=False)["cust_sales"].sum().sort_values("fecha_mes")
    history = history[
        (history["fecha_mes"].dt.year == forecast_year)
        & (history["fecha_mes"] < first_forecast_month)
        & (history["cust_sales"] > 0)
    ].copy()
    x_start = history["fecha_mes"].min() if not history.empty else forecast["fecha_mes"].min()
    x_end = forecast["fecha_mes"].max()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=history["fecha_mes"],
            y=history["cust_sales"],
            name="Historico real",
            mode="lines+markers",
            line=dict(color="#64748b", width=3),
            marker=dict(size=6),
            hovertemplate="<b>Historico real</b><br>%{x|%b %Y}: %{y:,.0f}<extra></extra>",
        )
    )
    if not history.empty:
        bridge = pd.DataFrame(
            {
                "fecha_mes": [history["fecha_mes"].iloc[-1], forecast["fecha_mes"].iloc[0]],
                "valor": [history["cust_sales"].iloc[-1], forecast["Forecast"].iloc[0]],
            }
        )
        fig.add_trace(
            go.Scatter(
                x=bridge["fecha_mes"],
                y=bridge["valor"],
                name="Conexion",
                mode="lines",
                line=dict(color="rgba(56, 189, 248, .45)", width=2, dash="dot"),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=forecast["fecha_mes"],
            y=forecast["Forecast"],
            name="Forecast",
            mode="lines+markers+text",
            line=dict(color=COLORS["violet"], width=4, dash="dash"),
            marker=dict(size=9, color=COLORS["violet"], line=dict(color="#ffffff", width=1)),
            text=forecast["Forecast"].apply(_format_units),
            textposition="top center",
            hovertemplate="<b>Forecast</b><br>%{x|%b %Y}: %{y:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["fecha_mes"],
            y=forecast["Compromiso Base"],
            name="Compromiso Base",
            mode="lines+markers",
            line=dict(color=COLORS["green"], width=3, dash="dot"),
            marker=dict(size=7, color=COLORS["green"]),
            hovertemplate="<b>Compromiso Base</b><br>%{x|%b %Y}: %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=420,
        margin=dict(l=28, r=32, t=26, b=52),
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#475569"),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color="#334155")),
        hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#f8fafc"),
    )
    fig.update_xaxes(
        showgrid=False,
        tickformat="%b<br>%Y",
        tickfont=dict(color="#475569", size=11),
        range=[x_start, x_end],
    )
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, .16)", tickformat=",.0f", tickfont=dict(color="#475569", size=11))
    scope = "canales seleccionados" if selected_channels else "todos los canales"
    st.caption(f"Historico mensual real de ventas al consumidor y forecast total para los proximos tres meses ({scope}).")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _enriched_pairs(filtered):
    df = filtered.copy()
    projection_columns = [config["proyeccion"] for config in HORIZONS.values()]
    commitment_columns = [config["compromiso"] for config in HORIZONS.values()]
    df["Proyeccion 3m"] = df[projection_columns].sum(axis=1)
    df["Compromiso Base 3m"] = df[commitment_columns].sum(axis=1)
    df["Historico 3m"] = df["dem_promedio_hist"] * 3
    df["Cambio Unidades"] = df["Proyeccion 3m"] - df["Historico 3m"]
    df["Crecimiento"] = df.apply(
        lambda row: row["Proyeccion 3m"] / row["Historico 3m"] if row["Historico 3m"] > 0 else pd.NA,
        axis=1,
    )
    return df


def _commercial_answers(filtered, config):
    pairs = _enriched_pairs(filtered)
    pairs["Proyeccion Horizonte"] = pairs[config["proyeccion"]]
    pairs["Compromiso Base Horizonte"] = pairs[config["compromiso"]]
    pairs["Historico Horizonte"] = pairs["dem_promedio_hist"]
    pairs["Cambio Unidades Horizonte"] = pairs["Proyeccion Horizonte"] - pairs["Historico Horizonte"]
    pairs["Probabilidad Horizonte"] = pairs[config["probabilidad"]]

    products = (
        pairs.groupby("Material Description", as_index=False)
        .agg(
            Proyeccion_3m=("Proyeccion 3m", "sum"),
            Compromiso_Base_3m=("Compromiso Base 3m", "sum"),
            Historico_3m=("Historico 3m", "sum"),
            Probabilidad_de_Pedido=("P_promedio_3m", "mean"),
            Canales=("Channel", "nunique"),
        )
    )
    products["Cambio_Unidades"] = products["Proyeccion_3m"] - products["Historico_3m"]
    products["Crecimiento"] = products.apply(
        lambda row: row["Proyeccion_3m"] / row["Historico_3m"] if row["Historico_3m"] > 0 else pd.NA,
        axis=1,
    )

    clients = (
        pairs.groupby("Channel", as_index=False)
        .agg(
            Proyeccion_3m=("Proyeccion 3m", "sum"),
            Compromiso_Base_3m=("Compromiso Base 3m", "sum"),
            Historico_3m=("Historico 3m", "sum"),
            Probabilidad_de_Pedido=("P_promedio_3m", "mean"),
            SKUs=("Material Description", "nunique"),
        )
    )
    clients["Cambio_Unidades"] = clients["Proyeccion_3m"] - clients["Historico_3m"]
    clients["Retencion"] = clients.apply(
        lambda row: row["Compromiso_Base_3m"] / row["Historico_3m"] if row["Historico_3m"] > 0 else pd.NA,
        axis=1,
    )

    min_client_history = 100
    disappearance = clients[clients["Historico_3m"] >= min_client_history].sort_values(
        ["Retencion", "Probabilidad_de_Pedido", "Compromiso_Base_3m"],
        ascending=[True, True, True],
    )
    reductions = clients[clients["Historico_3m"] >= min_client_history].sort_values("Cambio_Unidades")
    dispatch = pairs[
        (pairs["Historico Horizonte"] >= 50)
        & (pairs["Proyeccion Horizonte"] > pairs["Historico Horizonte"] * 1.5)
        & (pairs["Probabilidad Horizonte"] >= 0.70)
    ].sort_values(["Proyeccion Horizonte", "Cambio Unidades Horizonte"], ascending=False)

    return {
        "rotation": products.sort_values("Proyeccion_3m", ascending=False),
        "disappearance": disappearance,
        "growth": products[products["Historico_3m"] > 0].sort_values(["Cambio_Unidades", "Probabilidad_de_Pedido"], ascending=False),
        "reductions": reductions,
        "dispatch": dispatch,
    }


def _show_answer_table(df, columns, probability_column=None, limit=12, display_names=None):
    df = df.copy()
    default_display_names = {
        "Material Description": "SKU",
        "Channel": "Cliente",
        "Proyeccion_3m": "Proyeccion 3m",
        "Compromiso_Base_3m": "Compromiso base",
        "Historico_3m": "Historico 3m",
        "Proyeccion_Horizonte": "Proyeccion horizonte",
        "Compromiso_Base_Horizonte": "Compromiso base horizonte",
        "Historico_Horizonte": "Historico promedio",
        "Cambio_Unidades_Horizonte": "Cambio esperado",
        "Probabilidad_Horizonte": "Prob. pedido",
        "Cambio_Unidades": "Cambio esperado",
        "Probabilidad_de_Pedido": "Prob. pedido",
        "Retencion": "Retencion",
        "Crecimiento": "Crecimiento",
        "Canales": "Canales",
        "SKUs": "SKUs",
    }
    display_names = {**default_display_names, **(display_names or {})}
    visible_columns = [display_names.get(column, column) for column in columns]
    df = df.rename(columns=display_names)
    probability_column = display_names.get(probability_column, probability_column)
    text_columns = {"Channel", "Material Description", "Cliente", "Canal", "SKU", "Canales", "SKUs"}
    config = {
        column: st.column_config.NumberColumn(format="%.0f")
        for column in visible_columns
        if column not in text_columns
    }
    if probability_column:
        df[probability_column] = df[probability_column] * 100
        config[probability_column] = st.column_config.ProgressColumn(format="%.0f%%", min_value=0, max_value=100)
    if "Crecimiento" in visible_columns:
        config["Crecimiento"] = st.column_config.NumberColumn(format="%.1fx")
    if "Retencion" in visible_columns:
        config["Retencion"] = st.column_config.NumberColumn(format="%.1fx")
    visible = df[visible_columns].head(limit)
    table_height = max(220, min(520, 84 + 35 * len(visible)))
    st.dataframe(visible, hide_index=True, width="stretch", height=table_height, column_config=config)


def _answer_kpi_cards(answers):
    items = [
        ("Despachar mas", len(answers["dispatch"])),
        ("Clientes en riesgo", len(answers["disappearance"])),
        ("Productos que crecen", len(answers["growth"])),
        ("Mayor rotacion", len(answers["rotation"])),
        ("Clientes que reducen", len(answers["reductions"])),
    ]
    cards = "".join(
        f"""
        <div class="answer-kpi-card">
            <div class="answer-kpi-label">{label}</div>
            <div class="answer-kpi-value">{_format_units(value)}</div>
        </div>
        """
        for label, value in items
    )
    st.html(f'<div class="answer-kpi-grid">{cards}</div>')


def _commercial_answers_section(filtered, config, horizon):
    answers = _commercial_answers(filtered, config)

    st.subheader("5.5 Modelado Predictivo de Indicadores Clave del Negocio")
    _answer_kpi_cards(answers)
    tabs = st.tabs(
        [
            "Despachar mas",
            "Clientes en riesgo",
            "Productos que crecen",
            "Mayor rotacion",
            "Clientes que reducen",
        ]
    )
    with tabs[0]:
        st.markdown(f"**Oportunidades para ampliar despacho - {horizon}**")
        table = answers["dispatch"].rename(
            columns={
                "Channel": "Canal",
                "Material Description": "SKU",
                "Proyeccion Horizonte": "Proyeccion_Horizonte",
                "Compromiso Base Horizonte": "Compromiso_Base_Horizonte",
                "Historico Horizonte": "Historico_Horizonte",
                "Cambio Unidades Horizonte": "Cambio_Unidades_Horizonte",
                "Probabilidad Horizonte": "Probabilidad_Horizonte",
            }
        )
        if table.empty:
            st.info(f"No hay combinaciones Canal x SKU que superen los criterios de despacho adicional para {horizon}.")
        else:
            _show_answer_table(
                table,
                ["Canal", "SKU", "Proyeccion_Horizonte", "Cambio_Unidades_Horizonte", "Probabilidad_Horizonte"],
                "Probabilidad_Horizonte",
                display_names={
                    "Proyeccion_Horizonte": f"Proyeccion {horizon}",
                    "Cambio_Unidades_Horizonte": f"Cambio esperado {horizon}",
                },
            )
    with tabs[1]:
        st.markdown("**Clientes con riesgo de baja actividad**")
        st.caption("Se priorizan clientes con historico relevante y bajo Compromiso Base frente a su historico.")
        _show_answer_table(
            answers["disappearance"],
            ["Channel", "Compromiso_Base_3m", "Historico_3m", "Retencion", "Probabilidad_de_Pedido"],
            "Probabilidad_de_Pedido",
        )
    with tabs[2]:
        st.markdown("**Productos con mayor crecimiento**")
        _show_answer_table(
            answers["growth"],
            ["Material Description", "Cambio_Unidades", "Proyeccion_3m", "Crecimiento", "Probabilidad_de_Pedido"],
            "Probabilidad_de_Pedido",
        )
    with tabs[3]:
        st.markdown("**Productos de mayor rotacion esperada**")
        _show_answer_table(
            answers["rotation"].rename(columns={"Material Description": "Material Description"}),
            ["Material Description", "Proyeccion_3m", "Compromiso_Base_3m", "Probabilidad_de_Pedido", "Canales"],
            "Probabilidad_de_Pedido",
        )
    with tabs[4]:
        st.markdown("**Clientes con caida proyectada**")
        _show_answer_table(
            answers["reductions"],
            ["Channel", "Cambio_Unidades", "Proyeccion_3m", "Historico_3m", "Compromiso_Base_3m", "Probabilidad_de_Pedido"],
            "Probabilidad_de_Pedido",
        )


def _opportunities_table(filtered, config, min_probability):
    table = filtered[
        filtered[config["proyeccion"]] > filtered["dem_promedio_hist"].clip(lower=1) * 1.5
    ].copy()
    table = table[table[config["probabilidad"]] >= min_probability].copy()
    table["Semaforo"] = table[config["probabilidad"]].apply(
        lambda value: "\U0001F7E2" if value > 0.70 else "\U0001F7E1" if value >= 0.30 else "\U0001F534"
    )
    table["Crecimiento vs Historico"] = table.apply(
        lambda row: row[config["proyeccion"]] / row["dem_promedio_hist"] if row["dem_promedio_hist"] > 0 else pd.NA,
        axis=1,
    )
    table = table.rename(
        columns={
            "Channel": "Canal",
            "Material Description": "SKU",
            "dem_promedio_hist": "Historico Promedio",
            config["proyeccion"]: "Proyeccion",
            config["compromiso"]: "Compromiso Base",
            config["probabilidad"]: "Probabilidad de Pedido",
        }
    )
    table["Probabilidad de Pedido"] = table["Probabilidad de Pedido"] * 100
    columns = [
        "Semaforo",
        "Canal",
        "SKU",
        "Proyeccion",
        "Compromiso Base",
        "Historico Promedio",
        "Crecimiento vs Historico",
        "Probabilidad de Pedido",
    ]
    table = table.sort_values(["Proyeccion", "Probabilidad de Pedido"], ascending=False)

    st.subheader("Oportunidades del Mes")
    st.caption("SKUs donde la proyeccion supera 1.5x el historico promedio y cumple la probabilidad minima seleccionada.")
    if table.empty:
        st.info("No hay oportunidades con los filtros actuales.")
        return
    st.dataframe(
        table[columns].head(250),
        hide_index=True,
        width="stretch",
        column_config={
            "SKU": st.column_config.TextColumn(width="large"),
            "Proyeccion": st.column_config.NumberColumn(format="%.0f"),
            "Compromiso Base": st.column_config.NumberColumn(format="%.0f"),
            "Historico Promedio": st.column_config.NumberColumn(format="%.0f"),
            "Crecimiento vs Historico": st.column_config.NumberColumn(format="%.1fx"),
            "Probabilidad de Pedido": st.column_config.ProgressColumn(format="%.0f%%", min_value=0, max_value=100),
        },
    )


def _top_products_next_3m(filtered):
    st.subheader("Top 15 productos por demanda esperada proximos 3 meses")
    if filtered.empty:
        st.info("No hay datos para graficar productos con los filtros actuales.")
        return

    monthly_columns = {
        "Agosto": "Stack_h+1 (Ago 2025)",
        "Septiembre": "Stack_h+2 (Sep 2025)",
        "Octubre": "Stack_h+3 (Oct 2025)",
    }
    products = filtered.groupby("Material Description", as_index=False).agg(
        **{month: (column, "sum") for month, column in monthly_columns.items()}
    )
    products["Total 3m"] = products[list(monthly_columns.keys())].sum(axis=1)
    products = products[products["Total 3m"] > 0].sort_values("Total 3m", ascending=False)

    if products.empty:
        st.info("No hay demanda esperada positiva para los proximos 3 meses con los filtros actuales.")
        return

    shown_count = min(15, len(products))
    chart_data = products.head(shown_count).copy()
    chart_data["Producto Completo"] = chart_data["Material Description"]
    chart_data["Producto Visible"] = chart_data["Material Description"].apply(lambda value: _shorten(value, 42))
    chart_data["Total Etiqueta"] = chart_data["Total 3m"].apply(_format_units)

    caption = "Top productos por proyeccion acumulada de Agosto, Septiembre y Octubre."
    if len(products) > shown_count:
        caption = f"{caption} Mostrando {shown_count} de {len(products)} productos."
    st.caption(caption)

    fig = go.Figure()
    colors = {
        "Agosto": COLORS["sky"],
        "Septiembre": COLORS["violet"],
        "Octubre": COLORS["green"],
    }
    for month in monthly_columns:
        fig.add_trace(
            go.Bar(
                x=chart_data[month],
                y=chart_data["Producto Visible"],
                name=month,
                orientation="h",
                marker=dict(color=colors[month], line=dict(color="rgba(248, 250, 252, .18)", width=1)),
                customdata=chart_data[["Producto Completo", month, "Total 3m"]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    + month
                    + ": %{customdata[1]:,.0f}<br>"
                    + "Total 3m: %{customdata[2]:,.0f}<extra></extra>"
                ),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=chart_data["Total 3m"],
            y=chart_data["Producto Visible"],
            mode="text",
            text=chart_data["Total Etiqueta"],
            textposition="middle right",
            textfont=dict(color="#334155", size=12),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_layout(
        template="plotly_dark",
        barmode="stack",
        height=max(460, min(820, 40 * len(chart_data) + 150)),
        margin=dict(l=28, r=104, t=28, b=44),
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#475569"),
        bargap=0.28,
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color="#334155")),
        hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#f8fafc"),
    )
    fig.update_traces(marker=dict(cornerradius=7), selector=dict(type="bar"))
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148, 163, 184, .16)",
        zeroline=False,
        tickformat=",.0f",
        tickfont=dict(color="#475569", size=11),
        range=[0, chart_data["Total 3m"].max() * 1.15 if not chart_data.empty else 1],
    )
    fig.update_yaxes(autorange="reversed", automargin=True, tickfont=dict(color="#334155", size=12))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _top_products_growth_log(filtered):
    st.subheader("Top 15 productos por crecimiento esperado proximos 3 meses")
    if filtered.empty:
        st.info("No hay datos para graficar crecimiento de productos con los filtros actuales.")
        return

    pairs = _enriched_pairs(filtered)
    products = (
        pairs.groupby("Material Description", as_index=False)
        .agg(
            Proyeccion_3m=("Proyeccion 3m", "sum"),
            Historico_3m=("Historico 3m", "sum"),
        )
    )
    products["Cambio_Unidades"] = products["Proyeccion_3m"] - products["Historico_3m"]
    products["Crecimiento"] = products.apply(
        lambda row: row["Proyeccion_3m"] / row["Historico_3m"] if row["Historico_3m"] > 0 else pd.NA,
        axis=1,
    )
    products = products[
        (products["Crecimiento"].notna())
        & (products["Crecimiento"] > 1)
        & (products["Cambio_Unidades"] > 0)
    ].sort_values(["Crecimiento", "Cambio_Unidades"], ascending=False)

    if products.empty:
        st.info("No hay productos con crecimiento esperado positivo frente al historico 3m.")
        return

    shown_count = min(15, len(products))
    chart_data = products.head(shown_count).copy()
    chart_data["Producto Completo"] = chart_data["Material Description"]
    chart_data["Producto Visible"] = chart_data["Material Description"].apply(lambda value: _shorten(value, 42))
    chart_data["Crecimiento Etiqueta"] = chart_data["Crecimiento"].apply(lambda value: f"{value:.1f}x")
    chart_data["Cambio Etiqueta"] = chart_data["Cambio_Unidades"].apply(_format_units)
    chart_data["Proyeccion Etiqueta"] = chart_data["Proyeccion_3m"].apply(_format_units)
    chart_data["Historico Etiqueta"] = chart_data["Historico_3m"].apply(_format_units)

    caption = "Escala logaritmica: compara ratios de crecimiento grandes sin ocultar productos de menor escala."
    if len(products) > shown_count:
        caption = f"{caption} Mostrando {shown_count} de {len(products)} productos con crecimiento positivo."
    st.caption(caption)

    fig = go.Figure(
        go.Bar(
            x=chart_data["Crecimiento"],
            y=chart_data["Producto Visible"],
            orientation="h",
            marker=dict(color=COLORS["green"], line=dict(color="rgba(248, 250, 252, .18)", width=1)),
            text=chart_data["Crecimiento Etiqueta"],
            textposition="outside",
            customdata=chart_data[
                [
                    "Producto Completo",
                    "Crecimiento Etiqueta",
                    "Cambio Etiqueta",
                    "Proyeccion Etiqueta",
                    "Historico Etiqueta",
                ]
            ],
            cliponaxis=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Crecimiento: %{customdata[1]}<br>"
                "Cambio esperado: %{customdata[2]}<br>"
                "Proyeccion 3m: %{customdata[3]}<br>"
                "Historico 3m: %{customdata[4]}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=max(460, min(820, 40 * len(chart_data) + 150)),
        margin=dict(l=28, r=96, t=28, b=44),
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#475569"),
        bargap=0.28,
        uniformtext=dict(minsize=11, mode="show"),
        hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#f8fafc"),
    )
    fig.update_traces(marker=dict(cornerradius=7), selector=dict(type="bar"))
    fig.update_xaxes(
        type="log",
        showgrid=True,
        gridcolor="rgba(148, 163, 184, .16)",
        zeroline=False,
        tickfont=dict(color="#475569", size=11),
        tickformat=".1f",
    )
    fig.update_yaxes(autorange="reversed", automargin=True, tickfont=dict(color="#334155", size=12))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _channel_ranking(filtered, config):
    ranking = (
        filtered.groupby("Channel", as_index=False)[config["proyeccion"]]
        .sum()
        .rename(columns={"Channel": "Canal", config["proyeccion"]: "Proyeccion"})
        .sort_values("Proyeccion", ascending=False)
    )

    st.subheader("Ranking de Canales")
    if ranking.empty:
        st.info("No hay canales para graficar con los filtros actuales.")
        return

    total_projection = ranking["Proyeccion"].sum()
    average = ranking["Proyeccion"].mean()
    shown_count = min(15, len(ranking))
    chart_data = ranking.head(shown_count).copy()
    chart_data["Participacion"] = chart_data["Proyeccion"] / total_projection if total_projection else 0
    chart_data["Etiqueta"] = chart_data["Proyeccion"].apply(_format_units)
    chart_data["Canal Completo"] = chart_data["Canal"]
    chart_data["Canal Visible"] = chart_data["Canal"].apply(lambda value: _shorten(value, 34))
    chart_data["Color"] = chart_data["Proyeccion"].apply(
        lambda value: COLORS["sky"] if value >= average else "rgba(148, 163, 184, .62)"
    )
    caption = f"Top {shown_count} canales por proyeccion del horizonte seleccionado; azul = sobre promedio."
    if len(ranking) > shown_count:
        caption = f"{caption} Mostrando {shown_count} de {len(ranking)} canales."
    st.caption(caption)

    fig = go.Figure(
        go.Bar(
            x=chart_data["Proyeccion"],
            y=chart_data["Canal Visible"],
            orientation="h",
            marker=dict(color=chart_data["Color"], line=dict(color="rgba(248, 250, 252, .18)", width=1)),
            text=chart_data["Etiqueta"],
            textposition="outside",
            customdata=chart_data[["Canal Completo", "Etiqueta", "Participacion"]],
            cliponaxis=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Proyeccion: %{customdata[1]}<br>"
                "Participacion: %{customdata[2]:.1%}<extra></extra>"
            ),
        )
    )
    fig.add_vline(
        x=average,
        line_dash="dash",
        line_color="rgba(203, 213, 225, .72)",
        annotation_text="Promedio",
        annotation_position="top left",
        annotation_font=dict(color="#cbd5e1", size=12),
    )
    fig.update_layout(
        template="plotly_dark",
        height=max(460, min(820, 40 * len(chart_data) + 150)),
        margin=dict(l=28, r=96, t=28, b=44),
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#475569"),
        bargap=0.28,
        uniformtext=dict(minsize=11, mode="show"),
        hoverlabel=dict(bgcolor="#0f172a", font_size=12, font_color="#f8fafc"),
    )
    fig.update_traces(marker=dict(cornerradius=7), selector=dict(type="bar"))
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148, 163, 184, .16)",
        zeroline=False,
        tickformat=",.0f",
        tickfont=dict(color="#475569", size=11),
        range=[0, chart_data["Proyeccion"].max() * 1.15 if not chart_data.empty else 1],
    )
    fig.update_yaxes(autorange="reversed", automargin=True, tickfont=dict(color="#334155", size=12))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _risk_alerts(filtered, config, min_probability):
    risks = filtered[
        (filtered[config["probabilidad"]] < min_probability)
        & (filtered[config["proyeccion"]] > 0)
    ].copy()
    risks = risks.sort_values(["Channel", config["proyeccion"]], ascending=[True, False])

    st.subheader("Alertas de Riesgo")
    st.caption("Pares Canal x SKU con proyeccion positiva, pero probabilidad de pedido por debajo del umbral.")
    if risks.empty:
        st.success("No hay alertas de riesgo con el umbral actual.")
        return

    for channel, group in risks.groupby("Channel", sort=True):
        total = group[config["proyeccion"]].sum()
        with st.expander(f"{channel} - {len(group)} alertas - {_format_units(total)} unidades"):
            table = group.rename(
                columns={
                    "Material Description": "SKU",
                    "dem_promedio_hist": "Historico Promedio",
                    config["proyeccion"]: "Proyeccion",
                    config["compromiso"]: "Compromiso Base",
                    config["probabilidad"]: "Probabilidad de Pedido",
                }
            )
            table["Probabilidad de Pedido"] = table["Probabilidad de Pedido"] * 100
            st.dataframe(
                table[["SKU", "Proyeccion", "Compromiso Base", "Historico Promedio", "Probabilidad de Pedido"]].head(150),
                hide_index=True,
                width="stretch",
                column_config={
                    "SKU": st.column_config.TextColumn(width="large"),
                    "Proyeccion": st.column_config.NumberColumn(format="%.0f"),
                    "Compromiso Base": st.column_config.NumberColumn(format="%.0f"),
                    "Historico Promedio": st.column_config.NumberColumn(format="%.0f"),
                    "Probabilidad de Pedido": st.column_config.ProgressColumn(format="%.0f%%", min_value=0, max_value=100),
                },
            )


def _pipeline_q3(filtered, selected_channels):
    st.subheader("Pipeline Q3")
    if filtered.empty:
        st.info("No hay datos para el pipeline con los filtros actuales.")
        return

    channels = selected_channels or (
        filtered.groupby("Channel")[[config["proyeccion"] for config in HORIZONS.values()]]
        .sum()
        .sum(axis=1)
        .sort_values(ascending=False)
        .head(12)
        .index
        .tolist()
    )
    pipeline = filtered[filtered["Channel"].isin(channels)].groupby("Channel", as_index=False).agg(
        Agosto=("Stack_h+1 (Ago 2025)", "sum"),
        Septiembre=("Stack_h+2 (Sep 2025)", "sum"),
        Octubre=("Stack_h+3 (Oct 2025)", "sum"),
        Total_3m=("Hurdle_total_3m", "sum"),
    )
    pipeline["Total Proyeccion 3m"] = pipeline[["Agosto", "Septiembre", "Octubre"]].sum(axis=1)
    pipeline = pipeline.sort_values("Total Proyeccion 3m", ascending=False)

    fig = go.Figure()
    colors = [COLORS["sky"], COLORS["violet"], COLORS["green"]]
    for month, color in zip(["Agosto", "Septiembre", "Octubre"], colors):
        fig.add_trace(
            go.Bar(
                x=pipeline["Channel"],
                y=pipeline[month],
                name=month,
                marker_color=color,
                hovertemplate="%{x}<br>" + month + ": %{y:,.0f}<extra></extra>",
            )
        )
    chart_height = max(560, min(820, 36 * len(pipeline) + 300))
    fig.update_layout(
        template="plotly_dark",
        barmode="group",
        height=chart_height,
        margin=dict(l=24, r=28, t=36, b=130),
        xaxis_title="Canal",
        yaxis_title="Proyeccion",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"),
        legend=dict(orientation="h", y=1.08, x=0),
        bargap=0.22,
        bargroupgap=0.08,
    )
    fig.update_xaxes(tickangle=-35, automargin=True, tickfont=dict(size=12))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148, 163, 184, .18)", tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    total_projection = pipeline["Total Proyeccion 3m"].sum()
    total_base = pipeline["Total_3m"].sum()
    c1, c2 = st.columns(2)
    c1.metric("Total Proyeccion 3 meses", _format_units(total_projection))
    c2.metric("Total Compromiso Base 3 meses", _format_units(total_base))


def render_predicciones():
    try:
        ancho = _prepare_ancho(load_predicciones_ancho())
        agregado = _build_agregado_from_ancho(ancho)
        mensual = load_df_mensual()
    except Exception as exc:
        st.error("No fue posible cargar los archivos de predicciones con el esquema esperado.")
        st.caption(str(exc))
        return

    source_errors = _validate_sources(agregado, ancho)
    if source_errors:
        st.error("Los CSV de predicciones no cuadran entre si. Revisa las fuentes antes de usar esta vista.")
        for error in source_errors:
            st.caption(error)
        return

    _inject_prediction_styles()
    st.title("Predicciones para Ventas")

    horizon, selected_channels, min_probability, filtered = _page_filters(ancho)
    config = HORIZONS[horizon]
    agregado_row = agregado[agregado["horizonte_label"].eq(config["label"])]
    if agregado_row.empty:
        st.error(f"No hay KPIs globales para {horizon}.")
        return
    agregado_row = agregado_row.iloc[0]

    _metric_row(agregado_row)
    st.divider()
    _commercial_answers_section(filtered, config, horizon)
    st.divider()
    _total_sales_forecast_chart(mensual, agregado, filtered, selected_channels)
    st.divider()
    _top_products_next_3m(filtered)
    st.divider()
    _top_products_growth_log(filtered)
    st.divider()
    _opportunities_table(filtered, config, min_probability)
    st.divider()
    _channel_ranking(filtered, config)
    st.divider()
    _pipeline_q3(filtered, selected_channels)
