import matplotlib.pyplot as plt
import numpy as np

# file size (MB)
audio_file_sizes = [0.32, 0.95, 1.8, 3.7, 7.3, 15]
# Workflow time (seconds)
# 600 is maximum because it timed out for both of those
workflow_time = [95, 112, 85, 168, 600, 600]

plt.figure(figsize=(8, 6))
plt.bar(audio_file_sizes, workflow_time, color='blue', width=0.3)

plt.title('Workflow Time vs File Size')
plt.xlabel('Audio File Size (MB)')
plt.ylabel('Workflow Time (seconds)')

plt.xticks(np.arange(min(audio_file_sizes), max(audio_file_sizes) + 1, 1.5))  # Step size of 2

# Display grid
plt.grid(True)

# Show the plot
plt.savefig("./filesize_vs_time.png")
plt.show()