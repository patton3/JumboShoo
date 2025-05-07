#!/usr/bin/env python3
"""
lora_cam_bridge.py
Listens on LoRa for trigger string (default '0.2').
When triggered, captures N frames with picam2 and runs YOLO.
If an elephant is detected it
    saves annotated JPGs
    appends a txt log line:  <run‑uuid>,<count>,<best‑conf>,<img‑file>
    radios hit string back over LoRa (default '2.0')
Returns to listening state.

Dependencies
------------
sudo pip3 install ultralytics picamera2 opencv-python
sudo pip3 install adafruit-circuitpython-rfm9x adafruit-blinka
"""

# ───────────────────────── imports ─────────────────────────
import os, sys, argparse, uuid, time

# RPi / LoRa
import busio
from digitalio import DigitalInOut
import board
import adafruit_rfm9x

# CV / AI
import cv2
from picamera2 import Picamera2
from ultralytics import YOLO

# ─────────────── defaults (modify with CLI) ───────────────
DEF_SAVE_DIR     = "/home/a/JumboShoo/logging/ElephantHits"
DEF_MODEL_PATH   = "/home/a/JumboShoo/scripts/models/Elephants2m.pt"        # Elephants2n/s/m/l/x
DEF_CONF         = 0.50                    # Confidence threshold for elephant detection
DEF_WIDTH        = 1280                    # Image Width
DEF_HEIGHT       = 720                     # Image Height
DEF_CYCLES       = 3                       # N number of cycles each trigger
DEF_TRIGGER      = "0.2"                   # listen word
DEF_HIT_REPLY    = "2.0"                   # reply word
DEF_LORA_FREQ    = 433                     # MHz
# ───────────────────────────────────────────────────────────


# ───────────────── helper functions ─────────────────
def ensure_dir(path: str):    # Ensures that the logging directories exist
    """Create folder if needed."""
    os.makedirs(path, exist_ok=True)


def log_hit(csv_path, run_id, count, best_conf, filename):
    with open(csv_path, "a") as f:   # When detection is positive, log in a .txt file
        f.write(f"{run_id},{count},{best_conf:.3f},{filename}\n")


# ───────────── YOLO elephant detector ──────────────
def run_detector(model, save_dir, cycles, conf_thres, cam): 
    print("Starting detector …")
    ensure_dir(save_dir)
    csv_log = os.path.join(save_dir, "detections_log.txt")
    run_id  = str(uuid.uuid4())[:8]           # unique per trigger

    hit, total_cnt, best_conf = False, 0, 0.0
    elephant_id = [k for k, v in model.names.items() if v == "elephant"][0]  # Define class as 'Elephant' for YOLO

    for idx in range(cycles):
        frame = cam.capture_array()
        print("Captured image")
        res = model(frame, classes=[elephant_id],
                    conf=conf_thres, verbose=False)[0]  # Run captured frame through YOLO

        if res.boxes and len(res.boxes) > 0: # If there is a drawn box, then elephant = yes
            hit = True
            cnt = len(res.boxes)
            total_cnt += cnt
            best_conf = max(best_conf, float(res.boxes.conf.max()))

            annotated = res.plot() # boxes drawn, BGR
            fname = f"ele_{run_id}_{idx:03}.jpg"
            cv2.imwrite(os.path.join(save_dir, fname), annotated) # Name and write image out
            log_hit(csv_log, run_id, cnt, best_conf, fname)
            print(f"[{run_id}] DETECTED {cnt} elephant(s) → saved {fname}")
        else:
            print(f"[{run_id}] no elephants")

    return hit, total_cnt, best_conf  # Return hit bool, # of eliphantes and best % confidence


# ────────────────── LoRa setup ─────────────────────
def init_lora(freq_mhz):
    i2c   = busio.I2C(board.SCL, board.SDA)
    cs    = DigitalInOut(board.CE1)
    reset = DigitalInOut(board.D25)
    spi   = busio.SPI(board.SCK, board.MOSI, board.MISO)
    radio = adafruit_rfm9x.RFM9x(spi, cs, reset, freq_mhz)
    radio.tx_power = 23  # adjust as needed
    return radio


# ───────────── argument parsing ─────────────
def parse_cli():                                # Adjustable command line variables
    p = argparse.ArgumentParser(description="LoRa‑triggered elephant camera")
    p.add_argument("--save_dir",   default=DEF_SAVE_DIR)
    p.add_argument("--model_path", default=DEF_MODEL_PATH)
    p.add_argument("--conf",       type=float, default=DEF_CONF)
    p.add_argument("--width",      type=int,   default=DEF_WIDTH)
    p.add_argument("--height",     type=int,   default=DEF_HEIGHT)
    p.add_argument("--cycles",     type=int,   default=DEF_CYCLES)
    p.add_argument("--trigger",    default=DEF_TRIGGER)
    p.add_argument("--hit_reply",  default=DEF_HIT_REPLY)
    p.add_argument("--freq",       type=float, default=DEF_LORA_FREQ)
    return p.parse_args()


# ───────────────────────── main loop ────────────────────────
def main():
    args  = parse_cli()            # Gather command line variables, or use defaults
    radio = init_lora(args.freq)   # Initialize LoRa module
    model = YOLO(args.model_path)  # Define YOLO model from path

    print(f"LoRa‑camera bridge ready "
          f"(trigger='{args.trigger}', reply='{args.hit_reply}')")

    cam = Picamera2()
    cam.configure(cam.create_still_configuration(
        main={"size": (args.width, args.height), "format": "RGB888"}))
    cam.set_controls({"AnalogueGain": 8, "AeEnable": True}) # Other camera controls are avaliable
    cam.start()
    time.sleep(0.2)

    while True:
        pkt = radio.receive()           
        if pkt is None:
            continue       # no packet, keep listening

        try:
            msg = pkt.decode("utf-8").strip() # Packet! try to decode
        except UnicodeDecodeError:
            print("Alert - non‑UTF8 packet ignored")
            continue

        print(f"LoRa RX: '{msg}'")
        if msg != args.trigger:
            continue                     # not the trigger

        # —— trigger hit: run detector ——
        hit, count, best = run_detector(
            model, args.save_dir, args.cycles, args.conf, cam)

        if hit:
            reply = args.hit_reply
            radio.send(reply.encode("utf-8"))        # Yes elephants, radio hit string
            print(f"LoRa TX: '{reply}'  (count={count}, best={best:.2f})")
        else:
            print("No elephants detected → no reply")

        print("Waiting for next trigger …")


# ───────────────── entry point ─────────────────
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser aborted.")
        sys.exit(0)
