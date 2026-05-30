import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import plotly_layout
from app.components import card_end, card_start
from app.config import COLORS
from app.data import load_df_mensual, load_df_panel


def _format_number(value):
    if pd.isna(value):
        return "0"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def _format_percent(value):
    if pd.isna(value):
        return "0.0%"
    return f"{value:.1f}%"


def _short_label(value, limit=44):
    value = str(value)
    return value if len(value) <= limit else f"{value[:limit - 3]}..."


def _family(series):
    return series.astype(str).str.split(",").str[0].str.strip()


def _safe_divide(numerator, denominator):
    return numerator / denominator.replace(0, pd.NA)


def _prepare_mensual(df):
    data = df.copy()
    data["familia"] = _family(data["Material Description"])
    return data


def _prepare_panel(df):
    data = df.copy()
    data["familia"] = _family(data["Material Description"])
    return data


def _family_summary(df):
    max_year = int(df["anio"].max())
    prev_year = max_year - 1
    max_month = int(df[df["anio"].eq(max_year)]["mes"].max())
    comparable = df[df["mes"].le(max_month)]
    current = comparable[comparable["anio"].eq(max_year)].groupby("familia")["cust_sales"].sum()
    previous = comparable[comparable["anio"].eq(prev_year)].groupby("familia")["cust_sales"].sum()
    summary = (
        df.groupby("familia", as_index=False)
        .agg(ventas=("cust_sales", "sum"), sell_in=("sell_in", "sum"), productos=("Material Description", "nunique"))
        .sort_values("ventas", ascending=False)
    )
    summary = summary.merge(current.rename("ventas_actual"), on="familia", how="left")
    summary = summary.merge(previous.rename("ventas_previa"), on="familia", how="left")
    summary[["ventas_actual", "ventas_previa"]] = summary[["ventas_actual", "ventas_previa"]].fillna(0)
    summary["crecimiento"] = _safe_divide(summary["ventas_actual"] - summary["ventas_previa"], summary["ventas_previa"]) * 100
    summary["sell_through"] = _safe_divide(summary["ventas"], summary["sell_in"]) * 100
    total = summary["ventas"].sum()
    summary["share"] = summary["ventas"] / total * 100 if total else 0
    summary["acumulado"] = summary["share"].cumsum()
    return summary


def _customer_summary(df):
    customer = df.groupby("Channel", as_index=False)["cust_sales"].sum().sort_values("cust_sales", ascending=False)
    total = customer["cust_sales"].sum()
    customer["share"] = customer["cust_sales"] / total * 100 if total else 0
    customer["acumulado"] = customer["share"].cumsum()
    return customer


def _inventory_signals(panel):
    latest_week = panel["fecha"].max()
    recent_weeks = sorted(panel["fecha"].drop_duplicates())[-8:]
    recent = panel[panel["fecha"].isin(recent_weeks)]
    sales8 = recent.groupby("Material Description")["cust_sales"].sum()
    sales_week = sales8 / max(len(recent_weeks), 1)
    inv = panel[panel["fecha"].eq(latest_week)].groupby("Material Description")["channel_inv"].sum()
    coverage = inv / sales_week.replace(0, pd.NA)
    signals = pd.DataFrame({"ventas_8w": sales8, "ventas_sem": sales_week, "inventario": inv, "cobertura": coverage}).fillna({"ventas_8w": 0, "ventas_sem": 0})
    stockout = signals[(signals["ventas_sem"] > 0) & (signals["cobertura"] < 1)].sort_values(["cobertura", "ventas_8w"], ascending=[True, False])
    overstock = signals[(signals["inventario"] > 0) & (signals["cobertura"] > 12)].sort_values("cobertura", ascending=False)
    negative_inventory = int((panel["channel_inv"] < 0).sum())
    return {
        "latest_week": latest_week,
        "recent_weeks": recent_weeks,
        "signals": signals,
        "stockout": stockout,
        "overstock": overstock,
        "negative_inventory": negative_inventory,
        "stockout_pct": panel["channel_inv"].eq(0).mean() * 100,
    }


