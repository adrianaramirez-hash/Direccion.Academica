import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1e-Zr56_EzGqNOdl1msgidEtpL_DZhJrzMKwwiyz6Bnk"


def conectar_google():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account_json"],
        scopes=scope
    )

    return gspread.authorize(creds)


@st.cache_data(ttl=300)
def cargar_hoja(nombre_hoja):
    gc = conectar_google()

    archivo = gc.open_by_key(SHEET_ID)

    hoja = archivo.worksheet(nombre_hoja)

    datos = hoja.get_all_records()

    return pd.DataFrame(datos)


@st.cache_data(ttl=300)
def cargar_kpis():
    return cargar_hoja("KPIS")


@st.cache_data(ttl=300)
def cargar_comentarios():
    return cargar_hoja("COMENTARIOS_ABIERTOS")


@st.cache_data(ttl=300)
def cargar_analisis_comentarios():
    return cargar_hoja("ANALISIS_COMENTARIOS")


def filtrar_dataframe(df, anio, modalidad, carrera):

    df_filtrado = df.copy()

    if "ANIO_ESCOLAR" in df_filtrado.columns and anio != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["ANIO_ESCOLAR"].astype(str) == anio
        ]

    if "MODALIDAD" in df_filtrado.columns and modalidad != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["MODALIDAD"].astype(str).str.upper() == modalidad.upper()
        ]

    if "SERVICIO_PROCEDENCIA" in df_filtrado.columns and carrera != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["SERVICIO_PROCEDENCIA"].astype(str) == carrera
        ]

    return df_filtrado
