import os

def check_file_for_null_bytes(file_path):
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if b'\x00' in content:
                print(f"Found null byte in {file_path}")
                # Print position of null byte
                positions = [i for i, x in enumerate(content) if x == 0]
                print(f"  Null bytes at positions: {positions}")
                # Print context around first null byte
                pos = positions[0]
                start = max(0, pos - 20)
                end = min(len(content), pos + 20)
                context = content[start:end]
                print(f"  Context: {context}")
                return True
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return False

def scan_directory(dir_path, extension='.py'):
    null_byte_files = []
    files_scanned = 0
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(extension):
                files_scanned += 1
                file_path = os.path.join(root, file)
                print(f"Scanning: {file_path}")
                if check_file_for_null_bytes(file_path):
                    null_byte_files.append(file_path)
    
    print(f"Total files scanned: {files_scanned}")
    return null_byte_files

if __name__ == "__main__":
    print("Scanning for null bytes in Python files...")
    null_byte_files = scan_directory('cabinet_digital')
    
    if null_byte_files:
        print(f"Found {len(null_byte_files)} files with null bytes")
    else:
        print("No files with null bytes found") 