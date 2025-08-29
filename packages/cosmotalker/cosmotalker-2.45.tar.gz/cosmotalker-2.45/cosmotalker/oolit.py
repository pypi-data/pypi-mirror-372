# oolit.py

import sys
from . import api

def oolit():
    # Get prompt from command-line arguments
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
    else:
        # Provide a default prompt if none is given
        prompt_user = input("Enter your prompt : ")
        prompt = prompt_user
    
    # Send prompt to Ollama and get response
    print("Thinking...")
    print("Oolit : ", end="")
    for chunk in api.api(prompt, stream=True):
        print(chunk, end="")
        sys.stdout.flush()
    print() # Newline at the end

if __name__ == "__main__":
    oolit()
