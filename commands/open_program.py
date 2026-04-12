import os
from sentence_transformers import util
from googletrans import Translator
from utils.models import model_sentence_transformers
from .search_programs import find_programs


class ProgramSearcher:
    def __init__(self):
        self.translator = Translator()
        self.model = model_sentence_transformers
        programs = find_programs()
        self.program_names = list(programs.keys())
        self.program_paths = list(programs.values())
        self.programs_embs = self.model.encode(self.program_names, convert_to_tensor=True)

    def search_s(self, query):

        query = str(self.translator.translate(query, dest='en'))
        query_em = self.model.encode(query, convert_to_tensor=True)

        similarities = util.cos_sim(query_em, self.programs_embs)[0]

        results = []
        for idx, similarity in enumerate(similarities):
            if similarity.item() >= 0.6:
                results.append({
                    'index': idx,
                    'similarity': similarity.item(),
                    'name': self.program_names[idx],
                    'path': self.program_paths[idx]
                })

        results.sort(key=lambda x: x['similarity'], reverse=True)

        if results:
            print(f"\nНайдено {len(results)} совпадений:")
            for r in results[:3]:
                print(f"  - {r['name']} (сходство: {r['similarity']:.3f})")

            return self.start_program(results[0])
        else:
            print('Программа не найдена')
            return 'Программа не найдена'

    def start_program(self, program):
        try:
            if not os.path.exists(program['path']):
                print(f'Файл не найден: {program["path"]}')
                return f'Файл не найден: {program["name"]}'

            os.startfile(program['path'])

            try:
                if any(ord(char) > 127 for char in program['name']):
                    display_name = program['name']
                else:
                    translated = self.translator.translate(program['name'], dest='ru')
                    display_name = translated.text
            except:
                display_name = program['name']

            print(f'Запущено: {display_name} (сходство: {program["similarity"]:.3f})')
            return f'Запущено: {display_name}'

        except Exception as e:
            error_msg = f'Ошибка при запуске {program["name"]}: {e}'
            print(error_msg)
            return error_msg
