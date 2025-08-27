import os, sys
from groq import Groq
from e2b_code_interpreter import Sandbox
from src.ds_assistant.sandbox.e2b_code_interpreter import e2b_sandbox_code_interpret
from src.ds_assistant.utils.some_utils import match_code_blocks
from typing import List, Literal, Optional, Any, Tuple
import streamlit as ui




def generate_natural_language_explanation(code_results: Optional[List[Any]], execution_info: dict, original_query: str, dataset_path: str) -> str:
  
    
    try:
        # Prepare context for the explanation
        explanation_context = f"""
        The user asked: "{original_query}"
        
        Code execution results:
        - Success: {execution_info['success']}
        - Standard Output: {execution_info['stdout']}
        - Standard Error: {execution_info['stderr']}
        - Error: {execution_info['error']}
        
        Please provide a clear, natural language explanation of what the code did and what the results mean.
        Focus on explaining the numerical results, visualizations, and any insights gained.
        If there were errors, explain what might have gone wrong in simple terms.
        """
        
        client = Groq(api_key=ui.session_state.groq_api_key)
        
        completion = client.chat.completions.create(
            model=ui.session_state.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful data science assistant that explains code execution results in clear, natural language."},
                {"role": "user", "content": explanation_context}
            ],
            temperature=0.3,  # Lower temperature for more factual responses
            max_completion_tokens=500,
            top_p=0.9,
            stream=False
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        return f"Error generating explanation: {str(e)}"
    


def chat_with_large_language_model(e2b_code_interpreter: Sandbox, user_message: str, dataset_path: str) -> Tuple[Optional[List[Any]], str, str, dict]:
    try:
        system_prompt = f"""
        You're a Python data scientist and data visualization expert. 
        You are given a dataset at path '{dataset_path}' and also the user's query.
        You need to analyze the dataset and answer the user's query with a response 
        and you run Python code to solve them.
        
        IMPORTANT: 
        1. Always use the dataset path variable '{dataset_path}' in your code when reading the CSV file.
        2. Write direct executable code, NOT function definitions.
        3. Do NOT use if __name__ == "__main__" blocks.
        4. After creating visualizations, make sure to display them using plt.show() for matplotlib.
        5. Use simple, direct code that can be executed line by line.
        6. Use print() statements to output numerical results and statistics.
        7. Your response should include both the Python code and a brief explanation.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        with ui.spinner('Getting response from Groq LLM model...'):
            client = Groq(api_key=ui.session_state.groq_api_key)

            completion = client.chat.completions.create(
                model=ui.session_state.model_name,
                messages=messages,
                temperature=0.7,
                max_completion_tokens=1024,
                top_p=1,
                stream=False
            )

            response_message = completion.choices[0].message.content

            python_code = match_code_blocks(response_message)

            if python_code:
                ui.code(python_code, language="python")
                code_interpreter_results, execution_info = e2b_sandbox_code_interpret(
                    e2b_code_interpreter, 
                    python_code
                )
                
                # Generate natural language explanation
                explanation = generate_natural_language_explanation(
                    code_interpreter_results, 
                    execution_info, 
                    user_message,
                    dataset_path
                )
                
                return code_interpreter_results, response_message, explanation, execution_info
            
            else:
                ui.warning("Failed to match any Python code in model's response")
                return None, response_message, "No code was executed.", {"success": False}

    except Exception as e:
        ui.error(f"[ERROR in chat_with_large_language_model]: {e}")
        return None, f"Error: {str(e)}", f"Error: {str(e)}", {"success": False}