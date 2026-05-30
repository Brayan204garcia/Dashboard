import html

import streamlit as st

from app.config import COLORS


def kpi_card(label, value, meta, trend, tone, values):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div style="display:flex;justify-content:space-between;gap:1rem;">
                <div class="kpi-title">{html.escape(label)}</div>
                <div style="display:flex;gap:.25rem;padding-top:.5rem;">
                    <span class="dot" style="background:#6b7280;margin:0;width:4px;height:4px;"></span>
                    <span class="dot" style="background:#6b7280;margin:0;width:4px;height:4px;"></span>
                    <span class="dot" style="background:#6b7280;margin:0;width:4px;height:4px;"></span>
                </div>
            </div>
            <div class="kpi-meta">{html.escape(meta)}</div>
            <div style="display:flex;align-items:center;gap:.75rem;">
                <div class="kpi-value">{html.escape(value)}</div>
                <span class="pill pill-{tone}">{html.escape(trend)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_start(title=None, eyebrow=None):
    if eyebrow:
        st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    if title:
        st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def card_end():
    return None
