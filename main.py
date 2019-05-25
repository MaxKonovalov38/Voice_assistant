# Импортируем модули
import os
import wave
from array import array
from datetime import datetime

import pyaudio
import requests
from bs4 import BeautifulSoup as bs


# Константы:
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 20
#WAVE_OUTPUT_FILENAME = "output.wav"  # !!!

USER_UUID = '86d656bbe650498592cbe2b0007c3ea8'
SPEECHKIT_API_KEY = 'KEY'

# Функция записи:
def record_audio(filename='speech.wav'):
    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
	    channels = CHANNELS,
	    input = True,
	    frames_per_buffer = CHUNK)

    print("* recording")

    frames = []

    silent_seconds = 0
    while silent_seconds < 3:
    	data = stream.read(CHUNK)
	    frames.append(data)

	    as_ints = array('h', data)
	    max_value = max(as_ints)

	    #print(max_value)
	    if max_value > 500:
	    	silent_seconds = 0
	    else:
	    	silent_seconds += CHUNK / RATE
	    #print(silent_seconds)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Функция воспроизведения:
def play_audio(filename='speech.wav'):
	wf = wave.open(filename, 'rb')

	p = pyaudio.PyAudio()

	stream = p.open(format = p.get_format_from_width(wf.getsapwidth()),
		channels = wf.getnchannels(),
		rate = wf.getframerate(),
		output = True)

	data = wf.readframes(CHUNK)

	while data:
		stream.write(data)
		data = wf.readframes(CHUNK)

	stream.stop_stream()
	stream.close()

	p.terminate()

# Функция отправки и обработки текста:
def speech_to_text(filename='speech.wav'):
	def read_in_chunks(file_object, blocksize=1024, chunks=-1):
		# Lazy function (generator) to read a file piece by piece.
		# Default chunk size: 1k.
		while chunks:
			data = file_object.read(blocksize)
			if not data:
				break
			yield data
			chunks -= 1

	result = requests.post(
		'https://asr.yandex.net/asr_xml',
		params={
		    'uuid': USER_UUID,
		    'key': SPEECHKIT_API_KEY,
		    'topic' : 'queries',
		},
		headers={
		    'Content-Type': 'audio/x-wav'
		},
		data=read_in_chunks(open(filename, 'rb'))
	)
	soup = bs(result.text, 'html.parser')
	return soup.variant.string

# Функция генерирования речи из теска:
def text_to_speech(text, emotion='neutral'):
	filename = 'wavs/{}.wav'.format(text.lower())
	if os.path.isfile(filename):
		play_audio(filename)
		return
	response = requests.get('https://tts.voicetech.yandex.net/generate',
		params={
		    'key': SPEECHKIT_API_KEY,
		    'text': text,
		    'format': 'wav',
		    'quality': 'hi',
		    'lang': 'ru-RU',
		    'speaker': 'oksana',
		    'emotion': emotion,
		}
	)
	if response.status_code == 200:
		with open(filename, 'wb') as f:
			f.write(response.content)

	play_audio(filename)

#
def main():
	text_to_speech('Привет!', 'good')
	while True:
		record_audio()
        text = speech_to_text()

        if text == 'привет':
        	text_to_speech('Как дела?', 'good')
        elif text in ['неплохо', 'хорошо', 'замечательно']:
        	text_to_speech('Здорово! У меня тоже.', 'good')
        elif text == 'сколько время':
        	text_to_speech('Правильно говорить который час', 'bad')
        elif text == 'который час':
        	text_to_speech('Сейчас {}'.format(datetime.now().strftime('%H:%M')))
        elif text == 'спасибо':
        	text_to_speech('Обращайся!', 'good')
        	break
        elif text.startswith('сколько будет'):
        	expr = text\
        	    .replace('сколько будет', '')\
        	    .replace('плюс', '+')\
        	    .replace('минус', '-')\
        	    .replace('умножить на', '*')\
        	    .replace('делить на', '/')
        	calc = str(eval(expr))
        	text_to_speech(calc)
        else:
        	text_to_speech('непонятно!!!', 'bad')

if __name__ == 'main':
	main()