def _period_metrics(df):
    max_year = int(df["anio"].max())
    prev_year = max_year - 1
    max_month = int(df[df["anio"].eq(max_year)]["mes"].max())
    comparable = df[df["mes"].le(max_month)]
    current = comparable[comparable["anio"].eq(max_year)]["cust_sales"].sum()
    previous = comparable[comparable["anio"].eq(prev_year)]["cust_sales"].sum()
    yoy = ((current - previous) / previous * 100) if previous else pd.NA
    return max_year, prev_year, max_month, current, previous, yoy


def _monthly_cumulative_chart(df):
    monthly = df.groupby(["anio", "mes"], as_index=False)["cust_sales"].sum()
    fig = go.Figure()
    palette = {2023: "#64748b", 2024: COLORS["sky"], 2025: COLORS["violet"]}
    for year in sorted(monthly["anio"].drop_duplicates()):
        subset = monthly[monthly["anio"].eq(year)].set_index("mes").reindex(range(1, 13), fill_value=0).reset_index()
        subset["acumulado"] = subset["cust_sales"].cumsum()
        fig.add_trace(
            go.Scatter(
                x=subset["mes"],
                y=subset["acumulado"],
                name=str(year),
                mode="lines+markers",
                line=dict(color=palette.get(int(year), COLORS["green"]), width=3 if int(year) == int(monthly["anio"].max()) else 2, shape="spline"),
                marker=dict(size=6),
                hovertemplate="<b>%{fullData.name}</b><br>Mes %{x}: %{y:,.0f}<extra></extra>",
            )
        )
    fig.update_xaxes(title_text="Mes", tickmode="array", tickvals=list(range(1, 13)))
    fig.update_yaxes(title_text="Ventas acumuladas")
    return plotly_layout(fig, height=350, show_legend=True)


def _pareto_chart(data, label_column, title_prefix):
    top = data.head(10).copy()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=top[label_column],
            y=top["share"],
            name="Share",
            marker_color=COLORS["violet"],
            text=top["share"].map(lambda value: f"{value:.1f}%"),
            textposition="outside",
            hovertemplate=f"<b>%{{x}}</b><br>{title_prefix}: %{{y:.1f}}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=top[label_column],
            y=top["acumulado"],
            name="Acumulado",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color=COLORS["sky"], width=3),
        )
    )
    fig.update_traces(marker=dict(cornerradius=7), selector=dict(type="bar"))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105], ticksuffix="%", showgrid=False))
    fig.update_xaxes(tickangle=-25)
    fig.update_yaxes(title_text="Participacion", ticksuffix="%")
    return plotly_layout(fig, height=360, show_legend=True)


