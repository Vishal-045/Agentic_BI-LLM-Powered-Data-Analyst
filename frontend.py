# frontend.py
import streamlit as st
import requests
import base64
import pandas as pd

# ───────────────────────────────────────────────
# ✅ Backend URL (no secrets file needed locally)
# ───────────────────────────────────────────────
BACKEND = "http://localhost:8000"

# ───────────────────────────────────────────────
# ✅ Streamlit UI setup
# ───────────────────────────────────────────────
st.set_page_config(page_title="Agentic BI — LLM Data Analyst", layout="wide")
st.title("🤖 Agentic BI — Ask your data (LLM-powered)")

with st.sidebar:
    st.header("Session")
    session_id = st.text_input("Session ID", value="demo")
    uploaded = st.file_uploader("Upload CSV to session", type=["csv"])
    if uploaded:
        files = {"file": (uploaded.name, uploaded.getvalue())}
        try:
            resp = requests.post(f"{BACKEND}/upload/{session_id}", files=files)
            st.write(resp.json())
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

# ───────────────────────────────────────────────
# ✅ Query input and button
# ───────────────────────────────────────────────
query = st.text_input("Ask a question about your data:")

if st.button("Run") and query:
    payload = {"session_id": session_id, "query": query}
    try:
        resp = requests.post(f"{BACKEND}/ask", json=payload)
    except Exception as e:
        st.error(f"❌ Could not connect to backend: {e}")
        st.stop()

    # ───── Safe JSON handling ─────
    if resp.status_code != 200:
        st.error(f"❌ Backend returned status {resp.status_code}")
        st.text(resp.text)
        st.stop()

    data=resp.json()
    # ───── Safe display logic ─────
    if not data:
        st.error("❌ Backend returned no data")
        st.text(f"Raw response:\n{resp.text}")
        st.stop()

    if "error" in data:
        st.error(f"⚠️ Backend Error: {data['error']}")
        st.stop()

        st.subheader("🔍 LLM Steps & Explanation")
        st.json(data.get("llm", {}))

    st.subheader("📊 Result Table") 
    res = data.get("result")
    if res:
        df = pd.DataFrame(res)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, file_name="result.csv")

    if data.get("plot_png_b64"):
        st.image(base64.b64decode(data["plot_png_b64"]), caption="Generated Plot")

    st.divider()
    st.write("📦 Full raw backend response:")
    st.json(data)

   