import unittest

from game import (
    MAX_ENERGY,
    apply_action,
    available_actions,
    can_light_beacon,
    is_loss,
    is_win,
    new_game,
    resolve_choice,
    state_snapshot,
)


class MysteryIslandTests(unittest.TestCase):
    def test_new_game_has_fresh_starting_state(self):
        player = new_game("Ada")
        self.assertEqual("Beach", player["location"])
        self.assertEqual(5, player["energy"])
        self.assertEqual([], player["inventory"])

    def test_blank_name_uses_default(self):
        self.assertEqual("Explorer", new_game("   ")["name"])

    def test_invalid_command_leaves_state_unchanged(self):
        player = new_game("Ada")
        before = state_snapshot(player)
        result = apply_action(player, "banana")
        self.assertFalse(result["ok"])
        self.assertEqual(before, player)

    def test_legal_move_costs_one_energy(self):
        player = new_game("Ada")
        result = apply_action(player, "move:jungle")
        self.assertTrue(result["ok"])
        self.assertEqual("Jungle", player["location"])
        self.assertEqual(4, player["energy"])

    def test_wrong_direction_is_free(self):
        player = new_game("Ada")
        before = state_snapshot(player)
        result = apply_action(player, "move:cave")
        self.assertFalse(result["ok"])
        self.assertEqual(before, player)

    def test_rope_can_only_be_collected_once(self):
        player = new_game("Ada")
        apply_action(player, "move:jungle")
        self.assertTrue(apply_action(player, "take:rope")["ok"])
        self.assertFalse(apply_action(player, "take:rope")["ok"])
        self.assertEqual(["rope"], player["inventory"])

    def test_bridge_is_blocked_without_rope_and_costs_nothing(self):
        player = new_game("Ada")
        apply_action(player, "move:jungle")
        apply_action(player, "move:cave")
        apply_action(player, "move:old bridge")
        before = state_snapshot(player)
        result = apply_action(player, "move:lighthouse")
        self.assertFalse(result["ok"])
        self.assertEqual(before, player)

    def test_beacon_is_blocked_without_lantern(self):
        player = self._player_at_lighthouse(with_lantern=False)
        before = state_snapshot(player)
        result = apply_action(player, "light")
        self.assertFalse(result["ok"])
        self.assertEqual(before, player)

    def test_correct_inventory_and_location_win(self):
        player = self._player_at_lighthouse(with_lantern=True)
        result = apply_action(player, "light beacon")
        self.assertTrue(result["ok"])
        self.assertTrue(is_win(player))
        self.assertIn("Ada", result["message"])

    def test_energy_exhaustion_causes_loss(self):
        player = new_game("Ada")
        apply_action(player, "reef")
        apply_action(player, "reef")
        apply_action(player, "move:jungle")
        self.assertTrue(is_loss(player))
        self.assertTrue(player["game_over"])
        self.assertEqual(0, player["energy"])

    def test_replay_state_is_independent_and_fresh(self):
        old_player = new_game("Ada")
        apply_action(old_player, "move:jungle")
        apply_action(old_player, "take:rope")
        new_player = new_game("Ada")
        self.assertEqual("Beach", new_player["location"])
        self.assertEqual(5, new_player["energy"])
        self.assertEqual([], new_player["inventory"])
        self.assertIsNot(old_player["inventory"], new_player["inventory"])
        self.assertIsNot(old_player["flags"], new_player["flags"])

    def test_exit_with_case_and_spaces_quits(self):
        player = new_game("Ada")
        result = apply_action(player, "  EXIT  ")
        self.assertTrue(result["ok"])
        self.assertTrue(player["quit"])
        self.assertTrue(player["game_over"])

    def test_energy_never_falls_below_zero(self):
        player = new_game("Ada")
        apply_action(player, "reef")
        apply_action(player, "reef")
        apply_action(player, "reef")
        self.assertEqual(0, player["energy"])

    def test_lantern_can_only_be_collected_once(self):
        player = new_game("Ada")
        apply_action(player, "move:jungle")
        apply_action(player, "move:cave")
        self.assertTrue(apply_action(player, "take:lantern")["ok"])
        self.assertFalse(apply_action(player, "take:lantern")["ok"])
        self.assertEqual(["lantern"], player["inventory"])

    def test_player_cannot_light_beacon_elsewhere(self):
        player = new_game("Ada")
        player["inventory"].append("lantern")
        self.assertFalse(can_light_beacon(player))
        self.assertFalse(apply_action(player, "light")["ok"])

    def test_actions_do_nothing_after_game_over(self):
        player = new_game("Ada")
        apply_action(player, "quit")
        before = state_snapshot(player)
        self.assertFalse(apply_action(player, "move:jungle")["ok"])
        self.assertEqual(before, player)

    def test_coconut_caps_energy_and_only_works_once(self):
        player = new_game("Ada")
        apply_action(player, "move:jungle")
        self.assertTrue(apply_action(player, "coconut")["ok"])
        self.assertEqual(MAX_ENERGY, player["energy"])
        before = state_snapshot(player)
        self.assertFalse(apply_action(player, "coconut")["ok"])
        self.assertEqual(before, player)

    def test_rest_restores_one_and_only_works_once(self):
        player = new_game("Ada")
        apply_action(player, "move:jungle")
        apply_action(player, "move:cave")
        self.assertEqual(3, player["energy"])
        self.assertTrue(apply_action(player, "rest")["ok"])
        self.assertEqual(4, player["energy"])
        self.assertFalse(apply_action(player, "rest")["ok"])

    def test_choice_parser_accepts_numbers_words_and_rejects_bad_input(self):
        player = new_game("Ada")
        actions = available_actions(player)
        self.assertEqual("move:jungle", resolve_choice(" 1 ", actions))
        self.assertEqual("move:jungle", resolve_choice("JUNGLE", actions))
        self.assertEqual("quit", resolve_choice(" EXIT ", actions))
        self.assertIsNone(resolve_choice("", actions))
        self.assertIsNone(resolve_choice("banana", actions))
        self.assertIsNone(resolve_choice("99", actions))

    def test_complete_documented_winning_path(self):
        player = new_game("Ada")
        for action in (
            "move:jungle",
            "take:rope",
            "coconut",
            "move:cave",
            "take:lantern",
            "rest",
            "move:old bridge",
            "move:lighthouse",
            "light",
        ):
            result = apply_action(player, action)
            self.assertTrue(result["ok"], result["message"])
        self.assertTrue(is_win(player))
        self.assertEqual(3, player["energy"])

    def _player_at_lighthouse(self, with_lantern):
        player = new_game("Ada")
        player["location"] = "Lighthouse"
        player["energy"] = 2
        player["inventory"].append("rope")
        if with_lantern:
            player["inventory"].append("lantern")
        return player


if __name__ == "__main__":
    unittest.main()