def _lifecycle_chart(summary):
    data = summary.sort_values("ventas", ascending=False).head(15).copy()
    share_threshold = 2
    data["growth_plot"] = data["crecimiento"].fillna(0).clip(-90, 140)
    data["cuadrante"] = "Emergentes"
    data.loc[(data["share"] >= share_threshold) & (data["crecimiento"] >= 0), "cuadrante"] = "Estrellas"
    data.loc[(data["share"] >= share_threshold) & (data["crecimiento"] < 0), "cuadrante"] = "Muriendo"
    data.loc[(data["share"] < share_threshold) & (data["crecimiento"] < 0), "cuadrante"] = "Muertos"
    colors = {"Estrellas": COLORS["green"], "Emergentes": COLORS["sky"], "Muriendo": COLORS["yellow"], "Muertos": COLORS["red"]}
    fig = go.Figure()
    backgrounds = [
        (-90, 0, share_threshold, 70, "rgba(234,179,8,.10)", "MURIENDO"),
        (0, 140, share_threshold, 70, "rgba(34,197,94,.10)", "ESTRELLAS"),
        (-90, 0, 0, share_threshold, "rgba(244,63,94,.10)", "MUERTOS"),
        (0, 140, 0, share_threshold, "rgba(56,189,248,.10)", "EMERGENTES"),
    ]
    for x0, x1, y0, y1, fill, _ in backgrounds:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, fillcolor=fill, line_width=0, layer="below")
    for x, y, label in [(-68, 61, "MURIENDO"), (58, 61, "ESTRELLAS"), (-68, .35, "MUERTOS"), (58, .35, "EMERGENTES")]:
        fig.add_annotation(x=x, y=y, text=label, showarrow=False, font=dict(size=11, color="#475569"), opacity=.78)
    for quadrant, subset in data.groupby("cuadrante"):
        fig.add_trace(
            go.Scatter(
                x=subset["growth_plot"],
                y=subset["share"],
                name=quadrant,
                mode="markers+text",
                marker=dict(size=(subset["share"].clip(1, 28) * 1.8) + 10, color=colors[quadrant], opacity=.86, line=dict(color="#ffffff", width=1)),
                text=subset["familia"],
                textposition="middle right",
                customdata=subset[["crecimiento", "ventas"]],
                hovertemplate="<b>%{text}</b><br>Crecimiento: %{customdata[0]:.1f}%<br>Share: %{y:.1f}%<br>Ventas: %{customdata[1]:,.0f}<extra></extra>",
            )
        )
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8")
    fig.add_hline(y=share_threshold, line_dash="dash", line_color="#94a3b8")
    fig.update_xaxes(title_text="Crecimiento periodo comparable", ticksuffix="%", range=[-90, 140])
    fig.update_yaxes(title_text="Share de ventas", ticksuffix="%", range=[0, max(70, data["share"].max() * 1.12)])
    return plotly_layout(fig, height=430, show_legend=True)


def _lifecycle_groups(summary):
    data = summary.sort_values("ventas", ascending=False).copy()
    high_share = data["share"].ge(2)
    growing = data["crecimiento"].ge(0)
    return {
        "MURIENDO": data[high_share & ~growing].head(5),
        "ESTRELLAS": data[high_share & growing].head(5),
        "MUERTOS": data[~high_share & ~growing].head(5),
        "EMERGENTES": data[~high_share & growing].sort_values("crecimiento", ascending=False).head(5),
    }


def _quadrant_block(title, subtitle, rows, tone):
    if rows.empty:
        body = '<div class="metric-row"><span class="muted">Sin familias en este cuadrante.</span></div>'
    else:
        body = "".join(
            f'<div class="metric-row"><span>'
            f'<span class="dot dot-{html.escape(tone)}"></span><b>{html.escape(row["familia"])}</b>'
            f'<br><span class="muted">Share {row["share"]:.1f}% | Crec. {_format_percent(row["crecimiento"])} | Ventas {_format_number(row["ventas"])}</span>'
            f'</span></div>'
            for _, row in rows.iterrows()
        )
    st.markdown(
        f'<div class="eyebrow">{html.escape(subtitle)}</div>'
        f'<div class="section-title">{html.escape(title)}</div>'
        f'{body}',
        unsafe_allow_html=True,
    )


def _render_lifecycle_matrix(summary):
    groups = _lifecycle_groups(summary)
    top_left, top_right = st.columns(2)
    with top_left:
        _quadrant_block("Muriendo", "Share alto + caida", groups["MURIENDO"], "yellow")
    with top_right:
        _quadrant_block("Estrellas", "Share alto + crecimiento", groups["ESTRELLAS"], "green")

    bottom_left, bottom_right = st.columns(2)
    with bottom_left:
        _quadrant_block("Muertos", "Share bajo + caida", groups["MUERTOS"], "red")
    with bottom_right:
        _quadrant_block("Emergentes", "Share bajo + crecimiento", groups["EMERGENTES"], "sky")


