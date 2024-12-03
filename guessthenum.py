"""
Guess The Number Game

A simple number guessing game with configurable settings and menu system.
The player needs to guess a randomly generated number within a specified range
with limited attempts and lives.

Classes:
    Menu: Handles menu creation and navigation
    Game: Main game logic and settings
"""

import sys
import random

class ConsoleMenu:
    """
    A flexible menu system that handles user input and navigation.
    
    Attributes:
        headerDecor (str): Template for header decoration
        name (str): Menu name
        header (str): Formatted header
        footer (str): Formatted footer
        choices (list): List of menu options

    Usage:
        The Menu class supports three types of menu items:
        1. Option - Executes a function when selected
        2. Value - Configures a variable when selected
        3. Submenu - Opens another menu when selected

    Example:
        #### Create a simple menu with options
        - menu = Menu("Main Menu", [
            Menu.Option("start", start_game),
            Menu.Option("quit", quit_game)
        ])

        #### Create a menu with configurable values
        - settings = Menu("Settings", [
            Menu.Value(game, "lives", "Player Lives"),
            Menu.Value(game, "range", "Number Range")
        ])

        #### Create a menu with submenus
        - main = Menu("Game", [
            Menu.Option("play", play_game),
            settings,  # Submenu
            Menu.Option("exit", quit_game)
        ])

        #### Open the menu
        - main.open()

    Notes:
        - Options are displayed as numbered choices
        - Values show current value in parentheses
        - Use callable menu items for dynamic submenus
        - Input validation is handled automatically
    """
    
    # Format string for creating decorated headers
    headerDecor = "<=-=-=-=-=-={ %s }=-=-=-=-=-=>"
    
    def __init__(self, name: str, choices: list, header: str = None) -> None:
        """
        Initialize menu with name and choices.

        Args:
            name (str): Menu name
            choices (list): List of menu options
            header (str, optional): Custom header text
        """
        # Capitalize menu name
        self.name = name.title()
        # Create header with custom text or menu name
        if header is None:
            self.header = self.headerDecor % self.name
        else:
            self.header = self.headerDecor % header.title()
        # Create footer line matching header length
        self.footer = "=" * len(self.header)
        self.choices = choices
    
    def open(self) -> None:
        """
        Display menu and handle user input.
        Processes user selection and navigates to appropriate option.
        """
        print("") # Visual spacing
        
        # Display menu header
        print(self.header)
        # Display numbered menu options
        for i, option in enumerate(self.choices):
            # Handle callable menu items (like dynamic submenus)
            if callable(option):
                option = option()
            print(f"[{i + 1}] {option.name}", end = "")
            # Show current value for configurable options
            if option.__class__ is self.Value:
                print(f" ({getattr(option.parent, option.atr)})", end = "\n")
            else:
                print("", end = "\n")
        print(self.footer)
        
        # Menu selection loop
        choosing = True
        while choosing:
            try:
                # Get user input (subtract 1 for zero-based indexing)
                choice = int(input(">>> ")) - 1
            except ValueError:
                print("Please enter the number of the option you want to choose.")
                continue
                
            # Validate input range
            if choice > len(self.choices) - 1 or choice < 0:
                print("Please enter a valid option.")
                continue
            else:
                choice = self.choices[choice]
                # Handle callable menu items
                if callable(choice):
                    choice = choice()
                
                # Process different types of menu items
                if choice.__class__ is ConsoleMenu:
                    choosing = False
                    choice.open()  # Open submenu
                elif choice.__class__ is self.Value:
                    choice.select(len(self.header))  # Configure value
                    self.open()  # Reopen current menu
                elif choice.__class__ is self.Option:
                    choosing = False
                    choice.select()  # Execute option function
                    
    class Option:
        """
        Represents a menu option that executes a function when selected.
        
        Attributes:
            name (str): Option display name
            func (callable): Function to execute when selected

        Example:
            option = Menu.Option("start game", start_function)
        """
        def __init__(self, name: str, func: callable) -> None:
            self.name = name.title()
            self.func = func
            
        def select(self) -> None:
            self.func()
                    
    class Value:
        """
        Represents a configurable value in the menu system.
        
        Attributes:
            parent (object): Object containing the value
            atr (str): Attribute name to modify
            name (str): Display name for the value

        Example:
            value = Menu.Value(game, "lives", "Player Lives")\n
            value = Menu.Value(game, "range", "Number Range")\n
        """
        def __init__(self, obj: object, atr: str, name: str = None) -> None:
            self.parent = obj
            self.atr = atr
            self.name = name or atr
            
        def select(self, padding: int = 0) -> None:
            print("")
            # Display value configuration UI
            print(f"{self.name.title().center(padding, "-")}")
            print(f"enter the new value ".center(padding))
            
            choosing = True
            while choosing:
                try:
                    # Get current value type
                    atrType = getattr(self.parent, self.atr).__class__
                    print("<<<", end="")
                    # Handle list/tuple inputs differently
                    if atrType is list or atrType is tuple:
                        setattr(self.parent, self.atr, atrType(map(int or str, input().split())))
                    else:
                        setattr(self.parent, self.atr, atrType(input()))
                except TypeError:
                    print("Value must be of type %s" % atrType.__name__)
                    continue
                choosing = False


