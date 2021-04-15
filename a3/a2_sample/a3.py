import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

DIRECTIONS = {
    "W": (-1, 0),
    "S": (1, 0),
    "D": (0, 1),
    "A": (0, -1)
}

INVESTIGATE = "I"
QUIT = "Q"
HELP = "H"

VALID_ACTIONS = [INVESTIGATE, QUIT, HELP, *DIRECTIONS.keys()]

HELP_MESSAGE = f"Here is a list of valid actions: {VALID_ACTIONS}"

INVALID = "That's invalid."

WIN_TEXT = "You have won the game with your strength and honour!"

LOSE_TEST = "You have lost all your strength and honour."
LOSE_TEXT = "You have lost all your strength and honour."

# Fill these in with your details
__author__ = "{{Joseph Fernando}} ({{s46424873}})"
__email__ = "j.fernando@uqconnect.edu.au"
__date__ = "30/10/20"


class Display:
    """Display of the dungeon."""

    def __init__(self, game_information, dungeon_size):
        """Construct a view of the dungeon.

        Parameters:
            game_information (dict<tuple<int, int>: Entity): Dictionary 
                containing the position and the corresponding Entity
            dungeon_size (int): the width of the dungeon.
        """
        self._game_information = game_information
        self._dungeon_size = dungeon_size

    def display_game(self, player_pos):
        """Displays the dungeon.
        
        Parameters:
            player_pos (tuple<int, int>): The position of the Player
        """
        dungeon = ""

        for i in range(self._dungeon_size):
            rows = ""
            for j in range(self._dungeon_size):
                position = (i, j)
                entity = self._game_information.get(position)

                if entity is not None:
                    char = entity.get_id()
                elif position == player_pos:
                    char = PLAYER
                else:
                    char = SPACE
                rows += char
            if i < self._dungeon_size - 1:
                rows += "\n"
            dungeon += rows
        print(dungeon)

    def display_moves(self, moves):
        """Displays the number of moves the Player has left.
        
        Parameters:
            moves (int): THe number of moves the Player can preform. 
        """
        print(f"Moves left: {moves}\n")


def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.
    
    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the 
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    return dungeon_layout


class Entity:
    """ """

    _id = "Entity"

    def __init__(self):
        """
        Something the player can interact with
        """
        self._collidable = True

    def get_id(self):
        """ """
        return self._id

    def set_collide(self, collidable):
        """ """
        self._collidable = collidable

    def can_collide(self):
        """ """
        return self._collidable

    def __str__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        return str(self)


class Wall(Entity):
    """ """

    _id = WALL
    
    def __init__(self):
        """ """
        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """ """
    def on_hit(self, game):
        """ """
        raise NotImplementedError


class Key(Item):
    """ """

    _id = KEY

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())


class MoveIncrease(Item):
    """ """

    _id = MOVE_INCREASE

    def __init__(self, moves=5):
        """ """
        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """ """
    _id = DOOR

    def on_hit(self, game):
        """ """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.set_win(True)
                return

        messagebox.showinfo(title=None, message="You don't have the key!")


class Player(Entity):
    """ """

    _id = PLAYER

    def __init__(self, move_count):
        """ """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self, position):
        """ """
        self._position = position

    def get_position(self):
        """ """
        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """
        self._move_count += number

    def moves_remaining(self):
        """ """
        return self._move_count

    def add_item(self, item):
        """Adds item (Item) to inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """ """
        return self._inventory


class GameLogic():
    """ """
    def __init__(self, dungeon_name):
        """ """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False

    def get_positions(self, entity):
        """ """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """ """
        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)[0]
        door_position = self.get_positions(DOOR)[0]
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)
        self._player.set_position(player_pos)

        information = {
            key_position: Key(),
            door_position: Door(),
        }

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()
        return information
    def get_player(self):
        """ """
        return self._player

    def get_entity(self, position):
        """ """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """ """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """ """
        return self._game_information

    def get_dungeon_size(self):
        """ """
        return self._dungeon_size

    def move_player(self, direction):
        """ """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True
        
        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """ """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """ """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """ """
        self._win = win

    def won(self):
        """ """
        return self._win

