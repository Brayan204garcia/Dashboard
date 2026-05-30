import streamlit as st

from app.config import PAGES


def render_topbar(page):
    brand_text = "Hola, Equipo Samsung Colombia" if page == "Resumen ejecutivo" else "Equipo AI Creators"
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand">{brand_text}</div>
            <div class="muted">AI CREATORS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <svg class="sidebar-logo" viewBox="0 0 32 32" aria-hidden="true">
                <path fill="currentColor" d="M31.956 14.8C31.372 6.92 25.08.628 17.2.044V5.76a9.04 9.04 0 0 0 9.04 9.04h5.716ZM14.8 26.24v5.716C6.92 31.372.63 25.08.044 17.2H5.76a9.04 9.04 0 0 1 9.04 9.04Zm11.44-9.04h5.716c-.584 7.88-6.876 14.172-14.756 14.756V26.24a9.04 9.04 0 0 1 9.04-9.04ZM.044 14.8C.63 6.92 6.92.628 14.8.044V5.76a9.04 9.04 0 0 1-9.04 9.04H.044Z"/>
            </svg>
            <div class="sidebar-title">AI CREATORS</div>
        </div>
        <div class="sidebar-pages">Menú</div>
        """,
        unsafe_allow_html=True,
    )
    return st.sidebar.radio(
        "Pages",
        PAGES,
        label_visibility="collapsed",
    )
