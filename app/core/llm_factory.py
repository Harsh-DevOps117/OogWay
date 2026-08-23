import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    elif provider == "groq":

        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="qwen/qwen3.6-27b", 
            temperature=0
        )
    elif provider == "ollama":

        return ChatOllama(model="llama3", temperature=0)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

def get_embeddings():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif provider == "groq":


        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    elif provider == "ollama":
        return OllamaEmbeddings(model="nomic-embed-text")
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER for embeddings: {provider}")