class AbstractGrid(tk.Canvas):
    """Base class for UI elements"""
    def __init__(self, master, dungeon_name):
        self._game=GameLogic(dungeon_name)
        self._door=Door()
        self._key=Key()
        self._move_increase=MoveIncrease()
        self._player=Player(5)
        self._wall=Wall()
        self._master=master
    def get_bbox(self, position):
        pass
    def pixel_to_position(self, pixel):
        pass
    def get_position_center(self, position):
        pass
    def annotate_position(self, position, text):
        pass
    def picture(self, picture, frame, size, placement):
        """Places a resized square image in a specifed frame at a specified location.

        Args:
        picture: the image to be used (example.gif)
        frame: the frame to put the image in (tk.frame, etc.)
        size: the square resize of the image in pixels (int)
        placement: the placement of the image from the top left (list)

        """
        
        load=Image.open(picture)
        load=load.resize((size, size))
        render=ImageTk.PhotoImage(load)
        img=tk.Label(frame, image=render, bd=0, highlightthickness=0)
        img.image=render
        img.place(x=placement[0], y=placement[1])

class GameApp(AbstractGrid):
    def __init__(self, master, task='TASK_TWO', dungeon_name='game2.txt'):
        """Binds keys to UI elements, creates initial window
        Args:
        task: which mode to use (TASK_ONE, TASK_TWO)
        dungeon_name: which game to use (game1.txt, etc.)

        """
        super().__init__(master, dungeon_name)
        self._master.title('Key Cave Adventure Game')
        self._heading_frame=tk.Frame(self._master, bg='green', width=800, height=100)
        self._heading_frame.grid(row=0, column=0, columnspan=2)
        self._heading=tk.Label(self._heading_frame, text='Key Cave Adventure Game', bg='medium spring green', padx=330)
        self._heading.pack(side=tk.RIGHT)
        self._player=self._game.get_player()
        self._initial_move_count=self._player.moves_remaining()
        self._task=task
        self._dungeon_name=dungeon_name
        
        if task=='TASK_ONE':
            self._dungeon_map=DungeonMap(self._master, dungeon_name)
        else:
            self._dungeon_map=AdvancedDungeonMap(self._master, dungeon_name)
            self._status_bar=StatusBar(self._master, dungeon_name)
            self.moves_remaining=self._status_bar._moves_remaining_frame.create_text(100, 80, text=f'{self._player.moves_remaining()} moves remaining')
        self._keypad=KeyPad(self._master, dungeon_name)
        
        self._keypad._keypad_frame.bind('<Button-1>', self.play)
        
        self._master.bind('<w>', self.play)
        self._master.bind('<a>', self.play)
        self._master.bind('<s>', self.play)
        self._master.bind('<d>', self.play)
        
        self._status_bar._quit.bind('<Button-1>', self.quit)
        self._status_bar._new_game.bind('<Button-1>', self.restart)
        self._count=0
        self.timer()
    def timer(self):
        """Text indicating time elapsed and counting time"""
        if self._task=='TASK_ONE':
            return None
        else:
            try:
                self._status_bar._timer_frame.itemconfig(self._timing, text=f'{self._count//60}m {self._count%60}s')
            except:
                self._timing=self._status_bar._timer_frame.create_text(100, 80, text=f'{self._count//60}m {self._count%60}s')
            self._count+=1
            root.after(1000, self.timer)
    def movesleft(self):
        """Text indicating moves left for the player"""
        if self._task=='TASK_ONE':
            return None
        else:
            try:
                self._status_bar._moves_remaining_frame.itemconfig(self.moves_remaining, text=f'{self._player.moves_remaining()-1} moves remaining')
            except:
                self.moves_remaining=self._status_bar._moves_remaining_frame.create_text(100, 80, text=f'{self._player.moves_remaining()} moves remaining')
    def play(self, event):
        """Binds keys to UI elements, creates initial window
        Args:
        event:key presses and mouse click

        """
        #Game already lost
        if self._player.moves_remaining()==0:
            return
            print('ok')
        #Moving with keypad
        if str(self._keypad.pixel_to_direction(event.x, event.y)) in 'WASD':
            self._direction=str(self._keypad.pixel_to_direction(event.x, event.y))

        #Moving with keys
        elif (str(event.keysym)).upper() in 'WASD':
            self._direction=(str(event.keysym)).upper()
        else:
            return
        if not self._game.collision_check(self._direction):
            self._game.move_player(self._direction)
            self._dungeon_map._player_position=self._game.get_player().get_position()
            entity = self._game.get_entity(self._player.get_position())
            
         
        
            # process on_hit and check win state
            if entity is not None:
                entity.on_hit(self._game)
                if str(entity)==str(Key()):
                    self._dungeon_map._key_position=self._game.get_positions(KEY)
                if str(entity)==str(MoveIncrease()):
                    self._dungeon_map._move_increase_position=self._game.get_positions(MOVE_INCREASE)
                    self.movesleft()
                if self._game.won():
                    self.update()
                    self._win_box=messagebox.askquestion(title='You won!', message=f'You have finished the level with a score of {self._count-1}. \n\nWould you like to play again?')
                    if self._win_box=='yes':
                        self.restart()
                    if self._win_box=='no':
                        self.quit()
                        return
                        
        
        #Invalid move
        else:
            messagebox.showinfo(title=None, message=INVALID)
        

        self.update()
        #Game lost
        if self._game.check_game_over():
            messagebox.showinfo(title=None, message=LOSE_TEST)
            return
        
    def update(self):
        """Updates timer, map and moves remaining"""
        self._dungeon_map.draw_grid()
        self.movesleft()
        self._player.change_move_count(-1)

    def quit(self, event=None):
        """Destroys window"""
        root.destroy()

    def restart(self, event=None):
        """Binds keys to UI elements, creates initial window
        Args:
        event: triggers after mouse click on quit

        """
        #Restore moves, clear inventory
        self._game._player.change_move_count(self._initial_move_count-self._player.moves_remaining()+1)
        self._game._player._inventory.clear()
        #Reset entity positions and win
        self._game._game_information = self._game.init_game_information()
        self._game._win = False
        #Reset entity positions (for dungeon map)
        self._dungeon_map._player_position=self._game.get_player().get_position()
        self._dungeon_map._key_position=self._game.get_positions(KEY)[0]
        try:
            self._dungeon_map._move_increase_position=self._game.get_positions(MOVE_INCREASE)[0]
        except:
            self._dungeon_map._move_increase_position=None
        self._dungeon_map=AdvancedDungeonMap(self._master, self._dungeon_name)
        #Redraw grid, moves and timer
        self._dungeon_map.draw_grid()
        self._count=0
        self.movesleft()
        
