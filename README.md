# Chess Game with AI

A complete chess game implementation in Python using Pygame, featuring an AI opponent with multiprocessing support.

## Features

- **Complete Chess Rules**: All standard chess moves including castling, en passant, and pawn promotion
- **AI Opponent**: Sophisticated AI using minimax algorithm with alpha-beta pruning
- **Flexible Player Setup**: Choose between Human vs Human, Human vs AI, AI vs Human, or AI vs AI
- **Move Validation**: Real-time legal move checking and highlighting
- **Move Log**: Complete history of all moves made in the game
- **Smooth Animations**: Piece movement animations for better user experience


## Installation

1. **Clone the repository**:
   
   -git clone https://github.com/yourusername/chess-engine.git
   -cd chess-engine
   

2. **Install dependencies**:
   pip install -r requirements.txt
   

3. **Run the game**:
   -cd Chess
   -python ChessMain.py

## How to Play

### Menu System
- **White Player**: Choose between Human or AI
- **Black Player**: Choose between Human or AI
- **Start Game**: Begin playing with selected settings

### Game Controls
- **Mouse**: Click pieces to select, click destination to move
- **Z Key**: Undo last move
- **R Key**: Reset the game
-**Ctrl-c or X out of the window to exit the game**

### AI Features
- **Multiprocessing**: AI calculations run in separate processes for better performance
- **Depth Search**: Adjustable search depth for AI difficulty (DEPTH var in AIMoveFinder)
- **Position Evaluation**: AI considers material value and piece positioning


## Project Structure

```
ChessEngine/
├── Chess/
│   ├── ChessMain.py      # Main game loop and UI
│   ├── ChessEngine.py    # Core chess logic and game state
│   └── AiMoveFinder.py   # AI algorithms and move calculation
├── images/
│   ├── wp.png, bp.png    # Pawns
│   ├── wR.png, bR.png    # Rooks
│   ├── wN.png, bN.png    # Knights
│   ├── wB.png, bB.png    # Bishops
│   ├── wQ.png, bQ.png    # Queens
│   └── wK.png, bK.png    # Kings
├── requirements.txt
└── README.md
```
## Acknowledgments
- The original tutorial was created by Eddie Sharick over on Youtube and I adapted the code to improve the performance of the game
- Inspired by classic chess engines and modern chess applications

#Improvements
-More efficent move calculation
-Add 50 move draw and 3 move repeating rule
-Allow engine to look at more important moves first like checks, captures, attacks to improve alpha beta pruning


## License

This project is licensed under the MIT License 


 