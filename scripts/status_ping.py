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