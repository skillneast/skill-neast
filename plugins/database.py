"from pymongo import MongoClient
import motor.motor_asyncio
from info import MONGODB_URI

client = MongoClient(MONGODB_URI)
db = client['videoplays']
collection = db['playscount']

def record_visit(user: int, count: int):
    existing_visit = collection.find_one({
        "user": user
    })   
    if not existing_visit:
        collection.insert_one({
            "user": user,
            "count": count,
            "withdraw": False
        })
    else:
        user_data = {
            "count": count
        }
        collection.update_one({"user": user}, {"$set": user_data})

def record_withdraw(user, withdraw):
    existing_visit = collection.find_one({
        "user": user
    })
    if existing_visit:
        user_data = {
            "withdraw": withdraw
        }
        collection.update_one({"user": user}, {"$set": user_data})

def get_count(user):
    existing_visit = collection.find_one({
        "user": user
    })
    if existing_visit:
        return existing_visit["count"]
    else: 
        return None

def get_withdraw(user):
    existing_visit = collection.find_one({
        "user": user
    })
    if existing_visit:
        try:
            return existing_visit["withdraw"]
        except:
            return False
    else: 
        return False


class Database2:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            b_name = None,
            c_link = None,
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)

checkdb = Database2(MONGODB_URI, "TechVJVideoPlayerBot")

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            b_name = None,
            c_link = None,
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_name(self, id, name):
        await self.col.update_one({'id': int(id)}, {'$set': {'b_name': name}})

    async def get_name(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('b_name')

    async def set_link(self, id, link):
        await self.col.update_one({'id': int(id)}, {'$set': {'c_link': link}})

    async def get_link(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('c_link')

db = Database(MONGODB_URI, "VJVideoPlayerBot")"
