// Threads Post Scraper
// Run this in the browser console while on threads.com

function scrapeThreadsPosts() {
    const posts = [];
    
    // Common selectors that Threads might use (these may need adjustment)
    const postSelectors = [
        '[data-pressable-container="true"]', // Common for Meta apps
        'article',
        '[role="article"]',
        'div[style*="flex-direction"]', // Threads often uses flex layouts
    ];
    
    // Try different selectors to find posts
    let postElements = [];
    for (const selector of postSelectors) {
        postElements = document.querySelectorAll(selector);
        if (postElements.length > 0) {
            console.log(`Found ${postElements.length} elements with selector: ${selector}`);
            break;
        }
    }
    
    if (postElements.length === 0) {
        console.log('No posts found. The page structure might have changed.');
        return [];
    }
    
    postElements.forEach((element, index) => {
        try {
            // Find the actual post text, avoiding usernames and UI elements
            const spans = element.querySelectorAll('span');
            let postText = '';
            let longestText = '';
            
            spans.forEach(span => {
                const text = span.textContent.trim();
                // Find the longest meaningful text that's not a username/UI element
                if (text.length > longestText.length && 
                    text.length > 15 && 
                    !span.closest('a') &&  // Not inside a link (usernames are links)
                    !text.match(/^[@\d.,KMk\s]+$/) && // Not just numbers/symbols
                    !text.includes('Follow') &&
                    !text.includes('Like') &&
                    !text.includes('Reply') &&
                    !text.includes('Repost') &&
                    !text.includes('Share') &&
                    !text.includes('More') &&
                    !text.includes(' ago') &&
                    !text.includes('Verified') &&
                    !span.closest('svg') &&
                    !span.querySelector('svg')) {
                    longestText = text;
                }
            });
            
            postText = longestText;
            
            // Try to find timestamp
            const timeElement = element.querySelector('time[datetime]');
            let timestamp = '';
            let postDate = '';
            
            if (timeElement) {
                timestamp = timeElement.getAttribute('datetime');
                console.log('Found datetime attribute:', timestamp);
                
                // If no datetime attribute, try title or text content
                if (!timestamp) {
                    timestamp = timeElement.getAttribute('title') || 
                               timeElement.textContent.trim();
                    console.log('Using fallback timestamp:', timestamp);
                }
            } else {
                console.log('No time element found in post');
            }
            
            // Use the timestamp directly if it's already in ISO format
            if (timestamp) {
                if (timestamp.includes('T') && timestamp.includes('Z')) {
                    // Already in ISO format
                    postDate = timestamp;
                } else {
                    // Try to parse other formats
                    try {
                        const date = new Date(timestamp);
                        if (!isNaN(date.getTime())) {
                            postDate = date.toISOString();
                        } else {
                            postDate = timestamp; // Keep original if can't parse
                        }
                    } catch (e) {
                        postDate = timestamp;
                    }
                }
            }
            
            // Only add posts that have actual text content
            if (postText && postText.length > 15) {
                posts.push({
                    index: index + 1,
                    text: postText,
                    timestamp: postDate || 'Unknown',
                    rawTimestamp: timestamp
                });
            }
        } catch (error) {
            console.log(`Error processing post ${index}:`, error);
        }
    });
    
    return posts;
}

