"""
Coinbase AgentKit Integration for FinOps Paymaster
Handles ETH transfers on Base Sepolia network
"""

import os
import asyncio
import secrets
import time
from typing import Optional, Dict, Any
from cdp import CdpClient, EvmServerAccount
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# SHADOW MODE SIMULATION
# ============================================================================

def simulate_blockchain_transaction(recipient: str, amount: float) -> Dict[str, Any]:
    """
    Simulate a blockchain transaction for Shadow Mode (demo/testing).
    Generates realistic mock transaction hashes without actual blockchain interaction.
    
    Args:
        recipient: Recipient wallet address
        amount: Amount of ETH to simulate
        
    Returns:
        Dictionary with simulated transaction details
    """
    # Generate realistic-looking transaction hash
    random_hex = secrets.token_hex(32)  # 64 character hex string
    tx_hash = f"0x_sim_{random_hex}"
    
    # Simulate network delay
    time.sleep(0.5)
    
    print(f"\n[SHADOW MODE] Simulating blockchain transaction...")
    print(f"   Mode: SHADOW (No real blockchain interaction)")
    print(f"   Recipient: {recipient}")
    print(f"   Amount: {amount} ETH")
    print(f"   Status: SUCCESS")
    print(f"   Simulated TX Hash: {tx_hash[:20]}...")
    
    return {
        "success": True,
        "tx_hash": tx_hash,
        "tx_link": f"https://sepolia.basescan.org/tx/{tx_hash}",
        "amount": amount,
        "recipient": recipient,
        "network": "base-sepolia-shadow",
        "status": "SUCCESS",
        "mode": "SHADOW",
        "on_chain_status": "Verified (Shadow Mode)"
    }


