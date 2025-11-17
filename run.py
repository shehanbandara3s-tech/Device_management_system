import os
import sys
from streamlit.web import cli as stcli

if __name__ == "__main__":
    # Change to the current directory
    os.chdir(os.path.dirname(__file__)) 

    # Command to run the main Streamlit app file (replace 'app_english.py')
    sys.argv = [
        "streamlit", 
        "run", 
        "app.py", # Change this to your main Streamlit file name
        "--global.developmentMode=false"
    ]
    sys.exit(stcli.main())