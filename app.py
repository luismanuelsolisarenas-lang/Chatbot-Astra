import streamlit as st
from google import genai
from google.genai import types
import time

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==============================================================================

st.set_page_config(
    page_title="Asistente AI - Sistemas Inteligentes",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Asistente Virtual 'Astra'")

st.caption(
    "UAdeO • Materia: Sistemas Inteligentes • "
    "Dra. Aiblis Susej Herrera Palafox"
)

# ==============================================================================
# 2. GESTIÓN SEGURA DE LA API KEY
# ==============================================================================

try:
    api_key = st.secrets["GEMINI_API_KEY"]

    if not api_key:
        st.error("❌ La API Key está vacía.")
        st.stop()

except Exception:
    st.error(
        "❌ No se encontró la API Key de Gemini. "
        "Verifica el archivo .streamlit/secrets.toml"
    )
    st.stop()

# ==============================================================================
# 3. CONFIGURACIÓN DE PERSONALIDAD DEL BOT
# ==============================================================================

CONFIG_INSTRUCCIONES = types.GenerateContentConfig(
    system_instruction=(
        "Eres 'Astra', un asistente académico inteligente, "
        "formal y estructurado para la materia "
        "Sistemas Inteligentes de la UAdeO. "

        "Tu objetivo es explicar conceptos de Inteligencia Artificial, "
        "Agentes Inteligentes y Redes Neuronales "
        "de forma clara y accesible. "

        "Responde de manera amable, educativa y profesional. "

        "Cuando expliques conceptos complejos, utiliza ejemplos "
        "sencillos para facilitar el aprendizaje. "

        "Si te preguntan por entregas, tareas o fechas, "
        "indica amablemente que deben verificar las indicaciones "
        "de la Dra. Aiblis Susej Herrera Palafox."
    ),
    temperature=0.7
)

# ==============================================================================
# 4. CONFIGURACIÓN DEL MODELO DE GEMINI
# ==============================================================================

MODELO = "gemini-3.8-flash"

# ==============================================================================
# 5. INICIALIZACIÓN DEL CLIENTE Y MEMORIA
# ==============================================================================

if (
    "client" not in st.session_state
    or st.session_state.get("current_api_key") != api_key
):

    st.session_state.client = genai.Client(
        api_key=api_key
    )

    st.session_state.current_api_key = api_key

    st.session_state.chat_session = (
        st.session_state.client.chats.create(
            model=MODELO,
            config=CONFIG_INSTRUCCIONES
        )
    )

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 ¡Hola! Soy Astra, tu asistente académico "
                "de Sistemas Inteligentes. "
                "¿En qué puedo ayudarte hoy?"
            )
        }
    ]

# ==============================================================================
# 6. HISTORIAL DE MENSAJES
# ==============================================================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 ¡Hola! Soy Astra. "
                "¿En qué tema de Sistemas Inteligentes "
                "te puedo ayudar hoy?"
            )
        }
    ]

# ==============================================================================
# 7. BARRA LATERAL
# ==============================================================================

with st.sidebar:

    st.header("⚙️ Opciones del Agente")

    st.markdown("### 🤖 Información del chatbot")

    st.write("Nombre: Astra")

    st.write("Materia: Sistemas Inteligentes")

    st.write("Universidad: UAdeO")

    st.markdown(f"Modelo backend: **{MODELO}**")

    st.divider()

    st.subheader("💬 Conversación")

    if st.button(
        "🧹 Limpiar Conversación",
        use_container_width=True
    ):

        st.session_state.chat_session = (
            st.session_state.client.chats.create(
                model=MODELO,
                config=CONFIG_INSTRUCCIONES
            )
        )

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "🧹 La conversación ha sido reiniciada. "
                    "¿Qué otra duda tienes?"
                )
            }
        ]

        st.rerun()

    st.divider()

    st.caption(
        "Proyecto académico desarrollado con "
        "Python, Streamlit y Gemini API."
    )

# ==============================================================================
# 8. MOSTRAR HISTORIAL DE CONVERSACIÓN
# ==============================================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ==============================================================================
# 9. ENTRADA DE TEXTO DEL USUARIO
# ==============================================================================

if user_input := st.chat_input(
    "Escribe tu pregunta o duda aquí..."
):

    # Guardar mensaje del usuario
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Mostrar mensaje del usuario
    with st.chat_message("user"):

        st.markdown(user_input)

    # ======================================================================
    # 10. GENERAR RESPUESTA CON GEMINI
    # ======================================================================

    with st.chat_message("assistant"):

        with st.spinner("🤖 Astra está pensando..."):

            try:

                respuesta = None

                # Intentar hasta 3 veces si Gemini está saturado
                for intento in range(3):

                    try:

                        response = (
                            st.session_state.chat_session.send_message(
                                user_input
                            )
                        )

                        respuesta = response.text

                        # Si Gemini respondió, salir del ciclo
                        break

                    except Exception as e:

                        error = str(e)

                        # Detectar error de saturación 503
                        if "503" in error or "UNAVAILABLE" in error:

                            if intento < 2:

                                st.warning(
                                    "⏳ Gemini está saturado. "
                                    f"Reintentando conexión "
                                    f"({intento + 1}/2)..."
                                )

                                # Esperar antes de reintentar
                                time.sleep(5 * (intento + 1))

                            else:

                                raise Exception(
                                    "El servidor de Gemini continúa "
                                    "saturado después de 3 intentos. "
                                    "Espera unos minutos y vuelve "
                                    "a intentarlo."
                                )

                        else:

                            # Mostrar otros errores normalmente
                            raise

                # ==========================================================
                # 11. MOSTRAR RESPUESTA
                # ==========================================================

                if not respuesta:

                    respuesta = (
                        "No pude generar una respuesta. "
                        "Por favor, intenta nuevamente."
                    )

                st.markdown(respuesta)

                # Guardar respuesta en historial
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": respuesta
                    }
                )

            except Exception as e:

                st.error(
                    f"❌ Error al consultar la API de Gemini: {e}"
                )

                st.info(
                    "💡 Verifica tu conexión a internet, "
                    "tu API Key y la disponibilidad del modelo. "
                    "Si Gemini está saturado, espera unos minutos."
                )