def _inventory_health_chart(stockout_count, overstock_count, healthy_count):
    labels = ["Stockout", "Saludable", "Sobrestock"]
    values = [stockout_count, healthy_count, overstock_count]
    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color=[COLORS["red"], COLORS["green"], COLORS["yellow"]],
            text=[_format_number(value) for value in values],
            textposition="outside",
        )
    )
    fig.update_yaxes(title_text="Productos")
    return plotly_layout(fig, height=310)


def _alert_rows(families, customers, inventory):
    rows = []
    top_family = families.iloc[0]
    top_customer = customers.iloc[0]
    top_stockout = inventory["stockout"].head(1)
    top_overstock = inventory["overstock"].head(1)

    rows.append(
        {
            "Tipo": "Mix critico",
            "Hallazgo": f'{top_family["familia"]} concentra {top_family["share"]:.1f}% y cambia {_format_percent(top_family["crecimiento"])}',
            "Impacto": _format_number(top_family["ventas"]),
            "Accion": "Revisar plan comercial e inventario de la familia lider",
        }
    )
    rows.append(
        {
            "Tipo": "Concentracion cliente",
            "Hallazgo": f'{top_customer["Channel"]} aporta {top_customer["share"]:.1f}% de ventas',
            "Impacto": _format_number(top_customer["cust_sales"]),
            "Accion": "Proteger cuenta clave y monitorear caidas",
        }
    )
    if not top_stockout.empty:
        product = top_stockout.index[0]
        row = top_stockout.iloc[0]
        rows.append(
            {
                "Tipo": "Stockout observado",
                "Hallazgo": f"{_short_label(product)} tiene cobertura {row['cobertura']:.1f} sem",
                "Impacto": _format_number(row["ventas_8w"]),
                "Accion": "Priorizar reposicion o revisar disponibilidad",
            }
        )
    if not top_overstock.empty:
        product = top_overstock.index[0]
        row = top_overstock.iloc[0]
        rows.append(
            {
                "Tipo": "Sobrestock",
                "Hallazgo": f"{_short_label(product)} tiene cobertura {row['cobertura']:.1f} sem",
                "Impacto": _format_number(row["inventario"]),
                "Accion": "Reducir despacho, liquidar o reasignar inventario",
            }
        )
    if inventory["negative_inventory"] > 0:
        rows.append(
            {
                "Tipo": "Calidad de dato",
                "Hallazgo": f'{_format_number(inventory["negative_inventory"])} registros con inventario negativo',
                "Impacto": "Dato atipico",
                "Accion": "Validar antes de tomar decisiones operativas",
            }
        )
    weak_families = families[(families["share"] >= 2) & (families["crecimiento"] < -20)].head(2)
    for _, row in weak_families.iterrows():
        rows.append(
            {
                "Tipo": "Familia en caida",
                "Hallazgo": f'{row["familia"]} cae {_format_percent(row["crecimiento"])} en periodo comparable',
                "Impacto": _format_number(row["ventas_actual"]),
                "Accion": "Separar caida de demanda vs ruptura o menor despacho",
            }
        )
    return pd.DataFrame(rows).head(8)


def _headline(text, detail):
    st.markdown(
        f'<div class="metric-row"><span><b>{html.escape(text)}</b><br>'
        f'<span class="muted">{html.escape(detail)}</span></span></div>',
        unsafe_allow_html=True,
    )


