
import tkinter as tk
from tkinter import messagebox
import threading
import time
import random


# ============================================================================
# GAME ENVIRONMENT
# ============================================================================

class DotsAndBoxesGame:
    """
    Fixed 6x6 grid (5x5 boxes)
    EDGE VALUES:
        0 = not drawn
        1 = drawn by Player 1 (YOU)
        2 = drawn by Player 2 (AI)
    """
    
    def __init__(self):
        # Fixed 6x6 grid
        self.rows = 6
        self.cols = 6
        
        # Edge matrices: 0=empty, 1=player1, 2=player2
        self.h_edges = [[0] * (self.cols - 1) for _ in range(self.rows)]
        self.v_edges = [[0] * self.cols for _ in range(self.rows - 1)]
        
        # Box ownership: 0=unclaimed, 1=player1, 2=player2
        self.boxes = [[0] * (self.cols - 1) for _ in range(self.rows - 1)]
        
        # Game state — randomly decide who goes first
        self.current_player = random.choice([1, 2])
        self.scores = [0, 0]  # [player1, player2]
    
    def get_available_moves(self):
        """Get all legal moves"""
        moves = []
        
        # Check horizontal edges
        for r in range(self.rows):
            for c in range(self.cols - 1):
                if self.h_edges[r][c] == 0:
                    moves.append(('h', r, c))
        
        # Check vertical edges
        for r in range(self.rows - 1):
            for c in range(self.cols):
                if self.v_edges[r][c] == 0:
                    moves.append(('v', r, c))
        
        return moves
    
    def is_valid_move(self, move):
        """Check if a move is legal"""
        edge_type, row, col = move
        
        if edge_type == 'h':
            if 0 <= row < self.rows and 0 <= col < self.cols - 1:
                return self.h_edges[row][col] == 0
        elif edge_type == 'v':
            if 0 <= row < self.rows - 1 and 0 <= col < self.cols:
                return self.v_edges[row][col] == 0
        
        return False
    
    def check_box_completion(self, row, col):
        """Check if a box is completed"""
        if row < 0 or row >= self.rows - 1 or col < 0 or col >= self.cols - 1:
            return False
        
        # Check all 4 edges of the box (any non-zero value means drawn)
        top    = self.h_edges[row][col]     != 0
        bottom = self.h_edges[row + 1][col] != 0
        left   = self.v_edges[row][col]     != 0
        right  = self.v_edges[row][col + 1] != 0
        
        return top and bottom and left and right
    
    def make_move(self, move):
        """Execute a move and return number of boxes completed"""
        edge_type, row, col = move
        
        if not self.is_valid_move(move):
            return 0
        
        # Draw the edge — store WHICH player drew it
        if edge_type == 'h':
            self.h_edges[row][col] = self.current_player
        else:
            self.v_edges[row][col] = self.current_player
        
        # Check which boxes might be completed
        boxes_completed = 0
        
        if edge_type == 'h':
            # Horizontal edge can complete box above or below
            if row > 0:
                if self.check_box_completion(row - 1, col) and self.boxes[row - 1][col] == 0:
                    self.boxes[row - 1][col] = self.current_player
                    boxes_completed += 1
            
            if row < self.rows - 1:
                if self.check_box_completion(row, col) and self.boxes[row][col] == 0:
                    self.boxes[row][col] = self.current_player
                    boxes_completed += 1
        
        else:  # vertical edge
            # Vertical edge can complete box to left or right
            if col > 0:
                if self.check_box_completion(row, col - 1) and self.boxes[row][col - 1] == 0:
                    self.boxes[row][col - 1] = self.current_player
                    boxes_completed += 1
            
            if col < self.cols - 1:
                if self.check_box_completion(row, col) and self.boxes[row][col] == 0:
                    self.boxes[row][col] = self.current_player
                    boxes_completed += 1
        
        # Update score
        self.scores[self.current_player - 1] += boxes_completed
        
        # Switch player only if no boxes were completed
        if boxes_completed == 0:
            self.current_player = 3 - self.current_player
        
        return boxes_completed
    
    def is_game_over(self):
        """Check if all edges are drawn"""
        for row in self.h_edges:
            if 0 in row:
                return False
        
        for row in self.v_edges:
            if 0 in row:
                return False
        
        return True
    
    def get_winner(self):
        """Return winner: 1, 2, or 0 (tie)"""
        if not self.is_game_over():
            return None
        
        if self.scores[0] > self.scores[1]:
            return 1
        elif self.scores[1] > self.scores[0]:
            return 2
        else:
            return 0
    
    def reset_game(self):
        # Reset the game to initial state
        # Reset edges
        self.h_edges = [[0] * (self.cols - 1) for _ in range(self.rows)]
        self.v_edges = [[0] * self.cols for _ in range(self.rows - 1)]

        # Reset boxes
        self.boxes = [[0] * (self.cols - 1) for _ in range(self.rows - 1)]

        # Reset game state
        self.current_player = random.choice([1, 2])
        self.scores = [0, 0]

    def copy(self):
        """Create a deep copy of the game"""
        new_game = DotsAndBoxesGame()
        new_game.h_edges = [row[:] for row in self.h_edges]
        new_game.v_edges = [row[:] for row in self.v_edges]
        new_game.boxes   = [row[:] for row in self.boxes]
        new_game.current_player = self.current_player
        new_game.scores  = self.scores[:]
        return new_game


