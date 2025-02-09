import streamlit as st
import numpy as np
import librosa
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.io import wavfile

# 마이크 설정
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048

# Streamlit 앱 설정
st.title("실시간 음성 피치 분석기")

# 마이크 권한 요청
if st.button("마이크 권한 요청"):
    try:
        sd.query_devices()
        st.success("마이크 권한이 승인되었습니다.")
    except sd.PortAudioError:
        st.error("마이크 권한을 승인해주세요.")

# 실시간 피치 분석 함수
def analyze_pitch(indata, frames, time, status):
    if status:
        print(status)
    if any(indata):
        signal = np.frombuffer(indata, dtype=np.float32)
        pitch, _ = librosa.piptrack(y=signal, sr=SAMPLE_RATE)
        pitch = pitch[pitch > 0]
        if len(pitch) > 0:
            mean_pitch = np.mean(pitch)
            st.session_state.pitches.append(mean_pitch)
            st.session_state.times.append(time)

# 그래프 초기화
if 'pitches' not in st.session_state:
    st.session_state.pitches = []
    st.session_state.times = []

# 실시간 분석 시작/중지
if st.button("분석 시작/중지"):
    if 'stream' not in st.session_state:
        st.session_state.stream = sd.InputStream(callback=analyze_pitch, channels=1, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE)
        st.session_state.stream.start()
        st.success("분석이 시작되었습니다.")
    else:
        st.session_state.stream.stop()
        del st.session_state.stream
        st.warning("분석이 중지되었습니다.")

# 실시간 그래프 표시
fig, ax = plt.subplots()
line, = ax.plot(st.session_state.times, st.session_state.pitches)
ax.set_xlabel("시간 (초)")
ax.set_ylabel("피치 (Hz)")
ax.set_title("실시간 음성 피치")

graph = st.pyplot(fig)

# 그래프 업데이트
def update_graph():
    line.set_xdata(st.session_state.times)
    line.set_ydata(st.session_state.pitches)
    ax.relim()
    ax.autoscale_view()
    graph.pyplot(fig)

# 주기적으로 그래프 업데이트
if 'stream' in st.session_state:
    st.empty()
    while True:
        update_graph()
        st.experimental_rerun()
