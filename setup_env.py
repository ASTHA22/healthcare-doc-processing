import os
from pathlib import Path

def setup_environment():
    env_file = Path(".env")
    if env_file.exists():
        print(".env file already exists. Please update it with your Azure credentials if needed.")
        return
    
    print("Setting up .env file...")
    print("Please enter your Azure credentials (press Enter to leave blank):")
    
    form_recognizer_endpoint = input("Azure Form Recognizer Endpoint: ")
    form_recognizer_key = input("Azure Form Recognizer Key: ")
    vision_endpoint = input("Azure Computer Vision Endpoint: ")
    vision_key = input("Azure Computer Vision Key: ")
    
    with open(env_file, "w") as f:
        f.write(f"AZURE_FORM_RECOGNIZER_ENDPOINT={form_recognizer_endpoint}\n")
        f.write(f"AZURE_FORM_RECOGNIZER_KEY={form_recognizer_key}\n")
        f.write(f"AZURE_COMPUTER_VISION_ENDPOINT={vision_endpoint}\n")
        f.write(f"AZURE_COMPUTER_VISION_KEY={vision_key}\n")
        f.write("DOCUMENT_TYPES=insurance_claim,medical_report,prescription,id_proof\n")
    
    print(f"Created {env_file} with provided credentials.")
    print("Please review the file and make sure all values are correct.")

if __name__ == "__main__":
    setup_environment()
