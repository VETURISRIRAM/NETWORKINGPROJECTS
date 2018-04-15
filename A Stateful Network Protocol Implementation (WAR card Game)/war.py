"""
war card game client and server
"""
import asyncio
from collections import namedtuple
from enum import Enum
import logging
from random import shuffle
import sys


pairedplayers = list()

"""
Namedtuples work like classes, but are much more lightweight so they end
up being faster. It would be a good idea to keep objects in each of these
for each game which contain the game's state, for instance things like the
socket, the cards given, the cards still available, etc.
"""
Game = namedtuple("Game", ["p1", "p2"])


class Command(Enum):
    """
    The byte values sent as the first byte of any message in the war protocol.
    """
    WANTGAME = 0
    GAMESTART = 1
    PLAYCARD = 2
    PLAYRESULT = 3


class Result(Enum):
    """
    The byte values sent as the payload byte of a PLAYRESULT message.
    """
    WIN = 0
    DRAW = 1
    LOSE = 2


def readexactly(sock, numbytes):
    """
    Accumulate exactly `numbytes` from `sock` and return those. If EOF is found
    before numbytes have been received, be sure to account for that here or in
    the caller.
    """

    response = b'' # The response is always a bytestream

    while len(response) != numbytes: # Accumulating exactly 'numbytes'

        recieved_data = sock.recv(1) # Recieving the response
        response = response + recieved_data

        # Checking for EOF
        if len(recieved_data) == 0 and len(response) != numbytes:
            print('ERROR! End of File Detected')
            sock.close() # If EOF detected, close the connection
            return

    return response

# Function to end the game in case of any errors
def kill_game(player1, player2):
    # Close the connections
    player1.close()
    player2.close()
    
# Function to compare the cards of the players
def compare_cards(player1_card, player2_card):
    # Mod 13 would give us the value to be compared
    P1 = player1_card % 13
    P2 = player2_card % 13

    if P1 < P2:  # Player 2 wins
        return 2

    if P1 == P2:  # Draw
        return 1

    if P1 > P2:  # Player 1 wins
        return 0

# Function to deal the cards to the players
def deal_cards():
    cards_deck = []
    i = 0

    while len(cards_deck) != 52:  # Initializing the deck
        cards_deck.append(i)
        i = i + 1

    shuffle(cards_deck)  # Shuffle the deck before dealing

    hand1 = []
    hand2 = []

    while len(hand1) < 26:  # Dealing cards to Player 1
        temp1 = cards_deck.pop()
        hand1.append(temp1)

    while len(hand2) < 26:  # Dealing cards to Player 2
        temp2 = cards_deck.pop()
        hand2.append(temp2)

    playing_cards = [hand1, hand2]
    return playing_cards  # Returning both the players' decks

# Function to check if the card is used or not
def card_in_deck(used_card, dealt_deck):
    if used_card in dealt_deck:  # Check if the card is in deck
        return True
    else:
        return False

# Function to execute the game between players
async def game_execution(first_player, second_player):  # Function
    # Dealing the shuffled cards equally to both the players
    cards_distribute = deal_cards()

    p1_cards = cards_distribute[0]
    p2_cards = cards_distribute[1]
    p1_played = [False] * 26
    p2_played = [False] * 26

    print("\nDeck is split as follows:")
    print("\nPlayer 1 Deck:", p1_cards)
    print("Player 2 Deck:", p2_cards)
    turns = 0
    try:
        # The connected players send the 00 to indicate they WANTGAME
        # first_player and second_player contains the connection information
        first_player_data = await first_player[0].readexactly(2)
        print("\nFist Player sent   :", first_player_data)
        second_player_data = await second_player[0].readexactly(2)
        print("Second Player sent :", second_player_data)

        # Server sends the indication of GAMESTART and the dealt deck to connected players
        first_player[1].write(bytes(([Command.GAMESTART.value] + p1_cards)))
        second_player[1].write(bytes(([Command.GAMESTART.value] + p2_cards)))

        while turns < 26:  # The game should be executed 26 times

            print("\nTurn Count : ", turns + 1)

            # Players send their cards and it is stored in player_data variables
            first_player_data = await first_player[0].readexactly(2)
            print("\nFirst Player plays the following card  :", first_player_data)
            second_player_data = await second_player[0].readexactly(2)
            print("Second player plays the following card :", second_player_data)

            # Display error if the users don't push 2 as "PLAYCARD"
            # player_data[0] should contain 2, indicating they want to PLAYGAME
            if first_player_data[0] != 2 and second_player_data[0] != 2:
                print("\nERROR!! The user/users need to enter 2(PLAYCARD)")
                kill_game(first_player[1], second_player[1])
                kill_game(first_player[1].get_extra_info('socket'),
                          second_player[1].get_extra_info('socket'))
                return
            else:
                print("\nThe players entered 2(PLAYCARD)")

            # Display error if the card are not found in the initially dealt deck
            # player_data[1] should contain the individual cards from players
            if (card_in_deck(first_player_data[1], cards_distribute[0]) is False) or\
               (card_in_deck(second_player_data[1], cards_distribute[1]) is False):
                print("\nERROR!! The player's/players' cards were not dealt")
                kill_game(first_player[1], second_player[1])
                kill_game(first_player[1].get_extra_info('socket'),
                          second_player[1].get_extra_info('socket'))
                return

            x = 0
            # Display error if the used card is used again
            while x < 26:
                if first_player_data[1] == p1_cards[x]:

                    if p1_played[x] is False:
                        p1_played[x] = True
                    else:
                        print("\nERROR!! The player/players played the already used card")
                        kill_game(first_player[1], second_player[1])
                        kill_game(first_player[1].get_extra_info('socket'),
                                  second_player[1].get_extra_info('socket'))
                        return

                if second_player_data[1] == p2_cards[x]:

                    if p2_played[x] is False:
                        p2_played[x] = True
                    else:
                        print("\nERROR!! The player/players played the already used card")
                        kill_game(first_player[1], second_player[1])
                        kill_game(first_player[1].get_extra_info('socket'),
                                  second_player[1].get_extra_info('socket'))
                        return
                x = x + 1

            # The cards are compared to get the results
            player1_result = compare_cards(first_player_data[1], second_player_data[1])
            player2_result = compare_cards(second_player_data[1], first_player_data[1])

            # PLAYRESULT and results can't be sent directly
            player1_send_result = [Command.PLAYRESULT.value, player1_result]
            player2_send_result = [Command.PLAYRESULT.value, player2_result]

            # Server now sends the individual results to the players.
            first_player[1].write(bytes(player1_send_result))
            second_player[1].write(bytes(player2_send_result))

            turns = turns + 1

        print("\nResult of the game sent to the players!!")

        # At the end, terminate all the connections.
        kill_game(first_player[1], second_player[1])
        kill_game(first_player[1].get_extra_info('socket'),
                  second_player[1].get_extra_info('socket'))
    # Exceptions to be handled
    except ConnectionResetError:
        logging.error("ConnectionResetError")
        return 0
    except asyncio.streams.IncompleteReadError:
        logging.error("asyncio.streams.IncompleteReadError")
        return 0
    except OSError:
        logging.error("OSError")
        return 0

