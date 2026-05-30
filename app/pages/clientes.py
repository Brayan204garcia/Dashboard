import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import plotly_layout
from app.components import kpi_card
from app.config import COLORS
from app.data import load_df_mensual


SEGMENT_ORDER = ["Campeones", "Leales Valiosos", "En Riesgo Alto", "Perdidos"]
SEGMENT_META = {
    "Campeones": ("Proteger a toda costa", "green"),
    "Leales Valiosos": ("Mantener relacion", "sky"),
    "En Riesgo Alto": ("Accion comercial urgente", "yellow"),
    "Perdidos": ("Evaluar recuperacion", "red"),
}


def _format_percent(value):
    if pd.isna(value):
        return "0.0%"
    return f"{value:.1f}%"


def _format_number(value):
    if pd.isna(value):
        return "0"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def _short_label(value, limit=42):
    value = str(value)
    return value if len(value) <= limit else f"{value[:limit - 3]}..."


def _family(series):
    return series.astype(str).str.split(",").str[0].str.strip()


def _client_chart_header(title, subtitle=None, badges=None):
    subtitle_html = f'<div class="client-chart-subtitle">{html.escape(subtitle)}</div>' if subtitle else ""
    badges_html = "".join(
        f'<span class="client-chart-badge">{html.escape(str(badge))}</span>' for badge in (badges or [])
    )
    st.markdown(
        f"""
        <div class="client-chart-head">
            <div>
                <div class="client-chart-title">{html.escape(title)}</div>
                {subtitle_html}
            </div>
            <div class="client-chart-badges">{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _style_client_fig(fig, height=390, show_legend=False, hovermode="x unified"):
    fig = plotly_layout(fig, height=height, show_legend=show_legend)
    fig.update_layout(
        hovermode=hovermode,
        bargap=.32,
        margin=dict(l=8, r=12, t=8, b=8),
        font=dict(family="Inter, Arial, sans-serif", color="#334155", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#334155", size=12),
        ),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#cbd5e1", font=dict(color="#0f172a", size=12)),
        xaxis=dict(
            showline=True,
            linecolor="#cbd5e1",
            linewidth=1,
            ticks="outside",
            ticklen=3,
            title_font=dict(color="#1f2937", size=12),
            tickfont=dict(color="#334155", size=11),
        ),
        yaxis=dict(
            showline=False,
            title_font=dict(color="#1f2937", size=12),
            tickfont=dict(color="#334155", size=11),
        ),
    )
    fig.update_xaxes(gridcolor="#e2e8f0", showgrid=True)
    fig.update_yaxes(gridcolor="#e2e8f0")
    return fig


def _prepare_mensual(df):
    data = df.copy()
    data["familia"] = _family(data["Material Description"])
    data["trimestre"] = ((data["mes"] - 1) // 3 + 1).astype(int)
    data["periodo_trimestre"] = data["anio"].astype(str) + " T" + data["trimestre"].astype(str)
    return data


def _filter_mensual(df):
    max_date = df["fecha_mes"].max()
    max_year = int(df["anio"].max())
    families = (
        df.groupby("familia")["cust_sales"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )
    period_options = [
        "Todo el historico",
        f"{max_year}",
        "Ultimos 12 meses",
        "Ultimos 6 meses",
    ]

    with st.container(border=True):
        cols = st.columns([1.15, 1.85])
        with cols[0]:
            period = st.selectbox("Periodo comercial", period_options, key="clients_period")
        with cols[1]:
            family = st.selectbox(
                "Familia producto",
                ["Todas las familias"] + families,
                key="clients_family",
            )

    mask = pd.Series(True, index=df.index)
    if period == f"{max_year}":
        mask &= df["anio"].eq(max_year)
    elif period == "Ultimos 12 meses":
        mask &= df["fecha_mes"].ge(max_date - pd.DateOffset(months=11))
    elif period == "Ultimos 6 meses":
        mask &= df["fecha_mes"].ge(max_date - pd.DateOffset(months=5))

    selected_families = []
    if family != "Todas las familias":
        selected_families = [family]
        mask &= df["familia"].eq(family)

    filtered = df.loc[mask].copy()
    selected_years = sorted(filtered["anio"].dropna().unique().tolist())
    selected_quarters = sorted(filtered["trimestre"].dropna().unique().tolist())
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    return filtered, selected_years, selected_quarters, selected_families


def _monthly_by_customer(df):
    return (
        df.groupby(["fecha_mes", "periodo_trimestre", "Channel"], as_index=False)
        .agg(cust_sales=("cust_sales", "sum"), sell_in=("sell_in", "sum"))
        .sort_values(["fecha_mes", "Channel"])
    )


def _customer_summary(df):
    monthly = _monthly_by_customer(df)
    max_date = monthly["fecha_mes"].max()
    active = monthly[monthly["cust_sales"] > 0]
    last_sale = active.groupby("Channel")["fecha_mes"].max().rename("Ultima compra")
    summary = (
        monthly.groupby("Channel", as_index=False)
        .agg(
            Ventas=("cust_sales", "sum"),
            Sell_in=("sell_in", "sum"),
            Meses_compra=("cust_sales", lambda s: int((s > 0).sum())),
        )
        .merge(last_sale.reset_index(), on="Channel", how="left")
    )
    summary["Recencia dias"] = (max_date - summary["Ultima compra"]).dt.days
    summary["Recencia dias"] = summary["Recencia dias"].fillna(9999)
    summary["monetary_pct"] = summary["Ventas"].rank(pct=True) * 100
    summary["frequency_pct"] = summary["Meses_compra"].rank(pct=True) * 100
    summary["recency_pct"] = (1 - summary["Recencia dias"].rank(pct=True)) * 100
    summary["rfm_score"] = (summary["monetary_pct"] * .45) + (summary["frequency_pct"] * .30) + (summary["recency_pct"] * .25)

    recent_months = sorted(monthly["fecha_mes"].drop_duplicates())[-3:]
    prior_months = sorted(monthly["fecha_mes"].drop_duplicates())[-6:-3]
    recent = monthly[monthly["fecha_mes"].isin(recent_months)].groupby("Channel")["cust_sales"].sum()
    prior = monthly[monthly["fecha_mes"].isin(prior_months)].groupby("Channel")["cust_sales"].sum()
    summary = summary.merge(recent.rename("Ventas ult 3M"), on="Channel", how="left")
    summary = summary.merge(prior.rename("Ventas prev 3M"), on="Channel", how="left")
    summary[["Ventas ult 3M", "Ventas prev 3M"]] = summary[["Ventas ult 3M", "Ventas prev 3M"]].fillna(0)
    summary["Tendencia 3M"] = (
        (summary["Ventas ult 3M"] - summary["Ventas prev 3M"]) / summary["Ventas prev 3M"].replace(0, pd.NA)
    )

    def segment(row):
        if row["Recencia dias"] > 365 or (row["Ventas ult 3M"] == 0 and row["Ventas prev 3M"] > 0):
            return "Perdidos"
        if row["Recencia dias"] > 150 or (pd.notna(row["Tendencia 3M"]) and row["Tendencia 3M"] <= -.45):
            return "En Riesgo Alto"
        if row["rfm_score"] >= 72:
            return "Campeones"
        if row["monetary_pct"] >= 55 or row["frequency_pct"] >= 60:
            return "Leales Valiosos"
        return "En Riesgo Alto"

    summary["Segmento"] = summary.apply(segment, axis=1)
    return summary.sort_values("Ventas", ascending=False)


def _rfm_card(summary, segment):
    segment_df = summary[summary["Segmento"].eq(segment)].sort_values("Ventas", ascending=False)
    customers = ", ".join(segment_df.head(3)["Channel"].tolist()) or "Sin clientes"
    action, tone = SEGMENT_META[segment]
    st.markdown(
        f"""
        <div class="rfm-card rfm-{tone}">
            <div class="rfm-card-top">
                <div class="rfm-title">{html.escape(segment)}</div>
                <div class="rfm-count">{len(segment_df)}</div>
            </div>
            <div class="rfm-customers">{html.escape(customers)}</div>
            <div class="rfm-action">{html.escape(action)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _trend_table(df, limit=12):
    years = sorted(df["anio"].drop_duplicates())
    if len(years) < 2:
        return pd.DataFrame(columns=["Cliente", "Ventas base", "Ventas actual", "Tendencia"])
    base_year, current_year = years[-2], years[-1]
    pivot = (
        df[df["anio"].isin([base_year, current_year])]
        .groupby(["Channel", "anio"])["cust_sales"]
        .sum()
        .unstack(fill_value=0)
    )
    pivot["Tendencia valor"] = (pivot[current_year] - pivot[base_year]) / pivot[base_year].replace(0, pd.NA)
    pivot["impacto"] = (pivot[current_year] - pivot[base_year]).abs()
    table = pivot.sort_values("impacto", ascending=False).head(limit).reset_index()
    table = table.rename(columns={"Channel": "Cliente", base_year: f"Ventas {base_year}", current_year: f"Ventas {current_year}"})
    table["Tendencia"] = table["Tendencia valor"].map(_trend_label)
    return table[["Cliente", f"Ventas {base_year}", f"Ventas {current_year}", "Tendencia"]]


def _trend_label(value):
    if pd.isna(value):
        return "Sin base"
    direction = "Sube" if value >= 0 else "Baja"
    return f"{direction} {value * 100:+.1f}%"


def _quarterly_chart(monthly, customers):
    data = (
        monthly[monthly["Channel"].isin(customers)]
        .groupby(["periodo_trimestre", "Channel"], as_index=False)["cust_sales"]
        .sum()
    )
    order = monthly.drop_duplicates("periodo_trimestre")["periodo_trimestre"].tolist()
    palette = [COLORS["violet"], COLORS["sky"], COLORS["green"], COLORS["yellow"], COLORS["red"], "#0ea5e9", "#14b8a6"]
    fig = go.Figure()
    for index, customer in enumerate(customers):
        subset = data[data["Channel"].eq(customer)].set_index("periodo_trimestre").reindex(order).fillna(0).reset_index()
        fig.add_trace(
            go.Scatter(
                x=subset["periodo_trimestre"],
                y=subset["cust_sales"],
                name=customer,
                mode="lines+markers",
                line=dict(width=3 if index == 0 else 2, color=palette[index % len(palette)], shape="spline", smoothing=1.1),
                marker=dict(size=7),
                hovertemplate="<b>%{fullData.name}</b><br>%{x}: %{y:,.0f}<extra></extra>",
            )
        )
    fig.update_yaxes(title_text="Ventas")
    return _style_client_fig(fig, height=390, show_legend=True)


def _pareto_chart(summary):
    data = summary.sort_values("Ventas", ascending=False).head(10).copy()
    total = summary["Ventas"].sum()
    data["share"] = data["Ventas"] / total * 100 if total else 0
    data["acumulado"] = data["share"].cumsum()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data["Channel"],
            y=data["share"],
            name="Share ventas",
            marker_color=COLORS["violet"],
            marker_line_width=0,
            text=data["share"].map(lambda v: f"{v:.1f}%"),
            textposition="outside",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["Channel"],
            y=data["acumulado"],
            name="Acumulado",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color=COLORS["sky"], width=3),
            marker=dict(size=8),
        )
    )
    fig.update_traces(marker=dict(cornerradius=7), selector=dict(type="bar"))
    fig.update_layout(
        yaxis2=dict(
            overlaying="y",
            side="right",
            ticksuffix="%",
            range=[0, 105],
            showgrid=False,
            tickfont=dict(color="#334155", size=11),
            title_font=dict(color="#1f2937", size=12),
        )
    )
    fig.update_yaxes(title_text="Participacion", ticksuffix="%")
    fig.update_xaxes(tickangle=-25)
    return _style_client_fig(fig, height=455, show_legend=True, hovermode="closest")


