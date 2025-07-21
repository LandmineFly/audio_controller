import threading
import time
import os
import sys
import pygame
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from fastapi import WebSocket
import asyncio


class AudioPlayer:

    def __init__(self):
        self.loop = None
        self.websocket: WebSocket = None

        self.current_audio: str = None
        self.total_time: float = 0
        self.start_time: float = 0
        self.elapsed_time: float = 0
        # 未播放或停止, playing=False, paused=False;
        # 正在播放, playing=True, paused=False;
        # 暂停, playing=True, paused=True;
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.update_thread = None
        self.is_thread_running: bool = False

    def play(self, file_path):
        if not os.path.exists(file_path):
            print(f"[ERROR] Audio file does not exist: [{file_path}]",
                  flush=True)
            return False

        try:
            # 恢复播放
            if self.current_audio and os.path.samefile(self.current_audio,
                                                       file_path):
                if (not self.is_playing or self.is_paused):
                    # 初始化声卡
                    pygame.mixer.init()
                    pygame.mixer.music.load(self.current_audio)

                    pygame.mixer.music.play(start=self.elapsed_time)
                    pygame.mixer.music.unpause()
                # else:
                #     print(
                #         f"[WARN] Try to play the audio file which is already playing: [{self.current_audio}], miss",
                #         flush=True)
            # 开始播放
            elif self._load_audio(file_path):
                # if (not self.is_playing or self.is_paused):
                pygame.mixer.music.play()
        except Exception as e:
            print(f"[ERROR] Failed to play audio: [{file_path}], {e}",
                  flush=True)
            return False
        self.is_playing = True
        self.is_paused = False
        self.start_time = time.time() - self.elapsed_time
        self._start_update_thread()
        return True

    def stop(self):
        pygame.mixer.music.stop()
        # 释放声卡
        pygame.mixer.quit()
        self.is_playing = False
        self.is_paused = False
        self.elapsed_time = 0
        self.start_time = 0
        # self.current_audio = None
        return True

    def pause(self):
        """暂停播放"""
        if self.current_audio and (self.is_playing and not self.is_paused):
            pygame.mixer.music.pause()
            # 释放声卡
            pygame.mixer.quit()
            self.is_paused = True
            # self.on_pause and self.on_pause()
            return True
        # elif not self.current_audio:
        #     print(f"[WARN] No loaded audio file", flush=True)
        # else:
        #     print(
        #         f"[WRAN] Try to pause the audio file which is not playing or already paused: [{self.current_audio}], miss",
        #         flush=True)
        return False

    def resume(self):
        """继续播放"""
        if self.current_audio and (not self.is_playing or self.is_paused):
            return self.play(self.current_audio)
        # elif not self.current_audio:
        #     print(f"[WARN] No loaded audio file", flush=True)
        # else:
        #     print(
        #         f"[WRAN] Try to resume the audio file which is already playing: [{self.current_audio}], miss",
        #         flush=True)
        return False

    def _load_audio(self, file_path):
        # 初始化声卡
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        self.current_audio = file_path
        self.is_playing = False
        self.is_paused = False
        self.elapsed_time = 0
        self.start_time = 0
        self._update_total_sec()
        return True

    def _update_total_sec(self):
        if not self.current_audio:
            return
        try:
            if self.current_audio.endswith('.mp3'):
                audio = MP3(self.current_audio)
                self.total_time = audio.info.length
            elif self.current_audio.endswith('.wav'):
                audio = WAVE(self.current_audio)
                self.total_time = audio.info.length
            else:
                raise ValueError("Unsupported audio format")
        except Exception as e:
            print(f"[ERROR] Failed to get audio duration: {e}", flush=True)
            self.total_time = 0

    def _start_update_thread(self):
        if not self.is_thread_running:
            self.is_thread_running = True
            self.update_thread = threading.Thread(target=self._update_progress,
                                                  daemon=True)
            self.update_thread.start()

    def _update_progress(self):
        while self.is_thread_running:
            if self.is_playing and not self.is_paused:
                self.elapsed_time = time.time() - self.start_time

                asyncio.run_coroutine_threadsafe(
                    self._on_progress(self.elapsed_time), self.loop)

                # 自然播放完毕
                if self.elapsed_time >= self.total_time:
                    self.stop()
                    asyncio.run_coroutine_threadsafe(self._on_stop(),
                                                     self.loop)
                    self.is_thread_running = False
                    break
            elif self.is_paused:
                # 手动暂停
                # self.on_pause and self.on_pause()
                self.is_thread_running = False
                break
            elif not self.is_playing:
                # 手动停止
                # self.on_stop and self.on_stop()
                self.is_thread_running = False
                break
            time.sleep(0.1)  # 每100毫秒更新一次

    async def _on_progress(self, progress):
        await self.websocket.send_json({
            "type": "play_progress",
            "data": progress
        })

    async def _on_stop(self):
        await self.websocket.send_json({"type": "play_end"})
