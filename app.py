from dotenv import load_dotenv
load_dotenv()

# app.py
import os
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from llm_client import LLMClient
from tools import DataStore, plot_df
import json

app = FastAPI()
llm = LLMClient()
store = DataStore()

class QueryRequest(BaseModel):
    session_id: str
    query: str

@app.post('/upload/{session_id}')
async def upload_csv(session_id: str, file: UploadFile = File(...)):
    content = await file.read()
    name = file.filename
    info = store.load_csv(name, content)
    return {"status": "ok", "name": name, "info": info}

@app.post('/ask')
async def ask(req: QueryRequest):
    available = store.list()
    prompt = f"""
    You are a data analyst assistant. Available datasets: {available}.
    User question: {req.query}

    Respond ONLY in valid JSON (no markdown or explanations outside JSON).
    Keys: steps, python_snippet, explanation, plot_instructions (x,y,kind)
    """

    try:
        llm_resp = llm.generate(prompt, max_tokens=800)
    except Exception as e:
        return {"error": f"LLM generation failed: {str(e)}"}

    # ✅ Place the new JSON parsing block HERE
    import re
    try:
        # Remove any Markdown code fences like ```json ... ```
        cleaned = re.sub(r"```json|```", "", llm_resp).strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {
            "steps": str(llm_resp),
            "python_snippet": "# no valid code",
            "explanation": "LLM did not return valid JSON; cleaned response shown instead.",
            "plot_instructions": None
        }

    # Then the rest of your existing logic follows...
        # Execute pandas snippet if present
        # Then the rest of your existing logic follows...
    # Execute pandas snippet if present
    python_snippet = parsed.get('python_snippet')
    result_table = None
    plot_bytes = None

    if python_snippet:
        try:
            # ⚙️ Replace any standalone read_csv calls with our in-memory dataset
            name = store.list()[0]
            python_snippet = python_snippet.replace(
                "pd.read_csv('Churn_Modelling.csv')", f"store.get('{name}')"
            )
            python_snippet = python_snippet.replace(
                "pd.read_csv(\"Churn_Modelling.csv\")", f"store.get('{name}')"
            )

            # Make sure the LLM uses the variable 'df'
            if "df" not in python_snippet:
                python_snippet = f"df = store.get('{name}')\n" + python_snippet

            # Force the snippet to end with "result = df.head()" if it prints
            if "print(" in python_snippet:
                python_snippet = python_snippet.replace("print(df.head())", "result = df.head()")

            # 🧠 Execute safely
            parsed_result = store.run_pandas_snippet(name, python_snippet)
            if hasattr(parsed_result, 'to_dict'):
                result_table = parsed_result.to_dict(orient='records')

            # 🧩 Handle plots if present
            plot_instr = parsed.get('plot_instructions')
            if plot_instr and plot_instr.get('x') and plot_instr.get('y'):
                df = store.get(name)
                plot_bytes = plot_df(
                    df,
                    plot_instr['x'],
                    plot_instr['y'],
                    plot_instr.get('kind', 'bar')
                )

        except Exception as e:
            parsed['explanation'] += f"\nExecution error: {e}"

    # ✅ Build final response
    response = {"llm": parsed, "result": result_table}

    if plot_bytes:
        import base64
        response['plot_png_b64'] = base64.b64encode(plot_bytes).decode('utf-8')

    # ✅ Safety fallback — always return valid JSON
    if not response:
        response = {"error": "Backend failed to generate response"}

    return response
