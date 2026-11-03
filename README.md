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
