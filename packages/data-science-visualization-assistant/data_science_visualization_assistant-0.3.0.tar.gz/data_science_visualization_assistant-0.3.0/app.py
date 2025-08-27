import os, sys

import streamlit as ui
import pandas as pd
from e2b_code_interpreter import Sandbox
from src.ds_assistant.utils.some_utils import upload_dataset
from src.ds_assistant.chat_completions.llm_chat_completions import chat_with_large_language_model
from io import BytesIO
from PIL import Image
import base64




def main_app_ui():
    ui.title("📊 AI Data Science and Visualization Agent")
    ui.write("Upload your dataset and ask it....")

    # Initialize session state variables
    if 'groq_api_key' not in ui.session_state:
        ui.session_state.groq_api_key = ''
    if 'e2b_api_key' not in ui.session_state:
        ui.session_state.e2b_api_key = ''
    if 'model_name' not in ui.session_state:
        ui.session_state.model_name = ''

    with ui.sidebar:
        ui.header("API Keys and Model Configuration")
        ui.session_state.groq_api_key = ui.text_input("Groq API Key", type="password", value=ui.session_state.groq_api_key)
        ui.info("💡 Groq provides free API access with high-speed inference")
        ui.markdown("[Get Groq API Key](https://console.groq.com/keys)")
        
        ui.session_state.e2b_api_key = ui.text_input("E2B API Key", type="password", value=ui.session_state.e2b_api_key)
        ui.markdown("[Get E2B API Key](https://e2b.dev/docs/legacy/getting-started/api-key)")    

        model_options = {
            "llama-3.3-70b-versatile": "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant": "llama-3.1-8b-instant"
        }

        ui.session_state.model_name = ui.selectbox(
            "Select Model",
            options=list(model_options.keys()),
            index=0
        )

    uploaded_file = ui.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Display dataset with toggle
        df = pd.read_csv(uploaded_file)
        ui.write("Dataset:")
        show_full = ui.checkbox("Show full dataset")
        if show_full:
            ui.dataframe(df)
        else:
            ui.write("Preview (first 5 rows):")
            ui.dataframe(df.head())
        
        # Query input
        query = ui.text_area("What would you like to know about your data?",
                            "Can you show a bar plot of the Class_Label column?")
        
        if ui.button("Analyze"):
            if not ui.session_state.groq_api_key or not ui.session_state.e2b_api_key:
                ui.error("Please enter both API keys in the sidebar.")
            else:
                try:
                    with Sandbox(api_key=ui.session_state.e2b_api_key) as code_interpreter:
                        # Upload the dataset
                        dataset_path = upload_dataset(code_interpreter, uploaded_file)
                        
                        # Pass dataset_path to chat_with_llm
                        code_results, llm_response, explanation, execution_info = chat_with_large_language_model(
                            code_interpreter, query, dataset_path
                        )
                        
                        # Display LLM's original response
                        ui.write("### AI Analysis Plan:")
                        ui.write(llm_response)
                        
                        # Display natural language explanation of results
                        ui.write("### Results Explanation:")
                        ui.write(explanation)
                        
                        # Display raw execution output if needed
                        if execution_info.get('stdout'):
                            with ui.expander("View Raw Output"):
                                ui.code(execution_info['stdout'], language="text")
                        
                        # Display results/visualizations
                        if code_results:
                            ui.write("### Visualizations:")
                            for result in code_results:
                                if hasattr(result, 'png') and result.png:
                                    png_data = base64.b64decode(result.png)
                                    image = Image.open(BytesIO(png_data))
                                    ui.image(image, caption="Generated Visualization", use_container_width=True)
                                elif hasattr(result, 'figure'):
                                    fig = result.figure
                                    ui.pyplot(fig)
                                elif hasattr(result, 'show'):
                                    ui.plotly_chart(result)
                                elif isinstance(result, (pd.DataFrame, pd.Series)):
                                    ui.dataframe(result)
                            
                except Exception as e:
                    ui.error(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main_app_ui()