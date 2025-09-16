import busio, board, time
from digitalio import DigitalInOut
import adafruit_rfm9x

def send_ping():
    i2c = busio.I2C(board.SCL, board.SDA)
    cs = DigitalInOut(board.CE1)
    rst = DigitalInOut(board.D25)
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    rfm9x = adafruit_rfm9x.RFM9x(spi, cs, rst, 433)
    rfm9x.tx_power = 23
    
    rfm9x.send("CamPi Status 1".encode("utf-8"))
    
if __name__ == "__main__":
    send_ping()
    #Not Active without the boot service that's commented out in the installer. The purpose of those is to have the script
    #running in the background, Spring 2025 I mistakenly tried to have this and the main (camera/brain/whatever)
    #active and initialized at the same time, which led to errors due to the rfm9x radio being in use by one
    #or the other script at any time. Ideally this is integrated into the main script rather than as a seperate program
    #and seperate service.
