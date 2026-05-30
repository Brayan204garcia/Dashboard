import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import plotly_layout
from app.components import card_end, card_start, kpi_card
from app.config import COLORS
from app.data import load_df_panel


def _format_percent(value):
    return f"{value:.1f}%"


def _format_number(value):
    if pd.isna(value):
        return "0"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def _safe_divide(numerator, denominator):
    denominator = denominator.replace(0, pd.NA)
    return numerator / denominator


def _date_range_label(start_date, end_date):
    return f"{start_date:%d/%m/%Y} - {end_date:%d/%m/%Y}"


def _section_note(title, detail, tone="sky"):
    st.markdown(
        f'<div class="metric-row"><span><span class="dot dot-{tone}"></span><b>{title}</b><br><span class="muted">{detail}</span></span></div>',
        unsafe_allow_html=True,
    )


def _last_four_weeks(df):
    return sorted(df["fecha"].drop_duplicates())[-4:]


def _filter_panel(df):
    customers = sorted(df["Channel"].dropna().unique())
    products = sorted(df["Material Description"].dropna().unique())
    min_date = df["fecha"].min().date()
    max_date = df["fecha"].max().date()

    with st.container(border=True):
        control_cols = st.columns([1.35, .85, .85, 2.2])
        with control_cols[0]:
            card_start("Periodo y alcance de analisis")
            st.markdown('<div class="muted">Filtros aplicados a la vista.</div>', unsafe_allow_html=True)
        with control_cols[1]:
            include_all_customers = st.checkbox("Todos los clientes", value=True, key="inventory_all_customers")
        with control_cols[2]:
            include_all_products = st.checkbox("Todos los productos", value=True, key="inventory_all_products")
        with control_cols[3]:
            start_date, end_date = st.slider(
                "Periodo seleccionado",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="YYYY-MM-DD",
                key="inventory_date_range",
            )

        selected_customers = []
        selected_products = []
        if not include_all_customers or not include_all_products:
            selector_cols = st.columns(2)
            with selector_cols[0]:
                if not include_all_customers:
                    selected_customers = st.multiselect(
                        "Clientes",
                        customers,
                        default=[],
                        placeholder="Selecciona clientes",
                        key="inventory_customers",
                    )
            with selector_cols[1]:
                if not include_all_products:
                    selected_products = st.multiselect(
                        "Productos",
                        products,
                        default=[],
                        placeholder="Selecciona productos",
                        key="inventory_products",
                    )

    selected_customers = customers if include_all_customers else selected_customers
    selected_products = products if include_all_products else selected_products
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    mask = df["fecha"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
    if selected_customers and len(selected_customers) < len(customers):
        mask &= df["Channel"].isin(selected_customers)
    if selected_products and len(selected_products) < len(products):
        mask &= df["Material Description"].isin(selected_products)
    if not selected_customers or not selected_products:
        return df.iloc[0:0], start_date, end_date
    return df.loc[mask].copy(), start_date, end_date


def _weekly_inventory_chart(df):
    weekly = (
        df.groupby("fecha", as_index=False)["channel_inv"]
        .agg(promedio="mean", mediana="median", p90=lambda values: values.quantile(.9))
        .sort_values("fecha")
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=weekly["fecha"],
            y=weekly["p90"],
            name="P90",
            mode="lines",
            line=dict(color="rgba(139,92,246,.28)", width=1),
            fill="tozeroy",
            fillcolor="rgba(139,92,246,.12)",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=weekly["fecha"],
            y=weekly["promedio"],
            name="Promedio",
            mode="lines",
            line=dict(color=COLORS["violet"], width=3),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=weekly["fecha"],
            y=weekly["mediana"],
            name="Mediana",
            mode="lines",
            line=dict(color=COLORS["sky"], width=2),
        )
    )
    for start, end, label, color in [
        ("2023-01-01", "2023-12-31", "Desacumulacion 2023", "rgba(244,63,94,.06)"),
        ("2024-01-01", "2024-12-31", "Equilibrio 2024", "rgba(56,189,248,.06)"),
        ("2025-01-01", "2025-12-31", "Acumulacion 2025", "rgba(34,197,94,.06)"),
    ]:
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor=color,
            line_width=0,
            layer="below",
            annotation_text=label,
            annotation_position="top left",
        )
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color=COLORS["red"],
        annotation_text="Inventario cero",
        annotation_position="top left",
    )
    fig.update_yaxes(title_text="Inventario canal")
    return plotly_layout(fig, height=390, show_legend=True)


