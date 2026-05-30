import plotly.graph_objects as go
import streamlit as st

from app.charts import bar_chart, donut_chart, plotly_layout, smooth_line_chart
from app.components import card_end, card_start, kpi_card
from app.config import COLORS
from app.data import executive_kpis, inventory, months, product_families, quarterly, rfm_customers, sales_evolution


def render_team():
    members = [
        {"name": "Brayan Garcia Torres", "place": "Guataca, Mompos"},
        {"name": "Juan Carlos Pastas Palencia", "place": "Popayan, Cauca"},
        {"name": "Juan Diego ", "place": "Lugar por definir"},
        {"name": "Michell Pulistar", "place": "Cali, Valle del Cauca"},
    ]

    member_cards = "".join(
        f'<div class="team-member-card"><div class="team-member-name">{member["name"]}</div>'
        f'<div class="team-member-place">{member["place"]}</div></div>'
        for member in members
    )
    st.markdown(
        f"""
        <div class="team-grid">
            {member_cards}
        </div>
        """,
        unsafe_allow_html=True,
    )
