import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import glob
from pydub import AudioSegment
import json
import wave
import sys

from vosk import Model, KaldiRecognizer



UPLOAD_FOLDER = './files' #ПУть для загрузки файлов
ALLOWED_EXTENSIONS = set(['wav']) # набор допустимых расширений

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#проверка допустимости файла
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#обработка файла
# передается в secure_filename имя файла и он возвращает безопасную версию
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template('index.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    filename_list = glob.glob('files/*.wav')
    filename = filename_list[-1]  # Последний файл

    #Преобразование стерео дорожки в моно
    sound = AudioSegment.from_wav(filename)
    sound = sound.set_channels(1)
    sound.export(filename, format="wav")

    #Обработка аудио файла и преобразование голоса в текст
    wf = wave.open(filename, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return "Audio file must be WAV format mono PCM."
        sys.exit(1)

    # You can also init model by name or with a folder path
    model = Model(model_name="vosk-model-ru-0.22")
    # model = Model("models/en")

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass
            # print(rec.Result()) # вывод промежуточных результатов
        else:
            pass
            # print(rec.PartialResult()) # вывод промежуточных результатов

    #запись текста в файл и его сохранение в директории
    with open("text_voice/voice_text.txt", "w", encoding="utf-8") as file:
        rec_text = json.loads(rec.FinalResult())
        file.write(f'{rec_text.get("text")}\n')

    #вывод результата на экран
    return f'{rec_text.get("text")}'


if __name__ == "__main__":
     app.run(debug=True)