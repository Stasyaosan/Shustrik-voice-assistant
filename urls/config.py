from pathlib import Path

project_path = Path(__file__).parent.parent

URLS = {
    'weather_txt': project_path / 'user_data' / 'data_weather.txt',
    'weather_csv': project_path / 'user_data' / 'weather_data.csv',
    'weather_now': project_path / 'user_data' / 'weather_data_now.csv',
    'schedule': project_path / 'user_data' / '9а.csv',
    'current_city': project_path / 'user_data' / 'current_city.json',
    'russia_cities': project_path / 'user_data' / 'russia-cities.json',
    'config': project_path / 'config.json',
    'vosk_model': project_path / 'utils' / 'models' / 'vosk-model-small-ru-0.22',
    'models': project_path / 'utils' / 'models',
    'transformers_model': project_path / 'utils' / 'models' / 'paraphrase-multilingual-MiniLM-L12-v2',
    'silero_model': project_path / 'utils' / 'models' / 'silero' / 'v4_ru.pt'
}