# services/database.py
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from models.player import Player
from models.game import Game

class Database:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls, mongodb_url: str):
        cls.client = AsyncIOMotorClient(mongodb_url)
        
    @classmethod
    async def close_db(cls):
        if cls.client:
            await cls.client.close()

    @classmethod
    async def get_player(cls, player_id: str) -> Optional[Player]:
        player = await cls.client.battleship.players.find_one({"id": ObjectId(player_id)})
        return player

    @classmethod
    async def create_player(cls, player: Player) -> Player:
        await cls.client.battleship.players.insert_one(player.dict())
        return player

    @classmethod
    async def update_player(cls, player: Player) -> bool:
        result = await cls.client.battleship.players.update_one(
            {"_id": player['id']},
            {"$set": player}
        )
        return result.modified_count > 0

    @classmethod
    async def get_games(cls, grid_id: str) -> List[Game]:
        cursor = cls.client.battleship.games.find({"grid_id": grid_id})
        games = []
        async for game in cursor:
            games.append(game)
        return games

    @classmethod
    async def get_game(cls, game_id: str) -> List[Game]:
        game = cls.client.battleship.games.find_one({"id": ObjectId(game_id)})
        return game
    
    @classmethod
    async def create_game(cls, game: Game) -> Game:
        await cls.client.battleship.games.insert_one(game.dict())
        return game

    @classmethod
    async def update_game(cls, game: Game) -> bool:
        result = await cls.client.battleship.games.update_one(
            {"grid_id": game.grid_id},
            {"$set": game.dict()}
        )
        return result.modified_count > 0
    
    @classmethod
    def get_collection(cls, collection_name: str):
        return cls.client.battleship[collection_name]
    
