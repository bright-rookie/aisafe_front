import time
import streamlit as st

import cv2
import tempfile
import os
import moviepy.editor as mp
import base64
import pyaudio
import wave
import threading

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




# Button 1: Start Video Recording using OpenCV
def record_video() :
    cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 20.0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
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
    # final_video = video.set_audio(audio)
    # recorded_file_path = temp_video_file.name.replace('.mp4', '_final.mp4')
    # final_video.write_videofile(recorded_file_path, codec='libx264', audio_codec='aac', fps=fps)

    return video.name, audio.name


"""    st.video(recorded_file_path)

    with open(recorded_file_path, "rb") as file:
        btn = st.download_button(
            label="Download Recorded Video",
            data=file,
            file_name="recorded_video.mp4",
            mime="video/mp4"
        )
"""

# Button 2: Upload Video File
def video_dissembly(uploaded_video) :
    # Save uploaded video to a temporary file
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video_file.write(uploaded_video.read())
    temp_video_file.close()

    # Use moviepy to separate video with and without audio
    video = mp.VideoFileClip(temp_video_file.name)
    audio_only = video.audio
    video_only = video.without_audio()

    return audio_only.name, video_only.name
