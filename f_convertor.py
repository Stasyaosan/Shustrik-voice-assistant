import re
from pathlib import Path
import os

r = r"\{([^{}]*?)\}"

rr = ['.venv', '__pycache__', '.git', '.idea', 'models']

p = Path('.').rglob('*.py')

for path in p:
    path_list = str(path).split('\\')
    if path_list[0] not in rr:
        os.makedirs('../Shustrik_VA_python3_11', exist_ok=True)
        with open(str(path), 'w+', encoding='utf-8') as f:
            pass
