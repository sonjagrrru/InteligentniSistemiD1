import pygame
import os
import config
from array import *
from queue import Queue


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]
        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path


class Aki(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = []
        row = self.row
        col = self.col

        sirina = len(game_map[0])
        visina = len(game_map)

        #da li je cvor posecen ili ne
        visited = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append(False)
            visited.append(tmplist)

        #da znamo kuda da idemo
        prethodni=[]
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append([-1,-1])
            prethodni.append(tmplist)

        #za dfs se koristi stek
        stack = [[row, col]]

        while len(stack) > 0:

            trenutno = stack.pop()
            row = trenutno[0]
            col = trenutno[1]

            if row == goal[0] and col == goal[1]:
                break

            #cvor je posecen kada ga skinemo sa steka
            visited[row][col] = True

            matrica = [[0,0,0],
                       [0,0,0],
                       [0,0,0],
                       [0,0,0]]

            #popunjavanje matrice po stranama sveta
            if row > 0 and not visited[row - 1][col]:
                cena = game_map[row - 1][col].cost()
                matrica[3][0] = row -1
                matrica[3][1] = col
                matrica[3][2] = cena
            else:
                matrica[3][0] = -1
            if col <= (sirina-2) and not visited[row][col+1]:
                cena = game_map[row][col+1].cost()
                matrica[2][0] = row
                matrica[2][1] = col + 1
                matrica[2][2] = cena
            else:
                matrica[2][0] = -1
            if row <= (visina-2) and not visited[row+1][col]:
                cena = game_map[row + 1][col].cost()
                matrica[1][0] = row + 1
                matrica[1][1] = col
                matrica[1][2] = cena
            else:
                matrica[1][0] = -1
            if col > 0 and not visited[row][col-1]:
                cena = game_map[row][col - 1].cost()
                matrica[0][0] = row
                matrica[0][1] = col - 1
                matrica[0][2] = cena
            else:
                matrica[0][0] = -1

            #sortiranje matrice po koloni cena
            matrica.sort(key= lambda x: -x[2])

            for lst in matrica:
                if lst[0]!=-1:
                    stack.append([lst[0],lst[1]])
                    prethodni[lst[0]][lst[1]]=[row,col]

        #prvo trazimo putanju od nazad
        tmp = [row,col]
        tmplis=[]
        while tmp!=[-1,-1]:
            tmplis.append(tmp)
            tmp=prethodni[tmp[0]][tmp[1]]
            if tmp==[self.row,self.col]:
                prethodni[self.row][self.col]=[-1,-1]

        #pa je u obrnutom redosledu dodajemo u putanju kojom idemo
        while tmplis:
            tmp=tmplis.pop()
            path.append(game_map[tmp[0]][tmp[1]])
        return path


class Jocke(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = []
        row = self.row
        col = self.col
        sirina = len(game_map[0])
        visina = len(game_map)

        #deo heuristicke funkcije (cena zbira svih komsija)
        cene_komsija = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append(0)
            cene_komsija.append(tmplist)

        for i in range(visina):
            for j in range(sirina):
                if i > 0:
                    cene_komsija[i][j] += game_map[i-1][j].cost()
                if j > 0:
                    cene_komsija[i][j] += game_map[i][j-1].cost()
                if j <= sirina-2:
                    cene_komsija[i][j] += game_map[i][j+1].cost()
                if i <= visina-2:
                    cene_komsija[i][j] += game_map[i+1][j].cost()

        #drugi deo heuristicke funkcije (broj komsija razlicit od nas kojim se deli cena)
        faktor = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                if (i==0 and j==0) or (i==visina-1 and j==0):
                    tmplist.append(1)
                elif(i==visina-1 and j==sirina-1) or (i==0 and j==sirina-1):
                    tmplist.append(1)
                elif i==0 or i==visina-1:
                    tmplist.append(2)
                elif j==0 or j==sirina-1:
                    tmplist.append(2)
                else:
                    tmplist.append(3)
            faktor.append(tmplist)

        #da li je cvor posecen ili ne
        visited = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append(False)
            visited.append(tmplist)

        #da znamo nasu putanju kojom smo isli
        prethodni = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append([-1, -1])
            prethodni.append(tmplist)

        queue = Queue() #za bfs se koristi red
        queue.put([row, col])
        while queue.not_empty:
            trenutno = queue.get()
            row = trenutno[0]
            col = trenutno[1]

            if row == goal[0] and col == goal[1]:
                break

            cenatr = game_map[row][col].cost()
            matrica = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

            #popunjavanje matrice po stranama sveta i racunanje heuristicke funkcije
            if row > 0 and not visited[row - 1][col]:
                cena = (cene_komsija[row - 1][col] - cenatr)/faktor[row-1][col]
                matrica[0][0]=row-1
                matrica[0][1]=col
                matrica[0][2]=cena
            else:
                matrica[0][0]=-1

            if col <= (sirina-2) and not visited[row][col+1]:
                cena = (cene_komsija[row][col+1]-cenatr)/faktor[row][col+1]
                matrica[1][0] = row
                matrica[1][1] = col +1
                matrica[1][2] = cena
            else:
                matrica[1][0] = -1

            if row <= (visina-2) and not visited[row+1][col]:
                cena = (cene_komsija[row+1][col] - cenatr)/faktor[row+1][col]
                matrica[2][0] = row + 1
                matrica[2][1] = col
                matrica[2][2] = cena
            else:
                matrica[2][0] = -1

            if col > 0 and not visited[row][col-1]:
                cena = (cene_komsija[row][col - 1] - cenatr)/faktor[row][col-1]
                matrica[3][0] = row
                matrica[3][1] = col - 1
                matrica[3][2] = cena
            else:
                matrica[3][0] = -1

            #sortiranje matrice po heuristickoj funkciji (manje je bolje)
            matrica.sort(key= lambda x:x[2])

            for lst in matrica:
                if lst[0] != -1:
                    queue.put([lst[0], lst[1]])
                    prethodni[lst[0]][lst[1]]=[row,col]
                    visited[lst[0]][lst[1]] = True #cvor je posecen kad se doda u red

        #pronalazak putanje od cilja do starta
        tmp = [row, col]
        tmplis = []
        while tmp != [-1, -1]:
            tmplis.append(tmp)
            tmp = prethodni[tmp[0]][tmp[1]]
            if tmp == [self.row, self.col]:
                prethodni[self.row][self.col] = [-1, -1]

        #ispis putanje od starta do cilja
        while tmplis:
            tmp = tmplis.pop()
            path.append(game_map[tmp[0]][tmp[1]])
        return path



class Bole(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = []
        row = self.row
        col = self.col

        sirina = len(game_map[0])
        visina = len(game_map)

        # da li je cvor posecen ili ne
        visited = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append(False)
            visited.append(tmplist)

        # da znamo kuda da idemo
        prethodni = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append([-1, -1])
            prethodni.append(tmplist)

        #heuristika kod A*
        vazdusno=[]
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append(abs(i-goal[0])+abs(j-goal[1]))
            vazdusno.append(tmplist)
        print(vazdusno)

        # za A* se koristi stek
        stack = [[row, col, vazdusno[row][col], vazdusno[row][col],[-1,-1]]]

        while stack:

            trenutno = stack.pop()
            row = trenutno[0]
            col = trenutno[1]
            visited[row][col]=True
            cost = trenutno[2]
            heuristika = trenutno[3]
            prethodni[row][col] = trenutno[4]

            for lstiter in stack:
                if lstiter[0] == row and lstiter[1] == col:
                    stack.remove(lstiter)


            if row == goal[0] and col == goal[1]:
                break

            matrica = [[0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0]]

            # popunjavanje matrice po stranama sveta
            if row > 0 and not visited[row - 1][col]:
                cena = game_map[row - 1][col].cost() + cost
                matrica[3][0] = row - 1
                matrica[3][1] = col
                matrica[3][2] = cena
                matrica[3][3] = vazdusno[row-1][col] + cena
                matrica[3][4] = [row, col]
            else:
                matrica[3][0] = -1
            if col <= (sirina - 2) and not visited[row][col + 1]:
                cena = game_map[row][col + 1].cost() + cost
                matrica[2][0] = row
                matrica[2][1] = col + 1
                matrica[2][2] = cena
                matrica[2][3] = vazdusno[row][col+1] + cena
                matrica[2][4] = [row, col]
            else:
                matrica[2][0] = -1
            if row <= (visina - 2) and not visited[row + 1][col]:
                cena = game_map[row + 1][col].cost() + cost
                matrica[1][0] = row + 1
                matrica[1][1] = col
                matrica[1][2] = cena
                matrica[1][3] = vazdusno[row+1][col] + cena
                matrica[1][4] = [row, col]
            else:
                matrica[1][0] = -1
            if col > 0 and not visited[row][col - 1]:
                cena = game_map[row][col - 1].cost() + cost
                matrica[0][0] = row
                matrica[0][1] = col - 1
                matrica[0][2] = cena
                matrica[0][3] = vazdusno[row][col-1] + cena
                matrica[0][4] = [row, col]
            else:
                matrica[0][0] = -1

            # sortiranje matrice po koloni cena
            matrica.sort(key=lambda x: -x[3])

            for lst in matrica:
                if lst[0] != -1:
                    stack.append(lst)
                    prethodni[lst[0]][lst[1]] = [row, col]

            stack.sort(key=lambda x: -x[3])

        # prvo trazimo putanju od nazad
        tmp = [row, col]
        tmplis = []
        while tmp != [-1, -1]:
            tmplis.append(tmp)
            tmp = prethodni[tmp[0]][tmp[1]]
            if tmp == [self.row, self.col]:
                prethodni[self.row][self.col] = [-1, -1]

        # pa je u obrnutom redosledu dodajemo u putanju kojom idemo
        while tmplis:
            tmp = tmplis.pop()
            path.append(game_map[tmp[0]][tmp[1]])
        return path

class Draza(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = []
        row = self.row
        col = self.col

        sirina = len(game_map[0])
        visina = len(game_map)

        # da li je cvor posecen ili ne
        visited = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append(False)
            visited.append(tmplist)

        # da znamo kuda da idemo
        prethodni = []
        for i in range(visina):
            tmplist = []
            for j in range(sirina):
                tmplist.append([-1, -1])
            prethodni.append(tmplist)

        # za branch and bound se koristi stek
        stack = [[row, col, 0, 0, 0]]

        while stack:

            trenutno = stack.pop()
            row = trenutno[0]
            col = trenutno[1]
            cost = trenutno[2]
            koraci = trenutno[3]
            prethodni[row][col]=trenutno[4]
            visited[row][col]=True

            for lstiter in stack:
                if lstiter[0]==row and lstiter[1]==col:
                    stack.remove(lstiter)

            if row == goal[0] and col == goal[1]:
                break

            matrica = [[0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0]]

            # popunjavanje matrice po stranama sveta
            if row > 0 and not visited[row - 1][col]:
                cena = game_map[row - 1][col].cost() + cost
                matrica[3][0] = row - 1
                matrica[3][1] = col
                matrica[3][2] = cena
                matrica[3][3] = koraci + 1
                matrica[3][4] = [row,col]
            else:
                matrica[3][0] = -1
            if col <= (sirina - 2) and not visited[row][col + 1]:
                cena = game_map[row][col + 1].cost() + cost
                matrica[2][0] = row
                matrica[2][1] = col + 1
                matrica[2][2] = cena
                matrica[2][3] = koraci + 1
                matrica[2][4] = [row,col]
            else:
                matrica[2][0] = -1
            if row <= (visina - 2) and not visited[row + 1][col]:
                cena = game_map[row + 1][col].cost() + cost
                matrica[1][0] = row + 1
                matrica[1][1] = col
                matrica[1][2] = cena
                matrica[1][3] = koraci + 1
                matrica[1][4] = [row,col]
            else:
                matrica[1][0] = -1
            if col > 0 and not visited[row][col - 1]:
                cena = game_map[row][col - 1].cost() + cost
                matrica[0][0] = row
                matrica[0][1] = col - 1
                matrica[0][2] = cena
                matrica[0][3] = koraci + 1
                matrica[0][4] = [row,col]
            else:
                matrica[0][0] = -1

            # sortiranje matrice po koloni cena
            matrica.sort(key=lambda x: -x[2])

            for lst in matrica:
                if lst[0] != -1:
                    stack.append(lst)
                    prethodni[lst[0]][lst[1]] = [row, col]
                    #visited[lst[0]][lst[1]] = True

            stack.sort(key=lambda x: -x[3])
            stack.sort(key=lambda x: -x[2])

        # prvo trazimo putanju od nazad
        tmp = [row, col]
        tmplis = []
        while tmp != [-1, -1]:
            tmplis.append(tmp)
            tmp = prethodni[tmp[0]][tmp[1]]
            if tmp == [self.row, self.col]:
                prethodni[self.row][self.col] = [-1, -1]

        # pa je u obrnutom redosledu dodajemo u putanju kojom idemo
        while tmplis:
            tmp = tmplis.pop()
            path.append(game_map[tmp[0]][tmp[1]])
        return path

class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass

class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
