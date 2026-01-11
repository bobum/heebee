# Economy and Shop System for Ren'Py Visual Novel
# Includes: Multi-currency wallet, shops, haggling, price fluctuation, transaction history

init python:
    import time
    import random
    from collections import defaultdict

    # ==================== CURRENCY SYSTEM ====================

    class Currency:
        """Represents a type of currency in the game."""

        def __init__(self, name, symbol, description="", exchange_rate=1.0):
            self.name = name
            self.symbol = symbol
            self.description = description
            self.exchange_rate = exchange_rate  # Relative to base currency (gold)

        def __repr__(self):
            return f"Currency({self.name})"

        def format_amount(self, amount):
            """Format an amount with the currency symbol."""
            return f"{amount} {self.symbol}"

    # Define currency types
    CURRENCY_GOLD = Currency("Gold", "G", "Standard currency used throughout the realm", 1.0)
    CURRENCY_GEMS = Currency("Gems", "Gem", "Rare magical gems with high value", 100.0)
    CURRENCY_TOKENS = Currency("Tokens", "Tok", "Special tokens earned through quests", 10.0)

    ALL_CURRENCIES = {
        "gold": CURRENCY_GOLD,
        "gems": CURRENCY_GEMS,
        "tokens": CURRENCY_TOKENS
    }

    # ==================== WALLET SYSTEM ====================

    class Wallet:
        """Manages player's money across multiple currencies."""

        def __init__(self, starting_gold=100, starting_gems=0, starting_tokens=5):
            self.balances = {
                "gold": starting_gold,
                "gems": starting_gems,
                "tokens": starting_tokens
            }
            self.transaction_history = []
            self.max_history = 100  # Keep last 100 transactions

        def add(self, currency_type, amount, source="Unknown"):
            """Add currency to the wallet."""
            if currency_type not in self.balances:
                raise ValueError(f"Unknown currency type: {currency_type}")
            if amount < 0:
                raise ValueError("Cannot add negative amount")

            self.balances[currency_type] += amount
            self._log_transaction("add", currency_type, amount, source)
            return True

        def spend(self, currency_type, amount, destination="Unknown"):
            """Spend currency from the wallet. Returns True if successful."""
            if currency_type not in self.balances:
                raise ValueError(f"Unknown currency type: {currency_type}")
            if amount < 0:
                raise ValueError("Cannot spend negative amount")
            if self.balances[currency_type] < amount:
                return False

            self.balances[currency_type] -= amount
            self._log_transaction("spend", currency_type, amount, destination)
            return True

        def check_balance(self, currency_type=None):
            """Check balance. If no type specified, return all balances."""
            if currency_type is None:
                return dict(self.balances)
            if currency_type not in self.balances:
                raise ValueError(f"Unknown currency type: {currency_type}")
            return self.balances[currency_type]

        def can_afford(self, currency_type, amount):
            """Check if player can afford a purchase."""
            return self.balances.get(currency_type, 0) >= amount

        def exchange_currency(self, from_type, to_type, amount):
            """Exchange one currency for another based on exchange rates."""
            if from_type not in ALL_CURRENCIES or to_type not in ALL_CURRENCIES:
                return False

            if not self.can_afford(from_type, amount):
                return False

            from_rate = ALL_CURRENCIES[from_type].exchange_rate
            to_rate = ALL_CURRENCIES[to_type].exchange_rate

            converted_amount = int((amount * from_rate) / to_rate)
            if converted_amount <= 0:
                return False

            self.spend(from_type, amount, f"Exchange to {to_type}")
            self.add(to_type, converted_amount, f"Exchange from {from_type}")
            return True

        def _log_transaction(self, trans_type, currency, amount, details):
            """Log a transaction to history."""
            transaction = {
                "type": trans_type,
                "currency": currency,
                "amount": amount,
                "details": details,
                "timestamp": time.time(),
                "balance_after": self.balances[currency]
            }
            self.transaction_history.append(transaction)

            # Trim history if too long
            if len(self.transaction_history) > self.max_history:
                self.transaction_history = self.transaction_history[-self.max_history:]

        def get_transaction_history(self, count=10, currency_type=None):
            """Get recent transactions, optionally filtered by currency."""
            history = self.transaction_history
            if currency_type:
                history = [t for t in history if t["currency"] == currency_type]
            return history[-count:]

        def get_total_value_in_gold(self):
            """Calculate total wallet value in gold equivalent."""
            total = 0
            for currency_type, amount in self.balances.items():
                rate = ALL_CURRENCIES[currency_type].exchange_rate
                total += amount * rate
            return int(total)

    # ==================== SHOP ITEM SYSTEM ====================

    class ShopItem:
        """Represents an item that can be bought or sold in shops."""

        def __init__(self, item_id, name, description, base_price, currency_type="gold",
                     category="general", stock=-1, restock_rate=0, max_stock=-1,
                     can_sell=True, sell_modifier=0.5):
            self.item_id = item_id
            self.name = name
            self.description = description
            self.base_price = base_price
            self.currency_type = currency_type
            self.category = category
            self.stock = stock  # -1 means unlimited
            self.restock_rate = restock_rate  # Items restored per restock
            self.max_stock = max_stock if max_stock > 0 else stock
            self.can_sell = can_sell
            self.sell_modifier = sell_modifier  # Percentage of buy price when selling
            self.times_bought = 0
            self.times_sold = 0

        def __repr__(self):
            return f"ShopItem({self.item_id}: {self.name})"

        def is_available(self):
            """Check if item is in stock."""
            return self.stock != 0

        def reduce_stock(self, amount=1):
            """Reduce stock by amount. Returns True if successful."""
            if self.stock == -1:  # Unlimited stock
                return True
            if self.stock >= amount:
                self.stock -= amount
                return True
            return False

        def increase_stock(self, amount=1):
            """Increase stock by amount."""
            if self.stock == -1:  # Already unlimited
                return
            self.stock += amount
            if self.max_stock > 0:
                self.stock = min(self.stock, self.max_stock)

        def restock(self):
            """Restock item based on restock rate."""
            if self.restock_rate > 0 and self.stock != -1:
                self.increase_stock(self.restock_rate)

        def get_demand_modifier(self):
            """Calculate price modifier based on supply/demand."""
            if self.stock == -1:
                return 1.0

            # Price increases as stock decreases
            if self.max_stock > 0:
                stock_ratio = self.stock / self.max_stock
                # Price can increase up to 50% when stock is low
                return 1.0 + (0.5 * (1 - stock_ratio))
            return 1.0

    # ==================== SHOP SYSTEM ====================

    class Shop:
        """A shop that can buy and sell items."""

        def __init__(self, shop_id, name, description="", shop_type="general"):
            self.shop_id = shop_id
            self.name = name
            self.description = description
            self.shop_type = shop_type
            self.inventory = {}  # item_id -> ShopItem
            self.buy_price_modifier = 1.0  # Global price modifier for this shop
            self.sell_price_modifier = 1.0  # Global sell price modifier
            self.reputation = 0  # Affects prices (-100 to 100)
            self.is_open = True
            self.event_modifiers = {}  # Event-based price modifiers
            self.haggle_difficulty = 0.5  # 0 = easy, 1 = hard
            self.purchase_history = []

        def add_item(self, item):
            """Add an item to shop inventory."""
            self.inventory[item.item_id] = item

        def remove_item(self, item_id):
            """Remove an item from shop inventory."""
            if item_id in self.inventory:
                del self.inventory[item_id]

        def get_item(self, item_id):
            """Get an item from inventory."""
            return self.inventory.get(item_id)

        def get_available_items(self, category=None):
            """Get list of available items, optionally filtered by category."""
            items = [item for item in self.inventory.values() if item.is_available()]
            if category:
                items = [item for item in items if item.category == category]
            return items

        def get_categories(self):
            """Get list of unique categories in this shop."""
            return list(set(item.category for item in self.inventory.values()))

        def calculate_buy_price(self, item, quantity=1):
            """Calculate the price to buy an item from this shop."""
            if isinstance(item, str):
                item = self.get_item(item)
            if not item:
                return None

            base = item.base_price * quantity

            # Apply shop's global modifier
            price = base * self.buy_price_modifier

            # Apply demand modifier
            price *= item.get_demand_modifier()

            # Apply reputation discount (up to 20% off at max reputation)
            rep_modifier = 1.0 - (self.reputation / 500)  # -100 to 100 rep = 1.2 to 0.8
            price *= rep_modifier

            # Apply event modifiers
            for event_id, modifier in self.event_modifiers.items():
                price *= modifier

            return max(1, int(price))

        def calculate_sell_price(self, item, quantity=1):
            """Calculate the price when selling an item to this shop."""
            if isinstance(item, str):
                item = self.get_item(item)
            if not item or not item.can_sell:
                return 0

            base = item.base_price * item.sell_modifier * quantity

            # Apply shop's sell modifier
            price = base * self.sell_price_modifier

            # Apply reputation bonus (up to 20% more at max reputation)
            rep_modifier = 1.0 + (self.reputation / 500)
            price *= rep_modifier

            return max(1, int(price))

        def buy_item(self, item_id, wallet, quantity=1, haggle_price=None):
            """
            Buy an item from the shop.
            Returns (success, message)
            """
            item = self.get_item(item_id)
            if not item:
                return (False, "Item not found in this shop.")

            if not item.is_available():
                return (False, "Item is out of stock.")

            if item.stock != -1 and item.stock < quantity:
                return (False, f"Not enough stock. Only {item.stock} available.")

            # Use haggled price or calculate normal price
            price = haggle_price if haggle_price else self.calculate_buy_price(item, quantity)

            if not wallet.can_afford(item.currency_type, price):
                return (False, f"Not enough {item.currency_type}. Need {price}.")

            # Complete transaction
            wallet.spend(item.currency_type, price, f"Bought {quantity}x {item.name} from {self.name}")
            item.reduce_stock(quantity)
            item.times_bought += quantity

            self.purchase_history.append({
                "type": "buy",
                "item_id": item_id,
                "quantity": quantity,
                "price": price,
                "timestamp": time.time()
            })

            return (True, f"Purchased {quantity}x {item.name} for {price} {item.currency_type}!")

        def sell_item(self, item_id, wallet, quantity=1, haggle_price=None):
            """
            Sell an item to the shop.
            Returns (success, message)
            """
            item = self.get_item(item_id)
            if not item:
                return (False, "This shop doesn't deal in that item.")

            if not item.can_sell:
                return (False, "This shop doesn't buy that item.")

            # Use haggled price or calculate normal price
            price = haggle_price if haggle_price else self.calculate_sell_price(item, quantity)

            # Add money to wallet
            wallet.add(item.currency_type, price, f"Sold {quantity}x {item.name} to {self.name}")
            item.increase_stock(quantity)
            item.times_sold += quantity

            self.purchase_history.append({
                "type": "sell",
                "item_id": item_id,
                "quantity": quantity,
                "price": price,
                "timestamp": time.time()
            })

            return (True, f"Sold {quantity}x {item.name} for {price} {item.currency_type}!")

        def set_event_modifier(self, event_id, modifier):
            """Set a temporary price modifier due to story events."""
            self.event_modifiers[event_id] = modifier

        def clear_event_modifier(self, event_id):
            """Remove an event-based price modifier."""
            if event_id in self.event_modifiers:
                del self.event_modifiers[event_id]

        def restock_all(self):
            """Restock all items in the shop."""
            for item in self.inventory.values():
                item.restock()

        def improve_reputation(self, amount):
            """Improve shop reputation (affects prices)."""
            self.reputation = min(100, self.reputation + amount)

        def decrease_reputation(self, amount):
            """Decrease shop reputation."""
            self.reputation = max(-100, self.reputation - amount)

    # ==================== HAGGLING SYSTEM ====================

    class HaggleSystem:
        """Mini-game system for haggling prices."""

        def __init__(self):
            self.current_shop = None
            self.current_item = None
            self.base_price = 0
            self.current_offer = 0
            self.min_price = 0
            self.max_rounds = 3
            self.current_round = 0
            self.is_buying = True
            self.is_active = False
            self.merchant_mood = 0.5  # 0 = angry, 1 = happy

        def start_haggle(self, shop, item, is_buying=True):
            """Start a haggling session."""
            self.current_shop = shop
            self.current_item = item
            self.is_buying = is_buying
            self.current_round = 0
            self.is_active = True
            self.merchant_mood = 0.5

            if is_buying:
                self.base_price = shop.calculate_buy_price(item)
                # Minimum the merchant will accept (based on difficulty)
                difficulty = shop.haggle_difficulty
                self.min_price = int(self.base_price * (0.6 + (0.3 * difficulty)))
            else:
                self.base_price = shop.calculate_sell_price(item)
                # Maximum the merchant will pay
                difficulty = shop.haggle_difficulty
                self.min_price = int(self.base_price * (1.0 + (0.4 * (1 - difficulty))))

            self.current_offer = self.base_price
            return self.base_price

        def make_offer(self, player_offer):
            """
            Player makes an offer.
            Returns (accepted, counter_offer, message, mood_change)
            """
            if not self.is_active:
                return (False, 0, "No active haggle session.", 0)

            self.current_round += 1

            if self.is_buying:
                return self._handle_buy_offer(player_offer)
            else:
                return self._handle_sell_offer(player_offer)

        def _handle_buy_offer(self, player_offer):
            """Handle haggling when buying."""
            # Player wants to pay less
            if player_offer >= self.current_offer:
                # Player offered more than current - auto accept
                self.is_active = False
                return (True, player_offer, "Deal! The merchant happily accepts.", 0.2)

            if player_offer >= self.min_price:
                # Acceptable range - might accept or counter
                acceptance_chance = (player_offer - self.min_price) / (self.base_price - self.min_price)
                acceptance_chance += (self.merchant_mood - 0.5) * 0.3

                if random.random() < acceptance_chance or self.current_round >= self.max_rounds:
                    self.is_active = False
                    return (True, player_offer, "The merchant considers... 'Fine, we have a deal!'", 0.1)
                else:
                    # Counter offer
                    counter = int((player_offer + self.current_offer) / 2)
                    counter = max(counter, self.min_price)
                    self.current_offer = counter
                    mood_change = -0.1 if player_offer < self.min_price * 1.1 else 0
                    self.merchant_mood = max(0, min(1, self.merchant_mood + mood_change))
                    return (False, counter, f"'How about {counter}? That's my best offer.'", mood_change)
            else:
                # Offer too low
                mood_change = -0.2
                self.merchant_mood = max(0, min(1, self.merchant_mood + mood_change))

                if self.merchant_mood <= 0.1:
                    self.is_active = False
                    return (False, 0, "The merchant is offended and refuses to haggle further!", mood_change)

                if self.current_round >= self.max_rounds:
                    self.is_active = False
                    return (False, self.current_offer, "The merchant won't go lower. Take it or leave it.", mood_change)

                # Counter with a smaller reduction
                counter = int(self.current_offer * 0.95)
                counter = max(counter, self.min_price)
                self.current_offer = counter
                return (False, counter, f"'That's insulting! {counter} is as low as I'll go.'", mood_change)

        def _handle_sell_offer(self, player_offer):
            """Handle haggling when selling."""
            # Player wants more money
            if player_offer <= self.current_offer:
                # Player asked for less than current - auto accept
                self.is_active = False
                return (True, player_offer, "Deal! The merchant eagerly accepts.", 0.2)

            if player_offer <= self.min_price:
                # Acceptable range
                acceptance_chance = (self.min_price - player_offer) / (self.min_price - self.base_price)
                acceptance_chance += (self.merchant_mood - 0.5) * 0.3

                if random.random() < acceptance_chance or self.current_round >= self.max_rounds:
                    self.is_active = False
                    return (True, player_offer, "The merchant sighs... 'Alright, I'll pay that.'", 0.1)
                else:
                    counter = int((player_offer + self.current_offer) / 2)
                    counter = min(counter, self.min_price)
                    self.current_offer = counter
                    mood_change = -0.1
                    self.merchant_mood = max(0, min(1, self.merchant_mood + mood_change))
                    return (False, counter, f"'I can offer {counter}, no more.'", mood_change)
            else:
                # Asking too much
                mood_change = -0.2
                self.merchant_mood = max(0, min(1, self.merchant_mood + mood_change))

                if self.merchant_mood <= 0.1:
                    self.is_active = False
                    return (False, 0, "The merchant laughs and walks away!", mood_change)

                if self.current_round >= self.max_rounds:
                    self.is_active = False
                    return (False, self.current_offer, "Final offer. Take it or leave it.", mood_change)

                counter = int(self.current_offer * 1.05)
                counter = min(counter, self.min_price)
                self.current_offer = counter
                return (False, counter, f"'That's too much! I'll give you {counter}.'", mood_change)

        def accept_current_offer(self):
            """Accept the current offer and end haggling."""
            if not self.is_active:
                return None

            final_price = self.current_offer
            self.is_active = False
            return final_price

        def cancel_haggle(self):
            """Cancel the haggling session."""
            self.is_active = False
            self.current_shop = None
            self.current_item = None

    # ==================== PRICE FLUCTUATION SYSTEM ====================

    class PriceFluctuationManager:
        """Manages dynamic price changes based on events and time."""

        def __init__(self):
            self.global_modifiers = {}
            self.item_modifiers = defaultdict(dict)
            self.shop_modifiers = defaultdict(dict)

        def set_global_event(self, event_id, modifier, description=""):
            """Set a global price modifier affecting all shops."""
            self.global_modifiers[event_id] = {
                "modifier": modifier,
                "description": description
            }

        def clear_global_event(self, event_id):
            """Remove a global price modifier."""
            if event_id in self.global_modifiers:
                del self.global_modifiers[event_id]

        def set_item_event(self, item_id, event_id, modifier, description=""):
            """Set a price modifier for a specific item across all shops."""
            self.item_modifiers[item_id][event_id] = {
                "modifier": modifier,
                "description": description
            }

        def clear_item_event(self, item_id, event_id):
            """Remove an item-specific price modifier."""
            if item_id in self.item_modifiers and event_id in self.item_modifiers[item_id]:
                del self.item_modifiers[item_id][event_id]

        def set_shop_event(self, shop_id, event_id, modifier, description=""):
            """Set a price modifier for a specific shop."""
            self.shop_modifiers[shop_id][event_id] = {
                "modifier": modifier,
                "description": description
            }

        def clear_shop_event(self, shop_id, event_id):
            """Remove a shop-specific price modifier."""
            if shop_id in self.shop_modifiers and event_id in self.shop_modifiers[shop_id]:
                del self.shop_modifiers[shop_id][event_id]

        def get_total_modifier(self, shop_id=None, item_id=None):
            """Calculate the total price modifier for a shop/item combination."""
            modifier = 1.0

            # Apply global modifiers
            for event_data in self.global_modifiers.values():
                modifier *= event_data["modifier"]

            # Apply shop-specific modifiers
            if shop_id and shop_id in self.shop_modifiers:
                for event_data in self.shop_modifiers[shop_id].values():
                    modifier *= event_data["modifier"]

            # Apply item-specific modifiers
            if item_id and item_id in self.item_modifiers:
                for event_data in self.item_modifiers[item_id].values():
                    modifier *= event_data["modifier"]

            return modifier

        def get_active_events(self):
            """Get list of all active price-affecting events."""
            events = []
            for event_id, data in self.global_modifiers.items():
                events.append({
                    "id": event_id,
                    "type": "global",
                    "modifier": data["modifier"],
                    "description": data["description"]
                })
            return events

    # ==================== SHOP MANAGER ====================

    class ShopManager:
        """Central manager for all shops in the game."""

        def __init__(self):
            self.shops = {}
            self.price_manager = PriceFluctuationManager()
            self.haggle_system = HaggleSystem()

        def register_shop(self, shop):
            """Register a shop with the manager."""
            self.shops[shop.shop_id] = shop

        def get_shop(self, shop_id):
            """Get a shop by ID."""
            return self.shops.get(shop_id)

        def get_all_shops(self):
            """Get all registered shops."""
            return list(self.shops.values())

        def daily_update(self):
            """Called daily to restock shops and update prices."""
            for shop in self.shops.values():
                shop.restock_all()

        def apply_story_event(self, event_id, modifier, description=""):
            """Apply a story event that affects prices."""
            self.price_manager.set_global_event(event_id, modifier, description)
            # Apply to all shops
            for shop in self.shops.values():
                shop.set_event_modifier(event_id, modifier)

        def clear_story_event(self, event_id):
            """Clear a story event's effects on prices."""
            self.price_manager.clear_global_event(event_id)
            for shop in self.shops.values():
                shop.clear_event_modifier(event_id)

    # ==================== INITIALIZE GAME OBJECTS ====================

    # Create the shop manager
    shop_manager = ShopManager()

    # Create player wallet
    player_wallet = Wallet(starting_gold=100, starting_gems=0, starting_tokens=5)

    # ==================== CREATE EXAMPLE SHOPS ====================

    def create_example_shops():
        """Create example shops with items."""

        # === GENERAL STORE ===
        general_store = Shop(
            "general_store",
            "Martha's General Store",
            "A cozy shop selling everyday supplies and provisions.",
            "general"
        )
        general_store.haggle_difficulty = 0.3  # Easy to haggle

        # Add items to general store
        general_store.add_item(ShopItem(
            "bread", "Fresh Bread", "Warm, crusty bread baked this morning.",
            base_price=5, category="food", stock=20, restock_rate=10, max_stock=20
        ))
        general_store.add_item(ShopItem(
            "cheese", "Aged Cheese", "Sharp cheddar aged for 6 months.",
            base_price=15, category="food", stock=10, restock_rate=5, max_stock=10
        ))
        general_store.add_item(ShopItem(
            "rope", "Hemp Rope", "50 feet of sturdy rope.",
            base_price=25, category="supplies", stock=5, restock_rate=2, max_stock=5
        ))
        general_store.add_item(ShopItem(
            "lantern", "Oil Lantern", "Reliable light source for dark places.",
            base_price=50, category="supplies", stock=3, restock_rate=1, max_stock=3
        ))
        general_store.add_item(ShopItem(
            "healing_salve", "Healing Salve", "Herbal mixture that speeds healing.",
            base_price=75, category="medicine", stock=5, restock_rate=2, max_stock=5
        ))

        # === BLACKSMITH ===
        blacksmith = Shop(
            "blacksmith",
            "Iron Will Smithy",
            "Master-crafted weapons and armor.",
            "weapons"
        )
        blacksmith.haggle_difficulty = 0.6  # Moderate difficulty
        blacksmith.buy_price_modifier = 1.1  # Slightly higher prices

        blacksmith.add_item(ShopItem(
            "iron_sword", "Iron Sword", "A reliable blade for any adventurer.",
            base_price=150, category="weapons", stock=3, restock_rate=1, max_stock=3
        ))
        blacksmith.add_item(ShopItem(
            "steel_sword", "Steel Sword", "Superior craftsmanship for the discerning warrior.",
            base_price=350, category="weapons", stock=2, restock_rate=1, max_stock=2
        ))
        blacksmith.add_item(ShopItem(
            "iron_armor", "Iron Chainmail", "Protective chainmail armor.",
            base_price=300, category="armor", stock=2, restock_rate=1, max_stock=2
        ))
        blacksmith.add_item(ShopItem(
            "steel_shield", "Steel Shield", "A sturdy shield that has saved many lives.",
            base_price=200, category="armor", stock=3, restock_rate=1, max_stock=3
        ))
        blacksmith.add_item(ShopItem(
            "dagger", "Iron Dagger", "Small but deadly in the right hands.",
            base_price=50, category="weapons", stock=5, restock_rate=2, max_stock=5
        ))

        # === MAGIC SHOP ===
        magic_shop = Shop(
            "magic_shop",
            "Mystic Emporium",
            "Arcane artifacts and mystical supplies.",
            "magic"
        )
        magic_shop.haggle_difficulty = 0.8  # Hard to haggle
        magic_shop.buy_price_modifier = 1.2  # Premium prices

        magic_shop.add_item(ShopItem(
            "mana_potion", "Mana Potion", "Restores magical energy.",
            base_price=100, category="potions", stock=10, restock_rate=3, max_stock=10
        ))
        magic_shop.add_item(ShopItem(
            "health_potion", "Health Potion", "Instantly restores vitality.",
            base_price=80, category="potions", stock=10, restock_rate=3, max_stock=10
        ))
        magic_shop.add_item(ShopItem(
            "fire_scroll", "Scroll of Fireball", "Single-use fire magic.",
            base_price=200, category="scrolls", stock=5, restock_rate=1, max_stock=5
        ))
        magic_shop.add_item(ShopItem(
            "ice_scroll", "Scroll of Ice Storm", "Single-use ice magic.",
            base_price=200, category="scrolls", stock=5, restock_rate=1, max_stock=5
        ))
        magic_shop.add_item(ShopItem(
            "enchanted_ring", "Ring of Protection", "Magical ring that wards off harm.",
            base_price=500, currency_type="gold", category="artifacts", stock=1, restock_rate=0, max_stock=1
        ))
        magic_shop.add_item(ShopItem(
            "crystal_orb", "Crystal Scrying Orb", "See glimpses of the future.",
            base_price=5, currency_type="gems", category="artifacts", stock=1, restock_rate=0, max_stock=1
        ))

        # Register all shops
        shop_manager.register_shop(general_store)
        shop_manager.register_shop(blacksmith)
        shop_manager.register_shop(magic_shop)

    # Initialize shops when game starts
    create_example_shops()

