import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# Configuración de Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1nlsu-q7RTwYkVH8oiGUCA7ij2ZCA14i2YMZWLZYfHps'
RANGE_NAME = 'Hoja 1!A:E'

@st.cache_resource
def get_google_sheets_service():
    # Cargar las credenciales desde el archivo
    with open('credential.json', 'r') as f:
        creds_info = json.load(f)
    
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )
    
    service = build('sheets', 'v4', credentials=credentials)
    return service

def read_google_sheets():
    try:
        service = get_google_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        
        if not values:
            return []
            
        # Convertir a DataFrame y luego a lista de diccionarios
        df = pd.DataFrame(values[1:], columns=values[0])
        return df.to_dict('records')
    except HttpError as err:
        st.error(f"Error al leer Google Sheets: {err}")
        return []

def write_to_google_sheets(cita):
    try:
        service = get_google_sheets_service()
        sheet = service.spreadsheets()
        
        values = [[
            cita['id'],
            cita['nombre'],
            cita['email'],
            cita['fecha_hora'],
            cita['motivo']
        ]]
        
        body = {
            'values': values
        }
        
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return True
    except HttpError as err:
        st.error(f"Error al escribir en Google Sheets: {err}")
        return False

def delete_from_google_sheets(index):
    try:
        service = get_google_sheets_service()
        sheet = service.spreadsheets()
        
        # Leer datos actuales
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        
        # Eliminar la fila correspondiente
        if len(values) > index + 1:  # +1 por la fila de encabezados
            values.pop(index + 1)
            
            # Limpiar todo el rango y escribir los nuevos valores
            sheet.values().clear(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            
            body = {
                'values': values
            }
            
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
    except HttpError as err:
        st.error(f"Error al eliminar de Google Sheets: {err}")
        return False

def main():
    st.title("📅 Sistema de Agendamiento de Citas")
    
    # Sidebar para navegación
    menu = st.sidebar.selectbox(
        "Menú",
        ["Agendar Cita", "Ver Citas", "Cancelar Cita"]
    )
    
    if menu == "Agendar Cita":
        agendar_cita()
    elif menu == "Ver Citas":
        ver_citas()
    else:
        cancelar_cita()

def agendar_cita():
    st.header("Agendar Nueva Cita")
    
    # Obtener citas existentes
    citas = read_google_sheets()
    
    # Formulario para nueva cita
    with st.form("nueva_cita"):
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Correo electrónico")
        
        # Selector de fecha
        fecha = st.date_input(
            "Fecha de la cita",
            min_value=datetime.now().date(),
            max_value=datetime.now().date() + timedelta(days=30)
        )
        
        # Selector de hora
        horas_disponibles = [
            f"{h:02d}:00" for h in range(9, 18)
            if f"{fecha.isoformat()} {h:02d}:00" not in [
                cita['fecha_hora'] for cita in citas
            ]
        ]
        
        if horas_disponibles:
            hora = st.selectbox("Hora disponible", horas_disponibles)
            fecha_hora = f"{fecha.isoformat()} {hora}"
            
            motivo = st.text_area("Motivo de la cita")
            
            if st.form_submit_button("Agendar Cita"):
                if nombre and email and motivo:
                    nueva_cita = {
                        "id": str(len(citas) + 1),
                        "nombre": nombre,
                        "email": email,
                        "fecha_hora": fecha_hora,
                        "motivo": motivo
                    }
                    
                    if write_to_google_sheets(nueva_cita):
                        st.success("¡Cita agendada con éxito!")
                    else:
                        st.error("Error al agendar la cita")
                else:
                    st.error("Por favor complete todos los campos")
        else:
            st.warning("No hay horas disponibles para la fecha seleccionada")

def ver_citas():
    st.header("Citas Agendadas")
    
    citas = read_google_sheets()
    if citas:
        df = pd.DataFrame(citas)
        st.dataframe(df)
    else:
        st.info("No hay citas agendadas")

def cancelar_cita():
    st.header("Cancelar Cita")
    
    citas = read_google_sheets()
    if citas:
        citas_dict = {
            f"{cita['nombre']} - {cita['fecha_hora']}": i 
            for i, cita in enumerate(citas)
        }
        
        cita_seleccionada = st.selectbox(
            "Seleccione la cita a cancelar",
            list(citas_dict.keys())
        )
        
        if st.button("Cancelar Cita"):
            indice = citas_dict[cita_seleccionada]
            if delete_from_google_sheets(indice):
                st.success("Cita cancelada con éxito")
            else:
                st.error("Error al cancelar la cita")
    else:
        st.info("No hay citas para cancelar")

if __name__ == "__main__":
    main()
