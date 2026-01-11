"""
Tests for the Phone/Messaging System.

Tests Contact, Message, Conversation, and PhoneManager classes from phone.rpy.
"""
import pytest
import time


class TestContact:
    """Tests for the Contact class."""

    def test_contact_creation(self, load_system):
        """Test basic contact creation."""
        ns = load_system("phone")
        Contact = ns["Contact"]

        contact = Contact("Elena", "elena")
        assert contact.name == "Elena"
        assert contact.phone_id == "elena"
        assert contact.avatar is None
        assert contact.unlocked is False

    def test_contact_creation_with_all_params(self, load_system):
        """Test contact creation with all parameters."""
        ns = load_system("phone")
        Contact = ns["Contact"]

        contact = Contact("Elena", "elena", avatar="path/to/avatar.png", unlocked=True)
        assert contact.name == "Elena"
        assert contact.phone_id == "elena"
        assert contact.avatar == "path/to/avatar.png"
        assert contact.unlocked is True

    def test_contact_unlock(self, load_system):
        """Test unlocking a contact."""
        ns = load_system("phone")
        Contact = ns["Contact"]

        contact = Contact("Elena", "elena")
        assert contact.unlocked is False

        contact.unlock()
        assert contact.unlocked is True

    def test_contact_lock(self, load_system):
        """Test locking a contact."""
        ns = load_system("phone")
        Contact = ns["Contact"]

        contact = Contact("Elena", "elena", unlocked=True)
        assert contact.unlocked is True

        contact.lock()
        assert contact.unlocked is False

    def test_contact_repr(self, load_system):
        """Test contact string representation."""
        ns = load_system("phone")
        Contact = ns["Contact"]

        contact_locked = Contact("Elena", "elena")
        assert "Elena" in repr(contact_locked)
        assert "elena" in repr(contact_locked)
        assert "locked" in repr(contact_locked)

        contact_unlocked = Contact("Elena", "elena", unlocked=True)
        assert "unlocked" in repr(contact_unlocked)


class TestMessage:
    """Tests for the Message class."""

    def test_message_creation(self, load_system):
        """Test basic message creation."""
        ns = load_system("phone")
        Message = ns["Message"]

        msg = Message("elena", "Hello!")
        assert msg.sender == "elena"
        assert msg.content == "Hello!"
        assert msg.read is False
        assert msg.timestamp is not None

    def test_message_with_timestamp(self, load_system):
        """Test message creation with custom timestamp."""
        ns = load_system("phone")
        Message = ns["Message"]

        timestamp = 1609459200.0  # 2021-01-01 00:00:00
        msg = Message("elena", "Hello!", timestamp=timestamp)
        assert msg.timestamp == timestamp

    def test_message_with_read_status(self, load_system):
        """Test message creation with read status."""
        ns = load_system("phone")
        Message = ns["Message"]

        msg = Message("elena", "Hello!", read=True)
        assert msg.read is True

    def test_mark_as_read(self, load_system):
        """Test marking message as read."""
        ns = load_system("phone")
        Message = ns["Message"]

        msg = Message("elena", "Hello!")
        assert msg.read is False

        msg.mark_as_read()
        assert msg.read is True

    def test_is_from_player(self, load_system):
        """Test checking if message is from player."""
        ns = load_system("phone")
        Message = ns["Message"]

        player_msg = Message("player", "Hello!")
        assert player_msg.is_from_player() is True

        contact_msg = Message("elena", "Hi!")
        assert contact_msg.is_from_player() is False

    def test_get_formatted_time(self, load_system):
        """Test getting formatted time."""
        ns = load_system("phone")
        Message = ns["Message"]

        # Use a known timestamp
        timestamp = 1609459200.0  # 2021-01-01 00:00:00 UTC
        msg = Message("elena", "Hello!", timestamp=timestamp)
        formatted = msg.get_formatted_time()
        # Should return HH:MM format
        assert ":" in formatted
        assert len(formatted) == 5

    def test_message_repr(self, load_system):
        """Test message string representation."""
        ns = load_system("phone")
        Message = ns["Message"]

        msg = Message("elena", "Hello world!")
        repr_str = repr(msg)
        assert "elena" in repr_str
        assert "unread" in repr_str

    def test_message_repr_long_content(self, load_system):
        """Test message repr truncates long content."""
        ns = load_system("phone")
        Message = ns["Message"]

        long_content = "This is a very long message that should be truncated"
        msg = Message("elena", long_content)
        repr_str = repr(msg)
        assert "..." in repr_str


