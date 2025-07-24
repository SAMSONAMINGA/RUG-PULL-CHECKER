import requests
from bs4 import BeautifulSoup

# Configuration
SCAM_KEYWORDS = ["1000x", "no dev tax", "stealth launch", "LP burned", "CEX listing soon"]
TWITTER_SEARCH_URL = "https://twitter.com/search?q={query}"
BSC_API_KEY = "YOUR_API_KEY"  # Get free at bscscan.com

def scan_twitter(token_symbol):
    """Search Twitter for scam-related tweets about a token."""
    query = f"${token_symbol} ({' OR '.join(SCAM_KEYWORDS)})"
    url = TWITTER_SEARCH_URL.format(query=requests.utils.quote(query))
    
    try:
        # Mock headers to avoid bot detection
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract tweet texts (Twitter's HTML structure may change - this is a starting point)
        tweets = []
        for tweet in soup.find_all('div', {'data-testid': 'tweetText'}):
            tweet_text = tweet.get_text(separator=' ', strip=True)
            if any(keyword.lower() in tweet_text.lower() for keyword in SCAM_KEYWORDS):
                tweets.append(tweet_text)
        
        return tweets[:5]  # Return top 5 scammy tweets
    
    except Exception as e:
        print(f"\n❌ Twitter scan failed: {str(e)}")
        return []

def check_liquidity(token_address):
    """Check if token has locked liquidity via BscScan API."""
    if not BSC_API_KEY or BSC_API_KEY == "YOUR_API_KEY":
        print("\n⚠️ BscScan API key not configured. Skipping liquidity check.")
        return False
    
    api_url = (
        f"https://api.bscscan.com/api?module=account&action=txlist"
        f"&address={token_address}&apikey={BSC_API_KEY}"
    )
    
    try:
        response = requests.get(api_url, timeout=10).json()
        if response["status"] == "1":
            for tx in response["result"]:
                if "liquidity" in tx.get("input", "").lower():
                    return True
        return False
    
    except Exception as e:
        print(f"\n❌ Liquidity check failed: {str(e)}")
        return False

def analyze_token():
    """Main function to analyze a token."""
    print("\n" + "="*50)
    print("🕵️♂️ Rug Pull Detector - Crypto Scam Analysis")
    print("="*50)
    
    # User input
    token_symbol = input("\nEnter token symbol (e.g., PEPE): ").strip().upper()
    token_address = input("Enter token contract address (or press Enter to skip): ").strip()
    
    print(f"\n🔍 Analyzing ${token_symbol}...")
    
    # Twitter scan
    print("\n[1/2] Scanning Twitter for scam signals...")
    scam_tweets = scan_twitter(token_symbol)
    
    if scam_tweets:
        print("\n🚨 RED FLAGS FOUND:")
        for i, tweet in enumerate(scam_tweets, 1):
            print(f"{i}. {tweet}")
    else:
        print("\n✅ No obvious scam signals found on Twitter.")
    
    # Liquidity check
    if token_address:
        print("\n[2/2] Checking token liquidity...")
        if check_liquidity(token_address):
            print("\n🔒 Liquidity appears locked (good sign).")
        else:
            print("\n⚠️ WARNING: Liquidity NOT locked or couldn't verify!")

if __name__ == "__main__":
    analyze_token()
    print("\nAnalysis complete. Always DYOR (Do Your Own Research)!")