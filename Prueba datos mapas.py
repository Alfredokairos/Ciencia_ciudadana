#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(page_title="Mapa Interactivo", layout="wide")

# Título y explicación
st.title("Mapa Interactivo de Zonas Coralinas")
st.markdown("""
Este mapa interactivo presenta distintas capas que muestran la distribución de corales, zonas de restauración, y áreas monitoreadas en la Bahía de La Paz.

### Cómo usar el mapa:
- Usa los controles en la esquina superior derecha para activar o desactivar capas.
- Haz zoom con el scroll o los botones del mapa.
- Haz clic en los marcadores para más detalles de cada punto.

Si tienes preguntas o quieres colaborar, contáctanos en [tu-email@ejemplo.com](mailto:tu-email@ejemplo.com).
""")
path = "I:/MARIS/CICESE_2022/Proyecto_cerralvo/Datos_entrevistas_mapas/"
# Leer el HTML del mapa y mostrarlo
with open("I:/MARIS/CICESE_2022/Proyecto_cerralvo/Datos_entrevistas_mapas/avistamiento_por_especie_final.html", "r", encoding="utf-8") as f:
    map_html = f.read()

# Insertar el mapa en la app
html(map_html, height=700, width=1200)


# In[ ]:




