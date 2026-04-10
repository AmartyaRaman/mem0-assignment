import os
from pathlib import Path

# Config
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def create_file(filename: str, content: str = "") -> str:
    """Creates a file in the output folder."""
    # Safety: ensure filename doesn't escape output directory
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"File created successfully: {file_path}"

def write_code(filename: str, code: str) -> str:
    """Writes code to a file in the output folder."""
    # Safety: ensure filename doesn't escape output directory
    safe_name = Path(filename).name
    file_path = OUTPUT_DIR / safe_name
    
    # Ensure common extensions if missing
    if "." not in safe_name:
        safe_name += ".py"
        file_path = OUTPUT_DIR / safe_name

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    return f"Code saved successfully to: {file_path}"

def summarize_text(text: str) -> str:
    """Summarizes the provided text using logic (usually called by the LLM)."""
    # For now, this is a placeholder tool. In agent.py, the LLM will actually 
    # generate the summary, and this tool might be used to save it or log it.
    summary_path = OUTPUT_DIR / "summary.txt"
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- Summary ---\n{text}\n")
    
    return f"Summary appended to {summary_path}"

def list_output_files() -> str:
    """Lists files in the output directory."""
    files = list(OUTPUT_DIR.glob("*"))
    if not files:
        return "The output folder is empty."
    return "Files in output folder:\n" + "\n".join([f"- {f.name}" for f in files])
