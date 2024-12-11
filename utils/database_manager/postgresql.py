from typing import Union
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def connection(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                host=config.DB_HOST,
                database=config.DB_NAME
            )
        except Exception as e:
            print(f"Ma'lumotlar bazasiga ulanishda xatolik: {e}")
            raise

    async def execute(self, command, *args, fetch: bool = False, fetchval: bool = False,
                      fetchrow: bool = False, execute: bool = False):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                try:
                    if fetch:
                        result = await connection.fetch(command, *args)
                    elif fetchval:
                        result = await connection.fetchval(command, *args)
                    elif fetchrow:
                        result = await connection.fetchrow(command, *args)
                    elif execute:
                        result = await connection.execute(command, *args)
                except Exception as e:
                    print(f"So'rovni bajarishda xatolik: {e}")
                    raise
            return result

    async def users_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Users (
                id SERIAL PRIMARY KEY,
                fullname VARCHAR(255) NULL,
                telegram_id BIGINT NOT NULL UNIQUE,
                language VARCHAR(255) DEFAULT 'uz',
                score INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """
        await self.execute(sql, execute=True)

    async def channels_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Channels (
            id SERIAL PRIMARY KEY,
            channel_name VARCHAR(255) NULL,
            channel_id BIGINT NOT NULL UNIQUE,
            channel_members_count INT NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def referrals_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Referrals (
            id SERIAL PRIMARY KEY,
            referrer_id BIGINT NOT NULL,
            referred_id BIGINT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY (referrer_id) REFERENCES Users (telegram_id),
            FOREIGN KEY (referred_id) REFERENCES Users (telegram_id)
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)])
        return sql, tuple(parameters.values())

    async def add_user(self, fullname, telegram_id, language: str = "uz"):
        sql = """
        INSERT INTO Users (fullname, telegram_id, language)
        VALUES ($1, $2, $3)
        ON CONFLICT (telegram_id) DO NOTHING
        RETURNING *;
        """
        return await self.execute(sql, fullname, telegram_id, language, fetchrow=True)

    async def add_channel(self, channel_name, channel_id, channel_members_count):
        sql = """
        INSERT INTO Channels (channel_name, channel_id, channel_members_count)
        VALUES ($1, $2, $3) RETURNING *;
        """
        return await self.execute(sql, channel_name, int(channel_id), int(channel_members_count), fetchrow=True)

    async def add_referral(self, referrer_id, referred_id):
        # Referrer mavjudligini tekshiramiz
        referrer = await self.select_user(referrer_id)
        if not referrer:
            print(f"Referrer {referrer_id} topilmadi.")
            return None  # Agar referrer topilmasa, referralni qo'shish mumkin emas

        sql = """
        INSERT INTO Referrals (referrer_id, referred_id)
        VALUES ($1, $2)
        ON CONFLICT (referred_id) DO NOTHING
        RETURNING *;
        """
        referral = await self.execute(sql, referrer_id, referred_id, fetchrow=True)
        if referral:
            await self.update_user_score(referrer_id, points=10)
        return referral

    async def update_user_score(self, telegram_id, points: int):
        sql = """
        UPDATE Users SET score = score + $1 WHERE telegram_id = $2;
        """
        await self.execute(sql, points, telegram_id, execute=True)

    async def delete_channel(self, channel_id):
        sql = """
        DELETE FROM Channels WHERE channel_id = $1;
        """
        return await self.execute(sql, int(channel_id), fetchrow=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users;"
        return await self.execute(sql, fetch=True)

    async def select_all_channels(self):
        sql = "SELECT * FROM Channels;"
        return await self.execute(sql, fetch=True)

    async def select_user(self, telegram_id):
        sql = "SELECT * FROM Users WHERE telegram_id = $1;"
        return await self.execute(sql, telegram_id, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users;"
        return await self.execute(sql, fetchval=True)

    async def update_user_language(self, language, telegram_id):
        sql = """
        UPDATE Users SET language = $1 WHERE telegram_id = $2;
        """
        return await self.execute(sql, language, telegram_id, execute=True)

    async def is_referred_by(self, referrer_id, referred_id):
        referrer_id = int(referrer_id)  # Telegram ID ni int ga aylantirish
        referred_id = int(referred_id)  # Telegram ID ni int ga aylantirish
        sql = """
        SELECT 1 FROM Referrals 
        WHERE referrer_id = $1 AND referred_id = $2;
        """
        result = await self.execute(sql, referrer_id, referred_id, fetchrow=True)
        return result is not None

    async def add_score(self, telegram_id, points: int):
        telegram_id = int(telegram_id)  # Telegram ID ni int ga aylantirish
        sql = """
        UPDATE Users SET score = score + $1 WHERE telegram_id = $2;
        """
        await self.execute(sql, points, telegram_id, execute=True)

    async def get_score(self, telegram_id):
        sql = "SELECT score FROM Users WHERE telegram_id = $1;"
        row = await self.execute(sql, telegram_id, fetchrow=True)
        return row['score'] if row else None  # Natija bo'lmasa, None qaytariladi

    async def friends_count(self, telegram_id):
        sql = """
        SELECT COUNT(*) 
        FROM Referrals 
        WHERE referrer_id = $1;
        """
        return await self.execute(sql, telegram_id, fetchval=True)

    async def mark_as_referred(self, referrer_id, referred_id):
        referrer_id = int(referrer_id)  # Telegram ID ni int ga aylantirish
        referred_id = int(referred_id)  # Telegram ID ni int ga aylantirish
        sql = """
        INSERT INTO Referrals (referrer_id, referred_id)
        VALUES ($1, $2)
        ON CONFLICT (referred_id) DO NOTHING;
        """
        await self.execute(sql, referrer_id, referred_id, execute=True)

    async def is_referred_by_anyone(self, referred_id):
        sql = "SELECT 1 FROM Referrals WHERE referred_id = $1;"
        result = await self.execute(sql, referred_id, fetchrow=True)
        return result is not None  # Foydalanuvchi referal bo'lgan bo'lsa, True qaytaradi

    async def get_user_start_time(self, telegram_id):
        sql = "SELECT created_at FROM Users WHERE telegram_id = $1;"
        row = await self.execute(sql, telegram_id, fetchrow=True)
        return row['created_at'] if row else None  # Foydalanuvchining start vaqti bo'lsa, uni qaytaradi

    async def top_users_by_score(self, limit: int = 10):
        sql = """
        SELECT 
            fullname, 
            telegram_id, 
            score
        FROM Users
        ORDER BY score DESC
        LIMIT $1;
        """
        return await self.execute(sql, limit, fetch=True)

