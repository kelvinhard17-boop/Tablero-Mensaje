import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

st.set_page_config(page_title="Tablero de Mensajes", page_icon="💬", layout="centered")

ARCHIVO_MENSAJES = "mensajes.csv"
ARCHIVO_USUARIOS = "usuarios.csv"
AVATARES = ["👤", "🤖", "🐱", "🐶", "🦁", "🦊", "👑", "🚀", "🔥", "⚽"]

# Helper para encriptar contraseñas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Helper para generar color único por nombre
def color_nombre(nombre):
    h = hashlib.md5(nombre.encode()).hexdigest()
    return f"#{h[:6]}"

# Inicializar archivos si no existen
if not os.path.exists(ARCHIVO_MENSAJES):
    pd.DataFrame(columns=["Fecha", "Usuario", "Avatar", "Mensaje"]).to_csv(ARCHIVO_MENSAJES, index=False)

if not os.path.exists(ARCHIVO_USUARIOS):
    pd.DataFrame(columns=["Usuario", "Password", "Avatar"]).to_csv(ARCHIVO_USUARIOS, index=False)

# Estado de sesión
if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None
if "avatar_logueado" not in st.session_state:
    st.session_state.avatar_logueado = "👤"

st.title("💬 Tablero de Mensajes")

# --- VISTA DE AUTENTICACIÓN (LOGIN / REGISTRO) ---
if st.session_state.usuario_logueado is None:
    st.write("Bienvenido. Inicia sesión o regístrate para interactuar.")
    pestana_login, pestana_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])

    df_usuarios = pd.read_csv(ARCHIVO_USUARIOS)

    # Tab 1: Iniciar Sesión
    with pestana_login:
        with st.form("form_login"):
            usr_input = st.text_input("Usuario:").strip()
            pass_input = st.text_input("Contraseña:", type="password").strip()
            btn_login = st.form_submit_button("Entrar 🚀")

            if btn_login:
                if not usr_input or not pass_input:
                    st.error("Por favor completa usuario y contraseña.")
                else:
                    user_match = df_usuarios[df_usuarios['Usuario'].astype(str).str.lower() == usr_input.lower()]
                    if not user_match.empty:
                        stored_pass = str(user_match.iloc[0]['Password'])
                        if stored_pass == hash_password(pass_input):
                            st.session_state.usuario_logueado = user_match.iloc[0]['Usuario']
                            st.session_state.avatar_logueado = user_match.iloc[0]['Avatar']
                            st.success(f"¡Bienvenido de nuevo, {st.session_state.usuario_logueado}!")
                            st.rerun()
                        else:
                            st.error("Contraseña incorrecta.")
                    else:
                        st.error("El usuario no existe. Por favor regístrate.")

    # Tab 2: Registrarse
    with pestana_registro:
        with st.form("form_registro"):
            nuevo_usr = st.text_input("Elige tu Nombre de Usuario:").strip()
            nuevo_pass = st.text_input("Elige tu Contraseña:", type="password").strip()
            nuevo_avatar = st.selectbox("Elige tu Avatar / Figurita:", AVATARES)
            btn_registro = st.form_submit_button("Crear Cuenta ✨")

            if btn_registro:
                if not nuevo_usr or not nuevo_pass:
                    st.error("Por favor completa todos los campos.")
                else:
                    if not df_usuarios.empty and nuevo_usr.lower() in df_usuarios['Usuario'].astype(str).str.lower().values:
                        st.error("Ese nombre de usuario ya está registrado. Elige otro.")
                    else:
                        pass_hashed = hash_password(nuevo_pass)
                        nuevo_registro = pd.DataFrame([{"Usuario": nuevo_usr, "Password": pass_hashed, "Avatar": nuevo_avatar}])
                        nuevo_registro.to_csv(ARCHIVO_USUARIOS, mode='a', header=False, index=False)
                        
                        st.session_state.usuario_logueado = nuevo_usr
                        st.session_state.avatar_logueado = nuevo_avatar
                        st.success("¡Cuenta creada con éxito!")
                        st.rerun()

    st.stop()  # Detiene la ejecución para que no cargue el chat si no está logueado

# --- VISTA PRINCIPAL DEL CHAT (USUARIO LOGUEADO) ---
col_user, col_logout = st.columns([3, 1])
with col_user:
    st.write(f"Sesión activa: **{st.session_state.avatar_logueado} {st.session_state.usuario_logueado}**")
with col_logout:
    if st.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None
        st.session_state.avatar_logueado = "👤"
        st.rerun()

# Formulario para publicar mensaje
with st.form("form_mensaje", clear_on_submit=True):
    mensaje = st.text_area("Mensaje:", placeholder="Escribe tu mensaje aquí...").strip()
    enviado = st.form_submit_button("Enviar Mensaje 🚀")

    if enviado:
        if not mensaje:
            st.error("El mensaje no puede estar vacío.")
        else:
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nuevo_df = pd.DataFrame([{
                "Fecha": ahora,
                "Usuario": st.session_state.usuario_logueado,
                "Avatar": st.session_state.avatar_logueado,
                "Mensaje": mensaje
            }])
            nuevo_df.to_csv(ARCHIVO_MENSAJES, mode='a', header=False, index=False)
            st.success("¡Mensaje enviado!")
            st.rerun()

st.divider()
st.subheader("📋 Historial de Mensajes")

if st.button("🔄 Actualizar Mensajes"):
    st.rerun()

if os.path.exists(ARCHIVO_MENSAJES):
    try:
        df = pd.read_csv(ARCHIVO_MENSAJES, on_bad_lines='skip')
        if df.empty:
            st.info("Aún no hay mensajes.")
        else:
            df = df.iloc[::-1]
            for _, fila in df.iterrows():
                icono = fila['Avatar'] if 'Avatar' in fila and pd.notna(fila['Avatar']) else "👤"
                usr = fila['Usuario'] if 'Usuario' in fila and pd.notna(fila['Usuario']) else "Anónimo"
                msg = fila['Mensaje'] if 'Mensaje' in fila and pd.notna(fila['Mensaje']) else ""
                fcha = fila['Fecha'] if 'Fecha' in fila and pd.notna(fila['Fecha']) else ""
                c = color_nombre(str(usr))
                
                with st.chat_message("user", avatar=icono):
                    html = f'<span style="color:{c}; font-weight:bold; font-size:1.1em;">{usr}</span> <span style="color:gray; font-size:0.85em;">({fcha})</span>'
                    st.markdown(html, unsafe_allow_html=True)
                    st.write(msg)
    except Exception as e:
        st.error(f"Error al cargar los mensajes: {e}")
else:
    st.info("Aún no hay mensajes.")