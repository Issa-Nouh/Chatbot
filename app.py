import streamlit as st

from config import get_config, missing_required_values


st.set_page_config(page_title="PDF Chatbot", page_icon=":speech_balloon:", layout="wide")

config = get_config()

st.title("Basic PDF Chatbot")
st.write(
    "Use the sidebar to navigate to **Chatbot** or **CMS**. "
    "This app answers from PDF files in this folder and logs to MongoDB Atlas."
)

missing = missing_required_values(config)
if missing:
    st.warning(
        "Missing environment values: "
        + ", ".join(missing)
        + ". Create a `.env` file based on `.env.example`."
    )
else:
    st.success("Configuration loaded. You can start chatting from the Chatbot page.")

st.markdown(
    """
### Pages
- **Chatbot**: Ask questions based on your local PDF files.
- **CMS**: Review the loaded documents and recent conversation logs.
"""
)
