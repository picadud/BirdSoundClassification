import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('finalRawData.csv')

# Load the audio file
audio_paths = df['converted_file_path']

def gettingSegments(audio_path):
    y, sr = librosa.load(audio_path, sr=44100)

    # Normalize the audio signal
    y = y / np.max(np.abs(y))

    # Define frame length and hop length
    frame_length = 1024
    hop_length = 512

    # Apply a window function (Hamming window)
    window = np.hamming(frame_length)

    # Calculate STE
    energy = np.array([
        np.sum((y[i:i + frame_length] * window) ** 2)
        for i in range(0, len(y) - frame_length + 1, hop_length)
    ])
    #print(energy)


    # Define T2 and T1 for the double threshold
    T2 = np.mean(energy) * 1.5
    T1 = np.mean(energy) * 0.5
    #print((T1, T2))
    # Find segments above T2
    segments = np.where(energy > T2)[0]
    #print(segments)
    # Find start (A) and end points (B) using T1
    start_end_points = []
    start = None

    # Iterate over all frames of energy, not just the segments
    for i in range(len(energy)):
        # Detect the start of a sound segment when energy crosses above T2
        if start is None and energy[i] > T2:
            start = i

        # Detect the end of a sound segment when energy crosses below T1 after starting
        if start is not None and energy[i] < T1:
            end = i
            start_end_points.append((start, end))
            start = None

    # Handle the case where a segment reaches the end of the signal
    if start is not None:
        start_end_points.append((start, len(energy) - 1))

    #print("Start and end points (in frame indices):", start_end_points)

    # Calculate Zero-Crossing Rate (ZCR)
    zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)[0]

    # Define T3 as the mean ZCR
    T3 = np.mean(zcr)

    # Apply ZCR refinement to find the final segments
    final_segments = []
    for (start, end) in start_end_points:
        # Search outward from start and end points until ZCR is below T3
        while start > 0 and zcr[start] > T3:
            start -= 1
        while end < len(zcr) and zcr[end] > T3:
            end += 1
        final_segments.append((start, end))

    # Convert frame indices to time
    final_segments_time = [(librosa.frames_to_time(s, sr=sr, hop_length=hop_length),
                           librosa.frames_to_time(e, sr=sr, hop_length=hop_length))
                          for (s, e) in final_segments]
    return final_segments_time

df['segments'] = audio_paths.apply(lambda path: gettingSegments(path))
df['segments_count'] = df['segments'].apply(lambda seg: len(seg))
#df.to_csv('segmentedData.csv')


#print("Final detected segments (start, end in seconds):")
#to plot an example segmentation
def gettingSegmentsAndPlot(audio_path):
    y, sr = librosa.load(audio_path, sr=44100)

    # Normalize the audio signal
    y = y / np.max(np.abs(y))

    # Define frame length and hop length
    frame_length = 1024
    hop_length = 512

    # Apply a window function (Hamming window)
    window = np.hamming(frame_length)

    # Calculate STE
    energy = np.array([
        np.sum((y[i:i + frame_length] * window) ** 2)
        for i in range(0, len(y) - frame_length + 1, hop_length)
    ])
    #print(energy)


    # Define T2 and T1 for the double threshold
    T2 = np.mean(energy) * 1.5
    T1 = np.mean(energy) * 0.5
    #print((T1, T2))
    # Find segments above T2
    segments = np.where(energy > T2)[0]
    #print(segments)
    # Find start (A) and end points (B) using T1
    start_end_points = []
    start = None

    # Iterate over all frames of energy, not just the segments
    for i in range(len(energy)):
        # Detect the start of a sound segment when energy crosses above T2
        if start is None and energy[i] > T2:
            start = i

        # Detect the end of a sound segment when energy crosses below T1 after starting
        if start is not None and energy[i] < T1:
            end = i
            start_end_points.append((start, end))
            start = None

    # Handle the case where a segment reaches the end of the signal
    if start is not None:
        start_end_points.append((start, len(energy) - 1))

    #print("Start and end points (in frame indices):", start_end_points)

    # Calculate Zero-Crossing Rate (ZCR)
    zcr = librosa.feature.zero_crossing_rate(y, frame_length=frame_length, hop_length=hop_length)[0]

    # Define T3 as the mean ZCR
    T3 = np.mean(zcr)

    # Apply ZCR refinement to find the final segments
    final_segments = []
    for (start, end) in start_end_points:
        # Search outward from start and end points until ZCR is below T3
        while start > 0 and zcr[start] > T3:
            start -= 1
        while end < len(zcr) and zcr[end] > T3:
            end += 1
        final_segments.append((start, end))

    # Convert frame indices to time
    final_segments_time = [(librosa.frames_to_time(s, sr=sr, hop_length=hop_length),
                           librosa.frames_to_time(e, sr=sr, hop_length=hop_length))
                          for (s, e) in final_segments]


    for segment in final_segments_time:
        print(segment)
    y, sr = librosa.load(df['converted_file_path'].iloc[0], sr=44100)
    # Plotting
    plt.figure(figsize=(14, 8))

    # Plot the waveform
    plt.subplot(3, 1, 1)
    librosa.display.waveshow(y, sr=sr, alpha=0.6)
    plt.title("Waveform of Bird Sound")
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')

    # Mark final segments start and end points
    for start, end in final_segments_time:
        plt.axvline(x=start, color='red', linestyle='--', label='Start Point' if start == final_segments_time[0][0] else "",
                    linewidth=0.1, ymin=0.1, ymax=0.9)
        plt.axvline(x=end, color='blue', linestyle='--', label='End Point' if end == final_segments_time[0][1] else "",
                    linewidth=0.1, ymin=0.1, ymax=0.9)
    plt.legend()

    # Mark final segments
    for start, end in final_segments_time:
        plt.axvspan(start, end, color='green', alpha=0.3, label='Detected Segment')

    # Plot Short-Time Energy (STE)
    plt.subplot(3, 1, 2)
    frames = range(len(energy))
    t = librosa.frames_to_time(frames, sr=sr, hop_length=hop_length)
    plt.plot(t, energy, label='Short-Time Energy', color='blue')
    plt.axhline(T1, color='orange', linestyle='--', label='T1 (Low Threshold)')
    plt.axhline(T2, color='red', linestyle='--', label='T2 (High Threshold)')
    plt.title("Short-Time Energy with Thresholds")
    plt.xlabel('Time (seconds)')
    plt.ylabel('Energy')
    plt.legend(loc='upper right')

    # Plot Short-Time Zero-Crossing Rate (ZCR)
    frames_zcr = range(len(zcr))  # Number of frames corresponding to ZCR
    t_zcr = librosa.frames_to_time(frames_zcr, sr=sr, hop_length=hop_length)
    plt.subplot(3, 1, 3)
    plt.plot(t_zcr, zcr, label='Zero-Crossing Rate', color='purple')
    plt.axhline(T3, color='green', linestyle='--', label='T3 (ZCR Threshold)')
    plt.title("Short-Time Zero-Crossing Rate with Threshold")
    plt.xlabel('Time (seconds)')
    plt.ylabel('ZCR')
    plt.legend(loc='upper right')

    plt.tight_layout()
    plt.show()
    return final_segments_time

gettingSegmentsAndPlot(audio_paths.iloc[0])
