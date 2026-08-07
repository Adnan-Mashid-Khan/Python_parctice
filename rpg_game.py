#!/usr/bin/env python

import random
import time

poke_library = {
    "pikachu": {
        "name": "pikachu",
        "symbol": "@",
        "hp": 35,
        "moves": [
            "Thunder Shock",
            "Quick Attack"
        ]
    }
}

move_library = {
    "Thunder Shock": {
        "damage": 12
    },
    "Quick Attack": {
        "damage": 8
    }
}


class World:
    def __init__(self):
        self.width = 10
        self.height = 10
        self.game_map = []
        self.respawn_timer = None
        self.respawn_delay = 30

    def grid(self):
        for y in range(self.width):
            row = []
            for x in range(self.height):
            
                if 3 <= x <= 6 and 3 <= y <= 6:
                    terrain = "grass"
                elif 6 <= x <= 8 and 7 <= y <= 9:
                    terrain  = "water"
                else:
                    terrain = "rest of the area"
                    
                tile = Tile(x, y, terrain)
                row.append(tile)
            self.game_map.append(row)

    def display(self):
        for row in self.game_map:
            for tile in row:
                if tile == player.current_tile:
                    print(player.name, end= " ")

                elif tile == healer.current_tile:
                    print(healer.symbol, end= " ")
                    
                elif tile == wild_pokemon.current_tile:
                    print(wild_pokemon.symbol, end= " ")
                
                else:
                    tile.describe_tile()
            print()

    def spawn_player(self, player):
        player.current_tile = self.game_map[0][0]

    def spawn_healer(self, healer):
        healer.current_tile = self.game_map[0][9]

    def spawn_pokemon(self, wild_pokemon):
        grass_tiles = []
        for row in self.game_map:
            for tile in row:
                if tile.terrain == "grass":
                    grass_tiles.append(tile)

        wild_pokemon.current_tile = random.choice(grass_tiles)


    def next_tile(self, player, command):
        current = player.current_tile
        x = current.x
        y = current.y

        if command == "r":
            x = x + 1
            if x >= self.width:
                return current
            
        if command == "l":
            x = x - 1
            if x < 0:
                return current

        if command == "u":
            y = y - 1
            if y < 0:
                return current
                
        if command == "d":
            y = y + 1
            if y >= self.height:
                return current

        next_tile = self.game_map[y][x]

        if next_tile.terrain == "water":
            return current

        return next_tile


    def check_for_encounter(self, player, wild_pokemon, healer):
        if player.current_tile == wild_pokemon.current_tile:
            print(f"A Wild {wild_pokemon.name} Appeared!")
            self.battle_menu(player, wild_pokemon, healer)
            

    def battle_menu(self, player, wild_pokemon, healer):
        
        while True:
            print("1. Fight")
            print("2. Capture")
            print("3. Run")
            choice = input("Choice: ")

            if choice == "1":
                for index, move in enumerate(player.active_pokemon.moves, start=1):
                    print(f"{index}. {move}")

                
                try:
                    move_choice = int(input("Choice: "))
                    if move_choice < 1 or move_choice > len(player.active_pokemon.moves):
                        print("Choose one of the listed moves.")
                        continue
                    chosen_move = player.active_pokemon.moves[move_choice - 1]
                    
                except ValueError:
                    print("please choose from given options")
                    continue
                    
                print(f"player {player.active_pokemon.name} used {chosen_move}!")
                player.active_pokemon.attack(wild_pokemon, chosen_move)
                print(f"Wild {wild_pokemon.name} hp remaining {wild_pokemon.hp}")

                if wild_pokemon.is_fainted():
                    print(f"Wild {wild_pokemon.name} fainted!")
                    wild_pokemon.current_tile = None
                    player.active_pokemon.gain_exp(100)
                    self.respawn_timer = time.time()
                    break
                    
                move_choice = random.randint(0, 1)
                chosen_move = wild_pokemon.moves[move_choice]
                print(f"Wild {wild_pokemon.name} used {chosen_move}")
                wild_pokemon.attack(player.active_pokemon, chosen_move)
                print(f"Player {player.active_pokemon.name} hp remaining {player.active_pokemon.hp}")

                if player.active_pokemon.is_fainted():
                    print(f"Player {player.active_pokemon.name} fainted!")
                    for pokemon in player.pokemon:
                        if pokemon.hp > 0:
                            player.active_pokemon = pokemon
                            print(f"{pokemon.species} sent out!")
                            break
                            
                    else:
                        print("all pokemon knocked out")
                        player.current_tile = self.game_map[0][9]
                        print("reached poke center!")
                        healer.heal(player)
                    
                    break
        
            elif choice == "2":
                if player.inventory["pokeball"] <= 0:
                    print("no pokeball in remaining!")
                    continue
                
                player.inventory["pokeball"] -=1
                print("You threw pokeball!")
                caught = player.catch(wild_pokemon)
                if caught:
                    player.pokemon.append(wild_pokemon)
                    self.respawn_timer = time.time()
                    wild_pokemon.current_tile = None
                    for pokemon in player.pokemon:
                        print(pokemon.name)
                    break
                else: 
                    wild_move = random.randint(0, 1)
                    wild_pokemon.attack(player.active_pokemon, wild_pokemon.moves[wild_move])
                    print(f"Player {player.active_pokemon.name} hp remaining {player.active_pokemon.hp}")

            elif choice == "3":
                print("You Ran Away!")
                break

            else:
                print("please choose from available options")


    def check_for_npc(self, player, healer):
        if healer.current_tile == player.current_tile:
            print("1. Press T to Talk")
            print("2. Press L to leave")

            talk_choice = input("choose: ")

            if talk_choice == "t":
                healer.talk(player)

            elif talk_choice == "l":
                print("you left")
                
            else: print("please choose from given options")

    def check_respawn(self, wild_pokemon):
        if wild_pokemon.current_tile is None:
            if time.time() - self.respawn_timer >= self.respawn_delay:
                wild_pokemon.hp = wild_pokemon.max_hp
                self.spawn_pokemon(wild_pokemon)
                self.respawn_timer = None
            


