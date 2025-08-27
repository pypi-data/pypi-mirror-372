import os
import pathlib

def run():
    # Get the path to app.py inside the installed package
    app_path = pathlib.Path(__file__).resolve().parent / "app.py"
    os.system(f"streamlit run {app_path}")

if __name__ == "__main__":
    run()