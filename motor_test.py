import time
import logging
import argparse
from datetime import datetime
import mac400

# Configuration Constants
IP_ADDRESS = "192.168.13.3"  # IP address of the motor
NODE_ID = 1                  # JVL MAC400 Modbus node ID
VELOCITY = 1000             # Velocity in counts/sec
POLL_DELAY = 0.1            # Delay for polling motor status
TOLERANCE = 5               # Position tolerance for asserting arrival

# Set up logging
LOG_FILENAME = f"motor_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

def decode_err_stat(err_val):
    binary_string = bin(err_val)[2:].rjust(32, '0')
    tripped_bits = [i for i in range(32) if err_val & (1 << i)]
    logging.warning(f"ERROR STATUS REGISTER (35): {err_val} ({binary_string})")
    logging.warning(f"Tripped bits: {tripped_bits}")

def check_errors(motor):
    err_stat = motor.read_register(35)
    if err_stat != 0:
        decode_err_stat(err_stat)

def wait_until_motor_stops(motor):
    while True:
        status_word = motor.read_register(0x6041)
        motor_running = bool(status_word & (1 << 10))  # Target reached flag
        if motor_running:
            break
        time.sleep(POLL_DELAY)
    while True:
        status_word = motor.read_register(0x6041)
        motor_stopped = not (status_word & (1 << 10))
        if motor_stopped:
            break
        time.sleep(POLL_DELAY)

def set_mode(motor, mode):
    motor.write_register(0x6060, mode)
    actual_mode = motor.read_register(0x6061)
    assert actual_mode == mode, f"Mode mismatch: expected {mode}, got {actual_mode}"

def move_to_position(motor, target_position):
    set_mode(motor, 1)  # Position mode
    motor.write_register(0x607A, target_position)
    motor.write_register(0x6040, 0x003F)  # Enable + Start
    wait_until_motor_stops(motor)
    check_errors(motor)

def set_velocity(motor, velocity):
    set_mode(motor, 3)  # Velocity mode
    motor.write_register(0x60FF, velocity)
    motor.write_register(0x6040, 0x003F)
    check_errors(motor)

def set_passive_mode(motor):
    set_mode(motor, 0)  # Passive
    check_errors(motor)

def get_position(motor):
    return motor.read_register(0x6064, signed=True)

def test_motor_loop(counts_to_move, idle_time):
    motor = mac400(IP_ADDRESS, NODE_ID)
    print("Initializing motor test...")
    logging.info("Motor test started.")

    start_pos = get_position(motor)
    print(f"Starting position: {start_pos}")
    logging.info(f"Starting position: {start_pos}")

    while True:
        try:
            # Step 1: Move forward in velocity mode
            print(f"Moving forward {counts_to_move} counts...")
            logging.info(f"Moving forward {counts_to_move} counts...")
            set_velocity(motor, VELOCITY)
            time.sleep(abs(counts_to_move / VELOCITY))
            set_passive_mode(motor)

            # Step 2: Idle
            print("Idling...")
            logging.info("Idling...")
            time.sleep(idle_time)

            # Step 3: Return to start
            print("Returning to start position...")
            logging.info("Returning to start position...")
            move_to_position(motor, start_pos)

            # Step 4: Idle again
            print("Idling at start position...")
            logging.info("Idling at start position...")
            set_passive_mode(motor)
            time.sleep(idle_time)

        except Exception as e:
            logging.exception(f"Exception during motor test loop: {e}")
            print(f"Exception occurred: {e}")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test MAC400 motor movement over Ethernet.")
    parser.add_argument("--counts", type=int, required=True,
                        help="Number of counts to move in each cycle")
    parser.add_argument("--idle-time", type=int, default=60,
                        help="Idle time in seconds between movements")
    args = parser.parse_args()

    test_motor_loop(args.counts, args.idle_time)
