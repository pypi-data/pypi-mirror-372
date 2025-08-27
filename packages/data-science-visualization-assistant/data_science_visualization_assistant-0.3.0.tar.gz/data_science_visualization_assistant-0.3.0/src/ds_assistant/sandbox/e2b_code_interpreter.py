import os, sys

from e2b_code_interpreter import Sandbox
from typing import List, Optional, Any, Tuple

from io import BytesIO
import io

import streamlit as ui
import contextlib


import warnings
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings(
    "ignore", 
    category=UserWarning, 
    module="pydantic"
)



def e2b_sandbox_code_interpret(e2b_code_interpreter: Sandbox, code: str) -> Tuple[Optional[List[Any]], str, dict]:
    
    try:
        with ui.spinner('Executing code in E2B sandbox...'):
            # Run the code directly in the sandbox
            execution = e2b_code_interpreter.run_code(code)
            
            # Capture stdout output
            stdout_output = ""
            if execution.logs.stdout:
                stdout_output = execution.logs.stdout
            
            # Capture stderr output
            stderr_output = ""
            if execution.logs.stderr:
                stderr_output = execution.logs.stderr
                
            execution_info = {
                "stdout": stdout_output,
                "stderr": stderr_output,
                "error": str(execution.error) if execution.error else None,
                "success": execution.error is None
            }
            
            return execution.results, execution_info

    except Exception as e:
        print(f"[ERROR in e2b_sandbox_code_interpret]: {e}")
        return None, {"error": str(e), "success": False}