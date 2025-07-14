import queue
import threading
import subprocess
import time


# TODO: 添加日志记录
# TODO: 强制退出时杀死subprocess.Popen开启的子进程
# TODO: 添加音频播放错误处理
# BUG: 连续（连续代码）下一首时，由于没执行到_play_audio，下一首操作会失效
class AudioPlayer:
    def __init__(self):
        self.play_queue = queue.Queue()
        self.lock = threading.Lock()
        self.current_process = None
        self.interrupt_audio = None
        self.is_running = True
        # 守护进程不会阻塞主程序退出，当所有非守护线程结束后，守护线程会自动终止
        threading.Thread(target=self._queue_handler, daemon=True).start()

    def _queue_handler(self):
        while self.is_running:
            audio_path = None

            with self.lock:
                if self.interrupt_audio:
                    audio_path = self.interrupt_audio
                    self.interrupt_audio = None
            if audio_path is None:
                try:
                    audio_path = self.play_queue.get(timeout=0.3)
                except queue.Empty:
                    continue
            print(
                f"""start print:
                queue_size: {self.play_queue.qsize()}
                audio_path: {audio_path}
                interrupt_audio: {self.interrupt_audio}
                """
            )

            with self.lock:
                if self.interrupt_audio:
                    continue
                self._terminate_current_process()
                self.current_process = self._play_audio(audio_path)

            self.current_process.wait()

            with self.lock:
                self.current_process = None

    def enqueue(self, file_path):
        with self.lock:
            self.play_queue.put(file_path)

    def interrupt(self, file_path):
        with self.lock:
            self._terminate_current_process()
            self.interrupt_audio = file_path

    def next_audio(self):
        with self.lock:
            self._terminate_current_process()

            

    def _play_audio(self, file_path):
        return subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
            )
    
    def _clear_queue(self):
        with self.lock:
            self.queue.clear()
    
    def _terminate_current_process(self):
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                print("进程未响应，正在强制 kill")
                self.current_process.kill()
            self.current_process = None