class Game(object):
    """
    Main game class handling game logic and state.
    
    Attributes:
        lives (int): Total lives available
        remainingLives (int): Current remaining lives
        highscore (int): Highest score achieved
        score (int): Current score
        range (tuple): Range for random number generation (min, max)
        attempts (int): Number of attempts allowed per round
    """
    
    def __init__(self) -> None:
        """Initialize game with default settings."""
        # Initialize game state
        self.lives = 3
        self.remainingLives = self.lives
        self.highscore = 0
        self.score = 0
        
        # Game configuration
        self.range = (1, 100)  # Number range for guessing
        self.attempts = 7      # Attempts per round
    
    def enter(self):
        """Start the game by opening the main menu."""
        self.mainMenu().open()
        
    def mainMenu(self):
        """
        Create and return the main menu structure.
        
        Returns:
            Menu: Main menu with start, settings, and quit options
        """
        return ConsoleMenu("main menu", [ConsoleMenu.Option("start", self.startGame), self.settingsMenu, ConsoleMenu.Option("quit", self.quit)])
    
    def startGame(self) -> None:
        """Initialize a new game session with fresh score and lives."""
        print("")
        print("||||||||||!Game started!||||||||||")
        self.score = 0
        self.remainingLives = self.lives
        self.startRound()
        
    def startRound(self):
        """
        Start a new round of the game.
        Generates random number and handles guess attempts.
        Updates score and lives based on performance.
        """
        # Generate target number
        num = random.randint(*self.range)
        # Update highscore if needed
        if self.score > self.highscore:
            self.highscore = self.score
        
        # Display round information
        print("")
        print(f"Range: {self.range[0]}-{self.range[1]}")
        print(f"Score: {self.score}")
        print(f"Highscore: {self.highscore}")
        print(f"Remaining lives: {self.remainingLives}")
        print("")
        print("!!!!!Guess the number!!!!!")
        
        # Main game loop
        attempts = self.attempts
        while attempts > 0:
            print("")
            try:
                guess = int(input("<<< "))
            except ValueError:
                print("Guess must be a number!")
                continue
            
            # Process guess
            if guess == num:
                print("You guessed correctly!")
                self.score += 1
                break
            elif guess < self.range[0] or guess > self.range[1]:
                print("Guess must be within range!")
                continue
            elif guess < num:
                print("Too low!")
                attempts -= 1
            elif guess > num:
                print("Too high!")
                attempts -= 1
            print(f"attempts left: {attempts}")
        else:
            # Handle failed round
            print("You ran out of attempts!")
            print(f"The number was {num}")
            self.remainingLives -= 1
            
        # Update game state and continue
        if self.score > self.highscore:
            self.highscore = self.score
        
        if self.remainingLives <= 0:
            self.restart().open()
        else:
            self.startRound().open()
    
    def restart(self):
        """
        Create and return the restart menu.
        
        Returns:
            Menu: Restart menu with yes/no options
        """
        return ConsoleMenu("Try Again?", [ConsoleMenu.Option("yes", self.startGame), ConsoleMenu.Option("no", self.endGame)])
            
    def endGame(self):
        """Display final game statistics and exit."""
        print("")
        
        print("||||||||||!Game ended!||||||||||")
        print(f"Range: {self.range[0]}-{self.range[1]}")
        print(f"Score: {self.score}")
        print(f"Highscore: {self.highscore}")
        print(f"Attemps per Round: {self.attempts}")
        print(f"Total lives: {self.lives}")
        
        self.score = 0
        self.quit()
        
    def settingsMenu(self):
        """
        Create and return the settings menu.
        
        Returns:
            Menu: Settings menu with configurable game parameters
        """
        return ConsoleMenu("settings", [self.mainMenu, ConsoleMenu.Value(self, "lives"), ConsoleMenu.Value(self, "range"), ConsoleMenu.Value(self, "attempts")])
    
    def quit(self):
        """Exit the game."""
        sys.exit()
        

if __name__ == "__main__":
    Game().enter()