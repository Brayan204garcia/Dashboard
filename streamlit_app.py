import streamlit as st

from app.layout import render_sidebar, render_topbar
from app.config import INITIAL_SIDEBAR_STATE, LAYOUT, PAGE_ICON, PAGE_TITLE
from app.pages import render_clientes, render_inventario, render_predicciones, render_productos, render_resumen, render_team
from app.styles import inject_css


st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
)


def main():
    inject_css()
    page = render_sidebar()
    render_topbar(page)

    if page == "Resumen ejecutivo":
        render_resumen()
    elif page == "Clientes":
        render_clientes()
    elif page == "Productos":
        render_productos()
    elif page == "Inventario":
        render_inventario()
    elif page == "Predicciones":
        render_predicciones()
    else:
        render_team()


if __name__ == "__main__":
    main()
