# tools.py
import io
import pandas as pd
import matplotlib.pyplot as plt

class DataStore:
    def __init__(self):
        # session_id -> {filename -> DataFrame}
        self.sessions = {}

    def load_csv(self, name, content, session_id="default"):
        """Load a CSV into memory for a session"""
        df = pd.read_csv(io.BytesIO(content))
        if session_id not in self.sessions:
            self.sessions[session_id] = {}
        self.sessions[session_id][name] = df
        return {"rows": len(df), "columns": list(df.columns)}

    def list(self, session_id="default"):
        """List all loaded datasets for a session"""
        if session_id not in self.sessions:
            return []
        return list(self.sessions[session_id].keys())

    def get(self, name, session_id="default"):
        """Return a dataset by filename"""
        return self.sessions.get(session_id, {}).get(name)

    def run_pandas_snippet(self, name, snippet):
        """Execute a pandas code snippet in a controlled environment"""
        df = self.get(name)

        # ✅ Make 'df' and 'store' available to executed code
        local_vars = {
            "df": df,
            "store": self,
            "pd": __import__("pandas"),
        }

        try:
            exec(snippet, {}, local_vars)
        except Exception as e:
            raise RuntimeError(f"Execution error: {e}")

        # Return 'result' if defined, else the current df
        return local_vars.get("result", df)


def plot_df(df: pd.DataFrame, x: str, y: str, kind: str = "bar") -> bytes:
    """Plot and return image bytes"""
    plt.figure(figsize=(8, 5))
    df.plot(x=x, y=y, kind=kind)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf.getvalue()
