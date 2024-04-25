import dns.resolver
import os
from telegram.error import BadRequest 
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
import pymongo

# Manually configure the default DNS resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google's public DNS servers

# MongoDB connection details
MONGO_URL = "mongodb+srv://ivarmone:ivarmone009@cluster0.ggfwxno.mongodb.net/"
DB_NAME = "ivarmone"
COLLECTION_NAME = "team_membersX"

# Initialize MongoDB client
client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Function to save team members data to MongoDB
def save_data(team_members): collection.update_one({}, {"$set": {"team_membersX": team_members}}, upsert=True)

# Function to load team members data from MongoDB
def load_data():
    data = collection.find_one({})
    if data:
        return data.get("team_membersX", {})
    else:
        return {
            'team1': {'leader_id': '6369933143', 'members': [], 'extra_name': '👁️⃤ Goated Club'},
            'team2': {'leader_id': '7196174452', 'members': [], 'extra_name': '☮ Archangels ☮'},
            'team3': {'leader_id': '6824897749', 'members': [], 'extra_name': '🦦 Otters club 🦦'},
            'team4': {'leader_id': '5821282564', 'members': [], 'extra_name':'💰 The Billionaires Club 💰'},
            'team5': {'leader_id': '5920451104', 'members': [], 'extra_name': '👑Imperial🦇'}
        }
# Function to mass add members to a team

async def mass_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.split()
    if len(text) < 2:
        await update.message.reply_text("Usage: /madd <user_id1> <user_id2> <user_id3> ...")
        return
    
    # Find which team the user is a leader of
    team_name = None
    team_membersX = load_data()  # You'll need to import load_data from your main script
    for team, data in team_membersX.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        await update.message.reply_text("You are not authorized to add members to any team.")
        return
    
    # Check if the team has reached its member limit
    max_members_per_team = 11  # Set your desired limit here
    current_members_count = len(team_membersX[team_name]['members'])
    if current_members_count >= max_members_per_team:
        await update.message.reply_text(f"Sorry, {team_name} has reached the maximum member limit.")
        return
    
    # Initialize flag to track cancellation
    cancel_command = False
    
    # Check each user ID provided in the command
    for member_id in text[1:]:
        try:
            member_id = int(member_id)
        except ValueError:
            await update.message.reply_text(f"Invalid user ID: {member_id}. Skipping.")
            cancel_command = True
            break
        
        # Check if the user is a leader of any team
        for data in team_membersX.values():
            if member_id == int(data['leader_id']):
                await update.message.reply_text(f"Cannot add user {member_id}: a leader cannot be added as a member.")
                cancel_command = True
                break
        
        if cancel_command:
            break
        
        # Check if the user is a member of any other team
        for other_team, other_data in team_membersX.items():
            if str(member_id) in other_data['members']:
                await update.message.reply_text(f"Cannot add user {member_id}: already a member of another team.")
                cancel_command = True
                break
        
        if cancel_command:
            break
        
        # Check if the user is already a member of the team
        if str(member_id) in team_membersX[team_name]['members']:
            await update.message.reply_text(f"Cannot add user {member_id}: already a member of this team.")
            cancel_command = True
            break
    
    # If any condition triggered cancellation, abort command execution
    if cancel_command:
        await update.message.reply_text("Mass addition canceled.")
        return
    
    # If all checks passed, add the users to the team
    for member_id in text[1:]:
        team_membersX[team_name]['members'].append(str(member_id))
    
    save_data(team_membersX)
    await update.message.reply_text(f"Members have been added to {team_name}.")
    
# function to removeall members from team
async def remove_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Load the current teams and members data
    team_members = load_data()

    # Find which team the user is a leader of
    team_name = None
    for team, data in team_members.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        await update.message.reply_text("You are not authorized to remove members from any team.")
        return
    
    # Remove all members from the user's team
    if team_members[team_name]['members']:
        team_members[team_name]['members'] = []  # Clear the list of members
        save_data(team_members)  # Save the updated data
        await update.message.reply_text(f"All members have been removed from {team_name}.")
    else:
        await update.message.reply_text("There are no members to remove in your team.")
        
# Function to allow a member to leave a team
async def leave_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    team_membersX = load_data()

    left_team = None
    # Check all teams to see if the user is a member and not the leader
    for team, data in team_membersX.items():
        if data['leader_id'] == user_id:
            await update.message.reply_text("You are the leader of the team and cannot leave using this command.")
            return
        
        if user_id in data['members']:
            data['members'].remove(user_id)
            left_team = team
            break

    if left_team:
        save_data(team_membersX)
        await update.message.reply_text(f"You have left {left_team}.")
    else:
        await update.message.reply_text("You are not a member of any team.")

