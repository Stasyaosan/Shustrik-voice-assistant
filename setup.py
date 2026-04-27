import os.path
import platform
import subprocess


def get_python_path(venv='venv'):
    python_cmd = ''
    if platform.system() == 'Windows':
        python_cmd = 'python'
    else:
        python_cmd = 'python3'

    subprocess.run([python_cmd, '-m', 'venv', venv], text=True, check=True)
    if python_cmd == 'python':
        activate_script = os.path.join(venv, 'Scripts', 'activate')
        cmd = f'start cmd /k "{activate_script} && pip install -r requirements.txt && {python_cmd} main.py"'
        subprocess.run(cmd, shell=True)
    else:
        activate_script = os.path.join('source', venv, 'bin', 'activate')
        cmd = f'{activate_script} && pip install -r requirements.txt && {python_cmd} main.py"'
        subprocess.run(cmd, shell=True)


get_python_path('venv')
