import re
from pathlib import Path
import os

r = r"\{([^{}]*?)\}"

rr = ['.venv', '__pycache__', '.git', '.idea', 'models']

p = Path('.').rglob('*.py')

for path in p:
    path_list = str(path).split('\\')
    if path_list[0] not in rr:
        path_new = '../Shustrik_VA_python3_11/' + str(path)
        dir_path = os.path.dirname(path_new)
        if dir_path != '':
            os.makedirs(dir_path, exist_ok=True)
            with open(str(path).replace('\\', '/'), 'r', encoding='utf-8') as f1, open(str(path_new).replace('\\', '/'), 'w', encoding='utf-8') as f2:
                data = f1.read()
                res = re.sub(r, lambda m: '{' + m.group(1).replace("'", '"') + '}', data)
                f2.write(res)
