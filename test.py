import unittest
from main import won, generate_opponent_move, get_default_state

class TicTacToeTests(unittest.TestCase):
    def setUp(self):
        self.state = get_default_state()

    def test_winning_rows(self):
        # Test horizontal winning rows
        self.state[0] = ['X', 'X', 'X']
        self.assertTrue(won(self.state, 'X'))

        self.state[1] = ['O', 'O', 'O']
        self.assertTrue(won(self.state, 'O'))

        self.state[2] = ['X', 'X', 'X']
        self.assertTrue(won(self.state, 'X'))

    def test_winning_columns(self):
        # Test vertical winning columns
        self.state = [
            ['X', 'O', 'X'],
            ['X', 'O', 'O'],
            ['X', 'X', 'X']
        ]
        self.assertTrue(won(self.state, 'X'))
        self.assertFalse(won(self.state, 'O'))

    def test_winning_diagonals(self):
        # Test winning diagonals
        self.state = [
            ['O', 'X', 'X'],
            ['X', 'O', 'O'],
            ['X', 'X', 'O']
        ]
        self.assertTrue(won(self.state, 'O'))
        self.assertFalse(won(self.state, 'X'))

        self.state = [
            ['X', 'X', 'O'],
            ['X', 'O', 'O'],
            ['O', 'X', 'X']
        ]
        self.assertTrue(won(self.state, 'O'))
        self.assertFalse(won(self.state, 'X'))

    def test_generate_opponent_move(self):
        # Test generating opponent move
        self.state = [
            ['X', '.', 'X'],
            ['O', 'O', 'X'],
            ['X', 'O', 'O']
        ]
        opponent_move = generate_opponent_move(self.state)
        self.assertEqual(opponent_move, (0, 1))

if __name__ == '__main__':
    unittest.main()