# ==================== SHOP SCREEN UI ====================

screen shop_screen(current_shop):
    tag menu
    modal True

    default selected_item = None
    default current_tab = "buy"
    default quantity = 1
    default show_haggle = False
    default haggle_offer = 0
    default haggle_message = ""

    frame:
        style_prefix "shop"
        xfill True
        yfill True

        vbox:
            spacing 10

            # Shop header
            hbox:
                xfill True
                text current_shop.name style "shop_title"
                textbutton "X Close" action Return() xalign 1.0

            text current_shop.description style "shop_description"

            # Player wallet display
            hbox:
                spacing 20
                text "Your Gold: [player_wallet.balances['gold']]" style "shop_wallet"
                text "Gems: [player_wallet.balances['gems']]" style "shop_wallet"
                text "Tokens: [player_wallet.balances['tokens']]" style "shop_wallet"

            null height 10

            # Buy/Sell tabs
            hbox:
                spacing 10
                textbutton "Buy" action SetScreenVariable("current_tab", "buy") style "shop_tab"
                textbutton "Sell" action SetScreenVariable("current_tab", "sell") style "shop_tab"

            null height 10

            # Main content area
            hbox:
                spacing 20

                # Item list
                frame:
                    style "shop_item_list_frame"
                    xsize 400
                    ysize 400

                    viewport:
                        scrollbars "vertical"
                        mousewheel True

                        vbox:
                            spacing 5

                            if current_tab == "buy":
                                for item in current_shop.get_available_items():
                                    $ buy_price = current_shop.calculate_buy_price(item)
                                    $ can_afford = player_wallet.can_afford(item.currency_type, buy_price)

                                    textbutton "[item.name] - [buy_price] [item.currency_type]":
                                        action SetScreenVariable("selected_item", item)
                                        style "shop_item_button"
                                        sensitive can_afford and item.is_available()
                            else:
                                for item in current_shop.inventory.values():
                                    if item.can_sell:
                                        $ sell_price = current_shop.calculate_sell_price(item)
                                        textbutton "[item.name] - [sell_price] [item.currency_type]":
                                            action SetScreenVariable("selected_item", item)
                                            style "shop_item_button"

                # Item details panel
                frame:
                    style "shop_details_frame"
                    xsize 350
                    ysize 400

                    if selected_item:
                        vbox:
                            spacing 10

                            text selected_item.name style "shop_item_name"
                            text selected_item.description style "shop_item_desc"

                            null height 10

                            if current_tab == "buy":
                                $ price = current_shop.calculate_buy_price(selected_item, quantity)
                                text "Price: [price] [selected_item.currency_type]"
                                if selected_item.stock != -1:
                                    text "In Stock: [selected_item.stock]"
                                else:
                                    text "In Stock: Unlimited"
                            else:
                                $ price = current_shop.calculate_sell_price(selected_item, quantity)
                                text "Sell Value: [price] [selected_item.currency_type]"

                            null height 10

                            # Quantity selector
                            hbox:
                                spacing 10
                                text "Quantity:"
                                textbutton "-" action SetScreenVariable("quantity", max(1, quantity - 1))
                                text "[quantity]"
                                textbutton "+" action SetScreenVariable("quantity", quantity + 1)

                            null height 20

                            # Action buttons
                            hbox:
                                spacing 10

                                if current_tab == "buy":
                                    textbutton "Buy":
                                        action [
                                            Function(current_shop.buy_item, selected_item.item_id, player_wallet, quantity),
                                            SetScreenVariable("selected_item", None)
                                        ]
                                        sensitive player_wallet.can_afford(selected_item.currency_type, current_shop.calculate_buy_price(selected_item, quantity))

                                    textbutton "Haggle":
                                        action [
                                            SetScreenVariable("show_haggle", True),
                                            SetScreenVariable("haggle_offer", current_shop.calculate_buy_price(selected_item))
                                        ]
                                else:
                                    textbutton "Sell":
                                        action [
                                            Function(current_shop.sell_item, selected_item.item_id, player_wallet, quantity),
                                            SetScreenVariable("selected_item", None)
                                        ]

                                    textbutton "Haggle":
                                        action [
                                            SetScreenVariable("show_haggle", True),
                                            SetScreenVariable("haggle_offer", current_shop.calculate_sell_price(selected_item))
                                        ]
                    else:
                        text "Select an item to view details" style "shop_placeholder"

    # Haggle overlay
    if show_haggle and selected_item:
        modal True
        frame:
            style "haggle_frame"
            xalign 0.5
            yalign 0.5
            xsize 400
            ysize 300

            vbox:
                spacing 15
                xalign 0.5

                text "Haggling for [selected_item.name]" style "haggle_title"

                if current_tab == "buy":
                    text "Current offer: [haggle_offer] [selected_item.currency_type]"
                else:
                    text "Your asking price: [haggle_offer] [selected_item.currency_type]"

                if haggle_message:
                    text "[haggle_message]" style "haggle_message"

                hbox:
                    spacing 10
                    xalign 0.5
                    textbutton "-10" action SetScreenVariable("haggle_offer", max(1, haggle_offer - 10))
                    textbutton "-5" action SetScreenVariable("haggle_offer", max(1, haggle_offer - 5))
                    textbutton "+5" action SetScreenVariable("haggle_offer", haggle_offer + 5)
                    textbutton "+10" action SetScreenVariable("haggle_offer", haggle_offer + 10)

                text "Your offer: [haggle_offer]" xalign 0.5

                hbox:
                    spacing 20
                    xalign 0.5

                    textbutton "Make Offer":
                        action [
                            Function(process_haggle, current_shop, selected_item, haggle_offer, current_tab == "buy"),
                            SetScreenVariable("show_haggle", False)
                        ]

                    textbutton "Cancel":
                        action SetScreenVariable("show_haggle", False)

