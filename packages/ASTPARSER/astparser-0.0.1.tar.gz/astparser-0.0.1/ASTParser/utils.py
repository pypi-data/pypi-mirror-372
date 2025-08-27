from pathlib import Path

def detect_js_or_ts(file_path: str) -> str:
        try:
            extension = Path(file_path).suffix.lower()
            if extension in ['.js', '.jsx']:
                return 'javascript'
            elif extension in ['.ts', '.tsx']:
                return 'typescript'
            else:
                return 'unknown'
        except Exception as e:
            print(f"The error with detecting the filetype : {e}")