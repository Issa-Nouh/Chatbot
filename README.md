# Streamlit PDF Chatbot + CMS

Very basic chatbot app that reads local PDF files, answers questions via OpenAI API, and logs query/answer pairs to MongoDB Atlas.

## Features

- Chatbot page using your local project PDFs as context
- CMS page to inspect extracted document content
- MongoDB Atlas logging for every chat turn

## Project Structure

- `app.py` - Streamlit app home page
- `pages/1_Chatbot.py` - Chat UI
- `pages/2_CMS.py` - Document and logs viewer
- `services/pdf_loader.py` - PDF discovery + extraction
- `services/openai_client.py` - OpenAI API wrapper
- `services/mongo_logger.py` - MongoDB Atlas logging helpers
- `config.py` - Env-based configuration

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and set:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` (default example: `gpt-4o-mini`)
   - `MONGODB_URI`
   - `MONGODB_DB`
   - `MONGODB_COLLECTION`
4. Put your PDF file(s) in the project root folder.

## Run

```bash
streamlit run app.py
```

## MongoDB Atlas Notes

- Use your Atlas connection string in `MONGODB_URI`.
- Ensure your user has write access to the selected DB/collection.
- Allow your IP in Atlas network access settings while testing.