class DungeonMap(AbstractGrid):
    def __init__(self, master, dungeon_name):
        """Draws grid and gets positions of entities
        Args:
        dungeon_name: which game to use (game1.txt, etc.)

        """
        super().__init__(master, dungeon_name)
        self._player_position=self._game.get_player().get_position()
        self._key_position=self._game.get_positions(KEY)[0]
        try:
            self._move_increase_position=self._game.get_positions(MOVE_INCREASE)[0]
        except:
            self._move_increase_position=None
        self.draw_grid()
        
    def draw_grid(self):
        """Creates map"""
        self._dungeon_map_frame=tk.Canvas(self._master, bg='dark grey', width=600, height=600)
        
        self._dungeon_map_frame.grid(row=1, column=0)
        row=0
        while self._game._dungeon_size>row:
            column=0
            while self._game._dungeon_size>column:
                
                self._rectangle_placement=(column*(600/self._game._dungeon_size),row*(600/self._game._dungeon_size),
                (column+1)*(600/self._game._dungeon_size),(row+1)*(600/self._game._dungeon_size))
                
                self._text_placement=600*(2*column+1)/self._game._dungeon_size/2, 600*(2*row+1)/self._game._dungeon_size/2
                
                if self._player_position==(row, column):
                    self._dungeon_map_frame.create_rectangle(self._rectangle_placement, fill='medium spring green')
                    self._dungeon_map_frame.create_text(self._text_placement, text='Ibis')

                elif str(self._game.get_entity((row, column)))==str(Door()):
                    self._dungeon_map_frame.create_rectangle(self._rectangle_placement, fill='red')
                    self._dungeon_map_frame.create_text(self._text_placement, text='Nest')

                elif str(self._game.get_entity((row, column)))==str(Wall()):
                    self._dungeon_map_frame.create_rectangle(self._rectangle_placement, fill='grey')

                elif self._key_position==((row, column)):
                    self._dungeon_map_frame.create_rectangle(self._rectangle_placement, fill='yellow')
                    self._dungeon_map_frame.create_text(self._text_placement, text='Trash')

                elif self._move_increase_position==((row, column)) and self._move_increase_position!=None:
                    self._dungeon_map_frame.create_rectangle(self._rectangle_placement, fill='orange')
                    self._dungeon_map_frame.create_text(self._text_placement, text='Banana')
                    
                column+=1
            row+=1

