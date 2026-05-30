# Samsung EDA Dashboard

Dashboard ejecutivo en Streamlit para analizar ventas, clientes, productos e inventario con enfoque EDA.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Datos

La app espera estos archivos en la raiz del proyecto:

- `df_mensual_limpio.csv`
- `df_panel_limpio.csv`

Los CSV se versionan con Git LFS porque `df_panel_limpio.csv` supera el limite normal de GitHub.