// Enhanced scraper based on Threads HTML structure
function advancedScrape() {
    console.log('Starting Threads post scraping...');
    
    const posts = [];
    const processedTexts = new Set();
    
    // Method 1: Look for time elements first, then find related post content
    const timeElements = document.querySelectorAll('time[datetime]');
    console.log(`Found ${timeElements.length} time elements`);
    
    timeElements.forEach((timeEl, index) => {
        try {
            const datetime = timeEl.getAttribute('datetime');
            console.log('Advanced scraper found datetime:', datetime);
            const postContainer = timeEl.closest('[data-pressable-container="true"]');
            
            if (postContainer) {
                // Look for post text - exclude usernames and UI elements
                const textSpans = postContainer.querySelectorAll('span');
                let postText = '';
                
                // Find the longest text span that's not a username/link
                let longestText = '';
                textSpans.forEach(span => {
                    const text = span.textContent.trim();
                    // Skip if it's a username (usually contains @ or is short)
                    // Skip if it's inside a link
                    // Skip if it contains numbers only (like like counts)
                    if (text.length > longestText.length && 
                        text.length > 15 && 
                        !span.closest('a') && 
                        !text.match(/^[@\d.,KMk\s]+$/) &&
                        !text.includes('Follow') &&
                        !text.includes('Like') &&
                        !text.includes('Reply') &&
                        !text.includes('Repost') &&
                        !text.includes('Share') &&
                        !text.includes('More') &&
                        !text.includes('ago') &&
                        !span.closest('svg')) {
                        longestText = text;
                    }
                });
                
                if (longestText && !processedTexts.has(longestText)) {
                    processedTexts.add(longestText);
                    posts.push({
                        index: posts.length + 1,
                        text: longestText,
                        timestamp: datetime,
                        rawTimestamp: timeEl.getAttribute('title') || timeEl.textContent.trim()
                    });
                }
            }
        } catch (error) {
            console.log(`Error processing time element ${index}:`, error);
        }
    });
    
    // Method 2: Look for specific post content patterns if Method 1 fails
    if (posts.length === 0) {
        console.log('Method 1 failed, trying pattern-based approach...');
        
        // Look for containers that have pressable-container attribute
        const postContainers = document.querySelectorAll('[data-pressable-container="true"]');
        
        postContainers.forEach((container, index) => {
            try {
                // Find the main text content (usually the longest span without links)
                const spans = container.querySelectorAll('span');
                let mainText = '';
                
                spans.forEach(span => {
                    const text = span.textContent.trim();
                    if (text.length > mainText.length && 
                        text.length > 20 && 
                        !span.closest('a') && 
                        !text.match(/^[@\d.,KMk\s]+$/) &&
                        !text.includes('ago') &&
                        !span.querySelector('svg')) {
                        mainText = text;
                    }
                });
                
                // Find timestamp
                const timeEl = container.querySelector('time[datetime]');
                let timestamp = 'Unknown';
                if (timeEl) {
                    timestamp = timeEl.getAttribute('datetime');
                    console.log('Method 2 found datetime:', timestamp);
                }
                
                if (mainText && !processedTexts.has(mainText)) {
                    processedTexts.add(mainText);
                    posts.push({
                        index: posts.length + 1,
                        text: mainText,
                        timestamp: timestamp,
                        rawTimestamp: timeEl ? (timeEl.getAttribute('title') || timeEl.textContent.trim()) : 'Unknown'
                    });
                }
            } catch (error) {
                console.log(`Error processing container ${index}:`, error);
            }
        });
    }
    
    return posts;
}

// Global variables for controlling the scraper
let isScrapingActive = false;
let scrollTimer = null;
let startTime = null;

// Auto-scroll function to load more posts (interruptible)
function startAutoScroll() {
    const scrollInterval = 2000; // Scroll every 2 seconds
    startTime = Date.now();
    
    console.log('🔄 Starting auto-scroll...');
    
    scrollTimer = setInterval(() => {
        if (!isScrapingActive) {
            clearInterval(scrollTimer);
            return;
        }
        
        const elapsed = Date.now() - startTime;
        const elapsedSeconds = Math.floor(elapsed / 1000);
        
        // Scroll to bottom
        window.scrollTo(0, document.body.scrollHeight);
        
        // Show progress every 10 seconds
        if (elapsedSeconds % 10 === 0 && elapsedSeconds > 0) {
            const minutes = Math.floor(elapsedSeconds / 60);
            const seconds = elapsedSeconds % 60;
            console.log(`⏱️ Auto-scrolling... ${minutes}:${seconds.toString().padStart(2, '0')} elapsed`);
        }
    }, scrollInterval);
}