def _client_stockout_chart(df):
    stockout = (
        df.assign(stockout=df["channel_inv"].eq(0))
        .groupby("Channel", as_index=False)["stockout"]
        .mean()
    )
    stockout["stockout_pct"] = stockout["stockout"] * 100
    top = stockout.sort_values("stockout_pct", ascending=False).head(15)

    fig = go.Figure(
        go.Bar(
            x=top["stockout_pct"],
            y=top["Channel"],
            orientation="h",
            marker_color=COLORS["red"],
            text=top["stockout_pct"].map(lambda value: f"{value:.1f}%"),
            textposition="auto",
        )
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), xaxis=dict(range=[0, 100]))
    fig.update_xaxes(title_text="% semanas en stockout")
    return plotly_layout(fig, height=430)


def _coverage_chart(df):
    weekly = (
        df.groupby("fecha", as_index=False)
        .agg(channel_inv=("channel_inv", "sum"), cust_sales=("cust_sales", "sum"))
        .sort_values("fecha")
    )
    weekly["coverage"] = _safe_divide(weekly["channel_inv"], weekly["cust_sales"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=weekly["fecha"],
            y=weekly["coverage"],
            name="Cobertura",
            mode="lines",
            line=dict(color=COLORS["green"], width=3),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,.12)",
        )
    )
    fig.add_hline(
        y=1,
        line_dash="dash",
        line_color=COLORS["yellow"],
        annotation_text="Cobertura < 1: riesgo de stockout",
        annotation_position="top left",
    )
    fig.update_yaxes(title_text="Cobertura inventario / ventas", rangemode="tozero")
    return plotly_layout(fig, height=360)


def _risk_products(df):
    if df.empty:
        return pd.DataFrame(columns=["Producto", "Ventas ultimas 4 semanas del periodo", "Inventario semana final"])

    latest_week = df["fecha"].max()
    last_four_weeks = _last_four_weeks(df[df["fecha"].le(latest_week)])
    sales_last_four = (
        df[df["fecha"].isin(last_four_weeks)]
        .groupby("Material Description", as_index=False)["cust_sales"]
        .sum()
        .rename(columns={"cust_sales": "Ventas ultimas 4 semanas del periodo"})
    )
    latest_inventory = (
        df[df["fecha"].eq(latest_week)]
        .groupby("Material Description", as_index=False)["channel_inv"]
        .sum()
        .rename(columns={"channel_inv": "Inventario semana final"})
    )
    risk = sales_last_four.merge(latest_inventory, on="Material Description", how="inner")
    risk = risk[(risk["Ventas ultimas 4 semanas del periodo"] > 0) & (risk["Inventario semana final"] == 0)]
    risk = risk.sort_values("Ventas ultimas 4 semanas del periodo", ascending=False).head(15)
    return risk.rename(columns={"Material Description": "Producto"})


