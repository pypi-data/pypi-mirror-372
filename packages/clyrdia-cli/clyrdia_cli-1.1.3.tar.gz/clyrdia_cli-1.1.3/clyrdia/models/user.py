"""
User models for Clyrdia CLI authentication and licensing.
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class UserStatus:
    """User subscription and credit status"""
    user_name: str
    plan: str  # "free" or "pro"
    credits_remaining: int
    resets_on: str
    api_key: str

@dataclass
class CreditEstimate:
    """Credit cost estimation for a benchmark run"""
    total_tests: int
    cache_hits: int
    live_api_calls: int
    estimated_credits: int
    current_balance: int
    test_breakdown: Dict[str, int]
