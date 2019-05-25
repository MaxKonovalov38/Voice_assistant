# импортируем модули
import pyaudio
import wave

# Константы:
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 20
#WAVE_OUTPUT_FILENAME = "output.wav"  # !!!

# Функция записи:
def record_audio(filename='speech.wav'):
    p = pyaudio.PyAudio()

    stream = p.open(format = FORMAT,
	    channels = CHANNELS,
	    input = True,
	    frames_per_buffer = CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    frames.append(data)

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

#
def main():
	record_audio()
	#sleep()
	play_audio()

if __name__ == 'main':
	main()