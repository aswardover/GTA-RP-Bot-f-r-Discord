# -*- coding: utf-8 -*-
import aiosqlite
import asyncio
import os

DB_FILE = "bot_data.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        # Moderation
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sanktionen (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                betrag TEXT,
                grund TEXT,
                dauer INTEGER,
                end_time TEXT,
                guild_id TEXT,
                role_id TEXT,
                log_channel TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                grund TEXT,
                dauer INTEGER,
                end_time TEXT,
                guild_id TEXT,
                log_channel TEXT
            )
        ''')
        # Giveaways
        await db.execute('''
            CREATE TABLE IF NOT EXISTS giveaways (
                id INTEGER PRIMARY KEY,
                giveaway_id TEXT UNIQUE,
                item TEXT,
                end_time TEXT,
                channel_id TEXT,
                message_id TEXT,
                participants TEXT
            )
        ''')
        # Polls
        await db.execute('''
            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY,
                poll_id TEXT UNIQUE,
                question TEXT,
                options TEXT,
                anonymous INTEGER,
                votes TEXT,
                counts TEXT,
                channel_id TEXT,
                message_id TEXT
            )
        ''')
        # Reaction Roles
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reaction_roles (
                id INTEGER PRIMARY KEY,
                message_id TEXT UNIQUE,
                emoji_role_map TEXT
            )
        ''')
        await db.commit()

# Moderation
async def add_sanktion(user_id, betrag, grund, dauer, end_time, guild_id, role_id, log_channel):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('INSERT INTO sanktionen (user_id, betrag, grund, dauer, end_time, guild_id, role_id, log_channel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                         (user_id, betrag, grund, dauer, end_time, guild_id, role_id, log_channel))
        await db.commit()

async def get_sanktionen():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute('SELECT * FROM sanktionen')
        return await cursor.fetchall()

async def remove_sanktion(sanktion_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('DELETE FROM sanktionen WHERE id = ?', (sanktion_id,))
        await db.commit()

# Ähnlich für warns, giveaways, etc.
async def add_warn(user_id, grund, dauer, end_time, guild_id, log_channel):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('INSERT INTO warns (user_id, grund, dauer, end_time, guild_id, log_channel) VALUES (?, ?, ?, ?, ?, ?)',
                         (user_id, grund, dauer, end_time, guild_id, log_channel))
        await db.commit()

async def get_warns():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute('SELECT * FROM warns')
        return await cursor.fetchall()

async def remove_warn(warn_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('DELETE FROM warns WHERE id = ?', (warn_id,))
        await db.commit()

async def add_giveaway(giveaway_id, item, end_time, channel_id, message_id, participants):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('INSERT INTO giveaways (giveaway_id, item, end_time, channel_id, message_id, participants) VALUES (?, ?, ?, ?, ?, ?)',
                         (giveaway_id, item, end_time, channel_id, message_id, participants))
        await db.commit()

async def get_giveaways():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute('SELECT * FROM giveaways')
        return await cursor.fetchall()

async def remove_giveaway(giveaway_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('DELETE FROM giveaways WHERE giveaway_id = ?', (giveaway_id,))
        await db.commit()

async def update_giveaway_participants(giveaway_id, participants):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('UPDATE giveaways SET participants = ? WHERE giveaway_id = ?', (participants, giveaway_id))
        await db.commit()

async def add_poll(poll_id, question, options, anonymous, votes, counts, channel_id, message_id):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('INSERT INTO polls (poll_id, question, options, anonymous, votes, counts, channel_id, message_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                         (poll_id, question, options, anonymous, votes, counts, channel_id, message_id))
        await db.commit()

async def get_polls():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute('SELECT * FROM polls')
        return await cursor.fetchall()

async def update_poll_votes(poll_id, votes, counts):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('UPDATE polls SET votes = ?, counts = ? WHERE poll_id = ?', (votes, counts, poll_id))
        await db.commit()

async def add_reaction_role(message_id, emoji_role_map):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute('INSERT INTO reaction_roles (message_id, emoji_role_map) VALUES (?, ?)',
                         (message_id, emoji_role_map))
        await db.commit()

async def get_reaction_roles():
    async with aiosqlite.connect(DB_FILE) as db:
        cursor = await db.execute('SELECT * FROM reaction_roles')
        return await cursor.fetchall()

# Cache für Settings
settings_cache = {}
discord_data_cache = {}

async def get_cached_settings():
    if not settings_cache:
        # Load from file
        pass  # Implement later
    return settings_cache

# Init is triggered explicitly from bot startup.