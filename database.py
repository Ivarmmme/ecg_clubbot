import dns.resolver
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
def save_data(team_members):
    collection.update_one({}, {"$set": {"team_membersX": team_members}}, upsert=True)

# Function to load team members data from MongoDB
def load_data():
    data = collection.find_one({})
    if data:
        teams_data = data.get("team_membersX", {})
        # Add the message_count field to each team if it doesn't exist
        for team_name, team_info in teams_data.items():
            team_info.setdefault('message_count', 0)  # Set default value of message_count to 0
        return teams_data
    else:
        return {
            'team1': {'leader_id': '6369933143', 'members': [], 'extra_name': '👁️⃤ Goated Club', 'message_count': 0},
            'team2': {'leader_id': '7196174452', 'members': [], 'extra_name': '☮ Archangels ☮', 'message_count': 0},
            'team3': {'leader_id': '6824897749', 'members': [], 'extra_name': '🦦 Otters club 🦦', 'message_count': 0},
            'team4': {'leader_id': '5920451104', 'members': [], 'extra_name':'👑Imperial🦇', 'message_count': 0}
        }

