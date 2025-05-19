# JVL MAC400 Motor Test Script

This *very preliminary draft* script providing a standalone, ROS-free interface to control a JVL MAC400 motor over Modbus using mac400.py. It is designed for quick testing and development, with basic safety handling.

Disclaimer: this code was generated code with the assistance of an AI model and still needs to be tested. This is just a starting point for ongoing testing of our MAC400 motors.

## Features
The test script runs in a loop consisting of the following steps:
- Initializes the motor.
- Gets the current position.
- Moves N counts forward in velocity mode.
- Idles in passive mode for a set duration.
- Returns to the starting position in position mode.
- Returns motor to `PASSIVE` mode on exit or error.
- Works over Modbus TCP.
- Read register 35 (err_stat) regularly, decode the 32-bit binary output, and log tripped error bits to a timestamped log file.

## Prerequisites

- Python 3.7+
- `pymodbus` (Install via `pip install pymodbus`)
- A running instance of a MAC400 motor accessible over Modbus TCP

## Usage

1. Ensure the motor is powered and connected to Sierra Wireless unit
2. Edit the `motor_test.py` script:
   - Set the correct IP address and port in the `ModbusTcpClient` constructor
   - Optionally, change the `slave_id`, `test_speed`, and `test_duration`
3. Run the script:
   
   ```bash
   python3 motor_test.py --counts 5000 --idle-time 30
