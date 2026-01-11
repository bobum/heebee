# Phone/Messaging System for Ren'Py Visual Novel
# This module provides a phone interface with contacts, conversations, and messaging.

init python:
    import time

    # =========================================================================
    # CONTACT CLASS - Represents a phone contact
    # =========================================================================

    class Contact:
        """
        Represents a contact in the player's phone.

        Attributes:
            name (str): Display name of the contact
            phone_id (str): Unique identifier for the contact
            avatar (str): Path to contact avatar image
            unlocked (bool): Whether the contact is unlocked/available
        """

        def __init__(self, name, phone_id, avatar=None, unlocked=False):
            self.name = name
            self.phone_id = phone_id
            self.avatar = avatar
            self.unlocked = unlocked

        def unlock(self):
            """Unlock this contact."""
            self.unlocked = True

        def lock(self):
            """Lock this contact."""
            self.unlocked = False

        def __repr__(self):
            status = "unlocked" if self.unlocked else "locked"
            return f"Contact({self.name}, {self.phone_id}, {status})"

    # =========================================================================
    # MESSAGE CLASS - Represents a single message
    # =========================================================================

    class Message:
        """
        Represents a single message in a conversation.

        Attributes:
            sender (str): The phone_id of the sender ("player" for player messages)
            content (str): The message text content
            timestamp (float): Unix timestamp when message was sent
            read (bool): Whether the message has been read
        """

        def __init__(self, sender, content, timestamp=None, read=False):
            self.sender = sender
            self.content = content
            self.timestamp = timestamp if timestamp is not None else time.time()
            self.read = read

        def mark_as_read(self):
            """Mark this message as read."""
            self.read = True

        def is_from_player(self):
            """Check if this message was sent by the player."""
            return self.sender == "player"

        def get_formatted_time(self):
            """Get a formatted time string for display."""
            try:
                t = time.localtime(self.timestamp)
                return time.strftime("%H:%M", t)
            except (ValueError, OSError):
                return "??:??"

        def __repr__(self):
            status = "read" if self.read else "unread"
            preview = self.content[:20] + "..." if len(self.content) > 20 else self.content
            return f"Message({self.sender}, '{preview}', {status})"

    # =========================================================================
    # CONVERSATION CLASS - Manages messages between player and contact
    # =========================================================================

    class Conversation:
        """
        Manages a conversation between the player and a contact.

        Attributes:
            contact_id (str): The phone_id of the contact this conversation is with
            messages (list): List of Message objects in chronological order
        """

        def __init__(self, contact_id):
            self.contact_id = contact_id
            self.messages = []

        def add_message(self, sender, content, timestamp=None, read=False):
            """
            Add a new message to the conversation.

            Args:
                sender (str): The phone_id of the sender
                content (str): The message text
                timestamp (float): Optional timestamp (defaults to current time)
                read (bool): Whether the message is already read

            Returns:
                Message: The newly created message
            """
            message = Message(sender, content, timestamp, read)
            self.messages.append(message)
            return message

        def send_message(self, content):
            """
            Send a message from the player.

            Args:
                content (str): The message text

            Returns:
                Message: The sent message
            """
            return self.add_message("player", content, read=True)

        def receive_message(self, content, timestamp=None):
            """
            Receive a message from the contact.

            Args:
                content (str): The message text
                timestamp (float): Optional timestamp

            Returns:
                Message: The received message
            """
            return self.add_message(self.contact_id, content, timestamp, read=False)

        def get_unread_count(self):
            """Get the number of unread messages in this conversation."""
            return sum(1 for msg in self.messages if not msg.read and not msg.is_from_player())

        def mark_all_as_read(self):
            """Mark all messages in this conversation as read."""
            for message in self.messages:
                message.mark_as_read()

        def get_last_message(self):
            """Get the most recent message, or None if no messages."""
            if self.messages:
                return self.messages[-1]
            return None

        def get_messages(self):
            """Get all messages in chronological order."""
            return self.messages.copy()

        def get_message_count(self):
            """Get the total number of messages."""
            return len(self.messages)

        def clear_messages(self):
            """Clear all messages from this conversation."""
            self.messages = []

        def __repr__(self):
            return f"Conversation({self.contact_id}, {len(self.messages)} messages)"

    # =========================================================================
    # PHONE MANAGER CLASS - Central manager for phone system
    # =========================================================================

    class PhoneManager:
        """
        Central manager for the phone/messaging system.

        Manages contacts, conversations, and notifications.

        Attributes:
            contacts (dict): Dictionary mapping phone_id to Contact objects
            conversations (dict): Dictionary mapping phone_id to Conversation objects
            notifications_enabled (bool): Whether notifications are enabled
        """

        def __init__(self):
            self.contacts = {}
            self.conversations = {}
            self.notifications_enabled = True

        # ---------------------------------------------------------------------
        # Contact Management
        # ---------------------------------------------------------------------

        def add_contact(self, contact):
            """
            Add a contact to the phone.

            Args:
                contact (Contact): The contact to add

            Returns:
                Contact: The added contact
            """
            self.contacts[contact.phone_id] = contact
            return contact

        def create_contact(self, name, phone_id, avatar=None, unlocked=False):
            """
            Create and add a new contact.

            Args:
                name (str): Display name
                phone_id (str): Unique identifier
                avatar (str): Path to avatar image
                unlocked (bool): Whether contact is unlocked

            Returns:
                Contact: The newly created contact
            """
            contact = Contact(name, phone_id, avatar, unlocked)
            return self.add_contact(contact)

        def get_contact(self, phone_id):
            """Get a contact by phone_id."""
            return self.contacts.get(phone_id, None)

        def remove_contact(self, phone_id):
            """
            Remove a contact from the phone.

            Args:
                phone_id (str): The contact's phone_id

            Returns:
                bool: True if contact was removed, False if not found
            """
            if phone_id in self.contacts:
                del self.contacts[phone_id]
                # Also remove conversation if exists
                if phone_id in self.conversations:
                    del self.conversations[phone_id]
                return True
            return False

        def unlock_contact(self, phone_id):
            """
            Unlock a contact.

            Args:
                phone_id (str): The contact's phone_id

            Returns:
                bool: True if contact was unlocked, False if not found
            """
            contact = self.get_contact(phone_id)
            if contact:
                contact.unlock()
                return True
            return False

        def lock_contact(self, phone_id):
            """
            Lock a contact.

            Args:
                phone_id (str): The contact's phone_id

            Returns:
                bool: True if contact was locked, False if not found
            """
            contact = self.get_contact(phone_id)
            if contact:
                contact.lock()
                return True
            return False

        def get_unlocked_contacts(self):
            """Get all unlocked contacts."""
            return [c for c in self.contacts.values() if c.unlocked]

        def get_all_contacts(self):
            """Get all contacts (locked and unlocked)."""
            return list(self.contacts.values())

        # ---------------------------------------------------------------------
        # Conversation Management
        # ---------------------------------------------------------------------

        def get_conversation(self, phone_id):
            """
            Get or create a conversation with a contact.

            Args:
                phone_id (str): The contact's phone_id

            Returns:
                Conversation: The conversation, or None if contact doesn't exist
            """
            if phone_id not in self.contacts:
                return None

            if phone_id not in self.conversations:
                self.conversations[phone_id] = Conversation(phone_id)

            return self.conversations[phone_id]

        def send_message(self, phone_id, content):
            """
            Send a message to a contact.

            Args:
                phone_id (str): The contact's phone_id
                content (str): The message text

            Returns:
                Message: The sent message, or None if contact doesn't exist
            """
            conversation = self.get_conversation(phone_id)
            if conversation:
                return conversation.send_message(content)
            return None

        def receive_message(self, phone_id, content, timestamp=None):
            """
            Receive a message from a contact.

            Args:
                phone_id (str): The contact's phone_id
                content (str): The message text
                timestamp (float): Optional timestamp

            Returns:
                Message: The received message, or None if contact doesn't exist
            """
            conversation = self.get_conversation(phone_id)
            if conversation:
                message = conversation.receive_message(content, timestamp)
                if self.notifications_enabled:
                    contact = self.get_contact(phone_id)
                    if contact:
                        renpy.notify(f"New message from {contact.name}")
                return message
            return None

        def mark_conversation_read(self, phone_id):
            """Mark all messages in a conversation as read."""
            conversation = self.get_conversation(phone_id)
            if conversation:
                conversation.mark_all_as_read()

        # ---------------------------------------------------------------------
        # Notification Methods
        # ---------------------------------------------------------------------

        def get_unread_count(self):
            """Get total unread message count across all conversations."""
            total = 0
            for conversation in self.conversations.values():
                total += conversation.get_unread_count()
            return total

        def get_conversation_unread_count(self, phone_id):
            """Get unread count for a specific conversation."""
            if phone_id in self.conversations:
                return self.conversations[phone_id].get_unread_count()
            return 0

        def has_unread_messages(self):
            """Check if there are any unread messages."""
            return self.get_unread_count() > 0

        def get_contacts_with_unread(self):
            """Get list of contacts with unread messages."""
            result = []
            for phone_id, conversation in self.conversations.items():
                if conversation.get_unread_count() > 0:
                    contact = self.get_contact(phone_id)
                    if contact:
                        result.append(contact)
            return result

        # ---------------------------------------------------------------------
        # Utility Methods
        # ---------------------------------------------------------------------

        def get_conversation_history(self, phone_id):
            """
            Get message history for a contact.

            Args:
                phone_id (str): The contact's phone_id

            Returns:
                list: List of Message objects, or empty list if no conversation
            """
            if phone_id in self.conversations:
                return self.conversations[phone_id].get_messages()
            return []

        def clear_conversation(self, phone_id):
            """Clear all messages in a conversation."""
            if phone_id in self.conversations:
                self.conversations[phone_id].clear_messages()

        def enable_notifications(self):
            """Enable message notifications."""
            self.notifications_enabled = True

        def disable_notifications(self):
            """Disable message notifications."""
            self.notifications_enabled = False

        def __repr__(self):
            return f"PhoneManager({len(self.contacts)} contacts, {len(self.conversations)} conversations)"

