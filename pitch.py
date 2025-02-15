import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import numpy as np
import matplotlib.pyplot as plt
import librosa

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.sr = 44100
        self.chunk_size = 1024
        self.fig, self.ax = plt.subplots()
        self.x = np.arange(0, 2 * self.chunk_size, 2)
        self.line, = self.ax.plot(self.x, np.random.rand(self.chunk_size))
        self.ax.set_ylim(0, 5000)
        self.ax.set_xlim(0, self.chunk_size)

    def recv(self, frame):
        audio_data = np.frombuffer(frame.to_ndarray(), dtype=np.int16)
        pitch = librosa.core.pitch.yin(audio_data.astype(float), fmin=50, fmax=500)
        self.line.set_ydata(pitch)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        return frame

st.title("실시간 피치 그래프")
st.write("음성 데이터를 입력 받아 실시간으로 피치 그래프를 그립니다.")

webrtc_ctx = webrtc_streamer(
    key="example",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

if webrtc_ctx.state.playing:
    st.pyplot(webrtc_ctx.audio_processor.fig)
