import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Tablero & Juego Emoji", page_icon="💬", layout="centered")

ARCHIVO_MENSAJES = "mensajes.csv"
ARCHIVO_USUARIOS = "usuarios.csv"
ARCHIVO_SCORES = "scores.csv"

AVATARES = ["👤", "🤖", "🐱", "🐶", "🦁", "🦊", "👑", "🚀", "🔥", "⚽"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def color_nombre(nombre):
    h = hashlib.md5(nombre.encode()).hexdigest()
    return f"#{h[:6]}"

# Inicializar archivos CSV si no existen
if not os.path.exists(ARCHIVO_MENSAJES):
    pd.DataFrame(columns=["Fecha", "Usuario", "Avatar", "Mensaje"]).to_csv(ARCHIVO_MENSAJES, index=False)

if not os.path.exists(ARCHIVO_USUARIOS):
    pd.DataFrame(columns=["Usuario", "Password", "Avatar"]).to_csv(ARCHIVO_USUARIOS, index=False)

if not os.path.exists(ARCHIVO_SCORES):
    pd.DataFrame(columns=["Usuario", "Puntaje", "Fecha"]).to_csv(ARCHIVO_SCORES, index=False)

# Estado de sesión
if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None
if "avatar_logueado" not in st.session_state:
    st.session_state.avatar_logueado = "👤"

st.title("💬 Tablero & Entretenimiento")

# --- VISTA DE AUTENTICACIÓN ---
if st.session_state.usuario_logueado is None:
    st.write("Inicia sesión o regístrate para chatear y jugar.")
    pestana_login, pestana_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])

    df_usuarios = pd.read_csv(ARCHIVO_USUARIOS)

    with pestana_login:
        with st.form("form_login"):
            usr_input = st.text_input("Usuario:").strip()
            pass_input = st.text_input("Contraseña:", type="password").strip()
            btn_login = st.form_submit_button("Entrar 🚀")

            if btn_login:
                if not usr_input or not pass_input:
                    st.error("Completa usuario y contraseña.")
                else:
                    user_match = df_usuarios[df_usuarios['Usuario'].astype(str).str.lower() == usr_input.lower()]
                    if not user_match.empty:
                        stored_pass = str(user_match.iloc[0]['Password'])
                        if stored_pass == hash_password(pass_input):
                            st.session_state.usuario_logueado = user_match.iloc[0]['Usuario']
                            st.session_state.avatar_logueado = user_match.iloc[0]['Avatar']
                            st.success(f"¡Bienvenido, {st.session_state.usuario_logueado}!")
                            st.rerun()
                        else:
                            st.error("Contraseña incorrecta.")
                    else:
                        st.error("El usuario no existe.")

    with pestana_registro:
        with st.form("form_registro"):
            nuevo_usr = st.text_input("Nombre de Usuario:").strip()
            nuevo_pass = st.text_input("Contraseña:", type="password").strip()
            nuevo_avatar = st.selectbox("Avatar / Figurita:", AVATARES)
            btn_registro = st.form_submit_button("Crear Cuenta ✨")

            if btn_registro:
                if not nuevo_usr or not nuevo_pass:
                    st.error("Completa todos los campos.")
                else:
                    if not df_usuarios.empty and nuevo_usr.lower() in df_usuarios['Usuario'].astype(str).str.lower().values:
                        st.error("El usuario ya existe.")
                    else:
                        pass_hashed = hash_password(nuevo_pass)
                        nuevo_registro = pd.DataFrame([{"Usuario": nuevo_usr, "Password": pass_hashed, "Avatar": nuevo_avatar}])
                        nuevo_registro.to_csv(ARCHIVO_USUARIOS, mode='a', header=False, index=False)
                        st.session_state.usuario_logueado = nuevo_usr
                        st.session_state.avatar_logueado = nuevo_avatar
                        st.success("¡Cuenta creada!")
                        st.rerun()
    st.stop()

# --- HEADER USUARIO ---
col_user, col_logout = st.columns([3, 1])
with col_user:
    st.write(f"Sesión activa: **{st.session_state.avatar_logueado} {st.session_state.usuario_logueado}**")
with col_logout:
    if st.button("Cerrar Sesión"):
        st.session_state.usuario_logueado = None
        st.session_state.avatar_logueado = "👤"
        st.rerun()

# --- PESTAÑAS PRINCIPALES: CHAT Y JUEGO ---
tab_chat, tab_juego, tab_leaderboard = st.tabs(["💬 Mensajes", "🎮 Emoji Bounce", "🏆 Tabla de Líderes"])

# === PESTAÑA 1: MENSAJES ===
with tab_chat:
    with st.form("form_mensaje", clear_on_submit=True):
        mensaje = st.text_area("Mensaje:", placeholder="Escribe tu mensaje...").strip()
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
            st.error(f"Error al cargar mensajes: {e}")

