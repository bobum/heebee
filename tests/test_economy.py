"""
Tests for the economy system (game/economy.rpy).

Tests cover:
- Currency creation and conversion
- Wallet operations (add, subtract, check balance)
- Shop buying and selling
- Price calculations and discounts
- Transaction validation
- Multiple currency types
"""
import pytest


class TestCurrency:
    """Tests for the Currency class."""

    def test_currency_creation(self, load_system):
        """Test basic currency creation."""
        ns = load_system("economy")
        Currency = ns["Currency"]

        gold = Currency("gold", "G", 1.0)
        assert gold.name == "gold"
        assert gold.symbol == "G"
        assert gold.exchange_rate == 1.0

    def test_currency_default_symbol(self, load_system):
        """Test that currency uses first letter as default symbol."""
        ns = load_system("economy")
        Currency = ns["Currency"]

        currency = Currency("platinum")
        assert currency.symbol == "P"

    def test_currency_format_amount(self, load_system):
        """Test currency amount formatting."""
        ns = load_system("economy")
        Currency = ns["Currency"]

        gold = Currency("gold", "G")
        assert gold.format_amount(100) == "100G"
        assert gold.format_amount(0) == "0G"

    def test_currency_conversion(self, load_system):
        """Test converting between currencies."""
        ns = load_system("economy")
        Currency = ns["Currency"]

        gold = Currency("gold", "G", 1.0)
        gems = Currency("gems", "D", 100.0)  # 1 gem = 100 gold

        # 100 gold = 1 gem
        assert gold.convert_to(100, gems) == 1

        # 1 gem = 100 gold
        assert gems.convert_to(1, gold) == 100

        # Partial conversion rounds down
        assert gold.convert_to(50, gems) == 0
        assert gold.convert_to(150, gems) == 1

    def test_currency_conversion_zero_rate(self, load_system):
        """Test conversion with zero exchange rate."""
        ns = load_system("economy")
        Currency = ns["Currency"]

        gold = Currency("gold", "G", 1.0)
        broken = Currency("broken", "X", 0.0)

        assert gold.convert_to(100, broken) == 0