class Tile:
    def __init__(self, x, y, terrain):
        self.x = x
        self.y = y
        self.terrain = terrain

    def describe_tile(self):
        if self.terrain == "grass":
            print("G", end= " ")
        elif self.terrain == "water":
            print("w", end= " ")
        else:
            print(".", end= " ")
        


class Player:
    def __init__(self):
        self.name = "P"
        self.current_tile = None
        self.pokemon = []
        self.active_pokemon = None
        self.inventory = {
            "pokeball": 5,
            "potion": 0,
            "gold": 0
        }

    def move(self, command, world):

        if command in ['l', 'r', 'u', 'd']:
            next_step = world.next_tile(self, command)
            if next_step == self.current_tile:
                print("No movement space")
            else:
                self.current_tile = next_step

    def catch(self, wild_pokemon):
        roll = random.randint(1, 100)
        catch_chance = 100 - ((wild_pokemon.hp / wild_pokemon.max_hp) * 100)
        if catch_chance < 1:
            catch_chance = 1

        if roll <= catch_chance:
            print(f"You caught {wild_pokemon.name}!")
            return True
        
        print(f"{wild_pokemon.owner} {wild_pokemon.name} broke free!")
        return False

    def status(self, command):
        if command == "status":
            print("1. pokemon team")
            print("2. inventory")

            choice = str(input("choice: "))
                
            if choice == "1":

                for index, poke in enumerate(self.pokemon):
                    print(f"{index +1}. {poke.species}")
                print("choose number to see pokemon detail")
                print("type (back) to go back")
                    
                choice = input("choice: ")

                if choice == "back":
                    return

                choice = int(choice)
                
                if choice in range(1, len(self.pokemon) + 1):
                    selected = self.pokemon[choice - 1]

                    print(f"species: {selected.species}")
                    print(f"level: {selected.level}")
                    print(f"hp/max hp: {selected.hp} / {selected.max_hp}")
                    print(f"exp: {selected.exp}")

                else:
                    print("please choose from the given options!")


        
            elif choice == "2":
                for item, amount in self.inventory.items():
                    print(f"{item}: {amount}")

            else:
                print("please choose from the given options!")

    def save(self, command):
        if command == "save":
            print("saving the game...")
            with open("save_rpg.txt", "w") as f:
                x = self.current_tile.x
                y = self.current_tile.y

                f.write(f"{x} {y}\n")
                
                for item, value in self.inventory.items():
                    f.write(f"{item} {value}\n")

                active_index = self.pokemon.index(self.active_pokemon)
                f.write(f"{str(active_index)}\n")

                for pokemon in player.pokemon:
                    f.write(f"{pokemon.species}\n")
                    f.write(f"{str(pokemon.level)}\n")
                    f.write(f"{str(pokemon.exp)}\n")
                    f.write(f"{str(pokemon.hp)}\n")
                    f.write(f"{str(pokemon.max_hp)}\n")


            print("progress saved!")

    def load(self, command, world):
        if command == "load":
            print("loading game...")
            
            with open("save_rpg.txt", "r") as f:
                lines = f.readlines()

            
            x, y = lines[0].split()
            x = int(x)
            y = int(y)

            self.current_tile = world.game_map[y][x]
            for line in lines[1:3]:
                item, value = line.strip().split()
                self.inventory[item] = int(value)

            active_index = int(lines[4].strip())
            
            for i in range(5, len(lines), 5):
                species = lines[i].strip()

                load_pokemon = Pokemon(species)

                load_pokemon.level = int(lines[i + 1].strip())
                load_pokemon_exp = int(lines[i + 2].strip())
                load_pokemon_hp = int(lines[i + 3].strip())
                load_pokemon.max_hp = int(lines[i + 4].strip())

                self.pokemon.append(load_pokemon)

            self.active_pokemon = self.pokemon[active_index]
            
            print("Progress Loaded!")
                
                
            


