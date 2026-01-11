# Systems Demo - Showcases all 24+ game systems in Heebee
# Text-only demos showing what each system can do

label systems_demo:
    scene bg room with fade

    "Welcome to the Heebee Systems Demo!"
    "This showcases ALL 24+ game systems that have been implemented."

    call systems_menu

    return

label systems_menu:
    scene bg room
    "Select a category to explore:"

    menu:
        "Core Systems":
            call core_systems_menu

        "World Systems":
            call world_systems_menu

        "Progression Systems":
            call progression_systems_menu

        "Content Systems":
            call content_systems_menu

        "Gameplay Systems":
            call gameplay_systems_menu

        "Meta Systems":
            call meta_systems_menu

        "Exit Demo":
            "Thanks for exploring all the systems!"
            return

    jump systems_menu

label core_systems_menu:
    scene bg room
    menu:
        "Stats System":
            call demo_stats
        "Inventory System":
            call demo_inventory
        "Combat System":
            call demo_combat
        "Skills System":
            call demo_skills
        "Relationships System":
            call demo_relationships
        "Back":
            return
    jump core_systems_menu

label world_systems_menu:
    scene bg room
    menu:
        "Exploration System":
            call demo_exploration
        "Time System":
            call demo_time
        "Economy System":
            call demo_economy
        "World Map System":
            call demo_world_map
        "Weather System":
            call demo_weather
        "Back":
            return
    jump world_systems_menu

label progression_systems_menu:
    scene bg room
    menu:
        "Quest System":
            call demo_quests
        "Achievement System":
            call demo_achievements
        "Morality System":
            call demo_morality
        "Route System":
            call demo_routes
        "Endings System":
            call demo_endings
        "Back":
            return
    jump progression_systems_menu

label content_systems_menu:
    scene bg room
    menu:
        "Phone System":
            call demo_phone
        "Gallery System":
            call demo_gallery
        "Journal System":
            call demo_journal
        "Flashback System":
            call demo_flashback
        "Back":
            return
    jump content_systems_menu

label gameplay_systems_menu:
    scene bg room
    menu:
        "Minigames System":
            call demo_minigames
        "Crafting System":
            call demo_crafting
        "Breeding System":
            call breeding_demo
        "Back":
            return
    jump gameplay_systems_menu

label meta_systems_menu:
    scene bg room
    menu:
        "Dynamic Music System":
            call demo_music
        "Accessibility System":
            call demo_accessibility
        "Mod Framework":
            call demo_mods
        "Back":
            return
    jump meta_systems_menu

# =============================================================================
# STATS DEMO
# =============================================================================
label demo_stats:
    scene bg room
    "=== STATS SYSTEM ==="

    python:
        demo_player = Player("Hero")

    $ hp = demo_player.hp
    $ str = demo_player.strength
    $ int = demo_player.intelligence
    $ lvl = demo_player.level

    "Your character:"
    "Level [lvl] | HP: [hp] | STR: [str] | INT: [int]"

    "Training strength (+5)..."
    $ demo_player.add_stat("strength", 5)
    $ str = demo_player.strength
    "Strength is now [str]"

    "Taking damage (-20 HP)..."
    $ demo_player.subtract_stat("hp", 20)
    $ hp = demo_player.hp
    "HP is now [hp]"

    "Gaining 150 XP..."
    $ demo_player.add_xp(150)
    $ lvl = demo_player.level
    $ xp = demo_player.xp
    "Level: [lvl] | XP: [xp]"

    return

# =============================================================================
# INVENTORY DEMO
# =============================================================================
label demo_inventory:
    scene bg room
    "=== INVENTORY SYSTEM ==="

    python:
        demo_inv = Inventory(max_slots=20)
        potion = Item("potion", "Health Potion", "Restores HP", category=ItemCategory.CONSUMABLE, stackable=True)
        sword = Item("sword", "Iron Sword", "A sturdy blade", category=ItemCategory.WEAPON, value=100)
        demo_inv.add_item(potion, quantity=3)
        demo_inv.add_item(sword, quantity=1)

    $ items = len([s for s in demo_inv.slots if s.item])
    $ gold = demo_inv.gold
    "Inventory: [items] item types | Gold: [gold]"

    "Adding 5 more potions..."
    python:
        demo_inv.add_item(Item("potion", "Health Potion", "", category=ItemCategory.CONSUMABLE, stackable=True), quantity=5)

    "Earning 50 gold..."
    $ demo_inv.gold += 50
    $ gold = demo_inv.gold
    "Gold is now [gold]"

    return

# =============================================================================
# COMBAT DEMO
# =============================================================================
label demo_combat:
    scene bg room
    "=== COMBAT SYSTEM ==="

    python:
        hero = Combatant("Hero", hp=100, mp=50, attack=15, defense=10, speed=12)
        goblin = Enemy("Goblin", hp=40, mp=0, attack=8, defense=5, speed=8, xp_reward=25)

    $ h_hp = hero.hp
    $ g_hp = goblin.hp
    "A Goblin appears!"
    "Hero HP: [h_hp] | Goblin HP: [g_hp]"

    "Hero attacks!"
    python:
        dmg = max(1, hero.attack - goblin.defense)
        goblin.hp -= dmg

    $ g_hp = goblin.hp
    "Dealt [dmg] damage! Goblin HP: [g_hp]"

    "Goblin strikes back!"
    python:
        dmg = max(1, goblin.attack - hero.defense)
        hero.hp -= dmg

    $ h_hp = hero.hp
    "Took [dmg] damage! Hero HP: [h_hp]"

    $ reward = goblin.xp_reward
    "Defeat the goblin to earn [reward] XP!"

    return

