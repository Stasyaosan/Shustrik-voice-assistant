# import subprocess
# subprocess.run([r'C:\Users\PC\AppData\Local\Postman\Postman.exe'])
import os
from pathlib import Path


class ProgramSearcher:
    def __init__(self):
        self.programs = {}

    def search_desktop(self, program_name):
        desktop_paths = [
            os.path.join(os.environ['USERPROFILE'], 'Desktop')
        ]
        res = []

        for desktop_path in desktop_paths:
            if os.path.exists(desktop_path):
                for lnk_file in Path(desktop_path).glob('*.lnk'):
                    name = lnk_file.stem.lower()

                    if program_name.lower() in name:
                        res.append(str(lnk_file))
                        os.startfile(f'{str(lnk_file)}')
        return res
