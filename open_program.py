import os
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from googletrans import Translator
from models import model_sentence_transformers


class ProgramSearcher:
    def __init__(self):
        self.translator = Translator()
        self.programs = {}
        self.model = model_sentence_transformers
        self.search_desktop()

    def search_desktop(self):
        desktop_paths = [
            os.path.join(os.environ['USERPROFILE'], 'Desktop')
        ]
        program_names = []
        program_paths = []

        for desktop_path in desktop_paths:
            if os.path.exists(desktop_path):
                for lnk_file in Path(desktop_path).glob('*.lnk'):
                    name = lnk_file.stem.lower()
                    program_names.append(name)
                    program_paths.append(str(lnk_file))

        if program_names:
            self.programs_embs = self.model.encode(program_names, convert_to_tensor=True)
            self.program_names = program_names
            self.program_paths = program_paths

    def search_s(self, query):
        query_em = self.model.encode(query, convert_to_tensor=True)
        s = util.cos_sim(query_em, self.programs_embs)[0]
        res = []
        for idx, i in enumerate(s):
            if i.item() > 0.5:
                res.append({
                    'index': idx,
                    'k': i.item(),
                    'name': self.program_names[idx],
                    'path': self.program_paths[idx]
                })
        if res:
            return self.start_program(res[0])
        else:
            print('Программа не найдена')
            return 'Программа не найдена'

    def start_program(self, program):
        program_name = self.translator.translate(program['name'], dest='ru')
        try:
            os.startfile(program['path'])
            print(f'Запущено: {program['name']}')
            return f'Запущено {program_name.text}'
        except Exception as e:
            print(f'Ошибка при запуске {program['name']}')
            return f'Ошибка при запуске {program_name.text}'
