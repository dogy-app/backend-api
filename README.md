<!-- @format -->

# dogy.backend

Backend for dogy app

### Stetps to start

1. Create virtual environment
   `python -m venv venv`
2. Create `.env` file add these keys:
   `AZURE_STORAGE_CONNECTION_STRING=KEY`
   `AZURE_CONTAINER_NAME=KEY`
   `AZURE_ESSENTIALS_CONTAINER_NAME=KEY`
   `AZURE_STORAGE_FIREBASE_KEY_BLOB_NAME=KEY`
   `GOOGLE_API_KEY=KEY`
   `OPENAI_API_KEY=KEY`
   `DOGY_COMPANION_ID=KEY`
3. Install requirements
   `pip install -r requirements.txt`
4. run `uvicorn main:app --reload` to start dev server