# =============================================================================
# GLOBAL PHONE MANAGER INSTANCE
# =============================================================================

default phone_manager = PhoneManager()

# =============================================================================
# PHONE STATE VARIABLES
# =============================================================================

default phone_current_contact = None
default phone_view = "contacts"  # "contacts" or "conversation"

# =============================================================================
# EXAMPLE CONTACT SETUP
# =============================================================================

init python:
    def setup_example_contacts():
        """Initialize example contacts for the phone system."""
        # Create example contacts
        phone_manager.create_contact(
            name="Elena Brightwood",
            phone_id="elena",
            avatar="images/characters/elena.png",
            unlocked=True
        )

        phone_manager.create_contact(
            name="Marcus Sterling",
            phone_id="marcus",
            avatar="images/characters/marcus.png",
            unlocked=True
        )

        phone_manager.create_contact(
            name="Lady Victoria",
            phone_id="victoria",
            avatar="images/characters/victoria.png",
            unlocked=False
        )

        phone_manager.create_contact(
            name="Sage Aldric",
            phone_id="aldric",
            avatar="images/characters/aldric.png",
            unlocked=False
        )

        # Add some example messages
        phone_manager.receive_message("elena", "Hey! Thanks for helping me earlier.")
        phone_manager.receive_message("elena", "Let me know if you need anything!")
        phone_manager.receive_message("marcus", "The shipment arrived safely. Good work.")

