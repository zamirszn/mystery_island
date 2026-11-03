"""Pure game rules for Mystery Island: The Lost Lighthouse."""

from copy import deepcopy


MAX_ENERGY = 5
STARTING_ENERGY = 5

LOCATIONS = {
    "Beach": {
        "connections": ["Jungle"],
        "description": (
            "Waves wash over the storm-battered beach. A dark lighthouse stands "
            "beyond the jungle, and a reef glints offshore."
        ),
    },
    "Jungle": {
        "connections": ["Beach", "Cave"],
        "description": (
            "Vines crowd a narrow jungle trail. A coil of rope and a ripe "
            "coconut lie near an old supply crate."
        ),
    },
    "Cave": {
        "connections": ["Jungle", "Old Bridge"],
        "description": (
            "A sheltered cave holds a lantern. The embers of a campfire still "
            "give off a little warmth."
        ),
    },
    "Old Bridge": {
        "connections": ["Cave", "Lighthouse"],
        "description": (
            "A broken bridge crosses a deep ravine. It can be made safe with "
            "a strong rope."
        ),
    },
    "Lighthouse": {
        "connections": ["Old Bridge"],
        "description": (
            "The lighthouse lantern room is cold and dark. The beacon waits "
            "to be relit."
        ),
    },
}

HELP_TEXT = (
    "Choose an action by entering its number or a shown command. Legal moves "
    "cost 1 energy. Reef swimming costs 2. Other actions are free. Collect "
    "the rope and lantern, cross the bridge, and light the beacon before your "
    "energy reaches 0. Use inventory, look, help, or q at any menu."
)


def new_game(name):
    """Return an independent, fresh player state."""
    clean_name = str(name).strip() if name is not None else ""
    return {
        "name": clean_name or "Explorer",
        "location": "Beach",
        "energy": STARTING_ENERGY,
        "inventory": [],
        "flags": {
            "coconut_eaten": False,
            "rested": False,
        },
        "game_over": False,
        "won": False,
        "quit": False,
    }


def can_cross_bridge(player):
    """Return whether the player has the rope needed for the bridge."""
    return "rope" in player["inventory"]


def can_light_beacon(player):
    """Return whether the player is in position to light the beacon."""
    return (
        player["location"] == "Lighthouse"
        and "lantern" in player["inventory"]
        and player["energy"] > 0
    )


def is_win(player):
    """Return whether the game has ended in victory."""
    return player["game_over"] and player["won"]


def is_loss(player):
    """Return whether energy exhaustion has ended the game."""
    return player["energy"] == 0 and not player["won"]


def available_actions(player):
    """Return menu-ready actions for the player's current state."""
    if player["game_over"]:
        return []

    location = player["location"]
    actions = [
        {
            "key": f"move:{destination.lower()}",
            "label": f"Go to {destination}",
            "aliases": [destination.lower(), f"go {destination.lower()}"],
        }
        for destination in LOCATIONS[location]["connections"]
    ]

    if location == "Jungle" and "rope" not in player["inventory"]:
        actions.append(
            {"key": "take:rope", "label": "Pick up the rope", "aliases": ["rope", "take rope"]}
        )
    if location == "Cave" and "lantern" not in player["inventory"]:
        actions.append(
            {
                "key": "take:lantern",
                "label": "Pick up the lantern",
                "aliases": ["lantern", "take lantern"],
            }
        )
    if location == "Jungle" and not player["flags"]["coconut_eaten"]:
        actions.append(
            {"key": "coconut", "label": "Eat the coconut", "aliases": ["eat coconut"]}
        )
    if location == "Cave" and not player["flags"]["rested"]:
        actions.append(
            {"key": "rest", "label": "Rest by the campfire", "aliases": ["campfire"]}
        )
    if location == "Beach":
        actions.append(
            {"key": "reef", "label": "Swim out to the reef", "aliases": ["swim", "swim reef"]}
        )
    if location == "Lighthouse":
        actions.append(
            {"key": "light", "label": "Light the beacon", "aliases": ["beacon", "light beacon"]}
        )

    actions.extend(
        [
            {"key": "look", "label": "Look around", "aliases": ["l", "look around"]},
            {"key": "inventory", "label": "Show inventory and energy", "aliases": ["i", "inv", "status"]},
            {"key": "help", "label": "Show help", "aliases": ["h", "?"]},
            {"key": "quit", "label": "Quit", "aliases": ["q", "exit"]},
        ]
    )
    return actions


def resolve_choice(raw_choice, actions):
    """Convert a menu number or word command to an action key."""
    choice = str(raw_choice).strip().lower()
    if not choice:
        return None

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(actions):
            return actions[index]["key"]
        return None

    for action in actions:
        accepted = [action["key"], *action.get("aliases", [])]
        if choice in accepted:
            return action["key"]
    return None


