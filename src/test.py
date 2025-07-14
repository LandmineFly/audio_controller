from controller import AudioPlayer
import time

if __name__ == "__main__":
    ap = AudioPlayer()
    
    ap.enqueue("../audio/ykn.mp3")
    ap.enqueue("../audio/ykn.mp3")
    ap.enqueue("../audio/ykn.mp3")
    ap.enqueue("../audio/ykn.mp3")
    ap.enqueue("../audio/ykn.mp3")
    ap.enqueue("../audio/ykn.mp3")
    ap.enqueue("../audio/ykn.mp3")



    # time.sleep(5)

    # ap.interrupt("../audio/ykn.mp3")
    # # time.sleep(1)
    # ap.interrupt("../audio/SB.mp3")

    time.sleep(0.0001)
    ap.next_audio()
    time.sleep(0.0001)
    ap.next_audio()
    time.sleep(0.0001)
    ap.next_audio()



    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")