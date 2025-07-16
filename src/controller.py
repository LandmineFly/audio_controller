import threading
import time
import os
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
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.update_thread = None
        self.is_thread_running: bool = False

    def play(self, file_path):
        if self.current_audio:
            if (not self.is_playing or self.is_paused):
                pygame.mixer.music.play(start=self.elapsed_time)
                pygame.mixer.music.unpause()
        elif self._load_audio(file_path):
            if (not self.is_playing or self.is_paused):
                pygame.mixer.music.play()
        else:
            return False
        self.is_playing = True
        self.is_paused = False
        self.start_time = time.time() - self.elapsed_time
        self._start_update_thread()
        # self.update_thread.join()
        return True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.elapsed_time = 0
        self.start_time = 0
        self.current_audio = None
        return True

    def pause(self):
        """暂停播放"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            # self.on_pause and self.on_pause()
            return True
        return False

    def unpause(self):
        """继续播放"""
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.start_time = time.time() - self.elapsed_time  # 更新开始时间
            self._start_update_thread()
            # self.on_unpause and self.on_unpause()
            return True
        return False

    def _load_audio(self, file_path):
        if not os.path.exists(file_path):
            print(f"歌曲文件不存在: {file_path}")
            return False

        self.current_audio = file_path
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
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
                raise ValueError("不支持的音频文件格式")
        except Exception as e:
            print(f"获取音频时长失败: {e}")
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
