import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.charts import plotly_layout
from app.components import card_end, card_start, kpi_card
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


def _short_label(value, limit=34):
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
    current = df[df["anio"].eq(max_year)].groupby("familia")["cust_sales"].sum()
    previous = df[df["anio"].eq(prev_year)].groupby("familia")["cust_sales"].sum()
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
    total_sales = summary["ventas"].sum()
    summary["share"] = summary["ventas"] / total_sales * 100 if total_sales else 0
    summary["acumulado"] = summary["share"].cumsum()
    return summary


def _product_summary(monthly, panel):
    latest_week = panel["fecha"].max()
    latest_inventory = (
        panel[panel["fecha"].eq(latest_week)]
        .groupby("Material Description", as_index=False)["channel_inv"]
        .sum()
        .rename(columns={"channel_inv": "inventario_actual"})
    )
    weekly_sales = (
        panel.groupby(["fecha", "Material Description"], as_index=False)["cust_sales"]
        .sum()
        .sort_values("fecha")
    )
    recent_weeks = sorted(weekly_sales["fecha"].drop_duplicates())[-8:]
    recent_sales = (
        weekly_sales[weekly_sales["fecha"].isin(recent_weeks)]
        .groupby("Material Description", as_index=False)["cust_sales"]
        .sum()
        .rename(columns={"cust_sales": "ventas_8w"})
    )
    products = (
        monthly.groupby("Material Description", as_index=False)
        .agg(familia=("familia", "first"), ventas=("cust_sales", "sum"), sell_in=("sell_in", "sum"))
    )
    max_year = int(monthly["anio"].max())
    prev_year = max_year - 1
    current = monthly[monthly["anio"].eq(max_year)].groupby("Material Description")["cust_sales"].sum()
    previous = monthly[monthly["anio"].eq(prev_year)].groupby("Material Description")["cust_sales"].sum()
    products = products.merge(current.rename("ventas_actual"), on="Material Description", how="left")
    products = products.merge(previous.rename("ventas_previa"), on="Material Description", how="left")
    products = products.merge(recent_sales, on="Material Description", how="left")
    products = products.merge(latest_inventory, on="Material Description", how="left")
    products[["ventas_actual", "ventas_previa", "ventas_8w", "inventario_actual"]] = products[
        ["ventas_actual", "ventas_previa", "ventas_8w", "inventario_actual"]
    ].fillna(0)
    products["crecimiento"] = _safe_divide(products["ventas_actual"] - products["ventas_previa"], products["ventas_previa"]) * 100
    products["sell_through"] = _safe_divide(products["ventas"], products["sell_in"]) * 100
    products["ventas_sem"] = products["ventas_8w"] / max(len(recent_weeks), 1)
    products["cobertura"] = _safe_divide(products["inventario_actual"], products["ventas_sem"])
    return products.sort_values("ventas", ascending=False)


def _tone_for_sell_through(value):
    if pd.isna(value) or value < 30:
        return "red"
    if value < 50:
        return "yellow"
    return "green"


def _pareto_chart(summary):
    top = summary.head(12).copy()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=top["familia"],
            y=top["share"],
            name="Participacion ventas",
            marker_color=COLORS["violet"],
            text=top["share"].map(lambda value: f"{value:.1f}%"),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Share: %{y:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=top["familia"],
            y=top["acumulado"],
            name="Acumulado",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color=COLORS["sky"], width=3),
            marker=dict(size=7),
            hovertemplate="<b>%{x}</b><br>Acumulado: %{y:.1f}%<extra></extra>",
        )
    )
    fig.update_traces(marker=dict(cornerradius=7), selector=dict(type="bar"))
    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right", range=[0, 105], ticksuffix="%", showgrid=False),
        yaxis=dict(ticksuffix="%", title_text="Participacion"),
    )
    fig.update_xaxes(tickangle=-25)
    return plotly_layout(fig, height=420, show_legend=True)


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
                marker=dict(
                    size=(subset["share"].clip(lower=1, upper=28) * 1.8) + 10,
                    color=colors[quadrant],
                    opacity=.86,
                    line=dict(color="#ffffff", width=1),
                ),
                text=subset["familia"],
                textposition="middle right",
                customdata=subset[["crecimiento", "ventas"]],
                hovertemplate="<b>%{text}</b><br>Crecimiento: %{customdata[0]:.1f}%<br>Share: %{y:.1f}%<br>Ventas: %{customdata[1]:,.0f}<extra></extra>",
            )
        )
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8")
    fig.add_hline(y=share_threshold, line_dash="dash", line_color="#94a3b8")
    fig.update_xaxes(title_text="Crecimiento 2024 a 2025", ticksuffix="%", range=[-90, 140])
    fig.update_yaxes(title_text="Share de ventas", ticksuffix="%", range=[0, max(70, data["share"].max() * 1.12)])
    return plotly_layout(fig, height=470, show_legend=True)


