import os
from .key_manager import generate_key, apply_key
from .metadata import log_operation

def generate_maratmak_output(encoded_data: str) -> str:
    """Create ultra-secure maratmak output"""
    # Multi-layer scramble example
    key2 = generate_key(32)
    maratmak = apply_key(encoded_data, key2)
    # Further obfuscation
    return "".join(format(ord(c), "02x") for c in maratmak)

def encode_text(input_text: str) -> str:
    try:
        key = generate_key()
        encoded = apply_key(input_text, key)
        maratmak = generate_maratmak_output(encoded)
        log_operation("text_input", "success")
        return maratmak
    except Exception as e:
        log_operation("text_input", f"fail: {e}")
        return None

def encode_file(file_path: str) -> str:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found.")
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        key = generate_key()
        encoded = apply_key(content, key)
        maratmak = generate_maratmak_output(encoded)
        
        # Save new encoded file
        base, ext = os.path.splitext(file_path)
        output_file = f"{base}_encoded.hx"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(maratmak)
        
        log_operation(file_path, "success")
        return output_file
    except Exception as e:
        log_operation(file_path, f"fail: {e}")
        return None
