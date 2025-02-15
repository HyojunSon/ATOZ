import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import librosa
import streamlit as st
import threading

# Streamlit 설정
st.title("실시간 피치 그래프")
st.write("음성 데이터를 입력 받아 실시간으로 피치 그래프를 그립니다.")

# PyAudio 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# 실시간 피치 그래프 그리기
fig, ax = plt.subplots()
x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))
ax.set_ylim(0, 5000)
ax.set_xlim(0, CHUNK)

def update_plot():
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        pitch = librosa.core.pitch.yin(data.astype(float), fmin=50, fmax=500)
        line.set_ydata(pitch)
        fig.canvas.draw()
        fig.canvas.flush_events()

thread = threading.Thread(target=update_plot)
thread.start()

st.pyplot(fig)

# 스트림 종료
stream.stop_stream()
stream.close()
p.terminate()
