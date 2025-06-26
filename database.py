from pymongo import MongoClient   #lets Python talk to MongoDB
from pymongo.server_api import ServerApi  #ensures python is connected to a MongoDB server version

uri = "mongodb+srv://shorryah:mongo123@cluster0.9cfchjz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client["user_db"]
collection = db["user_data"]  #collection where all the login register data will be stored
chat_collection = db["chat_data"] #collection where all the chat data will be stored