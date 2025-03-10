# battleship_api_curls.sh

# 1. Create a new player
curl -X 'POST' \
  'http://localhost:8000/players' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Player1"
  }'

# Expected Response:
# {
#   "_id": "65aa12345678901234567890",
#   "name": "Player1",
#   "score": 0,
#   "is_online": false,
#   "created_at": "2024-01-19T10:00:00.000Z",
#   "updated_at": "2024-01-19T10:00:00.000Z"
# }

# 2. Get online player count
curl -X 'GET' \
  'http://localhost:8000/players/online/count' \
  -H 'accept: application/json'

# Expected Response:
# {
#   "count": 0
# }

# 3. WebSocket Connection (using wscat tool)
# First, install wscat if not installed:
# npm install -g wscat

# Connect to WebSocket (replace player_id and grid_id with actual values)
wscat -c "ws://localhost:8000/ws/65aa12345678901234567890/A1"

# 4. WebSocket Messages

# 4.1 Send shot coordinates
# In wscat:
{
  "type": "shot",
  "position": "B3"
}

# Expected Response:
# {
#   "type": "shot_result",
#   "position": "B3",
#   "hit": true,
#   "destroyed": false,
#   "ship_destroyed": false,
#   "game": {
#     "_id": "65aa12345678901234567890",
#     "grid_id": "A1",
#     "state": "in_progress",
#     "players": ["player1_id", "player2_id"],
#     "boards": {
#       "player1_id": {
#         "cells": {...},
#         "missile_count": 80,
#         "is_berserk": false
#       },
#       "player2_id": {
#         "cells": {...},
#         "missile_count": 81,
#         "is_berserk": false
#       }
#     },
#     "current_turn": "player2_id",
#     "winner": null,
#     "score": null,
#     "created_at": "2024-01-19T10:00:00.000Z",
#     "updated_at": "2024-01-19T10:00:00.000Z"
#   }
# }

# 4.2 Request new game
# In wscat:
{
  "type": "new_game"
}

# Expected Response:
# {
#   "type": "new_game_created",
#   "game": {
#     "_id": "65aa12345678901234567891",
#     "grid_id": "A1",
#     "state": "waiting",
#     "players": ["player1_id"],
#     "boards": {},
#     "current_turn": null,
#     "winner": null,
#     "score": null,
#     "created_at": "2024-01-19T10:01:00.000Z",
#     "updated_at": "2024-01-19T10:01:00.000Z"
#   }
# }

# 4.3 Set berserk mode (when waiting for opponent)
# In wscat:
{
  "type": "set_mode",
  "berserk": true
}

# Expected Response:
# {
#   "type": "mode_updated",
#   "berserk": true
# }

# Testing with multiple terminals:
# Terminal 1 (Player 1):
wscat -c "ws://localhost:8000/ws/player1_id/A1"

# Terminal 2 (Player 2):
wscat -c "ws://localhost:8000/ws/player2_id/A1"

# Health check (if implemented)
curl -X 'GET' \
  'http://localhost:8000/health' \
  -H 'accept: application/json'

# Expected Response:
# {
#   "status": "healthy",
#   "mongodb": "connected"
# }
