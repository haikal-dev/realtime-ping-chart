#!/usr/bin/env python3

import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import subprocess
import sys

# Ping target from command line argument
ping_target = sys.argv[1]

# Initialize an empty list to store ping times
ping_times = []

# Create the plot
fig, ax = plt.subplots()
line, = ax.plot(ping_times)
ax.set_ylim(0, 200)  # Adjust y-limit to ensure we can see points above 100ms

# Initialize a variable to hold the latest point annotation
latest_annotation = None

# Add a text element for max, min, and average values
stats_text = ax.text(0.95, 0.95, '', transform=ax.transAxes, ha='right', va='top',
                     bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

# Add an annotation for the tooltip
tooltip = ax.annotate('', xy=(0, 0), xytext=(10, 10),
                      textcoords='offset points', bbox=dict(boxstyle='round,pad=0.5', fc='white', edgecolor='black'),
                      arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2'),
                      visible=False)

# Function to update the plot with new ping data
def update(frame):
    global latest_annotation  # Use global to track the latest annotation

    # Run the ping command and capture the output
    result = subprocess.run(["ping", "-c", "1", ping_target], capture_output=True, text=True)

    # Extract the ping time using regex
    ping_time_match = re.search(r'time=(\d+\.\d+)', result.stdout)

    if ping_time_match:
        ping_time = float(ping_time_match.group(1))
        
        ping_times.append(ping_time)

        # Limit the number of points shown on the graph
        if len(ping_times) > 100:
            ping_times.pop(0)

        # Update the line data
        line.set_data(range(len(ping_times)), ping_times)
        ax.set_xlim(0, len(ping_times))

        # Label every point that exceeds 100ms
        # if ping_time > 100:
        #     ax.annotate(f'{ping_time}ms', 
        #                 xy=(len(ping_times) - 1, ping_time),
        #                 xytext=(len(ping_times) - 1, ping_time + 10),
        #                 arrowprops=dict(facecolor='red', shrink=0.05),
        #                 bbox=dict(facecolor='yellow', edgecolor='red', boxstyle='round,pad=0.5'))

        # Remove the previous latest annotation
        if latest_annotation:
            latest_annotation.remove()

        # Always label the latest point, regardless of value
        latest_annotation = ax.annotate(f'{ping_time}ms', 
                                        xy=(len(ping_times) - 1, ping_time),
                                        xytext=(len(ping_times) - 1, ping_time + 5),
                                        arrowprops=dict(arrowstyle="->"),
                                        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

        # Calculate real-time statistics
        min_ping = min(ping_times)
        max_ping = max(ping_times)
        avg_ping = sum(ping_times) / len(ping_times)

        # Update the stats text
        stats_text.set_text(f'Max: {max_ping:.2f} ms\nMin: {min_ping:.2f} ms\nAvg: {avg_ping:.2f} ms')

    return line,

# Event handler for mouse motion
def on_mouse_move(event):
    if event.inaxes == ax:
        # Get the x and y coordinates of the mouse
        x, y = event.xdata, event.ydata
        
        # Find the closest data point
        if len(ping_times) > 0:
            xdata = range(len(ping_times))
            ydata = ping_times
            distances = [(xi - x) ** 2 + (yi - y) ** 2 for xi, yi in zip(xdata, ydata)]
            closest_idx = distances.index(min(distances))

            # Update tooltip text and position
            tooltip.set_text(f'{ping_times[closest_idx]:.2f} ms')
            tooltip.xy = (xdata[closest_idx], ydata[closest_idx])
            tooltip.set_visible(True)
        else:
            tooltip.set_visible(False)
        fig.canvas.draw_idle()
    else:
        tooltip.set_visible(False)
        fig.canvas.draw_idle()

# Set up the animation
ani = animation.FuncAnimation(fig, update, interval=1000)  # Update every second

# Connect the event handler
fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

# Show the plot
plt.xlabel("Ping Number")
plt.ylabel("Ping Time (ms)")
plt.title("Real-time Latency Chart")
plt.show()
