import aiosqlite


async def create_table():
    async with aiosqlite.connect('main.db') as connect:
        cursor = await connect.cursor()

        await cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                user_id BIGINT,
                                user_type VARCHAR(255),
                                full_name VARCHAR(255),
                                phone_number VARCHAR(255)
                            )""")
        await cursor.execute("""CREATE TABLE IF NOT EXISTS announcements (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                from_user_id BIGINT,
                                created_at TIMESTAMP,
                                title VARCHAR(255),
                                description TEXT,
                                status VARCHAR(255) DEFAULT 'noone_accepted')
                            )""")
        await cursor.execute("""CREATE TABLE IF NOT EXISTS accepted (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id BIGINT,
                                announcement_id INT,
                                status VARCHAR(255)
                            )""")
        await connect.commit()

        return None
    
async def get_user(user_id: int):
    async with aiosqlite.connect('main.db') as connect:
        cursor = await connect.cursor()

        user = await (await cursor.execute(f"""SELECT * FROM users WHERE user_id = {user_id}""")).fetchone()
        await connect.commit()

        return user

async def create_user(user_id: int, phone_number: str, full_name: str):
    async with aiosqlite.connect('main.db') as connect:
        cursor = await connect.cursor()

        await cursor.execute(f"""INSERT INTO users 
                         (user_id, phone_number, full_name, user_type) 
                         VALUES ({user_id}, '{phone_number}', '{full_name}', 'user')""")
        user = await (await cursor.execute(f"""SELECT * FROM users WHERE user_id = {user_id}""")).fetchone()
        await connect.commit()

        return user
    

async def create_announcement(from_user_id: int, title: str, description: str):
    async with aiosqlite.connect('main.db') as connect:
        cursor = await connect.cursor()

        await cursor.execute(f"""INSERT INTO announcements 
                         (from_user_id, created_at, title, description)
                         VALUES ({from_user_id}, DATETIME('now'), '{title}', '{description}')""")
        await connect.commit()

        return None


async def get_users_list():
    async with aiosqlite.connect('main.db') as connect:
        cursor = await connect.cursor()

        users = await (await cursor.execute(f"""SELECT * FROM users WHERE user_type = 'user'""")).fetchall()
        await connect.commit()

        return users