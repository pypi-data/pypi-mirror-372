import re
import logging
from typing import Dict, Optional

def parse_traceback(traceback_text: str) -> Optional[Dict[str, any]]:

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    try:
        file_line_pattern = r'File "(.*?)", line (\d+),'
        file_line_matches = re.findall(file_line_pattern, traceback_text)
        
        if not file_line_matches:
            logging.error("Could not find file path and line number in traceback.")
            return None
        
        file_path, line_number_str = file_line_matches[-1]
        line_number = int(line_number_str)

        error_pattern = r'^\s*([a-zA-Z_]\w*Error):\s*(.*)'
        error_match = None

        for line in reversed(traceback_text.strip().split('\n')):
            match = re.match(error_pattern, line)
            if match:
                error_match = match
                break
        
        if not error_match:
            logging.error("Could not find error type and message in traceback.")
            return None

        error_type = error_match.group(1)
        error_message = error_match.group(2)

        parsed_data = {
            "file_path": file_path,
            "line_number": line_number,
            "error_type": error_type,
            "error_message": error_message
        }
        
        logging.info(f"Successfully parsed traceback. Data: {parsed_data}")
        return parsed_data

    except Exception as e:
        logging.error(f"An unexpected error occurred during parsing: {e}")
        return None
