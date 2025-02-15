# import streamlit as st
# import numpy as np
# import matplotlib.pyplot as plt
# import sounddevice as sd
# from scipy.signal import find_peaks

# # 피치 계산 함수
# def pitch_detection(audio, fs):
#     # 오디오 신호의 FFT를 계산
#     freqs = np.fft.fftfreq(len(audio), 1/fs)
#     fft = np.fft.fft(audio)
    
#     # 주파수의 절대값을 취함
#     magnitude = np.abs(fft)
    
#     # 피크 찾기
#     peaks, _ = find_peaks(magnitude, height=0)
#     if len(peaks) > 0:
#         # 가장 큰 피크의 주파수 반환
#         peak_freq = freqs[peaks][np.argmax(magnitude[peaks])]
#         return peak_freq
#     return 0

# # 스트림릿 앱 설정
# st.title("Real-time Pitch Detection")
# st.write("Press the button below to start recording audio.")

# # 오디오 녹음 버튼
# if st.button("Start Recording"):
#     fs = 44100  # 샘플링 주파수
#     duration = 5  # 녹음 시간 (초)
    
#     st.write("Recording...")
#     audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float64', device=1)
#     sd.wait()  # 녹음이 끝날 때까지 대기
#     st.write("Recording finished.")
    
#     # 피치 계산
#     pitch = pitch_detection(audio.flatten(), fs)
    
#     # 피치 그래프 그리기
#     plt.figure(figsize=(10, 4))
#     plt.plot(audio)
#     plt.title(f"Detected Pitch: {pitch:.2f} Hz")
#     plt.xlabel("Samples")
#     plt.ylabel("Amplitude")
#     st.pyplot(plt)

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pyaudio
import wave
from scipy.signal import find_peaks

# 피치 계산 함수
def pitch_detection(audio, fs):
    # 오디오 신호의 FFT를 계산
    freqs = np.fft.fftfreq(len(audio), 1/fs)
    fft = np.fft.fft(audio)
    
    # 주파수의 절대값을 취함
    magnitude = np.abs(fft)
    
    # 피크 찾기
    peaks, _ = find_peaks(magnitude, height=0)
    if len(peaks) > 0:
        # 가장 큰 피크의 주파수 반환
        peak_freq = freqs[peaks][np.argmax(magnitude[peaks])]
        return peak_freq
    return 0

# 오디오 녹음 함수
def record_audio(duration, fs):
    p = pyaudio.PyAudio()
    
    # 스트림 열기
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    input=True,
                    frames_per_buffer=1024)

    frames = []
    
    st.write("Recording...")
    for _ in range(0, int(fs / 1024 * duration)):
        data = stream.read(1024)
        frames.append(np.frombuffer(data, dtype=np.float32))
    
    st.write("Recording finished.")
    
    # 스트림 종료
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return np.concatenate(frames)

# 스트림릿 앱 설정
st.title("Real-time Pitch Detection with PyAudio")
st.write("Press the button below to start recording audio.")

# 오디오 녹음 버튼
if st.button("Start Recording"):
    fs = 44100  # 샘플링 주파수
    duration = 5  # 녹음 시간 (초)
    
    audio = record_audio(duration, fs)
    
    # 피치 계산
    pitch = pitch_detection(audio, fs)
    
    # 피치 그래프 그리기
    plt.figure(figsize=(10, 4))
    plt.plot(audio)
    plt.title(f"Detected Pitch: {pitch:.2f} Hz")
    plt.xlabel("Samples")
    plt.ylabel("Amplitude")
    st.pyplot(plt)
