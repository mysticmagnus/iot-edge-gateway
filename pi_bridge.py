import serial
import time
import requests
import sys

# --- CONFIGURATION ---

# --- Arduino Config ---
# This is the Pi's name for the USB port.
# Run 'ls /dev/tty*' to find it. It's often /dev/ttyACM0 or /dev/ttyUSB0
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
TIMEOUT = 1
INSTRUMENT_ID = 'ArduinoSensorKit,v1.0,SN:SK12345'

# --- API Config ---
# We use 'localhost' (or 127.0.0.1) because this script
# is on the *same machine* as the API it's talking to.
API_ENDPOINT = 'http://127.0.0.1:5000/api/readings'
DELAY_BETWEEN_READINGS = 2  # seconds


# ---------------------

# We reuse the same Instrument class from Project 5
class Instrument:
    """A class to represent our Arduino-based instrument."""

    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        """Opens the serial connection."""
        try:
            self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"Bridge: Connecting to instrument at {self.port}...")
            time.sleep(2)
            print("Bridge: Connection established.")
            return True
        except serial.SerialException as e:
            print(f"Bridge Error: Could not connect to {self.port}. {e}")
            return False

    def disconnect(self):
        """Closes the serial connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Bridge: Disconnected from instrument.")

    def query(self, command):
        """Sends a command and returns the response."""
        if not self.connection or not self.connection.is_open:
            print("Bridge Error: Not connected.")
            return None
        try:
            self.connection.write(command.encode('utf-8') + b'\n')
            response_bytes = self.connection.readline()
            response_str = response_bytes.decode('utf-8').strip()
            return response_str
        except serial.SerialException as e:
            print(f"Bridge Error during query '{command}': {e}")
            return None


def run_bridge(device):
    """
    The main loop of the bridge.
    Queries the sensor and POSTs to the API.
    """
    print(f"Bridge: Starting data loop. Posting to {API_ENDPOINT} every {DELAY_BETWEEN_READINGS}s.")
    while True:
        try:
            # 1. Query the Arduino
            pot_value_str = device.query("MEAS:POT?")

            if pot_value_str:
                try:
                    # 2. Convert value to an integer
                    pot_value_int = int(pot_value_str)
                    print(f"Bridge: Read value {pot_value_int}")

                    # 3. Prepare data for the API
                    payload = {"value": pot_value_int}

                    # 4. POST to the local API
                    try:
                        requests.post(API_ENDPOINT, json=payload, timeout=0.5)
                        print(f"Bridge: Posted {payload} to API.")
                    except requests.exceptions.RequestException as e:
                        print(f"Bridge Error: Could not post to API. Is it running? {e}")

                except ValueError:
                    print(f"Bridge Error: Got non-integer value from sensor: {pot_value_str}")
            else:
                print("Bridge Error: No data from sensor.")

            # 5. Wait
            time.sleep(DELAY_BETWEEN_READINGS)

        except KeyboardInterrupt:
            print("\nBridge: Shutting down.")
            sys.exit()


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    my_instrument = Instrument(SERIAL_PORT, BAUD_RATE, TIMEOUT)

    try:
        if my_instrument.connect():
            # 1. Verify we have the RIGHT instrument
            idn_response = my_instrument.query("*IDN?")
            print(f"Bridge: Instrument ID: {idn_response}")

            if idn_response == INSTRUMENT_ID:
                # 2. Start the main bridge loop
                run_bridge(my_instrument)
            else:
                print("Bridge Error: Connected to wrong instrument!")
        else:
            print("Bridge Error: Could not connect. Exiting.")

    except Exception as e:
        print(f"An unhandled error occurred: {e}")
    finally:
        my_instrument.disconnect()