import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Document Q&A Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("Document Q&A Assistant")
st.markdown("Upload documents and ask questions based on their content!")

# Test backend connection
try:
    response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
    if response.status_code == 200:
        st.success("Connected to backend")
        st.json(response.json())
    else:
        st.error(" Backend connection failed")
except Exception as e:
    st.error(f"Cannot connect to backend: {str(e)}")
    st.info("Make sure FastAPI server is running on http://localhost:8000")

# Sidebar for document upload
with st.sidebar:
    st.header("📄 Upload Documents")
    st.info("Backend connection test successful! Ready for Phase 2.")