# =============================================================================
# SKILLS DEMO
# =============================================================================
label demo_skills:
    scene bg room
    "=== SKILL TREE SYSTEM ==="

    python:
        demo_tree = SkillTree()
        demo_tree.add_skill(Skill("fireball", "Fireball", "Launch a ball of fire", cost=1, branch="magic"))
        demo_tree.add_skill(Skill("heal", "Heal", "Restore health", cost=2, branch="magic"))
        demo_tree.add_skill(Skill("sword_mastery", "Sword Mastery", "Better with swords", cost=1, branch="combat"))
        demo_tree.skill_points = 5

    $ pts = demo_tree.skill_points
    "You have [pts] skill points."

    $ skills = len(demo_tree.skills)
    "Available skills: [skills]"
    "- Fireball (1 pt, Magic)"
    "- Heal (2 pts, Magic)"
    "- Sword Mastery (1 pt, Combat)"

    "Learning Fireball..."
    python:
        demo_tree.unlock_skill("fireball")

    $ pts = demo_tree.skill_points
    $ learned = len(demo_tree.get_unlocked_skills())
    "Spent 1 point! Points remaining: [pts]"
    "Skills learned: [learned]"

    return

# =============================================================================
# RELATIONSHIPS DEMO
# =============================================================================
label demo_relationships:
    scene bg room
    "=== RELATIONSHIPS SYSTEM ==="

    python:
        demo_rel = RelationshipManager()
        demo_rel.add_character("elena", "Elena", initial_affection=50)
        demo_rel.add_character("marcus", "Marcus", initial_affection=30)

    $ elena = demo_rel.get_relationship("elena")
    $ marcus = demo_rel.get_relationship("marcus")
    $ e_aff = elena.affection
    $ m_aff = marcus.affection

    "Elena's affection: [e_aff]"
    "Marcus's affection: [m_aff]"

    "You give Elena a gift..."
    $ elena.affection += 15
    $ e_aff = elena.affection
    $ e_status = elena.get_status()
    "Elena's affection is now [e_aff] ([e_status])"

    "You help Marcus with a problem..."
    $ marcus.affection += 20
    $ marcus.trust += 10
    $ m_aff = marcus.affection
    $ m_trust = marcus.trust
    "Marcus: Affection [m_aff], Trust [m_trust]"

    return

# =============================================================================
# EXPLORATION DEMO
# =============================================================================
label demo_exploration:
    scene bg room
    "=== EXPLORATION SYSTEM ==="

    python:
        demo_explore = ExplorationManager()
        library = Location("library", "Old Library", "bg room", description="A dusty library")
        library.add_hotspot(Hotspot("bookshelf", "Ancient Bookshelf", 100, 200, 150, 300))
        library.add_hotspot(Hotspot("desk", "Dusty Desk", 400, 300, 200, 100))
        library.add_hotspot(Hotspot("window", "Cracked Window", 600, 100, 80, 200))
        demo_explore.add_location(library)

    $ loc = library.name
    $ desc = library.description
    "[loc]"
    "[desc]"

    $ spots = len(library.hotspots)
    "Interactive hotspots: [spots]"
    "- Ancient Bookshelf (click to examine)"
    "- Dusty Desk (click to search)"
    "- Cracked Window (click to look outside)"

    "Click hotspots to trigger events and find items!"

    return

# =============================================================================
# TIME DEMO
# =============================================================================
label demo_time:
    scene bg room
    "=== TIME SYSTEM ==="

    python:
        demo_time = TimeManager(start_day=1, start_time_period=0, start_week_day=0)

    $ day = demo_time.current_day
    $ period = demo_time.time_period_name
    $ weekday = demo_time.day_of_week
    $ energy = demo_time.energy
    "Day [day] ([weekday]) - [period]"
    "Energy: [energy]/100"

    "Advancing time by 2 periods..."
    $ demo_time.advance_time(2)
    $ period = demo_time.time_period_name
    $ energy = demo_time.energy
    "Time: [period] | Energy: [energy]"

    "Sleeping until tomorrow..."
    $ demo_time.advance_day(1)
    $ day = demo_time.current_day
    $ weekday = demo_time.day_of_week
    $ energy = demo_time.energy
    "Now Day [day] ([weekday]) | Energy restored: [energy]"

    return

# =============================================================================
# ECONOMY DEMO
# =============================================================================
label demo_economy:
    scene bg room
    "=== ECONOMY SYSTEM ==="

    python:
        demo_wallet = Wallet()
        demo_wallet.add("gold", 100)

    $ gold = demo_wallet.get_balance("gold")
    "Your wallet: [gold] gold"

    "Earning 50 gold from a quest..."
    $ demo_wallet.add("gold", 50)
    $ gold = demo_wallet.get_balance("gold")
    "Gold: [gold]"

    "Buying a Health Potion (25 gold)..."
    $ demo_wallet.subtract("gold", 25)
    $ gold = demo_wallet.get_balance("gold")
    "Gold remaining: [gold]"

    "Selling loot for 30 gold..."
    $ demo_wallet.add("gold", 30)
    $ gold = demo_wallet.get_balance("gold")
    "Final balance: [gold] gold"

    return

