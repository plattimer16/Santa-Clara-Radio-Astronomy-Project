# This is the code that we're writing in order to make our gta_function be its own function instead of a script
import pyfirmata2
import time
import serial
from scipy.io import savemat
import numpy as np

# Timeout value to determine when you want the function that reads data to wait until it gets what it needs
global timeout_time
global timeout_counter
global timeout_flag
timeout_time = 1000
timeout_counter = 0
timeout_flag = False
# Normalization factor
# Experimental value that will give you the true angle is 205-206, so use these values when using the system
# If you want to return the system back to its resting position, set to 203 then set target angle to 0
normalization_factor = 203
# Inform user that the system is beginning to load
print('\n\n\nLoading Rotation System...')
# Create a variable in order to define which ports to use
arduino_port = 'COM3'
sensor_port = 'COM6'
# Create the arduino object board
board = pyfirmata2.Arduino(arduino_port)
# Pin connected to motor driver set up as pwm outputs
RMB = board.get_pin('d:10:p')  # reverse motor bias
FMB = board.get_pin('d:11:p')  # forward

# LED Pins for System Diagnostics
PIN_GREEN = board.get_pin('d:5:o')
PIN_RED = board.get_pin('d:4:o')
PIN_YELLOW = board.get_pin('d:2:o')
PIN_BLUE = board.get_pin('d:3:o')
# Pin connected to the sound component
SOUND_PIN = board.get_pin('d:9:o')
# Time variables
short_time = 1
very_short_time = 2


# BEGINING OF FUNCTION DEFINITION
def light_pattern():
    # Pretty light pattern
    PIN_BLUE.write(1)
    time.sleep(0.1)
    PIN_BLUE.write(0)
    PIN_RED.write(1)
    time.sleep(0.1)
    PIN_RED.write(0)
    PIN_GREEN.write(1)
    PIN_YELLOW.write(1)
    time.sleep(0.3)
    PIN_GREEN.write(0)
    PIN_YELLOW.write(0)
    PIN_RED.write(1)
    time.sleep(0.1)
    PIN_RED.write(0)
    PIN_BLUE.write(1)
    time.sleep(0.1)
    PIN_BLUE.write(0)
# END OF FUNCTION DEFINITION


light_pattern()


# BEGINING OF FUNCTION DEFINITION
def FWB_motor(board):
    # Deactivate Stop motor
    PIN_RED.write(0)
    # Deactivate the Reverse movement
    PIN_YELLOW.write(0)
    RMB.write(0)
    FMB.write(1)
    # Activate the Green LED to indicate the motor is pushing forward (up)
    PIN_GREEN.write(1)
# END OF FUNCTION DEFINITION


# BEGINING OF FUNCTION DEFINITION
def RVB_motor(board):
    # Deactivate Forward movement
    PIN_GREEN.write(0)
    # Deactivate stop movement
    PIN_RED.write(0)
    FMB.write(0)
    # Activate the Yellow LED to indicate the motor is reversing
    PIN_YELLOW.write(1)
    RMB.write(1)
# END OF FUNCTION DEFINITION


# BEGINING OF FUNCTION DEFINITION
def STOP_motor(board):
    # Deactivate Forward movement
    PIN_GREEN.write(0)
    FMB.write(0)
    # Deactivate the Reverse movement
    PIN_YELLOW.write(0)
    RMB.write(0)
    # Activate the red LED to indicate the motor has been stopped
    PIN_RED.write(1)
# END OF FUNCTION DEFINITION


# BEGINING OF FUNCTION DEFINITION
def sound_success(board):
    # Turn the speaker on
    SOUND_PIN.write(1)
    # Wait 0.25 seconds
    time.sleep(0.25)
    # Turn the speaker off
    SOUND_PIN.write(0)
    # Wait 0.25 seconds
    time.sleep(0.25)
    # Turn the speaker on
    SOUND_PIN.write(1)
    # Wait 0.25 seconds
    time.sleep(0.25)
    # Turn the speaker off
    SOUND_PIN.write(0)
# END OF FUNCTION DEFINITION


# BEGINING OF FUNCTION DEFINITION
def serial_getRoll():
    global timeout_counter, timeout_flag
    # Open the serial port
    ser = serial.Serial(sensor_port, 9600, timeout=5)
    # Listen for the data from the sensor
    heard_data = ser.read_until(b'UT')
    # Define a variable that will hold the angle of roll
    angle_roll = -1
    # Loop that will continue to occur until the function got the data that it needs
    # Define a flag to determine when we get the data we needed
    loop_flag = False
    while loop_flag == False:
        # If statement to decide how to handle the data it managed to read
        if len(heard_data) >= 13:
            # There was enough data, process the angle
            # There was enough data to calculate angle of roll, process it
            data = heard_data[-13:-2]
            # Obtain and calculate Roll
            RollL = data[2]
            RollH = data[3]
            angle_roll = ((RollH << 8) | (RollL)) / 32768.0 * 180.0
            # Close the serial object
            ser.close()
            # Change the status of the loop flag just in case
            loop_flag = True
            # Normalize the angle to compensate for the radio telescope inclination
            angle_roll = angle_roll - normalization_factor
            # Return the angle of roll
            return angle_roll
        else:
            # Iterate the timeout counter
            timeout_counter = timeout_counter + 1
            # Check if the getRoll function has timed out
            if timeout_counter > timeout_time:
                # At this point, there was a timeout, set the timeout flag to true
                timeout_flag = True
                print('Failed to communicate')
                # Possibly redundant
                loop_flag = True
                # Return a negative one so user can process the timeout error as a number (Easier to process)
                return -1
            else:
                loop_flag = False
                # This means that there wasn't enough data, ensure that the flag is false to keep loop going
# END OF FUNCTION DEFINITION


