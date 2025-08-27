import os, sys
import re
from e2b_code_interpreter import Sandbox
import streamlit as ui

# Define pattern for code extraction
pattern = re.compile(r"```python\n(.*?)\n```", re.DOTALL)

def match_code_blocks(llm_response: str) -> str:
    match = pattern.search(llm_response)
    if match:
        code = match.group(1)
        # Remove function definitions and if __name__ block
        code = re.sub(r'def\s+\w+\(.*?\):.*?(?=def|\Z)', '', code, flags=re.DOTALL)
        code = re.sub(r'if\s+__name__\s*==\s*["\']__main__["\']:.*', '', code, flags=re.DOTALL)
        return code.strip()
    return ""


def upload_dataset(code_interpreter: Sandbox, uploaded_file) -> str:
    dataset_path = f"./{uploaded_file.name}"
    
    try:
        # Convert UploadedFile to bytes and write to sandbox
        file_bytes = uploaded_file.getvalue()
        code_interpreter.files.write(dataset_path, file_bytes)
        return dataset_path
    except Exception as error:
        ui.error(f"[ERROR in upload_dataset]: {error}")
        raise error