def _summary_kpis(items):
    cards = []
    for item in items:
        tone = item["tone"]
        cards.append(
            f'<div class="summary-kpi summary-kpi-{html.escape(tone)}">'
            f'<div class="summary-kpi-top"><span>{html.escape(item["label"])}</span><b>{html.escape(item["badge"])}</b></div>'
            f'<div class="summary-kpi-value">{html.escape(item["value"])}</div>'
            f'<div class="summary-kpi-meta">{html.escape(item["meta"])}</div>'
            f'</div>'
        )
    st.markdown(
        f"""<style>
.summary-kpi-grid {{
display: grid;
grid-template-columns: 1.15fr 1.15fr 1fr 1fr;
grid-template-areas:
"sales sales yoy sellin"
"stockout stockout concentration overstock";
gap: .7rem;
align-items: stretch;
margin-bottom: 1.25rem;
}}
.summary-kpi {{
min-height: 112px;
border-radius: 10px;
padding: .82rem .9rem;
background: #ffffff;
border: 1px solid #e2e8f0;
box-shadow: 0 1px 2px rgba(15,23,42,.05);
display: flex;
flex-direction: column;
justify-content: space-between;
gap: .55rem;
}}
.summary-kpi:first-child {{
background: #1f2937;
color: #ffffff;
border-color: #1f2937;
}}
.summary-kpi-top {{
display: flex;
align-items: flex-start;
justify-content: space-between;
gap: .5rem;
color: #475569;
font-size: .72rem;
line-height: 1.12;
font-weight: 850;
text-transform: uppercase;
}}
.summary-kpi:first-child .summary-kpi-top {{ color: #cbd5e1; }}
.summary-kpi-top b {{
flex: 0 0 auto;
border-radius: 999px;
padding: .16rem .42rem;
background: #f1f5f9;
color: #334155;
font-size: .66rem;
line-height: 1;
white-space: nowrap;
}}
.summary-kpi:first-child .summary-kpi-top b {{
background: rgba(255,255,255,.12);
color: #ffffff;
}}
.summary-kpi-value {{
color: #0f172a;
font-size: 1.58rem;
line-height: 1;
font-weight: 900;
letter-spacing: 0;
white-space: nowrap;
}}
.summary-kpi:first-child .summary-kpi-value {{
color: #ffffff;
font-size: 1.9rem;
}}
.summary-kpi-meta {{
color: #64748b;
font-size: .76rem;
line-height: 1.18;
font-weight: 750;
}}
.summary-kpi:first-child .summary-kpi-meta {{ color: #cbd5e1; }}
.summary-kpi:nth-child(1) {{ grid-area: sales; }}
.summary-kpi:nth-child(2) {{ grid-area: sellin; }}
.summary-kpi:nth-child(3) {{ grid-area: yoy; }}
.summary-kpi:nth-child(4) {{ grid-area: concentration; }}
.summary-kpi:nth-child(5) {{ grid-area: stockout; background: #fff1f2; border-color: #fecdd3; }}
.summary-kpi:nth-child(5) .summary-kpi-value {{ color: #be123c; }}
.summary-kpi:nth-child(6) {{ grid-area: overstock; }}
@media (max-width: 1250px) {{
.summary-kpi-grid {{
grid-template-columns: repeat(2, minmax(0, 1fr));
grid-template-areas:
"sales yoy"
"sellin stockout"
"concentration overstock";
}}
}}
@media (max-width: 760px) {{
.summary-kpi-grid {{
grid-template-columns: repeat(2, minmax(0, 1fr));
grid-template-areas:
"sales sales"
"yoy sellin"
"stockout stockout"
"concentration overstock";
}}
.summary-kpi-value, .summary-kpi:first-child .summary-kpi-value {{ font-size: 1.38rem; }}
}}
@media (max-width: 520px) {{
.summary-kpi-grid {{
grid-template-columns: 1fr;
grid-template-areas:
"sales"
"yoy"
"sellin"
"stockout"
"concentration"
"overstock";
}}
}}
</style>
<div class="summary-kpi-grid">{''.join(cards)}</div>""",
        unsafe_allow_html=True,
    )


