/**
 * CurseForge Favorites Data Extractor
 * 
 * This JavaScript snippet can be run in the browser console while viewing
 * the CurseForge favorites page to extract mod data in JSON format.
 * 
 * Usage:
 * 1. Go to https://www.curseforge.com/members/kirbskyer/favorites
 * 2. Open browser DevTools (F12)
 * 3. Go to the Console tab
 * 4. Copy and paste this entire script
 * 5. Press Enter to run it
 * 6. The JSON data will be logged to console
 * 7. Copy the JSON output and save it to favorites-data.json
 * 
 * Alternative: Save this as a bookmarklet
 */

(function() {
  console.log('Starting CurseForge Favorites extraction...');
  
  const data = {
    metadata: {
      username: 'kirbskyer',
      modpack_version: '1.20.1',
      forge_version: '47.4.5',
      last_updated: new Date().toISOString().split('T')[0]
    },
    favorites: []
  };
  
  // Try to find project cards (CurseForge's structure may vary)
  // Adjust selectors based on actual page structure
  const selectors = [
    '.project-card',
    '.project-list-item',
    '.project-listing-row',
    '[class*="project"]',
    '[class*="ProjectCard"]',
    '[class*="favorites-list"] > *'
  ];
  
  let projectElements = [];
  
  for (const selector of selectors) {
    projectElements = document.querySelectorAll(selector);
    if (projectElements.length > 0) {
      console.log(`Found ${projectElements.length} projects using selector: ${selector}`);
      break;
    }
  }
  
  if (projectElements.length === 0) {
    console.error('Could not find any project elements. The page structure may have changed.');
    console.log('Available elements:', document.body.innerHTML.substring(0, 500));
    return;
  }
  
  projectElements.forEach((element, index) => {
    try {
      // Find the mod link
      const link = element.querySelector('a[href*="/minecraft/"]') || 
                   element.querySelector('a[href*="curseforge.com"]');
      
      if (!link) {
        console.warn(`Element ${index}: No link found`);
        return;
      }
      
      const url = link.href.startsWith('http') ? link.href : `https://www.curseforge.com${link.href}`;
      
      // Extract mod name
      const nameElement = element.querySelector('[class*="name"]') || 
                         element.querySelector('[class*="title"]') ||
                         link;
      const name = nameElement ? nameElement.textContent.trim() : `Unknown Mod ${index}`;
      
      // Extract description
      const descElement = element.querySelector('[class*="description"]') ||
                         element.querySelector('[class*="summary"]') ||
                         element.querySelector('p');
      const description = descElement ? descElement.textContent.trim() : '';
      
      // Extract categories/tags
      const categoryElements = element.querySelectorAll('[class*="tag"]') ||
                              element.querySelectorAll('[class*="category"]');
      const categories = Array.from(categoryElements).map(el => el.textContent.trim());
      
      // Determine mod type
      let mod_type = 'mod';
      if (url.includes('/texture-packs/') || url.includes('/resource-packs/')) {
        mod_type = 'resourcepack';
      }
      
      // Extract version info (if available on this page)
      const versionElement = element.querySelector('[class*="version"]') ||
                            element.querySelector('[class*="game-version"]');
      const game_versions = [];
      if (versionElement) {
        const versionText = versionElement.textContent;
        // Try to extract version numbers
        const versionMatches = versionText.match(/1\.\d+(\.\d+)?/g);
        if (versionMatches) {
          game_versions.push(...versionMatches);
        }
      }
      
      data.favorites.push({
        name,
        url,
        description,
        game_versions,
        mod_type,
        categories
      });
      
      console.log(`Extracted: ${name}`);
      
    } catch (error) {
      console.error(`Error processing element ${index}:`, error);
    }
  });
  
  console.log(`\nExtracted ${data.favorites.length} mods`);
  console.log('\nJSON Output (copy this to favorites-data.json):\n');
  console.log(JSON.stringify(data, null, 2));
  
  // Also copy to clipboard if possible
  if (navigator.clipboard) {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2))
      .then(() => console.log('\n✓ JSON copied to clipboard!'))
      .catch(() => console.log('\n✗ Could not copy to clipboard'));
  }
  
  return data;
})();
