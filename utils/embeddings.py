import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_embedding_model():

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    return embeddings