def apply_action(player, action):
    """Validate and apply one action, returning an ok flag and message."""
    if player["game_over"]:
        return _result(False, "The game is already over. Start a new game to continue.")

    normalized = str(action).strip().lower()
    normalized = {
        "q": "quit",
        "exit": "quit",
        "inv": "inventory",
        "i": "inventory",
        "h": "help",
        "?": "help",
        "l": "look",
        "light beacon": "light",
        "eat coconut": "coconut",
        "campfire": "rest",
        "swim": "reef",
        "swim reef": "reef",
    }.get(normalized, normalized)

    if normalized == "quit":
        player["game_over"] = True
        player["quit"] = True
        return _result(True, f"Goodbye, {player['name']}. The island will be waiting.")
    if normalized == "inventory":
        items = ", ".join(player["inventory"]) if player["inventory"] else "empty"
        return _result(True, f"Inventory: {items}. Energy: {player['energy']}/{MAX_ENERGY}.")
    if normalized == "help":
        return _result(True, HELP_TEXT)
    if normalized == "look":
        return _result(True, LOCATIONS[player["location"]]["description"])
    if normalized.startswith("move:"):
        return _move(player, normalized.split(":", 1)[1])
    if normalized.startswith("take:"):
        return _take_item(player, normalized.split(":", 1)[1])
    if normalized == "coconut":
        return _eat_coconut(player)
    if normalized == "rest":
        return _rest(player)
    if normalized == "reef":
        return _swim_reef(player)
    if normalized == "light":
        return _light_beacon(player)
    return _result(False, "That action is not available. Choose one of the listed options.")


def _move(player, destination_text):
    destination = _location_named(destination_text)
    current = player["location"]
    if destination is None or destination not in LOCATIONS[current]["connections"]:
        return _result(False, "You cannot go there from here. No energy was used.")
    if current == "Old Bridge" and destination == "Lighthouse" and not can_cross_bridge(player):
        return _result(False, "The bridge is unsafe. Find a rope before crossing.")

    player["location"] = destination
    player["energy"] = max(0, player["energy"] - 1)
    if player["energy"] == 0:
        player["game_over"] = True
        return _result(
            True,
            f"You reach {destination}, but your last strength is gone. The beacon stays dark. You lose.",
        )
    return _result(True, f"You travel to {destination}. Energy: {player['energy']}/{MAX_ENERGY}.")


def _take_item(player, item):
    item_locations = {"rope": "Jungle", "lantern": "Cave"}
    if item not in item_locations:
        return _result(False, "There is no such item to collect.")
    if item in player["inventory"]:
        return _result(False, f"You already have the {item}.")
    if player["location"] != item_locations[item]:
        return _result(False, f"The {item} is not here.")
    player["inventory"].append(item)
    return _result(True, f"You pick up the {item}.")


def _eat_coconut(player):
    if player["location"] != "Jungle":
        return _result(False, "There is no coconut here.")
    if player["flags"]["coconut_eaten"]:
        return _result(False, "You already ate the coconut.")
    before = player["energy"]
    player["energy"] = min(MAX_ENERGY, player["energy"] + 2)
    player["flags"]["coconut_eaten"] = True
    gained = player["energy"] - before
    return _result(True, f"The coconut restores {gained} energy. Energy: {player['energy']}/{MAX_ENERGY}.")


def _rest(player):
    if player["location"] != "Cave":
        return _result(False, "There is no campfire here.")
    if player["flags"]["rested"]:
        return _result(False, "You have already rested by the campfire.")
    before = player["energy"]
    player["energy"] = min(MAX_ENERGY, player["energy"] + 1)
    player["flags"]["rested"] = True
    gained = player["energy"] - before
    return _result(True, f"A short rest restores {gained} energy. Energy: {player['energy']}/{MAX_ENERGY}.")


def _swim_reef(player):
    if player["location"] != "Beach":
        return _result(False, "You can only swim to the reef from the Beach.")
    player["energy"] = max(0, player["energy"] - 2)
    if player["energy"] == 0:
        player["game_over"] = True
        return _result(True, "The reef holds nothing. You return exhausted, and the beacon stays dark. You lose.")
    return _result(
        True,
        f"You fight the current to the reef, find nothing, and return. Energy: {player['energy']}/{MAX_ENERGY}.",
    )


def _light_beacon(player):
    if player["location"] != "Lighthouse":
        return _result(False, "You must reach the Lighthouse before you can light the beacon.")
    if "lantern" not in player["inventory"]:
        return _result(False, "The beacon is cold and dark. Find a lantern to ignite it.")
    if not can_light_beacon(player):
        return _result(False, "You are too exhausted to light the beacon.")
    player["won"] = True
    player["game_over"] = True
    return _result(
        True,
        f"{player['name']} lights the beacon! Its beam sweeps the sea, and the rescue boat arrives. You win!",
    )


def _location_named(text):
    normalized = text.strip().lower()
    for location in LOCATIONS:
        if location.lower() == normalized:
            return location
    return None


def _result(ok, message):
    return {"ok": ok, "message": message}


def state_snapshot(player):
    """Return a deep copy useful for checking that invalid actions changed nothing."""
    return deepcopy(player)