def render_resumen():
    mensual = _prepare_mensual(load_df_mensual())
    panel = _prepare_panel(load_df_panel())
    families = _family_summary(mensual)
    customers = _customer_summary(mensual)
    inventory = _inventory_signals(panel)
    max_year, prev_year, max_month, current_sales, previous_sales, yoy = _period_metrics(mensual)

    total_sales = mensual["cust_sales"].sum()
    total_sell_in = mensual["sell_in"].sum()
    sell_gap = total_sales - total_sell_in
    top10_customer_share = customers.head(10)["share"].sum()
    stockout_count = len(inventory["stockout"])
    overstock_count = len(inventory["overstock"])
    healthy_count = max(mensual["Material Description"].nunique() - stockout_count - overstock_count, 0)

    _summary_kpis(
        [
            {"label": "Ventas consumidor", "value": _format_number(total_sales), "meta": "cust_sales total del historico", "badge": "EDA", "tone": "sky"},
            {"label": "Sell-in", "value": _format_number(total_sell_in), "meta": f"Brecha: {_format_number(sell_gap)}", "badge": "Despacho", "tone": "green" if sell_gap >= 0 else "yellow"},
            {"label": f"{max_year} vs {prev_year}", "value": _format_percent(yoy), "meta": f"Comparacion meses 1-{max_month}", "badge": "YoY", "tone": "red" if pd.notna(yoy) and yoy < 0 else "green"},
            {"label": "Top 10 clientes", "value": _format_percent(top10_customer_share), "meta": "Concentracion de ventas", "badge": "Riesgo", "tone": "yellow"},
            {"label": "Stockout", "value": _format_number(stockout_count), "meta": "Productos con cobertura < 1 sem", "badge": "Accion", "tone": "red"},
            {"label": "Sobrestock", "value": _format_number(overstock_count), "meta": "Productos con cobertura > 12 sem", "badge": "Control", "tone": "yellow"},
        ]
    )

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    _headline(
        "Negocio concentrado, Mobile domina el mix y la salud de inventario requiere gestion por extremos.",
        f'MOBILE explica {families.iloc[0]["share"]:.1f}% de ventas; Top 10 clientes concentra {top10_customer_share:.1f}%; fecha inventario {inventory["latest_week"]:%d/%m/%Y}.',
    )

    left, right = st.columns([1.2, .8])
    with left:
        with st.container(border=True):
            card_start("Evolucion acumulada real", "Ventas consumidor por mes y anio")
            st.plotly_chart(_monthly_cumulative_chart(mensual), use_container_width=True, config={"displayModeBar": False})
            card_end()
    with right:
        with st.container(border=True):
            card_start("Riesgos prioritarios", "Reglas EDA trazables, no predicciones")
            alerts = _alert_rows(families, customers, inventory)
            st.dataframe(alerts, hide_index=True, use_container_width=True)
            card_end()

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            card_start("Pareto por familia", "Dependencia del mix de producto")
            st.plotly_chart(_pareto_chart(families, "familia", "Familia"), use_container_width=True, config={"displayModeBar": False})
            card_end()
    with right:
        with st.container(border=True):
            card_start("Pareto por cliente", "Dependencia de cuentas clave")
            st.plotly_chart(_pareto_chart(customers, "Channel", "Cliente"), use_container_width=True, config={"displayModeBar": False})
            card_end()

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    left, right = st.columns([1.25, .75])
    with left:
        with st.container(border=True):
            card_start("Ciclo de vida por familia", "Matriz EDA: share de ventas vs crecimiento comparable")
            _render_lifecycle_matrix(families)
            card_end()
    with right:
        with st.container(border=True):
            card_start("Salud producto-inventario", "Cobertura calculada con las ultimas 8 semanas")
            st.plotly_chart(_inventory_health_chart(stockout_count, overstock_count, healthy_count), use_container_width=True, config={"displayModeBar": False})
            st.markdown(
                f'<div class="metric-row"><span><b>Stockout observado:</b> productos con ventas recientes y cobertura menor a 1 semana.<br>'
                f'<span class="muted">Sobrestock: inventario actual mayor a 12 semanas de venta reciente.</span></span></div>',
                unsafe_allow_html=True,
            )
            card_end()
