import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import base64
import time

# JavaScript를 사용하여 오디오 녹음
def audio_recorder():
    st.markdown("""
    <script>
    let mediaRecorder;
    let audioChunks = [];
    let audioContext;
    let analyser;
    let dataArray;

    async function startRecording() {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 2048;
        dataArray = new Uint8Array(analyser.frequencyBinCount);

        mediaRecorder.ondataavailable = function(event) {
            audioChunks.push(event.data);
        };

        function updateGraph() {
            analyser.getByteFrequencyData(dataArray);
            const audioData = Array.from(dataArray);
            const audioDataBase64 = btoa(JSON.stringify(audioData));
            fetch('/update_graph', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ audioData: audioDataBase64 }),
            });
            requestAnimationFrame(updateGraph);
        }

        updateGraph();
    }

    function stopRecording() {
        mediaRecorder.stop();
        audioContext.close();
    }

    window.startRecording = startRecording;
    window.stopRecording = stopRecording;
    </script>
    """, unsafe_allow_html=True)

    st.button("Start Recording", on_click=startRecording)
    st.button("Stop Recording", on_click=stopRecording)

# 스트림릿 앱 설정
st.title("Real-time Audio Visualization")
st.write("Press the buttons below to start and stop recording audio.")

# 오디오 녹음 버튼
audio_recorder()

# 그래프 업데이트
if st.session_state.get("audio_data"):
    audio_data = st.session_state.audio_data
    audio_array = np.frombuffer(base64.b64decode(audio_data), dtype=np.uint8)

    # 그래프 그리기
    plt.figure(figsize=(10, 4))
    plt.bar(range(len(audio_array)), audio_array)
    plt.title("Real-time Audio Data")
    plt.xlabel("Frequency Bins")
    plt.ylabel("Amplitude")
    st.pyplot(plt)

# 오디오 데이터 업로드 처리
def update_graph():
    if st.session_state.get("audio_data"):
        st.session_state.audio_data = st.session_state.audio_data
    else:
        st.session_state.audio_data = None

st.experimental_singleton(update_graph)
