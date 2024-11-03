import os
import cv2
import time
import wave
import pyaudio
import threading
import tempfile
import ffmpeg
import moviepy.editor as mp

# Audio recording function
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


# Video recording function
def record_video():
    cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 20.0
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Temporary files for video and audio
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    out = cv2.VideoWriter(temp_video_file.name, fourcc, fps, (int(cap.get(3)), int(cap.get(4))))

    # Audio recording setup
    audio_frames = []
    stop_event = threading.Event()
    audio_thread = threading.Thread(target=record_audio, args=(temp_audio_file.name, audio_frames, stop_event))

    # Start audio and video recording simultaneously
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

    # Stop recording
    cap.release()
    out.release()
    stop_event.set()
    audio_thread.join()
    cv2.destroyAllWindows()

    # Separate audio and video using ffmpeg
    output_video = "output_video.mp4"
    output_audio = "output_audio.mp3"

    # Save audio only
    ffmpeg.input(temp_audio_file.name).output(output_audio).run(overwrite_output=True)

    # Save video without audio
    ffmpeg.input(temp_video_file.name).output(output_video, an=None).run(overwrite_output=True)

    return output_video, output_audio


# Upload video file and disassemble
def video_dissembly(uploaded_video):
    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video_file.write(uploaded_video.read())
    temp_video_file.close()

    video = mp.VideoFileClip(temp_video_file.name)
    audio_only = video.audio
    video_only = video.without_audio()

    # Save audio and video separately
    video_only.write_videofile("output_video.mp4", codec='libx264')
    audio_only.write_audiofile("output_audio.mp3")

    return "output_video.mp4", "output_audio.mp3"


# Save uploaded audio file
def audio_save(uploaded_audio):
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_audio_file.write(uploaded_audio.read())
    temp_audio_file.close()

    os.rename(temp_audio_file.name, "output_audio.mp3")

    return None, "output_audio.mp3"
