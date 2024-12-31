import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Configuración de la página
st.set_page_config(page_title="Sistema de Agendamiento de Citas", layout="wide")

# Inicialización del estado de la aplicación
if 'citas' not in st.session_state:
    if os.path.exists('citas.json'):
        with open('citas.json', 'r') as f:
            st.session_state.citas = json.load(f)
    else:
        st.session_state.citas = []

def guardar_citas():
    with open('citas.json', 'w') as f:
        json.dump(st.session_state.citas, f)

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
                cita['fecha_hora'] for cita in st.session_state.citas
            ]
        ]
        
        if horas_disponibles:
            hora = st.selectbox("Hora disponible", horas_disponibles)
            fecha_hora = f"{fecha.isoformat()} {hora}"
            
            motivo = st.text_area("Motivo de la cita")
            
            if st.form_submit_button("Agendar Cita"):
                if nombre and email and motivo:
                    nueva_cita = {
                        "id": len(st.session_state.citas),
                        "nombre": nombre,
                        "email": email,
                        "fecha_hora": fecha_hora,
                        "motivo": motivo
                    }
                    
                    st.session_state.citas.append(nueva_cita)
                    guardar_citas()
                    st.success("¡Cita agendada con éxito!")
                else:
                    st.error("Por favor complete todos los campos")
        else:
            st.warning("No hay horas disponibles para la fecha seleccionada")

def ver_citas():
    st.header("Citas Agendadas")
    
    if st.session_state.citas:
        df = pd.DataFrame(st.session_state.citas)
        st.dataframe(df)
    else:
        st.info("No hay citas agendadas")

def cancelar_cita():
    st.header("Cancelar Cita")
    
    if st.session_state.citas:
        citas_dict = {
            f"{cita['nombre']} - {cita['fecha_hora']}": i 
            for i, cita in enumerate(st.session_state.citas)
        }
        
        cita_seleccionada = st.selectbox(
            "Seleccione la cita a cancelar",
            list(citas_dict.keys())
        )
        
        if st.button("Cancelar Cita"):
            indice = citas_dict[cita_seleccionada]
            st.session_state.citas.pop(indice)
            guardar_citas()
            st.success("Cita cancelada con éxito")
    else:
        st.info("No hay citas para cancelar")

if __name__ == "__main__":
    main()