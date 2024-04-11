import time
import sys

def spinner(spinnertime=5):
    """
    Displays a simple text-based spinner in the console for a specified duration.
    
    Parameters:
    spinnertime (int): The duration for which the spinner should be displayed, in seconds. Default is 5 seconds.
    
    Example:
    spinner(10) # Displays the spinner for 10 seconds
    """
    spinner_frames = ['|', '/', '-', '\\']
    end_time = time.time() + spinnertime
    while time.time() < end_time:
        for frame in spinner_frames:
            sys.stdout.write('\r' + frame)
            sys.stdout.flush()
            time.sleep(0.1)

# help(spinner)
spinner()
