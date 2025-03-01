#!/usr/bin/env python3
import os
import fnmatch
import sys
import traceback

def should_ignore(path):
    # Patterns to ignore - focusing on non-logic files
    ignore_patterns = [
        # Build and cache
        '*archiver_app*',
        '*/__pycache__*',
        '*.pyc',
        '__pycache__*',
        '*/.local/*',
        '/.virtualenvs/*',
        '*/.ssh/*',
        '*/.cache/*',
        '*/.virtualenvs/*',
        '*/.ipython/*',
        '*/.pki/*',

        '*/migrations/*',
        '*/management/*',
        '*/software/*',
        '.git*',  # This will catch .git and .gitignore
        '.gitignore*',
        '.env',
        'node_modules/*',
        'pyvenv.cfg',
        '*.code-workspace',
        'tailwind.config.js',
        '*config.py',
        '*settings.py',
        '*urls.py',
        '*wsgi.py',
        '*asgi.py',
        '*__init__.py',

        # Static resources
        '*/static/*',
        '*/media/*',
        '*.css',
        '*.scss',
        '*.svg',
        '*.png',
        '*.jpg',
        '*.jpeg',
        '*.gif',
        '*.ico',
        '*.webp',
        '*.mp4',
        '*.mp3',
        '*.json',


        # Documentation and data
        '*.md',
        '*.txt',
        '*.csv',
        '*.xml',

        # Migration files
        '*/migrations/*',

        # Test files
        '*test*.py',

        # Utility scripts
        '*codebase_to_txt*',
        '*manage.py'
    ]

    # Explicit check for .git directory
    if '.git' in path.split(os.sep):
        return True

    if 'venv' in path.split(os.sep):
        return True
    if 'node_modules' in path.split(os.sep):
        return True
    if 'outils' in path.split(os.sep):
        return True
    if 'templates/admin' in path.split(os.sep):
        return True


    return any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns)

def process_codebase(root_dir, output_file):
    file_count = 0
    selected_files = []

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# CODEBASE LOGIC\n\n")

            # First pass - collect structure and files
            for root, dirs, files in os.walk(root_dir):
                dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]

                for file in files:
                    if not file.startswith('.') and not should_ignore(os.path.join(root, file)):
                        file_path = os.path.join(root, file)
                        if os.path.getsize(file_path) <= 1000000:  # Only include files under 1MB
                            rel_file_path = os.path.relpath(file_path, root_dir)
                            selected_files.append(rel_file_path)

            # Write selected files
            f.write("## FILES INCLUDED\n\n")
            for file_path in sorted(selected_files):
                f.write(f"- {file_path}\n")

            # Write file contents
            f.write("\n## FILE CONTENTS\n\n")
            for file_path in sorted(selected_files):
                abs_path = os.path.join(root_dir, file_path)
                try:
                    with open(abs_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()

                    f.write(f"\n{'='*80}\n")
                    f.write(f"FILE: {file_path}\n")
                    f.write(f"{'='*80}\n\n")
                    f.write(content)
                    f.write("\n")
                    file_count += 1
                    print(f"Processed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    continue

    except Exception as e:
        print(f"Error writing to output file: {str(e)}")
        return file_count

    return file_count

if __name__ == "__main__":
    try:
        print("Starting codebase processing...")
        current_dir = os.getcwd()
        output_file = os.path.join(current_dir, "codebase_content.txt")

        file_count = process_codebase(current_dir, output_file)

        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"Successfully processed {file_count} files")
            print(f"Output written to: {output_file} ({size:,} bytes)")
        else:
            print("Error: File was not created successfully")
            sys.exit(1)
    except Exception as e:
        print("Fatal error occurred:", str(e))
        sys.exit(1)