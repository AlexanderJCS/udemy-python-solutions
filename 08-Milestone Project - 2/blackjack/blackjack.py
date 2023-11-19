import random


class Card:
    SUITS = ("Spades", "Hearts", "Diamonds", "Clubs")
    RANKS: dict[str, int | tuple] = {
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
        "Six": 6,
        "Seven": 7,
        "Eight": 8,
        "Nine": 9,
        "Ten": 10,
        "Jack": 10,
        "Queen": 10,
        "King": 10,
        "Ace": (1, 11)
    }

    def __init__(self, rank, suit):
        if rank not in Card.RANKS.keys() or suit not in Card.SUITS:
            raise ValueError("The card rank and suit must be within the keys of Card.RANKS and within Card.SUITS")

        self.rank = rank
        self.suit = suit
        self.face_up = True

    def get_value(self) -> int | tuple:
        """
        :return: An int of the card value or a tuple of possible card values
        """

        return Card.RANKS[self.rank]

    def __str__(self):
        return f"{self.rank} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = []

        for rank in Card.RANKS:
            for suit in Card.SUITS:
                self.cards.append(Card(rank, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def get_card(self):
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)


class Participant:
    def __init__(self, deck: Deck):
        self.cards = []
        self.deck: Deck = deck

    def get_cards_value(self) -> int:
        total_value = 0
        optional_values = []  # card values that may be multiple numbers (example: ace can be 1 or 11)

        for card in self.cards:
            card_value = card.get_value()

            if type(card_value) == int:
                total_value += card_value
            elif type(card_value) == tuple:
                optional_values.append(card_value)

        # Add optional card values
        for optional_value in optional_values:
            total_value += min(*optional_value)

        # Optimize the optional values by adding the higher value whenever possible
        # This algorithm assumes that the higher optional value will always be the same, which is the case in Blackjack.
        # Otherwise, it may not provide the most optimal result
        for optional_value in optional_values:
            add_value = max(*optional_value) - min(*optional_value)

            if add_value + total_value <= 21:
                total_value += add_value

            else:
                break

        return total_value

    def print_cards(self):
        hidden_cards = 0

        for card in self.cards:
            if card.face_up:
                print(f"  - {card}")
            else:
                hidden_cards += 1

        if hidden_cards > 0:
            print(f"  - {hidden_cards} hidden cards")

    def busted(self) -> bool:
        """
        :return: True if the participant busted (i.e., is over 21), otherwise false
        """

        return self.get_cards_value() > 21


class Dealer(Participant):
    def __init__(self, deck: Deck):
        super().__init__(deck)

        self.cards.append(deck.get_card())
        self.cards.append(deck.get_card())

        self.cards[-1].face_up = False

    def print_cards_more_info(self):
        print("Current cards:")
        self.print_cards()
        print(f"Cards value: {self.get_cards_value()}")

    def play(self, score_to_beat: int):
        for card in self.cards:
            card.face_up = True

        self.print_cards_more_info()

        while self.get_cards_value() < score_to_beat:
            self.cards.append(self.deck.get_card())
            print(f"Drawing a {self.cards[-1]}...")

            self.print_cards_more_info()

class Player(Participant):
    def __init__(self, deck: Deck):
        super().__init__(deck)

        self.cards.append(deck.get_card())
        self.cards.append(deck.get_card())

    @staticmethod
    def hit_or_stand():
        hit_or_stand = input("Hit or stand? ").lower()

        while hit_or_stand not in ("hit", "stand"):
            print("Please enter either \"hit\" or \"stand\"")
            hit_or_stand = input("Hit or stand? ")

        return hit_or_stand

    def play(self):
        print("Your cards:")
        self.print_cards()

        print(f"Cards value: {self.get_cards_value()}")

        while self.hit_or_stand() == "hit":
            received_card = self.deck.get_card()
            self.cards.append(received_card)
            print(f"You drawed a {received_card}. Your cards are:")
            self.print_cards()
            print(f"Cards value: {self.get_cards_value()}")

            if self.busted():
                print(f"You busted with a card value of {self.get_cards_value()}")
                break

            if self.get_cards_value() == 21:
                print("You got 21 and won!")
                break


class Betting:
    def __init__(self):
        self.bet = 0
        self.money = 1000

    def get_bet(self):
        while True:
            try:
                proposed_bet = float(input(f"You have ${round(self.money, 2)}. Enter your bet: "))

                if 0 > proposed_bet or proposed_bet > self.money:
                    print(f"The bet must be within the range [0, {round(self.money, 2)}")
                    continue

                self.bet = proposed_bet

            except ValueError:
                print("Please enter a number!")

            break

    def win_bet(self):
        self.money += self.bet
        self.bet = 0
        print(f"You won your bet! You now have ${round(self.money, 2)}")

    def lose_bet(self):
        self.money -= self.bet
        self.bet = 0
        print(f"You lost your bet. You now have ${round(self.money, 2)}")


def play_again() -> bool:
    return input("Do you want to play again? (y/n): ") == "y"


def main():
    betting_system: Betting = Betting()

    while True:
        # Game setup
        deck: Deck = Deck()
        deck.shuffle()

        player: Player = Player(deck)
        dealer: Dealer = Dealer(deck)

        # Main Game
        betting_system.get_bet()

        # Human Player
        print("--- YOU ---")

        player.play()

        if player.busted():
            betting_system.lose_bet()

            if play_again():
                continue
            else:
                break

        if player.get_cards_value() == 21:
            betting_system.win_bet()

            if play_again():
                continue
            else:
                break

        # Computer Dealer
        print("\n\n--- DEALER ---")
        dealer.play(player.get_cards_value())

        print("\n\n --- END GAME ---")

        if dealer.busted():
            print("Dealer busted. You win!")
            betting_system.win_bet()

        elif dealer.get_cards_value() > player.get_cards_value():
            print("Dealer won.")
            betting_system.lose_bet()

        if not play_again():
            break


if __name__ == "__main__":
    main()
