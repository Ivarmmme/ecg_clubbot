import os
from telegram.error import BadRequest 
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, CallbackContext, filters
from database import save_data, load_data

async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if the command is replied to a message
    if update.message.reply_to_message:
        replied_user_id = str(update.message.reply_to_message.from_user.id)
        
        team_membersX = load_data()
        
        # Check if the replied user is a member of any team
        is_member = False
        member_info = None
        for team_name, team_info in team_membersX.items():
            if replied_user_id == team_info['leader_id'] or replied_user_id in team_info['members']:
                is_member = True
                member_info = team_info
                break
        
        # Prepare response based on membership status
        if is_member:
            user_full_name = f"{update.message.reply_to_message.from_user.first_name} {update.message.reply_to_message.from_user.last_name or ''}".strip()
            team_extra_name = member_info.get('extra_name', '')
            leader_id = member_info['leader_id']
            leader_name = None
            try:
                leader = await context.bot.get_chat_member(update.effective_chat.id, leader_id)
                leader_name = f"{leader.user.first_name} {leader.user.last_name if leader.user.last_name else ''}".strip()
            except Exception as e:
                print(f"Error: {e}")
            
            response = f"U𝘀𝗲𝗿: {user_full_name}\nT𝗲𝗮𝗺: {team_extra_name}\nL𝗲𝗮𝗱𝗲𝗿: {leader_name}"
        else:
            response = "This user is not a member of any team."
        
        # Send the response
        await context.bot.send_message(update.effective_chat.id, response)
    else:
        await update.message.reply_text("Please reply to a message with the /check command to check membership.")



async def notify_team_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Find out which team the user is a leader of
    team_name = None
    team_membersX = load_data()
    for team, data in team_membersX.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        await context.bot.send_message(update.effective_chat.id, "You are not authorized to send notifications to your team.")
        return
    
    # Check if the message contains text
    if not context.args:
        await context.bot.send_message(update.effective_chat.id, "Please provide a message to send to your team members.")
        return
    
    text = ' '.join(context.args)  # Join command arguments into a single string
    
    # Get team members' first names and last names with mentions
    member_mentions = []
    for member_id in team_membersX[team_name]['members']:
        try:
            member = await context.bot.get_chat_member(update.effective_chat.id, member_id)
            first_name = member.user.first_name
            last_name = member.user.last_name
            if last_name:
                member_name = f"[{first_name} {last_name}](tg://user?id={member.user.id})"
            else:
                member_name = f"[{first_name}](tg://user?id={member.user.id})"
            member_mentions.append(member_name)
        except Exception as e:
            print(f"Error retrieving member info: {e}")
    
    # Prepare the notification message
    notification_message = f"{text}\n\nTeam Members:\n"
    notification_message += "\n".join(member_mentions) if member_mentions else "No members."
    
    # Send the notification message to the team leader
    await context.bot.send_message(update.effective_chat.id, notification_message, parse_mode=ParseMode.MARKDOWN)


# Command handler for /points
async def points_command(update: Update, context):
    # Check if the user is a sudo user
    if is_sudo_user(update.effective_user.id):
        try:
            # Extract points from the command
            points = int(context.args[0])
            if points < 0:
                await update.message.reply_text("Points must be a positive integer.")
                return
            
            # Load team data from the database
            team_membersX = load_data()
            
            # Generate inline keyboard buttons for each team dynamically
            keyboard = []
            for team_name, team_info in team_membersX.items():
                button_text = f"{team_name} - {team_info.get('extra_name', '')}"
                callback_data = f'points_{team_name}_{points}'  # Include points in callback data
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Pick a team to add {points} points:", reply_markup=reply_markup)
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /points <points>")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

