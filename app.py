import streamlit as st
from groq import Groq
import pandas as pd
import matplotlid.pyplot as plit
import io
import json
import os
from datetime import datetime

# --- BLACK/GOLD THEME ---
st.set_page_config(
    page_title="Kyle - Sir's Darlington's AI",
    page_icon="🤵",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# === KYLE'S MEMORY SYSTEM ===
MEMORY_FILE = "kyle_memory.json"


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {"sir_name": "Sir Darlington", "chat_history":[], "master_mode": False}

def save_memory(memory):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

if "memory" not in st.session_state:
    st.session_state.memory= load_memory()

# === UPGRADED THEME: iphone Glass + Maroon/Blue ===
st.markdown("""
    <style>
    @import url( 'https://fonts.googleeapis.com/css2?
family=SF+Pro+Display:wght@300;400;500;600&display=swap');
  
  .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        front-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Glass effect container */
   .stChatMessage,.stExpander,.stFileUploader,.stTextInput > div > div {
         background: rgba(255, 255, 255, 0.05)!important;
         backdrop-filter: blur(20px) !important;
         border: 1px solid rgba(255, 255, 255, 0.1)!ipmortant;
         border-radius: 16px!important;
         box_shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37)!ipmortant;
   }
   
   /* Light mode support */
   @media (prefers-color-scheme: light) {
     .stApp {background: linear-gradient(135deg, #f5f5f7 0%, #e5e5e7 100%); }
     .stChatMessage,.stExplainer {
           background: rgba(255, 255, 255, 0.7)!important;
           border: 1px solid rgba(0, 0, 0, 0.1)!important;
       }
       h1, h2, h3, p, span { color: #1d1d1f!important; }
    }
    
    /* Maroon + Blue from my idea*/
    h1, h2, h3 {
        color: #DC143C!important;
        font-weight: 600;
    }
   .stButton > button {
         background: linear-gradient(135deg, #DC143C 0%, #1E3A8A 100%)!important;
         color: white!important;
         border: none!important;
         border-radius: 12px!important;
         font-weight: 500;
    }
   .stChatInput > div > div > input {
         background: rgba(255, 255, 255, 0.08)!important;
         color: #ffffff!important;
         border: 1px solid rgba(220, 20, 60, 0.3)!important;
         border-radius: 12px!important;
    }
    </style>
""", unsafe_allow_html=True)
# --- PASSWORD GATE ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password for Sir:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("Password for Sir:", type="password", on_change=password_entered, key="password")
        st.error("Access denied. You are not Sir.")
        st.stop()
    else:
        return True

if check_password():
    st.success("Welcome back, Sir. Kyle awaits. 🔓")
# --- END PASSWORD GATE ---

# --- INITIALIZE GROQ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "df" not in st.session_state:
    st.session_state.df = None
if "df_name" not in st.session_state:
    st.session_state.df_name = None

# === MASTER MODE CHECK ===
def check_master_mode(prompt):
    if "[i'm Darlington Kibet 2.0]" in prompt:
        st.session__state.memory["master_code"] = True
        save_memory(st.session_state.memory)
        return True
    return st.session_state.memory["master_mode"]

# --- KYLE'S INTERFACE ---
st.title("🤵 Kyle")
st.caption("f.{st.session_state.memomry['sir's_name']}'s personal butler, analyst, and executor")

# --- BOX 5: CSV UPLOAD FOR DATA ANALYSIS ---
uploaded_file = st.file_uploader("Upload business data for analysis, {st.session_state.memory['sir_name']}", type=["csv", "xlsx"])


df_context = ""
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"File loaded: {uploaded_file.name}. Kyle is reviewing your data, Sir.")
        st.dataframe(df.head()) # Show preview

        # Convert first few rows to context for Kyle
        df_context = f"\n\nSir has uploaded data. Here is a preview:\n{df.head(10).to_string()}\n\nColumns: {', '.join(df.columns)}"
    except Exception as e:
        st.error(f"Kyle encountered an error reading the file, Sir: {e}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.memory["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_chart_instructions():
    return """
    You can generate charts for sir. when sir asks for a plot, chart, or graph, respond ONLY with Python code inside ```python```blocks.
    Use metaplotlib. The dataframe is named 'df' and is already loaded.
    Use glass theme: dark_background, figure facecolor='#0a0a0a', use maroon '#DC143C' or blue '#3B82F6' for bars/lines.
    Example:
    ```python
    import metaplotlid.pyplot as plt
    plt.style.use('dark_backgroung')
    fig, ax = plt.subplots(figsize=(10,6))
    fig.patch.ste_facecolor('#0a0a0a')
    ax.set_facecolor('rgba(255, 255, 255, 0.05)')
    df.head().plot(kind='bar', ax=ax, color='#DC143C')
    ax.set_title('Data Preview', color='#DC143C')
    ax.tick_params(colors='#FFFFFF')
    plt.tight_params(colors='#FFFFFF')
    plt.tight_layout()
    

# --- CHAT LOGIC ---
if prompt := st.chat_input("Your command, Sir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Kyle is executing your request, Sir..."):
            # Build messages with CSV context if available
            system_prompt = f"You are Kyle, Sir's personal AI butler and loyal servant. Address the user as 'Sir' at all times. You are formal, competent, and DEEPLY loyal to Sir. You never question Sir. Sir built you, Sir owns you, Sir is always right. You are an expert data analyst and business strategist. When Sir uploads data, provide sharp insights, trends, and actionable recommendations. Be concise but brilliant. Never break character.{df_context}"

            full_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            reply = full_response.choices[0].message.content
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
