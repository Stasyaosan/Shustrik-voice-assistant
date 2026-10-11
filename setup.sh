#!/usr/bin/env bash
# ============================================================
#  Python 3.12 — venv, requirements,
#  скачивание Vosk (GitHub), Silero TTS (CDN),
#  paraphrase-multilingual-MiniLM-L12-v2 (hf-mirror.com),
#  запуск main.py
# ============================================================

set -e  # выход при ошибке

# --- Настройки Python ---
PYTHON_VERSION="3.12"
VENV_DIR=".venv"
REQUIREMENTS="requirements.txt"
MAIN_SCRIPT="main.py"

# --- Общая папка моделей ---
MODELS_DIR="utils/models"

# --- Модель Vosk (GitHub-зеркало) ---
VOSK_MODEL="vosk-model-small-ru-0.22"
VOSK_MODEL_PATH="${MODELS_DIR}/${VOSK_MODEL}"
VOSK_URL="https://github.com/kercre123/vosk-models/raw/main/${VOSK_MODEL}.zip"
VOSK_ZIP="/tmp/${VOSK_MODEL}.zip"

# --- Модель Silero TTS (официальный CDN) ---
SILERO_MODEL="v4_ru.pt"
SILERO_DIR="${MODELS_DIR}/silero"
SILERO_URL="https://models.silero.ai/models/tts/ru/${SILERO_MODEL}"

# --- Модель Sentence-Transformers (HF-зеркало) ---
HF_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
HF_LOCAL="${MODELS_DIR}/paraphrase-multilingual-MiniLM-L12-v2"
export HF_ENDPOINT="https://hf-mirror.com"
export HF_HUB_DISABLE_SYMLINKS_WARNING="1"

echo "============================================"
echo " Шаг 1: Проверка Python ${PYTHON_VERSION}"
echo "============================================"

if command -v "python${PYTHON_VERSION}" >/dev/null 2>&1; then
    PYTHON_BIN="python${PYTHON_VERSION}"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "ОШИБКА: Python не найден. Установите Python ${PYTHON_VERSION} вручную."
    exit 1
fi

echo "Используем: $($PYTHON_BIN --version)"

echo
echo "============================================"
echo " Шаг 2: Создание виртуального окружения"
echo "============================================"

if [ -f "${VENV_DIR}/bin/activate" ]; then
    echo "Виртуальное окружение уже существует."
else
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    echo "venv создан."
fi

echo
echo "============================================"
echo " Шаг 3: Активация venv и установка requirements"
echo "============================================"

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip

if [ -f "$REQUIREMENTS" ]; then
    pip install -r "$REQUIREMENTS"
else
    echo "Файл ${REQUIREMENTS} не найден. Пропускаем."
fi

# --- Гарантируем наличие huggingface_hub[cli] ---
if ! pip show huggingface_hub >/dev/null 2>&1; then
    echo "Устанавливаем huggingface_hub[cli]..."
    pip install "huggingface_hub[cli]"
fi

echo
echo "============================================"
echo " Шаг 3.5: Скачивание модели Vosk (GitHub)"
echo " в ${MODELS_DIR}"
echo "============================================"

mkdir -p "$MODELS_DIR"

if [ -d "$VOSK_MODEL_PATH" ]; then
    echo "Модель Vosk уже установлена: ${VOSK_MODEL_PATH}"
else
    echo "Модель Vosk не найдена. Скачиваем с GitHub-зеркала..."
    echo "URL: ${VOSK_URL}"

    if command -v curl >/dev/null 2>&1; then
        curl -L --retry 5 --retry-delay 3 -C - -o "$VOSK_ZIP" "$VOSK_URL"
    elif command -v wget >/dev/null 2>&1; then
        wget -c -O "$VOSK_ZIP" "$VOSK_URL"
    else
        echo "ОШИБКА: ни curl, ни wget не найдены."
        exit 1
    fi

    if [ ! -f "$VOSK_ZIP" ]; then
        echo "ОШИБКА: не удалось скачать модель Vosk."
        exit 1
    fi

    ZIP_SIZE=$(stat -c%s "$VOSK_ZIP" 2>/dev/null || stat -f%z "$VOSK_ZIP")
    if [ "$ZIP_SIZE" -lt 1000000 ]; then
        echo "ОШИБКА: файл слишком мал (${ZIP_SIZE} байт)."
        rm -f "$VOSK_ZIP"
        exit 1
    fi

    echo "Распаковываем архив в ${MODELS_DIR}..."
    if command -v unzip >/dev/null 2>&1; then
        unzip -q -o "$VOSK_ZIP" -d "$MODELS_DIR"
    else
        python -c "import zipfile; zipfile.ZipFile('${VOSK_ZIP}').extractall('${MODELS_DIR}')"
    fi

    if [ ! -d "$VOSK_MODEL_PATH" ]; then
        echo "ОШИБКА: после распаковки папка ${VOSK_MODEL_PATH} не найдена."
        exit 1
    fi

    rm -f "$VOSK_ZIP"
    echo "Модель Vosk установлена: ${VOSK_MODEL_PATH}"
