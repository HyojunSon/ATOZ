import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import librosa
import sounddevice as sd

st.title("실시간 음성 피치 분석")

SAMPLE_RATE = 22050
DURATION = 5  # 녹음 시간 (초)

if st.button("녹음 시작"):
    st.write("5초 동안 말씀해 주세요...")
    audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()
    st.write("녹음 완료!")

    # 피치 추출
    pitches, magnitudes = librosa.piptrack(y=audio.flatten(), sr=SAMPLE_RATE)
    
    # 시간 축 생성
    times = librosa.times_like(pitches)
    
    # 각 프레임에서 가장 강한 피치 선택
    pitches_filtered = np.zeros_like(times)
    for i in range(len(times)):
        index = magnitudes[:, i].argmax()
        pitches_filtered[i] = pitches[index, i]
    
    # 그래프 그리기
    fig, ax = plt.subplots()
    ax.plot(times, pitches_filtered)
    ax.set_xlabel("시간 (초)")
    ax.set_ylabel("피치 (Hz)")
    ax.set_title("실시간 음성 피치 분석")
    
    st.pyplot(fig)

st.write("'녹음 시작' 버튼을 클릭하여 음성을 녹음하고 피치 그래프를 확인하세요.")