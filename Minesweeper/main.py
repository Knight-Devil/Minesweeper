import pygame
import random
from queue import Queue
import time


pygame.init()

WIDTH,HEIGHT = 500,600
BG_COLOR="white"
ROWS,COLS=15,15
MINES = 25
size = WIDTH / ROWS
NUM_FONT = pygame.font.SysFont('comicsans',20)
NUM_COLOURS = {1:"blue" , 2:"green" , 3:"red" , 4:"purple" , 5:"orange" , 6:"yellow" , 7:"pink" , 8:"black"}
RECT_COLOUR = (200,200,200)
CLICKED_RECT_COLOUR = (140,140,140)
FLAG_IMAGE = pygame.image.load('flag_image.png')
BOMB_IMAGE = pygame.image.load('bomb_image.png')
LOST_FONT= pygame.font.SysFont('comicsans',70)
TIME_FONT= pygame.font.SysFont('comicsans',50)

FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (int(size), int(size)))
BOMB_IMAGE = pygame.transform.scale(BOMB_IMAGE, (int(size), int(size)))

win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Minesweeper")


# this function will get postions of all the neighbours of the coordinate on which a mine will be placed...and then we'll increment the neighbours by 1
def get_neighbours(rows,cols,row,col):
    neighbours = []
    if row>0: neighbours.append((row-1,col))# UP
    if row<rows - 1:neighbours.append((row+1,col))# DOWN
    if col>0: neighbours.append((row,col-1))# LEFT
    if col<cols - 1:neighbours.append((row,col+1))# RIGHT

    if row >0 and col>0:neighbours.append((row-1,col-1))
    if row<rows - 1 and col<cols - 1:neighbours.append((row+1,col+1))
    if row<rows - 1 and col>0 :neighbours.append((row+1,col-1))
    if row>0 and col<cols - 1:neighbours.append((row-1,col+1))

    return neighbours