# =============================================================================
# WORLD MAP DEMO
# =============================================================================
label demo_world_map:
    scene bg room
    "=== WORLD MAP SYSTEM ==="

    python:
        demo_map = WorldMapManager()
        demo_map.register_location(MapLocation("home", "Your Home", "A cozy house", position=(100, 100), unlocked=True))
        demo_map.register_location(MapLocation("town", "Town Square", "Bustling market", position=(300, 150), unlocked=True))
        demo_map.register_location(MapLocation("forest", "Dark Forest", "Mysterious woods", position=(500, 200), unlocked=False))
        demo_map.register_location(MapLocation("castle", "Ancient Castle", "Ruined fortress", position=(700, 100), unlocked=False))

    $ unlocked = len(demo_map.get_unlocked_locations())
    $ total = len(demo_map.get_all_locations())
    "Discovered: [unlocked]/[total] locations"

    "- Your Home (unlocked)"
    "- Town Square (unlocked)"
    "- Dark Forest (locked)"
    "- Ancient Castle (locked)"

    "Discovering the Dark Forest..."
    $ demo_map.unlock_location("forest")
    $ unlocked = len(demo_map.get_unlocked_locations())
    "Locations unlocked: [unlocked]/[total]"

    "Travel between locations costs time and gold!"

    return

# =============================================================================
# WEATHER DEMO
# =============================================================================
label demo_weather:
    scene bg room
    "=== WEATHER SYSTEM ==="

    python:
        demo_weather = WeatherManager()

    $ weather = demo_weather.current_weather
    $ season = demo_weather.current_season
    $ weather_label = demo_weather.get_weather_label()
    "Current: [weather_label] | Season: [season]"

    "Weather types: Clear, Cloudy, Rain, Storm, Snow, Fog"

    "A storm rolls in..."
    $ demo_weather.set_weather(WeatherType.STORM)
    $ weather_label = demo_weather.get_weather_label()
    $ visibility = demo_weather.get_modifier("visibility")
    $ mood = demo_weather.get_modifier("mood")
    "Weather changed to: [weather_label]"
    "Modifiers: Visibility [visibility], Mood [mood]"

    "The storm passes, now it's just rain..."
    $ demo_weather.set_weather(WeatherType.RAIN)
    $ weather_label = demo_weather.get_weather_label()
    $ visibility = demo_weather.get_modifier("visibility")
    "Weather: [weather_label] | Visibility: [visibility]"

    "Changing to sunny..."
    $ demo_weather.set_weather(WeatherType.SUNNY)
    $ weather_label = demo_weather.get_weather_label()
    $ mood = demo_weather.get_modifier("mood")
    "Weather: [weather_label] | Mood bonus: +[mood]"

    "Weather affects visibility, NPC schedules, and events!"

    return

# =============================================================================
# QUESTS DEMO
# =============================================================================
label demo_quests:
    scene bg room
    "=== QUEST SYSTEM ==="

    python:
        demo_quest_mgr = QuestManager()
        # Create a quest with objectives
        quest = Quest(
            id="demo_quest",
            name="The Lost Artifact",
            description="Find the ancient artifact hidden in the ruins.",
            category=QUEST_CATEGORY_MAIN,
            rewards=QuestRewards(gold=100, xp=50, items=["rare_gem"])
        )
        quest.add_objective("Enter the ancient ruins")
        quest.add_objective("Solve the stone puzzle")
        quest.add_objective("Retrieve the artifact")
        quest.add_objective("Find the secret treasure", optional=True)
        demo_quest_mgr.add_quest(quest)

    $ q_name = quest.name
    $ q_desc = quest.description
    "Quest: [q_name]"
    "[q_desc]"

    $ obj_count = len(quest.objectives)
    "Objectives: [obj_count] total"

    "Starting the quest..."
    $ demo_quest_mgr.start_quest("demo_quest")
    $ status = quest.status
    "Status: [status]"

    "Completing first objective..."
    $ demo_quest_mgr.complete_objective("demo_quest", 0)
    $ completed, total, pct = quest.get_progress()
    $ pct_int = int(pct)
    "Progress: [completed]/[total] ([pct_int] percent)"

    "Completing second objective..."
    $ demo_quest_mgr.complete_objective("demo_quest", 1)
    $ completed, total, pct = quest.get_progress()
    $ pct_int = int(pct)
    "Progress: [completed]/[total] ([pct_int] percent)"

    $ reward_gold = quest.rewards.gold
    $ reward_xp = quest.rewards.xp
    "Rewards on completion: [reward_gold] gold, [reward_xp] XP"

    return

