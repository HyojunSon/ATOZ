import streamlit as st
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# 스트림릿 앱 설정
st.set_page_config(page_title="Real-time Pitch Detection", layout="wide")

st.title("Real-time Pitch Detection")
st.write("This app captures audio in real-time and plots the pitch graph.")

# 샘플링 레이트와 버퍼 크기 설정
SAMPLING_RATE = 44100
BUFFER_SIZE = 2048

# 실시간 오디오 스트림 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        st.warning(f"Warning: {status}")
    audio_buffer.extend(indata[:, 0])

# 오디오 버퍼 초기화
audio_buffer = []

# 오디오 스트림 시작
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLING_RATE, blocksize=BUFFER_SIZE)
stream.start()

# 실시간 피치 그래프 그리기
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.set_ylim(0, 1000)
ax.set_xlim(0, BUFFER_SIZE)
ax.set_xlabel("Samples")
ax.set_ylabel("Frequency (Hz)")

def update_plot():
    if len(audio_buffer) >= BUFFER_SIZE:
        data = np.array(audio_buffer[-BUFFER_SIZE:])
        audio_buffer.clear()
        
        # FFT를 사용하여 주파수 스펙트럼 계산
        fft_spectrum = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(len(data), 1/SAMPLING_RATE)
        magnitudes = np.abs(fft_spectrum)
        
        # 피크 주파수 찾기
        peaks, _ = find_peaks(magnitudes, height=0.1)
        if peaks.size > 0:
            pitch = freqs[peaks[0]]
        else:
            pitch = 0
        
        # 그래프 업데이트
        line.set_data(np.arange(len(data)), data)
        ax.set_title(f"Detected Pitch: {pitch:.2f} Hz")
        fig.canvas.draw()
        fig.canvas.flush_events()

# 스트림릿 앱 메인 루프
while True:
    update_plot()
    st.pyplot(fig)
