import ast
import logging
from typing import Optional

def get_code_context(file_path: str, line_number: int) -> Optional[str]:

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    try:
        with open(file_path, 'r') as source_file:
            source_code = source_file.read()

        tree = ast.parse(source_code, filename=file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = getattr(node, 'end_lineno', start_line)

                if start_line <= line_number <= end_line:
                    logging.info(f"Found function '{node.name}' containing line {line_number}.")
                    function_source = ast.get_source_segment(source_code, node)
                    return function_source
        
        logging.warning(f"Could not find a function containing line {line_number} in {file_path}.")
        return None

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except SyntaxError:
        logging.error(f"Could not parse file due to syntax error: {file_path}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred in context manager: {e}")
        return None