# Callback query handler for team selection
async def points_team_selection(update: Update, context):
    query = update.callback_query
    data = query.data.split('_')
    selected_team = data[1]  # Extract selected team from callback data
    points = int(data[2])  # Extract points from the callback query data

    # Check if the user is a sudo user
    if is_sudo_user(query.from_user.id):
        # Load team data from the database
        team_membersX = load_data()
        
        # Update points for the selected team in the database
        if selected_team in team_membersX:
            team_membersX[selected_team]['points'] = team_membersX[selected_team].get('points', 0) + points
            save_data(team_membersX)
            await query.answer(f"{points} points added to {selected_team.title()}.")
        else:
            await query.answer("Invalid team selected.")
    else:
        await query.answer("You are not authorized to add points.")

# Helper function to check if user is a sudo user
def is_sudo_user(user_id):
    sudo_users = [7023056247, 834552248, 1475288014]  # Replace with your sudo users' IDs
    return user_id in sudo_users

# Command handler for /cutpoints
import asyncio

async def cutpoints_command(update: Update, context):
    # Check if the user is a sudo user
    if is_sudo_user(update.effective_user.id):
        try:
            # Extract points from the command
            points = int(context.args[0])
            if points < 0:
                await update.message.reply_text("Points to cut must be a positive integer.")
                return
            
            # Load team data from the database
            team_membersX = load_data()
            
            # Generate inline keyboard buttons for each team dynamically
            keyboard = []
            for team_name, team_info in team_membersX.items():
                button_text = f"{team_name} - {team_info.get('extra_name', '')}"
                callback_data = f'cutpoints_{team_name}_{points}'  # Include points in callback data
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Pick a team to deduct {points} points:", reply_markup=reply_markup)
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /cutpoints <points>")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

# Callback query handler for team selection to cut points
async def cutpoints_team_selection(update: Update, context):
    query = update.callback_query
    data = query.data.split('_')
    selected_team = data[1]  # Extract selected team from callback data
    points = int(data[2])  # Extract points from the callback query data

    # Check if the user is a sudo user
    if is_sudo_user(query.from_user.id):
        # Load team data from the database
        team_membersX = load_data()
        
        # Deduct points from the selected team in the database
        if selected_team in team_membersX:
            current_points = team_membersX[selected_team].get('points', 0)
            if current_points >= points:
                team_membersX[selected_team]['points'] = current_points - points
                save_data(team_membersX)
                await query.answer(f"{points} points deducted from {selected_team.title()}.")
            else:
                await query.answer("Not enough points to deduct.")
        else:
            await query.answer("Invalid team selected.")
    else:
        await query.answer("You are not authorized to deduct points.")


active_join_requests = {}

async def handle_request_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    # Load team data from the database
    team_membersX = load_data()
    
    # Check if the user already has an active join request section
    if user_id in active_join_requests:
        await update.message.reply_text("You already have an active join request section.")
        return
    
    # Create a new section for the user's join request
    active_join_requests[user_id] = {'team_selected': False}
    
    # Generate team selection buttons
    team_buttons = []
    for team_name, team_info in team_membersX.items():
        button_text = f"{team_name} - {team_info.get('extra_name', '')}"
        team_buttons.append([InlineKeyboardButton(button_text, callback_data=f"team_selection_{team_name}")])
    
    # Create inline keyboard markup
    reply_markup = InlineKeyboardMarkup(team_buttons)
    
    # Send message with team selection buttons
    await update.message.reply_text("Select a team to join:", reply_markup=reply_markup)        

