import os
from os import path

from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import glob
from pydub import AudioSegment

import speech_recognition as sr




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
    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "our_sound.wav")

    # use the audio file as the audio source
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = r.record(source)  # read the entire audio file

        #запись текста в файл и его сохранение в директории
    with open('text_voice/textttt.txt', 'w', encoding='utf-8') as fil:
        fil.write(r.recognize_google(audio, language="ru-RU") + '\n')

    return r.recognize_google(audio, language='ru_RU')

    #вывод результата на экран
    # return f'{rec_text.get("text")}'


if __name__ == "__main__":
     app.run(debug=True)