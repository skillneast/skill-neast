# Fully Asynchronous and Corrected database.py
# Using motor for all operations to prevent blocking

import motor.motor_asyncio
from info import MONGODB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_col = self.db.users
        self.plays_col = self.db.playscount # Consolidated collection

    # ---- User Management Methods ----
    
    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            b_name = None, # Business Name
            c_link = None, # Channel Link
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.users_col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.users_col.find_one({'id': int(id)})
        return bool(user)
    
    async def total_users_count(self):
        return await self.users_col.count_documents({})

    async def get_all_users(self):
        return self.users_col.find({})

    async def delete_user(self, user_id):
        await self.users_col.delete_many({'id': int(user_id)})

    async def set_name(self, id, name):
        await self.users_col.update_one({'id': int(id)}, {'$set': {'b_name': name}})

    async def get_name(self, id):
        user = await self.users_col.find_one({'id': int(id)})
        return user.get('b_name') if user else None

    async def set_link(self, id, link):
        await self.users_col.update_one({'id': int(id)}, {'$set': {'c_link': link}})

    async def get_link(self, id):
        user = await self.users_col.find_one({'id': int(id)})
        return user.get('c_link') if user else None

    # ---- Visit/Play Count Management Methods (NOW ASYNC) ----
    
    async def record_visit(self, user_id: int):
        """
        Atomically increments the visit count for a user.
        If user doesn't exist, it creates one.
        This is much faster and safer than find-then-update.
        """
        # Using $inc is the correct and atomic way to increment in MongoDB
        await self.plays_col.update_one(
            {'user': user_id},
            {
                '$inc': {'count': 1},
                '$setOnInsert': {'withdraw': False} # Set withdraw status only on creation
            },
            upsert=True # If user not found, create (insert) them
        )
    
    async def get_count(self, user_id: int):
        data = await self.plays_col.find_one({'user': user_id})
        return data.get('count') if data else 0

    async def reset_count(self, user_id: int):
        """ Resets a user's count to 0, typically after a successful withdrawal. """
        await self.plays_col.update_one(
            {'user': user_id},
            {'$set': {'count': 0}}
        )

    # ---- Withdrawal Status Management Methods (NOW ASYNC) ----

    async def set_withdraw_status(self, user_id: int, status: bool):
        await self.plays_col.update_one(
            {'user': user_id},
            {'$set': {'withdraw': status}},
            upsert=True # Create if doesn't exist
        )

    async def get_withdraw_status(self, user_id: int):
        data = await self.plays_col.find_one({'user': user_id})
        return data.get('withdraw', False) if data else False


# Create a single instance of the database to be used everywhere
# You can name the DB whatever you like in MongoDB Atlas
db = Database(MONGODB_URI, "VJStreamBotDB") 

# For backward compatibility if other files are using 'checkdb'
checkdb = db
