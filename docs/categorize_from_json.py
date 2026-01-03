#!/usr/bin/env python3
"""
CurseForge Favorites Categorizer from JSON

This script reads mod data from favorites-data.json and generates a categorized
markdown file for the Kirbfinity modpack (1.20.1 Forge 47.4.5).

Usage:
    python3 categorize_from_json.py [input.json] [output.md]

Input JSON format:
    {
      "metadata": {...},
      "favorites": [
        {
          "name": "Mod Name",
          "url": "https://...",
          "description": "...",
          "game_versions": ["1.20.1", ...],
          "mod_type": "mod|resourcepack",
          "categories": ["category1", ...]
        }
      ]
    }
"""

import json
import sys
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class ModInfo:
    """Information about a CurseForge mod."""
    name: str
    url: str
    description: str = ""
    game_versions: List[str] = field(default_factory=list)
    mod_type: str = "mod"
    categories: List[str] = field(default_factory=list)
    
    def is_compatible_version(self) -> bool:
        """Check if mod is compatible with 1.20.1"""
        return any('1.20.1' in version for version in self.game_versions)
    
    def is_resource_pack(self) -> bool:
        """Check if this is a resource pack"""
        return self.mod_type.lower() in ['resourcepack', 'resource-pack', 'texturepack', 'texture-pack']


