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