# =============================================================================
# ACHIEVEMENTS DEMO
# =============================================================================
label demo_achievements:
    scene bg room
    "=== ACHIEVEMENT SYSTEM ==="

    python:
        demo_ach_mgr = AchievementManager()
        # Register achievements
        demo_ach_mgr.register_achievement("first_steps", "First Steps", "Begin your adventure", points=10, category="story")
        demo_ach_mgr.register_achievement("explorer", "Explorer", "Visit 5 locations", points=25, hidden=False, category="exploration")
        demo_ach_mgr.register_progress_achievement("collector", "Collector", "Collect 10 items", target=10, points=50, category="completion")
        demo_ach_mgr.register_achievement("secret_find", "Secret Hunter", "Find the hidden room", points=100, hidden=True, category="secret")

    $ total = demo_ach_mgr.get_total_count()
    $ unlocked = demo_ach_mgr.get_unlock_count()
    "Achievements registered: [total]"
    "Unlocked: [unlocked]"

    "Unlocking 'First Steps'..."
    $ demo_ach_mgr.unlock("first_steps", notify=False)
    $ unlocked = demo_ach_mgr.get_unlock_count()
    $ points = demo_ach_mgr.get_total_points()
    "Unlocked: [unlocked] | Points earned: [points]"

    "Adding progress to 'Collector' (5 items)..."
    $ demo_ach_mgr.add_progress("collector", 5, notify=False)
    $ coll = demo_ach_mgr.get("collector")
    $ progress = coll.get_progress_text()
    "Collector progress: [progress]"

    "Adding more progress (5 more items)..."
    $ demo_ach_mgr.add_progress("collector", 5, notify=False)
    $ progress = coll.get_progress_text()
    $ is_unlocked = coll.unlocked
    "Collector progress: [progress] | Unlocked: [is_unlocked]"

    $ unlocked = demo_ach_mgr.get_unlock_count()
    $ points = demo_ach_mgr.get_total_points()
    $ completion = demo_ach_mgr.get_completion_percent()
    "Total unlocked: [unlocked] | Points: [points] | Completion: [completion] percent"

    return

# =============================================================================
# MORALITY DEMO
# =============================================================================
label demo_morality:
    scene bg room
    "=== MORALITY SYSTEM ==="

    python:
        demo_morality = MoralityManager(initial_karma=0)

    $ karma = demo_morality.karma
    $ align_id, align_label, align_color = demo_morality.get_alignment()
    "Starting karma: [karma] | Alignment: [align_label]"

    "You help a stranger in need (+15 karma)..."
    $ demo_morality.modify_karma(15, "Helped a stranger")
    $ karma = demo_morality.karma
    $ align_label = demo_morality.get_alignment_label()
    "Karma: [karma] | Alignment: [align_label]"

    "You donate to charity (+10 karma)..."
    $ demo_morality.modify_karma(10, "Donated to charity")
    $ karma = demo_morality.karma
    $ align_label = demo_morality.get_alignment_label()
    "Karma: [karma] | Alignment: [align_label]"

    "You tell a harmful lie (-20 karma)..."
    $ demo_morality.modify_karma(-20, "Told a harmful lie")
    $ karma = demo_morality.karma
    $ align_label = demo_morality.get_alignment_label()
    "Karma: [karma] | Alignment: [align_label]"

    $ good_total = demo_morality.get_total_positive_karma()
    $ bad_total = demo_morality.get_total_negative_karma()
    "Total good deeds: +[good_total] | Total bad deeds: -[bad_total]"

    $ history_count = len(demo_morality.karma_history)
    "Karma changes recorded: [history_count]"

    "Karma affects dialogue options, NPC reactions, and story paths!"

    return

# =============================================================================
# ROUTES DEMO
# =============================================================================
label demo_routes:
    scene bg room
    "=== ROUTE SYSTEM ==="

    python:
        demo_route_mgr = RouteManager()
        # Create character routes
        elena_route = Route("elena", "Elena Brightwood", "Adventure and discovery await", requirements={"affection": 60, "trust": 40, "respect": 30}, incompatible_routes=["victoria"])
        marcus_route = Route("marcus", "Marcus Sterling", "Uncover merchant secrets", requirements={"affection": 50, "trust": 50, "respect": 40})
        victoria_route = Route("victoria", "Lady Victoria", "Noble intrigue and forbidden love", requirements={"affection": 70, "trust": 30, "respect": 60}, incompatible_routes=["elena"])
        demo_route_mgr.register_route(elena_route)
        demo_route_mgr.register_route(marcus_route)
        demo_route_mgr.register_route(victoria_route)

    $ route_count = len(demo_route_mgr.routes)
    "Available routes: [route_count]"

    "- Elena Brightwood (requires: Affection 60, Trust 40)"
    "- Marcus Sterling (requires: Affection 50, Trust 50)"
    "- Lady Victoria (requires: Affection 70, Respect 60)"

    "Locking into Elena's route..."
    $ demo_route_mgr.lock_into_route("elena", "chapter_3")
    $ current = demo_route_mgr.get_current_route()
    $ char_name = current.character_name
    $ is_locked = demo_route_mgr.is_locked_in()
    "Locked into: [char_name] | Route active: [is_locked]"

    $ blocked = demo_route_mgr.get_blocked_routes()
    $ blocked_count = len(blocked)
    "Routes now blocked: [blocked_count]"
    "Victoria's route is now inaccessible!"

    $ marcus_available = "marcus" not in blocked
    "Marcus route still available: [marcus_available]"

    "Routes unlock unique story content and endings!"

    return

