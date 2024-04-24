import dns.resolver
import os
import pymongo
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, CallbackContext

# Manually configure the default DNS resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google's public DNS servers

# MongoDB connection details
MONGO_URL = "mongodb+srv://ivarmone:ivarmone009@cluster0.ggfwxno.mongodb.net/"
DB_NAME = "ivarmone"
COLLECTION_NAME = "team_members"

# Initialize MongoDB client
client = pymongo.MongoClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Function to save team members data to MongoDB
def save_data(team_members):
    collection.update_one({}, {"$set": {"team_members": team_members}}, upsert=True)

# Function to load team members data from MongoDB
def load_data():
    data = collection.find_one({})
    if data:
        return data.get("team_members", {})
    else:
        return {
            'team1': {'leader_id': '6369933143', 'members': [], 'extra_name': '👁️⃤ Goated Club🐐'},
            'team2': {'leader_id': '7196174452', 'members': [], 'extra_name': '🪬 Banana cult 🌵'},
            'team3': {'leader_id': '5449676227', 'members': [], 'extra_name': '🦦 Otters club 🦦'},
            'team4': {'leader_id': '5821282564', 'members': [], 'extra_name': '💰 The Billionaire Club 💰'}
        }

# Function to handle the /req command
async def request_to_join(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    full_name = update.effective_user.full_name
    
    # Check if the user is a member of any team
    team_members = load_data()
    for team, data in team_members.items():
        if user_id == data['leader_id'] or user_id in data['members']:
            await update.message.reply_text("You are already a member of a team or a team leader.")
            return
    
    # Get the list of teams and their extra information
    team_buttons = []
    for team, data in team_members.items():
        extra_info = data.get('extra_name', '')
        button_text = f"{team} - {extra_info}"
        team_buttons.append([InlineKeyboardButton(button_text, callback_data=team)])
    
    # Create inline keyboard markup with team selection buttons
    reply_markup = InlineKeyboardMarkup(team_buttons)
    
    # Send message asking user to select a team
    await update.message.reply_text(
        f"{full_name}, select the team you want to request to join:",
        reply_markup=reply_markup
    )

    # Create inline keyboard markup with team selection buttons
    reply_markup = InlineKeyboardMarkup(team_buttons)
    
    # Send message asking user to select a team
    await update.message.reply_text(
        f"{full_name}, select the team you want to request to join:",
        reply_markup=reply_markup
    )

# Function to handle the team join request
async def handle_join_request(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(update.effective_user.id)
    user_full_name = update.effective_user.full_name
    team_name = query.data
    
    # Get the team leader ID from the database
    team_members = load_data()
    team_leader_id = team_members.get(team_name, {}).get('leader_id')
    
    # Check if the team leader is found
    if not team_leader_id:
        await query.message.reply_text("Error: Team leader not found.")
        return
    
    # Check if the user is already a member of any team or a team leader
    for team, data in team_members.items():
        if user_id == data['leader_id'] or user_id in data['members']:
            await query.message.reply_text("You are already a member of a team or a team leader.")
            return
    
    # Check if the accept or reject button was clicked
    if query.data.startswith("accept"):
        # Add the user to the team in the database
        if user_id not in team_members[team_name]['members']:
            team_members[team_name]['members'].append(user_id)
            save_data(team_members)
            await query.message.reply_text("You have accepted the join request. The user has been added to your team.")
        else:
            await query.message.reply_text("The user is already a member of your team.")
    else:
        await query.message.reply_text("You have rejected the join request.")

    # Answer the callback query to remove the "processing" status
    await query.answer()

# Function to allow a member to leave a team
async def leave_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    team_members = load_data()

    left_team = None
    # Check all teams to see if the user is a member and not the leader
    for team, data in team_members.items():
        if data['leader_id'] == user_id:
            await update.message.reply_text("You are the leader of the team and cannot leave using this command.")
            return
        
        if user_id in data['members']:
            data['members'].remove(user_id)
            left_team = team
            break

    if left_team:
        save_data(team_members)
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
    team_members = load_data()
    for team, data in team_members.items():
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
    for team, data in team_members.items():
        if member_id == int(data['leader_id']):
            await update.message.reply_text("You cannot add another leader to your team.")
            return
        if member_id in data['members']:
            await update.message.reply_text("This user is already a member of another team.")
            return
    
    # Check if the user is already a member of the team
    if str(member_id) in team_members[team_name]['members']:
        await update.message.reply_text("This user is already a member of your team.")
        return
    
    # Check if the user is a member of any other team
    for team, data in team_members.items():
        if str(member_id) in data['members']:
            await update.message.reply_text("This user is already a member of another team.")
            return
    
    # Add the user specified in the command to the team
    team_members[team_name]['members'].append(str(member_id))
    await update.message.reply_text(f"Member {member_id} has been added to {team_name}.")
    save_data(team_members)

# Function to remove a member from a team
async def remove_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.split()
    if len(text) != 2:
        await update.message.reply_text("Usage: /remove <user_id>")
        return
    
    # Find which team the user is a leader of
    team_name = None
    team_members = load_data()
    for team, data in team_members.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        await update.message.reply_text("You are not authorized to remove members from any team.")
        return
    
    # Remove the user specified in the command from the team
    member_id = text[1]
    if member_id in team_members[team_name]['members']:
        team_members[team_name]['members'].remove(member_id)
        await update.message.reply_text(f"Member {member_id} has been removed from {team_name}.")
        save_data(team_members)
    else:
        await update.message.reply_text(f"Member {member_id} is not in {team_name}.")

# Function to list the members of a team
async def team_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        team_name = context.args[0] if context.args else update.message.text[1:]
        team_members = load_data()
        if team_name in team_members:
            team_info = team_members[team_name]
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
    application.add_handler(CommandHandler("req", request_to_join))
    application.add_handler(CallbackQueryHandler(handle_join_request))
   
    application.run_polling()

if __name__ == '__main__':
    main()
