import time
import atexit
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class EEGDataCollector:

    # Initializer
    def __init__(self, debug=False):

        # Setting up the board
        if debug:
            # Create a synthetic board for debugging purposes
            self.board_id = BoardIds.SYNTHETIC_BOARD
            self.params = BrainFlowInputParams()
        else:
            # Setting up the board
            self.params = BrainFlowInputParams()
            self.params.serial_number = 'UN-2023.02.30'
            self.board_id = BoardIds.UNICORN_BOARD
            
        self.board = BoardShim(self.board_id, self.params)

        # Getting specific board details
        self.channels = self.board.get_eeg_channels(self.board_id) #EEG Channels
        self.timestamp_channel = self.board.get_timestamp_channel(self.board_id) # Timestamp channel
        self.marker_channel = self.board.get_marker_channel(self.board_id) # Marker channel for synchronization
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id) # Hz
        
        

        # Start recording/collecting data
        self.board.prepare_session()
        self.board.start_stream ()
        print(f"Starting EEG Stream, debug={debug}")
        atexit.register(self.close)
        
        # Create an active variable to ensure proper closing
        self.active = True
        

    # Return timestamp data
    def setMarker(self, message):
        print("Marker set")
        self.board.insert_marker(int(message)) # Stop sequence
    
    def close(self):
        if self.active == True:
            # Get EEG data from board and stops EEG session
            data = self.board.get_board_data()
            self.board.stop_stream()
            self.board.release_session()
            
            t = time.localtime()
            current_time = time.strftime("%H%M%S", t)
            np.savetxt(f"eeg_data{current_time}.csv", np.transpose(data), delimiter=",")
            print("Saved File")
            self.active = False
    
    