def _top_product(df):
    product_sales = df.groupby("Material Description")["cust_sales"].sum().sort_values(ascending=False)
    if product_sales.empty:
        return None, 0
    return product_sales.index[0], product_sales.iloc[0]


def _heatmap(df, summary):
    product, total_sales = _top_product(df)
    if product is None:
        fig = go.Figure()
        return _style_client_fig(fig, height=390, hovermode="closest")

    product_df = df[df["Material Description"].eq(product)]
    top_customers = (
        product_df.groupby("Channel")["cust_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )
    if not top_customers:
        top_customers = summary.head(10)["Channel"].tolist()

    matrix = (
        product_df[product_df["Channel"].isin(top_customers)]
        .groupby(["Channel", "Material Description"])["cust_sales"]
        .sum()
        .unstack(fill_value=0)
        .reindex(index=top_customers, columns=[product], fill_value=0)
    )
    share = matrix[product].div(total_sales).mul(100) if total_sales else matrix[product] * 0
    hover_data = [
        [[product, f"{share.loc[customer]:.1f}%"]]
        for customer in matrix.index
    ]
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=[_short_label(product)],
            y=matrix.index,
            customdata=hover_data,
            colorscale=[[0, "#f8fafc"], [.35, "#bfdbfe"], [.7, "#60a5fa"], [1, "#7c3aed"]],
            hovertemplate="<b>%{y}</b><br>%{customdata[0]}: %{z:,.0f}<br>Share producto: %{customdata[1]}<extra></extra>",
            colorbar=dict(title="Ventas"),
        )
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return _style_client_fig(fig, height=390, hovermode="closest")


def _client_profile(df, summary, customer):
    customer_summary = summary[summary["Channel"].eq(customer)].iloc[0]
    customer_data = df[df["Channel"].eq(customer)]
    products = (
        customer_data.groupby("familia")["cust_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
    )
    total = products.sum()
    trend = _trend_label(customer_summary["Tendencia 3M"])
    product_lines = "".join(
        f"<div class='profile-line'><span>{html.escape(name)}</span><strong>{_format_number(value)} ({(value / total * 100 if total else 0):.0f}%)</strong></div>"
        for name, value in products.items()
    )
    recommendation = "Visita comercial urgente recomendada" if customer_summary["Segmento"] == "En Riesgo Alto" else (
        "Evaluar si vale recuperar" if customer_summary["Segmento"] == "Perdidos" else "Mantener y ampliar relacion"
    )
    st.markdown(
        f"""
        <div class="client-profile">
            <div class="profile-title">{html.escape(customer)}</div>
            <div class="profile-grid">
                <div class="profile-line"><span>Segmento RFM</span><strong>{html.escape(customer_summary["Segmento"])}</strong></div>
                <div class="profile-line"><span>Recencia</span><strong>{customer_summary["Recencia dias"]:.0f} dias</strong></div>
                <div class="profile-line"><span>Ventas totales</span><strong>{_format_number(customer_summary["Ventas"])}</strong></div>
                <div class="profile-line"><span>Tendencia</span><strong>{html.escape(trend)}</strong></div>
            </div>
            <div class="profile-subtitle">Top 3 familias producto</div>
            <div class="profile-stack">
                {product_lines}
            </div>
            <div class="profile-reco">{html.escape(recommendation)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_clientes():
    df_mensual = _prepare_mensual(load_df_mensual())
    filtered, selected_years, selected_quarters, selected_families = _filter_mensual(df_mensual)

    if filtered.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    summary = _customer_summary(filtered)
    monthly = _monthly_by_customer(filtered)
    total_customers = summary["Channel"].nunique()
    active_customers = summary[summary["Ventas"] > 0]["Channel"].nunique()
    risk_customers = int(summary["Segmento"].eq("En Riesgo Alto").sum())
    lost_customers = int(summary["Segmento"].eq("Perdidos").sum())

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Total Clientes", _format_number(total_customers), "Base filtrada", "Clientes", "sky", [])
    with cols[1]:
        kpi_card("Clientes Activos", _format_number(active_customers), "Ventas > 0", "Activos", "green", [])
    with cols[2]:
        kpi_card("Clientes En Riesgo", _format_number(risk_customers), "Prioridad comercial", "Riesgo", "yellow", [])
    with cols[3]:
        kpi_card("Clientes Perdidos", _format_number(lost_customers), "Sin compra reciente", "Perdidos", "red", [])

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        _client_chart_header("Semaforo RFM", "Lectura ejecutiva para proteger, recuperar y priorizar clientes.", ["RFM", "Accion"])
        rfm_cols = st.columns(4)
        for index, col in enumerate(rfm_cols):
            with col:
                _rfm_card(summary, SEGMENT_ORDER[index])

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    left, right = st.columns([.86, 1.14])
    with left:
        with st.container(border=True):
            _client_chart_header("Ranking de clientes con tendencia", "Comparativo de ventas entre los dos ultimos anios filtrados.", ["Tendencia"])
            trend = _trend_table(filtered)
            if trend.empty:
                st.info("Se requieren al menos dos anios en el filtro para calcular tendencia.")
            else:
                view = trend.copy()
                for column in view.columns:
                    if column.startswith("Ventas"):
                        view[column] = view[column].map(_format_number)
                st.dataframe(view, hide_index=True, use_container_width=True)
    with right:
        with st.container(border=True):
            _client_chart_header("Concentracion Pareto", "Barras de participacion y linea acumulada de ventas.", ["Top clientes"])
            st.plotly_chart(_pareto_chart(summary), use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    top_customers = summary.head(10)["Channel"].tolist()
    selected_line = st.multiselect(
        "Clientes para evolucion trimestral",
        summary["Channel"].tolist(),
        default=top_customers[:5],
        key="clients_quarterly_customers",
    )

    with st.container(border=True):
        _client_chart_header("Evolucion trimestral", "Lineas por cliente para ver quien sube y quien baja.", ["Trimestre"])
        st.plotly_chart(_quarterly_chart(monthly, selected_line or top_customers[:5]), use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        top_product, top_product_sales = _top_product(filtered)
        top_product_label = _short_label(top_product, 58) if top_product else "Sin producto"
        _client_chart_header(
            "Mapa de calor Cliente x Producto",
            f"Producto mas vendido del filtro: {top_product_label} ({_format_number(top_product_sales)} ventas).",
            ["Producto top"],
        )
        st.plotly_chart(_heatmap(filtered, summary), use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        _client_chart_header("Ficha individual por cliente", "Detalle ejecutivo para la conversacion comercial.", ["Cliente"])
        selected_customer = st.selectbox("Selecciona cliente", summary["Channel"].tolist(), key="clients_profile")
        _client_profile(filtered, summary, selected_customer)