# =============================================================================
# ENDINGS DEMO
# =============================================================================
label demo_endings:
    scene bg room
    "=== ENDINGS SYSTEM ==="

    python:
        demo_endings = EndingsManager()
        demo_endings.create_ending("true_ending", "The True Path", "You discovered the ultimate truth.", hidden=False, category="main", priority=1)
        demo_endings.create_ending("good_ending", "A Bright Future", "Happiness with those you love.", hidden=False, category="main", priority=2)
        demo_endings.create_ending("bad_ending", "Bitter Conclusion", "Your choices had consequences.", hidden=False, category="main", priority=3)
        demo_endings.create_ending("secret_ending", "The Hidden Truth", "A secret revealed...", hidden=True, category="secret", priority=50)
        demo_endings.create_ending("elena_romance", "Elena's Heart", "Love blossoms.", hidden=False, category="romance", priority=10)

    $ total = len(demo_endings.endings)
    $ unlocked_list = demo_endings.get_unlocked_endings()
    $ unlocked = len(unlocked_list)
    "Total endings: [total] | Unlocked: [unlocked]"

    "Unlocking 'Good Ending'..."
    $ demo_endings.unlock_ending("good_ending")
    $ completion = demo_endings.get_completion_percentage()
    $ comp_int = int(completion)
    "Completion: [comp_int] percent"

    "Unlocking 'Elena Romance'..."
    $ demo_endings.unlock_ending("elena_romance")
    $ unlocked_list = demo_endings.get_unlocked_endings()
    $ unlocked = len(unlocked_list)
    $ completion = demo_endings.get_completion_percentage()
    $ comp_int = int(completion)
    "Unlocked: [unlocked] | Completion: [comp_int] percent"

    $ visible = demo_endings.get_visible_endings()
    $ hidden = demo_endings.get_hidden_endings()
    $ hidden_count = len(hidden)
    "Visible endings: [len(visible)] | Hidden endings: [hidden_count]"

    $ categories = demo_endings.get_categories()
    $ cat_count = len(categories)
    "Ending categories: [cat_count] (main, romance, secret)"

    "Collect all endings for 100 percent completion!"

    return

# =============================================================================
# PHONE DEMO
# =============================================================================
label demo_phone:
    scene bg room
    "=== PHONE SYSTEM ==="

    python:
        demo_phone = PhoneManager()
        elena_contact = Contact("Elena", "elena", unlocked=True)
        marcus_contact = Contact("Marcus", "marcus", unlocked=True)
        demo_phone.add_contact(elena_contact)
        demo_phone.add_contact(marcus_contact)

    $ contacts = len(demo_phone.contacts)
    "Contacts in phone: [contacts]"

    "Starting conversation with Elena..."
    python:
        convo = demo_phone.get_conversation("elena")
        convo.receive_message("Hey! How's it going?")
        convo.send_message("Good! Just exploring the library.")
        convo.receive_message("Find anything interesting?")

    $ msg_count = convo.get_message_count()
    "Messages in conversation: [msg_count]"

    $ last_msg = convo.get_last_message()
    $ last_content = last_msg.content
    "Last message: '[last_content]'"

    $ unread = convo.get_unread_count()
    "Unread messages: [unread]"

    "Marking all as read..."
    $ convo.mark_all_as_read()
    $ unread = convo.get_unread_count()
    "Unread after reading: [unread]"

    "Receiving new message from Marcus..."
    python:
        marcus_convo = demo_phone.get_conversation("marcus")
        marcus_convo.receive_message("I have a business proposition for you...")

    $ total_unread = demo_phone.get_unread_count()
    "Total unread across all contacts: [total_unread]"

    "Phone notifications alert you to new messages!"

    return

# =============================================================================
# GALLERY DEMO
# =============================================================================
label demo_gallery:
    scene bg room
    "=== GALLERY SYSTEM ==="

    python:
        demo_gallery = GalleryManager()
        # Register CG images
        demo_gallery.register_gallery_item(GalleryItem("cg_elena_smile", "Elena's Smile", "images/cg/elena_smile.png", category="character"))
        demo_gallery.register_gallery_item(GalleryItem("cg_sunset", "Beautiful Sunset", "images/cg/sunset.png", category="scene"))
        demo_gallery.register_gallery_item(GalleryItem("cg_library", "Ancient Library", "images/cg/library.png", category="background"))
        demo_gallery.register_gallery_item(GalleryItem("cg_ending1", "Good Ending", "images/cg/ending1.png", category="ending"))
        # Register music
        demo_gallery.register_music_track(MusicTrack("ost_main", "Main Theme", "audio/main_theme.mp3"))
        demo_gallery.register_music_track(MusicTrack("ost_romance", "Romance Theme", "audio/romance.mp3"))
        # Register scenes
        demo_gallery.register_scene_replay(SceneReplay("scene_meeting", "First Meeting", "meeting_scene"))

    $ cg_count = len(demo_gallery.gallery_items)
    $ music_count = len(demo_gallery.music_tracks)
    $ scene_count = len(demo_gallery.scene_replays)
    "Gallery items: [cg_count] CGs, [music_count] tracks, [scene_count] scenes"

    "Unlocking CG: Elena's Smile..."
    $ demo_gallery.unlock_gallery_item("cg_elena_smile")
    $ unlocked_cgs = demo_gallery.get_unlocked_gallery_items()
    "Unlocked CGs: [len(unlocked_cgs)]"

    "Unlocking CG: Beautiful Sunset..."
    $ demo_gallery.unlock_gallery_item("cg_sunset")

    "Unlocking music: Main Theme..."
    $ demo_gallery.unlock_music_track("ost_main")
    $ unlocked_music = demo_gallery.get_unlocked_music_tracks()
    "Unlocked tracks: [len(unlocked_music)]"

    $ cg_pct = demo_gallery.get_gallery_completion()
    $ cg_pct_int = int(cg_pct)
    "CG Gallery completion: [cg_pct_int] percent"

    $ character_cgs = demo_gallery.get_gallery_items_by_category("character")
    "Character CGs: [len(character_cgs)]"

    "Gallery unlocks as you play through the story!"

    return