# =============================================================================
# PHONE UI SCREENS
# =============================================================================

screen phone_screen():
    """Main phone screen - shows contacts or conversation based on state."""

    tag menu
    modal True

    # Phone background frame
    frame:
        xalign 0.5
        yalign 0.5
        xsize 450
        ysize 700
        background "#1a1a2e"
        padding (0, 0)

        vbox:
            spacing 0

            # Phone header
            frame:
                xfill True
                ysize 60
                background "#2a2a4e"
                padding (15, 10)

                hbox:
                    yalign 0.5
                    spacing 10

                    # Back button (only in conversation view)
                    if phone_view == "conversation":
                        textbutton "<" action [SetVariable("phone_view", "contacts"), SetVariable("phone_current_contact", None)] style "phone_back_button"

                    # Title
                    if phone_view == "contacts":
                        text "Contacts" size 24 color "#ffffff" yalign 0.5
                    else:
                        if phone_current_contact:
                            $ contact = phone_manager.get_contact(phone_current_contact)
                            if contact:
                                text contact.name size 24 color "#ffffff" yalign 0.5

                    # Spacer
                    null width 10

                    # Unread indicator (only in contacts view)
                    if phone_view == "contacts":
                        $ unread = phone_manager.get_unread_count()
                        if unread > 0:
                            frame:
                                background "#ff4444"
                                padding (8, 4)
                                xalign 1.0
                                text "[unread]" size 14 color "#ffffff"

            # Content area
            if phone_view == "contacts":
                use phone_contacts_list()
            else:
                use phone_conversation_view()

            # Close button at bottom
            frame:
                xfill True
                ysize 50
                background "#2a2a4e"

                textbutton "Close Phone" action [Hide("phone_screen"), SetVariable("phone_view", "contacts"), SetVariable("phone_current_contact", None)] xalign 0.5 yalign 0.5 style "phone_close_button"


