# filename: models.py
"""
Data models for Expense Tracker
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Expense:
    """Expense data model"""
    id: Optional[int] = None
    description: str = ""
    amount: float = 0.0
    category: str = "Other"
    date: str = ""
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    @property
    def formatted_amount(self) -> str:
        """Return amount formatted as currency"""
        return f"${self.amount:.2f}"
    
    @property
    def formatted_date(self) -> str:
        """Return date in a readable format"""
        try:
            dt = datetime.strptime(self.date, "%Y-%m-%d")
            return dt.strftime("%B %d, %Y")
        except ValueError:
            return self.date
    
    def to_dict(self) -> dict:
        """Convert expense to dictionary"""
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Expense':
        """Create an Expense from a dictionary"""
        return cls(
            id=data.get('id'),
            description=data.get('description', ''),
            amount=data.get('amount', 0.0),
            category=data.get('category', 'Other'),
            date=data.get('date', ''),
            created_at=data.get('created_at')
        )

@dataclass
class CategorySummary:
    """Summary statistics for a category"""
    category: str
    count: int
    total: float
    average: float
    
    @property
    def formatted_total(self) -> str:
        return f"${self.total:.2f}"
    
    @property
    def formatted_average(self) -> str:
        return f"${self.average:.2f}"

@dataclass
class MonthlyTrend:
    """Monthly trend data"""
    month: str
    total: float
    count: int
    average: float
    
    @property
    def month_name(self) -> str:
        """Convert YYYY-MM to month name"""
        try:
            dt = datetime.strptime(self.month, "%Y-%m")
            return dt.strftime("%B %Y")
        except ValueError:
            return self.month
    
    @property
    def formatted_total(self) -> str:
        return f"${self.total:.2f}"
