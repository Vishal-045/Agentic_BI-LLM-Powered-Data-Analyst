🤖 Agentic BI — LLM-Powered Data Analyst

A full-stack artificial intelligence system that allows users to upload datasets, ask analytical questions in natural language, and automatically receive:

Step-by-step reasoning

Clean pandas code

Executable results

Auto-generated visualizations

JSON-structured analysis

This project combines FastAPI, Streamlit, FAISS, LangChain, and Google Gemini 2.5 Flash (via OpenAI-compatible API) to create an agentic data analyst that performs end-to-end BI workflows.# Agentic_BI-LLM-Powered-Data-Analyst

🛠️ Tech Stack

Backend (FastAPI)

FastAPI

FAISS for vector search

LangChain

Google Gemini API (OpenAI-compatible mode)

Frontend

Streamlit

REST communication with FastAPI backend

Utilities

pandas / numpy

matplotlib

python-dotenv

🏗️ System Architecture


User Query → Streamlit UI

               ↓
               
     FastAPI Backend
     
               ↓
               
    LLM Reasoning Engine (Agent)
    
               ↓
               
     Tool Execution Layer
     
   (Pandas, Plots, FAISS Search)
   
               ↓
               
      Final Human-Like Answer
                 + Visual Output
