import numpy as np
import pygame
import random
import heapq
import time
import sys

# 30 до 41 Zobrist Hash
# 44 до 176 Имплементации за МинМакс
# 178 до 260 Имплементации за UCS
# 263 до 417 Функции за логика во играта
# 420 до 445 Функции за логика на таблата
# 447 до 458 Функции за пресметување на брзината на потег
# 461 до 534 Поставување и започнување на играта/симулацијата

# Податоци за игратра
BOARD_ROWS = 15
BOARD_COLS = 15
SQUARE_SIZE = 40
WIDTH = BOARD_COLS * SQUARE_SIZE
HEIGHT = BOARD_ROWS * SQUARE_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
PLAYER_1 = 1
PLAYER_2 = 2

board = np.zeros((BOARD_ROWS, BOARD_COLS), dtype=int)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gomoku AI")

# Zobrist Hashing Setup
HASH_TABLE = {}
ZOBRIST_TABLE = np.random.randint(1, 2 ** 64, size=(BOARD_ROWS, BOARD_COLS, 2), dtype=np.uint64)

def compute_hash():
    hash_value = np.uint64(0)
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] != 0:
                piece = board[row][col] - 1
                hash_value ^= ZOBRIST_TABLE[row, col, piece]
    return hash_value


# Еверистика
def score_move(row, col, player):
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2

    for dr, dc in directions:
        player_streak = 0
        opponent_streak = 0
        open_ends = 0

        streak = []
        for i in range(-4, 5):
            r, c = row + i * dr, col + i * dc
            if 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS:
                streak.append(board[r][c])

        for i in range(len(streak)):
            if streak[i] == player:
                player_streak += 1
                opponent_streak = 0
            elif streak[i] == opponent:
                opponent_streak += 1
                player_streak = 0
            else:
                open_ends += 1

            if player_streak == 4 and open_ends > 0:
                score += 100000
            if opponent_streak == 4 and open_ends > 0:
                score += 90000
            if player_streak == 3 and open_ends > 1:
                score += 10000
            if opponent_streak == 3 and open_ends > 1:
                score += 8000
            if player_streak == 2 and open_ends > 1:
                score += 500
            if opponent_streak == 2 and open_ends > 1:
                score += 400
            if player_streak == 3 and open_ends == 1:
                score += 12000
            if opponent_streak == 3 and open_ends == 1:
                score += 11000
            if player_streak == 2 and open_ends > 2:
                score += 2000
            if opponent_streak == 2 and open_ends > 2:
                score += 1500
            if player_streak == 1 and open_ends > 2:
                score += 1000
            if opponent_streak == 1 and open_ends > 2:
                score += 800
            if player_streak == 4 and open_ends == 0:
                score += 1000000
            if opponent_streak == 4 and open_ends == 0:
                score += 1000000
            if player_streak == 2 and open_ends == 1:
                score += 2000
            if opponent_streak == 2 and open_ends == 1:
                score += 1500

    return score

def get_candidate_moves(player, max_candidates=10):
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2
    candidates = set()
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] != 0:
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < BOARD_ROWS and 0 <= nc < BOARD_COLS and board[nr][nc] == 0:
                            candidates.add((nr, nc))
    scored_candidates = [(score_move(r, c, player) + score_move(r, c, opponent), (r, c)) for r, c in candidates]

    if type == 1:
        scored_candidates.sort(key=lambda x: x[0])
    else:
        scored_candidates.sort(reverse=True, key=lambda x: x[0])

    max = scored_candidates[0][0]
    tmp = [list(move) for score, move in scored_candidates[:max_candidates] if score == max]
    random.shuffle(tmp)
    return [tuple(move) for move in tmp]

def evaluate(player):
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2
    score = 0
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if board[row][col] == player:
                score += 10
            elif board[row][col] == opponent:
                score -= 10
    return score

def minimax(player, depth, alpha, beta, is_maximizing):
    opponent = PLAYER_1 if player == PLAYER_2 else PLAYER_2
    hash_value = compute_hash()
    if hash_value in HASH_TABLE:
        return HASH_TABLE[hash_value]

    if check_win(player):
        return float('inf')
    if check_win(opponent):
        return float('-inf')
    if is_board_full() or depth == 3:
        return evaluate(player)

    if is_maximizing:
        best_score = -float('inf')
        for row, col in get_candidate_moves(player):
            board[row][col] = player
            score = minimax(player, depth + 1, alpha, beta, False)
            board[row][col] = 0
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        HASH_TABLE[hash_value] = best_score
        return best_score
    else:
        worst_score = float('inf')
        for row, col in get_candidate_moves(player):
            board[row][col] = opponent
            score = minimax(player, depth + 1, alpha, beta, True)
            board[row][col] = 0
            worst_score = min(worst_score, score)
            beta = min(beta, worst_score)
            if beta <= alpha:
                break
        HASH_TABLE[hash_value] = worst_score
        return worst_score

