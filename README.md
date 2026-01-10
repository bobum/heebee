# Heebee

A visual novel created with [Ren'Py](https://www.renpy.org/).

## Getting Started

### Prerequisites

- Ren'Py SDK 8.3+ (included in this repository under `renpy-8.3.3-sdk/`)

### Running the Game

1. **Using the included SDK:**
   ```bash
   ./renpy-8.3.3-sdk/renpy.sh .
   ```

2. **Or download Ren'Py separately:**
   - Download from [renpy.org](https://www.renpy.org/latest.html)
   - Open the Ren'Py launcher
   - Click "preferences" and add this project folder
   - Select the project and click "Launch Project"

## Project Structure

```
heebee/
├── game/
│   ├── script.rpy      # Main story script
│   ├── options.rpy     # Game configuration (title, version, etc.)
│   ├── gui.rpy         # GUI styling (colors, fonts, sizes)
│   ├── screens.rpy     # UI screen definitions
│   ├── images/         # Image assets
│   │   ├── characters/ # Character sprites
│   │   └── backgrounds/# Background images
│   └── gui/            # GUI image assets
├── renpy-8.3.3-sdk/    # Ren'Py SDK (not tracked in git)
└── README.md
```

## Writing Your Story

The main story lives in `game/script.rpy`. Key concepts:

### Characters
```renpy
define e = Character("Elena", color="#c8ffc8")
```

### Dialogue
```renpy
e "Hello! This is Elena speaking."
"This is narration with no speaker."
```

### Choices
```renpy
menu:
    "What do you want to do?"

    "Option A":
        jump option_a_path

    "Option B":
        jump option_b_path
```

### Images
```renpy
scene bg library          # Show background
show elena happy          # Show character
hide elena                # Hide character
```

### Transitions
```renpy
scene bg sunset with fade
show elena happy with dissolve
```

## Adding Assets

1. **Character sprites:** Place in `game/images/characters/`
2. **Backgrounds:** Place in `game/images/backgrounds/`
3. **Music:** Create `game/audio/` and add `.mp3` or `.ogg` files
4. **GUI images:** Place in `game/gui/`

Ren'Py auto-detects images by filename. Name them like:
- `elena happy.png` → accessible as `show elena happy`
- `bg library.png` → accessible as `scene bg library`

## Documentation

- [Ren'Py Documentation](https://www.renpy.org/doc/html/)
- [Quickstart Guide](https://www.renpy.org/doc/html/quickstart.html)
- [GUI Customization](https://www.renpy.org/doc/html/gui.html)
- [Ren'Py Cookbook](https://www.renpy.org/wiki/renpy/Cookbook)

## License

This project is available under the MIT License.

The Ren'Py engine is available under its own license. See [renpy.org](https://www.renpy.org/) for details.
