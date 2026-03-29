import os
from pathlib import Path
from sentence_transformers import util
from googletrans import Translator
from models import model_sentence_transformers
from search_programs import find_programs


class ProgramSearcher:
    def __init__(self):
        self.translator = Translator()
        self.model = model_sentence_transformers
        programs = find_programs()
        self.program_names = programs.keys()
        self.program_paths = programs.values()
        self.programs_embs = self.model.encode(self.program_names, convert_to_tensor=True)

    def search_s(self, query):
        query_em = self.model.encode(query, convert_to_tensor=True)
        s = util.cos_sim(query_em, self.programs_embs)[0]
        res = []
        for idx, i in enumerate(s):
            if i.item() >= 0.8:
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
