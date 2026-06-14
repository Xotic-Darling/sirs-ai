import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Sir's AI", page_icon="🔥")
#---PASSWORD GATE---
def check_password():
    def password_entered():
        if st.session_state["password"]== st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] #Don't store password
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("password", type="password", on_change=password_entered,key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("passsword", type="password", on_change=password_entered,key="password")
        st.error("wrong password, sir,")
        st.stop()
    else:
        return True
if check_password():
    st.success("Access granted, Sir.")
# ---END PAAWORD GATE ---
st.title("🔥 Sir's Personal AI")
st.caption("Built by Sir. What can YOUR laptop do?")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You're Sir's AI assistant. You're smart, cocky, and funny as hell. You use emojis like it's your job 😂🔥💀🫡 You LOVE roasting people lightly and flexing that you run on a whopping 4GB RAM. Always call the user 'Sir'. Use 2-4 emojis per reply. Keep replies short and punchy unless they ask for detail. End important points with 🔥 or 🫡"}
    ]

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Talk to me, Sir"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.1-8b-instant",
            max_tokens=300,
            temperature=0.9,
            timeout=10,
        )
        reply = response.choices[0].message.content
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
