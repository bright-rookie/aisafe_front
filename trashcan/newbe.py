import streamlit as st
import cv2
import tempfile
import os
import moviepy.editor as mp
import base64
import pyaudio
import wave
import time
import threading

# Define button states
video_recorded = False
video_uploaded = False
audio_uploaded = False
recorded_file_path = None

def record_audio(output_file, frames, stop_event):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    rate = 44100
    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=rate,
                    frames_per_buffer=chunk,
                    input=True)

    while not stop_event.is_set():
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

st.title("Media Upload Page")

# Button 1: Start Video Recording using OpenCV
if st.button("Start video recording"):
    # Using OpenCV to start webcam recording
    st.info("Recording will automatically stop after 1 minute.")
    cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 20.0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    out = cv2.VideoWriter(temp_video_file.name, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    # Prepare for audio recording
    audio_frames = []
    stop_event = threading.Event()
    audio_thread = threading.Thread(target=record_audio, args=(temp_audio_file.name, audio_frames, stop_event))

    # Start both audio and video recording simultaneously
    audio_thread.start()
    start_time = time.time()
    while (time.time() - start_time) < 60:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Recording...', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Stop video and audio recording
    cap.release()
    out.release()
    stop_event.set()
    audio_thread.join()
    cv2.destroyAllWindows()

    # Combine audio and video using moviepy
    video = mp.VideoFileClip(temp_video_file.name)
    audio = mp.AudioFileClip(temp_audio_file.name)
    final_video = video.set_audio(audio)
    recorded_file_path = temp_video_file.name.replace('.mp4', '_final.mp4')
    final_video.write_videofile(recorded_file_path, codec='libx264', audio_codec='aac', fps=fps)

    video_recorded = True
    st.success("Video recording saved successfully.")
    st.video(recorded_file_path)

    with open(recorded_file_path, "rb") as file:
        btn = st.download_button(
            label="Download Recorded Video",
            data=file,
            file_name="recorded_video.mp4",
            mime="video/mp4"
        )

# Button 2: Upload Video File
uploaded_video = st.file_uploader("Upload video file (MP4)", type=['mp4'])
if uploaded_video:
    video_uploaded = True
    st.success("Video file uploaded successfully.")

    # Save uploaded video to a temporary file
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video_file.write(uploaded_video.read())
    temp_video_file.close()

    # Use moviepy to separate video with and without audio
    video = mp.VideoFileClip(temp_video_file.name)
    video_with_audio = video
    video_without_audio = video.without_audio()

    st.success("Video has been separated into versions with and without audio.")

# Button 3: Upload Audio File
uploaded_audio = st.file_uploader("Upload audio file (MP3)", type=['mp3'])
if uploaded_audio:
    audio_uploaded = True
    st.success("Audio file uploaded successfully.")

# Proceed to next step
if video_recorded or video_uploaded or audio_uploaded:
    st.button("Proceed to Next Step")
else:
    st.warning("You must either record a video or upload a video or an audio file to proceed.")