# Function to pair the incoming players' connections
async def pairing_players(reader, writer):  # Function

    print("Incoming client connection!")  # Connections counter
    # This function waits for the second player to connect to the server
    # players[0] and players[1] are the players connected
    for players in pairedplayers:

        # If second player is not connected, wait for its connection before starting the game
        if players[1] is None:
            players[1] = (reader, writer)

            # After establishing connection, play the game!
            await game_execution(players[0], players[1])

            # After playing game, remove players from pairedplayers list.
            pairedplayers.remove(players)
            return

    # Accept connection from first player again
    pairedplayers.append([(reader, writer), None])


def serve_game(host, port):
    print("Server Implementation!!")

    # Get an event loop
    my_event_loop = asyncio.get_event_loop()

    # Coroutine to start the server
    my_coroutine = asyncio.start_server(pairing_players, host, port, loop=my_event_loop)

    # This event loop would run until the future(my_coroutine)
    my_server = my_event_loop.run_until_complete(my_coroutine)

    # Server listening for players' connections
    print('Server is serving on {}\n'.format(my_server.sockets[0].getsockname()))

    # Exit when Ctrl + c is detected
    try:
        my_event_loop.run_forever()
    except KeyboardInterrupt:
        print("Exit!! Keyboard Interrupt Detected.")

    # Close the server
    my_server.close()
    my_event_loop.run_until_complete(my_server.wait_closed())

    # Close the get event loop
    my_event_loop.close()

async def limit_client(host, port, loop, sem):
    async with sem:
        return await client(host, port, loop)


async def client(host, port, loop):
    try:

        reader, writer = await asyncio.open_connection(host, port, loop=loop)
        # send want game
        myscore = 0

        writer.write(b"\0\0")
        card_msg = await reader.readexactly(27)

        for card in card_msg[1:]:

            writer.write(bytes([Command.PLAYCARD.value, card]))
            result = await reader.readexactly(2)

            if result[1] == Result.WIN.value:
                myscore += 1
            elif result[1] == Result.LOSE.value:
                myscore -= 1
        if myscore > 0:
            result = "won"
        elif myscore < 0:
            result = "lost"
        else:
            result = "drew"

        print("Result: ", result)
        logging.debug("Game complete, I %s", result)
        writer.close()
        return 1
    except ConnectionResetError:
        logging.error("ConnectionResetError")
        return 0
    except asyncio.streams.IncompleteReadError:
        logging.error("asyncio.streams.IncompleteReadError")
        return 0
    except OSError:
        logging.error("OSError")
        return 0


def main(args):
    """
    launch a client/server
    """
    host = args[1]
    port = int(args[2])
    if args[0] == "server":
        try:
            serve_game(host, port)
        except KeyboardInterrupt:
            pass
        return
    else:
        loop = asyncio.get_event_loop()

    if args[0] == "client":
        loop.run_until_complete(client(host, port, loop))
    elif args[0] == "clients":
        sem = asyncio.Semaphore(1000)
        num_clients = int(args[3])
        clients = [limit_client(host, port, loop, sem)
                   for x in range(num_clients)]
        async def run_all_clients():
            """
            use `as_completed` to spawn all clients simultaneously
            and collect their results in arbitrary order.
            """
            completed_clients = 0
            for client_result in asyncio.as_completed(clients):
                completed_clients += await client_result
            return completed_clients
        res = loop.run_until_complete(
            asyncio.Task(run_all_clients(), loop=loop))
        logging.info("%d completed clients", res)

    loop.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main(sys.argv[1:])
