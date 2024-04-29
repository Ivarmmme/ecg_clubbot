from telegram import Update
from telegram.ext import CallbackContext
from typing import Dict, Any
from database import load_data, save_data   

def ranks(update: Update, context: CallbackContext):
    # Get the team data from the database
    team_data = load_data()  # Assuming you have a function to load data from the database

    # Create a dictionary to store the message counts for each team
    message_counts = {}

    # Iterate over the team data to calculate message counts
    for team_name, team_info in team_data.items():
        # Get the list of members for the current team
        members = team_info.get('members', [])

        # Initialize the message count for the current team
        message_count = 0

        # Iterate over the members and sum up their message counts
        for member_id in members:
            # Assuming you have a function to get the message count for each member
            member_message_count = get_message_count(member_id)  
            message_count += member_message_count

        # Store the message count for the current team
        message_counts[team_name] = message_count

    # Sort the teams by message count in descending order
    sorted_teams = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)

    # Generate the message to display ranks
    ranks_message = "Message Ranks:\n"
    for index, (team_name, count) in enumerate(sorted_teams, start=1):
        extra_name = team_data[team_name].get('extra_name', '')
        ranks_message += f"{index}. {team_name} - {extra_name} - ({count})\n"

    # Send the ranks message
    update.message.reply_text(ranks_message)


