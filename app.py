import streamlit as st
from groq import Groq
import pandas as pd

# --- BLACK/GOLD THEME ---
st.set_page_config(
    page_title="Kyle - Sir's AI",
    page_icon="🤵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Black + Gold luxury theme
st.markdown("""
    <style>
   .stApp {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: #D4AF37!important;
    }
   .stChatInput > div > div > input {
        background-color: #1E1E1E;
        color: #D4AF37;
        border: 1px solid #D4AF37;
    }
   .stButton > button {
        background-color: #D4AF37;
        color: #0E1117;
        font-weight: bold;
        border: none;
    }
   .stButton > button:hover {
        background-color: #F0C75E;
        color: #0E1117;
    }
   .st-emotion-cache-1c7y2kd {
        background-color: #1E1E1E;
        border-left: 3px solid #D4AF37;
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

# --- KYLE'S INTERFACE ---
st.title("🤵 Kyle")
st.caption("Sir's personal butler, analyst, and executor")

# --- BOX 5: CSV UPLOAD FOR DATA ANALYSIS ---
uploaded_file = st.file_uploader("Upload business data for analysis, Sir", type=["csv", "xlsx"])

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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
