import time
import atexit
import numpy as np
import scipy.io as sio
from scipy import signal
from sklearn.cross_decomposition import CCA
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class EEGController:

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
            self.params.serial_number = 'UN-2022.04.22'
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
        
        # Filter properties
        self.cutoff_high = 2
        self.cutoff_low = 30
        
        # SSVEP Properties
        self.epoch_timelength = 4 # Seconds
        self.epoch_samples =  self.epoch_timelength * self.sampling_rate
        self.labels = [7, 7.5, 10, 10.5, 12, 12.5, 15, 15.5]
        self.labels_phaseshift = [0, 1, 0, 1, 0, 1, 0, 1]
        
        self.reference_signals = []
        for i in range(len(self.labels)):
            self.reference_signals.append(self.CCAReferenceSignal(self.labels[i], self.labels_phaseshift[i], 2))
        
        

    # Return timestamp data
    def setMarker(self, start=False):
        if start == True:
            self.board.insert_marker(420)
        else:
            self.board.insert_marker(469)
            
    
    def evaluate(self):
        data = self.board.get_current_board_data(self.epoch_samples)
        
        epoch_data = []
        for i in range(4, 8):
            temp_epoch = np.array(data[i]).flatten() # 6 is the electrode for Oz
            
            temp_epoch = self.butter_highpass_filter(
                data=temp_epoch,
                cutoff=self.cutoff_high,
                order=4)

            temp_epoch = self.butter_lowpass_filter(
                data=temp_epoch,
                cutoff=self.cutoff_low,
                order=4)
            
            epoch_data.append(temp_epoch)
        
        features = []
        for i in range(len(self.reference_signals)):
            calculated_coeff = self.coeff(np.array(epoch_data), self.reference_signals[i])
            features.append(calculated_coeff)
            print(f'Correlation of {self.labels[i]} Hz is {calculated_coeff}')

        print(f"Predicted {self.labels[np.argmax(features)]}")
        
        return self.labels[np.argmax(features)]
    

    def close(self):
        if self.active == True:
            # Get EEG data from board and stops EEG session
            data = self.board.get_board_data()
            self.board.stop_stream()
            self.board.release_session()
            
            np.savetxt("eeg_data.csv", np.transpose(data), delimiter=",")
            print("Saved File")
            self.active = False



    def butter_highpass_filter(self, data, cutoff, order=5):
        """Butterworth high-pass filter.
        Args:
            data (array_like): data to be filtered.
            cutoff (float): cutoff frequency.
            order (int): order of the filter.
        Returns:
            array: filtered data."""
            
        nyq = self.sampling_rate / 2
        normal_cutoff = cutoff / nyq  # normalized cutoff frequency
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data



    def butter_lowpass_filter(self, data, cutoff, order=5):
        """Butterworth low-pass filter.
        Args:
            data (array_like): data to be filtered.
            cutoff (float): cutoff frequency.
            order (int): order of the filter.
        Returns:
            array: filtered data."""
            
        nyq = self.sampling_rate / 2
        normal_cutoff = cutoff / nyq  # normalized cutoff frequency
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        filtered_data = signal.lfilter(b, a, data)
        return filtered_data
    
    
    def CCAReferenceSignal(self, freq, phase_shift, harmonics):
        # Get the time vector
        t = np.arange(self.epoch_samples) / self.sampling_rate

        # temp array to hold reference signals
        reference_signals = []

        for h in range(1, harmonics + 1):
            reference_signals.append(np.sin(2 * np.pi * h * freq * t + phase_shift*np.pi))
            reference_signals.append(np.cos(2 * np.pi * h * freq * t + phase_shift*np.pi))
            
        return np.array(reference_signals)
    
    
    def coeff(self, x, y):
        x_t = np.transpose(x.reshape(4, -1))
        y_t = np.transpose(y)

        cca = CCA(n_components=1)
        cca.fit_transform(x_t, y_t)
        X_c, Y_c = cca.transform(x_t, y_t)

        return np.corrcoef(X_c.T, Y_c.T)[0, 1]
    
    