# =============================================================================
# JOURNAL DEMO
# =============================================================================
label demo_journal:
    scene bg room
    "=== JOURNAL SYSTEM ==="

    python:
        demo_journal = JournalManager()
        # Register entries across categories
        demo_journal.register_entry("lore_ancient", "Ancient Legends", "The old stories tell of spirits that once walked among us...", JournalCategory.LORE)
        demo_journal.register_entry("char_elena", "Elena Brightwood", "A curious researcher with a passion for folklore.", JournalCategory.CHARACTERS)
        demo_journal.register_entry("loc_library", "The Old Library", "A repository of ancient knowledge hidden in the town.", JournalCategory.LOCATIONS)
        demo_journal.register_entry("item_artifact", "Mysterious Artifact", "A strange relic found in the ruins.", JournalCategory.ITEMS)
        demo_journal.register_entry("clue_symbol", "Strange Symbol", "A recurring mark found throughout the ruins.", JournalCategory.CLUES)

    $ total = demo_journal.get_total_count()
    $ unlocked = demo_journal.get_unlocked_count()
    "Journal entries: [total] | Unlocked: [unlocked]"

    "Unlocking 'Ancient Legends' entry..."
    $ demo_journal.unlock_entry("lore_ancient")
    $ entry = demo_journal.get_entry("lore_ancient")
    $ title = entry.title
    "Entry unlocked: [title]"

    "Unlocking 'Elena Brightwood' entry..."
    $ demo_journal.unlock_entry("char_elena")
    $ unlocked = demo_journal.get_unlocked_count()
    "Unlocked entries: [unlocked]"

    "Unlocking location entry..."
    $ demo_journal.unlock_entry("loc_library")

    $ lore_entries = demo_journal.get_entries_by_category(JournalCategory.LORE)
    $ char_entries = demo_journal.get_entries_by_category(JournalCategory.CHARACTERS)
    "Lore entries: [len(lore_entries)] | Character entries: [len(char_entries)]"

    $ unread = demo_journal.get_unread_count()
    "Unread entries: [unread]"

    "Marking 'Ancient Legends' as read..."
    $ demo_journal.mark_read("lore_ancient")
    $ unread = demo_journal.get_unread_count()
    "Unread after reading: [unread]"

    "Journal stores lore, characters, locations, items, and clues!"

    return

# =============================================================================
# FLASHBACK DEMO
# =============================================================================
label demo_flashback:
    scene bg room
    "=== FLASHBACK SYSTEM ==="

    python:
        demo_flashback = FlashbackManager()
        # Register memories
        demo_flashback.register("mem_meeting", "First Meeting", "The day you met Elena in the library.", "flashback_meeting", category="story")
        demo_flashback.register("mem_discovery", "The Discovery", "Finding the ancient artifact.", "flashback_discovery", category="discovery")
        demo_flashback.register("mem_elena_laugh", "Elena's Laugh", "A cherished moment with Elena.", "flashback_elena", category="character")
        demo_flashback.register("mem_secret", "Hidden Chamber", "Discovering the secret room.", "flashback_secret", category="discovery")

    $ total = len(demo_flashback.memories)
    "Memories registered: [total]"

    "Unlocking 'First Meeting' memory..."
    $ demo_flashback.unlock_memory("mem_meeting", show_notification=False)
    $ unlocked = demo_flashback.get_unlocked_memories()
    "Unlocked memories: [len(unlocked)]"

    "Unlocking 'The Discovery' memory..."
    $ demo_flashback.unlock_memory("mem_discovery", show_notification=False)

    "Unlocking 'Elena's Laugh' memory..."
    $ demo_flashback.unlock_memory("mem_elena_laugh", show_notification=False)

    $ unlocked = demo_flashback.get_unlocked_memories()
    $ total_count = len(demo_flashback.memories)
    "Memories: [len(unlocked)]/[total_count] unlocked"

    $ story_mems = demo_flashback.get_memories_by_category("story")
    $ disc_mems = demo_flashback.get_memories_by_category("discovery")
    $ char_mems = demo_flashback.get_memories_by_category("character")
    "Story: [len(story_mems)] | Discovery: [len(disc_mems)] | Character: [len(char_mems)]"

    $ is_unlocked = demo_flashback.is_memory_unlocked("mem_meeting")
    $ is_locked = demo_flashback.is_memory_unlocked("mem_secret")
    "First Meeting unlocked: [is_unlocked]"
    "Hidden Chamber unlocked: [is_locked]"

    "Replay unlocked memories from the gallery anytime!"

    return

