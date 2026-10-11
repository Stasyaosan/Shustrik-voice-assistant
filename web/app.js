let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const audioPlayback = document.getElementById('audioPlayback');

// 1. Старт записи
startBtn.addEventListener('click', async () => {
  audioChunks = []; // Очищаем старые данные перед новой записью

  try {
    // Запрашиваем доступ к микрофону
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Создаем объект для записи
    mediaRecorder = new MediaRecorder(stream);

    // Собираем кусочки аудиоданных по мере их поступления
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data);
      }
    };

    // Когда запись остановлена — создаем файл
    mediaRecorder.onstop = () => {
      // Собираем все кусочки в один Blob-объект (аудиофайл)
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

      // Создаем локальную ссылку на этот файл
      const audioUrl = URL.createObjectURL(audioBlob);

      // 1. Выводим плеер на страницу для прослушивания
      audioPlayback.src = audioUrl;

      // 2. Автоматическое скачивание файла на компьютер
      const downloadLink = document.createElement('a');
      downloadLink.href = audioUrl;
      downloadLink.download = `recording_${Date.now()}.webm`; // Имя файла
      downloadLink.click();

      // Отключаем микрофон, чтобы иконка записи в браузере пропала
      stream.getTracks().forEach(track => track.stop());
    };

    // Запускаем запись
    mediaRecorder.start();

    startBtn.disabled = true;
    stopBtn.disabled = false;
    console.log("Запись пошла...");

  } catch (err) {
    console.error("Не удалось получить доступ к микрофону:", err);
    alert("Пожалуйста, разрешите доступ к микрофону в браузере.");
  }
});

// 2. Остановка записи
stopBtn.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop(); // Это вызовет событие onstop, описанное выше
    startBtn.disabled = false;
    stopBtn.disabled = true;
    console.log("Запись остановлена.");
  }
});