# Function to add a member to a team
async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.split()
    if len(text) != 2:
        await update.message.reply_text("Usage: /add <user_id>")
        return
    
    # Find which team the user is a leader of
    team_name = None
    team_membersX = load_data()
    for team, data in team_membersX.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        await update.message.reply_text("You are not authorized to add members to any team.")
        return
    
    # Validate the user ID
    member_id = text[1]
    try:
        member_id = int(member_id)
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a valid user ID.")
        return

    # Check if the team has reached its member limit
    max_members_per_team = 11  # Set your desired limit here
    current_members_count = len(team_membersX[team_name]['members'])
    if current_members_count >= max_members_per_team:
        await update.message.reply_text(f"Sorry, {team_name} has reached the maximum member limit.")
        return
        
    # Check if the user ID exists in the chat
    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, member_id)
    except telegram.error.BadRequest as e:
        await update.message.reply_text("Invalid user ID. Please provide a valid user ID.")
        return
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return
    
    # Check if the user being added is already a leader or a member of another team
    for team, data in team_membersX.items():
        if member_id == int(data['leader_id']):
            await update.message.reply_text("You cannot add another leader to your team.")
            return
        if member_id in data['members']:
            await update.message.reply_text("This user is already a member of another team.")
            return
    
    # Check if the user is already a member of the team
    if str(member_id) in team_membersX[team_name]['members']:
        await update.message.reply_text("This user is already a member of your team.")
        return
    
    # Check if the user is a member of any other team
    for team, data in team_membersX.items():
        if str(member_id) in data['members']:
            await update.message.reply_text("This user is already a member of another team.")
            return
    
    # Add the user specified in the command to the team
    team_membersX[team_name]['members'].append(str(member_id))
    await update.message.reply_text(f"Member {member_id} has been added to {team_name}.")
    save_data(team_membersX)

# Function to remove a member from a team
async def remove_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.split()
    if len(text) != 2:
        await update.message.reply_text("Usage: /remove <user_id>")
        return
    
    # Find which team the user is a leader of
    team_name = None
    team_membersX = load_data()
    for team, data in team_membersX.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        await update.message.reply_text("You are not authorized to remove members from any team.")
        return
    
    # Remove the user specified in the command from the team
    member_id = text[1]
    if member_id in team_membersX[team_name]['members']:
        team_membersX[team_name]['members'].remove(member_id)
        await update.message.reply_text(f"Member {member_id} has been removed from {team_name}.")
        save_data(team_membersX)
    else:
        await update.message.reply_text(f"Member {member_id} is not in {team_name}.")

# Function to list the members of a team
async def team_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        team_name = context.args[0] if context.args else update.message.text[1:]
        team_membersX = load_data()
        if team_name in team_membersX:
            team_info = team_membersX[team_name]
            leader_id = team_info['leader_id']
            leader_mention = None
            leader = await context.bot.get_chat_member(update.effective_chat.id, leader_id)
            leader = leader.user
            if leader:
                leader_name = f"{leader.first_name} {leader.last_name if leader.last_name else ''}".strip()
                leader_mention = f"[{leader_name}](tg://user?id={leader_id})"
            
            extra_name = team_info.get('extra_name', '')
            
            members = team_info['members']
            member_mentions = [
                await context.bot.get_chat_member(update.effective_chat.id, member)
                for member in members
            ]
            
            member_names = []
            for member_mention in member_mentions:
                member = member_mention.user
                member_name = f"{member.first_name} {member.last_name if member.last_name else ''}".strip()
                member_names.append(f"[{member_name}](tg://user?id={member_mention.user.id})")
            
            response = f"| {extra_name} |:\nLeader: {leader_mention}\nMembers:\n"
            response += "\n".join(member_names) if member_names else "No members."
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    except BadRequest as e:
        print(f"Error: {e}")
        
def main():
    # Get the bot token from an environment variable
    bot_token = os.environ.get("BOT_TOKEN")  # Replace with your actual environment variable name

    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("add", add_member))
    application.add_handler(CommandHandler("remove", remove_member))
    application.add_handler(CommandHandler("leave", leave_team))
    application.add_handler(CommandHandler("team1", team_list))
    application.add_handler(CommandHandler("team2", team_list))
    application.add_handler(CommandHandler("team3", team_list))
    application.add_handler(CommandHandler("team4", team_list))
    application.add_handler(CommandHandler("team5", team_list))
    application.add_handler(CommandHandler("madd", mass_add))
    application.add_handler(CommandHandler("removeall", remove_all))

    application.run_polling()

if __name__ == '__main__':
    main()


    
