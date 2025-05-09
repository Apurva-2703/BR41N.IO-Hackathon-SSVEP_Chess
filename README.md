# ♟️ SSVEP-Based Chess BCI — Br41n.io Hackathon Project

## 🧠 Project Overview

This project was developed during the **Br41n.io Hackathon** as a proof-of-concept brain-computer interface (BCI) that enables users to play chess using **Steady-State Visual Evoked Potentials (SSVEP)**. By fixating on flickering visual stimuli, the user can select a piece and its destination square, all via EEG.

---

## ⚙️ Technical Summary

### 🧩 Unity Integration
- We forked a public Unity chess template from GitHub to serve as base-game for this EEG-integrated Chess BCI. (SebLague/Chess-Coding-Adventure)
- Flickering stimuli (each with a distinct phase shift) were added beside each **row and column** of the chessboard.
- The user’s gaze at a flickering point corresponds to a specific `(x, y)` coordinate, used to select and move pieces.
- Modified Unity C# scripts (primarily `Move.cs`) to allow EEG-based selection input.

## 🧠 Hardware Used
We used the **g.tec Unicorn Hybrid Black** — a wireless 8-channel EEG system — for signal acquisition.  
Key features:
- Dry/Wet electrodes - we used conductive gel to enhance signal and reduce signal impedance.
- 250 Hz sampling rate
- Bluetooth streaming
- Compatible with g.tec SDK and custom pipelines 

## 🧠 EEG Classification Pipeline
- We used **Individual-Template Canonical Correlation Analysis (IT-CCA)** to decode which flicker the user was focusing on.
  - The particular script responsible for this step is `EEGController_new.py`, which contains comments on each of the functions and methods.
  - IT-CCA was used instead of CCA due to greater classification accuracy (Nakanishi et al., 2015)
- IT-CCA compares EEG input against reference sinusoids (matching each flicker's phase-shift).
- The stimulus whose reference signal best correlates with the EEG is selected as the user's intention.

## 📈 Signal Processing & Feature Extraction
- EEG data was **bandpass filtered** around the expected SSVEP frequency range (6–50 Hz).
- Feature extraction was implicit in the **I-TCCA process**, which extracts phase-shift-specific correlation features from multichannel EEG data.
- No deep learning or dimensionality reduction was required — CCA directly handled spatial filtering and classification.

## 🧪 Testing Paradigm
- The user fixated on a flickering cue for ~4 seconds. (One cue amongst the eight total cues per row/column).
- The system performed CCA classification in real-time.
- Upon successful match, the corresponding chess coordinate was selected in the y-axis and the process was repeated for the x-axis.
- One the x,y coordinate was established, a move was executed.
- Chess rules remained unchanged from the original Unity implementation.

---

## 👥 Team Contributions
- Integrated flickering stimuli into Unity environment.
- Tuned flicker frequency placements and visual timing.
- Participated in classification tests and debugging.
- Documented architecture and implementation.

Special thanks to [@aaronjuma], who implemented the CCA pipeline and led the signal classification logic, and  [@Keerti25], who helped design `project_analysis.ipynb` to test the IT-CCA accuracy and the final presentation for this hackathon.

---

## 🏁 Notes
This was built in ~24 hours during the Br41n.io hackathon and serves as a functional prototype for EEG-controlled chess via SSVEP.  

--

## Citations
1. Nakanishi M, Wang Y, Wang YT, Jung TP. A Comparison Study of Canonical Correlation Analysis Based Methods for Detecting Steady-State Visual Evoked Potentials. PLoS One. 2015 Oct 19;10(10):e0140703. doi: 10.1371/journal.pone.0140703. PMID: 26479067; PMCID: PMC4610694.

