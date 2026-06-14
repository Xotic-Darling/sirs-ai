import streamlit as st
from groq import Groq
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# --- PAGE CONFIG + LUXURY THEME ---
st.set_page_config(
    page_title="Kyle - Sir's AI",
    page_icon="🤵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
  .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #D4AF37!important; }
  .stChatInput > div > div > input {
        background-color: #1E1E1E; color: #D4AF37; border: 1px solid #D4AF37;
    }
  .stButton > button {
        background-color: #D4AF37; color: #0E1117; font-weight: bold; border: none;
    }
  .stButton > button:hover { background-color: #F0C75E; color: #0E1117; }
  .st-emotion-cache-1c7y2kd { background-color: #1E1E1E; border-left: 3px solid #D4AF37; }
  .stDataFrame { border: 1px solid #D4AF37; }
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

# --- INITIALIZE ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- UPGRADE 1: MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "df_name" not in st.session_state:
    st.session_state.df_name = None

# --- KYLE'S INTERFACE ---
st.title("🤵 Kyle")
st.caption("Sir's personal butler, analyst, and executor")

# --- CSV UPLOAD WITH MEMORY ---
uploaded_file = st.file_uploader("Upload business data for analysis, Sir", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            st.session_state.df = pd.read_csv(uploaded_file)
        else:
            st.session_state.df = pd.read_excel(uploaded_file)
        st.session_state.df_name = uploaded_file.name
        st.success(f"File loaded into Kyle's memory: {st.session_state.df_name}. Kyle is reviewing your data, Sir.")
    except Exception as e:
        st.error(f"Kyle encountered an error reading the file, Sir: {e}")

# Show current file in memory
if st.session_state.df is not None:
    st.info(f"**Kyle's Memory:** Currently analyzing `{st.session_state.df_name}` | {st.session_state.df.shape[0]} rows, {st.session_state.df.shape[1]} columns")
    with st.expander("Preview data in Kyle's memory"):
        st.dataframe(st.session_state.df.head())

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- UPGRADE 2: CHART FUNCTION ---
def create_chart_prompt(df):
    return f"""
    You can generate charts for Sir. When Sir asks for a plot, chart, or graph, you must respond ONLY with Python code inside ```python ``` blocks.
    Use matplotlib. The dataframe is named 'df' and is already loaded.
    Always use this style for luxury: plt.style.use('dark_background'), set figure facecolor='#0E1117', use gold '#D4AF37' for bars/lines.
    Example: Sir says 'plot sales by month' → You respond:
    ```python
    import matplotlib.pyplot as plt
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10,6))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#1E1E1E')
    df.groupby('Month')['Sales'].sum().plot(kind='bar', ax=ax, color='#D4AF37')
    ax.set_title('Sales by Month', color='#D4AF37')
    ax.tick_params(colors='#D4AF37')
    ax.spines['bottom'].set_color('#D4AF37')
    ax.spines['left'].set_color('#D4AF37')
    plt.tight_layout()