class AdvancedDungeonMap(AbstractGrid):
    def __init__(self, master, dungeon_name):
        """Draws grid and gets positions of entities
        Args:
        dungeon_name: which game to use (game1.txt, etc.)

        """
        super().__init__(master, dungeon_name)
        self._player_position=self._game.get_player().get_position()
        self._key_position=self._game.get_positions(KEY)[0]
        self._door_position=self._game.get_positions(DOOR)[0]
        try:
            self._move_increase_position=self._game.get_positions(MOVE_INCREASE)[0]
        except:
            self._move_increase_position=None
        self.draw_grid()
        
    def draw_grid(self):
        """Creates map"""
        #Ensures window isn't clogged up by previous renditions of map
        try:
            self._dungeon_map_frame.destroy()
        except:
            pass
        self._dungeon_map_frame=tk.Canvas(self._master, bg='dark grey', width=600, height=600)
        self._dungeon_map_frame.grid(row=1, column=0)
        row=0
        while self._game._dungeon_size>row:
            column=0
            while self._game._dungeon_size>column:
                self._size=int(600/self._game._dungeon_size)
                self._placement=[column*(600/self._game._dungeon_size), row*(600/self._game._dungeon_size)]
                self.picture('empty.gif', self._dungeon_map_frame,self._size,
                self._placement)
                if self._player_position==(row, column):
                    self.picture('player.gif', self._dungeon_map_frame,self._size,
                self._placement)
                                       
                elif self._door_position==((row, column)):
                    self.picture('door.gif', self._dungeon_map_frame,self._size,
                self._placement)
                    
                elif str(self._game.get_entity((row, column)))==str(Wall()):
                    self.picture('wall.gif', self._dungeon_map_frame,self._size,
                self._placement)
                     
                elif self._key_position==((row, column)):
                    self.picture('key.gif', self._dungeon_map_frame,self._size,
                self._placement)
    
                elif self._move_increase_position==((row, column)) and self._move_increase_position!=None:
                    self.picture('moveIncrease.gif', self._dungeon_map_frame,self._size,
                    self._placement)
                
                column+=1
            row+=1

class KeyPad(AbstractGrid):
    def __init__(self, master, dungeon_name):
        """Creates keypad
        Args:
        dungeon_name: which game to use (game1.txt, etc.) (not nessesary)"""
        super().__init__(master, dungeon_name)
        self._keypad_frame=tk.Canvas(self._master, width=200, height=100)
        self._keypad_frame.grid(row=1, column=1)
        self._keypad_frame.create_rectangle(0,100,66,50, fill='grey')
        self._keypad_frame.create_text(33,75, text='A')
        
        self._keypad_frame.create_rectangle(66,0,134,50, fill='grey')
        self._keypad_frame.create_text(99,25, text='W')
        
        self._keypad_frame.create_rectangle(134,100,200,50, fill='grey')
        self._keypad_frame.create_text(167,75, text='D')
        
        self._keypad_frame.create_rectangle(66,50,134,100, fill='grey')
        
        self._keypad_frame.create_text(99,75, text='S')
        
    def pixel_to_direction(self, x, y):
        """Converts mouse click to direction
        Args:
        x, y: position of mouse when clicked
        Returns:
        str: letter indicating direction to move player
        """
        if 0<x<66 and 50<y<100:
            return 'A'
            
        elif 66<x<134 and 0<y<50:
            return 'W'

        elif 134<x<200 and 50<y<100:
            return 'D'

        elif 66<x<134 and 50<y<100:
            return 'S'
    
class StatusBar(AbstractGrid):
    def __init__(self, master, dungeon_name):
        """Creates status bar
        Args:
        dungeon_name: which game to use (game1.txt, etc.) to know number of moves"""
        super().__init__(master, dungeon_name)
        self._moves_remaining=3
        self._statusbar_frame=tk.Frame(self._master, width=600, height=100)
        self._statusbar_frame.grid(row=2, column=0, columnspan=2)
        self._size=50
        self._placement=[0, 25]
        self.timer()
        self.moves_remaining()
        self.menu()
    def timer(self):
        """Creates timer frame, text and image"""
        self._timer_frame=tk.Canvas(self._statusbar_frame, width=200, height=100)
        self._timer_frame.grid(row=0, column=1)
        self.picture('clock.gif', self._timer_frame,self._size,
                self._placement)
        self._timer_frame.create_text(100, 50, text='Time elapsed')
    def moves_remaining(self):
        """Creates moves remaining frame, text and image"""
        self._moves_remaining_frame=tk.Canvas(self._statusbar_frame, width=200, height=100)
        self._moves_remaining_frame.grid(row=0, column=2)
        self.picture('lightning.gif', self._moves_remaining_frame,self._size,
                self._placement)
        self._moves_remaining_frame.create_text(100, 50, text='Moves left')
                
    def menu(self):
        """Creates buttons for quitting and starting a new game"""
        self._menu_frame=tk.Canvas(self._statusbar_frame, width=200, height=100)
        self._menu_frame.grid(row=0, column=0)
        self._new_game=tk.Button(self._menu_frame, text='New game')
        self._new_game.pack()
        self._quit=tk.Button(self._menu_frame, text='Quit')
        self._quit.pack()

if __name__ == "__main__":
    root=tk.Tk()
    app=GameApp(root)
    root.mainloop()


