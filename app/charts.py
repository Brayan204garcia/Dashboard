import plotly.graph_objects as go

from app.config import COLORS


def plotly_layout(fig, height=320, show_legend=False):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", color=COLORS["muted"]),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, zeroline=False, color=COLORS["muted"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, color=COLORS["muted"])
    return fig


def smooth_line_chart(series, labels, height=320, show_markers=False):
    fig = go.Figure()
    for item in series:
        fig.add_trace(
            go.Scatter(
                x=labels,
                y=item["values"],
                name=item["name"],
                mode="lines+markers" if show_markers else "lines",
                line=dict(color=item["color"], width=item.get("width", 3), shape="spline", smoothing=1.25),
                fill=item.get("fill"),
                fillcolor=item.get("fillcolor"),
            )
        )
    return plotly_layout(fig, height=height, show_legend=True)


def bar_chart(categories, values, color=COLORS["violet"], height=310):
    fig = go.Figure(go.Bar(x=categories, y=values, marker_color=color, marker_line_width=0))
    fig.update_traces(marker=dict(cornerradius=6))
    return plotly_layout(fig, height=height)


def donut_chart(labels, values, colors, height=300):
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=.72,
            marker=dict(colors=colors),
            textinfo="label+percent",
        )
    )
    return plotly_layout(fig, height=height, show_legend=False)
