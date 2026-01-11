# Heebee - Economy System
# A complete economy system with currencies, wallets, shops, and transactions
#
# ============================================================================
# USAGE EXAMPLES:
# ============================================================================
#
# Initialize wallet at game start:
#   $ wallet = Wallet()
#
# Add currency:
#   $ wallet.add("gold", 100)
#   $ wallet.add("gems", 5)
#
# Check balance:
#   $ gold_amount = wallet.get_balance("gold")
#   if wallet.has_enough("gold", 50):
#       "You can afford it!"
#
# Create and use a shop:
#   $ shop = Shop("General Store")
#   $ shop.add_item("Health Potion", "gold", 25, stock=10)
#   $ shop.add_item("Sword", "gold", 100, stock=1)
#
# Buy from shop:
#   $ success = shop.buy("Health Potion", wallet)
#
# Sell to shop:
#   $ success = shop.sell("Old Sword", wallet, 15)
#
# ============================================================================

init python:
    from enum import Enum
    from typing import Dict, List, Optional, Tuple

    class TransactionType(Enum):
        """Types of transactions that can occur."""
        PURCHASE = "purchase"
        SALE = "sale"
        DEPOSIT = "deposit"
        WITHDRAWAL = "withdrawal"
        TRANSFER = "transfer"

    class TransactionResult:
        """Result of a transaction attempt."""

        def __init__(self, success: bool, message: str = "", amount: int = 0,
                     currency: str = "", transaction_type: TransactionType = None):
            self.success = success
            self.message = message
            self.amount = amount
            self.currency = currency
            self.transaction_type = transaction_type

        def __bool__(self):
            return self.success

        def __repr__(self):
            status = "Success" if self.success else "Failed"
            return f"TransactionResult({status}: {self.message})"


    class Currency:
        """
        Represents a type of currency in the game.
        Tracks name, symbol, and exchange rates.
        """

        def __init__(self, name: str, symbol: str = "", exchange_rate: float = 1.0,
                     max_amount: int = 999999):
            """
            Initialize a currency type.

            Args:
                name: Internal name of the currency (e.g., "gold")
                symbol: Display symbol (e.g., "G" or "$")
                exchange_rate: Rate relative to base currency (1.0 = base)
                max_amount: Maximum amount of this currency a wallet can hold
            """
            self.name = name.lower()
            self.symbol = symbol or name[0].upper()
            self.exchange_rate = exchange_rate
            self.max_amount = max_amount

        def format_amount(self, amount: int) -> str:
            """Format an amount with the currency symbol."""
            return f"{amount}{self.symbol}"

        def convert_to(self, amount: int, target_currency: 'Currency') -> int:
            """
            Convert an amount to another currency.

            Args:
                amount: Amount in this currency
                target_currency: Currency to convert to

            Returns:
                Amount in target currency (rounded down)
            """
            if target_currency.exchange_rate == 0:
                return 0
            base_value = amount * self.exchange_rate
            return int(base_value / target_currency.exchange_rate)

        def __repr__(self):
            return f"Currency({self.name}, {self.symbol})"


    class Wallet:
        """
        A wallet that holds multiple currencies.
        Tracks balances and provides transaction methods.
        """

        # Default currencies available in the game
        DEFAULT_CURRENCIES = {
            "gold": Currency("gold", "G", 1.0),
            "gems": Currency("gems", "D", 100.0),  # 1 gem = 100 gold
            "silver": Currency("silver", "S", 0.1),  # 10 silver = 1 gold
        }

        def __init__(self, currencies: Dict[str, Currency] = None):
            """
            Initialize a wallet.

            Args:
                currencies: Custom currency definitions. Uses defaults if None.
            """
            self.currencies = currencies if currencies else dict(self.DEFAULT_CURRENCIES)
            self._balances: Dict[str, int] = {name: 0 for name in self.currencies}
            self._transaction_history: List[TransactionResult] = []

        def register_currency(self, currency: Currency) -> bool:
            """
            Register a new currency type.

            Args:
                currency: Currency to register

            Returns:
                True if registered, False if currency already exists
            """
            if currency.name in self.currencies:
                return False
            self.currencies[currency.name] = currency
            self._balances[currency.name] = 0
            return True

        def get_balance(self, currency_name: str) -> int:
            """Get the current balance of a currency."""
            currency_name = currency_name.lower()
            return self._balances.get(currency_name, 0)

        def has_enough(self, currency_name: str, amount: int) -> bool:
            """Check if wallet has at least the specified amount."""
            return self.get_balance(currency_name) >= amount

        def get_currency(self, currency_name: str) -> Optional[Currency]:
            """Get a currency object by name."""
            return self.currencies.get(currency_name.lower())

        def add(self, currency_name: str, amount: int) -> TransactionResult:
            """
            Add currency to the wallet.

            Args:
                currency_name: Name of the currency
                amount: Amount to add (must be positive)

            Returns:
                TransactionResult indicating success or failure
            """
            currency_name = currency_name.lower()

            if amount < 0:
                return TransactionResult(
                    False, "Cannot add negative amount", 0, currency_name
                )

            if currency_name not in self.currencies:
                return TransactionResult(
                    False, f"Unknown currency: {currency_name}", 0, currency_name
                )

            currency = self.currencies[currency_name]
            current = self._balances[currency_name]
            new_balance = min(current + amount, currency.max_amount)
            actual_added = new_balance - current

            self._balances[currency_name] = new_balance

            result = TransactionResult(
                True,
                f"Added {actual_added} {currency_name}",
                actual_added,
                currency_name,
                TransactionType.DEPOSIT
            )
            self._transaction_history.append(result)
            return result

        def subtract(self, currency_name: str, amount: int) -> TransactionResult:
            """
            Remove currency from the wallet.

            Args:
                currency_name: Name of the currency
                amount: Amount to remove (must be positive)

            Returns:
                TransactionResult indicating success or failure
            """
            currency_name = currency_name.lower()

            if amount < 0:
                return TransactionResult(
                    False, "Cannot subtract negative amount", 0, currency_name
                )

            if currency_name not in self.currencies:
                return TransactionResult(
                    False, f"Unknown currency: {currency_name}", 0, currency_name
                )

            if not self.has_enough(currency_name, amount):
                return TransactionResult(
                    False,
                    f"Insufficient {currency_name} (need {amount}, have {self._balances[currency_name]})",
                    0,
                    currency_name
                )

            self._balances[currency_name] -= amount

            result = TransactionResult(
                True,
                f"Removed {amount} {currency_name}",
                amount,
                currency_name,
                TransactionType.WITHDRAWAL
            )
            self._transaction_history.append(result)
            return result

        def transfer(self, target_wallet: 'Wallet', currency_name: str,
                    amount: int) -> TransactionResult:
            """
            Transfer currency to another wallet.

            Args:
                target_wallet: Wallet to transfer to
                currency_name: Name of the currency
                amount: Amount to transfer

            Returns:
                TransactionResult indicating success or failure
            """
            currency_name = currency_name.lower()

            # Validate
            if currency_name not in self.currencies:
                return TransactionResult(
                    False, f"Unknown currency: {currency_name}", 0, currency_name
                )

            if currency_name not in target_wallet.currencies:
                return TransactionResult(
                    False, f"Target wallet doesn't support {currency_name}", 0, currency_name
                )

            if not self.has_enough(currency_name, amount):
                return TransactionResult(
                    False,
                    f"Insufficient {currency_name}",
                    0,
                    currency_name
                )

            # Perform transfer
            self._balances[currency_name] -= amount
            target_wallet._balances[currency_name] += amount

            result = TransactionResult(
                True,
                f"Transferred {amount} {currency_name}",
                amount,
                currency_name,
                TransactionType.TRANSFER
            )
            self._transaction_history.append(result)
            return result

        def convert(self, from_currency: str, to_currency: str,
                   amount: int) -> TransactionResult:
            """
            Convert currency from one type to another.

            Args:
                from_currency: Currency to convert from
                to_currency: Currency to convert to
                amount: Amount to convert

            Returns:
                TransactionResult with converted amount
            """
            from_currency = from_currency.lower()
            to_currency = to_currency.lower()

            from_curr = self.get_currency(from_currency)
            to_curr = self.get_currency(to_currency)

            if not from_curr:
                return TransactionResult(
                    False, f"Unknown currency: {from_currency}", 0, from_currency
                )

            if not to_curr:
                return TransactionResult(
                    False, f"Unknown currency: {to_currency}", 0, to_currency
                )

            if not self.has_enough(from_currency, amount):
                return TransactionResult(
                    False, f"Insufficient {from_currency}", 0, from_currency
                )

            converted_amount = from_curr.convert_to(amount, to_curr)

            if converted_amount == 0 and amount > 0:
                return TransactionResult(
                    False, "Conversion would result in 0", 0, to_currency
                )

            self._balances[from_currency] -= amount
            self._balances[to_currency] = min(
                self._balances[to_currency] + converted_amount,
                to_curr.max_amount
            )

            return TransactionResult(
                True,
                f"Converted {amount} {from_currency} to {converted_amount} {to_currency}",
                converted_amount,
                to_currency
            )

        def get_all_balances(self) -> Dict[str, int]:
            """Get all currency balances."""
            return dict(self._balances)

        def get_transaction_history(self) -> List[TransactionResult]:
            """Get the transaction history."""
            return list(self._transaction_history)

        def clear_history(self):
            """Clear the transaction history."""
            self._transaction_history.clear()

        def to_dict(self) -> dict:
            """Convert wallet to dictionary for saving."""
            return {
                "balances": dict(self._balances),
                "history_count": len(self._transaction_history)
            }

        @classmethod
        def from_dict(cls, data: dict) -> 'Wallet':
            """Create wallet from saved dictionary."""
            wallet = cls()
            for currency, amount in data.get("balances", {}).items():
                if currency in wallet._balances:
                    wallet._balances[currency] = amount
            return wallet


    class ShopItem:
        """An item available in a shop."""

        def __init__(self, name: str, base_price: int, currency: str = "gold",
                     stock: int = -1, description: str = ""):
            """
            Initialize a shop item.

            Args:
                name: Item name
                base_price: Base price before any discounts
                currency: Currency type required
                stock: Available quantity (-1 for unlimited)
                description: Item description
            """
            self.name = name
            self.base_price = base_price
            self.currency = currency.lower()
            self.stock = stock
            self.description = description

        def is_available(self) -> bool:
            """Check if item is in stock."""
            return self.stock != 0

        def get_price(self, discount: float = 0.0) -> int:
            """
            Get the current price after discount.

            Args:
                discount: Discount percentage (0.0 to 1.0)

            Returns:
                Final price (minimum 1)
            """
            discount = max(0.0, min(1.0, discount))
            discounted = self.base_price * (1.0 - discount)
            return max(1, int(discounted))

        def __repr__(self):
            stock_str = "unlimited" if self.stock < 0 else str(self.stock)
            return f"ShopItem({self.name}, {self.base_price} {self.currency}, stock={stock_str})"


    class Shop:
        """
        A shop that sells and buys items.
        Supports multiple currencies, discounts, and inventory tracking.
        """

        def __init__(self, name: str, buy_rate: float = 0.5):
            """
            Initialize a shop.

            Args:
                name: Shop name
                buy_rate: Rate at which shop buys items (0.5 = 50% of base price)
            """
            self.name = name
            self.buy_rate = max(0.0, min(1.0, buy_rate))
            self._items: Dict[str, ShopItem] = {}
            self._discounts: Dict[str, float] = {}  # Per-item discounts
            self._global_discount: float = 0.0

        def add_item(self, name: str, currency: str, price: int,
                    stock: int = -1, description: str = "") -> bool:
            """
            Add an item to the shop inventory.

            Args:
                name: Item name
                currency: Currency type
                price: Base price
                stock: Available quantity (-1 for unlimited)
                description: Item description

            Returns:
                True if added, False if item already exists
            """
            item_key = name.lower()
            if item_key in self._items:
                return False

            self._items[item_key] = ShopItem(name, price, currency, stock, description)
            return True

        def remove_item(self, name: str) -> bool:
            """Remove an item from the shop."""
            item_key = name.lower()
            if item_key in self._items:
                del self._items[item_key]
                if item_key in self._discounts:
                    del self._discounts[item_key]
                return True
            return False

        def get_item(self, name: str) -> Optional[ShopItem]:
            """Get an item by name."""
            return self._items.get(name.lower())

        def list_items(self) -> List[ShopItem]:
            """Get all items in the shop."""
            return list(self._items.values())

        def list_available_items(self) -> List[ShopItem]:
            """Get all items that are in stock."""
            return [item for item in self._items.values() if item.is_available()]

        def set_discount(self, item_name: str, discount: float) -> bool:
            """
            Set a discount for a specific item.

            Args:
                item_name: Name of the item
                discount: Discount percentage (0.0 to 1.0)

            Returns:
                True if discount was set
            """
            item_key = item_name.lower()
            if item_key not in self._items:
                return False

            self._discounts[item_key] = max(0.0, min(1.0, discount))
            return True

        def set_global_discount(self, discount: float):
            """Set a global discount for all items."""
            self._global_discount = max(0.0, min(1.0, discount))

        def clear_discounts(self):
            """Clear all discounts."""
            self._discounts.clear()
            self._global_discount = 0.0

        def get_effective_discount(self, item_name: str) -> float:
            """Get the total effective discount for an item."""
            item_key = item_name.lower()
            item_discount = self._discounts.get(item_key, 0.0)
            # Discounts stack additively, capped at 90%
            return min(0.9, item_discount + self._global_discount)

        def get_price(self, item_name: str) -> int:
            """Get the current price of an item with discounts applied."""
            item = self.get_item(item_name)
            if not item:
                return 0

            discount = self.get_effective_discount(item_name)
            return item.get_price(discount)

        def get_sell_price(self, item_name: str, base_value: int) -> int:
            """
            Calculate how much the shop will pay for an item.

            Args:
                item_name: Name of the item being sold
                base_value: Base value of the item

            Returns:
                Amount the shop will pay
            """
            return max(1, int(base_value * self.buy_rate))

        def can_afford(self, item_name: str, wallet: Wallet) -> bool:
            """Check if a wallet can afford an item."""
            item = self.get_item(item_name)
            if not item:
                return False

            price = self.get_price(item_name)
            return wallet.has_enough(item.currency, price)

        def buy(self, item_name: str, wallet: Wallet,
               quantity: int = 1) -> TransactionResult:
            """
            Purchase an item from the shop.

            Args:
                item_name: Name of the item to buy
                wallet: Wallet to pay from
                quantity: Number of items to buy

            Returns:
                TransactionResult indicating success or failure
            """
            item = self.get_item(item_name)

            if not item:
                return TransactionResult(
                    False, f"Item not found: {item_name}", 0, ""
                )

            if quantity < 1:
                return TransactionResult(
                    False, "Quantity must be at least 1", 0, item.currency
                )

            # Check stock
            if item.stock >= 0 and item.stock < quantity:
                return TransactionResult(
                    False,
                    f"Insufficient stock (need {quantity}, have {item.stock})",
                    0,
                    item.currency
                )

            # Calculate total price
            unit_price = self.get_price(item_name)
            total_price = unit_price * quantity

            # Check if wallet can afford
            if not wallet.has_enough(item.currency, total_price):
                return TransactionResult(
                    False,
                    f"Insufficient funds (need {total_price} {item.currency})",
                    0,
                    item.currency
                )

            # Process purchase
            wallet.subtract(item.currency, total_price)

            # Update stock
            if item.stock > 0:
                item.stock -= quantity

            return TransactionResult(
                True,
                f"Purchased {quantity}x {item.name} for {total_price} {item.currency}",
                total_price,
                item.currency,
                TransactionType.PURCHASE
            )

        def sell(self, item_name: str, wallet: Wallet, base_value: int,
                quantity: int = 1) -> TransactionResult:
            """
            Sell an item to the shop.

            Args:
                item_name: Name of the item being sold
                wallet: Wallet to receive payment
                base_value: Base value of the item
                quantity: Number of items to sell

            Returns:
                TransactionResult indicating success or failure
            """
            if quantity < 1:
                return TransactionResult(
                    False, "Quantity must be at least 1", 0, "gold"
                )

            if base_value < 0:
                return TransactionResult(
                    False, "Base value cannot be negative", 0, "gold"
                )

            # Calculate payment
            unit_payment = self.get_sell_price(item_name, base_value)
            total_payment = unit_payment * quantity

            # Add to wallet
            wallet.add("gold", total_payment)

            # Optionally add to shop inventory
            existing_item = self.get_item(item_name)
            if existing_item and existing_item.stock >= 0:
                existing_item.stock += quantity

            return TransactionResult(
                True,
                f"Sold {quantity}x {item_name} for {total_payment} gold",
                total_payment,
                "gold",
                TransactionType.SALE
            )

        def restock(self, item_name: str, quantity: int) -> bool:
            """
            Add stock to an item.

            Args:
                item_name: Name of the item
                quantity: Amount to add

            Returns:
                True if restocked successfully
            """
            item = self.get_item(item_name)
            if not item or quantity < 0:
                return False

            if item.stock < 0:
                # Item has unlimited stock
                return True

            item.stock += quantity
            return True

        def to_dict(self) -> dict:
            """Convert shop to dictionary for saving."""
            return {
                "name": self.name,
                "buy_rate": self.buy_rate,
                "items": {
                    key: {
                        "name": item.name,
                        "base_price": item.base_price,
                        "currency": item.currency,
                        "stock": item.stock,
                        "description": item.description
                    }
                    for key, item in self._items.items()
                },
                "discounts": dict(self._discounts),
                "global_discount": self._global_discount
            }

        @classmethod
        def from_dict(cls, data: dict) -> 'Shop':
            """Create shop from saved dictionary."""
            shop = cls(data.get("name", "Shop"), data.get("buy_rate", 0.5))

            for item_data in data.get("items", {}).values():
                shop.add_item(
                    item_data["name"],
                    item_data["currency"],
                    item_data["base_price"],
                    item_data.get("stock", -1),
                    item_data.get("description", "")
                )

            shop._discounts = data.get("discounts", {})
            shop._global_discount = data.get("global_discount", 0.0)

            return shop


    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================

    def create_wallet() -> Wallet:
        """Create a new wallet with default currencies."""
        return Wallet()

    def create_shop(name: str, buy_rate: float = 0.5) -> Shop:
        """Create a new shop."""
        return Shop(name, buy_rate)

    def format_currency(amount: int, currency_name: str, wallet: Wallet = None) -> str:
        """Format a currency amount for display."""
        if wallet and currency_name.lower() in wallet.currencies:
            currency = wallet.currencies[currency_name.lower()]
            return currency.format_amount(amount)
        return f"{amount} {currency_name}"


