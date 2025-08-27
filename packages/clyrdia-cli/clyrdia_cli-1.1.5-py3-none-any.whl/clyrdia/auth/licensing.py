"""
Licensing management for Clyrdia CLI - handles authentication and credit system.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from ..models.user import UserStatus, CreditEstimate
from ..models.results import TestCase
from ..caching.manager import CacheManager
from ..core.console import console

class LicensingManager:
    """Manages SaaS licensing and credit system"""
    
    def __init__(self):
        from ..config import config
        self.config = config
        self.config_dir = Path.home() / ".clyrdia"
        self.config_file = self.config_dir / "config.json"
        self.api_key = self._load_api_key()
    
    def _load_api_key(self) -> Optional[str]:
        """Load API key from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key')
            except (json.JSONDecodeError, KeyError):
                pass
        return None
    
    def is_first_run(self) -> bool:
        """Check if this is the user's first run"""
        return not self.config_file.exists()
    
    def _save_api_key(self, api_key: str):
        """Save API key to config file with secure permissions"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {'api_key': api_key}
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure file permissions (600)
        os.chmod(self.config_file, 0o600)
    
    async def _make_api_request(self, endpoint: str, method: str = "GET", 
                         data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Clyrdia backend"""
        if not self.api_key:
            raise Exception("No API key configured. Please run 'clyrdia-cli login' first.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = self.config.get_api_url(endpoint)
        
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API key. Please run 'clyrdia-cli login' again.")
            elif e.response.status_code == 402:
                return e.response.json()  # Return payment required response
            else:
                raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    async def login(self, api_key: str) -> UserStatus:
        """Login with API key and validate subscription"""
        # Test the API key by calling the status endpoint
        self._save_api_key(api_key)
        self.api_key = api_key
        
        try:
            status = await self.get_status()
            return status
        except Exception as e:
            # Remove invalid key
            self._remove_api_key()
            raise e
    
    async def get_status(self) -> UserStatus:
        """Get current user status and credit balance"""
        response = await self._make_api_request("/cli-status")
        
        return UserStatus(
            user_name=response["user_name"],
            plan=response["plan"],
            credits_remaining=response["credits_remaining"],
            resets_on=response["resets_on"],
            api_key=self.api_key
        )
    
    async def debit_credits(self, credits_to_debit: int, run_id: str) -> Dict[str, Any]:
        """Debit credits for a benchmark run"""
        data = {
            "credits_to_debit": credits_to_debit,
            "run_id": run_id
        }
        
        response = await self._make_api_request("/cli-usage-debit", method="POST", data=data)
        return response
    
    def _remove_api_key(self):
        """Remove API key from config"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.api_key = None
    
    def logout(self):
        """Logout and remove API key"""
        self._remove_api_key()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.api_key is not None
    
    async def estimate_credits(self, test_cases: List[TestCase], models: List[str], 
                        use_cache: bool = False) -> CreditEstimate:
        """Estimate credit cost for a benchmark run"""
        cache_manager = CacheManager()
        total_credits = 0
        test_breakdown = {}
        
        for test_case in test_cases:
            for model in models:
                test_key = f"{test_case.name}_{model}"
                
                if use_cache and cache_manager.get_cached_result(
                    model, test_case.name, test_case.prompt, 
                    test_case.max_tokens, test_case.temperature
                ):
                    test_breakdown[test_key] = 0  # Cache hit = 0 credits
                else:
                    # Estimate credits based on test case
                    estimated_tokens = len(test_case.prompt.split()) * 1.3  # Rough estimate
                    estimated_credits = max(1, int(estimated_tokens / 1000))  # 1 credit per 1K tokens
                    total_credits += estimated_credits
                    test_breakdown[test_key] = estimated_credits
        
        # Get current balance if authenticated
        current_balance = 0
        if self.is_authenticated():
            try:
                status = await self.get_status()
                current_balance = status.credits_remaining
            except:
                pass
        
        cache_hits = sum(1 for cost in test_breakdown.values() if cost == 0)
        live_api_calls = len(test_breakdown) - cache_hits
        
        return CreditEstimate(
            total_tests=len(test_breakdown),
            cache_hits=cache_hits,
            live_api_calls=live_api_calls,
            estimated_credits=total_credits,
            current_balance=current_balance,
            test_breakdown=test_breakdown
        )
    
    def display_credit_summary(self, before_credits: int, after_credits: int):
        """Display credit usage summary"""
        used = before_credits - after_credits
        console.print(f"[bold]💸 Credits Used: {used}[/bold]")
        console.print(f"[bold] Remaining: {after_credits} credits[/bold]")
    
    def get_credit_usage(self, run_id: str) -> Dict[str, Any]:
        """Get credit usage for a specific run"""
        try:
            response = self._make_api_request(f"/api/v1/usage/{run_id}")
            return response
        except Exception as e:
            return {"error": str(e), "run_id": run_id}
    
    def show_credit_balance(self):
        """Display current credit balance"""
        try:
            status = asyncio.run(self.get_status())
            console.print(f"[bold]💰 Current Balance: {status.credits_remaining} credits[/bold]")
            console.print(f"[dim]Plan: {status.plan.upper()}[/dim]")
            console.print(f"[dim]Resets on: {status.resets_on}[/dim]")
            
            # Show upgrade message if credits are low
            if status.credits_remaining <= 50:
                if status.plan == "free":
                    console.print(f"\n[yellow]⚠️  Low credits![/yellow]")
                    console.print(f"• You have {status.credits_remaining} credits remaining")
                    console.print(f"• Free plan includes 250 credits/month")
                    console.print(f"• Upgrade to Pro for 10,000 credits/month")
                    console.print(f"• Visit [bold]https://clyrdia.com[/bold] to upgrade")
                else:
                    console.print(f"\n[yellow]⚠️  Low credits![/yellow]")
                    console.print(f"• You have {status.credits_remaining} credits remaining")
                    console.print(f"• Consider upgrading for more credits")
                    console.print(f"• Visit [bold]https://clyrdia.com[/bold] to upgrade")
            
            return status.credits_remaining
        except Exception as e:
            console.print(f"[red]❌ Could not fetch credit balance: {str(e)}[/red]")
            return 0
    
    def check_credits_sufficient(self, required_credits: int) -> Tuple[bool, int]:
        """Check if user has sufficient credits for an operation"""
        try:
            status = asyncio.run(self.get_status())
            if status.credits_remaining >= required_credits:
                return True, status.credits_remaining
            else:
                return False, status.credits_remaining
        except Exception as e:
            console.print(f"[red]❌ Could not check credit balance: {str(e)}[/red]")
            return False, 0
    
    def show_upgrade_message(self):
        """Display upgrade message when credits are insufficient"""
        console.print(f"\n[red]🚫 Out of Credits![/red]")
        console.print(f"• You've used all your available credits")
        console.print(f"• Upgrade to Pro for 10,000 credits/month")
        console.print(f"• Priority support and advanced features")
        console.print(f"• Visit [bold]https://clyrdia.com[/bold] to upgrade")
        console.print(f"• No credit card required for free plan")
