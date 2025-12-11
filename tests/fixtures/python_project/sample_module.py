"""
Sample Python module for testing scanner.
This file contains various Python constructs to test extraction.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class User:
    """User data model with validation."""
    id: int
    name: str
    email: str
    is_active: bool = True
    
    def validate_email(self) -> bool:
        """Validate email format."""
        return "@" in self.email
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        return f"{self.name} ({self.email})"
    
    @classmethod
    def create(cls, name: str, email: str) -> "User":
        """Factory method to create user."""
        import random
        return cls(id=random.randint(1, 1000), name=name, email=email)


class UserService:
    """Service layer for user operations."""
    
    def __init__(self, database_url: str):
        """Initialize service with database connection."""
        self.database_url = database_url
        self.users: List[User] = []
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Retrieve user by ID.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            User object if found, None otherwise
        """
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        user = User.create(name, email)
        self.users.append(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_user(user_id)
        if user:
            self.users.remove(user)
            return True
        return False


def calculate_statistics(numbers: List[int]) -> dict:
    """
    Calculate statistics for a list of numbers.
    
    Args:
        numbers: List of integers
        
    Returns:
        Dictionary with mean, median, and mode
    """
    if not numbers:
        return {"mean": 0, "median": 0, "count": 0}
    
    return {
        "mean": sum(numbers) / len(numbers),
        "median": sorted(numbers)[len(numbers) // 2],
        "count": len(numbers)
    }


async def fetch_data(url: str, timeout: int = 30) -> dict:
    """Async function to fetch data from URL."""
    # Simulated async operation
    return {"status": "success", "url": url}