# =============================================================================
# MINIGAMES DEMO
# =============================================================================
label demo_minigames:
    scene bg room
    "=== MINIGAMES SYSTEM ==="

    python:
        demo_number_game = NumberGuessingGame()
        demo_memory_game = MemoryCardGame()

    "Available minigames:"
    "1. Number Guessing - Guess the secret number"
    "2. Memory Match - Match pairs of cards"

    "Starting Number Guessing Game..."
    $ demo_number_game.set_difficulty(MinigameBase.MEDIUM)
    $ diff = demo_number_game.get_difficulty_name()
    "Difficulty: [diff]"

    $ demo_number_game.start()
    $ min_n = demo_number_game.min_num
    $ max_n = demo_number_game.max_num
    $ guesses = demo_number_game.guesses_left
    "Guess a number between [min_n] and [max_n]"
    "Guesses remaining: [guesses]"

    "Guessing 50..."
    $ hint = demo_number_game.make_guess(50)
    "[hint]"

    $ guesses = demo_number_game.guesses_left
    "Guesses remaining: [guesses]"

    "Testing Memory Card Game..."
    $ demo_memory_game.set_difficulty(MinigameBase.EASY)
    $ demo_memory_game.start()
    $ pairs = demo_memory_game.pairs_found
    $ total = demo_memory_game.total_pairs
    "Memory game: [pairs]/[total] pairs found"

    $ high_score = demo_number_game.high_score
    $ attempts = demo_number_game.attempts
    $ win_rate = demo_number_game.get_win_rate()
    "Stats - High Score: [high_score] | Attempts: [attempts] | Win Rate: [win_rate] percent"

    python:
        # Simulate a win for reward demo
        demo_number_game.score = 50
        demo_number_game.end(won=True)
        rewards = RewardSystem.calculate_reward(demo_number_game)

    $ gold = rewards["gold"]
    $ xp = rewards["xp"]
    "Win rewards: [gold] gold, [xp] XP"

    "Minigames can be played anytime for rewards!"

    return

# =============================================================================
# CRAFTING DEMO
# =============================================================================
label demo_crafting:
    scene bg room
    "=== CRAFTING SYSTEM ==="

    python:
        demo_craft = CraftingManager()
        # Register recipes
        health_potion = Recipe("health_potion", "Health Potion", {"herb": 2, "water": 1}, result_item="health_potion", result_quantity=1, category="potions", description="Restores 50 HP")
        iron_sword = Recipe("iron_sword", "Iron Sword", {"iron_ore": 3, "wood": 1}, result_item="iron_sword", category="weapons", description="A sturdy blade")
        magic_ring = Recipe("magic_ring", "Magic Ring", {"silver": 2, "gem": 1, "essence": 1}, result_item="magic_ring", category="accessories", description="Increases magic power", unlock_condition="learn_enchanting")
        demo_craft.register_recipe(health_potion)
        demo_craft.register_recipe(iron_sword)
        demo_craft.register_recipe(magic_ring)

    $ recipe_count = len(demo_craft.recipes)
    $ categories = demo_craft.get_categories()
    $ cat_count = len(categories)
    "Recipes: [recipe_count] | Categories: [cat_count]"

    "Recipe: Health Potion"
    $ hp_recipe = demo_craft.get_recipe("health_potion")
    $ hp_ingredients = hp_recipe.get_ingredients_list()
    "Requires: 2 Herb, 1 Water"

    "Recipe: Iron Sword"
    "Requires: 3 Iron Ore, 1 Wood"

    $ unlocked = demo_craft.get_unlocked_recipes()
    $ locked = demo_craft.get_locked_recipes()
    "Unlocked recipes: [len(unlocked)] | Locked: [len(locked)]"

    "The Magic Ring recipe is locked until you learn enchanting!"

    python:
        # Simulate having ingredients
        test_inventory = {"herb": 5, "water": 3, "iron_ore": 2}
        demo_craft.set_inventory_callbacks(lambda: test_inventory)

    $ can_craft_potion = demo_craft.can_craft("health_potion")
    $ can_craft_sword = demo_craft.can_craft("iron_sword")
    "Can craft Health Potion: [can_craft_potion]"
    "Can craft Iron Sword: [can_craft_sword] (need more iron)"

    $ potion_recipes = demo_craft.get_recipes_by_category("potions")
    $ weapon_recipes = demo_craft.get_recipes_by_category("weapons")
    "Potion recipes: [len(potion_recipes)] | Weapon recipes: [len(weapon_recipes)]"

    "Craft items at workstations throughout the world!"

    return

