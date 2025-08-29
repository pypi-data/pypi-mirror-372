import random
import time

import gradio as gr
from ctypes import c_int16

# import numpy as np
import wave
import os

WAV_FILE = "output.wav"
SAMPLE_RATE = 48000
CHANNELS = 1
SAMPLE_WIDTH = 2

total_bytes = 0
wav_handle = None


# ---------- 工具 ----------
def open_wav():
    global wav_handle
    if wav_handle is None:
        wav_handle = wave.open(WAV_FILE, "wb")
        wav_handle.setnchannels(CHANNELS)
        wav_handle.setsampwidth(SAMPLE_WIDTH)
        wav_handle.setframerate(SAMPLE_RATE)


def close_wav():
    global wav_handle
    if wav_handle is not None:
        wav_handle.close()
        wav_handle = None


# ---------- 回调 ----------
def on_chunk(audio_chunk):
    global total_bytes
    if audio_chunk is None:
        return total_bytes, None

    sr, data = audio_chunk
    print(sr, data)
    pcm_bytes = data.astype(c_int16).tobytes()

    open_wav()
    wav_handle.writeframes(pcm_bytes)

    total_bytes += len(pcm_bytes)
    return total_bytes, None  # 第二个 None 占位给播放器


def on_stop():
    """用户停止录音：关闭文件 + 返回路径供播放"""
    close_wav()
    # 如果文件存在，返回路径；否则返回 None
    path = WAV_FILE if os.path.isfile(WAV_FILE) else None
    return total_bytes, path


def text_nlu_tab():
    gr.Markdown("## Input text -> send")

    def echo_partial(text: str) -> str:
        """这里可以接入任何 LLM、TTS 等流式模型"""
        return text

    with gr.Row():
        inp = gr.Textbox(label="input")
        out = gr.Textbox(label="output")

        inp.input(fn=echo_partial, inputs=inp, outputs=out)


def audio_nlu_tab():
    gr.Markdown("## Recording → Saving → Replay")
    with gr.Row():
        mic = gr.Audio(
            sources=["microphone"],
            streaming=True,
            type="numpy",
            label="Microphone"
        )
        byte_num = gr.Number(label="Received Bytes", value=0)
    # 录音结束后自动出现播放器
    player = gr.Audio(label="Replay", interactive=False)
    # 流式处理
    mic.stream(
        fn=on_chunk,
        inputs=mic,
        outputs=[byte_num, player],
        stream_every=0.5
    )
    # 停止录音时收尾并加载播放器
    mic.stop_recording(
        fn=on_stop,
        outputs=[byte_num, player]
    )


# ---------- 前端 ----------
with gr.Blocks() as demo:
    with gr.Row(equal_height=False):
        with gr.Column(scale=2):  # "Working Space"
            with gr.Blocks():  # input
                with gr.Row():
                    gr.Markdown("## Input")
                with gr.Row():
                    with gr.Tab("Audio+NLU"):
                        audio_nlu_tab()
                    with gr.Tab("Text+NLU"):
                        text_nlu_tab()
            with gr.Blocks():  # output
                gr.Markdown("## Output")
        with gr.Column(scale=1):  # "log"
            with gr.Blocks():  # "参数-配置"
                gr.Markdown("## Config")
                gr.Markdown("### env")
                gr.Markdown("### headers")
                gr.Markdown("### request body")
            with gr.Blocks():  # 日志
                gr.Markdown("## Logs")


def main() -> None:
    demo.queue().launch()


if __name__ == "__main__":
    main()
