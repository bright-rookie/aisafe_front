import os
from datetime import datetime

import av
import cv2
import streamlit as st
from streamlit_webrtc import (
    AudioProcessorBase,
    ClientSettings,
    VideoTransformerBase,
    WebRtcMode,
    webrtc_streamer,
)

# WebRTC configuration for allowing video and audio streams
WEBRTC_CLIENT_SETTINGS = ClientSettings(
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": True, "audio": True},
)

# Title of the application
st.title("Webcam & Audio Recorder")


# Transformer for handling both video and audio
class VideoAudioTransformer(VideoTransformerBase, AudioProcessorBase):
    def __init__(self):
        self.is_recording = False
        self.video_out = None
        self.audio_out = None
        self.output_video_file = None
        self.output_audio_file = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # If recording, write frames to the video file
        if self.is_recording:
            if self.video_out is None:
                height, width, _ = img.shape
                # Create a new file name with a timestamp for each recording
                self.output_video_file = (
                    f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
                )
                # Define the codec and create VideoWriter object
                self.video_out = cv2.VideoWriter(
                    self.output_video_file,
                    cv2.VideoWriter_fourcc(*"XVID"),
                    20.0,
                    (width, height),
                )
            self.video_out.write(img)

        return img

    def recv_audio(self, frame: av.AudioFrame):
        # If recording, write audio data to the file
        if self.is_recording and self.audio_out is None:
            # Create a new file name with a timestamp for each recording
            self.output_audio_file = (
                f"output_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            )
            self.audio_out = open(self.output_audio_file, "wb")

        if self.is_recording:
            data = frame.to_ndarray()
            self.audio_out.write(data.tobytes())

    def start_recording(self):
        # Start recording video and audio
        self.is_recording = True
        st.info("Recording started...")

    def stop_recording(self):
        # Stop recording video and audio, and save the files
        self.is_recording = False

        if self.video_out is not None:
            self.video_out.release()
            self.video_out = None

        if self.audio_out is not None:
            self.audio_out.close()
            self.audio_out = None

        st.success(
            f"Recording saved as {self.output_video_file} and {self.output_audio_file}"
        )

    def save_video(self):
        # Display a download button for the video file if it exists
        if self.output_video_file and os.path.exists(self.output_video_file):
            with open(self.output_video_file, "rb") as video_file:
                st.download_button(
                    label="Download video",
                    data=video_file,
                    file_name=self.output_video_file,
                    mime="video/avi",
                )

        # Display a download button for the audio file if it exists
        if self.output_audio_file and os.path.exists(self.output_audio_file):
            with open(self.output_audio_file, "rb") as audio_file:
                st.download_button(
                    label="Download audio",
                    data=audio_file,
                    file_name=self.output_audio_file,
                    mime="audio/wav",
                )


# Instantiate the transformer class
transformer = VideoAudioTransformer()

# Start recording button
if st.button("Start Recording"):
    if transformer.is_recording:
        transformer.stop_recording()
    else:
        transformer.start_recording()

# WebRTC video and audio stream
webrtc_ctx = webrtc_streamer(
    key="example",
    mode=WebRtcMode.SENDRECV,
    client_settings=WEBRTC_CLIENT_SETTINGS,
    video_processor_factory=lambda: transformer,
    audio_processor_factory=lambda: transformer,
)

# Allow users to save and download the video/audio files
transformer.save_video()