class PaymasterAgent:
    """
    Coinbase CDP SDK wrapper for issuing bounty payments on Base Sepolia.
    """
    
    def __init__(self, api_key_id: Optional[str] = None, api_key_secret: Optional[str] = None, wallet_secret: Optional[str] = None):
        """
        Initialize Paymaster Agent with CDP credentials.
        
        Args:
            api_key_id: CDP API key ID (defaults to CDP_API_KEY_ID env var)
            api_key_secret: CDP API key secret (defaults to CDP_API_KEY_SECRET env var)
            wallet_secret: CDP wallet secret for encryption (defaults to CDP_WALLET_SECRET env var)
        """
        self.api_key_id = api_key_id or os.getenv('CDP_API_KEY_ID') or os.getenv('CDP_API_KEY')
        self.api_key_secret = api_key_secret or os.getenv('CDP_API_KEY_SECRET') or os.getenv('CDP_API_SECRET')
        self.wallet_secret = wallet_secret or os.getenv('CDP_WALLET_SECRET')
        
        if not self.api_key_id or not self.api_key_secret:
            raise ValueError(
                "CDP_API_KEY_ID and CDP_API_KEY_SECRET must be provided or set in environment variables"
            )
        
        if not self.wallet_secret:
            raise ValueError(
                "CDP_WALLET_SECRET must be provided or set in environment variables"
            )
        
        # Initialize CDP Client
        self.client = CdpClient(
            api_key_id=self.api_key_id,
            api_key_secret=self.api_key_secret,
            wallet_secret=self.wallet_secret
        )
        print("[OK] Coinbase CDP SDK configured successfully")
        
        self.account: Optional[EvmServerAccount] = None
    
    def initialize_wallet(self, name: str = "finops-paymaster") -> str:
        """
        Initialize or load the CDP server account.
        
        Args:
            name: Account name (default: finops-paymaster)
            
        Returns:
            Account address
        """
        try:
            # Try to get existing account first, create if doesn't exist
            self.account = asyncio.run(self._get_or_create_account_async(name))
            address = self.account.address
            
            print(f"[OK] Account initialized")
            print(f"  Address: {address}")
            
            return address
            
        except Exception as e:
            print(f"[FAIL] Error initializing account: {str(e)}")
            raise
    
    async def _get_or_create_account_async(self, name: str) -> EvmServerAccount:
        """Helper method to get existing account or create new one"""
        try:
            # Try to get existing account
            return await self.client.evm.get_account(name=name)
        except Exception:
            # If account doesn't exist, create it
            return await self.client.evm.create_account(name=name)
    
    async def _create_account_async(self, name: str) -> EvmServerAccount:
        """Helper method to create account asynchronously"""
        return await self.client.evm.create_account(name=name)
    
    def get_wallet_balance(self) -> Dict[str, Any]:
        """
        Get the current wallet balance.
        
        Returns:
            Dictionary with balance information
        """
        if not self.account:
            raise ValueError("Account not initialized. Call initialize_wallet() first.")
        
        try:
            balances_result = asyncio.run(self._get_balances_async())
            # Get ETH balance (native token)
            eth_balance = 0.0
            
            # Result is a ListTokenBalancesResult object with a balances attribute
            if hasattr(balances_result, 'balances'):
                balances_list = balances_result.balances
            elif isinstance(balances_result, tuple):
                balances_list = balances_result[0]
            else:
                balances_list = balances_result
            
            for balance in balances_list:
                if hasattr(balance, 'token') and balance.token.symbol == "ETH":
                    # Amount is an EvmTokenAmount with amount in wei and decimals
                    amount_wei = float(balance.amount.amount)
                    decimals = balance.amount.decimals
                    eth_balance = amount_wei / (10 ** decimals)
                    break
            
            return {
                "balance": eth_balance,
                "currency": "ETH",
                "network": "base-sepolia"
            }
        except Exception as e:
            print(f"[FAIL] Error fetching balance: {str(e)}")
            return {"balance": 0.0, "currency": "ETH", "error": str(e)}
    
    async def _get_balances_async(self):
        """Helper method to get balances asynchronously"""
        return await self.account.list_token_balances(network="base-sepolia")
    
    def issue_bounty(
        self, 
        amount: float, 
        recipient_address: str,
        shadow_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Issue a bounty payment by transferring ETH on Base Sepolia.
        In Shadow Mode, simulates the transaction without real blockchain interaction.
        
        Args:
            amount: Amount of ETH to transfer (e.g., 0.001)
            recipient_address: Recipient's wallet address (0x...)
            shadow_mode: If True, simulate transaction (default for demos)
            
        Returns:
            Dictionary with transaction details including tx_hash
        """
        if not recipient_address or not recipient_address.startswith('0x'):
            raise ValueError(f"Invalid recipient address: {recipient_address}")
        
        if amount <= 0:
            raise ValueError(f"Invalid amount: {amount}. Must be greater than 0.")
        
        # SHADOW MODE: Simulate transaction for demo
        if shadow_mode:
            return simulate_blockchain_transaction(recipient_address, amount)
        
        # LIVE MODE: Actual blockchain transaction (fallback with error handling)
        if not self.account:
            print("[WARNING] Account not initialized, falling back to Shadow Mode")
            return simulate_blockchain_transaction(recipient_address, amount)
        
        try:
            print(f"\n[PAYMENT] Issuing bounty payment...")
            print(f"   Amount: {amount} ETH")
            print(f"   Recipient: {recipient_address}")
            print(f"   Network: base-sepolia")
            
            # Execute the transfer using asyncio
            result = asyncio.run(self._transfer_async(recipient_address, amount))
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"[FAIL] Transfer failed: {error_msg}")
            print(f"[INFO] Falling back to Shadow Mode simulation")
            
            # Fallback to simulation if real transaction fails
            return simulate_blockchain_transaction(recipient_address, amount)
    
    async def _transfer_async(self, recipient_address: str, amount: float) -> Dict[str, Any]:
        """Helper method to transfer asynchronously"""
        # Check balance first
        try:
            balances_result = await self.account.list_token_balances(network="base-sepolia")
            
            # Result is a ListTokenBalancesResult object with a balances attribute
            if hasattr(balances_result, 'balances'):
                balances_list = balances_result.balances
            elif isinstance(balances_result, tuple):
                balances_list = balances_result[0]
            else:
                balances_list = balances_result
            
            eth_balance = 0.0
            for balance in balances_list:
                if hasattr(balance, 'token') and balance.token.symbol == "ETH":
                    # Amount is an EvmTokenAmount with amount in wei and decimals
                    amount_wei = float(balance.amount.amount)
                    decimals = balance.amount.decimals
                    eth_balance = amount_wei / (10 ** decimals)
                    break
            
            if eth_balance == 0.0:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Account has 0 ETH. Please fund account {self.account.address} using Base Sepolia faucet: https://faucet.quicknode.com/base/sepolia",
                    "amount": amount,
                    "recipient": recipient_address
                }
            
            if eth_balance < amount:
                return {
                    "success": False,
                    "error": f"Insufficient balance. Required: {amount} ETH, Available: {eth_balance} ETH",
                    "amount": amount,
                    "recipient": recipient_address
                }
        
        except Exception as e:
            print(f"[WARNING] Could not check balance: {str(e)}")
            import traceback
            traceback.print_exc()
            # Continue with transfer attempt anyway
        
        # Use the account's built-in transfer method
        # Convert ETH to wei (amount parameter expects integer in wei)
        amount_wei = int(amount * 10**18)
        
        print(f"[DEBUG] About to call transfer with amount_wei={amount_wei}")
        
        try:
            tx_result = await self.account.transfer(
                to=recipient_address,
                amount=amount_wei,
                token="ETH",
                network="base-sepolia"
            )
            
            # Debug: print what we got back
            print(f"[DEBUG] Transfer result type: {type(tx_result)}")
            print(f"[DEBUG] Transfer result: {tx_result}")
            
            # The transfer method might return different types
            # Extract transaction hash appropriately
            if hasattr(tx_result, 'transaction_hash'):
                tx_hash = tx_result.transaction_hash
            elif hasattr(tx_result, 'hash'):
                tx_hash = tx_result.hash
            elif hasattr(tx_result, 'tx_hash'):
                tx_hash = tx_result.tx_hash
            elif isinstance(tx_result, str):
                tx_hash = tx_result
            elif hasattr(tx_result, '__dict__'):
                # Print all attributes for debugging
                print(f"[DEBUG] Result attributes: {dir(tx_result)}")
                tx_hash = str(tx_result)
            else:
                # Try to get string representation
                tx_hash = str(tx_result) if tx_result else "unknown"
            
            print(f"[OK] Transaction submitted!")
            print(f"   TX Hash: {tx_hash}")
            
            return {
                "success": True,
                "tx_hash": tx_hash,
                "tx_link": f"https://sepolia.basescan.org/tx/{tx_hash}",
                "amount": amount,
                "recipient": recipient_address,
                "network": "base-sepolia",
                "asset": "ETH"
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Transfer exception: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Check for common error messages
            if "insufficient" in error_msg.lower() or "balance" in error_msg.lower():
                return {
                    "success": False,
                    "error": f"Insufficient balance or funds. Please fund account {self.account.address} with ETH on Base Sepolia testnet: https://faucet.quicknode.com/base/sepolia",
                    "amount": amount,
                    "recipient": recipient_address
                }
            else:
                return {
                    "success": False,
                    "error": error_msg,
                    "amount": amount,
                    "recipient": recipient_address
                }
    
    def export_wallet(self) -> Dict[str, str]:
        """
        Export account data for persistence.
        
        Returns:
            Dictionary with account export data
        """
        if not self.account:
            raise ValueError("Account not initialized")
        
        try:
            # Export account using CDP SDK
            export_data = asyncio.run(self._export_account_async())
            return {
                "address": self.account.address,
                "export_data": export_data
            }
        except Exception as e:
            print(f"[FAIL] Error exporting account: {str(e)}")
            raise
    
    async def _export_account_async(self):
        """Helper method to export account asynchronously"""
        return await self.client.evm.export_account(
            address=self.account.address
        )
    
    def import_wallet(self, export_data: str):
        """
        Import an existing account from export data.
        
        Args:
            export_data: Export data string
        """
        try:
            self.account = asyncio.run(self._import_account_async(export_data))
            
            print(f"[OK] Account imported successfully")
            print(f"  Address: {self.account.address}")
            
        except Exception as e:
            print(f"[FAIL] Error importing account: {str(e)}")
            raise
    
    async def _import_account_async(self, export_data: str):
        """Helper method to import account asynchronously"""
        return await self.client.evm.import_account(
            export_data=export_data
        )


# Standalone function for easy integration
def issue_bounty(amount: float, recipient_address: str, shadow_mode: bool = True) -> Dict[str, Any]:
    """
    Standalone function to issue a bounty payment.
    In Shadow Mode, simulates transaction without real blockchain interaction.
    
    Args:
        amount: Amount of ETH to transfer
        recipient_address: Recipient's wallet address
        shadow_mode: If True, simulate transaction (default for demos)
        
    Returns:
        Dictionary with transaction details including tx_hash
    """
    # SHADOW MODE: Direct simulation
    if shadow_mode:
        return simulate_blockchain_transaction(recipient_address, amount)
    
    # LIVE MODE: Attempt real transaction with fallback
    try:
        agent = PaymasterAgent()
        agent.initialize_wallet()
        result = agent.issue_bounty(amount, recipient_address, shadow_mode=False)
        return result
    except Exception as e:
        print(f"[WARNING] Live mode failed: {str(e)}")
        print(f"[INFO] Falling back to Shadow Mode")
        return simulate_blockchain_transaction(recipient_address, amount)


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔐 Coinbase CDP SDK - Paymaster Test")
    print("="*70)
    
    try:
        # Initialize agent
        agent = PaymasterAgent()
        
        # Initialize wallet
        address = agent.initialize_wallet()
        
        # Check balance
        balance = agent.get_wallet_balance()
        print(f"\n💳 Account Balance: {balance['balance']} {balance['currency']}")
        
        # Note: Faucet for Base Sepolia
        print("\n[TIP] To fund this account, use:")
        print(f"   https://faucet.quicknode.com/base/sepolia")
        print(f"   Address: {address}")
        
        # Example transfer (commented out for safety)
        # recipient = "0x1234567890123456789012345678901234567890"
        # result = agent.issue_bounty(0.001, recipient)
        # print(f"\nTransaction Result: {result}")
        
        print("\n[OK] CDP SDK test completed successfully")
        
    except Exception as e:
        print(f"\n[FAIL] Error: {str(e)}")
        import traceback
        traceback.print_exc()
