"""
Bot for playing tic tac toe game with multiple CallbackQueryHandlers.
"""
from copy import deepcopy
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

import os

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# get token using BotFather
TOKEN = os.getenv('TG_TOKEN')

CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE = '.'
CROSS = 'X'
ZERO = 'O'


DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


def get_default_state():
    """Helper function to get default state of the game"""
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state: list[list[str]]) -> list[list[InlineKeyboardButton]]:
    """Generate tic tac toe keyboard 3x3 (telegram buttons)"""
    return [
        [
            InlineKeyboardButton(state[r][c], callback_data=f'{r}{c}')
            for r in range(3)
        ]
        for c in range(3)
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    context.user_data['keyboard_state'] = get_default_state()
    keyboard = generate_keyboard(context.user_data['keyboard_state'])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f'X (your) turn! Please, put X to the free place', reply_markup=reply_markup
    )
    return CONTINUE_GAME


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Main processing of the game"""
    # Get the clicked position from the callback data
    clicked_position = update.callback_query.data

    # Extract row and column from the clicked position
    row = int(clicked_position[0])
    column = int(clicked_position[1])

    # Check if the clicked position is not occupied
    if context.user_data['keyboard_state'][row][column] != FREE_SPACE:
        await update.callback_query.answer(text='Invalid move! Please choose a free cell.', show_alert=True)
        return CONTINUE_GAME

    # Update the game state with the user's move
    keyboard_state = context.user_data['keyboard_state']
    keyboard_state[row][column] = CROSS

    # Check if the user has won
    if won(keyboard_state, CROSS):
        await update.callback_query.message.reply_text('Congratulations! You won!')
        return end(update, context)  # End the conversation

    # Check if there are no more empty positions
    if not any(FREE_SPACE in row for row in keyboard_state):
        await update.callback_query.message.reply_text("It's a draw!")
        return end(update, context)  # End the conversation

    # Generate the opponent's move
    opponent_move_row, opponent_move_column = generate_opponent_move(keyboard_state)
    keyboard_state[opponent_move_row][opponent_move_column] = ZERO

    # Check if the opponent has won
    if won(keyboard_state, ZERO):
        await update.callback_query.message.reply_text('Sorry, you lost! Better luck next time.')
        return end(update, context)  # End the conversation

    # Update the game board and send it to the user
    keyboard = generate_keyboard(keyboard_state)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)

    # Check if the game ended in a draw after the opponent's move
    if not any(FREE_SPACE in row for row in keyboard_state):
        await update.callback_query.message.reply_text("It's a draw!")
        return end(update, context)  # End the conversation

    return CONTINUE_GAME


def won(state: list[list[str]], player: str) -> bool:
    """Check if the player has won the game"""
    # Check rows
    for row in state:
        if row[0] == row[1] == row[2] == player:
            return True

    # Check columns
    for col in range(3):
        if state[0][col] == state[1][col] == state[2][col] == player:
            return True

    # Check diagonals
    if state[0][0] == state[1][1] == state[2][2] == player:
        return True
    if state[0][2] == state[1][1] == state[2][0] == player:
        return True

    return False


def generate_opponent_move(state: list[list[str]]) -> tuple[int, int]:
    """Generate a random move for the opponent"""
    import random

    # Find all the empty positions on the board
    empty_positions = []
    for row in range(3):
        for col in range(3):
            if state[row][col] == FREE_SPACE:
                empty_positions.append((row, col))

    # Select a random empty position for the opponent's move
    opponent_move = random.choice(empty_positions)
    return opponent_move


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    # Print the final game board
    final_board = generate_keyboard(context.user_data['keyboard_state'])
    reply_markup = InlineKeyboardMarkup(final_board)
    await update.message.reply_text('Final Game Board:', reply_markup=reply_markup)

    # Reset state to default so you can play again with /start
    context.user_data['keyboard_state'] = get_default_state()
    return ConversationHandler.END


def main() -> None:
    """Run the bot"""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states CONTINUE_GAME and FINISH_GAME
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern='^' + f'{r}{c}' + '$')
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()