class TestWallet:
    """Tests for the Wallet class."""

    def test_wallet_creation(self, load_system):
        """Test wallet creation with default currencies."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        assert wallet.get_balance("gold") == 0
        assert wallet.get_balance("gems") == 0
        assert wallet.get_balance("silver") == 0

    def test_wallet_add_currency(self, load_system):
        """Test adding currency to wallet."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        result = wallet.add("gold", 100)

        assert result.success
        assert wallet.get_balance("gold") == 100
        assert result.amount == 100

    def test_wallet_add_negative_amount(self, load_system):
        """Test that adding negative amount fails."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        result = wallet.add("gold", -50)

        assert not result.success
        assert wallet.get_balance("gold") == 0
        assert "negative" in result.message.lower()

    def test_wallet_add_unknown_currency(self, load_system):
        """Test adding unknown currency fails."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        result = wallet.add("unknown", 100)

        assert not result.success
        assert "unknown" in result.message.lower()

    def test_wallet_subtract_currency(self, load_system):
        """Test subtracting currency from wallet."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 100)
        result = wallet.subtract("gold", 30)

        assert result.success
        assert wallet.get_balance("gold") == 70
        assert result.amount == 30

    def test_wallet_subtract_insufficient_funds(self, load_system):
        """Test subtracting more than available fails."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 50)
        result = wallet.subtract("gold", 100)

        assert not result.success
        assert wallet.get_balance("gold") == 50
        assert "insufficient" in result.message.lower()

    def test_wallet_subtract_negative_amount(self, load_system):
        """Test that subtracting negative amount fails."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 100)
        result = wallet.subtract("gold", -50)

        assert not result.success
        assert wallet.get_balance("gold") == 100

    def test_wallet_has_enough(self, load_system):
        """Test checking if wallet has enough currency."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 100)

        assert wallet.has_enough("gold", 50)
        assert wallet.has_enough("gold", 100)
        assert not wallet.has_enough("gold", 150)

    def test_wallet_transfer(self, load_system):
        """Test transferring currency between wallets."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet1 = Wallet()
        wallet2 = Wallet()
        wallet1.add("gold", 100)

        result = wallet1.transfer(wallet2, "gold", 40)

        assert result.success
        assert wallet1.get_balance("gold") == 60
        assert wallet2.get_balance("gold") == 40

    def test_wallet_transfer_insufficient_funds(self, load_system):
        """Test transfer with insufficient funds fails."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet1 = Wallet()
        wallet2 = Wallet()
        wallet1.add("gold", 50)

        result = wallet1.transfer(wallet2, "gold", 100)

        assert not result.success
        assert wallet1.get_balance("gold") == 50
        assert wallet2.get_balance("gold") == 0

    def test_wallet_convert_currency(self, load_system):
        """Test converting between currencies in wallet."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 100)

        result = wallet.convert("gold", "gems", 100)

        assert result.success
        assert wallet.get_balance("gold") == 0
        assert wallet.get_balance("gems") == 1  # 100 gold = 1 gem

    def test_wallet_convert_insufficient_funds(self, load_system):
        """Test conversion with insufficient funds fails."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 50)

        result = wallet.convert("gold", "gems", 100)

        assert not result.success
        assert wallet.get_balance("gold") == 50

    def test_wallet_register_custom_currency(self, load_system):
        """Test registering a custom currency."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]
        Currency = ns["Currency"]

        wallet = Wallet()
        platinum = Currency("platinum", "P", 1000.0)

        assert wallet.register_currency(platinum)
        assert wallet.get_balance("platinum") == 0

        wallet.add("platinum", 5)
        assert wallet.get_balance("platinum") == 5

    def test_wallet_register_duplicate_currency(self, load_system):
        """Test registering duplicate currency fails."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]
        Currency = ns["Currency"]

        wallet = Wallet()
        gold = Currency("gold", "X", 1.0)

        assert not wallet.register_currency(gold)

    def test_wallet_transaction_history(self, load_system):
        """Test transaction history tracking."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 100)
        wallet.subtract("gold", 30)
        wallet.add("gems", 5)

        history = wallet.get_transaction_history()
        assert len(history) == 3
        assert all(r.success for r in history)

    def test_wallet_clear_history(self, load_system):
        """Test clearing transaction history."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 100)
        wallet.clear_history()

        assert len(wallet.get_transaction_history()) == 0

    def test_wallet_get_all_balances(self, load_system):
        """Test getting all balances at once."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 100)
        wallet.add("gems", 5)

        balances = wallet.get_all_balances()
        assert balances["gold"] == 100
        assert balances["gems"] == 5
        assert balances["silver"] == 0

    def test_wallet_max_amount_cap(self, load_system):
        """Test that wallet respects maximum currency amounts."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]
        Currency = ns["Currency"]

        # Create wallet with low-cap currency
        limited = Currency("limited", "L", 1.0, max_amount=100)
        wallet = Wallet({limited.name: limited})

        wallet.add("limited", 150)
        assert wallet.get_balance("limited") == 100

    def test_wallet_serialization(self, load_system):
        """Test wallet save/load functionality."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet1 = Wallet()
        wallet1.add("gold", 100)
        wallet1.add("gems", 5)

        data = wallet1.to_dict()
        wallet2 = Wallet.from_dict(data)

        assert wallet2.get_balance("gold") == 100
        assert wallet2.get_balance("gems") == 5


class TestShopItem:
    """Tests for the ShopItem class."""

    def test_shop_item_creation(self, load_system):
        """Test basic shop item creation."""
        ns = load_system("economy")
        ShopItem = ns["ShopItem"]

        item = ShopItem("Health Potion", 25, "gold", 10)
        assert item.name == "Health Potion"
        assert item.base_price == 25
        assert item.currency == "gold"
        assert item.stock == 10

    def test_shop_item_unlimited_stock(self, load_system):
        """Test unlimited stock item."""
        ns = load_system("economy")
        ShopItem = ns["ShopItem"]

        item = ShopItem("Common Item", 10, stock=-1)
        assert item.is_available()
        assert item.stock == -1

    def test_shop_item_out_of_stock(self, load_system):
        """Test out of stock detection."""
        ns = load_system("economy")
        ShopItem = ns["ShopItem"]

        item = ShopItem("Rare Item", 100, stock=0)
        assert not item.is_available()

    def test_shop_item_price_with_discount(self, load_system):
        """Test item price calculation with discount."""
        ns = load_system("economy")
        ShopItem = ns["ShopItem"]

        item = ShopItem("Item", 100)

        assert item.get_price(0.0) == 100
        assert item.get_price(0.1) == 90
        assert item.get_price(0.5) == 50
        assert item.get_price(0.9) == 9

    def test_shop_item_minimum_price(self, load_system):
        """Test that item price never goes below 1."""
        ns = load_system("economy")
        ShopItem = ns["ShopItem"]

        item = ShopItem("Cheap Item", 10)

        # Even with 100% discount, price is minimum 1
        assert item.get_price(1.0) == 1

    def test_shop_item_discount_clamping(self, load_system):
        """Test that discount is clamped between 0 and 1."""
        ns = load_system("economy")
        ShopItem = ns["ShopItem"]

        item = ShopItem("Item", 100)

        # Negative discount treated as 0
        assert item.get_price(-0.5) == 100

        # Discount over 1 treated as 1
        assert item.get_price(1.5) == 1


class TestShop:
    """Tests for the Shop class."""

    def test_shop_creation(self, load_system):
        """Test basic shop creation."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("General Store")
        assert shop.name == "General Store"
        assert shop.buy_rate == 0.5  # Default

    def test_shop_add_item(self, load_system):
        """Test adding items to shop."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        assert shop.add_item("Sword", "gold", 100, 5)

        item = shop.get_item("Sword")
        assert item is not None
        assert item.name == "Sword"
        assert item.base_price == 100

    def test_shop_add_duplicate_item(self, load_system):
        """Test adding duplicate item fails."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        assert shop.add_item("Sword", "gold", 100)
        assert not shop.add_item("Sword", "gold", 200)

    def test_shop_remove_item(self, load_system):
        """Test removing items from shop."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Sword", "gold", 100)

        assert shop.remove_item("Sword")
        assert shop.get_item("Sword") is None

    def test_shop_list_items(self, load_system):
        """Test listing all items."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Sword", "gold", 100)
        shop.add_item("Shield", "gold", 75)

        items = shop.list_items()
        assert len(items) == 2

    def test_shop_list_available_items(self, load_system):
        """Test listing only available items."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Sword", "gold", 100, stock=1)
        shop.add_item("Shield", "gold", 75, stock=0)

        available = shop.list_available_items()
        assert len(available) == 1
        assert available[0].name == "Sword"

    def test_shop_buy_success(self, load_system):
        """Test successful purchase."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        shop.add_item("Potion", "gold", 25, stock=5)

        wallet = Wallet()
        wallet.add("gold", 100)

        result = shop.buy("Potion", wallet)

        assert result.success
        assert wallet.get_balance("gold") == 75
        assert shop.get_item("Potion").stock == 4

    def test_shop_buy_multiple(self, load_system):
        """Test buying multiple items at once."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        shop.add_item("Potion", "gold", 10, stock=10)

        wallet = Wallet()
        wallet.add("gold", 100)

        result = shop.buy("Potion", wallet, quantity=3)

        assert result.success
        assert wallet.get_balance("gold") == 70
        assert shop.get_item("Potion").stock == 7

    def test_shop_buy_insufficient_funds(self, load_system):
        """Test purchase with insufficient funds fails."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        shop.add_item("Expensive", "gold", 1000)

        wallet = Wallet()
        wallet.add("gold", 100)

        result = shop.buy("Expensive", wallet)

        assert not result.success
        assert wallet.get_balance("gold") == 100
        assert "insufficient" in result.message.lower()

    def test_shop_buy_out_of_stock(self, load_system):
        """Test purchase of out-of-stock item fails."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        shop.add_item("Rare", "gold", 50, stock=0)

        wallet = Wallet()
        wallet.add("gold", 100)

        result = shop.buy("Rare", wallet)

        assert not result.success
        assert "stock" in result.message.lower()

    def test_shop_buy_nonexistent_item(self, load_system):
        """Test purchase of nonexistent item fails."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        wallet = Wallet()
        wallet.add("gold", 100)

        result = shop.buy("Nonexistent", wallet)

        assert not result.success
        assert "not found" in result.message.lower()

    def test_shop_buy_unlimited_stock(self, load_system):
        """Test buying from unlimited stock."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        shop.add_item("Common", "gold", 10, stock=-1)

        wallet = Wallet()
        wallet.add("gold", 100)

        # Buy multiple times
        for _ in range(5):
            result = shop.buy("Common", wallet)
            assert result.success

        # Stock should still be unlimited
        assert shop.get_item("Common").stock == -1

    def test_shop_sell(self, load_system):
        """Test selling items to shop."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop", buy_rate=0.5)
        wallet = Wallet()

        result = shop.sell("Old Sword", wallet, base_value=100)

        assert result.success
        assert wallet.get_balance("gold") == 50  # 50% of 100

    def test_shop_sell_multiple(self, load_system):
        """Test selling multiple items."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop", buy_rate=0.5)
        wallet = Wallet()

        result = shop.sell("Potion", wallet, base_value=20, quantity=5)

        assert result.success
        assert wallet.get_balance("gold") == 50  # 5 * (20 * 0.5)

    def test_shop_sell_restocks_inventory(self, load_system):
        """Test that selling adds to shop inventory."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        shop.add_item("Potion", "gold", 20, stock=0)
        wallet = Wallet()

        shop.sell("Potion", wallet, base_value=20, quantity=3)

        assert shop.get_item("Potion").stock == 3

    def test_shop_item_discount(self, load_system):
        """Test setting discount on specific item."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Item", "gold", 100)

        shop.set_discount("Item", 0.2)

        assert shop.get_price("Item") == 80

    def test_shop_global_discount(self, load_system):
        """Test global discount on all items."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Item1", "gold", 100)
        shop.add_item("Item2", "gold", 200)

        shop.set_global_discount(0.1)

        assert shop.get_price("Item1") == 90
        assert shop.get_price("Item2") == 180

    def test_shop_stacked_discounts(self, load_system):
        """Test that discounts stack additively."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Item", "gold", 100)

        shop.set_global_discount(0.1)
        shop.set_discount("Item", 0.2)

        # Total discount: 30%
        assert shop.get_price("Item") == 70

    def test_shop_discount_cap(self, load_system):
        """Test that total discount is capped at 90%."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Item", "gold", 100)

        shop.set_global_discount(0.5)
        shop.set_discount("Item", 0.5)

        # Would be 100% but capped at 90%
        assert shop.get_effective_discount("Item") == 0.9
        assert shop.get_price("Item") == 9

    def test_shop_clear_discounts(self, load_system):
        """Test clearing all discounts."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Item", "gold", 100)
        shop.set_global_discount(0.1)
        shop.set_discount("Item", 0.2)

        shop.clear_discounts()

        assert shop.get_price("Item") == 100

    def test_shop_can_afford(self, load_system):
        """Test checking if wallet can afford item."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Test Shop")
        shop.add_item("Cheap", "gold", 50)
        shop.add_item("Expensive", "gold", 500)

        wallet = Wallet()
        wallet.add("gold", 100)

        assert shop.can_afford("Cheap", wallet)
        assert not shop.can_afford("Expensive", wallet)

    def test_shop_restock(self, load_system):
        """Test restocking items."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Item", "gold", 100, stock=5)

        assert shop.restock("Item", 10)
        assert shop.get_item("Item").stock == 15

    def test_shop_restock_unlimited(self, load_system):
        """Test restocking unlimited stock item."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop = Shop("Test Shop")
        shop.add_item("Item", "gold", 100, stock=-1)

        assert shop.restock("Item", 10)
        assert shop.get_item("Item").stock == -1

    def test_shop_buy_rate(self, load_system):
        """Test different buy rates."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop_low = Shop("Low", buy_rate=0.25)
        shop_high = Shop("High", buy_rate=0.75)

        assert shop_low.get_sell_price("item", 100) == 25
        assert shop_high.get_sell_price("item", 100) == 75

    def test_shop_serialization(self, load_system):
        """Test shop save/load functionality."""
        ns = load_system("economy")
        Shop = ns["Shop"]

        shop1 = Shop("Test Shop", buy_rate=0.6)
        shop1.add_item("Sword", "gold", 100, stock=5)
        shop1.add_item("Shield", "gold", 75, stock=3)
        shop1.set_discount("Sword", 0.1)

        data = shop1.to_dict()
        shop2 = Shop.from_dict(data)

        assert shop2.name == "Test Shop"
        assert shop2.buy_rate == 0.6
        assert shop2.get_item("Sword").base_price == 100
        assert shop2.get_item("Shield").stock == 3


class TestTransactionResult:
    """Tests for the TransactionResult class."""

    def test_transaction_result_bool(self, load_system):
        """Test that TransactionResult is truthy/falsy based on success."""
        ns = load_system("economy")
        TransactionResult = ns["TransactionResult"]

        success = TransactionResult(True, "OK")
        failure = TransactionResult(False, "Failed")

        assert success
        assert not failure

    def test_transaction_result_repr(self, load_system):
        """Test TransactionResult string representation."""
        ns = load_system("economy")
        TransactionResult = ns["TransactionResult"]

        result = TransactionResult(True, "Test message")
        repr_str = repr(result)

        assert "Success" in repr_str
        assert "Test message" in repr_str


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_create_wallet(self, load_system):
        """Test create_wallet helper."""
        ns = load_system("economy")
        create_wallet = ns["create_wallet"]

        wallet = create_wallet()
        assert wallet is not None
        assert wallet.get_balance("gold") == 0

    def test_create_shop(self, load_system):
        """Test create_shop helper."""
        ns = load_system("economy")
        create_shop = ns["create_shop"]

        shop = create_shop("My Shop", 0.4)
        assert shop.name == "My Shop"
        assert shop.buy_rate == 0.4

    def test_format_currency(self, load_system):
        """Test format_currency helper."""
        ns = load_system("economy")
        format_currency = ns["format_currency"]
        Wallet = ns["Wallet"]

        wallet = Wallet()
        formatted = format_currency(100, "gold", wallet)
        assert formatted == "100G"

    def test_format_currency_no_wallet(self, load_system):
        """Test format_currency without wallet."""
        ns = load_system("economy")
        format_currency = ns["format_currency"]

        formatted = format_currency(100, "platinum")
        assert formatted == "100 platinum"


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_shopping_workflow(self, load_system):
        """Test a complete shopping workflow."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        # Setup shop
        shop = Shop("Adventure Supplies")
        shop.add_item("Health Potion", "gold", 25, stock=10)
        shop.add_item("Mana Potion", "gold", 30, stock=10)
        shop.add_item("Antidote", "gold", 15, stock=5)

        # Setup wallet
        wallet = Wallet()
        wallet.add("gold", 100)

        # Buy some items
        assert shop.buy("Health Potion", wallet, quantity=2).success
        assert shop.buy("Antidote", wallet).success

        # Check results
        assert wallet.get_balance("gold") == 35  # 100 - 50 - 15
        assert shop.get_item("Health Potion").stock == 8
        assert shop.get_item("Antidote").stock == 4

        # Sell an item
        assert shop.sell("Old Equipment", wallet, base_value=40).success
        assert wallet.get_balance("gold") == 55  # 35 + 20

    def test_multi_currency_shopping(self, load_system):
        """Test shopping with multiple currencies."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Premium Shop")
        shop.add_item("Common Item", "gold", 50)
        shop.add_item("Rare Item", "gems", 5)

        wallet = Wallet()
        wallet.add("gold", 100)
        wallet.add("gems", 10)

        # Buy with gold
        assert shop.buy("Common Item", wallet).success
        assert wallet.get_balance("gold") == 50

        # Buy with gems
        assert shop.buy("Rare Item", wallet).success
        assert wallet.get_balance("gems") == 5

    def test_discount_event(self, load_system):
        """Test a shop sale event."""
        ns = load_system("economy")
        Shop = ns["Shop"]
        Wallet = ns["Wallet"]

        shop = Shop("Event Shop")
        shop.add_item("Normal Item", "gold", 100)
        shop.add_item("Featured Item", "gold", 200)

        wallet = Wallet()
        wallet.add("gold", 200)

        # Apply sale
        shop.set_global_discount(0.1)  # 10% off everything
        shop.set_discount("Featured Item", 0.15)  # Additional 15% off featured

        # Buy featured item (25% off total = 150)
        result = shop.buy("Featured Item", wallet)
        assert result.success
        assert wallet.get_balance("gold") == 50  # 200 - 150

    def test_currency_exchange(self, load_system):
        """Test converting currencies in wallet."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        wallet = Wallet()
        wallet.add("gold", 500)

        # Convert gold to gems
        result = wallet.convert("gold", "gems", 200)
        assert result.success

        assert wallet.get_balance("gold") == 300
        assert wallet.get_balance("gems") == 2  # 200 gold = 2 gems

        # Convert gems back to gold
        result = wallet.convert("gems", "gold", 1)
        assert result.success

        assert wallet.get_balance("gems") == 1
        assert wallet.get_balance("gold") == 400  # 300 + 100

    def test_wallet_transfer_between_players(self, load_system):
        """Test transferring currency between wallets."""
        ns = load_system("economy")
        Wallet = ns["Wallet"]

        player_wallet = Wallet()
        npc_wallet = Wallet()

        player_wallet.add("gold", 100)

        # Transfer to NPC
        result = player_wallet.transfer(npc_wallet, "gold", 30)
        assert result.success

        assert player_wallet.get_balance("gold") == 70
        assert npc_wallet.get_balance("gold") == 30