fi

echo
echo "============================================"
echo " Шаг 3.6: Скачивание модели Silero TTS"
echo " в ${SILERO_DIR}"
echo "============================================"

mkdir -p "$SILERO_DIR"

if [ -f "${SILERO_DIR}/${SILERO_MODEL}" ]; then
    echo "Модель Silero уже скачана: ${SILERO_DIR}/${SILERO_MODEL}"
else
    echo "Скачиваем Silero TTS..."
    echo "URL: ${SILERO_URL}"

    if command -v curl >/dev/null 2>&1; then
        curl -L --retry 5 --retry-delay 3 -C - \
             -o "${SILERO_DIR}/${SILERO_MODEL}" "$SILERO_URL"
    elif command -v wget >/dev/null 2>&1; then
        wget -c -O "${SILERO_DIR}/${SILERO_MODEL}" "$SILERO_URL"
    else
        echo "ОШИБКА: ни curl, ни wget не найдены."
        exit 1
    fi

    if [ ! -f "${SILERO_DIR}/${SILERO_MODEL}" ]; then
        echo "ОШИБКА: не удалось скачать модель Silero."
        exit 1
    fi

    SILERO_SIZE=$(stat -c%s "${SILERO_DIR}/${SILERO_MODEL}" 2>/dev/null || stat -f%z "${SILERO_DIR}/${SILERO_MODEL}")
    if [ "$SILERO_SIZE" -lt 10000000 ]; then
        echo "ОШИБКА: файл слишком мал (${SILERO_SIZE} байт)."
        rm -f "${SILERO_DIR}/${SILERO_MODEL}"
        exit 1
    fi

    echo "Модель Silero установлена: ${SILERO_DIR}/${SILERO_MODEL}"
fi

echo
echo "============================================"
echo " Шаг 3.7: Скачивание paraphrase-multilingual-MiniLM-L12-v2"
echo " через зеркало ${HF_ENDPOINT}"
echo "============================================"

mkdir -p "$MODELS_DIR"

if [ -f "${HF_LOCAL}/model.safetensors" ]; then
    echo "Модель Sentence-Transformers уже скачана: ${HF_LOCAL}"
else
    echo "Скачиваем модель..."
    echo "Repo ID: ${HF_MODEL}"
    echo "Куда:    ${HF_LOCAL}"

    if ! huggingface-cli download "$HF_MODEL" \
            --local-dir "$HF_LOCAL" \
            --local-dir-use-symlinks False \
            --resume-download; then

        echo
        echo "Зеркало ${HF_ENDPOINT} не сработало. Пробуем оригинал..."
        export HF_ENDPOINT="https://huggingface.co"
        huggingface-cli download "$HF_MODEL" \
            --local-dir "$HF_LOCAL" \
            --local-dir-use-symlinks False \
            --resume-download
    fi

    if [ ! -f "${HF_LOCAL}/model.safetensors" ]; then
        echo "ОШИБКА: model.safetensors не найден. Скачивание не удалось."
        exit 1
    fi

    echo "Модель Sentence-Transformers установлена: ${HF_LOCAL}"
fi

echo
echo "============================================"
echo " Шаг 4: Запуск ${MAIN_SCRIPT}"
echo "============================================"

if [ -f "$MAIN_SCRIPT" ]; then
    python "$MAIN_SCRIPT"
    EXIT_CODE=$?
    echo
    if [ $EXIT_CODE -ne 0 ]; then
        echo "ОШИБКА: ${MAIN_SCRIPT} завершился с кодом ${EXIT_CODE}"
        exit $EXIT_CODE
    else
        echo "${MAIN_SCRIPT} успешно выполнен."
    fi
else
    echo "Файл ${MAIN_SCRIPT} не найден в текущей папке."
fi

echo
echo "============================================"
echo " Готово. Для выхода из venv: deactivate"
echo "============================================"