# === PESTAÑA 2: JUEGO EMOJI BOUNCE ===
with tab_juego:
    st.subheader("🎯 Rebota el Emoji")
    st.caption("Usa el mouse o desliza el dedo en la pantalla del teléfono para mover la plataforma.")

    # Guardar récord mediante formulario oculto/input
    if "nuevo_score" in st.query_params:
        puntos_obtenidos = int(st.query_params["nuevo_score"])
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevo_score_df = pd.DataFrame([{
            "Usuario": st.session_state.usuario_logueado,
            "Puntaje": puntos_obtenidos,
            "Fecha": ahora
        }])
        nuevo_score_df.to_csv(ARCHIVO_SCORES, mode='a', header=False, index=False)
        st.success(f"¡Puntaje registrado: {puntos_obtenidos} pts!")
        st.query_params.clear()
        st.rerun()

    # Juego en Canvas HTML5 / JS
    juego_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; text-align: center; background: #0e1117; color: white; font-family: sans-serif; touch-action: none; }}
            canvas {{ background: #161b22; border: 2px solid #30363d; border-radius: 10px; display: block; margin: 10px auto; }}
            button {{ background: #238636; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <canvas id="gameCanvas" width="320" height="400"></canvas>
        <button onclick="startGame()">▶️ Jugar / Reiniciar</button>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let emoji = "{st.session_state.avatar_logueado}";
            let x, y, dx, dy, paddleX, score, gameRunning;
            const paddleHeight = 12, paddleWidth = 75;

            function startGame() {{
                x = canvas.width / 2;
                y = canvas.height - 50;
                dx = 3;
                dy = -3;
                paddleX = (canvas.width - paddleWidth) / 2;
                score = 0;
                gameRunning = true;
                draw();
            }}

            document.addEventListener("mousemove", (e) => {{
                let rect = canvas.getBoundingClientRect();
                let relativeX = e.clientX - rect.left;
                if(relativeX > 0 && relativeX < canvas.width) {{
                    paddleX = relativeX - paddleWidth / 2;
                }}
            }});

            document.addEventListener("touchmove", (e) => {{
                let rect = canvas.getBoundingClientRect();
                let relativeX = e.touches[0].clientX - rect.left;
                if(relativeX > 0 && relativeX < canvas.width) {{
                    paddleX = relativeX - paddleWidth / 2;
                }}
            }});

            function draw() {{
                if (!gameRunning) return;
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Dibujar Emoji
                ctx.font = "24px serif";
                ctx.fillText(emoji, x - 12, y + 8);

                // Dibujar Plataforma
                ctx.fillStyle = "#58a6ff";
                ctx.fillRect(paddleX, canvas.height - paddleHeight - 5, paddleWidth, paddleHeight);

                // Dibujar Puntaje
                ctx.fillStyle = "#ffffff";
                ctx.font = "16px sans-serif";
                ctx.fillText("Puntos: " + score, 10, 25);

                // Colisiones paredes laterales
                if (x + dx > canvas.width - 12 || x + dx < 12) dx = -dx;
                // Colisión techo
                if (y + dy < 12) dy = -dy;

                // Colisión Plataforma
                if (y + dy > canvas.height - paddleHeight - 15) {{
                    if (x > paddleX && x < paddleX + paddleWidth) {{
                        dy = -dy * 1.05; // Incrementa velocidad gradualmente
                        score++;
                    }} else if (y + dy > canvas.height) {{
                        gameRunning = false;
                        alert("¡Juego Terminado! Tu puntaje: " + score);
                        window.parent.postMessage({{type: 'streamlit:setQueryParams', queryParams: {{nuevo_score: score}}}}, '*');
                        return;
                    }}
                }}

                x += dx;
                y += dy;
                requestAnimationFrame(draw);
            }}
        </script>
    </body>
    </html>
    """
    components.html(juego_html, height=480)

# === PESTAÑA 3: TABLA DE LÍDERES (LEADERBOARD) ===
with tab_leaderboard:
    st.subheader("🏆 Máximos Puntajes")
    if os.path.exists(ARCHIVO_SCORES):
        df_scores = pd.read_csv(ARCHIVO_SCORES)
        if df_scores.empty:
            st.info("Aún no hay récords registrados. ¡Sé el primero en jugar!")
        else:
            # Obtener el puntaje máximo por usuario
            top_scores = df_scores.groupby("Usuario")["Puntaje"].max().reset_index()
            top_scores = top_scores.sort_values(by="Puntaje", ascending=False).reset_index(drop=True)
            top_scores.index += 1  # Ranking inicia en 1
            
            # Formatear tabla
            st.table(top_scores.rename(columns={"Usuario": "Jugador 👤", "Puntaje": "Puntos Máximos 🎯"}))
    else:
        st.info("Aún no hay récords registrados.")
