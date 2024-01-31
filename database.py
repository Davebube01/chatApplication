from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from bson import ObjectId

from user import User

# To connect to my cloud database on mongoDB and create a database for my chat application
client = MongoClient('mongodb+srv://test:test@chatappdemo1.9zdc5na.mongodb.net/?retryWrites=true&w=majority')



# This is to connect to the database and then its collection on mongDB atlas
# print(client.list_database_names())
db = client.chatDB   # chatDB being the database name we will be using which was printed in the statement above
# print(db.list_collection_names())     # This prints the collections in the database chatDB
users_collection = db.users
rooms_collection = db.rooms
room_members_collection = db.room_members



# To create new profile
# We will define the "_id" feed as the unique key in the database
# I am using the the password hash to hash the user password for protection
def save_new_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({
        '_id': username,
        'email': email,
        'password': password_hash
    })

# Function to get username
def get_user(username):
    user_data = users_collection.find_one({'_id':username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None

# Function to save room
def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one(
        {'name': room_name, 'created_by': created_by, 'created_at': datetime.now()}).inserted_id
   
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id

# Function to update room
def update_room(room_id, room_name):
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
 

# Function to get room
def get_room(room_id):
    rooms_collection.find_one({'_id': ObjectId(room_id)})
    

# Function to add room member
def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    room_members_collection.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 
        'added_by': added_by, 'added_at': datetime.now(), 'is_room_admin': is_room_admin}
        )

# Function to add multiple room members
def add_room_members(room_id, room_name, usernames, added_by):
    room_members_collection.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 
        'added_by': added_by, 'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])
    

# Function to remove room members 
def remove_room_members(room_id, usernames):
    room_members_collection.delete_many(
        {'_id': {'$in': [{'room_id': room_id, 'username': username} for username in usernames]}})

# Function to get room members
def get_room_members(room_id):
    room_members_collection.find({'_id.room_id': ObjectId(room_id)})


# Function to get room for users i.e room for a particular user 
def get_rooms_for_users(username):
    room_members_collection.find({'_id.username': username})


# Function to check if user is a room member
def is_room_member(room_id, username):
    room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})
    

# Function to check if user is room admin
def is_room_admin(room_id, username):
    room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})



# To test
# save_new_user('dave', 'abc@gmail.com', 'password')
    