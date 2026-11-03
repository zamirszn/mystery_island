# Mystery Island: The Lost Lighthouse

A deterministic, single-player Python text adventure. You wake on an island after a storm and must restore the lighthouse beacon before your energy runs out.

## Prerequisites and running

- Python 3.10 or newer
- No third-party packages

Start the game from this directory:

```bash
python main.py
```

On systems where Python is exposed as `python3` instead, run `python3 main.py`.

Enter a displayed number or command. Commands ignore case and surrounding spaces. `q`, `quit`, or `exit` ends the game immediately.

## Map and rules

```text
Beach <-> Jungle <-> Cave <-> Old Bridge <-> Lighthouse
```

- You begin at the Beach with 5 energy and an empty inventory.
- Every legal move costs 1 energy. Invalid or blocked actions cost nothing.
- Energy never exceeds 5 or falls below 0. Reaching 0 ends the game immediately, including on the final move to a location.
- The Jungle contains a rope. You need it to cross from the Old Bridge to the Lighthouse.
- The Cave contains a lantern. You need it to light the beacon.
- Items, looking, inventory, help, the coconut, resting, and lighting the beacon do not cost energy.
- The Jungle coconut restores 2 energy once, capped at 5.
- Resting at the Cave campfire restores 1 energy once, capped at 5.
- Swimming to the reef from the Beach costs 2 energy, finds nothing, and returns you to the Beach. It may be repeated.
- Win by lighting the beacon at the Lighthouse with the lantern and energy remaining.
- After a win or loss, replay creates a completely fresh state. Quitting exits immediately without asking to replay.

The interface accepts both numbered choices and word commands such as `jungle`, `take rope`, `inventory`, and `light beacon`.

## Example successful run

One winning sequence is:

```text
jungle
take rope
eat coconut
cave
take lantern
rest
old bridge
lighthouse
light beacon
```

The coconut and campfire provide enough spare energy to explore. A quick losing path is `swim`, `swim`, then `jungle`.

## Tests

Run the complete suite with:

```bash
python -m unittest discover -s tests -v
```

Use `python3 -m unittest discover -s tests -v` when your system does not provide the `python` alias.

The tests cover fresh state, input normalization, movement costs, blocked movement, one-time items and decisions, both item gates, energy limits, win/loss outcomes, replay isolation, quitting, and post-game immutability.

## Acceptance checklist

| Requirement | Status | Evidence |
| --- | --- | --- |
| Title, instructions, and player name | Pass | `main()` prints the title/help and calls `new_game(name)` |
| Repeating menu until win, loss, or quit | Pass | `play_one_game()` loops while `game_over` is false |
| Five required locations | Pass | `LOCATIONS` contains Beach, Jungle, Cave, Old Bridge, and Lighthouse |
| Energy, location, and inventory | Pass | All are stored in the player dictionary |
| Two one-time useful objects | Pass | Rope and lantern pickups reject duplicates |
| Three consequential decisions | Pass | Coconut restores energy, campfire rest restores energy, and reef swimming costs energy |
| Inventory gates | Pass | Rope gates the bridge and lantern gates the beacon |
| Invalid input recovery | Pass | `resolve_choice()` rejects invalid input without changing player state |
| Clear outcomes and replay | Pass | Win/loss messages are returned and replay calls `new_game()` |
| Automated acceptance tests | Pass | 23 `unittest` tests cover all T1–T10 rules and bug-hunter cases |

## Function guide

The code is split so terminal input/output and game decisions have separate jobs:

- `new_game()` builds a fresh player dictionary, inventory list, and flags dictionary.
- `available_actions()` creates the choices appropriate for the current location.
- `resolve_choice()` normalizes a number or word typed by the player into an action key.
- `apply_action()` routes a validated action to the matching rule.
- `can_cross_bridge()` and `can_light_beacon()` return booleans for the two item gates.
- `is_win()` and `is_loss()` report the current outcome without printing anything.
- `_move()`, `_take_item()`, `_eat_coconut()`, `_rest()`, `_swim_reef()`, and `_light_beacon()` each apply one game rule.
- `_location_named()` performs a case-insensitive location lookup, while `_result()` creates consistent action results.
- `state_snapshot()` makes an independent copy used to prove rejected actions changed nothing.
- `show_menu()` prints the current scene and numbered choices.
- `play_one_game()` owns the main `while` loop and stops when `game_over` becomes true.
- `ask_to_replay()` accepts only yes/no replay input.
- `main()` starts the program and creates a new state for each replay.

## Project structure

- `main.py` owns terminal input, output, menus, and replay.
- `game.py` owns deterministic game state and rules and never calls `input()`.
- `tests/test_game.py` tests the game logic without terminal interaction.

## Design decisions

- The final move that reduces energy to 0 causes a loss, even if it reaches the Lighthouse.
- Quit exits without a replay prompt.
- The default 5-energy budget is unchanged.
- Numbers and word commands are both supported.
- Choices are deterministic; the game has no random events or save files.

## Known limitations

- Progress cannot be saved between runs.
- The story has one ending and a linear five-location map.
- Terminal text is English-only and has no sound or graphics.

## Learning log

1. **State isolation** → A new game must create new nested lists and dictionaries → Created two games, changed one inventory, and asserted the other remained empty → Fresh mutable objects prevent replay data from leaking between games.
2. **Validate before mutation** → Rejected actions should leave every state field unchanged → Took deep snapshots before invalid and blocked actions in tests → Checking requirements first makes failures safe and predictable.

The concept I understand now that I did not before is that separating pure game rules from `input()` and `print()` makes each rule reproducible and easy to test with a specific state.

## Real-world connection

This project is a small state machine, the same pattern used by onboarding flows, troubleshooting assistants, interactive training scenarios, and order-status systems. The player dictionary is the current state, the menu offers valid transitions, `apply_action()` enforces business rules, and the tests prove invalid transitions do not corrupt the state. For example, a safety-training simulator could replace locations with training stages, inventory with completed certifications, energy with an attempt limit, and the locked bridge with a stage that cannot open until required training is complete.