# =============================================================================
# MUSIC DEMO
# =============================================================================
label demo_music:
    scene bg room
    "=== DYNAMIC MUSIC SYSTEM ==="

    python:
        demo_music = MusicManager()
        # Add music layers
        demo_music.add_layer("base", "audio/base_loop.mp3", volume=0.8, active=True)
        demo_music.add_layer("ambient", "audio/ambient.mp3", volume=0.5)
        demo_music.add_layer("tension", "audio/tension.mp3", volume=0.7)
        demo_music.add_layer("combat", "audio/combat.mp3", volume=0.9)
        demo_music.add_layer("melody", "audio/melody.mp3", volume=0.6)

    $ layer_count = len(demo_music.layers)
    $ context = demo_music.current_context
    "Music layers: [layer_count] | Current context: [context]"

    "Contexts: calm, tension, combat, romance, mystery, celebration, sadness"

    "Setting context to 'calm'..."
    $ demo_music.set_context("calm")
    $ active = [l.id for l in demo_music.layers.values() if l.active]
    $ active_count = len(active)
    "Active layers: [active_count] (base, ambient)"

    "Tension is rising..."
    $ demo_music.set_context("tension")
    $ context = demo_music.current_context
    $ active = [l.id for l in demo_music.layers.values() if l.active]
    $ active_count = len(active)
    "Context: [context] | Active layers: [active_count]"

    "Combat begins!"
    $ demo_music.set_context("combat")
    $ intensity = demo_music.intensity
    "Intensity: [intensity]"

    $ master_vol = demo_music.master_volume
    "Master volume: [master_vol]"

    "Ducking music for dialogue..."
    $ demo_music.duck_music(True)
    $ is_ducked = demo_music.is_ducked
    "Music ducked: [is_ducked]"

    "Restoring music..."
    $ demo_music.duck_music(False)

    "Music adapts dynamically to story context!"

    return

# =============================================================================
# ACCESSIBILITY DEMO
# =============================================================================
label demo_accessibility:
    scene bg room
    "=== ACCESSIBILITY SYSTEM ==="

    python:
        demo_access = AccessibilityManager()

    $ font_scale = demo_access.font_scale
    $ high_contrast = demo_access.high_contrast
    $ colorblind = demo_access.colorblind_mode
    "Font scale: [font_scale] | High contrast: [high_contrast]"
    "Colorblind mode: [colorblind]"

    "Available settings:"
    "- Font scaling (0.8x to 1.5x)"
    "- High contrast mode"
    "- Colorblind modes (protanopia, deuteranopia, tritanopia)"
    "- Reduce motion option"
    "- Button hold time for motor accessibility"

    "Increasing font size..."
    $ demo_access.font_scale = 1.2
    $ new_scale = demo_access.font_scale
    "Font scale: [new_scale]"

    "Enabling high contrast..."
    $ demo_access.high_contrast = True
    $ hc = demo_access.high_contrast
    "High contrast: [hc]"

    "Setting colorblind mode: deuteranopia..."
    $ demo_access.colorblind_mode = "deuteranopia"
    $ cb_mode = demo_access.colorblind_mode
    "Colorblind mode: [cb_mode]"

    $ reduce = demo_access.reduce_motion
    $ hold_time = demo_access.button_hold_time
    "Reduce motion: [reduce] | Button hold time: [hold_time]s"

    $ text_size = demo_access.get_scaled_size(24)
    $ name_size = demo_access.get_scaled_size(28)
    "Scaled text size: [text_size] | Name size: [name_size]"

    "Restoring defaults..."
    python:
        demo_access.font_scale = 1.0
        demo_access.high_contrast = False
        demo_access.colorblind_mode = "none"

    "All settings persist across game sessions!"

    return

# =============================================================================
# MODS DEMO
# =============================================================================
label demo_mods:
    scene bg room
    "=== MOD FRAMEWORK ==="

    python:
        demo_mod_mgr = ModManager()
        # Create demo mods (normally these would be discovered from filesystem)
        demo_mod1 = Mod("extra_content", "Extra Content Pack", version="1.2.0", author="CommunityDev", description="Adds new scenes and characters", priority=50)
        demo_mod2 = Mod("new_music", "Enhanced Soundtrack", version="2.0.0", author="MusicMaker", description="New music tracks", priority=100)
        demo_mod3 = Mod("hard_mode", "Challenge Mode", version="1.0.0", author="DifficultDev", description="Makes combat harder", priority=150, conflicts=["easy_mode"])
        demo_mod_mgr._mods["extra_content"] = demo_mod1
        demo_mod_mgr._mods["new_music"] = demo_mod2
        demo_mod_mgr._mods["hard_mode"] = demo_mod3

    $ mod_count = len(demo_mod_mgr.mods)
    "Discovered mods: [mod_count]"

    "Available mods:"
    $ m1_name = demo_mod1.name
    $ m1_ver = demo_mod1.version
    $ m1_author = demo_mod1.author
    "- [m1_name] v[m1_ver] by [m1_author]"

    $ m2_name = demo_mod2.name
    $ m2_ver = demo_mod2.version
    "- [m2_name] v[m2_ver]"

    $ m3_name = demo_mod3.name
    "- [m3_name] (conflicts with Easy Mode)"

    "Enabling 'Extra Content Pack'..."
    $ demo_mod_mgr.enable_mod("extra_content")
    $ enabled = demo_mod_mgr.get_enabled_mods()
    $ enabled_count = len(enabled)
    "Enabled mods: [enabled_count]"

    "Enabling 'Enhanced Soundtrack'..."
    $ demo_mod_mgr.enable_mod("new_music")
    $ enabled = demo_mod_mgr.get_enabled_mods()
    $ enabled_count = len(enabled)
    "Enabled mods: [enabled_count]"

    $ valid, errors = demo_mod1.validate()
    "Extra Content valid: [valid]"

    $ mod_list = demo_mod_mgr.get_mod_list()
    $ list_count = len(mod_list)
    "Total mods available: [list_count] (sorted by priority)"

    "Mods are loaded from game/mods/ directory!"
    "Each mod needs a mod.json manifest file."

    return
