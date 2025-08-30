import os
import logging
from typing import Dict, Optional
import google.generativeai as genai
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def generate_fix(error_details: Dict[str, any], code_context: str) -> Optional[str]:

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logging.error("GOOGLE_API_KEY not found in .env file. Please ensure the file exists in the project root and the key is set.")
        return None
    
    try:
        genai.configure(api_key=api_key)

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        model = genai.GenerativeModel('gemini-1.5-flash-latest', safety_settings=safety_settings)

    except Exception as e:
        logging.error(f"Failed to configure or initialize the Gemini API model: {e}")
        return None

    prompt_template = f"""
You are an expert automated Python debugging assistant. Your sole task is to fix a bug in a given Python function.
Analyze the provided error traceback and the source code of the function where the error occurred.
You must propose a corrected version of the entire function.

**CRITICAL INSTRUCTIONS:**
1.  Your output MUST be ONLY the complete, corrected Python code for the function.
2.  Do NOT include any explanations, comments, introductory text, or markdown formatting like ```python.
3.  Ensure the corrected function has the same name, arguments, and decorators as the original.
4.  The code you provide will be directly used to replace the old function in the source file.

**Error Traceback Details:**
- Error Type: {error_details['error_type']}
- Error Message: {error_details['error_message']}
- File Path: {error_details['file_path']}
- Line Number: {error_details['line_number']}

**Source Code of the Faulty Function:**
```python
{code_context}
```

**Corrected Function Code:**
"""

    try:
        logging.info("Sending request to Gemini API...")
        response = model.generate_content(prompt_template)
        
        if not response.text or not response.text.strip():
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                 logging.warning(f"Request was blocked by API. Reason: {response.prompt_feedback.block_reason}")
            else:
                logging.warning("Received an empty or invalid response from the Gemini API.")
            return None
        
        fixed_code = response.text.strip()
        if fixed_code.startswith("```python"):
            fixed_code = fixed_code[9:]
        if fixed_code.endswith("```"):
            fixed_code = fixed_code[:-3]
        
        fixed_code = fixed_code.strip()
        
        logging.info("Successfully received and cleaned response from API.")
        return fixed_code
        
    except Exception as e:
        logging.error(f"An error occurred while communicating with the Gemini API: {e}")
        return None
