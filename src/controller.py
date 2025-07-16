import queue
import threading
import subprocess
import time
import os
import pygame
from mutagen.mp3 import MP3
from mutagen.wave import WAVE

class AudioPlayer:
    def __init__(self):
        # self.play_queue = queue.Queue()
        # self.lock = threading.Lock()
        # self.current_process = None
        self.current_audio : str = None
        self.total_time : float = 0
        self.start_time : float = 0
        self.elapsed_time : float = 0
        self.is_playing : bool = False
        self.is_paused : bool = False
        self.update_thread = None
        self.is_thread_running : bool = False
        # self.interrupt_audio = None
        # self.is_running = True
        # 守护进程不会阻塞主程序退出，当所有非守护线程结束后，守护线程会自动终止
        # threading.Thread(target=self._queue_handler, daemon=True).start()

    # def _queue_handler(self):
    #     while self.is_running:
    #         audio_path = None

    #         with self.lock:
    #             if self.interrupt_audio:
    #                 audio_path = self.interrupt_audio
    #                 self.interrupt_audio = None
    #         if audio_path is None:
    #             try:
    #                 audio_path = self.play_queue.get(timeout=0.3)
    #             except queue.Empty:
    #                 continue

    #         self._print_data(audio_path=audio_path)

    #         with self.lock:
    #             if self.interrupt_audio:
    #                 continue
    #             self._terminate_current_process()
    #             self.current_playing = audio_path
    #             self.current_process = self._play_audio(audio_path)

    #         self.current_process.wait()

    #         with self.lock:
    #             self.current_process = None
    #             self.current_playing = None

    # def enqueue(self, file_path):
    #     time.sleep(0.01)
    #     with self.lock:
    #         self.play_queue.put(file_path)
    #     print(f"Added {file_path} to queue.")

    # def interrupt(self, file_path):
    #     time.sleep(0.01)
    #     with self.lock:
    #         self._terminate_current_process()
    #         self.interrupt_audio = file_path

    # def next_audio(self):
    #     time.sleep(0.01)
    #     if self.play_queue.empty():
    #         print("Queue is empty.")
    #         return
    #     with self.lock:
    #         self._terminate_current_process()

    # def clear_queue(self):
    #     time.sleep(0.01)
    #     with self.lock:
    #         while not self.play_queue.empty():
    #             self.play_queue.get_nowait()
    #         print("Queue cleared.")

    # def stop_and_clear_queue(self):
    #     time.sleep(0.01)
    #     with self.lock:
    #         while not self.play_queue.empty():
    #             self.play_queue.get_nowait()
    #         self._terminate_current_process()

    # def pause(self):
    #     time.sleep(0.01)
    #     with self.lock:
    #         self.current_process.send_signal(subprocess.signal.SIGSTOP)

    # def resume(self):
    #     time.sleep(0.01)
    #     with self.lock:
    #         self.current_process.send_signal(subprocess.signal.SIGCONT)

    # def get_play_list(self):
    #     time.sleep(0.01)
    #     return {'current_playing': self.current_playing, 'queue': list(self.play_queue.queue)}

    def play(self, file_path):
        self._load_audio(file_path)
        if self.current_audio:
            if not self.is_playing or self.is_paused:
                if self.elapsed_time == 0:
                    pygame.mixer.music.play()
                else:
                    pygame.mixer.music.play(start=self.elapsed_time)
                    pygame.mixer.music.unpause()
                self.is_playing = True
                self.is_paused = False
                self.start_time = time.time() - self.elapsed_time
                self._start_update_thread()
                # self.update_thread.join()
                return True
        return False

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.elapsed_time  = 0
        self.start_time = 0
        return True

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
            self.update_thread = threading.Thread(
                target=self._update_progress, 
                daemon=True
            )
            self.update_thread.start()
    
    def _update_progress(self):
        while self.is_thread_running:
            self._print_data()
            if self.is_playing and not self.is_paused:
                self.elapsed_time = time.time() - self.start_time
                self.on_progress and self.on_progress(self.elapsed_time)
                # 自然播放完毕
                if self.elapsed_time >= self.total_time:
                    self.stop()
                    # self.on_stop and self.on_stop()
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

    # def _play_audio(self, file_path):
    #     return subprocess.Popen(
    #         ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path],
    #         stdout=subprocess.DEVNULL,
    #         stderr=subprocess.DEVNULL
    #         )
    #
    # def _terminate_current_process(self):
    #     if self.current_process:
    #         try:
    #             self.current_process.terminate()
    #             self.current_process.wait(timeout=0.5)
    #         except subprocess.TimeoutExpired:
    #             print("Warning: process not responding, forcing kill")
    #             self.current_process.kill()
    #         self.current_process = None

    # def _print_data(self, audio_path = None):
    #     print(
    #             f"""start print:
    #             queue: {list(self.play_queue.queue)}
    #             queue_size: {self.play_queue.qsize()}
    #             {f"audio_path: {audio_path}" if audio_path else ""}
    #             interrupt_audio: {self.interrupt_audio}
    #             current_playing: {self.current_playing}
    #             """
    #             )

    def _print_data(self):
        print(
                f"""start print:
                current_audio: {self.current_audio}
                total_time: {self.total_time}
                start_time: {self.start_time}
                elapsed_time: {self.elapsed_time}
                is_playing: {self.is_playing}
                is_paused: {self.is_paused}
                update_thread: {self.update_thread}
                is_thread_running: {self.is_thread_running}
                """
                )