from pathlib import Path

project_path = Path(__file__).parent.parent

URLS = {
    'weather_txt': f'{project_path}\\user_data\\data_weather.txt',
    'weather_csv': f'{project_path}\\user_data\\weather_data.csv',
    'weather_now': f'{project_path}\\user_data\\weather_data_now.csv',
    'schedule': f'{project_path}\\user_data\\9а.csv',
    'current_city': f'{project_path}\\user_data\\current_city.json',
    'russia_cities': f'{project_path}\\user_data\\russia-cities.json',
    'config': f'{project_path}\\config.json',
    'vosk_model': f'{project_path}\\utils\\models\\vosk-model-small-ru-0.22',
    'transformers_model': f'{project_path}\\utils\\models\\paraphrase-multilingual-MiniLM-L12-v2',
    'silero_model': f'{project_path}\\utils\\models\\silero\\v3_1_ru.pt'
}
