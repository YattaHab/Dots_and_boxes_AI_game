# 🎯 Dots and Boxes — AI vs Player

A Python-based implementation of the classic **Dots and Boxes** game featuring an AI opponent powered by the **Minimax algorithm with Alpha-Beta Pruning**.

---

## 📖 About the Game

Dots and Boxes is a strategy game played on a grid of dots. Players take turns drawing lines between adjacent dots. The player who completes the fourth side of a box claims it , earns a point — and gets another turn. The player with the most boxes at the end wins.

This implementation features:
- A fixed **6×6 grid** (5×5 boxes)
- A **graphical interface** built with Python's `tkinter`
- An **AI opponent** using Minimax with Alpha-Beta pruning
- **Random first-turn assignment** at the start of each game
- **Color-coded** lines and boxes per player

---

## 🤖 AI Overview

| Component | Description |
|-----------|-------------|
| **Algorithm** | Minimax with Alpha-Beta Pruning |
| **Search Depth** | 3 levels |
| **Initial State** | Empty 6×6 grid, zero scores |
| **Actions** | Draw any available horizontal or vertical edge |
| **Goal** | Claim more boxes than the human player |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13
- `tkinter` (included with standard Python installations)

### Run the Game

```bash
python dots_and_boxes_final.py
```

---

## 🕹️ How to Play

1. Run the script — the game window will open automatically.
2. A coin flip decides who goes first (you or the AI).
3. **Click** on any line segment between two dots to draw it.
4. Complete all four sides of a box to claim it and earn a point.
5. If you complete a box, you get **another turn**.
6. The game ends when all lines are drawn — the player with more boxes wins.
7. Click **New Game** to play again at any time.
8. Click **Quit** to end the game at any time.
---

## 👥 Team

| Name | Section |
|------|---------|
| Habiba Ayman  | 3 |
| Toka Mostafa | 3 |
| Aya Nassar | 3 |

---

## 🛠️ Built With

- **Python 3** — Core language
- **tkinter** — GUI framework
- **threading** — Non-blocking AI computation
- **Minimax + Alpha-Beta Pruning** — AI decision-making

---

## 📄 License

**This project was developed for AI-1 course taught by Prof. Sarah El-Metwally -  CIS-MU.**
