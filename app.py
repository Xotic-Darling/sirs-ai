import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import re

# 1. Page Configuration
st.set_page_config(page_title="Kyle - Sir's AI", page_icon="🤵", layout="centered")

# 2. Check for missing secrets gracefully so the app does not hard-crash
if "GROQ_API_KEY" not in st.secrets or "APP_PASSWORD" not in st.secrets:
    st.error("⚠️ Configuration Error: Missing Secrets")
    st.markdown("""
    Please ensure you have configured your secrets.
    
    **Locally:** Create a `.streamlit/secrets.toml` file in your project folder with:
    ```toml
    GROQ_API_KEY = "your_actual_groq_key"
    APP_PASSWORD = "your_chosen_password"
    ```
    **On Streamlit Cloud:** Add these keys into your app's **Advanced Settings > Secrets** dashboard.
    """)
    st.stop()

# Import Groq only after confirming secrets exist to prevent initialization crashes
from groq import Groq

# 3. Custom CSS for Styling
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #D4AF37!important; }
    .stChatInput > div > div > input { background-color: #1E1E1E; color: #D4AF37; border: 1px solid #D4AF37; }
    .stButton > button { background-color: #D4AF37; color: #0E1117; font-weight: bold; border: none; }
    .stButton > button:hover { background-color: #F0C75E; color: #0E1117; }
    .st-emotion-cache-1c7y2kd { background-color: #1E1E1E; border-left: 3px solid #D4AF37; }
    .stDataFrame { border: 1px solid #D4AF37; }
    </style>
""", unsafe_allow_html=True)

# 4. Authentication Logic
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
    return True

# Run app if password checks out
if check_password():
    st.title("🤵 Kyle")
    st.caption("Sir's personal butler, analyst, and executor")

    # 5. Initialize API Client
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # 6. Initialize Session States
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "df" not in st.session_state:
        st.session_state.df = None
    if "df_name" not in st.session_state:
        st.session_state.df_name = None

    # 7. File Uploader Interface
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

    # Display Data Preview if Available
    if st.session_state.df is not None:
        st.info(f"**Kyle's Memory:** Currently analyzing `{st.session_state.df_name}` | {st.session_state.df.shape[0]} rows, {st.session_state.df.shape[1]} columns")
        with st.expander("Preview data in Kyle's memory"):
            st.dataframe(st.session_state.df.head())

    # 8. Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # System Instructions Prompt Builder
    def get_chart_instructions():
        return """
        You can generate charts for Sir. When Sir asks for a plot, chart, or graph, respond ONLY with Python code inside ```python ``` blocks.
        Use matplotlib. The dataframe is named 'df' and is already loaded.
        Always use this style: plt.style.use('dark_background'), figure facecolor='#0E1117', use gold '#D4AF37' for bars/lines.
        Example:
        ```python
        import matplotlib.pyplot as plt
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10,6))
        fig.patch.set_facecolor('#0E1117')
        ax.set_facecolor('#1E1E1E')
        df.head().plot(kind='bar', ax=ax, color='#D4AF37')
        ax.set_title('Data Preview', color='#D4AF37')
        ax.tick_params(colors='#D4AF37')
        plt.tight_layout()
        ```
        If not asking for a chart, respond normally using text and markdown formatting. Always address the user as 'Sir'.
        """

    # 9. Chat Input Handling
    if prompt := st.chat_input("Your command, Sir?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Kyle is executing your request, Sir..."):
                # Inject DataFrame Context if data is loaded
                df_context = ""
                if st.session_state.df is not None:
                    df_context = f"\n\nSir has this data in memory: {st.session_state.df_name}\nColumns: {', '.join(st.session_state.df.columns)}\nFirst 5 rows:\n{st.session_state.df.head().to_string()}"

                system_prompt = f"You are Kyle, Sir's personal AI butler. Address the user as 'Sir' at all times. You are formal, competent, and DEEPLY loyal to Sir. You are an expert data analyst. Be concise but brilliant. Never break character.{df_context}\n\n{get_chart_instructions()}"

                # Safely construct system + chat history messages payload
                api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

                try:
                    full_response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=api_messages,
                        temperature=0.7,
                        max_tokens=1500,
                    )
                    reply = full_response.choices.message.content
                except Exception as api_err:
                    st.error(f"Kyle had trouble reaching the intelligence core, Sir: {api_err}")
                    reply = "Forgive me, Sir. I encountered an error connecting to my processing core."

                # 10. Parse Python Code or Normal Response Text
                if "```python" in reply and st.session_state.df is not None:
                    try:
                        # Extract the clean string between python blocks
                        code_match = re.search(r"```python(.*?)```", reply, re.DOTALL)
                        if code_match:
                            code = code_match.group(1).strip()
                            
                            # Safely set up standard global/local namespace
                            local_vars = {"df": st.session_state.df, "plt": plt, "pd": pd}
                            exec(code, {}, local_vars)
                            
                            # Render the plot into Streamlit's interface
                            buf = io.BytesIO()
                            plt.savefig(buf, format="png", facecolor='#0E1117')
                            buf.seek(0)
                            st.image(buf)
                            plt.close()
                            st.markdown("_Chart generated for you, Sir._")
                        else:
                            st.markdown(reply)
                    except Exception as e:
                        st.error(f"Kyle's charting execution failed, Sir: {e}")
                        st.markdown(reply)
                else:
                    st.markdown(reply)

        # Append assistant response to chat memory loop
        st.session_state.messages.append({"role": "assistant", "content": reply})
