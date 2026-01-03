#!/usr/bin/env python3
"""
CurseForge Favorites Scraper and Categorizer

This script scrapes the CurseForge favorites page for user 'kirbskyer' and
categorizes the mods into logical groups for the Kirbfinity modpack (1.20.1 Forge 47.4.5).

Usage:
    python3 scrape_curseforge_favorites.py

Output:
    curseforge-favorites.md - Categorized list of mods
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ModInfo:
    """Information about a CurseForge mod."""
    name: str
    url: str
    description: str = ""
    game_versions: List[str] = field(default_factory=list)
    mod_type: str = "mod"  # mod, resourcepack, etc.
    categories: List[str] = field(default_factory=list)
    
    def is_compatible_version(self) -> bool:
        """Check if mod is compatible with 1.20.1"""
        return any('1.20.1' in version for version in self.game_versions)
    
    def is_resource_pack(self) -> bool:
        """Check if this is a resource pack"""
        return self.mod_type.lower() == 'resourcepack' or 'resource pack' in self.name.lower()


class CurseForgeScraper:
    """Scrapes and categorizes CurseForge favorites."""
    
    def __init__(self, username: str = "kirbskyer"):
        self.username = username
        self.base_url = f"https://www.curseforge.com/members/{username}/favorites"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.mods: List[ModInfo] = []
        
        # Category keywords for auto-categorization
        self.category_keywords = {
            'Exploration': ['exploration', 'adventure', 'dungeon', 'structure', 'biome', 'dimension'],
            'Mobs/Creatures': ['mob', 'creature', 'animal', 'enemy', 'spawn', 'entity'],
            'Building': ['building', 'construction', 'architect'],
            'Decoration': ['decoration', 'decorative', 'furniture', 'decor', 'aesthetic'],
            'World Generation': ['worldgen', 'generation', 'terrain', 'ore', 'cave'],
            'Tools': ['tool', 'utility', 'equipment'],
            'Food/Farming': ['food', 'farming', 'agriculture', 'cooking', 'crop'],
            'Transportation': ['transport', 'vehicle', 'travel', 'movement'],
            'Storage': ['storage', 'inventory', 'chest', 'container'],
            'Optimization': ['optimization', 'performance', 'fps', 'lag'],
            'Library': ['library', 'api', 'core', 'framework'],
            'Quality of Life': ['qol', 'quality of life', 'convenience', 'gui', 'hud', 'interface'],
            'Audio/Visual': ['visual', 'audio', 'sound', 'shader', 'graphics'],
        }
    
    def fetch_favorites(self) -> bool:
        """Fetch the favorites page from CurseForge."""
        try:
            print(f"Fetching favorites from: {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Error: Status code {response.status_code}")
                return False
            
            print("Successfully fetched favorites page")
            self.parse_html(response.text)
            return True
            
        except Exception as e:
            print(f"Error fetching favorites: {e}")
            return False
    
    def parse_html(self, html: str):
        """Parse HTML and extract mod information."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # CurseForge uses various classes for project listings
        # This will need to be adjusted based on actual HTML structure
        project_cards = soup.find_all(['div', 'li'], class_=re.compile(r'project|item|card'))
        
        print(f"Found {len(project_cards)} potential mod entries")
        
        for card in project_cards:
            mod_info = self.extract_mod_info(card)
            if mod_info:
                self.mods.append(mod_info)
        
        print(f"Successfully parsed {len(self.mods)} mods")
    
    def extract_mod_info(self, element) -> Optional[ModInfo]:
        """Extract mod information from HTML element."""
        try:
            # Look for mod name and link
            link = element.find('a', href=re.compile(r'/minecraft/'))
            if not link:
                return None
            
            name = link.get_text(strip=True)
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"https://www.curseforge.com{url}"
            
            # Extract description
            desc_elem = element.find(['p', 'div'], class_=re.compile(r'description|summary'))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract game versions (if available)
            version_elem = element.find(['span', 'div'], class_=re.compile(r'version|game-version'))
            versions = []
            if version_elem:
                versions = [v.strip() for v in version_elem.get_text().split(',')]
            
            # Determine mod type
            mod_type = 'mod'
            if '/texture-packs/' in url or '/resource-packs/' in url:
                mod_type = 'resourcepack'
            
            # Extract categories
            categories = []
            cat_elements = element.find_all(['a', 'span'], class_=re.compile(r'category|tag'))
            for cat_elem in cat_elements:
                categories.append(cat_elem.get_text(strip=True))
            
            return ModInfo(
                name=name,
                url=url,
                description=description,
                game_versions=versions,
                mod_type=mod_type,
                categories=categories
            )
        except Exception as e:
            print(f"Error extracting mod info: {e}")
            return None
    
    def categorize_mod(self, mod: ModInfo) -> str:
        """Determine the best category for a mod based on keywords."""
        # Check mod name and description
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
        output = ["# CurseForge Favorites - Categorized\n"]
        output.append("*Auto-generated categorization of kirbskyer's CurseForge favorites*\n")
        output.append("*Modpack: Kirbfinity - Minecraft 1.20.1 Forge 47.4.5*\n")
        
        # Separate mods by compatibility
        compatible_mods = [m for m in self.mods if not m.is_resource_pack() and m.is_compatible_version()]
        resource_packs = [m for m in self.mods if m.is_resource_pack()]
        incompatible_mods = [m for m in self.mods if not m.is_resource_pack() and not m.is_compatible_version()]
        
        # Categorize compatible mods
        categorized = {}
        for mod in compatible_mods:
            category = self.categorize_mod(mod)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(mod)
        
        # Output compatible mods by category
        output.append("## Compatible Mods (1.20.1 Forge)\n")
        
        for category in sorted(categorized.keys()):
            output.append(f"### {category}\n")
            for mod in sorted(categorized[category], key=lambda m: m.name.lower()):
                desc = f" - {mod.description[:100]}..." if len(mod.description) > 100 else f" - {mod.description}" if mod.description else ""
                output.append(f"- [{mod.name}]({mod.url}){desc}\n")
            output.append("\n")
        
        # Output resource packs
        if resource_packs:
            output.append("## Resource Packs (For Asset Reference)\n")
            output.append("*These are saved for extracting assets, not for direct inclusion*\n\n")
            for mod in sorted(resource_packs, key=lambda m: m.name.lower()):
                versions = ", ".join(mod.game_versions) if mod.game_versions else "version info needed"
                output.append(f"- [{mod.name}]({mod.url}) - {versions}\n")
            output.append("\n")
        
        # Output incompatible mods
        if incompatible_mods:
            output.append("## Non-1.20.1 Mods (For Asset Reference)\n")
            output.append("*These are saved for extracting assets, not for direct inclusion*\n\n")
            for mod in sorted(incompatible_mods, key=lambda m: m.name.lower()):
                versions = ", ".join(mod.game_versions) if mod.game_versions else "version info needed"
                output.append(f"- [{mod.name}]({mod.url}) - Available versions: {versions}\n")
            output.append("\n")
        
        return "".join(output)
    
    def save_to_file(self, filename: str = "curseforge-favorites.md"):
        """Save the categorized list to a markdown file."""
        content = self.generate_markdown()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved to {filename}")


def main():
    """Main execution function."""
    scraper = CurseForgeScraper("kirbskyer")
    
    print("=" * 60)
    print("CurseForge Favorites Scraper")
    print("=" * 60)
    
    if scraper.fetch_favorites():
        scraper.save_to_file("curseforge-favorites.md")
        print("\nDone! Check curseforge-favorites.md for the results.")
    else:
        print("\nFailed to fetch favorites. Please check:")
        print("1. Internet connection")
        print("2. CurseForge website availability")
        print("3. Username is correct (currently: kirbskyer)")


if __name__ == "__main__":
    main()
