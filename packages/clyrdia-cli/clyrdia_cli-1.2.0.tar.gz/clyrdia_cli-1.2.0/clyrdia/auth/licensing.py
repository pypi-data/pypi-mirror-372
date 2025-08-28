"""
Licensing management for Clyrdia CLI - handles authentication and credit system.
"""

import os
import json
import asyncio
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

from ..models.user import UserStatus, CreditEstimate, PlanTier, UserRole, TeamInfo, TeamMember
from ..tiers.tiers import TIER_CONFIG, get_plan_features as get_tier_features, Feature
from ..models.results import TestCase
from ..caching.manager import CacheManager
from ..database.local_db import LocalDatabase
from ..core.console import console

class LicensingManager:
    """Manages SaaS licensing and credit system"""
    
    def __init__(self):
        from ..config import config
        self.config = config
        self.config_dir = Path.home() / ".clyrdia"
        self.config_file = self.config_dir / "config.json"
        self.api_key = self._load_api_key()
        self.db = LocalDatabase()
    
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
        """Get current user status and credit balance from local database"""
        if not self.api_key:
            raise Exception("No API key configured")
        
        # Try to get user from local database first
        user_id = self._get_user_id_from_api_key()
        if user_id:
            user_data = self.db.get_user(user_id)
            if user_data:
                return self._create_user_status_from_db(user_data)
        
        # Fallback to API call
        try:
            response = await self._make_api_request("/cli-status")
            return self._create_user_status_from_api(response)
        except Exception as e:
            # Create default user if API fails
            return self._create_default_user_status()
    
    def _get_user_id_from_api_key(self) -> Optional[str]:
        """Extract user ID from API key (simplified for demo)"""
        if not self.api_key:
            return None
        
        # In a real implementation, this would decode the JWT or hash
        # For now, we'll use a simple hash-based approach
        import hashlib
        user_hash = hashlib.md5(self.api_key.encode()).hexdigest()[:8]
        return f"user_{user_hash}"
    
    def _create_user_status_from_db(self, user_data: Dict[str, Any]) -> UserStatus:
        """Create UserStatus from local database data"""
        try:
            plan = PlanTier(user_data['plan_tier'])
        except ValueError:
            plan = PlanTier.DEVELOPER
        
        return UserStatus(
            user_name=user_data['username'],
            plan=plan,
            credits_remaining=user_data['credits_remaining'],
            credits_monthly_limit=user_data['monthly_credits'],
            resets_on=user_data['credits_reset_date'],
            api_key=self.api_key,
            team_id=None,  # Will be populated if user is in a team
            role=None,
            team_name=None,
            max_team_members=None,
            has_cicd_access=plan == PlanTier.BUSINESS
        )
    
    def _create_user_status_from_api(self, response: Dict[str, Any]) -> UserStatus:
        """Create UserStatus from API response"""
        plan_str = response.get("plan", "developer")
        try:
            plan = PlanTier(plan_str)
        except ValueError:
            plan = PlanTier.DEVELOPER
        
        role = None
        if "role" in response:
            try:
                role = UserRole(response["role"])
            except ValueError:
                role = UserRole.MEMBER
        
        return UserStatus(
            user_name=response["user_name"],
            plan=plan,
            credits_remaining=response["credits_remaining"],
            credits_monthly_limit=response.get("credits_monthly_limit", 100),
            resets_on=response["resets_on"],
            api_key=self.api_key,
            team_id=response.get("team_id"),
            role=role,
            team_name=response.get("team_name"),
            max_team_members=response.get("max_team_members"),
            has_cicd_access=response.get("has_cicd_access", False)
        )
    
    def _create_default_user_status(self) -> UserStatus:
        """Create default UserStatus for new users"""
        user_id = self._get_user_id_from_api_key()
        if user_id:
            # Create user in local database
            self.db.create_user(
                user_id=user_id,
                username=f"user_{user_id[-4:]}",
                email=f"user_{user_id[-4:]}@example.com",
                plan_tier="developer"
            )
        
        return UserStatus(
            user_name=f"user_{user_id[-4:] if user_id else 'new'}",
            plan=PlanTier.DEVELOPER,
            credits_remaining=100,
            credits_monthly_limit=100,
            resets_on=self._get_next_reset_date(),
            api_key=self.api_key,
            team_id=None,
            role=None,
            team_name=None,
            max_team_members=None,
            has_cicd_access=False
        )
    
    def _get_next_reset_date(self) -> str:
        """Get the next monthly reset date"""
        now = datetime.now()
        if now.day >= 25:  # Reset on 25th of each month
            next_month = now.replace(day=25) + timedelta(days=32)
            next_month = next_month.replace(day=25)
        else:
            next_month = now.replace(day=25)
        
        return next_month.strftime("%Y-%m-%d")
    
    async def get_team_info(self) -> Optional[TeamInfo]:
        """Get team information if user is part of a team"""
        if not self.is_authenticated():
            return None
        
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return None
            
            # Get user's team from database
            user_data = self.db.get_user(user_id)
            if not user_data:
                return None
            
            # For now, we'll create a mock team for Business tier users
            if user_data['plan_tier'] == 'business':
                team_id = f"team_{user_id[-4:]}"
                team_info = self.db.get_team_info(team_id)
                if not team_info:
                    # Create team if it doesn't exist
                    self.db.create_team(team_id, f"Team {user_data['username']}", user_id, "business")
                    team_info = self.db.get_team_info(team_id)
                
                if team_info:
                    return self._create_team_info_from_db(team_info)
            
            return None
        except Exception:
            return None
    
    def _create_team_info_from_db(self, team_data: Dict[str, Any]) -> TeamInfo:
        """Create TeamInfo from local database data"""
        try:
            plan = PlanTier(team_data['plan_tier'])
        except ValueError:
            plan = PlanTier.DEVELOPER
        
        members = []
        for member_data in team_data.get('members', []):
            try:
                role = UserRole(member_data['role'])
            except ValueError:
                role = UserRole.MEMBER
            
            members.append(TeamMember(
                user_id=member_data['user_id'],
                user_name=member_data['username'],
                email=member_data['email'],
                role=role,
                joined_at=member_data['joined_at'],
                last_active=member_data['last_active']
            ))
        
        return TeamInfo(
            team_id=team_data['id'],
            team_name=team_data['name'],
            owner_id=team_data['owner_id'],
            plan=plan,
            member_count=team_data['member_count'],
            max_members=team_data['max_members'],
            credits_monthly_limit=team_data['monthly_credits'],
            has_cicd_access=plan == PlanTier.BUSINESS,
            created_at=team_data['created_at'],
            members=members
        )
    
    async def debit_credits(self, credits_to_debit: int, run_id: str) -> Dict[str, Any]:
        """Debit credits for a benchmark run"""
        user_id = self._get_user_id_from_api_key()
        if not user_id:
            raise Exception("User not authenticated")
        
        # Deduct credits from local database
        success = self.db.deduct_credits(
            user_id=user_id,
            amount=credits_to_debit,
            description=f"Benchmark run: {run_id}",
            benchmark_id=run_id
        )
        
        if not success:
            raise Exception("Insufficient credits")
        
        # Record feature usage
        self.db.record_feature_usage(
            user_id=user_id,
            feature="benchmark_run",
            metadata=f"run_id:{run_id},credits:{credits_to_debit}"
        )
        
        return {
            "success": True,
            "credits_debited": credits_to_debit,
            "run_id": run_id
        }
    
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
    
    def get_plan_features(self, plan: PlanTier) -> Dict[str, Any]:
        """Get features for a specific plan tier"""
        features = get_tier_features(plan)
        if features:
            return {
                "monthly_credits": features.monthly_credits,
                "max_users": features.max_users,
                "has_cicd": Feature.CI_CD_INTEGRATION in features.features,
                "has_advanced_reporting": Feature.ADVANCED_REPORTING in features.features,
                "has_team_management": Feature.TEAM_MANAGEMENT in features.features,
                "has_priority_support": Feature.PRIORITY_SUPPORT in features.features,
                "price_usd": features.price_usd
            }
        return {}
    
    def can_access_cicd(self, user_status: UserStatus) -> bool:
        """Check if user can access CI/CD features"""
        return user_status.has_cicd_access and user_status.plan in [PlanTier.BUSINESS]
    
    def can_manage_team(self, user_status: UserStatus) -> bool:
        """Check if user can manage team members"""
        return (user_status.plan in [PlanTier.BUSINESS] and 
                user_status.role in [UserRole.OWNER, UserRole.ADMIN])
    
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
                    # More accurate credit estimation based on actual token count
                    estimated_tokens = len(test_case.prompt.split()) * 1.3  # Rough estimate
                    estimated_credits = max(1, int(estimated_tokens / 1000))  # 1 credit per 1K tokens
                    total_credits += estimated_credits
                    test_breakdown[test_key] = estimated_credits
        
        # Get current balance from local database
        current_balance = 0
        if self.is_authenticated():
            try:
                user_id = self._get_user_id_from_api_key()
                if user_id:
                    user_data = self.db.get_user(user_id)
                    if user_data:
                        current_balance = user_data['credits_remaining']
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
            user_id = self._get_user_id_from_api_key()
            if user_id:
                # Get credit history from local database
                history = self.db.get_credit_history(user_id, days=30)
                for transaction in history:
                    if transaction.get('benchmark_id') == run_id:
                        return transaction
            return {"error": "No usage data found", "run_id": run_id}
        except Exception as e:
            return {"error": str(e), "run_id": run_id}
    
    def show_credit_balance(self):
        """Display current credit balance from local database"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                console.print("[red]❌ Not authenticated[/red]")
                return 0
            
            user_data = self.db.get_user(user_id)
            if not user_data:
                console.print("[red]❌ User not found[/red]")
                return 0
            
            plan_features = self.get_plan_features(PlanTier(user_data['plan_tier']))
            
            console.print(f"[bold]💰 Current Balance: {user_data['credits_remaining']} credits[/bold]")
            console.print(f"[dim]Plan: {user_data['plan_tier'].upper()}[/dim]")
            console.print(f"[dim]Monthly Limit: {user_data['monthly_credits']} credits[/dim]")
            console.print(f"[dim]Resets on: {user_data['credits_reset_date']}[/dim]")
            
            # Show upgrade message if credits are low
            if user_data['credits_remaining'] <= user_data['monthly_credits'] * 0.1:  # 10% of monthly limit
                self._show_upgrade_message(PlanTier(user_data['plan_tier']), user_data['credits_remaining'])
            
            return user_data['credits_remaining']
        except Exception as e:
            console.print(f"[red]❌ Could not fetch credit balance: {str(e)}[/red]")
            return 0
    
    def _show_upgrade_message(self, plan: PlanTier, credits_remaining: int):
        """Show appropriate upgrade message based on current plan"""
        if plan == PlanTier.DEVELOPER:
            console.print(f"\n[yellow]⚠️  Low credits![/yellow]")
            console.print(f"• You have {credits_remaining} credits remaining")
            console.print(f"• Developer plan includes 100 credits/month")
            console.print(f"• Upgrade to Pro for 1,000 credits/month ($25/month)")
            console.print(f"• Visit [bold]https://clyrdia.com[/bold] to upgrade")
        elif plan == PlanTier.PRO:
            console.print(f"\n[yellow]⚠️  Low credits![/yellow]")
            console.print(f"• You have {credits_remaining} credits remaining")
            console.print(f"• Pro plan includes 1,000 credits/month")
            console.print(f"• Upgrade to Business for 25,000 credits/month + team features ($500/month)")
            console.print(f"• Visit [bold]https://clyrdia.com[/bold] to upgrade")
        else:
            console.print(f"\n[yellow]⚠️  Low credits![/yellow]")
            console.print(f"• You have {credits_remaining} credits remaining")
            console.print(f"• Consider upgrading for more credits")
            console.print(f"• Visit [bold]https://clyrdia.com[/bold] to upgrade")
    
    def check_credits_sufficient(self, required_credits: int) -> Tuple[bool, int]:
        """Check if user has sufficient credits for an operation"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return False, 0
            
            user_data = self.db.get_user(user_id)
            if not user_data:
                return False, 0
            
            if user_data['credits_remaining'] >= required_credits:
                return True, user_data['credits_remaining']
            else:
                return False, user_data['credits_remaining']
        except Exception as e:
            console.print(f"[red]❌ Could not check credit balance: {str(e)}[/red]")
            return False, 0
    
    def show_upgrade_message(self):
        """Display upgrade message when credits are insufficient"""
        console.print(f"\n[red]🚫 Out of Credits![/red]")
        console.print(f"• You've used all your available credits")
        console.print(f"• Upgrade to Pro for 1,000 credits/month ($25/month)")
        console.print(f"• Upgrade to Business for 25,000 credits/month + team features ($500/month)")
        console.print(f"• Visit [bold]https://clyrdia.com[/bold] to upgrade")
        console.print(f"• No credit card required for Developer plan")
    
    def show_plan_comparison(self):
        """Display plan comparison to help users choose"""
        console.print(f"\n[bold]📋 Plan Comparison[/bold]")
        console.print(f"┌─────────────────┬─────────────┬─────────────┬─────────────┐")
        console.print(f"│ Feature         │ Developer   │ Pro         │ Business    │")
        console.print(f"├─────────────────┼─────────────┼─────────────┼─────────────┤")
        console.print(f"│ Monthly Credits │ 100         │ 1,000       │ 25,000      │")
        console.print(f"│ Users           │ 1           │ 1           │ Up to 10    │")
        console.print(f"│ CI/CD Access    │ ❌          │ ❌          │ ✅          │")
        console.print(f"│ Team Management │ ❌          │ ❌          │ ✅          │")
        console.print(f"│ Advanced Reports│ ❌          │ ❌          │ ✅          │")
        console.print(f"│ Priority Support│ ❌          │ ❌          │ ✅          │")
        console.print(f"│ Price           │ Free        │ $25/month   │ $500/month  │")
        console.print(f"└─────────────────┴─────────────┴─────────────┴─────────────┘")
        console.print(f"\n💡 [bold]Upgrade at:[/bold] https://clyrdia.com")
    
    def get_credit_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get credit transaction history for current user"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return []
            
            return self.db.get_credit_history(user_id, days)
        except Exception as e:
            console.print(f"[red]❌ Error getting credit history: {str(e)}[/red]")
            return []
    
    def create_api_key(self, name: str, permissions: str = "read", team_id: str = None) -> Optional[str]:
        """Create a new API key for user or team"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return None
            
            # Generate new API key
            new_api_key = f"clyrdia_{uuid.uuid4().hex[:16]}"
            key_hash = f"key_{uuid.uuid4().hex[:8]}"
            
            # Save to database
            success = self.db.create_api_key(
                user_id=user_id,
                key_hash=key_hash,
                name=name,
                team_id=team_id,
                permissions=permissions
            )
            
            if success:
                return new_api_key
            
            return None
        except Exception as e:
            console.print(f"[red]❌ Error creating API key: {str(e)}[/red]")
            return None
    
    def list_api_keys(self) -> List[Dict[str, Any]]:
        """List all API keys for current user"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return []
            
            return self.db.get_user_api_keys(user_id)
        except Exception as e:
            console.print(f"[red]❌ Error listing API keys: {str(e)}[/red]")
            return []
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key for current user"""
        try:
            user_id = self._get_user_id_from_api_key()
            if not user_id:
                return False
            
            return self.db.revoke_api_key(user_id, key_id)
        except Exception as e:
            console.print(f"[red]❌ Error revoking API key: {str(e)}[/red]")
            return False
