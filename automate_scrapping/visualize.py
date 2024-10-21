import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
import threading
import time
import random

# Global dictionary to store the counts of each personality type
personality_counts = dict()
User = "Mark Zuckerberg"  # Global user placeholder

def predict_personality_dynamically(Type):
    """Update personality counts based on new 'Type' received."""
    global personality_counts
    
    # Update the count for the given personality Type
    if Type in personality_counts:
        personality_counts[Type] += 1
    else:
        personality_counts[Type] = 1
    
    return personality_counts

def update_frame(Type):
    predict_personality_dynamically(Type)
    return True

def calculate_percentages(counts):
    """Calculate the percentages of each personality type based on total counts."""
    total = sum(counts.values())
    percentages = {ptype: (count / total) * 100 for ptype, count in counts.items()}
    return percentages

def update_plot(frame):
    if len(personality_counts) == 0:
        return
    global User
    counts = personality_counts

    # Calculate percentages based on the updated counts
    percentages = calculate_percentages(counts)
    
    personality_types = list(counts.keys())
    probabilities = list(percentages.values())
    
    # Clear the previous axes to redraw updated figures
    ax[0].cla()  # Clear the table plot area
    ax[1].cla()  # Clear the pie chart plot area

    # Create a pandas DataFrame for the table
    df = pd.DataFrame({
        'Personality Type': personality_types,
        'Count': [counts[ptype] for ptype in personality_types],
        'Percentage': [f"{percentages[ptype]:.2f}%" for ptype in personality_types]
    })

    # Update the table with the new data
    ax[0].axis('off')
    ax[0].set_title(f'Personality Prediction for {User}', fontsize=14, fontweight='bold')
    table = ax[0].table(cellText=df.values,
                        colLabels=df.columns,
                        cellLoc='center',
                        loc='center')
    table.scale(1, 2)

    # Update the pie chart
    ax[1].pie(probabilities, labels=personality_types, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax[1].axis('equal')
    ax[1].set_title('Personality Distribution', fontsize=14, fontweight='bold')

def visualize_personality_predictions():
    global fig, ax
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    # Set up animation to update the plot every 1 second (1000 milliseconds)
    animation = FuncAnimation(fig, update_plot, interval=500)

    # Show the initial plot window
    plt.tight_layout()
    plt.show()

def receive_data_and_update():
    """Simulates receiving data and updates the frame."""
    personality_types = ["INTJ", "ENFP", "ISTP", "ENTJ", "INFJ"]  # Example personality types
    
    while True:
        # Simulate predicting a random personality type
        new_prediction = random.choice(personality_types)
        print(f"New prediction: {new_prediction}")

        # Update the frame with the new prediction
        update_frame(new_prediction)

        # Sleep for some time to simulate real-time data prediction intervals
        time.sleep(2)  # Adjust this as needed

def start_receiving_data():
    """Starts a thread that simulates data reception."""
    data_thread = threading.Thread(target=receive_data_and_update)
    data_thread.daemon = True  # Daemon thread will exit when the main program exits
    data_thread.start()

# # Start the data reception thread
# #start_receiving_data()

# # Start the visualization
# visualize_personality_predictions()
