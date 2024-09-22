import aiosqlite
import datetime


async def create_table():
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()

        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT,
                user_type VARCHAR(255),
                full_name VARCHAR(255),
                phone_number VARCHAR(255),
                company_name VARCHAR(255),
                company_photo TEXT
            )
        """)

        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id BIGINT,
                created_at TIMESTAMP,
                title VARCHAR(255),
                description TEXT
            )
        """)

        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT,
                announcement_id INT
            )
        """)

        await connection.commit()
        return None


async def get_user(user_id: int):
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()

        user = await (await cursor.execute(
            f"SELECT * FROM users WHERE user_id = {user_id}"
        )).fetchone()

        await connection.commit()
        return user


async def create_user(user_id: int, phone_number: str, full_name: str, company_name: str = None, company_photo: str = None, user_type: str = 'user'):
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()

        await cursor.execute(
            f"""
            INSERT INTO users (user_id, phone_number, full_name, user_type, company_name, company_photo)
            VALUES ({user_id}, '{phone_number}', '{full_name}', '{user_type}', '{company_name}', '{company_photo}')
            """
        )

        user = await (await cursor.execute(
            f"SELECT * FROM users WHERE user_id = {user_id}"
        )).fetchone()

        await connection.commit()
        return user


async def create_announcement(from_user_id: int, title: str, description: str):
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()
        dt = datetime.datetime.now()

        await cursor.execute(
            f"""
            INSERT INTO announcements (from_user_id, created_at, title, description)
            VALUES ({from_user_id}, '{dt}', '{title}', '{description}')
            """
        )

        announcement = await (await cursor.execute(
            f"""
            SELECT * FROM announcements
            WHERE from_user_id = {from_user_id}
            ORDER BY id DESC LIMIT 1
            """
        )).fetchone()

        await connection.commit()
        return announcement


async def get_users_list():
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()

        users = await (await cursor.execute(
            "SELECT * FROM users WHERE user_type = 'user'"
        )).fetchall()

        await connection.commit()
        return users


async def get_announcement(announcement_id: int):
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()

        announcement = await (await cursor.execute(
            f"SELECT * FROM announcements WHERE id = {announcement_id}"
        )).fetchone()

        await connection.commit()
        return announcement


async def get_answer(answer_id: int):
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()

        answer = await (await cursor.execute(
            f"SELECT * FROM answers WHERE id = {answer_id}"
        )).fetchone()

        await connection.commit()
        return answer


async def create_answer(user_id: int, announcement_id: int):
    async with aiosqlite.connect('main.db') as connection:
        cursor = await connection.cursor()

        await cursor.execute(
            f"INSERT INTO answers (user_id, announcement_id) VALUES ({user_id}, {announcement_id})"
        )

        answer = await (await cursor.execute(
            f"""
            SELECT * FROM answers
            WHERE user_id = {user_id} AND announcement_id = {announcement_id}
            ORDER BY id DESC LIMIT 1
            """
        )).fetchone()

        await connection.commit()
        return answer