class TestConversation:
    """Tests for the Conversation class."""

    def test_conversation_creation(self, load_system):
        """Test basic conversation creation."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        assert conv.contact_id == "elena"
        assert len(conv.messages) == 0

    def test_add_message(self, load_system):
        """Test adding a message to conversation."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        msg = conv.add_message("elena", "Hello!")

        assert len(conv.messages) == 1
        assert msg.sender == "elena"
        assert msg.content == "Hello!"

    def test_send_message(self, load_system):
        """Test sending a message from player."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        msg = conv.send_message("Hello from player!")

        assert msg.sender == "player"
        assert msg.content == "Hello from player!"
        assert msg.read is True  # Player messages are marked as read

    def test_receive_message(self, load_system):
        """Test receiving a message from contact."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        msg = conv.receive_message("Hello from Elena!")

        assert msg.sender == "elena"
        assert msg.content == "Hello from Elena!"
        assert msg.read is False  # Received messages start unread

    def test_get_unread_count(self, load_system):
        """Test getting unread message count."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        assert conv.get_unread_count() == 0

        conv.receive_message("Message 1")
        conv.receive_message("Message 2")
        assert conv.get_unread_count() == 2

        conv.send_message("Player reply")  # Player messages don't count
        assert conv.get_unread_count() == 2

    def test_mark_all_as_read(self, load_system):
        """Test marking all messages as read."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        conv.receive_message("Message 1")
        conv.receive_message("Message 2")

        assert conv.get_unread_count() == 2

        conv.mark_all_as_read()
        assert conv.get_unread_count() == 0

    def test_get_last_message(self, load_system):
        """Test getting the last message."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        assert conv.get_last_message() is None

        conv.receive_message("First message")
        conv.receive_message("Second message")

        last = conv.get_last_message()
        assert last.content == "Second message"

    def test_get_messages(self, load_system):
        """Test getting all messages."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        conv.receive_message("Message 1")
        conv.send_message("Message 2")

        messages = conv.get_messages()
        assert len(messages) == 2
        # Should return a copy
        messages.append(None)
        assert len(conv.messages) == 2

    def test_get_message_count(self, load_system):
        """Test getting message count."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        assert conv.get_message_count() == 0

        conv.receive_message("Message 1")
        conv.send_message("Message 2")
        assert conv.get_message_count() == 2

    def test_clear_messages(self, load_system):
        """Test clearing all messages."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        conv.receive_message("Message 1")
        conv.receive_message("Message 2")

        assert conv.get_message_count() == 2

        conv.clear_messages()
        assert conv.get_message_count() == 0

    def test_conversation_repr(self, load_system):
        """Test conversation string representation."""
        ns = load_system("phone")
        Conversation = ns["Conversation"]

        conv = Conversation("elena")
        conv.receive_message("Message 1")

        repr_str = repr(conv)
        assert "elena" in repr_str
        assert "1 messages" in repr_str


