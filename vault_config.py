import os

"""
We need to import os to walk thorugh the fieles as we see in loop and os.walk recustivly goes through those 
root	The current folder path being looked at
dirs	A list of subdirectories in that folder
files	A list of filenames in that folder
"""

def load_markdown_files(vault_path):
    results = []
    for root, dirs, files in os.walk(vault_path):
        # Skip hidden folders like .obsidian
        dirs[:] = [folder for folder in dirs if not folder.startswith('.')]

        # Only does .md files (obsidian) and stores path and text as a tuple
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                results.append((full_path, content))
    
    return results

# Returns a list of (filename, content) tuples.