async def handle_team_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data.split('_')
    team_name = data[-1]
    
    # Load team data from the database
    team_membersX = load_data()
    
    # Check if the user has an active join request section
    if user_id not in active_join_requests:
        await query.answer("You don't have an active join request section.")
        return
    
    # Check if the user has already selected a team
    if active_join_requests[user_id]['team_selected']:
        await query.answer("You have already selected a team.")
        return
    
    # Mark team as selected for the user
    active_join_requests[user_id]['team_selected'] = True
    
    # Notify the team leader about the join request
    team_leader_id = team_membersX[team_name]['leader_id']
    user = query.from_user
    user_mention = f"{user.first_name} {user.last_name if user.last_name else ''} (<code>{user.id}</code>)"
    
    await context.bot.send_message(
        chat_id=team_leader_id,
        text=f"Join request from {user_mention} for team {team_name}.",
        parse_mode=ParseMode.HTML
    )
    
    # Edit the original message to inform the user that the request has been sent to the leader
    await query.message.edit_text(f"Your join request has been sent to the leader of {team_name} - {team_membersX[team_name].get('extra_name', '')}.")

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
    team_membersX = load_data()

    # Find which team the user is a leader of
    team_name = None
    for team, data in team_membersX.items():
        if data['leader_id'] == user_id:
            team_name = team
            break
    
    if not team_name:
        await update.message.reply_text("You are not authorized to remove members from any team.")
        return
    
    # Remove all members from the user's team
    if team_membersX[team_name]['members']:
        team_membersX[team_name]['members'] = []  # Clear the list of members
        save_data(team_membersX)  # Save the updated data
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
            
            # Retrieve points for the team and handle empty points case
            total_points = team_info.get('points', '0') if team_info.get('points', '') != '' else '0'
            
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
            
            response = f"| {extra_name} |:\nLeader: {leader_mention}\n𝐓𝐨𝐭𝐚𝐥 𝐏𝐨𝐢𝐧𝐭𝐬: {total_points}\nMembers:\n"
            response += "\n".join(member_names) if member_names else "No members."
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    except BadRequest as e:
        print(f"Error: {e}")

async def list_teams_with_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        team_membersX = load_data()
        
        response = ""
        for team_name, team_info in team_membersX.items():
            extra_name = team_info.get('extra_name', '')
            points = team_info.get('points', 0)
            message_count = team_info.get('message_count', 0)
            response += f"{extra_name}\nPoints: **{points}**\nTotal Messages: **{message_count}**\n\n"
        
        await context.bot.send_message(update.effective_chat.id, response, parse_mode=ParseMode.MARKDOWN)
    
    except BadRequest as e:
        print(f"Error: {e}")

async def track_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract relevant information from the message
    user_id = str(update.effective_user.id)
    user_data = update.effective_user.to_dict()
    chat_id = update.effective_chat.id
    
    # Check if the message is from the specified group
    specified_group_id = -1001289294178  # Replace with the ID of your specified group
    if chat_id != specified_group_id:
        return
    
    team_membersX = load_data()

    # Check if the user sending the message is a team member
    for team_name, team_info in team_membersX.items():
        if user_id == team_info['leader_id'] or user_id in team_info['members']:
            # Update the message count for the corresponding team
            team_info['message_count'] += 1
            # Save the updated team data to the MongoDB collection
            save_data(team_membersX)
            break


async def convert_messages_to_points():
    try:
        team_membersX = load_data()
        
        for team_name, team_info in team_membersX.items():
            message_count = team_info.get('message_count', 0)
            # Calculate points based on message count
            points = message_count // 1000 * 10  # 10 points for every 1000 messages
            remaining_messages = message_count % 1000
            points += remaining_messages / 1000 * 10  # Additional points for remaining messages
            
            # Update points for the team
            team_info['points'] = points
        
        # Save the updated team data to the MongoDB collection
        save_data(team_membersX)
    
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
    application.add_handler(CommandHandler("request", handle_request_command))
    application.add_handler(CallbackQueryHandler(handle_team_selection_callback, pattern=r'^team_selection_'))
    application.add_handler(CommandHandler("points", points_command))
    application.add_handler(CallbackQueryHandler(points_team_selection, pattern=r'^points_'))
    # Add command and callback query handlers to the application
    application.add_handler(CommandHandler('cut', cutpoints_command))
    application.add_handler(CallbackQueryHandler(cutpoints_team_selection, pattern=r'^cutpoints_'))
    application.add_handler(CommandHandler('ranks', list_teams_with_points))
    application.add_handler(CommandHandler("notify", notify_team_members))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_messages))
    # Add command handler for /check command
    application.add_handler(CommandHandler("check", check_membership))
    application.add_handler(CommandHandler("ch", check_membership))
    application.run_polling()

if __name__ == '__main__':
    main()


    
