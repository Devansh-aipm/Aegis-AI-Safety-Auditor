import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# --- GOOGLE MODEL INITIALIZATION FIX ---
def load_model():
    # 1. Try to get the key from Streamlit Secrets (Best Practice)
    # 2. Fallback to environment variables
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("Missing Google API Key. Please add it to Streamlit Secrets.")
        st.stop()

    try:
        # FIX: Use 'google_api_key' instead of 'api_key'
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            google_api_key=api_key,
            temperature=0.7
        )
        return model
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.stop()

# Usage in your app:
llm = load_model()
# ---------------------------------------

st.title("Aegis: AI Safety & Fairness Auditor")
# Rest of your red-teaming logic goes here...
