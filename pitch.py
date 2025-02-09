import streamlit as st
import numpy as np
import librosa
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import queue
import asyncio

# Streamlit 앱 설정
st.title("실시간 음성 피치 분석기")

# 전역 변수 설정
SAMPLE_RATE = 16000
frame_queue = queue.Queue()
pitch_queue = queue.Queue()

# 피치 분석 함수
def analyze_pitch(audio_frame):
    signal = audio_frame.to_ndarray().flatten()
    pitch, _ = librosa.piptrack(y=signal, sr=SAMPLE_RATE)
    pitch = pitch[pitch > 0]
    if len(pitch) > 0:
        mean_pitch = np.mean(pitch)
        return mean_pitch
    return None

# 오디오 프레임 처리 콜백
def audio_frame_callback(frame):
    sound = frame.to_ndarray().flatten()
    frame_queue.put(sound)
    return frame

# WebRTC 설정
rtc_configuration = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
webrtc_ctx = webrtc_streamer(
    key="audio-streaming",
    mode=WebRtcMode.SENDONLY,
    rtc_configuration=rtc_configuration,
    audio_receiver_size=1024,
    media_stream_constraints={"video": False, "audio": True},
)

# 실시간 분석 및 그래프 업데이트
if webrtc_ctx.state.playing:
    pitches = []
    while True:
        
# 그래프 초기화
fig, ax = plt.subplots()
line, = ax.plot([], [])
ax.set_xlim(0, 100)
ax.set_ylim(0, 1000)
ax.set_xlabel("Time (Frame)")
ax.set_ylabel("Pitch (Hz)")
ax.set_title("Realtime Pitch Graph")
graph = st.pyplot(fig)

# 상태 관리를 위한 세션 상태 초기화
if 'pitches' not in st.session_state:
    st.session_state.pitches = []

# 비동기 데이터 처리 함수
async def process_audio():
    while webrtc_ctx.state.playing:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                for audio_frame in audio_frames:
                    pitch = analyze_pitch(audio_frame)
                    if pitch:
                        st.session_state.pitches.append(pitch)
                        if len(st.session_state.pitches) > 100:
                            st.session_state.pitches.pop(0)
                await asyncio.sleep(0.1)  # 짧은 대기 시간
            except queue.Empty:
                continue
        else:
            break

# 그래프 업데이트 함수
def update_graph():
    line.set_xdata(range(len(st.session_state.pitches)))
    line.set_ydata(st.session_state.pitches)
    ax.relim()
    ax.autoscale_y()
    graph.pyplot(fig)

# 메인 실행 부분
if webrtc_ctx.state.playing:
    graph_placeholder = st.empty()
    
    # 비동기 처리 시작
    asyncio.run(process_audio())
    
    # 주기적 그래프 업데이트
    while True:
        update_graph()
        graph_placeholder.pyplot(fig)
        st.experimental_rerun()

st.write("마이크를 통해 음성을 입력하면 실시간으로 피치가 분석됩니다.")