# Функции за UCS
def ucs_move(player):
    valid_moves = get_valid_moves()
    priority_queue = []

    for move in valid_moves:
        cost = evaluate_board_state(move, player)
        heapq.heappush(priority_queue, (cost, move))

    priority_queue = sorted(priority_queue, key=lambda x: x[0])
    min = priority_queue[0][0]
    priority_queue = [[score, list(move)] for score, move in priority_queue[:10] if score == min]

    random.shuffle(priority_queue)

    return tuple(priority_queue[0][1])


def get_valid_moves():
    moves = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == 0:
                moves.append((i, j))
    return moves


def evaluate_board_state(move, player):
    x, y = move
    cost = 0

    if is_winning_move(move, player):
        return 0

    cost += threat_level(move, player)

    return cost

def threat_level(move, player): # Пресметува цени
    opponent = 3 - player

    x, y = move
    board[x][y] = player

    if check_win(player):
        board[x][y] = 0
        return 0

    board[x][y] = opponent
    if check_win(opponent):
        board[x][y] = 0
        return 1

    board[x][y] = player
    if count_sequence(move, player, 4):
        board[x][y] = 0
        return 2

    board[x][y] = opponent
    if count_sequence(move, opponent, 4):
        board[x][y] = 0
        return 3

    board[x][y] = player
    if count_sequence(move, player, 3):
        board[x][y] = 4

    board[x][y] = opponent
    if count_sequence(move, opponent, 3):
        board[x][y] = 5

    board[x][y] = player
    if count_sequence(move, player, 2):
        board[x][y] = 6

    board[x][y] = 0

    # Централизиран бонус
    center_x, center_y = BOARD_ROWS // 2, BOARD_COLS // 2
    distance = abs(x - center_x) + abs(y - center_y)
    central_bonus = distance * 0.5

    return random.randint(7, 10) + central_bonus

# Функции за логика во играта
def count_sequence(move, player, length):
    x, y = move
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    for dx, dy in directions:
        count = 1
        for dir in [-1, 1]:
            step = 1
            while True:
                nx, ny = x + step * dx * dir, y + step * dy * dir
                if 0 <= nx < len(board) and 0 <= ny < len(board[0]) and board[nx][ny] == player:
                    count += 1
                    step += 1
                else:
                    break
        if count >= length:
            return True

    return False


def check_win(player):
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            if col + 4 < BOARD_COLS and np.all(board[row, col:col + 5] == player):
                return True
            if row + 4 < BOARD_ROWS and np.all(board[row:row + 5, col] == player):
                return True
            if row + 4 < BOARD_ROWS and col + 4 < BOARD_COLS and all(
                    board[row + i, col + i] == player for i in range(5)):
                return True
            if row - 4 >= 0 and col + 4 < BOARD_COLS and all(board[row - i, col + i] == player for i in range(5)):
                return True
    return False

def is_winning_move(move, player):
    x, y = move
    board[x][y] = player
    win = check_win(player)
    board[x][y] = 0
    return win

def best_move(player, type):
    start_time = time.time()
    if all(board[row][col] == 0 for row in range(len(board)) for col in range(len(board[0]))):
        center = len(board) // 2
        board[center][center] = player
        move_time = time.time() - start_time
        move_times1.append(move_time)
        return True

    if type == 0:
        moves = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    moves.append((row, col))
        random.shuffle(moves)
        move = moves[0]
        board[move[0]][move[1]] = player
        move_time = time.time() - start_time
        move_times1.append(move_time)
        return True

    if type == 1:
        move = ucs_move(player)
        while board[move[0]][move[1]] != 0:
            move = ucs_move(player)
        board[move[0]][move[1]] = player
        move_time = time.time() - start_time
        move_times1.append(move_time)
        return True

    if type == 2:
        best_score = -float('inf')
        move = (-1, -1)
        for row, col in get_candidate_moves(player):
            board[row][col] = player
            if type == 2:
                score = minimax(player, 0, -float('inf'), float('inf'), False)
            else:
                score = score_move(row, col, player)
            board[row][col] = 0
            if score > best_score:
                best_score = score
                move = (row, col)
        if move != (-1, -1):
            board[move[0]][move[1]] = player
            move_time = time.time() - start_time
            move_times1.append(move_time)
            return True
        move_time = time.time() - start_time
        move_times1.append(move_time)
        return False

    else:
        return False