// Stop auto-scroll
function stopAutoScroll() {
    if (scrollTimer) {
        clearInterval(scrollTimer);
        scrollTimer = null;
    }
}

// Download function to save JSON as file
function downloadJSON(data, filename = 'threads_posts.json') {
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log(`📥 Downloaded: ${filename}`);
}

// Start scraping process
function startScraping() {
    isScrapingActive = true;
    console.log('🧵 Threads Post Scraper Starting...');
    startAutoScroll();
    updateButton();
}

// Stop scraping and download data
function stopScraping() {
    isScrapingActive = false;
    stopAutoScroll();
    
    console.log('🛑 Stopping scraper and extracting posts...');
    console.log('⏳ Waiting for final content to load...');
    
    // Wait a moment for final content to load, then scrape
    setTimeout(() => {
        console.log('🔍 Starting post extraction...');
        let scrapedPosts = scrapeThreadsPosts();
        
        if (scrapedPosts.length === 0) {
            console.log('First method failed, trying advanced scraping...');
            scrapedPosts = advancedScrape();
        }
        
        // Calculate scraping duration
        const elapsed = startTime ? Date.now() - startTime : 0;
        const elapsedMinutes = Math.floor(elapsed / 60000);
        const elapsedSeconds = Math.floor((elapsed % 60000) / 1000);
        
        // Prepare JSON output
        const jsonOutput = {
            scrapedAt: new Date().toISOString(),
            totalPosts: scrapedPosts.length,
            scrapingDuration: `${elapsedMinutes}:${elapsedSeconds.toString().padStart(2, '0')}`,
            posts: scrapedPosts.map(post => ({
                text: post.text,
                timestamp: post.timestamp,
                rawTimestamp: post.rawTimestamp
            }))
        };
        
        // Save to global variable
        window.scrapedThreadsPosts = jsonOutput;
        
        // Auto-download the JSON file
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
        const timeStr = new Date().toTimeString().slice(0, 5).replace(':', '-');
        const filename = `threads_posts_${timestamp}_${timeStr}.json`;
        downloadJSON(jsonOutput, filename);
        
        console.log('\n✅ Scraping completed successfully!');
        console.log(`📊 Total posts extracted: ${scrapedPosts.length}`);
        console.log(`⏱️ Scraping duration: ${elapsedMinutes}:${elapsedSeconds.toString().padStart(2, '0')}`);
        console.log(`📁 File downloaded: ${filename}`);
        
        updateButton();
    }, 2000);
}

// Create floating button UI
function createScraperButton() {
    // Remove existing button if any
    const existingButton = document.getElementById('threads-scraper-btn');
    if (existingButton) {
        existingButton.remove();
    }
    
    // Create button
    const button = document.createElement('button');
    button.id = 'threads-scraper-btn';
    button.textContent = '▶️ Start Scraping';
    
    // Style the button
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999999;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 14px;
        font-weight: bold;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        min-width: 140px;
        text-align: center;
    `;
    
    // Add hover effects
    button.onmouseover = () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 6px 25px rgba(0, 0, 0, 0.4)';
    };
    
    button.onmouseout = () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    };
    
    // Add click handler
    button.onclick = () => {
        if (!isScrapingActive) {
            startScraping();
        } else {
            stopScraping();
        }
    };
    
    // Add to page
    document.body.appendChild(button);
    
    return button;
}

// Update button text and appearance
function updateButton() {
    const button = document.getElementById('threads-scraper-btn');
    if (button) {
        if (isScrapingActive) {
            button.textContent = '🛑 Stop Scraping';
            button.style.background = 'linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)';
        } else {
            button.textContent = '▶️ Start Scraping';
            button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
    }
}

// Initialize the scraper UI
console.log('🧵 Threads Post Scraper Loaded!');
console.log('👆 Look for the floating button in the bottom-right corner');
console.log('🚀 Click "Start Scraping" to begin auto-scroll and data collection');
console.log('🛑 Click "Stop Scraping" to finish and download your data');

// Create the button
createScraperButton();
