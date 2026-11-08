@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM ============================================================
REM  Python 3.12.14 — установка, venv, requirements,
REM  скачивание Vosk (GitHub) + paraphrase-multilingual-MiniLM-L12-v2
REM  через зеркало hf-mirror.com, запуск main.py
REM ============================================================

REM --- Настройки Python ---
set PYTHON_VERSION=3.12.14
set PYTHON_TAG=3.12
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
set INSTALLER=%TEMP%\python-%PYTHON_VERSION%-amd64.exe
set VENV_DIR=venv
set REQUIREMENTS=requirements.txt
set MAIN_SCRIPT=main.py

REM --- Общая папка моделей ---
set MODELS_DIR=utils\models

REM --- Модель Vosk (GitHub-зеркало) ---
set VOSK_MODEL=vosk-model-small-ru-0.22
set VOSK_MODEL_PATH=%MODELS_DIR%\%VOSK_MODEL%
set VOSK_URL=https://github.com/kercre123/vosk-models/raw/main/%VOSK_MODEL%.zip
set VOSK_ZIP=%TEMP%\%VOSK_MODEL%.zip

REM --- Модель Sentence-Transformers (HF-зеркало) ---
set HF_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
set HF_LOCAL=%MODELS_DIR%\paraphrase-multilingual-MiniLM-L12-v2
set HF_ENDPOINT=https://hf-mirror.com
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

echo ============================================
echo  Шаг 1: Проверка и установка Python %PYTHON_VERSION%
echo ============================================

py -%PYTHON_TAG% --version >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo Python %PYTHON_TAG% уже установлен.
    goto :create_venv
)

echo Python %PYTHON_TAG% не найден. Скачиваем установщик...
echo URL: %PYTHON_URL%

powershell -NoProfile -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER%'"

if not exist "%INSTALLER%" (
    echo ОШИБКА: Не удалось скачать установщик.
    pause
    exit /b 1
)

echo Устанавливаем Python (тихий режим)...
start /wait "" "%INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

if !ERRORLEVEL! NEQ 0 (
    echo ОШИБКА: Установка Python завершилась с кодом !ERRORLEVEL!
    pause
    exit /b 1
)

del /q "%INSTALLER%" 2>nul
set "PATH=%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts"

:create_venv
echo.
echo ============================================
echo  Шаг 2: Создание виртуального окружения
echo ============================================

if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Виртуальное окружение уже существует.
    goto :activate_venv
)

python -m venv "%VENV_DIR%"
if !ERRORLEVEL! NEQ 0 (
    echo ОШИБКА: Не удалось создать venv.
    pause
    exit /b 1
)

:activate_venv
echo.
echo ============================================
echo  Шаг 3: Активация venv и установка requirements
echo ============================================

call "%VENV_DIR%\Scripts\activate.bat"
if !ERRORLEVEL! NEQ 0 (
    echo ОШИБКА: Не удалось активировать venv.
    pause
    exit /b 1
)

python -m pip install --upgrade pip

if exist "%REQUIREMENTS%" (
    pip install -r "%REQUIREMENTS%"
) else (
    echo Файл "%REQUIREMENTS%" не найден. Пропускаем.
)

REM --- Гарантируем наличие huggingface_hub[cli] ---
pip show huggingface_hub >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Устанавливаем huggingface_hub[cli]...
    pip install "huggingface_hub[cli]"
)

echo.
echo ============================================
echo  Шаг 3.5: Скачивание модели Vosk (GitHub)
echo  в %MODELS_DIR%
echo ============================================

if not exist "%MODELS_DIR%" (
    echo Создаём папку "%MODELS_DIR%"...
    mkdir "%MODELS_DIR%" 2>nul
)

if exist "%VOSK_MODEL_PATH%" (
    echo Модель Vosk уже установлена: %VOSK_MODEL_PATH%
    goto :download_hf
)

echo Модель Vosk не найдена. Скачиваем с GitHub-зеркала...
echo URL: %VOSK_URL%

where curl >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo curl не найден. Используем PowerShell...
    powershell -NoProfile -Command ^
        "$ProgressPreference='SilentlyContinue';" ^
        "Invoke-WebRequest -Uri '%VOSK_URL%' -OutFile '%VOSK_ZIP%'"
) else (
    echo Используем curl с докачкой...
    curl -L --retry 5 --retry-delay 3 ^
         -C - -o "%VOSK_ZIP%" "%VOSK_URL%"
)

if not exist "%VOSK_ZIP%" (
    echo ОШИБКА: Не удалось скачать модель Vosk.
    pause
    exit /b 1
)

for %%A in ("%VOSK_ZIP%") do set ZIP_SIZE=%%~zA
if !ZIP_SIZE! LSS 1000000 (
    echo ОШИБКА: Файл слишком мал ^(!ZIP_SIZE! байт^).
    del /q "%VOSK_ZIP%" 2>nul
    pause
    exit /b 1
)

echo Распаковываем архив в "%MODELS_DIR%"...
powershell -NoProfile -Command "Expand-Archive -Path '%VOSK_ZIP%' -DestinationPath '%MODELS_DIR%' -Force"

if not exist "%VOSK_MODEL_PATH%" (
    echo ОШИБКА: После распаковки папка "%VOSK_MODEL_PATH%" не найдена.
    pause
    exit /b 1
)

del /q "%VOSK_ZIP%" 2>nul
echo Модель Vosk установлена: %VOSK_MODEL_PATH%

:download_hf
echo.
echo ============================================
echo  Шаг 3.7: Скачивание paraphrase-multilingual-MiniLM-L12-v2
echo  через зеркало %HF_ENDPOINT%
echo ============================================

if not exist "%MODELS_DIR%" mkdir "%MODELS_DIR%" 2>nul

if exist "%HF_LOCAL%\model.safetensors" (
    echo Модель Sentence-Transformers уже скачана: %HF_LOCAL%
    goto :run_main
)

echo Скачиваем модель...
echo Repo ID: %HF_MODEL%
echo Куда:    %HF_LOCAL%

huggingface-cli download %HF_MODEL% ^
    --local-dir "%HF_LOCAL%" ^
    --local-dir-use-symlinks False ^
    --resume-download

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo Зеркало %HF_ENDPOINT% не сработало. Пробуем оригинал...
    set HF_ENDPOINT=https://huggingface.co
    huggingface-cli download %HF_MODEL% ^
        --local-dir "%HF_LOCAL%" ^
        --local-dir-use-symlinks False ^
        --resume-download
)

if not exist "%HF_LOCAL%\model.safetensors" (
    echo ОШИБКА: model.safetensors не найден. Скачивание не удалось.
    pause
    exit /b 1
)

echo Модель Sentence-Transformers установлена: %HF_LOCAL%

:run_main
echo.
echo ============================================
echo  Шаг 4: Запуск %MAIN_SCRIPT%
echo ============================================

REM --- Передаём в main.py переменные для HF ---
set HF_ENDPOINT=%HF_ENDPOINT%
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

if exist "%MAIN_SCRIPT%" (
    python "%MAIN_SCRIPT%"
    set EXIT_CODE=!ERRORLEVEL!
    echo.
    if !EXIT_CODE! NEQ 0 (
        echo ОШИБКА: %MAIN_SCRIPT% завершился с кодом !EXIT_CODE!
    ) else (
        echo %MAIN_SCRIPT% успешно выполнен.
    )
) else (
    echo Файл "%MAIN_SCRIPT%" не найден в текущей папке.
)

echo.
echo ============================================
echo  Готово. Для выхода из venv: deactivate
echo ============================================
pause