def create_mine_field(rows,cols,mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    
    while len(mine_positions) < mines:
        row = random.randrange(0,rows)
        col = random.randrange(0,cols)
        pos = row,col

        if pos in mine_positions:
            continue
        mine_positions.add(pos)
        #we are using -1 to indicate presence of a mine at that position...
        field[row][col] = -1

    for mine in mine_positions:
        neighbours = get_neighbours(rows,cols,*mine)
        for r,c in neighbours:
            if field[r][c]!=-1:
                field[r][c] += 1

    return field


def draw(win,field,display_field,current_time):
    win.fill(BG_COLOR)

    time_text = TIME_FONT.render(f"Time elapsed :{round(current_time)}",1,"black")
    win.blit(time_text,(10,HEIGHT - time_text.get_height()))
     
    for i,row in enumerate(field):
        y = size*i
        for j,value in enumerate(row):
            x = size*j  

            is_covered = display_field[i][j]==0
            is_flag = display_field[i][j]==-2
            is_bomb = value==-1
            
            
                

            if is_flag:
                win.blit(FLAG_IMAGE, (x, y))
                pygame.draw.rect(win,"black",(x,y,size,size),2)
                continue

            if is_covered:
                pygame.draw.rect(win,RECT_COLOUR,(x,y,size,size))
                pygame.draw.rect(win,"black",(x,y,size,size),2)
                continue

            else:
                pygame.draw.rect(win,CLICKED_RECT_COLOUR,(x,y,size,size))
                pygame.draw.rect(win,"black",(x,y,size,size),2)
                if is_bomb:
                    win.blit(BOMB_IMAGE, (x, y))

            if value>0:
                num = NUM_FONT.render(str(value),1,NUM_COLOURS[value])
                win.blit(num,(x + (size/2 - num.get_width()/2),y + (size/2 - num.get_height()/2)))

    pygame.display.update()

def get_grid_pos(mouse_pos):
    mx,my=mouse_pos
    row = int(my // size)
    col = int(mx // size)

    return row,col

def uncover_from_position(row,col,display_field,field):
    q = Queue()
    q.put((row,col))
    visited = set()

    while not q.empty():
        current = q.get()

        neighbours = get_neighbours(ROWS,COLS,*current)
        for r,c in neighbours:
            if (r,c) in visited:
                continue
            value = field[r][c]

            # Skip if the neighbor has a mine
            if value == -1:
                continue
            if value == 0 and display_field[r][c]!=-2:
                q.put((r,c))

            if display_field[r][c]!=-2:
                display_field[r][c] = 1
            visited.add((r,c))

def draw_lost(win,text):
    text = LOST_FONT.render(text,1,"red")
    win.blit(text,(WIDTH/2 - text.get_width()/2 , HEIGHT/2 - text.get_width()/2))
    pygame.display.update()

def draw_won(win,text):
    text = LOST_FONT.render(text,1,"green")
    win.blit(text,(WIDTH/2 - text.get_width()/2 , HEIGHT/2 - text.get_width()/2))
    pygame.display.update()

def check_win(display_field, field):
    for i in range(ROWS):
        for j in range(COLS):
            if field[i][j] != -1 and display_field[i][j] == 0:
                return False
    return True


def main():
    run = True
    field = create_mine_field(ROWS,COLS,MINES)
    display_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    flags = MINES
    clicks = 0
    lost = False
    won = False

    start_time=0

    while run:
        if start_time > 0:
            current_time=time.time()-start_time
        else:
            current_time = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                row,col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue
                if event.button == 1 and display_field[row][col]!=-2:
                    display_field[row][col] = 1  

                    if field[row][col]==-1:

                        lost = True

                    if clicks == 0:
                        start_time = time.time()   

                    if clicks == 0 or field[row][col]==0:
                        uncover_from_position(row,col,display_field,field)
                    clicks+=1
                elif event.button == 3:
                    if display_field[row][col]==-2:
                        display_field[row][col] = 0
                        flags+=1
                    else:
                        flags-=1
                        # used -2 for indicating position of flag...
                        display_field[row][col] = -2
                    
                if check_win(display_field, field):
                    won = True
            if lost:
                draw(win,field,display_field,current_time)
                draw_lost(win,"YOU LOSE")
                pygame.time.delay(5000)

                #the code below restarts the game by reseting the manipulated variables to base values...
                field = create_mine_field(ROWS,COLS,MINES)
                display_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                flags = MINES
                clicks = 0
                lost = False
                start_time=0
            if won:
                draw_won(win, "YOU WIN")
                pygame.time.delay(5000)

                # Restart the game by resetting the variables to base values
                field = create_mine_field(ROWS, COLS, MINES)
                display_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                flags = MINES
                clicks = 0
                lost = False
                won = False
                start_time=0

        draw(win,field,display_field,current_time)
    pygame.quit()

if __name__=="__main__":
    main()






"""

 ===================== EXPLANATION OF THE CODE ABOVE =================== READ BEFORE INTERVIEWS ====================
    
Certainly! Here is a detailed explanation of the Minesweeper code you provided:

### Libraries and Initialization

```python
import pygame
import random
from queue import Queue
import time

pygame.init()
```
- **pygame**: Used for creating the graphical interface and handling events.
- **random**: Used to place mines randomly.
- **Queue**: Used for breadth-first search when uncovering cells.
- **time**: Used to track elapsed time.
- **pygame.init()**: Initializes all imported Pygame modules.

### Constants and Variables

```python
WIDTH, HEIGHT = 500, 600
BG_COLOR = "white"
ROWS, COLS = 15, 15
MINES = 25
size = WIDTH / ROWS
NUM_FONT = pygame.font.SysFont('comicsans', 20)
NUM_COLOURS = {1: "blue", 2: "green", 3: "red", 4: "purple", 5: "orange", 6: "yellow", 7: "pink", 8: "black"}
RECT_COLOUR = (200, 200, 200)
CLICKED_RECT_COLOUR = (140, 140, 140)
FLAG_IMAGE = pygame.image.load('flag_image.png')
BOMB_IMAGE = pygame.image.load('bomb_image.png')
LOST_FONT = pygame.font.SysFont('comicsans', 70)
TIME_FONT = pygame.font.SysFont('comicsans', 50)

FLAG_IMAGE = pygame.transform.scale(FLAG_IMAGE, (int(size), int(size)))
BOMB_IMAGE = pygame.transform.scale(BOMB_IMAGE, (int(size), int(size)))

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")
```
- **WIDTH, HEIGHT**: Dimensions of the game window.
- **BG_COLOR**: Background color of the window.
- **ROWS, COLS**: Number of rows and columns in the minefield.
- **MINES**: Number of mines in the minefield.
- **size**: Size of each cell in the grid.
- **NUM_FONT, LOST_FONT, TIME_FONT**: Fonts used for displaying numbers, lost message, and time.
- **NUM_COLOURS**: Colors for displaying numbers indicating nearby mines.
- **RECT_COLOUR, CLICKED_RECT_COLOUR**: Colors for covered and clicked cells.
- **FLAG_IMAGE, BOMB_IMAGE**: Images for flags and bombs, resized to fit the cells.
- **win**: The Pygame window where everything is drawn.
- **pygame.display.set_caption**: Sets the title of the game window.

### Helper Functions

#### Get Neighbours

```python
def get_neighbours(rows, cols, row, col):
    neighbours = []
    if row > 0: neighbours.append((row - 1, col))  # UP
    if row < rows - 1: neighbours.append((row + 1, col))  # DOWN
    if col > 0: neighbours.append((row, col - 1))  # LEFT
    if col < cols - 1: neighbours.append((row, col + 1))  # RIGHT

    if row > 0 and col > 0: neighbours.append((row - 1, col - 1))  # UP-LEFT
    if row < rows - 1 and col < cols - 1: neighbours.append((row + 1, col + 1))  # DOWN-RIGHT
    if row < rows - 1 and col > 0: neighbours.append((row + 1, col - 1))  # DOWN-LEFT
    if row > 0 and col < cols - 1: neighbours.append((row - 1, col + 1))  # UP-RIGHT

    return neighbours
```
- **get_neighbours**: Returns a list of neighboring cells for a given cell. It checks the boundaries to ensure neighbors are within the grid.

#### Create Mine Field

```python
def create_mine_field(rows, cols, mines):
    field = [[0 for _ in range(cols)] for _ in range(rows)]
    mine_positions = set()

    while len(mine_positions) < mines:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        if pos in mine_positions:
            continue
        mine_positions.add(pos)
        field[row][col] = -1  # Indicates presence of a mine

    for mine in mine_positions:
        neighbours = get_neighbours(rows, cols, *mine)
        for r, c in neighbours:
            if field[r][c] != -1:
                field[r][c] += 1

    return field
```
- **create_mine_field**: Initializes the minefield with a specified number of mines. Mines are placed randomly, and numbers indicating adjacent mines are calculated.

### Drawing Functions

#### Draw the Game

```python
def draw(win, field, display_field, current_time):
    win.fill(BG_COLOR)

    time_text = TIME_FONT.render(f"Time elapsed :{round(current_time)}", 1, "black")
    win.blit(time_text, (10, HEIGHT - time_text.get_height()))

    for i, row in enumerate(field):
        y = size * i
        for j, value in enumerate(row):
            x = size * j

            is_covered = display_field[i][j] == 0
            is_flag = display_field[i][j] == -2
            is_bomb = value == -1

            if is_flag:
                win.blit(FLAG_IMAGE, (x, y))
                pygame.draw.rect(win, "black", (x, y, size, size), 2)
                continue

            if is_covered:
                pygame.draw.rect(win, RECT_COLOUR, (x, y, size, size))
                pygame.draw.rect(win, "black", (x, y, size, size), 2)
                continue

            else:
                pygame.draw.rect(win, CLICKED_RECT_COLOUR, (x, y, size, size))
                pygame.draw.rect(win, "black", (x, y, size, size), 2)
                if is_bomb:
                    win.blit(BOMB_IMAGE, (x, y))

            if value > 0:
                num = NUM_FONT.render(str(value), 1, NUM_COLOURS[value])
                win.blit(num, (x + (size / 2 - num.get_width() / 2), y + (size / 2 - num.get_height() / 2)))

    pygame.display.update()
```
- **draw**: Draws the entire game state on the window, including the grid, numbers, flags, and bombs. It also displays the elapsed time.

#### Get Grid Position

```python
def get_grid_pos(mouse_pos):
    mx, my = mouse_pos
    row = int(my // size)
    col = int(mx // size)

    return row, col
```
- **get_grid_pos**: Converts mouse click coordinates to grid coordinates.

#### Uncover from Position

```python
def uncover_from_position(row, col, display_field, field):
    q = Queue()
    q.put((row, col))
    visited = set()

    while not q.empty():
        current = q.get()

        neighbours = get_neighbours(ROWS, COLS, *current)
        for r, c in neighbours:
            if (r, c) in visited:
                continue
            value = field[r][c]

            if value == 0 and display_field[r][c] != -2:
                q.put((r, c))

            if display_field[r][c] != -2:
                display_field[r][c] = 1
            visited.add((r, c))
```
- **uncover_from_position**: Uses a breadth-first search (BFS) to uncover cells starting from the clicked position. If an uncovered cell is empty (value 0), it continues uncovering adjacent cells.

#### Draw Lose/Win Message

```python
def draw_lost(win, text):
    text = LOST_FONT.render(text, 1, "red")
    win.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_width() / 2))
    pygame.display.update()

def draw_won(win, text):
    text = LOST_FONT.render(text, 1, "green")
    win.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_width() / 2))
    pygame.display.update()
```
- **draw_lost**: Displays a "YOU LOSE" message when the player hits a mine.
- **draw_won**: Displays a "YOU WIN" message when the player wins.

#### Check Win Condition

```python
def check_win(display_field, field):
    for i in range(ROWS):
        for j in range(COLS):
            if field[i][j] != -1 and display_field[i][j] == 0:
                return False
    return True
```
- **check_win**: Checks if all non-mine cells are uncovered. If so, the player wins.

### Main Game Loop

```python
def main():
    run = True
    field = create_mine_field(ROWS, COLS, MINES)
    display_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    flags = MINES
    clicks = 0
    lost = False
    won = False

    start_time = 0

    while run:
        if start_time > 0:
            current_time = time.time()

 - start_time
        else:
            current_time = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_grid_pos(pygame.mouse.get_pos())
                if row >= ROWS or col >= COLS:
                    continue
                if event.button == 1 and display_field[row][col] != -2:
                    display_field[row][col] = 1

                    if field[row][col] == -1:
                        lost = True

                    if clicks == 0:
                        start_time = time.time()

                    if clicks == 0 or field[row][col] == 0:
                        uncover_from_position(row, col, display_field, field)
                    clicks += 1
                elif event.button == 3:
                    if display_field[row][col] == -2:
                        display_field[row][col] = 0
                        flags += 1
                    else:
                        flags -= 1
                        display_field[row][col] = -2

                if check_win(display_field, field):
                    won = True
            if lost:
                draw(win, field, display_field, current_time)
                draw_lost(win, "YOU LOSE")
                pygame.time.delay(5000)

                field = create_mine_field(ROWS, COLS, MINES)
                display_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                flags = MINES
                clicks = 0
                lost = False
                start_time = 0
            if won:
                draw_won(win, "YOU WIN")
                pygame.time.delay(5000)

                field = create_mine_field(ROWS, COLS, MINES)
                display_field = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                flags = MINES
                clicks = 0
                lost = False
                won = False
                start_time = 0

        draw(win, field, display_field, current_time)
    pygame.quit()

if __name__ == "__main__":
    main()
```
- **main**: Contains the main game loop, handling events such as mouse clicks and updating the game state. It checks for win/lose conditions and redraws the game state continuously.

### Explanation Summary

1. **Initialization**: Libraries and Pygame are initialized. Constants for the game are defined.
2. **Minefield Creation**: A grid is created with randomly placed mines and numbers indicating nearby mines.
3. **Drawing Functions**: Functions to draw the game state, uncover cells, and display win/lose messages.
4. **Game Loop**: Handles user input, updates the game state, checks for win/lose conditions, and redraws the game.

This explanation should help you recall the structure and functionality of the code for interviews and your CV."""