# ============================================================================
# DEFAULT GAME VARIABLES
# ============================================================================

default player_wallet = None
default current_shop = None


# ============================================================================
# SHOP SCREEN
# ============================================================================

screen shop_screen(shop):
    tag menu
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 40
        ypadding 30
        xminimum 600

        vbox:
            spacing 15

            # Shop name
            text shop.name size 36 xalign 0.5 color "#ffffff"

            null height 10

            # Wallet display
            if player_wallet:
                hbox:
                    spacing 20
                    xalign 0.5
                    text "Your Gold: [player_wallet.get_balance('gold')]G" size 20 color "#ffdd44"
                    text "Gems: [player_wallet.get_balance('gems')]D" size 20 color "#44ddff"

            null height 15

            # Items list
            text "Available Items:" size 22 color "#ffffff"

            viewport:
                scrollbars "vertical"
                ymaximum 300
                xmaximum 520

                vbox:
                    spacing 10

                    for item in shop.list_available_items():
                        $ price = shop.get_price(item.name)
                        $ can_buy = player_wallet and player_wallet.has_enough(item.currency, price)
                        $ discount = shop.get_effective_discount(item.name)

                        frame:
                            xfill True
                            xpadding 10
                            ypadding 8

                            hbox:
                                spacing 15

                                vbox:
                                    text item.name size 18 color "#ffffff"
                                    if item.description:
                                        text item.description size 14 color "#aaaaaa"
                                    if item.stock >= 0:
                                        text "Stock: [item.stock]" size 12 color "#888888"

                                null width 20

                                vbox:
                                    xalign 1.0
                                    if discount > 0:
                                        text "[item.base_price]" size 14 color "#888888" strikethrough True
                                    text "[price] [item.currency.upper()]" size 18 color "#ffdd44"

                                    if can_buy:
                                        textbutton "Buy" action Function(shop.buy, item.name, player_wallet) text_size 16
                                    else:
                                        text "Cannot Afford" size 14 color "#ff4444"

            null height 20

            # Close button
            textbutton "Close Shop" action Return() xalign 0.5 text_size 22
