# main.py
from contextlib import asynccontextmanager
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set
from models.player import Player
from models.game import Board, Game, GameState
from services.database import Database
from services.game_service import GameService
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://7685-2401-4900-1c68-46f2-b0a9-ce30-5845-df0c.ngrok-free.app"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory storage for active connections
active_connections: Dict[str, Dict[str, WebSocket]] = {}  # grid_id -> {player_id -> ws}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect_db("mongodb://localhost:27017")
    # Create a unique index on the name field in the players collection
    await Database.get_collection("players").create_index("name", unique=True)
    yield
    await Database.close_db()

app.router.lifespan_context = lifespan

@app.post("/players", response_model=Player)
async def create_player(player: Player):
    return await Database.create_player(player)

@app.get("/players/online/count")
async def get_online_player_count():
    return {"count": len([ws for grid in active_connections.values() for ws in grid.values()])}

@app.websocket("/ws/{player_id}/{grid_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: str, grid_id: str):
    await websocket.accept()
    
    if grid_id not in active_connections:
        active_connections[grid_id] = {}
    active_connections[grid_id][player_id] = websocket
    
    try:
        player = await Database.get_player(player_id)
        player['is_online'] = True
        await Database.update_player(player)
        
        games = await Database.get_games(grid_id)
        game = next(filter(lambda g: len(g['players']) == 1, games), None)
        game_id = game["id"] if game else None
        if not game:
            # Create new game
            game = {
                "grid_id": grid_id,
                "players": [player_id],
                "boards": {},
                "state": GameState.WAITING,
                "current_turn": None,
                "winner": None,
                "score": None
            }
            created_game = await Database.create_game(game)
            game_id = created_game["id"]
        elif game['state'] == GameState.WAITING:
            # Join existing game
            game['players'].append(player_id)
            game['state'] = GameState.IN_PROGRESS
            
            # Initialize boards
            for p_id in game["players"]:
                is_berserk = await _get_player_mode(p_id)
                game['boards'][p_id] = {
                    "cells": GameService.create_ship_configuration(),
                    "missile_count": GameService.calculate_missile_count(is_berserk),
                    "is_berserk": is_berserk
                }
            
            game['current_turn'] = game['players'][0]
            await Database.update_game(game)
            
            # Notify players
            await broadcast_to_grid(grid_id, {
                "type": "game_started",
                "game": game
            })
        
        while True:
            data = await websocket.receive_json()
            await handle_game_message(grid_id, player_id, data, str(game_id))
            
    except WebSocketDisconnect:
        active_connections[grid_id].pop(player_id, None)
        if not active_connections[grid_id]:
            del active_connections[grid_id]
        
        player['is_online'] = False
        await Database.update_player(player)
        
async def find_game_with_one_player(games):
    for game in games:
        if len(game['players']) == 1:
            return game
    return None

async def handle_game_message(grid_id: str, player_id: str, data: dict, game_id: str):
    game = await Database.get_game(game_id)
    
    if data["type"] == "shot":
        if game['current_turn'] != player_id:
            return
        
        target_id = next(p for p in game['players'] if p != player_id)
        position = data["position"]
        
        hit, destroyed, ship_destroyed = GameService.process_shot(
            game['boards'][target_id], 
            position
        )
        
        game['boards'][player_id]['missile_count'] -= 1
        
        if not hit:
            game['current_turn'] = target_id
        
        if all(cell['destroyed'] for cell in game['boards'][target_id]['cells'].values()):
            game['state'] = GameState.FINISHED
            game['winner'] = player_id
            game['score'] = game['boards'][player_id]['missile_count']
            
            # Update player score
            player = await Database.get_player(player_id)
            player['score'] += game['score']
            await Database.update_player(player)
        
        await Database.update_game(game)
        
        await broadcast_to_grid(grid_id, {
            "type": "shot_result",
            "position": position,
            "hit": hit,
            "destroyed": destroyed,
            "ship_destroyed": ship_destroyed,
            "game": game
        })
    
    elif data["type"] == "new_game":
        if game["state"] == GameState.FINISHED:
            new_game = {
                "grid_id": grid_id,
                "players": [player_id],
                "boards": {},
                "state": GameState.WAITING
            }
            await Database.create_game(new_game)
            
            await broadcast_to_grid(grid_id, {
                "type": "new_game_created",
                "game": new_game
            })

async def broadcast_to_grid(grid_id: str, message: dict):
    if grid_id in active_connections:
        for websocket in active_connections[grid_id].values():
            await websocket.send_json(message)

async def _get_player_mode(player_id: str) -> bool:
    # Return True 70% of the time and False 30% of the time
    return random.random() < 0.7

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, ws="auto")