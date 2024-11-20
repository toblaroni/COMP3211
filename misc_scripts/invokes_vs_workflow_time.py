import matplotlib.pyplot as plt

# Number of invokes
num_invokes = [2, 4, 6, 8, 10, 15, 20]
# Seconds from first upload to last analysis
workflow_time = [133, 150, 128, 180, 185, 137, 164]

plt.figure(figsize=(10, 6))
plt.bar(num_invokes, workflow_time, color='b', edgecolor='black')
plt.xlabel('Number of Invokes')
plt.ylabel('Workflow Time (seconds)')
plt.title('Workflow Time vs Number of Invokes')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig("./invokes_vs_workflow_time.png")
plt.show()
