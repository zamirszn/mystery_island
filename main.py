"""Terminal interface for Mystery Island: The Lost Lighthouse."""

from game import HELP_TEXT, LOCATIONS, apply_action, available_actions, new_game, resolve_choice


TITLE = """
====================================================
       MYSTERY ISLAND: THE LOST LIGHTHOUSE
====================================================
""".strip("\n")


def show_menu(player):
    """Print current status and return the numbered action list."""
    print(f"\n--- {player['location']} | Energy: {player['energy']}/5 ---")
    print(LOCATIONS[player["location"]]["description"])
    actions = available_actions(player)
    for number, action in enumerate(actions, start=1):
        print(f"{number}. {action['label']}  [{action['key']}]")
    return actions


def play_one_game(player):
    """Run menus until the supplied game reaches an ending."""
    print(f"\nThe storm has passed, {player['name']}, but the lighthouse is dark.")
    print("Restore its beacon before you run out of energy.")

    while not player["game_over"]:
        actions = show_menu(player)
        raw_choice = input("\nWhat will you do? ")
        action = resolve_choice(raw_choice, actions)
        if action is None:
            print("Please enter a listed number or command. Nothing changed.")
            continue
        result = apply_action(player, action)
        print(f"\n{result['message']}")


def ask_to_replay():
    """Ask a validated replay question after a win or loss."""
    while True:
        answer = input("\nPlay again? (y/n): ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no", "q", "quit", "exit"}:
            return False
        print("Please enter y or n.")


def main():
    print(TITLE)
    print(HELP_TEXT)
    name = input("\nWhat is your name? ")
    player = new_game(name)

    while True:
        play_one_game(player)
        if player["quit"]:
            break
        if not ask_to_replay():
            print(f"\nThanks for playing, {player['name']}!")
            break
        player = new_game(player["name"])
        print("\nA new storm washes you back onto Mystery Island...")


if __name__ == "__main__":
    main()
