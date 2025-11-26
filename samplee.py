import streamlit as st
import google.generativeai as genai
import time
import os

# --- PAGE SETTINGS ---
st.set_page_config(page_title="CanDer AI", page_icon="🧛🏻‍♀️🧛🏽")
st.title("🧛🏻‍♀️🧛🏽 CanDer AI")
st.caption("Your Personal AI Assistant")

# --- API KEY SETUP (IMPORTANT) ---
try:
    # 1. First checks server settings (Secrets)
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # 2. If not found (i.e., local machine), uses this key
    # PASTE YOUR OWN LONG KEY HERE
    api_key = "enter your api key"

genai.configure(api_key=api_key)

# --- AUTOMATIC MODEL SELECTOR ---
try:
    # Tries to find the fast and free "Flash" model
    tum_modeller = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    secilen_model = None
    
    for m in tum_modeller:
        if "flash" in m.name:
            secilen_model = m.name
            break
            
    if not secilen_model and tum_modeller:
        secilen_model = tum_modeller[0].name

    if secilen_model:
        model = genai.GenerativeModel(secilen_model)
        # Commented out to hide technical details from user
        # st.caption(f"✅ {secilen_model} active.") 
    else:
        st.error("Model not found.")
        model = None

except Exception as e:
    st.error(f"Model error: {e}")
    model = None

# --- MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT ---
prompt = st.chat_input("Ask something...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if model:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            basarili = False
            deneme = 0
            
            # Retry Loop for 503 Error
            while not basarili and deneme < 3:
                try:
                    deneme += 1
                    response = model.generate_content(prompt, stream=True)
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    basarili = True
                    
                except Exception as e:
                    if "503" in str(e) or "Overloaded" in str(e):
                        time.sleep(2)
                        if deneme == 3: st.error("Servers are very busy, please try again.")
                    else:
                        st.error(f"Error: {e}")
                        break