# BEGINING OF FUNCTION DEFINITION
# This function will keep running until it's over
def stability_test(TOLERABLE_DELTA, test_size):
    # Stop the motor
    STOP_motor(board)
    # Wait short time and do nothing
    time.sleep(short_time)
    # Loop until the last test_size roll angles read are close in their values to prevent using crazy data
    # Flag to determine if the sensor values are stable
    tolerable = False
    # Do a while loop until the angle values are stable
    while tolerable == False:
        # Create an array that will hold the values that we're testing stability with and load it with 0s
        angle_test = [0] * test_size
        print(angle_test)
        # Define the iterating value for the next while loop
        iter_1 = 0
        # Begin the next while loop to load angle_test
        while iter_1 != test_size:
            # Activate the blue LED to indicate that we are obtaining angular data
            PIN_BLUE.write(1)
            # Obtain the angle of roll
            angle_temp = serial_getRoll()
            # Deactivate the blue LED to indicate no longer obtaining angular data
            PIN_BLUE.write(0)
            # Get the iter_1 position for our angle_test array (so we're loading the array with test_size roll angles)
            angle_test[iter_1] = angle_temp
            # Diagnostic print
            print(angle_test)
            # Increase the iterator
            iter_1 = iter_1 + 1
        # Inner most while loop has ended, now we test for variation (stability of angle)
        # Define the iter_2 variable
        iter_2 = 1
        # Begin second while loop to determine stability of angle data
        while iter_2 != test_size:
            # Do an if statement to determine if the data is stable
            if abs(angle_test[0] - angle_test[iter_2]) <= TOLERABLE_DELTA:
                # Set the tolerable flag to true until told otherwise
                tolerable = True
                print('It looks good man')
                print(abs(angle_test[0] - angle_test[iter_2]))
                # The variation between them is good so iterate normally
                iter_2 = iter_2 + 1
            else:
                # If this occurred, the variation was too large and hence unstable therefore it failed the check
                # Set tolerable flag to false
                tolerable = False
                # Kill the loop by setting the iter_2 to max value
                iter_2 = test_size
        print('We killed the program')
    print('The signal is stable!')
# END OF FUNCTION DEFINITION


# BEGINING OF FUNCTION DEFINITION
def mode_gta(desa):
    # Set initial time to 0
    time_elapsed = 0
    true_angle = serial_getRoll()
    print(true_angle)
    # Obtain the current angle
    current_angle = round(true_angle)
    # Check if there was a timeout error
    if current_angle == -1:
        # print('TIMEOUT ERROR')
        return
    else:
        # Proceed with rest of the code
        random = 0
        # Print the angle and time in real time
        print('Current Angle: ')
        print(current_angle)
        print('Time Elapsed')
        print(time_elapsed)
        # Create the dynamic array for angle
        angle_array_np = np.array([true_angle])
        # Create the dynamic array for elapsed time
        time_array_np = np.array([time_elapsed])
        # Load the angle on the dynamic array using np
        # Load the elapsed time on the dynamic array using np
        # Beginning counting time
        start_time = time.time()
        # Set a timer flag to determine when to start counting time in the loop
        timerFlag = False
        # Flags to indicate if the direction was flipped
        forward_flag = True
        reverse_flag = False
        print('Desa while loop initiated')
        # Begin the loop that will move the actuator
        while current_angle != desa:
            # Determine when to start counting time in the loop
            if timerFlag == False:
                # Don't do anything, just set timerFlag to true
                timerFlag = True
            else:
                # This means that we have already gone through the loop, starting counting time now
                # Obtain the current angle
                true_angle = serial_getRoll()
                current_angle = round(true_angle)
                # Get the time
                time_elapsed = time_elapsed + (time.time() - start_time)
                # Start counting the time again
                start_time = time.time()
                # Display the vital information
                print('Current Angle: ')
                print(current_angle)
                print('Time Elapsed')
                print(time_elapsed)
                # Append the angle to the angle array
                angle_array_np = np.append(angle_array_np, true_angle)
                # Append the elapsed time to the time array
                time_array_np = np.append(time_array_np, time_elapsed)
            # If statement to determine what should be done
            if current_angle < desa:
                # Angle is too small, push the dish forward
                FWB_motor(board)
                # Delay a short amount of time
                # time.sleep(short_time)
                # Stop the motor when done to prevent over correction
                # STOP_motor(board)
            elif current_angle > desa:
                # The angle is too large, we need to correct our position. Do a very small reverse
                RVB_motor(board)
                # Delay a very short amount of time
                # time.sleep(very_short_time)
                # Stop the motor when done to prevent over correction
                # STOP_motor(board)
            else:
                # This means that the current angle is the desired angle (desa) so indicate success with sound and end
                # Stop the motor
                STOP_motor(board)
                # sound_success(board)
                # Show the content of the angle and time
                print(angle_array_np)
                print(time_array_np)
                # Save both arrays to a .m file for plotting on MATLAB
                data = {
                    'angle_array': angle_array_np,
                    'time_array': time_array_np
                }
                savemat('arrays.mat', data)
                # Wait short time before shutting off red light indicator
                time.sleep(2)
                # Turn the red LED off
                PIN_RED.write(0)
# END OF FUNCTION DEFINITION


# Main code goes here
print('\n\n\n\nRotation system has fully loaded!\n')
angle_of_choice = input('System Message: What angle would you like to move the telescope to?\n')
print('\nSystem Message: Attempting to execute system rotation.')
time.sleep(1.5)
mode_gta(int(angle_of_choice))
if timeout_flag == True:
    print('\n\n\nSystem Message: The telescope timed out when trying to read angular data from it! \n\n\n')
else:
    print('\n\n\nSystem Message: The telescope is now at ', angle_of_choice, ' degrees!')
    light_pattern()
