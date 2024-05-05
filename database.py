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
        return data.get("team_membersX", {})
    else:
        return {
    'team1': {'leader_id': '6369933143', 'members': [], 'extra_name': '👁️⃤ Goated Club', 'points': '', 'message_count': 0},
    'team2': {'leader_id': '7196174452', 'members': [], 'extra_name': '☮ Archangels ☮', 'points': '', 'message_count': 0},
    'team3': {'leader_id': '6824897749', 'members': [], 'extra_name': '🦦 Otters club 🦦', 'points': '', 'message_count': 0},
    'team4': {'leader_id': '5821282564', 'members': [], 'extra_name':'💰 The Billionaires Club 💰', 'points': '', 'message_count': 0},
    'team5': {'leader_id': '5920451104', 'members': [], 'extra_name': '👑Imperial🦇', 'points': '', 'message_count': 0}
}
