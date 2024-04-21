import json
import os
from pyrogram import Client, filters

# File path to store team members data
DATA_FILE = 'team_members.json'

# Load team members data from file
try:
    with open(DATA_FILE, 'r') as f:
        team_members = json.load(f)
except FileNotFoundError:
    team_members = {
        'team1': {'leader_id': '6369933143', 'members': [], 'extra_name': '⚗️ Heisenberg 🧪'},
        'team2': {'leader_id': '7023056247', 'members': [], 'extra_name': '🍌Banana cult 🍌'},
        'team3': {'leader_id': '5449676227', 'members': [], 'extra_name': '🦦 Otter club 🦦'},
        'team4': {'leader_id': '5821282564', 'members': [], 'extra_name': '💰 The Billionaire Club 💰'}
    }

# Function to save team members data to file
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(team_members, f)

# Function to add a member to a team
@Client.on_message(filters.command(["add"]))
def add_member(client, message):
    user_id = str(message.from_user.id)
    text = message.text.split()
    if len(text) != 2:
        message.reply_text("Usage: /add <user_id>")
        return
    
    # Find which team the user is a leader of
    team_name = None
    for team, data in team_members.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        message.reply_text("You are not authorized to add members to any team.")
        return
    
    # Validate the user ID
    member_id = text[1]
    try:
        member_id = int(member_id)
    except ValueError:
        message.reply_text("Invalid user ID. Please provide a valid user ID.")
        return
    
    # Check if the user ID exists in the chat
    # Note: Pyrogram doesn't have a direct equivalent to get_chat_member, so you may need to handle this differently.
    
    # Check if the user being added is already a leader or a member of another team
    for team, data in team_members.items():
        if member_id == int(data['leader_id']):
            message.reply_text("You cannot add another leader to your team.")
            return
        if member_id in data['members']:
            message.reply_text("This user is already a member of another team.")
            return
    
    # Check if the user is already a member of the team
    if str(member_id) in team_members[team_name]['members']:
        message.reply_text("This user is already a member of your team.")
        return
    
    # Check if the user is a member of any other team
    for team, data in team_members.items():
        if str(member_id) in data['members']:
            message.reply_text("This user is already a member of another team.")
            return
    
    # Add the user specified in the command to the team
    team_members[team_name]['members'].append(str(member_id))
    message.reply_text(f"Member {member_id} has been added to {team_name}.")
    save_data()

# Function to remove a member from a team
@Client.on_message(filters.command(["remove"]))
def remove_member(client, message):
    user_id = str(message.from_user.id)
    text = message.text.split()
    if len(text) != 2:
        message.reply_text("Usage: /remove <user_id>")
        return
    
    # Find which team the user is a leader of
    team_name = None
    for team, data in team_members.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        message.reply_text("You are not authorized to remove members from any team.")
        return
    
    # Remove the user specified in the command from the team
    member_id = text[1]
    if member_id in team_members[team_name]['members']:
        team_members[team_name]['members'].remove(member_id)
        message.reply_text(f"Member {member_id} has been removed from {team_name}.")
        save_data()
    else:
        message.reply_text(f"Member {member_id} is not in {team_name}.")

# Function to list the members of a team
@Client.on_message(filters.command(["team1", "team2", "team3", "team4"]))
def team_list(client, message):
    team_name = message.text[1:]
    if team_name in team_members:
        team_info = team_members[team_name]
        leader_id = team_info['leader_id']
        leader = client.get_users(leader_id)
        leader_name = f"{leader.first_name} {leader.last_name if leader.last_name else ''}".strip()
        leader_mention = f"[{leader_name}](tg://user?id={leader_id})"
        
        extra_name = team_info.get('extra_name', '')
        
        members = team_info['members']
        member_mentions = [
            f"[{client.get_users(member).first_name} {client.get_users(member).last_name if client.get_users(member).last_name else ''}](tg://user?id={member})".strip() 
            for member in members
        ]
        
        response = f"| {extra_name} |:\nLeader: {leader_mention}\nMembers:\n"
        response += "\n".join(member_mentions) if member_mentions else "No members."
        
        message.reply_text(response, parse_mode='markdown')

# Initialize the Pyrogram client with API ID, API hash, and bot token from environment variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
app = Client("my_account", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

if __name__ == '__main__':
    app.run()
