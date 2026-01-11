"""
Setup Agent Wallet
===================
Initializes a Coinbase CDP wallet for the FinOps agent using AgentKit.
Handles wallet creation, faucet funding, and persistence.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

# Import Coinbase SDK
try:
    from cdp import Wallet, Cdp
except ImportError:
    console.print("[red][ERROR] Error: Coinbase SDK not installed[/red]")
    console.print("Install with: pip install cdp-sdk")
    exit(1)


def setup_agent_wallet():
    """Initialize and configure the agent's CDP wallet on Base Sepolia."""
    
    console.print(Panel.fit(
        "🤖 [bold cyan]FinOps Agent Wallet Setup[/bold cyan]\n"
        "Initializing Coinbase Developer Platform wallet on Base Sepolia",
        border_style="cyan"
    ))
    
    # Validate environment variables
    if not os.getenv('CDP_API_KEY') or not os.getenv('CDP_API_SECRET'):
        console.print(Panel(
            "[red][ERROR] Missing CDP API credentials[/red]\n\n"
            "Please set CDP_API_KEY and CDP_API_SECRET in your .env file.\n\n"
            "[bold]How to get credentials:[/bold]\n"
            "1. Go to https://portal.cdp.coinbase.com/\n"
            "2. Create a new API key\n"
            "3. Download the credentials JSON file\n"
            "4. Copy the 'name' field to CDP_API_KEY\n"
            "5. Copy the entire 'privateKey' field to CDP_API_SECRET\n"
            "   (including -----BEGIN EC PRIVATE KEY----- header)",
            border_style="red",
            title="[WARNING]️  Configuration Error"
        ))
        return
    
    # Step 1: Configure CDP SDK
    console.print("\n[bold][1] Configuring CDP SDK...[/bold]")
    
    try:
        # Parse private key - replace literal \n with actual newlines
        private_key = os.getenv('CDP_API_SECRET').replace('\\n', '\n')
        
        Cdp.configure(
            api_key_name=os.getenv('CDP_API_KEY'),
            private_key=private_key
        )
        console.print("   [SUCCESS] CDP SDK configured successfully")
    except Exception as e:
        console.print(f"[red][ERROR] Failed to configure CDP: {e}[/red]")
        console.print("\n[yellow]Tip: Make sure your CDP_API_SECRET includes the full PEM format:[/yellow]")
        console.print("[dim]-----BEGIN EC PRIVATE KEY-----[/dim]")
        console.print("[dim]...base64 encoded key...[/dim]")
        console.print("[dim]-----END EC PRIVATE KEY-----[/dim]")
        return
    
    # Step 2: Check for existing wallet data
    console.print("\n[bold][2] Checking for existing wallet...[/bold]")
    wallet_file = Path('wallet_data.json')
    
    if wallet_file.exists():
        console.print("   📂 Found existing wallet_data.json")
        try:
            with open(wallet_file, 'r') as f:
                wallet_data = json.load(f)
            
            wallet = Wallet.import_data(wallet_data)
            console.print("   [SUCCESS] Wallet imported successfully")
        except Exception as e:
            console.print(f"[red][ERROR] Failed to import wallet: {e}[/red]")
            console.print("   Creating new wallet instead...")
            wallet = Wallet.create(network_id='base-sepolia')
            console.print("   [SUCCESS] New wallet created")
    else:
        console.print("   🆕 No existing wallet found, creating new one...")
        wallet = Wallet.create(network_id='base-sepolia')
        console.print("   [SUCCESS] Wallet created successfully")
    
    # Step 3: Display wallet address
    console.print("\n[bold][3] Wallet Information[/bold]")
    wallet_address = wallet.default_address.address_id
    console.print(f"   📍 [bold cyan]Address:[/bold cyan] {wallet_address}")
    
    # Step 4: Check balance and request faucet if needed
    console.print("\n[bold][4] Checking Balance...[/bold]")
    
    try:
        balance = wallet.balance('eth')
        console.print(f"   [PAYMENT] Current Balance: [yellow]{balance} ETH[/yellow]")
        
        if float(balance) == 0:
            console.print("\n   💧 [bold]Balance is 0 - Requesting faucet funds...[/bold]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                progress.add_task(
                    description="Fetching funds from Base Sepolia Faucet...",
                    total=None
                )
                
                try:
                    faucet_tx = wallet.faucet()
                    console.print(f"   [SUCCESS] Faucet request successful!")
                    console.print(f"   🔗 Transaction: {faucet_tx.transaction_hash}")
                except Exception as e:
                    console.print(f"[yellow][WARNING]️  Faucet request issue: {e}[/yellow]")
        else:
            console.print("   [SUCCESS] Wallet already funded")
            
    except Exception as e:
        console.print(f"[yellow][WARNING]️  Could not check balance: {e}[/yellow]")
    
    # Step 5: Export wallet data
    console.print("\n[bold][5] Saving Wallet Data...[/bold]")
    
    try:
        wallet_data = wallet.export_data()
        
        # Convert WalletData object to dict if needed
        if hasattr(wallet_data, 'to_dict'):
            wallet_dict = wallet_data.to_dict()
        elif hasattr(wallet_data, '__dict__'):
            wallet_dict = wallet_data.__dict__
        else:
            wallet_dict = wallet_data
        
        with open('wallet_data.json', 'w') as f:
            json.dump(wallet_dict, f, indent=2)
        
        console.print("   [SUCCESS] Wallet data saved to wallet_data.json")
        
        # Critical warning
        console.print(Panel(
            "[bold red][WARNING]️  CRITICAL WARNING [WARNING]️[/bold red]\n\n"
            "[yellow]DO NOT DELETE wallet_data.json[/yellow]\n"
            "[yellow]OR YOU WILL LOSE ACCESS TO YOUR AGENT WALLET[/yellow]\n\n"
            "This file contains the private keys for your agent's wallet.\n"
            "Back it up securely and never commit it to version control.",
            border_style="red",
            title="[WARNING]️  Security Alert",
            title_align="center"
        ))
        
    except Exception as e:
        console.print(f"[red][ERROR] Failed to export wallet: {e}[/red]")
        return
    
    # Step 6: Verify final balance after waiting for faucet transaction
    console.print("\n[bold]6️⃣ Verifying Final Balance...[/bold]")
    console.print("   ⏳ Waiting 10 seconds for faucet transaction to clear...")
    
    for i in range(10, 0, -1):
        console.print(f"   ⏰ {i} seconds remaining...", end='\r')
        time.sleep(1)
    
    console.print("   ⏰ 0 seconds remaining...   ")
    
    try:
        final_balance = wallet.balance('eth')
        console.print(f"\n   [PAYMENT] [bold green]Final Balance: {final_balance} ETH[/bold green]")
        
        # Basescan link
        basescan_url = f"https://sepolia.basescan.org/address/{wallet_address}"
        console.print(f"   [SEARCH] [bold cyan]View on Basescan:[/bold cyan] {basescan_url}")
        
    except Exception as e:
        console.print(f"[yellow][WARNING]️  Could not verify final balance: {e}[/yellow]")
    
    # Success summary
    console.print(Panel.fit(
        f"[bold green][SUCCESS] Agent Wallet Setup Complete![/bold green]\n\n"
        f"Address: {wallet_address}\n"
        f"Network: Base Sepolia\n"
        f"Balance: {final_balance} ETH\n\n"
        f"Your agent is ready to execute on-chain transactions!",
        border_style="green",
        title="🎉 Success"
    ))


if __name__ == "__main__":
    setup_agent_wallet()