# Haggle processing function
init python:
    def process_haggle(shop, item, offer, is_buying):
        """Process a haggle attempt."""
        haggle = shop_manager.haggle_system
        haggle.start_haggle(shop, item, is_buying)
        accepted, counter, message, mood = haggle.make_offer(offer)

        if accepted:
            if is_buying:
                shop.buy_item(item.item_id, player_wallet, 1, offer)
            else:
                shop.sell_item(item.item_id, player_wallet, 1, offer)
            renpy.notify(message)
        else:
            renpy.notify(message)

# ==================== SHOP UI STYLES ====================

style shop_title:
    size 32
    bold True

style shop_description:
    size 18
    italic True

style shop_wallet:
    size 20
    bold True

style shop_tab:
    size 22
    padding (15, 8)

style shop_item_list_frame:
    background "#2a2a2a"
    padding (10, 10)

style shop_details_frame:
    background "#3a3a3a"
    padding (15, 15)

style shop_item_button:
    size 18

style shop_item_name:
    size 24
    bold True

style shop_item_desc:
    size 16

style shop_placeholder:
    size 18
    italic True
    xalign 0.5
    yalign 0.5

style haggle_frame:
    background "#1a1a1a"
    padding (20, 20)

style haggle_title:
    size 24
    bold True
    xalign 0.5

