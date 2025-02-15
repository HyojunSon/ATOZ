import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import librosa
import streamlit as st
import threading

def get_audio_devices():
    p = pyaudio.PyAudio()
    device_list = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            device_list.append((i, info['name']))
    p.terminate()
    return device_list

# 오디오 장치 목록 가져오기
audio_devices = get_audio_devices()

# Streamlit 설정
st.title("실시간 피치 그래프")
st.write("음성 데이터를 입력 받아 실시간으로 피치 그래프를 그립니다.")

# 오디오 장치 선택
device_names = [device[1] for device in audio_devices]
device_index = st.selectbox("오디오 장치 선택", range(len(device_names)), format_func=lambda x: device_names[x])

# 선택한 장치 인덱스 가져오기
input_device_index = audio_devices[device_index][0]

# PyAudio 설정
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# PyAudio 인스턴스 생성
p = pyaudio.PyAudio()

# 스트림 열기
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=input_device_index,
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