# ============================================================================
# AI PLAYER
# ============================================================================

class AIPlayer:
    """
    AI player using minimax with alpha-beta pruning
    """
    
    def __init__(self, player_number=2):
        self.player_number   = player_number
        self.opponent_number = 3 - player_number
        self.max_depth       = 3  
        
        # Statistics
        self.nodes_explored = 0
        self.thinking_time  = 0
    
    def get_best_move(self, game):
        """Find the best move using minimax"""
        start_time = time.time()
        self.nodes_explored = 0
        
        available_moves = game.get_available_moves()
        
        if not available_moves:
            return None
        
        # Single move left
        if len(available_moves) == 1:
            self.thinking_time = time.time() - start_time
            return available_moves[0]
        
        best_move  = None
        best_score = float('-inf')
        
        for move in available_moves:
            game_copy       = game.copy()
            boxes_completed = game_copy.make_move(move)
            
            is_maximizing = (game_copy.current_player == self.player_number)
            
            score = self.minimax(
                game_copy,
                depth=self.max_depth - 1,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing=is_maximizing
            )
            
            # Add immediate box bonus
            score += boxes_completed * 100
            
            if score > best_score:
                best_score = score
                best_move  = move
        
        self.thinking_time = time.time() - start_time
        return best_move
    
    def minimax(self, game, depth, alpha, beta, maximizing):
        """Minimax algorithm with alpha-beta pruning"""
        self.nodes_explored += 1
        
        if game.is_game_over():
            return self.evaluate_terminal(game)
        
        if depth == 0:
            return self.evaluate_state(game)
        
        available_moves = game.get_available_moves()
        
        if maximizing:
            max_eval = float('-inf')
            
            for move in available_moves:
                game_copy       = game.copy()
                boxes_completed = game_copy.make_move(move)
                
                is_still_maximizing = (game_copy.current_player == self.player_number)
                
                eval_score  = self.minimax(game_copy, depth - 1, alpha, beta, is_still_maximizing)
                eval_score += boxes_completed * 50
                
                max_eval = max(max_eval, eval_score)
                alpha    = max(alpha, eval_score)
                
                if beta <= alpha:
                    break
            
            return max_eval
        
        else:  # Minimizing
            min_eval = float('inf')
            
            for move in available_moves:
                game_copy       = game.copy()
                boxes_completed = game_copy.make_move(move)
                
                is_still_minimizing = (game_copy.current_player == self.opponent_number)
                
                eval_score  = self.minimax(game_copy, depth - 1, alpha, beta, not is_still_minimizing)
                eval_score -= boxes_completed * 50
                
                min_eval = min(min_eval, eval_score)
                beta     = min(beta, eval_score)
                
                if beta <= alpha:
                    break
            
            return min_eval
    
    def evaluate_state(self, game):
        """Evaluate the current game state"""
        ai_score  = game.scores[self.player_number - 1]
        opp_score = game.scores[self.opponent_number - 1]
        return (ai_score - opp_score) * 100
    
    def evaluate_terminal(self, game):
        """Evaluate terminal state"""
        ai_score  = game.scores[self.player_number - 1]
        opp_score = game.scores[self.opponent_number - 1]
        
        if ai_score > opp_score:
            return 10000
        elif ai_score < opp_score:
            return -10000
        else:
            return 0