screen phone_contacts_list():
    """Contact list view for the phone."""

    viewport:
        xfill True
        ysize 590
        scrollbars "vertical"
        mousewheel True
        draggable True

        vbox:
            spacing 2

            $ unlocked_contacts = phone_manager.get_unlocked_contacts()

            if not unlocked_contacts:
                frame:
                    xfill True
                    ysize 100
                    background "#222244"

                    text "No contacts yet" color "#888888" xalign 0.5 yalign 0.5

            else:
                for contact in unlocked_contacts:
                    $ unread = phone_manager.get_conversation_unread_count(contact.phone_id)
                    $ last_msg = None
                    if contact.phone_id in phone_manager.conversations:
                        $ last_msg = phone_manager.conversations[contact.phone_id].get_last_message()

                    button:
                        xfill True
                        ysize 80
                        background "#222244"
                        hover_background "#333366"
                        action [SetVariable("phone_current_contact", contact.phone_id), SetVariable("phone_view", "conversation"), Function(phone_manager.mark_conversation_read, contact.phone_id)]

                        hbox:
                            spacing 15
                            yalign 0.5
                            xfill True

                            # Avatar placeholder
                            frame:
                                xsize 50
                                ysize 50
                                xoffset 10
                                background "#444466"
                                if contact.avatar:
                                    add contact.avatar fit "contain"
                                else:
                                    text contact.name[0] xalign 0.5 yalign 0.5 size 24 color "#ffffff"

                            vbox:
                                yalign 0.5
                                spacing 4

                                hbox:
                                    spacing 10
                                    text contact.name size 18 color "#ffffff"

                                    # Unread badge
                                    if unread > 0:
                                        frame:
                                            background "#ff4444"
                                            padding (6, 2)
                                            text "[unread]" size 12 color "#ffffff"

                                # Last message preview
                                if last_msg:
                                    $ preview = last_msg.content[:30] + "..." if len(last_msg.content) > 30 else last_msg.content
                                    text preview size 14 color "#888888"
                                else:
                                    text "No messages" size 14 color "#666666"


