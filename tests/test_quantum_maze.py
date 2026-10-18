import unittest

import pygame

from pocket_games.games.quantum_maze import QuantumMazeGame


class MockEngine:
    def __init__(self):
        class MockInput:
            def is_key_down(self, key):
                return False

        self.input = MockInput()


class TestQuantumMaze(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.engine = MockEngine()

    def tearDown(self):
        pygame.quit()

    def test_maze_generation_no_index_error(self):
        """Test that initializing and generating mazes across different grid sizes does not raise IndexError."""
        game = QuantumMazeGame(self.engine)

        # Verify initial walls are successfully generated
        self.assertGreater(len(game.walls), 0)

        # Test escalating grid sizes up to higher complexity levels
        for _ in range(6):
            game.grid_cols += 1
            game.grid_rows += 1
            try:
                game._generate_maze()
            except IndexError as e:
                self.fail(
                    f"IndexError raised during maze generation with grid {game.grid_cols}x{game.grid_rows}: {e}"
                )

            # Ensure walls and cores are populated correctly
            self.assertGreater(len(game.walls), 0)
            self.assertEqual(len(game.cores), 1)


if __name__ == "__main__":
    unittest.main()