# ============================================================================
# GUI
# ============================================================================

class GameGUI:
    
    # Background & canvas colors
    COLOR_BG     = '#1a1a2e'
    COLOR_CANVAS = '#16213e'
    COLOR_DOT    = '#0f3460'
    COLOR_TEXT   = '#ecf0f1'
    COLOR_HOVER  = '#95a5a6'
    
    # ---- EDGE COLORS: one clear color per player ----
    COLOR_P1_EDGE = '#4a90e2'   # Blue  → YOU
    COLOR_P2_EDGE = '#e74c3c'   # Red   → AI
    
    # Box fill colors (slightly darker shade of each edge color)
    COLOR_P1_BOX = '#3498db'
    COLOR_P2_BOX = '#c0392b'
    
    DOT_RADIUS = 8
    CELL_SIZE  = 50
    EDGE_WIDTH = 6
    MARGIN     = 30
    
    def __init__(self, master, game, ai_player):
        self.master    = master
        self.game      = game
        self.ai_player = ai_player
        
        self.master.title("Dots and Boxes - 6x6 Grid AI vs Player")
        self.master.configure(bg=self.COLOR_BG)
        
        # Canvas size
        self.canvas_width  = (game.cols - 1) * self.CELL_SIZE + 2 * self.MARGIN
        self.canvas_height = (game.rows - 1) * self.CELL_SIZE + 2 * self.MARGIN
        
        # State
        self.hover_edge = None
        self.ai_thinking = False
        self.game_over   = False
        
        self.setup_ui()
        self.draw_board()
        
        # If AI goes first
        if self.ai_player and self.game.current_player == self.ai_player.player_number:
            self.master.after(500, self.ai_make_move)
    
    # ------------------------------------------------------------------ UI setup
    def setup_ui(self):
        """Create UI elements"""
        main_frame = tk.Frame(self.master, bg=self.COLOR_BG)
        main_frame.pack(padx=20, pady=20)
        
        # Title
        tk.Label(
            main_frame,
            text="DOTS AND BOXES",
            font=('Arial', 24, 'bold'),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(pady=(0, 4))
        
        tk.Label(
            main_frame,
            text="6x6 Grid  •  AI vs Player",
            font=('Arial', 11),
            bg=self.COLOR_BG,
            fg=self.COLOR_HOVER
        ).pack()
        
        # Show who goes first
        first = "You go first!" if self.game.current_player == 1 else "AI goes first!"
        tk.Label(
            main_frame,
            text=first,
            font=('Arial', 11, 'bold'),
            bg=self.COLOR_BG,
            fg=self.COLOR_P1_EDGE if self.game.current_player == 1 else self.COLOR_P2_EDGE
        ).pack(pady=(2, 0))
        
        # ---- Color legend ------------------------------------------------
        legend_frame = tk.Frame(main_frame, bg=self.COLOR_BG)
        legend_frame.pack(pady=(6, 0))
        
        tk.Label(
            legend_frame,
            text="■",
            font=('Arial', 14),
            bg=self.COLOR_BG,
            fg=self.COLOR_P1_EDGE   # blue square
        ).pack(side=tk.LEFT)
        
        tk.Label(
            legend_frame,
            text=" Your lines    ",
            font=('Arial', 11),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(side=tk.LEFT)
        
        tk.Label(
            legend_frame,
            text="■",
            font=('Arial', 14),
            bg=self.COLOR_BG,
            fg=self.COLOR_P2_EDGE   # red square
        ).pack(side=tk.LEFT)
        
        tk.Label(
            legend_frame,
            text=" AI lines",
            font=('Arial', 11),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(side=tk.LEFT)
        # ------------------------------------------------------------------
        
        # Scores
        scores_frame = tk.Frame(main_frame, bg=self.COLOR_BG)
        scores_frame.pack(pady=12)
        
        # Player 1 score card
        p1_frame = tk.Frame(scores_frame, bg=self.COLOR_P1_BOX, padx=20, pady=10)
        p1_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(p1_frame, text="YOU", font=('Arial', 12, 'bold'),
                 bg=self.COLOR_P1_BOX, fg='white').pack()
        
        self.p1_score_label = tk.Label(
            p1_frame, text="0", font=('Arial', 28, 'bold'),
            bg=self.COLOR_P1_BOX, fg='white'
        )
        self.p1_score_label.pack()
        
        # VS
        tk.Label(scores_frame, text="VS", font=('Arial', 16, 'bold'),
                 bg=self.COLOR_BG, fg=self.COLOR_TEXT).pack(side=tk.LEFT, padx=15)
        
        # Player 2 score card
        p2_frame = tk.Frame(scores_frame, bg=self.COLOR_P2_BOX, padx=20, pady=10)
        p2_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(p2_frame, text="AI", font=('Arial', 12, 'bold'),
                 bg=self.COLOR_P2_BOX, fg='white').pack()
        
        self.p2_score_label = tk.Label(
            p2_frame, text="0", font=('Arial', 28, 'bold'),
            bg=self.COLOR_P2_BOX, fg='white'
        )
        self.p2_score_label.pack()
        
        # Canvas
        self.canvas = tk.Canvas(
            main_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.COLOR_CANVAS,
            highlightthickness=2,
            highlightbackground=self.COLOR_TEXT
        )
        self.canvas.pack(pady=10)
        
        self.canvas.bind('<Motion>',   self.on_mouse_move)
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<Leave>',    self.on_mouse_leave)
        
        # Status label
        initial_status = "Your turn!" if self.game.current_player == 1 else "AI is thinking..."
        initial_color  = self.COLOR_P1_EDGE if self.game.current_player == 1 else self.COLOR_P2_EDGE
        self.status_label = tk.Label(
            main_frame,
            text=initial_status,
            font=('Arial', 14, 'bold'),
            bg=self.COLOR_BG,
            fg=initial_color
        )
        self.status_label.pack(pady=8)
        
        # AI stats
        stats_frame = tk.Frame(main_frame, bg=self.COLOR_CANVAS, padx=15, pady=8)
        stats_frame.pack(pady=4)
        
        tk.Label(stats_frame, text="AI Statistics", font=('Arial', 11, 'bold'),
                 bg=self.COLOR_CANVAS, fg=self.COLOR_TEXT).pack()
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Waiting for AI move...",
            font=('Arial', 9),
            bg=self.COLOR_CANVAS,
            fg=self.COLOR_HOVER
        )
        self.stats_label.pack()
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=self.COLOR_BG)
        btn_frame.pack(pady=8)
        
        tk.Button(
            btn_frame, text="New Game",
            font=('Arial', 11, 'bold'), bg=self.COLOR_P1_EDGE, fg='white',
            padx=20, pady=8, relief=tk.FLAT, command=self.new_game
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame, text="Quit",
            font=('Arial', 11, 'bold'), bg=self.COLOR_P2_EDGE, fg='white',
            padx=20, pady=8, relief=tk.FLAT, command=self.master.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    # ---------------------------------------------------------------- Drawing
    def draw_board(self):
        """Draw the full game board"""
        self.canvas.delete('all')
        self.draw_all_edges()
        self.draw_all_boxes()
        self.draw_dots()
        if self.hover_edge and not self.ai_thinking:
            self.draw_hover_effect()
    
    def draw_dots(self):
        """Draw all dots"""
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                x = self.MARGIN + c * self.CELL_SIZE
                y = self.MARGIN + r * self.CELL_SIZE
                self.canvas.create_oval(
                    x - self.DOT_RADIUS, y - self.DOT_RADIUS,
                    x + self.DOT_RADIUS, y + self.DOT_RADIUS,
                    fill=self.COLOR_DOT, outline=self.COLOR_TEXT, width=2
                )
    
    def draw_all_edges(self):
        """Draw all edges"""
        for r in range(self.game.rows):
            for c in range(self.game.cols - 1):
                self.draw_edge('h', r, c, self.game.h_edges[r][c])
        
        for r in range(self.game.rows - 1):
            for c in range(self.game.cols):
                self.draw_edge('v', r, c, self.game.v_edges[r][c])
    
    def draw_edge(self, edge_type, row, col, drawn_by):
        """
        Draw a single edge.
        drawn_by:  0 = not drawn (show faint line)
                   1 = drawn by Player 1  → blue
                   2 = drawn by Player 2  → red
        """
        if edge_type == 'h':
            x1 = self.MARGIN + col * self.CELL_SIZE
            y1 = self.MARGIN + row * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1
        else:
            x1 = self.MARGIN + col * self.CELL_SIZE
            y1 = self.MARGIN + row * self.CELL_SIZE
            x2 = x1
            y2 = y1 + self.CELL_SIZE
        
        if drawn_by == 1:
            color = self.COLOR_P1_EDGE   # Blue  → YOU drew this
            width = self.EDGE_WIDTH
        elif drawn_by == 2:
            color = self.COLOR_P2_EDGE   # Red   → AI drew this
            width = self.EDGE_WIDTH
        else:
            color = '#2a2a3e'            # Dark grey → not drawn yet
            width = 2
        
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill=color, width=width, capstyle=tk.ROUND
        )
    
    def draw_all_boxes(self):
        """Draw all completed boxes"""
        for r in range(self.game.rows - 1):
            for c in range(self.game.cols - 1):
                if self.game.boxes[r][c] != 0:
                    self.draw_box(r, c, self.game.boxes[r][c])
    
    def draw_box(self, row, col, player):
        """Draw a completed box"""
        x1 = self.MARGIN + col * self.CELL_SIZE + 10
        y1 = self.MARGIN + row * self.CELL_SIZE + 10
        x2 = x1 + self.CELL_SIZE - 20
        y2 = y1 + self.CELL_SIZE - 20
        
        color = self.COLOR_P1_BOX if player == 1 else self.COLOR_P2_BOX
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
        
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        text = "P1" if player == 1 else "AI"
        
        self.canvas.create_text(
            center_x, center_y,
            text=text, font=('Arial', 14, 'bold'), fill='white'
        )
    
    def draw_hover_effect(self):
        """Draw hover highlight on the edge the mouse is over"""
        if not self.hover_edge:
            return
        
        edge_type, row, col = self.hover_edge
        
        if edge_type == 'h':
            x1 = self.MARGIN + col * self.CELL_SIZE
            y1 = self.MARGIN + row * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1
        else:
            x1 = self.MARGIN + col * self.CELL_SIZE
            y1 = self.MARGIN + row * self.CELL_SIZE
            x2 = x1
            y2 = y1 + self.CELL_SIZE
        
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill=self.COLOR_HOVER, width=self.EDGE_WIDTH, capstyle=tk.ROUND
        )
    
    # --------------------------------------------------------- Mouse handling
    def get_edge_at_position(self, x, y):
        """Return the edge closest to the mouse position, or None"""
        rel_x = x - self.MARGIN
        rel_y = y - self.MARGIN
        
        if rel_x < 0 or rel_y < 0:
            return None
        
        # Horizontal edges
        for r in range(self.game.rows):
            for c in range(self.game.cols - 1):
                edge_x = c * self.CELL_SIZE
                edge_y = r * self.CELL_SIZE
                if (abs(rel_x - edge_x - self.CELL_SIZE / 2) < self.CELL_SIZE / 2 + 10 and
                        abs(rel_y - edge_y) < 15):
                    if self.game.h_edges[r][c] == 0:
                        return ('h', r, c)
        
        # Vertical edges
        for r in range(self.game.rows - 1):
            for c in range(self.game.cols):
                edge_x = c * self.CELL_SIZE
                edge_y = r * self.CELL_SIZE
                if (abs(rel_x - edge_x) < 15 and
                        abs(rel_y - edge_y - self.CELL_SIZE / 2) < self.CELL_SIZE / 2 + 10):
                    if self.game.v_edges[r][c] == 0:
                        return ('v', r, c)
        
        return None
    
    def on_mouse_move(self, event):
        if self.ai_thinking or self.game_over:
            return
        edge = self.get_edge_at_position(event.x, event.y)
        if edge != self.hover_edge:
            self.hover_edge = edge
            self.draw_board()
    
    def on_mouse_leave(self, event):
        if self.hover_edge:
            self.hover_edge = None
            self.draw_board()
    
    def on_click(self, event):
        if self.ai_thinking or self.game_over:
            return
        if self.game.current_player != 1:
            return
        edge = self.get_edge_at_position(event.x, event.y)
        if edge and self.game.is_valid_move(edge):
            self.make_player_move(edge)
    
    # --------------------------------------------------------- Game logic
    def make_player_move(self, move):
        boxes_completed = self.game.make_move(move)
        self.update_display()
        
        if self.game.is_game_over():
            self.handle_game_over()
            return
        
        if boxes_completed > 0:
            self.status_label.config(text="You get another turn!")
        elif self.ai_player:
            self.master.after(500, self.ai_make_move)
    
    def ai_make_move(self):
        if not self.ai_player or self.game_over:
            return
        
        self.ai_thinking = True
        self.status_label.config(text="AI is thinking...", fg=self.COLOR_P2_EDGE)
        self.canvas.config(cursor='watch')
        
        def ai_thread():
            move = self.ai_player.get_best_move(self.game)
            self.master.after(0, lambda: self.execute_ai_move(move))
        
        threading.Thread(target=ai_thread, daemon=True).start()
    
    def execute_ai_move(self, move):
        if not move:
            self.ai_thinking = False
            self.canvas.config(cursor='')
            if self.game.is_game_over():
                self.handle_game_over()
            return
        
        boxes_completed = self.game.make_move(move)
        self.ai_thinking = False
        self.canvas.config(cursor='')
        
        self.stats_label.config(
            text=f"Nodes: {self.ai_player.nodes_explored} | Time: {self.ai_player.thinking_time:.2f}s"
        )
        
        self.update_display()
        
        if self.game.is_game_over():
            self.handle_game_over()
            return
        
        if boxes_completed > 0:
            self.status_label.config(text="AI gets another turn!")
            self.master.after(800, self.ai_make_move)
        else:
            self.status_label.config(text="Your turn!", fg=self.COLOR_P1_EDGE)
    
    def update_display(self):
        self.p1_score_label.config(text=str(self.game.scores[0]))
        self.p2_score_label.config(text=str(self.game.scores[1]))
        self.draw_board()
    
    def handle_game_over(self):
        self.game_over = True
        winner = self.game.get_winner()
        
        if winner == 1:
            message = "YOU WIN!"
            color   = self.COLOR_P1_BOX
        elif winner == 2:
            message = "AI WINS!"
            color   = self.COLOR_P2_BOX
        else:
            message = "IT'S A TIE!"
            color   = self.COLOR_HOVER
        
        self.status_label.config(text=message, fg=color)
        self.master.after(500, lambda: messagebox.showinfo(
            "Game Over",
            f"{message}\n\nFinal Score:\nYou: {self.game.scores[0]}\nAI: {self.game.scores[1]}"
        ))
    
    #def new_game(self):
    #    self.master.destroy()

    def new_game(self):
        """Start a completely new game"""
        # Reset the game data
        self.game.reset_game()

        # Reset GUI state
        self.game_over = False
        self.ai_thinking = False
        self.hover_edge = None

        # Clear any pending AI moves
        try:
            self.master.after_cancel(self.ai_after_id)
        except:
            pass
        
        # Redraw the board
        self.update_display()

        # Reset status
        if self.game.current_player == 1:
            self.status_label.config(text="Your turn!", fg=self.COLOR_P1_EDGE)
        else:
            self.status_label.config(text="AI is thinking...", fg=self.COLOR_P2_EDGE)
            # Schedule AI move if AI goes first
            self.master.after(500, self.ai_make_move)

        # Reset stats
        self.stats_label.config(text="Waiting for AI move...")

        # Reset AI stats
        if self.ai_player:
            self.ai_player.nodes_explored = 0
            self.ai_player.thinking_time = 0


# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    
    while True:
        game = DotsAndBoxesGame()
        ai   = AIPlayer(player_number=2)
        
        print("\nStarting new game...")
        
        root = tk.Tk()
        gui  = GameGUI(root, game, ai)
        root.mainloop()
        
        print("\n" + "=" * 60)
        again = input("Play again? press 'r' to restart and Enter: ").strip().lower()
        if again != 'r':
            print("\nThanks for playing!")
            break


if __name__ == "__main__":
    main()
