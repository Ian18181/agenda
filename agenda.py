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

# El resto del código permanece igual...
[El código continúa exactamente igual que en la versión anterior desde la función read_google_sheets() hasta el final]
