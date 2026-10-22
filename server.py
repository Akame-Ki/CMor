
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import string

# Start the server with:
# uvicorn main:app --host 0.0.0.0 --port 8000

app = FastAPI()

# Store all active game sessions
games = {}


class TableData(BaseModel):
    table: list[list[str | None]]


class PlayerData(BaseModel):
    player_id: int

class MoveData(BaseModel):
    player_id: int
    table: list[list[str | None]]



@app.get("/")
async def root():
    # Return a simple message to check whether the server is running
    return {"message": "Hello World"}


# Create a new game session
@app.post("/game/start")
async def start_game(data: PlayerData):

    # Validate the requested player ID
    if data.player_id not in (1, 2):
        raise HTTPException(
            status_code=400,
            detail="Player ID must be 1 or 2"
        )

    # Generate a unique session ID
    session_id = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )

    # Initialize the game session
    games[session_id] = {
        "player1": data.player_id,
        "player2": None,
        "board": [[None for _ in range(3)] for _ in range(3)],
        "end_game": None
    }

    print(
        f"Game session {session_id} created. "
        f"Host is player {data.player_id}."
    )

    # Return the new session ID and the host's player ID
    return {
        "session_id": session_id,
        "player_id": data.player_id
    }


# Join an existing game session
@app.post("/game/{session_id}/join")
async def join_game(session_id: str):

    # Find the requested game session
    game = games.get(session_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Prevent a third player from joining
    if game["player2"] is not None:
        raise HTTPException(
            status_code=409,
            detail="Game is already full"
        )

    # Assign the player ID not used by the host
    host_player = game["player1"]
    joining_player = 2 if host_player == 1 else 1

    # Register the joining player
    game["player2"] = joining_player

    print(
        f"Player {joining_player} joined game session {session_id}"
    )

    # Return the session ID and the assigned player ID
    return {
        "message": "Game joined successfully",
        "session_id": session_id,
        "player_id": joining_player
    }


def check_winner(board):

    # Check rows for a winner
    for row in board:
        if row[0] is not None and row[0] == row[1] == row[2]:
            return row[0]

    # Check columns for a winner
    for col in range(3):
        if board[0][col] is not None and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]

    # Check diagonals for a winner
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]


    # No winner found
    return None
    


# Update the board for a specific game session
@app.post("/game/{session_id}/board")
async def update_board(session_id: str, data: TableData):

    # Find the requested game session
    game = games.get(session_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Validate the board dimensions
    if len(data.table) != 3 or any(
        len(row) != 3 for row in data.table
    ):
        raise HTTPException(
            status_code=400,
            detail="Board must be 3x3"
        )

    # Store the updated board
    game["board"] = data.table

    if winner := check_winner(data.table):
        game["end_game"] = winner
        print(f"Game session {session_id} has a winner: Player {winner}")
        return {
            "table": game["board"],
            "end_game": winner
        }
    elif not any(cell is None for row in data.table for cell in row) and not winner:
        game["end_game"] = "Draw"
        print(f"Game session {session_id} ended in a draw.")
        return {
            "table": game["board"],
            "end_game": "Draw"
        }

    return {
        "message": "Board updated",
        "table": game["board"],
    }


# Retrieve the board for a specific game session
@app.get("/game/{session_id}/board")
async def get_board(session_id: str):

    # Find the requested game session
    game = games.get(session_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Return the current board
    return {
        "session_id": session_id,
        "table": game["board"],
        "end_game": game["end_game"],
        "player1_stage": game["player1"],
        "player2_stage": game["player2"]
    }