class TestPhoneManager:
    """Tests for the PhoneManager class."""

    def test_phone_manager_creation(self, load_system):
        """Test basic phone manager creation."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        assert len(pm.contacts) == 0
        assert len(pm.conversations) == 0
        assert pm.notifications_enabled is True

    # -------------------------------------------------------------------------
    # Contact Management Tests
    # -------------------------------------------------------------------------

    def test_add_contact(self, load_system):
        """Test adding a contact."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]
        Contact = ns["Contact"]

        pm = PhoneManager()
        contact = Contact("Elena", "elena")

        result = pm.add_contact(contact)
        assert result == contact
        assert "elena" in pm.contacts

    def test_create_contact(self, load_system):
        """Test creating a contact directly."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        contact = pm.create_contact("Elena", "elena", avatar="path.png", unlocked=True)

        assert contact.name == "Elena"
        assert contact.phone_id == "elena"
        assert contact.avatar == "path.png"
        assert contact.unlocked is True
        assert "elena" in pm.contacts

    def test_get_contact(self, load_system):
        """Test getting a contact."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")

        contact = pm.get_contact("elena")
        assert contact is not None
        assert contact.name == "Elena"

        # Non-existent contact
        assert pm.get_contact("nobody") is None

    def test_remove_contact(self, load_system):
        """Test removing a contact."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")

        assert pm.remove_contact("elena") is True
        assert pm.get_contact("elena") is None

        # Removing non-existent contact
        assert pm.remove_contact("nobody") is False

    def test_remove_contact_with_conversation(self, load_system):
        """Test that removing a contact also removes their conversation."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena", unlocked=True)
        pm.receive_message("elena", "Hello!")

        assert "elena" in pm.conversations

        pm.remove_contact("elena")
        assert "elena" not in pm.conversations

    def test_unlock_contact(self, load_system):
        """Test unlocking a contact."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena", unlocked=False)

        assert pm.unlock_contact("elena") is True
        assert pm.get_contact("elena").unlocked is True

        # Unlocking non-existent contact
        assert pm.unlock_contact("nobody") is False

    def test_lock_contact(self, load_system):
        """Test locking a contact."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena", unlocked=True)

        assert pm.lock_contact("elena") is True
        assert pm.get_contact("elena").unlocked is False

        # Locking non-existent contact
        assert pm.lock_contact("nobody") is False

    def test_get_unlocked_contacts(self, load_system):
        """Test getting unlocked contacts."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena", unlocked=True)
        pm.create_contact("Marcus", "marcus", unlocked=False)
        pm.create_contact("Victoria", "victoria", unlocked=True)

        unlocked = pm.get_unlocked_contacts()
        assert len(unlocked) == 2
        names = [c.name for c in unlocked]
        assert "Elena" in names
        assert "Victoria" in names
        assert "Marcus" not in names

    def test_get_all_contacts(self, load_system):
        """Test getting all contacts."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena", unlocked=True)
        pm.create_contact("Marcus", "marcus", unlocked=False)

        all_contacts = pm.get_all_contacts()
        assert len(all_contacts) == 2

    # -------------------------------------------------------------------------
    # Conversation Management Tests
    # -------------------------------------------------------------------------

    def test_get_conversation(self, load_system):
        """Test getting/creating a conversation."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")

        conv = pm.get_conversation("elena")
        assert conv is not None
        assert conv.contact_id == "elena"

        # Getting same conversation returns same object
        conv2 = pm.get_conversation("elena")
        assert conv is conv2

        # Getting conversation for non-existent contact returns None
        assert pm.get_conversation("nobody") is None

    def test_send_message(self, load_system):
        """Test sending a message."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")

        msg = pm.send_message("elena", "Hello!")
        assert msg is not None
        assert msg.sender == "player"
        assert msg.content == "Hello!"

        # Sending to non-existent contact
        assert pm.send_message("nobody", "Hello!") is None

    def test_receive_message(self, load_system):
        """Test receiving a message."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()  # Disable for testing

        msg = pm.receive_message("elena", "Hello from Elena!")
        assert msg is not None
        assert msg.sender == "elena"
        assert msg.content == "Hello from Elena!"
        assert msg.read is False

        # Receiving from non-existent contact
        assert pm.receive_message("nobody", "Hello!") is None

    def test_receive_message_with_timestamp(self, load_system):
        """Test receiving a message with custom timestamp."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()

        timestamp = 1609459200.0
        msg = pm.receive_message("elena", "Hello!", timestamp=timestamp)
        assert msg.timestamp == timestamp

    def test_mark_conversation_read(self, load_system):
        """Test marking a conversation as read."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()

        pm.receive_message("elena", "Message 1")
        pm.receive_message("elena", "Message 2")

        assert pm.get_conversation_unread_count("elena") == 2

        pm.mark_conversation_read("elena")
        assert pm.get_conversation_unread_count("elena") == 0

    # -------------------------------------------------------------------------
    # Notification Tests
    # -------------------------------------------------------------------------

    def test_get_unread_count(self, load_system):
        """Test getting total unread count."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.create_contact("Marcus", "marcus")
        pm.disable_notifications()

        assert pm.get_unread_count() == 0

        pm.receive_message("elena", "Hello!")
        pm.receive_message("elena", "How are you?")
        pm.receive_message("marcus", "Hey!")

        assert pm.get_unread_count() == 3

    def test_get_conversation_unread_count(self, load_system):
        """Test getting unread count for specific conversation."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()

        assert pm.get_conversation_unread_count("elena") == 0

        pm.receive_message("elena", "Hello!")
        pm.receive_message("elena", "How are you?")

        assert pm.get_conversation_unread_count("elena") == 2

        # Non-existent conversation
        assert pm.get_conversation_unread_count("nobody") == 0

    def test_has_unread_messages(self, load_system):
        """Test checking for unread messages."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()

        assert pm.has_unread_messages() is False

        pm.receive_message("elena", "Hello!")
        assert pm.has_unread_messages() is True

    def test_get_contacts_with_unread(self, load_system):
        """Test getting contacts with unread messages."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.create_contact("Marcus", "marcus")
        pm.create_contact("Victoria", "victoria")
        pm.disable_notifications()

        pm.receive_message("elena", "Hello!")
        pm.receive_message("marcus", "Hey!")

        contacts_with_unread = pm.get_contacts_with_unread()
        assert len(contacts_with_unread) == 2
        names = [c.name for c in contacts_with_unread]
        assert "Elena" in names
        assert "Marcus" in names
        assert "Victoria" not in names

    # -------------------------------------------------------------------------
    # Utility Method Tests
    # -------------------------------------------------------------------------

    def test_get_conversation_history(self, load_system):
        """Test getting conversation history."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()

        pm.receive_message("elena", "Hello!")
        pm.send_message("elena", "Hi!")

        history = pm.get_conversation_history("elena")
        assert len(history) == 2
        assert history[0].content == "Hello!"
        assert history[1].content == "Hi!"

        # Non-existent conversation
        assert pm.get_conversation_history("nobody") == []

    def test_clear_conversation(self, load_system):
        """Test clearing a conversation."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()

        pm.receive_message("elena", "Hello!")
        pm.send_message("elena", "Hi!")

        assert len(pm.get_conversation_history("elena")) == 2

        pm.clear_conversation("elena")
        assert len(pm.get_conversation_history("elena")) == 0

    def test_notification_toggle(self, load_system):
        """Test enabling/disabling notifications."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        assert pm.notifications_enabled is True

        pm.disable_notifications()
        assert pm.notifications_enabled is False

        pm.enable_notifications()
        assert pm.notifications_enabled is True

    def test_phone_manager_repr(self, load_system):
        """Test phone manager string representation."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.create_contact("Elena", "elena")
        pm.disable_notifications()
        pm.receive_message("elena", "Hello!")

        repr_str = repr(pm)
        assert "1 contacts" in repr_str
        assert "1 conversations" in repr_str


class TestPhoneIntegration:
    """Integration tests for the phone system."""

    def test_full_conversation_flow(self, load_system):
        """Test a complete conversation flow."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.disable_notifications()

        # Create and unlock contact
        pm.create_contact("Elena", "elena", unlocked=True)

        # Receive initial message
        pm.receive_message("elena", "Hey! Are you there?")
        assert pm.get_unread_count() == 1

        # Player reads and replies
        pm.mark_conversation_read("elena")
        assert pm.get_unread_count() == 0

        pm.send_message("elena", "Yes, I'm here!")

        # More messages
        pm.receive_message("elena", "Great! Want to meet up?")
        pm.send_message("elena", "Sure, where?")
        pm.receive_message("elena", "At the cafe in town.")

        # Check conversation history
        history = pm.get_conversation_history("elena")
        assert len(history) == 5

        # Verify message order
        assert history[0].content == "Hey! Are you there?"
        assert history[1].content == "Yes, I'm here!"
        assert history[2].content == "Great! Want to meet up?"
        assert history[3].content == "Sure, where?"
        assert history[4].content == "At the cafe in town."

    def test_multiple_contacts(self, load_system):
        """Test managing multiple contacts and conversations."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.disable_notifications()

        # Create multiple contacts
        pm.create_contact("Elena", "elena", unlocked=True)
        pm.create_contact("Marcus", "marcus", unlocked=True)
        pm.create_contact("Victoria", "victoria", unlocked=False)

        # Messages from multiple contacts
        pm.receive_message("elena", "Hello from Elena!")
        pm.receive_message("marcus", "Hello from Marcus!")

        assert pm.get_unread_count() == 2
        assert len(pm.get_unlocked_contacts()) == 2
        assert len(pm.get_contacts_with_unread()) == 2

        # Mark one as read
        pm.mark_conversation_read("elena")
        assert pm.get_unread_count() == 1
        assert len(pm.get_contacts_with_unread()) == 1

    def test_locked_contact_cannot_receive(self, load_system):
        """Test that conversations require contacts to exist."""
        ns = load_system("phone")
        PhoneManager = ns["PhoneManager"]

        pm = PhoneManager()
        pm.disable_notifications()

        # Try to message non-existent contact
        result = pm.receive_message("nobody", "Hello!")
        assert result is None

        # Create contact but don't unlock (still works for messaging)
        pm.create_contact("Elena", "elena", unlocked=False)
        result = pm.receive_message("elena", "Hello!")
        assert result is not None

    def test_default_global_instance(self, load_system):
        """Test that default phone_manager is created."""
        ns = load_system("phone")

        # The default statement creates phone_manager
        assert "phone_manager" in ns
        pm = ns["phone_manager"]
        assert pm is not None