class Pokemon:
    def __init__(self, species):
        self.species = species
        self.max_hp = None
        self.hp = None
        self.level = 1
        self.exp = 0
        self.owner = None
        self.symbol = None
        self.name = None
        self.moves = []
        self.current_tile = None

        self.load_data()

    def load_data(self):
        self.symbol = poke_library[self.species]["symbol"]
        self.name = poke_library[self.species]["name"]
        self.max_hp = poke_library[self.species]["hp"]
        self.hp = self.max_hp
        self.moves = poke_library[self.species]["moves"]
        

    def attack(self, target, chosen_move):
        damage = move_library[chosen_move]["damage"]
        target.hp = max(0, target.hp - damage)
        print(f"{self.owner} {self.name} dealt {damage} damage!")

    def is_fainted(self):
        return self.hp <= 0

    def gain_exp(self, amount):
        self.exp += amount
        self.check_level_up()

    def check_level_up(self):
        exp_to_next_lv = self.level * 100
        while self.exp >= exp_to_next_lv:
            self.exp -= exp_to_next_lv
            self.level += 1
            self.max_hp += 5
            self.hp = self.max_hp
            print("leveld up!")
            print(f"current level {self.level}!")
            print(f"max hp increased to {self.max_hp}!")
            print(f"pokemon healed, current hp {self.hp}!")

            exp_to_next_lv = self.level * 100


class HealerNPC:
    def __init__(self):
        self.name = "nurse joy"
        self.symbol = "H"
        self.current_tile = None
        self.dialogues = "Hello Player"

    def talk(self, player):
        print(self.dialogues)

        print("1. Heal Pokemon")
        print("2. Goodbye")

        choice = input("Choice: ")

        if choice == "1":
            self.heal(player)
        elif choice == "2":
            print("See you again!")

    def heal(self, player):
        for pokemon in player.pokemon:
            pokemon.hp = pokemon.max_hp

        print("pokemon healed")
    


world = World()

player = Player()
starter = Pokemon("pikachu")
starter.owner = "Player"

player.pokemon.append(starter)
player.active_pokemon = starter

wild_pokemon = Pokemon("pikachu")
wild_pokemon.owner = "wild"

healer = HealerNPC()

world.grid()
world.spawn_player(player)
world.spawn_pokemon(wild_pokemon)
world.spawn_healer(healer)
world.display()




while True:
    command = str(input(f"direction: "))
    player.move(command, world)
    player.status(command)
    player.save(command)
    player.load(command, world)
    
    world.check_for_encounter(player, wild_pokemon, healer)
    world.check_respawn(wild_pokemon)
    world.check_for_npc(player, healer)

    

    if command == "exit":
        print("Closing the game!")
        break

    world.display()
