import streamlit as st
import pandas as pd
import streamlit as st
import pandas as pd
import datetime
import os
from PIL import Image
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ----------------- CONFIGURACIÓN -----------------
st.set_page_config(page_title="Ciencia Ciudadana Marina", layout="centered")
PASSWORD   = "océano2025"                    # Cambia si lo deseas
IMAGES_DIR = "fotos"                         # Carpeta local para fotos
COLS       = ["Especie", "Fecha", "Hora", "Latitud", "Longitud", "Comentario", "Foto"]

# ID de tu hoja de cálculo (lo que va entre /d/ y /edit en la URL)
SHEET_ID = "1Jr0JHfkOtX_48Df6F9WxKyRKAQpMqKoFx5Fr7ydMR-g"

# ----------------- AUTENTICACIÓN BÁSICA -----------------
st.title("🔒 Avistamientos Marinos – Acceso")
if st.text_input("Contraseña:", type="password") != PASSWORD:
    st.stop()

# ----------------- CONEXIÓN A GOOGLE SHEETS -----------------
@st.cache_resource(show_spinner=False, ttl=3600)
def conectar_google_sheets(json_keyfile:str, sheet_id:str):
    """Devuelve el objeto worksheet (hoja 1) y garantiza encabezados."""
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds  = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    sheet  = client.open_by_key(sheet_id).sheet1

    # Garantiza que la primera fila contenga los encabezados correctos
    encabezados = sheet.row_values(1)
    if encabezados != COLS:
        sheet.delete_row(1) if encabezados else None
        sheet.insert_row(COLS, 1)
    return sheet

try:
    sheet = conectar_google_sheets("credenciales.json", SHEET_ID)
except Exception as e:
    st.error(f"❌ No se pudo conectar con Google Sheets: {e}")
    st.stop()

# ----------------- UTILIDADES -----------------
def sheet_to_df(ws):
    """Convierte la hoja a DataFrame con las columnas correctas."""
    registros = ws.get_all_records()
    return pd.DataFrame(registros, columns=COLS) if registros else pd.DataFrame(columns=COLS)

def save_row_to_sheet(row_df, ws):
    """Añade una fila a la hoja."""
    ws.append_row(row_df.iloc[0].astype(str).tolist())

# Carpeta local para fotos
os.makedirs(IMAGES_DIR, exist_ok=True)

# ----------------- CARGAR DATOS EXISTENTES -----------------
df = sheet_to_df(sheet)

# ----------------- FORMULARIO -----------------
st.header("📋 Nuevo Avistamiento")
with st.form("formulario"):
    especie = st.selectbox("Especie observada", ["Manta", "Mobula", "Ballena", "Orca", "Lobo marino", "Delfin nariz de botella", "Delfin comun", "Cachalote","Tiburon ballena", "Jorobada", "Ballena de aleta", "Ballena azul"])
    fecha   = st.date_input("Fecha", value=datetime.date.today())
    hora    = st.time_input("Hora", value=datetime.datetime.now().time())

    st.markdown("📍 Ingresa las coordenadas en decimales (latitud positiva norte, longitud negativa oeste).")
    lat = st.number_input("Latitud", format="%.6f")
    lon = st.number_input("Longitud", format="%.6f")

    comentario = st.text_area("Comentario (opcional)")
    foto_file  = st.file_uploader("📸 Sube una foto (opcional)", type=["jpg", "jpeg", "png"])

    enviar = st.form_submit_button("Enviar avistamiento")

    if enviar:
        # ---- Validaciones mínimas ----
        if lat == 0.0 or lon == 0.0:
            st.error("⚠️ Coordenadas no válidas (0.0).")
            st.stop()

        # ---- Guardar foto localmente si viene ----
        foto_path = ""
        if foto_file:
            ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            foto_name = f"{especie}_{ts}.jpg"
            foto_path = os.path.join(IMAGES_DIR, foto_name)
            with open(foto_path, "wb") as f:
                f.write(foto_file.read())

        # ---- Crear fila y guardar en Google Sheets ----
        nueva_fila = pd.DataFrame([[especie, fecha, hora, lat, lon, comentario, foto_path]], columns=COLS)
        try:
            save_row_to_sheet(nueva_fila, sheet)
            st.success("✅ Avistamiento registrado.")
            df = pd.concat([df, nueva_fila], ignore_index=True)
        except Exception as e:
            st.error(f"❌ No se pudo guardar en Google Sheets: {e}")

# ----------------- TABLA Y MAPA -----------------
st.subheader("🗒️ Registros actuales")
st.dataframe(df, use_container_width=True)

st.subheader("🗺️ Mapa de avistamientos")
if df.empty:
    st.info("Aún no hay registros.")
else:
    m = folium.Map(location=[df["Latitud"].mean(), df["Longitud"].mean()], zoom_start=6)
    mc = MarkerCluster().add_to(m)
    for _, r in df.iterrows():
        popup = (
            f"<b>{r['Especie']}</b><br>"
            f"{r['Fecha']} {r['Hora']}<br>"
            f"{r['Comentario'] or ''}"
        )
        folium.Marker([r["Latitud"], r["Longitud"]], tooltip=r["Especie"], popup=popup).add_to(mc)
    st_folium(m, use_container_width=True)
