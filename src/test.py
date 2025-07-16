from controller import AudioPlayer
import time
import sys
import signal

if __name__ == "__main__":
    
    ap = AudioPlayer()

    ap.play("../audio/ykn.mp3")

    time.sleep(5)

    ap.stop()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")