class FavoritesCategorizer:
    """Categorizes CurseForge favorites from JSON data."""
    
    def __init__(self):
        self.mods: List[ModInfo] = []
        self.metadata = {}
        
        # Category keywords for auto-categorization
        self.category_keywords = {
            'Exploration': ['exploration', 'adventure', 'dungeon', 'structure', 'tower', 'quest'],
            'Mobs/Creatures': ['mob', 'creature', 'animal', 'enemy', 'spawn', 'entity', 'boss'],
            'Building': ['building', 'construction', 'architect', 'blueprint'],
            'Decoration': ['decoration', 'decorative', 'furniture', 'decor', 'aesthetic', 'prop'],
            'World Generation': ['worldgen', 'generation', 'terrain', 'ore', 'cave', 'biome'],
            'Tools': ['tool', 'utility', 'equipment', 'weapon'],
            'Food/Farming': ['food', 'farming', 'agriculture', 'cooking', 'crop', 'harvest'],
            'Transportation': ['transport', 'vehicle', 'travel', 'movement', 'horse', 'boat'],
            'Storage': ['storage', 'inventory', 'chest', 'container', 'backpack'],
            'Optimization': ['optimization', 'performance', 'fps', 'lag', 'memory'],
            'Library': ['library', 'api', 'core', 'framework', 'loader'],
            'Quality of Life': ['qol', 'quality of life', 'convenience', 'gui', 'hud', 'interface', 'tooltip', 'waila'],
            'Audio/Visual': ['visual', 'audio', 'sound', 'shader', 'graphics', 'particle', 'effect'],
            'Nature': ['tree', 'plant', 'flower', 'nature', 'forest', 'garden'],
        }
    
    def load_from_json(self, filename: str = "favorites-data.json"):
        """Load mod data from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.metadata = data.get('metadata', {})
            
            for item in data.get('favorites', []):
                mod = ModInfo(
                    name=item['name'],
                    url=item['url'],
                    description=item.get('description', ''),
                    game_versions=item.get('game_versions', []),
                    mod_type=item.get('mod_type', 'mod'),
                    categories=item.get('categories', [])
                )
                self.mods.append(mod)
            
            print(f"Loaded {len(self.mods)} mods from {filename}")
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in '{filename}': {e}")
            return False
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return False
    
    def categorize_mod(self, mod: ModInfo) -> str:
        """Determine the best category for a mod based on keywords."""
        # Combine all text for analysis
        text = (mod.name + " " + mod.description + " " + " ".join(mod.categories)).lower()
        
        best_category = 'Other'
        max_matches = 0
        
        for category, keywords in self.category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return best_category
    
    def generate_markdown(self) -> str:
        """Generate categorized markdown output."""
        output = ["# CurseForge Favorites - Categorized\n\n"]
        
        # Add metadata
        if self.metadata:
            output.append(f"**User**: {self.metadata.get('username', 'kirbskyer')}  \n")
            output.append(f"**Modpack**: Kirbfinity  \n")
            output.append(f"**Target Version**: Minecraft {self.metadata.get('modpack_version', '1.20.1')} ")
            output.append(f"Forge {self.metadata.get('forge_version', '47.4.5')}  \n")
            if 'last_updated' in self.metadata:
                output.append(f"**Last Updated**: {self.metadata['last_updated']}  \n")
            output.append("\n")
        
        output.append("*This modpack avoids tech, magic, and quest content.*\n\n")
        output.append("---\n\n")
        
        # Separate mods by compatibility
        compatible_mods = [m for m in self.mods if not m.is_resource_pack() and m.is_compatible_version()]
        resource_packs = [m for m in self.mods if m.is_resource_pack()]
        incompatible_mods = [m for m in self.mods if not m.is_resource_pack() and not m.is_compatible_version()]
        unknown_version = [m for m in self.mods if not m.is_resource_pack() and not m.game_versions]
        
        # Categorize compatible mods
        categorized = {}
        for mod in compatible_mods:
            category = self.categorize_mod(mod)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(mod)
        
        # Output compatible mods by category
        output.append("## Compatible Mods (1.20.1 Forge)\n\n")
        output.append(f"*{len(compatible_mods)} mods compatible with the target version*\n\n")
        
        for category in sorted(categorized.keys()):
            output.append(f"### {category}\n\n")
            for mod in sorted(categorized[category], key=lambda m: m.name.lower()):
                desc = mod.description
                if desc:
                    # Truncate long descriptions
                    if len(desc) > 150:
                        desc = desc[:150] + "..."
                    output.append(f"- **[{mod.name}]({mod.url})** - {desc}\n")
                else:
                    output.append(f"- **[{mod.name}]({mod.url})**\n")
            output.append("\n")
        
        # Output resource packs
        if resource_packs:
            output.append("---\n\n")
            output.append("## Resource Packs (For Asset Reference)\n\n")
            output.append("*These are saved for extracting assets, not for direct inclusion in the modpack.*\n\n")
            for mod in sorted(resource_packs, key=lambda m: m.name.lower()):
                versions = ", ".join(mod.game_versions) if mod.game_versions else "version not specified"
                desc = f" - {mod.description}" if mod.description else ""
                output.append(f"- **[{mod.name}]({mod.url})** ({versions}){desc}\n")
            output.append("\n")
        
        # Output incompatible mods
        if incompatible_mods:
            output.append("---\n\n")
            output.append("## Non-1.20.1 Mods (For Asset Reference)\n\n")
            output.append("*These are saved for extracting assets, not for direct inclusion in the modpack.*\n\n")
            for mod in sorted(incompatible_mods, key=lambda m: m.name.lower()):
                versions = ", ".join(mod.game_versions) if mod.game_versions else "version not specified"
                desc = f" - {mod.description}" if mod.description else ""
                output.append(f"- **[{mod.name}]({mod.url})** (Available: {versions}){desc}\n")
            output.append("\n")
        
        # Output mods with unknown versions
        if unknown_version:
            output.append("---\n\n")
            output.append("## Mods with Unknown Version Compatibility\n\n")
            output.append("*Version information needed for these mods.*\n\n")
            for mod in sorted(unknown_version, key=lambda m: m.name.lower()):
                desc = f" - {mod.description}" if mod.description else ""
                output.append(f"- **[{mod.name}]({mod.url})**{desc}\n")
            output.append("\n")
        
        # Summary
        output.append("---\n\n")
        output.append("## Summary\n\n")
        output.append(f"- **Compatible Mods**: {len(compatible_mods)}\n")
        output.append(f"- **Resource Packs**: {len(resource_packs)}\n")
        output.append(f"- **Non-1.20.1 Mods**: {len(incompatible_mods)}\n")
        if unknown_version:
            output.append(f"- **Unknown Version**: {len(unknown_version)}\n")
        output.append(f"- **Total**: {len(self.mods)}\n")
        
        return "".join(output)
    
    def save_to_file(self, filename: str = "curseforge-favorites.md"):
        """Save the categorized list to a markdown file."""
        content = self.generate_markdown()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved to {filename}")


def main():
    """Main execution function."""
    input_file = sys.argv[1] if len(sys.argv) > 1 else "favorites-data.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "curseforge-favorites.md"
    
    print("=" * 60)
    print("CurseForge Favorites Categorizer")
    print("=" * 60)
    print()
    
    categorizer = FavoritesCategorizer()
    
    if categorizer.load_from_json(input_file):
        categorizer.save_to_file(output_file)
        print()
        print("Done! Check the output file for results.")
        print()
        print("Categories used:")
        for category in sorted(categorizer.category_keywords.keys()):
            print(f"  - {category}")
    else:
        print()
        print("Failed to process favorites. Please check the input file.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
