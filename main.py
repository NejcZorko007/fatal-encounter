# Create player and enemy objects
print("Welcome to the battle game!")
player_name = input("Enter your character's name: ")

# Create player and enemy objects
player = Player(player_name, health=100, attack=25, defense=10, heal=0)
enemy = Enemy(name="Noatov tič", health=75, attack=20, defense=10)

# Start the battle
battle(player, enemy)

# Function to handle the battle
def battle(player, enemy):
    print(f"\n{player.name} encounters {enemy.name}!")
    while player.is_alive() and enemy.is_alive():
        print(f"\n{player.name}'s HP: {player.health} | {enemy.name}'s HP: {enemy.health}")
        print("Choose an action:")
        print("1. Attack")
        print("2. Defend")
        print("3. Heal")
        choice = input("Enter 1, 2 or 3: ")

        if choice == '1':  # Player attacks enemy
            player.attack_enemy(enemy)
        elif choice == '2':  # Player defends (no damage for this round)
            print(f"{player.name} is defending this turn!")
        elif choice == '3':  # Player heals
            player.heal_player()
        else:
            print("Invalid choice. Please choose 1, 2, or 3.")
            continue

        # Enemy attacks player after player's action
        if enemy.is_alive():
            time.sleep(1)  # Simulate time between actions
            enemy.attack_player(player)

        time.sleep(1)  # Pause between turns

    # Determine winner
    if player.is_alive():
        print(f"\n{player.name} wins the battle!")
    else:
        print(f"\n{player.name} has been defeated. {enemy.name} wins.")