screen phone_conversation_view():
    """Conversation view showing messages with a contact."""

    vbox:
        spacing 0

        # Messages area
        viewport:
            xfill True
            ysize 500
            scrollbars "vertical"
            mousewheel True
            draggable True
            yinitial 1.0  # Start scrolled to bottom

            vbox:
                spacing 8
                xfill True

                $ messages = phone_manager.get_conversation_history(phone_current_contact)

                if not messages:
                    frame:
                        xfill True
                        ysize 100
                        background None

                        text "No messages yet" color "#888888" xalign 0.5 yalign 0.5

                else:
                    null height 10
                    for msg in messages:
                        use phone_message_bubble(msg)
                    null height 10

        # Reply options (placeholder - could be expanded for actual message input)
        frame:
            xfill True
            ysize 90
            background "#2a2a4e"
            padding (10, 10)

            vbox:
                spacing 5
                text "Quick Replies:" size 14 color "#888888"
                hbox:
                    spacing 10
                    textbutton "Hi!" action Function(send_quick_reply, "Hi!") style "phone_reply_button"
                    textbutton "Thanks!" action Function(send_quick_reply, "Thanks!") style "phone_reply_button"
                    textbutton "See you!" action Function(send_quick_reply, "See you later!") style "phone_reply_button"


screen phone_message_bubble(msg):
    """Individual message bubble."""

    $ is_player = msg.is_from_player()

    hbox:
        xfill True

        if is_player:
            null  # Spacer to push to right

        frame:
            xmaximum 300
            if is_player:
                xalign 1.0
                xoffset -15
                background "#4466aa"
            else:
                xalign 0.0
                xoffset 15
                background "#333355"

            padding (12, 8)

            vbox:
                spacing 4
                text msg.content size 16 color "#ffffff"
                text msg.get_formatted_time() size 11 color "#aaaaaa" xalign 1.0

        if not is_player:
            null  # Spacer to keep left-aligned


# =============================================================================
# PHONE HELPER FUNCTIONS
# =============================================================================

init python:
    def send_quick_reply(content):
        """Send a quick reply message."""
        if phone_current_contact:
            phone_manager.send_message(phone_current_contact, content)

    def open_phone():
        """Open the phone screen."""
        renpy.show_screen("phone_screen")

    def close_phone():
        """Close the phone screen."""
        renpy.hide_screen("phone_screen")

# =============================================================================
# PHONE STYLES
# =============================================================================

style phone_back_button:
    background "#444466"
    hover_background "#5555aa"
    padding (10, 5)
    xsize 40

style phone_back_button_text:
    color "#ffffff"
    size 20

style phone_close_button:
    background "#444466"
    hover_background "#5555aa"
    padding (20, 8)

style phone_close_button_text:
    color "#ffffff"
    size 16

style phone_reply_button:
    background "#333355"
    hover_background "#4466aa"
    padding (15, 8)

style phone_reply_button_text:
    color "#ffffff"
    size 14

# =============================================================================
# PHONE LABELS FOR GAME INTEGRATION
# =============================================================================

# Open phone screen
label open_phone:
    call screen phone_screen
    return

# Unlock a contact
label unlock_phone_contact(phone_id):
    $ phone_manager.unlock_contact(phone_id)
    $ contact = phone_manager.get_contact(phone_id)
    if contact:
        $ renpy.notify(f"New contact: {contact.name}")
    return

# Receive a message (with delay for dramatic effect)
label receive_phone_message(phone_id, content, delay=0.5):
    if delay > 0:
        pause delay
    $ phone_manager.receive_message(phone_id, content)
    return

# =============================================================================
# EXAMPLE USAGE IN GAME SCRIPT
# =============================================================================

# Example label showing phone system usage:
#
# label phone_example:
#     "Your phone buzzes..."
#     call receive_phone_message("elena", "Hey! Are you free later?")
#
#     menu:
#         "Check phone":
#             call open_phone
#         "Ignore it":
#             pass
#
#     return
#
# To unlock a new contact:
#     call unlock_phone_contact("victoria")
#
# To check unread messages:
#     $ unread = phone_manager.get_unread_count()
#     if unread > 0:
#         "You have [unread] unread messages."
