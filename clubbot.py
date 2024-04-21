import json
import os
from telegram import Update 
from telegram.ext import Updater, CommandHandler, CallbackContext

# File path to store team members data
DATA_FILE = 'team_members.json'

# Load team members data from file
try:
    with open(DATA_FILE, 'r') as f:
        team_members = json.load(f)
except FileNotFoundError:
    team_members = {
        'team1': {'leader_id': '6369933143', 'members': [], 'extra_name': '⚗️ Heisenberg club🧪'},
        'team2': {'leader_id': '7196174452', 'members': [], 'extra_name': '🍌Banana cult 🍌'},
        'team3': {'leader_id': '5449676227', 'members': [], 'extra_name': '🦦 Otter club 🦦'},
        'team4': {'leader_id': '5821282564', 'members': [], 'extra_name': '💰 The Billionaire Club 💰'}
    }

# Function to save team members data to file
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(team_members, f)

# Function to add a member to a team
def add_member(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text.split()
    if len(text) != 2:
        if update.message:
            update.message.reply_text("Usage: /add <user_id>")
        return
    
    # Find which team the user is a leader of
    team_name = None
    for team, data in team_members.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        if update.message:
            update.message.reply_text("You are not authorized to add members to any team.")
        return
    
    # Validate the user ID
    member_id = text[1]
    try:
        member_id = int(member_id)
    except ValueError:
        if update.message:
            update.message.reply_text("Invalid user ID. Please provide a valid user ID.")
        return
    
    # Check if the user ID exists in the chat
    try:
        member = context.bot.get_chat_member(update.effective_chat.id, member_id)
    except telegram.error.BadRequest as e:
        if update.message:
            update.message.reply_text("Invalid user ID. Please provide a valid user ID.")
        return
    except Exception as e:
        if update.message:
            update.message.reply_text(f"Error: {e}")
        return
    
    # Check if the user being added is already a leader or a member of another team
    for team, data in team_members.items():
        if member_id == int(data['leader_id']):
            if update.message:
                update.message.reply_text("You cannot add another leader to your team.")
            return
        if member_id in data['members']:
            if update.message:
                update.message.reply_text("This user is already a member of another team.")
            return
    
    # Check if the user is already a member of the team
    if str(member_id) in team_members[team_name]['members']:
        if update.message:
            update.message.reply_text("This user is already a member of your team.")
        return
    
    # Check if the user is a member of any other team
    for team, data in team_members.items():
        if str(member_id) in data['members']:
            if update.message:
                update.message.reply_text("This user is already a member of another team.")
            return
    
    # Add the user specified in the command to the team
    team_members[team_name]['members'].append(str(member_id))
    if update.message:
        update.message.reply_text(f"Member {member_id} has been added to {team_name}.")
    save_data()

# Function to remove a member from a team
def remove_member(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text.split()
    if len(text) != 2:
        if update.message:
            update.message.reply_text("Usage: /remove <user_id>")
        return
    
    # Find which team the user is a leader of
    team_name = None
    for team, data in team_members.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        if update.message:
            update.message.reply_text("You are not authorized to remove members from any team.")
        return
    
    # Remove the user specified in the command from the team
    member_id = text[1]
    if member_id in team_members[team_name]['members']:
        team_members[team_name]['members'].remove(member_id)
        if update.message:
            update.message.reply_text(f"Member {member_id} has been removed from {team_name}.")
        save_data()
    else:
        if update.message:
            update.message.reply_text(f"Member {member_id} is not in {team_name}.")

# Function to list the members of a team
def team_list(update: Update, context: CallbackContext):
    team_name = context.args[0] if context.args else update.message.text[1:]
    if team_name in team_members:
        team_info = team_members[team_name]
        leader_id = team_info['leader_id']
        leader = context.bot.get_chat_member(update.effective_chat.id, leader_id).user
        leader_name = f"{leader.first_name} {leader.last_name if leader.last_name else ''}".strip()
        leader_mention = f"[{leader_name}](tg://user?id={leader_id})"
        
        extra_name = team_info.get('extra_name', '')
        
        members = team_info['members']
        member_mentions = [
            f"[{context.bot.get_chat_member(update.effective_chat.id, member).user.first_name} {context.bot.get_chat_member(update.effective_chat.id, member).user.last_name if context.bot.get_chat_member(update.effective_chat.id, member).user.last_name else ''}](tg://user?id={member})".strip() 
            for member in members
        ]
        
        response = f"| {extra_name} |:\nLeader: {leader_mention}\nMembers:\n"
        response += "\n".join(member_mentions) if member_mentions else "No members."
        
        if update.message:
            update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

def main():
    # Get the bot token from the environment variables
    bot_token = os.environ.get("BOT_TOKEN")
    if bot_token is None:
        print("Error: Bot token not found in environment variables.")
        return
    
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("add", add_member))
    dp.add_handler(CommandHandler("remove", remove_member))
    dp.add_handler(CommandHandler("team1", team_list))
    dp.add_handler(CommandHandler("team2", team_list))
    dp.add_handler(CommandHandler("team3", team_list))
    dp.add_handler(CommandHandler("team4", team_list))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