def _risk_products_chart(risk):
    fig = go.Figure(
        go.Bar(
            x=risk["Ventas ultimas 4 semanas del periodo"],
            y=risk["Producto"],
            orientation="h",
            marker_color=COLORS["violet"],
            text=risk["Ventas ultimas 4 semanas del periodo"].map(_format_number),
            textposition="auto",
        )
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_xaxes(title_text="Ventas ultimas 4 semanas del periodo seleccionado")
    return plotly_layout(fig, height=430)


def _risk_heatmap_data(df):
    latest_week = df["fecha"].max()
    last_four_weeks = _last_four_weeks(df[df["fecha"].le(latest_week)])
    recent = df[df["fecha"].isin(last_four_weeks)]

    top_customers = (
        recent.groupby("Channel")["cust_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index
        .tolist()
    )
    top_products = (
        recent.groupby("Material Description")["cust_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index
        .tolist()
    )

    scoped = df[df["Channel"].isin(top_customers) & df["Material Description"].isin(top_products)]
    recent_sales = (
        scoped[scoped["fecha"].isin(last_four_weeks)]
        .groupby(["Channel", "Material Description"], as_index=False)["cust_sales"]
        .sum()
        .rename(columns={"cust_sales": "sales_4w"})
    )
    final_inventory = (
        scoped[scoped["fecha"].eq(latest_week)]
        .groupby(["Channel", "Material Description"], as_index=False)["channel_inv"]
        .sum()
        .rename(columns={"channel_inv": "final_inv"})
    )
    matrix = recent_sales.merge(final_inventory, on=["Channel", "Material Description"], how="outer").fillna(0)
    matrix["coverage"] = matrix["final_inv"] / matrix["sales_4w"].replace(0, pd.NA)

    def classify(row):
        if row["sales_4w"] > 0 and row["final_inv"] == 0:
            return 0, "Stockout inminente"
        if pd.notna(row["coverage"]) and row["coverage"] > 8:
            return 2, "Sobrestock"
        return 1, "Saludable"

    classified = matrix.apply(classify, axis=1, result_type="expand")
    matrix["risk_code"] = classified[0]
    matrix["risk_label"] = classified[1]
    return matrix, top_customers, top_products


def _risk_heatmap_chart(df):
    matrix, top_customers, top_products = _risk_heatmap_data(df)
    code_lookup = matrix.pivot(index="Channel", columns="Material Description", values="risk_code")
    label_lookup = matrix.pivot(index="Channel", columns="Material Description", values="risk_label")
    sales_lookup = matrix.pivot(index="Channel", columns="Material Description", values="sales_4w")
    inv_lookup = matrix.pivot(index="Channel", columns="Material Description", values="final_inv")
    coverage_lookup = matrix.pivot(index="Channel", columns="Material Description", values="coverage")

    code_lookup = code_lookup.reindex(index=top_customers, columns=top_products).fillna(1)
    label_lookup = label_lookup.reindex(index=top_customers, columns=top_products).fillna("Saludable")
    sales_lookup = sales_lookup.reindex(index=top_customers, columns=top_products).fillna(0)
    inv_lookup = inv_lookup.reindex(index=top_customers, columns=top_products).fillna(0)
    coverage_lookup = coverage_lookup.reindex(index=top_customers, columns=top_products)

    customdata = []
    for customer in top_customers:
        row = []
        for product in top_products:
            coverage = coverage_lookup.loc[customer, product]
            coverage_text = "N/A" if pd.isna(coverage) else f"{coverage:.2f}x"
            row.append(
                [
                    label_lookup.loc[customer, product],
                    _format_number(sales_lookup.loc[customer, product]),
                    _format_number(inv_lookup.loc[customer, product]),
                    coverage_text,
                ]
            )
        customdata.append(row)

    fig = go.Figure(
        go.Heatmap(
            z=code_lookup.values,
            x=top_products,
            y=top_customers,
            customdata=customdata,
            colorscale=[
                [0.0, COLORS["red"]],
                [0.333, COLORS["red"]],
                [0.334, COLORS["green"]],
                [0.666, COLORS["green"]],
                [0.667, COLORS["yellow"]],
                [1.0, COLORS["yellow"]],
            ],
            zmin=0,
            zmax=2,
            showscale=False,
            xgap=2,
            ygap=2,
            hovertemplate=(
                "<b>%{y}</b><br>%{x}<br>"
                "Estado: %{customdata[0]}<br>"
                "Ventas 4 sem.: %{customdata[1]}<br>"
                "Inventario final: %{customdata[2]}<br>"
                "Cobertura: %{customdata[3]}<extra></extra>"
            ),
        )
    )
    fig.update_xaxes(tickangle=-35, tickfont=dict(size=10))
    fig.update_yaxes(tickfont=dict(size=10))
    return plotly_layout(fig, height=470)


def render_inventario():
    df_panel = load_df_panel()
    filtered, start_date, end_date = _filter_panel(df_panel)

    if filtered.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    stockout_global = filtered["channel_inv"].eq(0).mean() * 100
    risk_products = _risk_products(filtered)
    weekly_coverage = (
        filtered.groupby("fecha")
        .agg(channel_inv=("channel_inv", "sum"), cust_sales=("cust_sales", "sum"))
        .assign(coverage=lambda data: _safe_divide(data["channel_inv"], data["cust_sales"]))
    )
    avg_coverage = weekly_coverage["coverage"].dropna().mean()
    period_label = _date_range_label(start_date, end_date)
    action_weeks = _last_four_weeks(filtered)
    action_label = _date_range_label(action_weeks[0].date(), action_weeks[-1].date())

    cols = st.columns(3)
    with cols[0]:
        kpi_card("% stockout en periodo", _format_percent(stockout_global), "Calculado con los filtros activos", "Periodo", "red", [])
    with cols[1]:
        kpi_card("Productos en riesgo ahora", _format_number(len(risk_products)), "Ventas ultimas 4 semanas + inventario cero final", "Accion", "yellow", [])
    with cols[2]:
        kpi_card("Cobertura promedio del periodo", f"{avg_coverage:.2f}x" if pd.notna(avg_coverage) else "0.00x", "Inventario / ventas en el periodo", "Riesgo < 1x", "green", [])

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        card_start("Inventario semanal dentro del periodo seleccionado", f"{period_label} | Promedio, mediana y P90 por semana")
        st.plotly_chart(_weekly_inventory_chart(filtered), use_container_width=True, config={"displayModeBar": False})
        card_end()

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            card_start("% de semanas con stockout por cliente", f"Top 15 clientes segun semanas con inventario cero | {period_label}")
            st.plotly_chart(_client_stockout_chart(filtered), use_container_width=True, config={"displayModeBar": False})
            card_end()
    with right:
        with st.container(border=True):
            card_start("Cobertura semanal dentro del periodo seleccionado", f"Inventario total / ventas totales por semana | {period_label}")
            st.plotly_chart(_coverage_chart(filtered), use_container_width=True, config={"displayModeBar": False})
            card_end()

    with st.container(border=True):
        card_start("Riesgo de stockout: productos con venta reciente e inventario cero", f"Ventas de las ultimas 4 semanas del periodo ({action_label}); inventario de la semana final")
        st.plotly_chart(_risk_products_chart(risk_products), use_container_width=True, config={"displayModeBar": False})
        if not risk_products.empty:
            st.markdown('<div class="eyebrow">Detalle para accion comercial inmediata</div>', unsafe_allow_html=True)
            st.dataframe(risk_products, hide_index=True, use_container_width=True)
        card_end()

    with st.container(border=True):
        card_start("Matriz cliente x producto - riesgo", "Top 10 clientes y Top 10 productos por ventas de las ultimas 4 semanas del periodo")
        st.markdown(
            '<div class="muted"><span class="dot dot-red"></span>Stockout inminente&nbsp;&nbsp;'
            '<span class="dot dot-green"></span>Saludable&nbsp;&nbsp;'
            '<span class="dot dot-yellow"></span>Sobrestock</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(_risk_heatmap_chart(filtered), use_container_width=True, config={"displayModeBar": False})
        card_end()
