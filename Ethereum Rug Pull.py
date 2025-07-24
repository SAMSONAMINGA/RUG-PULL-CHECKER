from flask import Flask, render_template, request
import requests
from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
app = Flask(__name__)

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{os.getenv('INFURA_KEY')}"))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        token_address = request.form['token_address']
        results = analyze_token(token_address)
        return render_template('results.html', 
                            token=token_address,
                            results=results)
    return render_template('index.html')

def analyze_token(token_address):
    """Core analysis function"""
    warnings = []
    
    # 1. Contract Verification Check
    verify_url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={token_address}&apikey={os.getenv('ETHERSCAN_KEY')}"
    if requests.get(verify_url).json().get("result") == "Contract source code not verified":
        warnings.append(("danger", "Unverified Contract", "Source code not publicly audited"))
    
    # 2. Proxy Pattern Detection
    bytecode = w3.eth.get_code(token_address).hex()
    if "363d3d373d3d3d363d73" in bytecode:
        warnings.append(("warning", "Proxy Pattern", "Contract may be upgradeable (potential backdoor)"))
    
    # 3. Liquidity Lock Check
    tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={token_address}&apikey={os.getenv('ETHERSCAN_KEY')}"
    txs = requests.get(tx_url).json().get("result", [])[:250]
    
    lp_indicators = {
        "Uniswap": "0xf305d719",
        "Sushiswap": "0xe8e33700", 
        "Lock Event": "lockLiquidity"
    }
    found_locks = set()
    
    for tx in txs:
        for dex, sig in lp_indicators.items():
            if sig.lower() in tx['input'].lower():
                found_locks.add(dex)
    
    if not found_locks:
        warnings.append(("danger", "No LP Lock", "No DEX liquidity locks detected"))
    else:
        warnings.append(("success", f"LP Locked ({', '.join(found_locks)})", "Liquidity appears secured"))
    
    return warnings

if __name__ == '__main__':
    app.run(debug=True)