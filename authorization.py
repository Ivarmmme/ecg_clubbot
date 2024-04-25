from telegram import Update
from telegram.ext import ContextTypes
from clubbot import load_data, save_data

async def authorize_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("You are not authorized to perform this action.")
        return
    
    text = update.message.text.split()
    if len(text) != 2:
        await update.message.reply_text("Usage: /auth <user_id>")
        return

    member_id = text[1]
    if member_id not in team_members[team_name]['members']:
        await update.message.reply_text("The specified user is not a member of your team.")
        return
    
    if 'auth_users' not in team_members[team_name]:
        team_members[team_name]['auth_users'] = []

    if member_id in team_members[team_name]['auth_users']:
        await update.message.reply_text("The specified user is already an authorized user.")
        return

    team_members[team_name]['auth_users'].append(member_id)
    save_data(team_members)
    await update.message.reply_text(f"User {member_id} has been authorized.")

async def unauthorize_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("You are not authorized to perform this action.")
        return
    
    text = update.message.text.split()
    if len(text) != 2:
        await update.message.reply_text("Usage: /unauth <user_id>")
        return

    member_id = text[1]
    if 'auth_users' not in team_members[team_name] or member_id not in team_members[team_name]['auth_users']:
        await update.message.reply_text("The specified user is not an authorized user.")
        return

    team_members[team_name]['auth_users'].remove(member_id)
    save_data(team_members)
    await update.message.reply_text(f"Authorization revoked for user {member_id}.")