def _sell_through_chart(summary):
    data = summary.sort_values("sell_through", ascending=False).head(14).copy()
    fig = go.Figure(
        go.Bar(
            x=data["sell_through"].fillna(0),
            y=data["familia"],
            orientation="h",
            marker_color=[COLORS[_tone_for_sell_through(value)] for value in data["sell_through"]],
            text=data["sell_through"].map(_format_percent),
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Sell-through: %{x:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_xaxes(title_text="Ventas consumidor / despacho", ticksuffix="%")
    return plotly_layout(fig, height=430)


def _seasonality_chart(df, family):
    scoped = df[df["familia"].eq(family)]
    monthly = scoped.groupby(["anio", "mes"], as_index=False)["cust_sales"].sum()
    fig = go.Figure()
    palette = [COLORS["violet"], COLORS["sky"], COLORS["green"], COLORS["yellow"]]
    for index, year in enumerate(sorted(monthly["anio"].drop_duplicates())):
        subset = monthly[monthly["anio"].eq(year)].set_index("mes").reindex(range(1, 13), fill_value=0).reset_index()
        fig.add_trace(
            go.Scatter(
                x=subset["mes"],
                y=subset["cust_sales"],
                name=str(year),
                mode="lines+markers",
                line=dict(color=palette[index % len(palette)], width=3, shape="spline", smoothing=1.1),
                marker=dict(size=7),
            )
        )
    fig.update_xaxes(title_text="Mes", tickmode="array", tickvals=list(range(1, 13)))
    fig.update_yaxes(title_text="Ventas")
    return plotly_layout(fig, height=390, show_legend=True)


def _seasonality_message(df, family):
    scoped = df[df["familia"].eq(family)]
    by_month = scoped.groupby("mes")["cust_sales"].sum()
    if by_month.empty or by_month.mean() == 0:
        return "No hay datos suficientes para leer estacionalidad."
    top_months = by_month.sort_values(ascending=False).head(2).index.tolist()
    peak_ratio = by_month.max() / by_month.mean()
    months = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
    if peak_ratio < 1.25:
        return f"{family} no muestra estacionalidad fuerte; planifique despacho estable."
    return f"{family} concentra picos en {months[top_months[0]]} y {months[top_months[1]]}; anticipe inventario un mes antes."


def _stockout_table(products):
    table = products[(products["ventas_sem"] > 0) & (products["cobertura"] < 1)].copy()
    table = table.sort_values(["cobertura", "ventas_sem"], ascending=[True, False]).head(30)
    table = table.rename(
        columns={
            "Material Description": "Producto",
            "ventas_sem": "Ventas/sem",
            "inventario_actual": "Inv actual",
            "cobertura": "Cobertura",
        }
    )
    return table[["Producto", "familia", "Ventas/sem", "Inv actual", "Cobertura"]]


def _overstock_table(products):
    table = products[(products["inventario_actual"] > 0) & (products["cobertura"] > 12)].copy()
    table = table.sort_values("cobertura", ascending=False).head(30)

    def action(coverage):
        if coverage >= 52:
            return "Descontinuar"
        if coverage >= 26:
            return "Liquidar"
        return "Reducir despacho"

    table["Accion"] = table["cobertura"].map(action)
    table = table.rename(
        columns={
            "Material Description": "Producto",
            "inventario_actual": "Inv actual",
            "cobertura": "Cobertura",
        }
    )
    return table[["Producto", "familia", "Inv actual", "Cobertura", "Accion"]]


def _heatmap_chart(df):
    top_products = df.groupby("Material Description")["cust_sales"].sum().sort_values(ascending=False).head(10).index.tolist()
    top_customers = df.groupby("Channel")["cust_sales"].sum().sort_values(ascending=False).head(10).index.tolist()
    matrix = (
        df[df["Material Description"].isin(top_products) & df["Channel"].isin(top_customers)]
        .groupby(["Material Description", "Channel"])["cust_sales"]
        .sum()
        .unstack(fill_value=0)
        .reindex(index=top_products, columns=top_customers, fill_value=0)
    )
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=[_short_label(product, 30) for product in matrix.index],
            colorscale=[[0, "#f8fafc"], [.35, "#bfdbfe"], [.7, "#38bdf8"], [1, "#7c3aed"]],
            colorbar=dict(title="Ventas"),
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    fig.update_xaxes(tickangle=-25)
    return plotly_layout(fig, height=470)


def _display_table(df, numeric_columns):
    view = df.copy()
    for column in numeric_columns:
        if column in view.columns:
            view[column] = view[column].map(lambda value: f"{value:,.1f}" if column == "Cobertura" else _format_number(value))
    st.dataframe(view, hide_index=True, use_container_width=True)


def render_productos():
    mensual = _prepare_mensual(load_df_mensual())
    panel = _prepare_panel(load_df_panel())
    family_summary = _family_summary(mensual)
    product_summary = _product_summary(mensual, panel)

    total_products = product_summary["Material Description"].nunique()
    growing_products = product_summary[(product_summary["crecimiento"] >= 20) & (product_summary["ventas_actual"] > 0)]
    dying_products = product_summary[(product_summary["crecimiento"] <= -20) & (product_summary["ventas_previa"] > 0)]
    avg_sell_through = family_summary["sell_through"].dropna().mean()
    sell_tone = _tone_for_sell_through(avg_sell_through)

    cols = st.columns(4)
    with cols[0]:
        kpi_card("Total Productos", _format_number(total_products), "Productos unicos en CSV", "Catalogo", "sky", [])
    with cols[1]:
        kpi_card("Productos Creciendo", _format_number(len(growing_products)), "Crecen >= 20% vs anio previo", "Crecen", "green", [])
    with cols[2]:
        kpi_card("Productos Muriendo", _format_number(len(dying_products)), "Caen <= -20% vs anio previo", "Riesgo", "red", [])
    with cols[3]:
        kpi_card("Sell-Through Promedio", _format_percent(avg_sell_through), "Ventas / despacho", "Control", sell_tone, [])

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        card_start("Ranking por familia - Pareto", "Barras de participacion y linea acumulada de ventas")
        st.plotly_chart(_pareto_chart(family_summary), use_container_width=True, config={"displayModeBar": False})
        top_family = family_summary.iloc[0]
        top5_share = family_summary.head(5)["share"].sum()
        st.markdown(
            f'<div class="metric-row"><span><b>{top_family["familia"]}</b> domina con '
            f'{top_family["share"]:.1f}% de las ventas y cambia {_format_percent(top_family["crecimiento"])} vs anio previo. '
            f'Top 5 = {top5_share:.1f}% de todas las ventas.</span></div>',
            unsafe_allow_html=True,
        )
        card_end()

    left, right = st.columns([1.1, .9])
    with left:
        with st.container(border=True):
            card_start("Matriz de ciclo de vida", "Eje X crecimiento 2024 a 2025 | Eje Y share de ventas | Top 15 familias")
            st.plotly_chart(_lifecycle_chart(family_summary), use_container_width=True, config={"displayModeBar": False})
            card_end()
    with right:
        with st.container(border=True):
            card_start("Sell-Through por familia", "Semaforo: verde >= 50%, amarillo 30% a 50%, rojo < 30%")
            st.plotly_chart(_sell_through_chart(family_summary), use_container_width=True, config={"displayModeBar": False})
            mobile = family_summary[family_summary["familia"].str.upper().eq("MOBILE")]
            if not mobile.empty and pd.notna(mobile.iloc[0]["sell_through"]):
                ratio = 100 / mobile.iloc[0]["sell_through"] if mobile.iloc[0]["sell_through"] else 0
                st.markdown(
                    f'<div class="metric-row"><span><b>MOBILE:</b> se despachan {ratio:.1f} unidades por cada 1 vendida al consumidor.</span></div>',
                    unsafe_allow_html=True,
                )
            card_end()

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        card_start("Estacionalidad por producto", "Seleccione una familia para comparar 2023, 2024 y 2025")
        family_options = family_summary["familia"].tolist()
        selected_family = st.selectbox("Familia de producto", family_options, key="products_seasonality_family")
        st.plotly_chart(_seasonality_chart(mensual, selected_family), use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div class="metric-row"><span>{_seasonality_message(mensual, selected_family)}</span></div>', unsafe_allow_html=True)
        card_end()

    stockout = _stockout_table(product_summary)
    overstock = _overstock_table(product_summary)
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            card_start("Top productos en riesgo de stockout", "Ventas recientes con cobertura menor a 1 semana")
            if stockout.empty:
                st.info("No hay productos con cobertura menor a 1 semana.")
            else:
                _display_table(stockout, ["Ventas/sem", "Inv actual", "Cobertura"])
                st.download_button(
                    "Exportar lista para reposicion",
                    stockout.to_csv(index=False).encode("utf-8"),
                    "productos_reposicion.csv",
                    "text/csv",
                    use_container_width=True,
                )
            card_end()
    with right:
        with st.container(border=True):
            card_start("Top productos en sobrestock", "Cobertura mayor a 12 semanas")
            if overstock.empty:
                st.info("No hay productos con sobrestock bajo el criterio actual.")
            else:
                _display_table(overstock, ["Inv actual", "Cobertura"])
            card_end()

    with st.container(border=True):
        card_start("Mapa de calor - Producto x Cliente", "Top 10 productos contra Top 10 clientes por ventas totales")
        st.plotly_chart(_heatmap_chart(mensual), use_container_width=True, config={"displayModeBar": False})
        card_end()