style haggle_message:
    size 16
    italic True
    xalign 0.5

# ==================== TRANSACTION HISTORY SCREEN ====================

screen transaction_history_screen():
    tag menu
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        ysize 500

        vbox:
            spacing 10

            hbox:
                xfill True
                text "Transaction History" size 28 bold True
                textbutton "X Close" action Return() xalign 1.0

            null height 10

            viewport:
                scrollbars "vertical"
                mousewheel True
                ysize 400

                vbox:
                    spacing 5

                    for trans in player_wallet.get_transaction_history(50):
                        frame:
                            xfill True
                            padding (10, 5)

                            hbox:
                                spacing 20

                                if trans["type"] == "add":
                                    text "+" style "trans_add"
                                else:
                                    text "-" style "trans_spend"

                                text "[trans['amount']] [trans['currency']]" xsize 100
                                text "[trans['details']]"

style trans_add:
    color "#4CAF50"
    bold True
    size 20

style trans_spend:
    color "#f44336"
    bold True
    size 20

# ==================== EXAMPLE USAGE LABELS ====================

label open_general_store:
    $ current_shop = shop_manager.get_shop("general_store")
    call screen shop_screen(current_shop)
    return

label open_blacksmith:
    $ current_shop = shop_manager.get_shop("blacksmith")
    call screen shop_screen(current_shop)
    return

label open_magic_shop:
    $ current_shop = shop_manager.get_shop("magic_shop")
    call screen shop_screen(current_shop)
    return

label view_transactions:
    call screen transaction_history_screen()
    return

# Example of applying story events that affect prices
label war_begins:
    # Weapons become more expensive during wartime
    $ shop_manager.apply_story_event("war", 1.5, "Wartime demand increases weapon prices")
    "The war has begun. Weapon prices have increased..."
    return

label war_ends:
    $ shop_manager.clear_story_event("war")
    "Peace has returned. Prices are normalizing..."
    return

label festival_sale:
    # Festival causes a sale at all shops
    $ shop_manager.apply_story_event("festival", 0.8, "Festival Sale - 20% off!")
    "The annual festival has begun! All shops are offering discounts."
    return
