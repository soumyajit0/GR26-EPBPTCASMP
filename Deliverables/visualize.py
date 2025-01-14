import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation
import threading
import time


# Global dictionary to store the counts of each personality type
personality_counts = dict()
User = "Mark Zuckerberg"  # Global user placeholder
current_url=None


from __init__ import set_dir
set_dir()

def reset(url,name):
    """Reset the user's name and clear personality counts."""
    global User, personality_counts,current_url
    current_url=url
    User = name
    personality_counts = dict()


def predict_personality_dynamically(Type):
    """Update personality counts based on new 'Type' received."""
    global personality_counts
    
    # Update the count for the given personality Type
    if Type in personality_counts:
        personality_counts[Type] += 1
    else:
        personality_counts[Type] = 1
    
    return personality_counts

def update_frame(url,Type):
    if current_url and url!=current_url:
        return True
    predict_personality_dynamically(Type)
    return True

def calculate_percentages(counts):
    """Calculate the percentages of each personality type based on total counts."""
    total = sum(counts.values())
    percentages = {ptype: (count / total) * 100 for ptype, count in counts.items()} if total > 0 else {}
    return percentages

def update_plot(frame):
    global User, personality_counts,name_mapping
    # Clear the plot if no data is available
    if len(personality_counts) == 0:
        ax[0].cla()
        ax[1].cla()
        ax[0].axis('off')
        ax[1].axis('off')
        ax[0].set_title("No Data Available", fontsize=14, fontweight='bold', pad=0)
        return

    counts = personality_counts

    # Calculate percentages based on the updated counts
    percentages = calculate_percentages(counts)
    
    personality_types = list(counts.keys())
    probabilities = list(percentages.values())
    
    # Clear previous axes to redraw updated figures
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

    ax[0].set_title(f'Personality Prediction for {User}', fontsize=14, fontweight='bold', pad=0)  

    table = ax[0].table(cellText=df.values,
                        colLabels=df.columns,
                        cellLoc='center',
                        loc='center')

    table.scale(1, 2)

    # Update the pie chart
    ax[1].pie(probabilities, labels=personality_types, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax[1].axis('equal')
    ax[1].set_title('Personality Distribution', fontsize=14, fontweight='bold', pad=0)  


def visualize_personality_predictions():
    global fig, ax
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    fig.subplots_adjust(top=0.75)
    # Add padding from top
    # Set up animation to update the plot every 500 mills
    animation = FuncAnimation(fig, update_plot, interval=500)

    # Show the initial plot window
    plt.tight_layout()
    plt.show()



if __name__=="__main__":
    threading.Thread(target=visualize_personality_predictions).start()
    update_frame("INFJ")
    update_frame("ISTP")
    time.sleep(4)
    update_user_name("abc","Pinaki")
    reset("abcdd","abc")