import time
import atexit
import numpy as np
import scipy.io as sio
from scipy import signal
from sklearn.cross_decomposition import CCA
import defaultdict
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
        
        # # Populate the board, will crash if not
        # time.sleep(0.2)
        # start = self.board.get_current_board_data(200)

        # # Get timestamp data
        # self.initial_time = start[self.timestamp_channel,0] #Get the initial timestamp data
        
        # Create an active variable to ensure proper closing
        self.active = True
        
        # Filter properties
        self.cutoff_high = 6
        self.cutoff_low = 50
        
        # SSVEP Properties
        self.epoch_timelength = 4 # Seconds
        self.epoch_samples =  self.epoch_timelength * self.sampling_rate
        self.labels = [9, 12, 8]
        self.labels_phaseshift = [0, 0.7, 1.5]
        self.train = True
        self.reference_signals = []
        self.templates = []
        for i in range(len(self.labels)):
            self.reference_signals.append(self.CCAReferenceSignal(self.labels[i], self.labels_phaseshift[i], 2))
        
        
    def epoch_data_process(self, processed_eeg, sampling_rate, epoch_duration, stimulus_info=None):
        """Segments the EEG data into epochs.
        stimulus_info (dict, optional): Dictionary where keys are timestamps and values are stimulus labels.
                                        If provided, epochs will be created around these events.
        """
        if stimulus_info:
            epochs = defaultdict(list)
            for timestamp, stimulus in stimulus_info.items():
                start_sample = int(timestamp * sampling_rate)
                end_sample = start_sample + int(epoch_duration * sampling_rate)
                if 0 <= start_sample < processed_eeg.shape[1] and end_sample <= processed_eeg.shape[1]:
                    epochs[stimulus].append(processed_eeg[:, start_sample:end_sample])
            return epochs
        else:
            num_samples_per_epoch = int(sampling_rate * epoch_duration)
            num_epochs = processed_eeg.shape[1] // num_samples_per_epoch
            epochs = processed_eeg[:, :num_epochs * num_samples_per_epoch].reshape(processed_eeg.shape[0], num_epochs, num_samples_per_epoch)
            return epochs
    def it_cca_train(self, epochs):
        """Trains individual templates for each stimulus using averaged epochs."""
        templates = {}
        for stimulus, epoch_list in epochs.items():
            if epoch_list:
                templates[stimulus] = np.mean(np.array(epoch_list), axis=0)
            else:
                print(f"Warning: No epochs found for stimulus {stimulus} during training.")
        return templates   
    # Return timestamp data
    def setMarker(self, start=False):
        if start == True:
            self.board.insert_marker(420)
        else:
            self.board.insert_marker(469)
    
    
    
    def evaluate(self,train=True):
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
        
        if train:
            train_epochs = self.epoch_data_process(data, self.sampling_rate, EPOCH_DURATION=1.0)

            # 3. Implement IT-CCA for decision making (Training phase)
            templates = self.it_cca_train(train_epochs, self.sampling_rate)
            self.templates = templates
        else:
            predicted_stimulus, correlation = self.it_cca_predict(np.array(epoch_data).reshape(data.shape[0], -1), self.templates)
            return self.labels[correlation]

        # features = []
        # for i in range(len(self.reference_signals)):
        #     calculated_coeff = self.coeff(np.array(epoch_data), self.reference_signals[i])
        #     features.append(calculated_coeff)
        #     print(f'Correlation of {self.labels[i]} Hz is {calculated_coeff}')

        # print(f"Predicted {self.labels[np.argmax(features)]}")
        
        # return self.labels[np.argmax(features)]
    

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
    
    def it_cca_predict(self, eeg_epoch, templates):
        """Predicts the target stimulus using Individual Template based CCA."""
        correlations = {}
        cca = CCA(n_components=1)
        for stimulus, template in templates.items():
            if eeg_epoch.shape[1] == template.shape[1]:
                cca.fit(eeg_epoch.T, template.T)
                U_test, V_template = cca.transform(eeg_epoch.T, template.T)
                correlation = np.corrcoef(U_test.T, V_template.T)[0, 1]
                # return correlation
                correlations[stimulus] = correlation
            else:
                print(f"Warning: Epoch length mismatch for stimulus {stimulus}.")
                correlations[stimulus] = -1  # Indicate mismatch

        if correlations:
            best_stimulus = max(correlations, key=correlations.get)
            return best_stimulus, correlations[best_stimulus]
        else:
            return "Unknown", -1

    def coeff(self, x, y):
        x_t = np.transpose(x.reshape(4, -1))
        y_t = np.transpose(y)

        cca = CCA(n_components=1)
        cca.fit_transform(x_t, y_t)
        X_c, Y_c = cca.transform(x_t, y_t)

        return np.corrcoef(X_c.T, Y_c.T)[0, 1]
    
    