def best_move2(player, type):
    start_time2 = time.time()
    if all(board[row][col] == 0 for row in range(len(board)) for col in range(len(board[0]))):
        center = len(board) // 2
        board[center][center] = player
        move_time2 = time.time() - start_time2
        move_times2.append(move_time2)
        return True

    if type == 0:
        moves = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    moves.append((row, col))
        random.shuffle(moves)
        move = moves[0]
        board[move[0]][move[1]] = player
        move_time2 = time.time() - start_time2
        move_times2.append(move_time2)
        return True

    if type == 1:
        move = ucs_move(player)
        while board[move[0]][move[1]] != 0:
            move = ucs_move(player)
        board[move[0]][move[1]] = player
        move_time2 = time.time() - start_time2
        move_times2.append(move_time2)
        return True

    if type == 2:
        best_score = -float('inf')
        move = (-1, -1)
        for row, col in get_candidate_moves(player):
            board[row][col] = player
            if type == 2:
                score = minimax(player, 0, -float('inf'), float('inf'), False)
            else:
                score = score_move(row, col, player)
            board[row][col] = 0
            if score > best_score:
                best_score = score
                move = (row, col)
        if move != (-1, -1):
            board[move[0]][move[1]] = player
            move_time2 = time.time() - start_time2
            move_times2.append(move_time2)
            return True
        move_time2 = time.time() - start_time2
        move_times2.append(move_time2)
        return False

    else:
        return False

# Функции за таблата
def is_board_full():
    return np.all(board != 0)

def mark_square(row, col, player):
    board[row][col] = player

def reset_board():
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            board[row][col] = 0

def draw_board():
    screen.fill(WHITE)
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            pygame.draw.rect(screen, GRAY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)
            if board[row][col] == PLAYER_1:
                pygame.draw.circle(screen, BLACK,
                                   (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   SQUARE_SIZE // 3)
            elif board[row][col] == PLAYER_2:
                pygame.draw.circle(screen, (255, 0, 0),
                                   (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                   SQUARE_SIZE // 3)
    pygame.display.update()

# Пресметка за времето на процесирање
move_times1 = []
move_times2 = []
def average_move_time1():
    if move_times1:
        return sum(move_times1) / len(move_times1)
    return 0

def average_move_time2():
    if move_times2:
        return sum(move_times2) / len(move_times2)
    return 0


# main loop
running = True
# player_turn = True
turn = PLAYER_1

counter1 = 0
counter2 = 0

# За играње човек против компјутер: одкоментирајте ги линиите 464 и од 481 до 503
# И коментирајте ги 465 и од 505 до 538

# За симулирање компјутер против компјутер: одкоментирајте ги линиите 465 и од 505 до 538
# И коментирајте ги 464 и од 481 до 503
# Во best_move type 0 е рандом, type 1 е UCS, type 2 е МинМакс
while running:
    draw_board()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    #     if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
    #         x, y = event.pos
    #         row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
    #         if board[row][col] == 0:
    #             mark_square(row, col, PLAYER_1)
    #             player_turn = False
    #
    # if not player_turn:
    #     if best_move(PLAYER_2, 2):
    #         player_turn = True
    #     else:
    #         print("Human wins WOHOOO")
    #         print("Candidate moves:", get_candidate_moves())
    #
    #     if check_win(PLAYER_1):
    #         print("Player 1 wins!")
    #         running = False
    #     elif check_win(PLAYER_2):
    #         print("Player 2 wins!")
    #         running = False
    #     elif is_board_full():
    #         print("It's a draw!")
    #         running = False

    if turn == PLAYER_1:
        best_move(turn, 2)
        turn = PLAYER_2
    else:
        best_move2(turn, 2)
        turn = PLAYER_1

    if check_win(PLAYER_1):
        print(f"Player 1 wins! {counter2 + counter1}")
        counter1 = counter1 + 1
        if counter1 + counter2 >= 100:
            one1 = average_move_time1()
            two2 = average_move_time2()
            print(f'Player 1 wins: {counter1}')
            print(f'Player2 wins: {counter2}')
            print(f'player 1: {one1}')
            print(f'player 2: {two2}')
            running = False
        reset_board()
    elif check_win(PLAYER_2):
        print(f"Player 2 wins! {counter1 + counter2}")
        counter2 = counter2 + 1
        if counter1 + counter2 >= 100:
            one1 = average_move_time1()
            two2 = average_move_time2()
            print(f'Player 1 wins: {counter1}')
            print(f'Player2 wins: {counter2}')
            print(f'player 1: {one1}')
            print(f'player 2: {two2}')
            running = False
        reset_board()
    elif is_board_full():
        print("It's a draw!")
        reset_board()

pygame.quit()
sys.exit()