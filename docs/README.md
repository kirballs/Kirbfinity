# CurseForge Favorites Categorization

This directory contains tools to scrape and categorize CurseForge favorites for the Kirbfinity modpack.

## Overview

The Kirbfinity modpack targets **Minecraft 1.20.1 with Forge 47.4.5**. These tools help organize favorited mods from CurseForge into logical categories, making it easy to:

- See which mods are compatible with 1.20.1
- Identify resource packs (saved for asset extraction)
- Track non-1.20.1 mods (also for asset extraction)
- Categorize mods by type (Exploration, Decoration, World Gen, etc.)

## Tools

### 1. `scrape_curseforge_favorites.py` (Direct Web Scraping)

**Requirements:**
```bash
pip install beautifulsoup4 lxml requests
```

**Usage:**
```bash
python3 scrape_curseforge_favorites.py
```

This script directly scrapes the CurseForge favorites page and generates a categorized markdown file. Use this if you have direct internet access to CurseForge.

**Note**: This may not work in all environments due to network restrictions or CurseForge's structure changes.

### 2. `categorize_from_json.py` (JSON-Based Processing)

**Usage:**
```bash
python3 categorize_from_json.py [input.json] [output.md]
```

**Default files:**
- Input: `favorites-data.json`
- Output: `curseforge-favorites.md`

This is the recommended approach if web scraping is not available. It processes a JSON file containing mod data.

## JSON Data Format

The `favorites-data.json` file should follow this structure:

```json
{
  "metadata": {
    "username": "kirbskyer",
    "modpack_version": "1.20.1",
    "forge_version": "47.4.5",
    "last_updated": "2026-01-03"
  },
  "favorites": [
    {
      "name": "Mod Name",
      "url": "https://www.curseforge.com/minecraft/mc-mods/example",
      "description": "Brief description of the mod",
      "game_versions": ["1.20.1", "1.20", "1.19.4"],
      "mod_type": "mod",
      "categories": ["decoration", "building"]
    }
  ]
}
```

### Field Descriptions

- **name**: The mod's display name
- **url**: Full CurseForge URL to the mod
- **description**: Brief description (optional)
- **game_versions**: Array of supported Minecraft versions
- **mod_type**: Either `"mod"` or `"resourcepack"`
- **categories**: Array of category hints (used for auto-categorization)

## Data Collection Methods

### Method 1: JavaScript Browser Console (Recommended)

Use the `extract-favorites.js` script to automatically extract data from the browser:

1. Visit https://www.curseforge.com/members/kirbskyer/favorites
2. Open browser DevTools (F12)
3. Go to the Console tab
4. Copy and paste the contents of `extract-favorites.js`
5. Press Enter to run it
6. The JSON data will be output to the console and copied to clipboard
7. Save the JSON output to `favorites-data.json`
8. Run: `python3 categorize_from_json.py`

**Note**: You may need to visit individual mod pages to get accurate version information.

### Method 2: Manual Entry

If you need to manually collect data from CurseForge:

1. Visit https://www.curseforge.com/members/kirbskyer/favorites
2. For each mod, collect:
   - Name
   - URL
   - Description (from the mod page)
   - Supported versions (check the "Game Versions" tab)
   - Type (mod or resource pack)
3. Add entries to `favorites-data.json`
4. Run: `python3 categorize_from_json.py`

## Categories

The script automatically categorizes mods based on keywords:

- **Exploration**: Adventure, dungeons, structures, dimensions
- **Mobs/Creatures**: Animals, enemies, spawns, entities
- **Building**: Construction, architecture
- **Decoration**: Furniture, decorative blocks, aesthetics
- **World Generation**: Terrain, ores, caves, biomes
- **Tools**: Utilities, equipment, weapons
- **Food/Farming**: Agriculture, cooking, crops
- **Transportation**: Vehicles, travel, movement
- **Storage**: Inventory, chests, containers
- **Optimization**: Performance, FPS improvements
- **Library**: APIs, frameworks, dependencies
- **Quality of Life**: GUI, HUD, tooltips, convenience
- **Audio/Visual**: Sounds, graphics, shaders, particles
- **Nature**: Trees, plants, flowers, forests
- **Other**: Anything that doesn't fit above

## Output Format

The generated `curseforge-favorites.md` includes:

1. **Compatible Mods (1.20.1 Forge)** - Organized by category
2. **Resource Packs (For Asset Reference)** - Separate section
3. **Non-1.20.1 Mods (For Asset Reference)** - Separate section
4. **Summary** - Statistics

## Modpack Context

The Kirbfinity modpack:
- Targets Minecraft 1.20.1 with Forge 47.4.5
- Avoids tech, magic, and quest content
- Keeps resource packs and non-1.20.1 mods favorited for asset extraction purposes only

## Updating the List

To update the favorites list:

1. Update `favorites-data.json` with new mods
2. Run: `python3 categorize_from_json.py`
3. Review the generated `curseforge-favorites.md`
4. Commit both files to the repository

## Example

```bash
# Edit the data file
nano favorites-data.json

# Generate the categorized list
python3 categorize_from_json.py

# Review the output
cat curseforge-favorites.md
```

## Troubleshooting

**Script fails to scrape CurseForge directly:**
- Use the JSON-based approach instead
- CurseForge may have updated their HTML structure
- Network restrictions may block access

**Mods are miscategorized:**
- Update the `categories` field in `favorites-data.json` with better keywords
- The script uses keyword matching to determine categories

**Missing version information:**
- Check the mod's CurseForge page under "Game Versions"
- Add all supported versions to the `game_versions` array

## License

These tools are part of the Kirbfinity modpack repository and follow the same license.
