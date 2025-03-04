import tkinter as tk
from tkinter import ttk
import random
from collections import Counter

class BlackjackCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Card Counter - Wong Halves System")
        self.root.geometry("600x450")

        # Wong Halves count values (replacing Hi-Lo)
        self.wong_halves_values = {
            '2': 0.5, '3': 1, '4': 1, '5': 1.5, '6': 1,
            '7': 0.5, '8': 0, '9': -0.5,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }
        
        # Valid input keys
        self.valid_keys = {'2', '3', '4', '5', '6', '7', '8', '9', '0', 'j', 'q', 'k', 'a'}
        
        # Create GUI first
        self.create_gui()
        
        # Then initialize decks
        self.reset_decks()
        
        # Bind keyboard events after GUI is created
        self.root.bind('<Key>', self.handle_keypress)

    def reset_decks(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [rank + suit for _ in range(6) for suit in suits for rank in ranks]
        random.shuffle(self.deck)
        self.running_count = 0
        self.cards_dealt = 0
        self.last_dealt_cards = []
        self.update_bust_probabilities()

    def create_gui(self):
        # Frame for controls
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        # Reset Button
        ttk.Button(control_frame, text="Reset", command=self.reset_game).pack(side=tk.LEFT, padx=5)
        
        # System label
        ttk.Label(control_frame, text="Wong Halves System", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)

        # Display Frame
        display_frame = ttk.Frame(self.root)
        display_frame.pack(pady=10)

        # Instructions
        ttk.Label(display_frame, text="Press 2-9, 0 (10), J (Jack), Q (Queen), K (King), A (Ace)").pack()
        
        # Wong Halves values reference
        values_text = "Card Values: 5 (+1.5) | 3,4,6 (+1) | 2,7 (+0.5) | 8 (0) | 9 (-0.5) | 10,J,Q,K,A (-1)"
        ttk.Label(display_frame, text=values_text, font=("Arial", 9)).pack(pady=5)
        
        # Last Dealt Cards
        self.last_cards_label = ttk.Label(display_frame, text="Last Dealt: ")
        self.last_cards_label.pack()

        # Running Count
        self.count_label = ttk.Label(display_frame, text="Running Count: 0")
        self.count_label.pack()

        # True Count
        self.true_count_label = ttk.Label(display_frame, text="True Count: 0")
        self.true_count_label.pack()

        # Betting Advice
        self.bet_label = ttk.Label(display_frame, text="Betting Advice: Normal")
        self.bet_label.pack()

        # Remaining Cards
        self.cards_label = ttk.Label(display_frame, text="Cards Remaining: 312")
        self.cards_label.pack()

        # Top Cards
        self.top_cards_label = ttk.Label(display_frame, text="Top 7 Likely Cards: ")
        self.top_cards_label.pack()

        # Bust Probabilities
        self.bust_label = ttk.Label(display_frame, text="Bust Probabilities:")
        self.bust_label.pack()

    def handle_keypress(self, event):
        key = event.keysym.lower()
        if key in self.valid_keys:
            # Map '0' to '10' for input
            rank = '10' if key == '0' else key.upper()
            self.deal_card(rank)

    def deal_card(self, rank):
        if not self.deck:
            self.reset_decks()
        
        # Find and remove a card with matching rank
        for i, card in enumerate(self.deck):
            if card.startswith(rank):
                dealt_card = self.deck.pop(i)
                break
        else:
            return  # No matching card found
        
        self.cards_dealt += 1
        self.running_count += self.wong_halves_values[rank]
        
        # Update last dealt cards (keep last 5)
        self.last_dealt_cards.append(dealt_card)
        if len(self.last_dealt_cards) > 5:
            self.last_dealt_cards.pop(0)
        self.last_cards_label.config(text="Last Dealt: " + " ".join(self.last_dealt_cards))
        
        # Update displays
        remaining_decks = (312 - self.cards_dealt) / 52
        
        # Calculate true count - with Wong Halves we need to show fractional values
        true_count = self.running_count / remaining_decks if remaining_decks > 0 else 0
        
        # Format running count to display properly with fractions
        running_count_display = f"{self.running_count:.1f}" if self.running_count % 1 != 0 else f"{int(self.running_count)}"
        true_count_display = f"{true_count:.2f}"
        
        self.count_label.config(text=f"Running Count: {running_count_display}")
        self.true_count_label.config(text=f"True Count: {true_count_display}")
        self.cards_label.config(text=f"Cards Remaining: {312 - self.cards_dealt}")
        
        # Betting advice - adjust thresholds for Wong Halves
        if true_count >= 2:
            self.bet_label.config(text="Betting Advice: Increase Bet!")
        elif true_count >= 1:
            self.bet_label.config(text="Betting Advice: Slightly Increase Bet")
        elif true_count <= -1.5:
            self.bet_label.config(text="Betting Advice: Decrease Bet")
        elif true_count <= -0.5:
            self.bet_label.config(text="Betting Advice: Slightly Decrease Bet")
        else:
            self.bet_label.config(text="Betting Advice: Normal")
        
        # Update top 7 cards
        card_counts = Counter(card[:-1] for card in self.deck)
        top_cards = card_counts.most_common(7)
        self.top_cards_label.config(text="Top 7 Likely Cards: " + ", ".join(f"{c} ({n})" for c, n in top_cards))

        # Update bust probabilities
        self.update_bust_probabilities()

    def update_bust_probabilities(self):
        remaining_cards = len(self.deck)
        if remaining_cards == 0:
            self.bust_label.config(text="Bust Probabilities: Deck Empty")
            return

        bust_cards = {
            12: ['10', 'J', 'Q', 'K'],
            13: ['9', '10', 'J', 'Q', 'K'],
            14: ['8', '9', '10', 'J', 'Q', 'K'],
            15: ['7', '8', '9', '10', 'J', 'Q', 'K'],
            16: ['6', '7', '8', '9', '10', 'J', 'Q', 'K']
        }
        
        probs = []
        for value in range(12, 17):
            bust_count = sum(1 for card in self.deck if card[:-1] in bust_cards[value])
            prob = (bust_count / remaining_cards) * 100
            probs.append(f"{value}: {prob:.1f}%")
        
        self.bust_label.config(text="Bust Probabilities:\n" + "\n".join(probs))

    def reset_game(self):
        self.reset_decks()
        self.count_label.config(text="Running Count: 0")
        self.true_count_label.config(text="True Count: 0")
        self.bet_label.config(text="Betting Advice: Normal")
        self.cards_label.config(text="Cards Remaining: 312")
        self.top_cards_label.config(text="Top 7 Likely Cards: ")
        self.last_cards_label.config(text="Last Dealt: ")

if __name__ == "__main__":
    root = tk.Tk()
    app = BlackjackCounter(root)
    root.mainloop()