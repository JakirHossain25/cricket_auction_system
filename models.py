from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json

@dataclass
class Player:
    name: str
    category: str
    image_path: str
    base_price: int = 0
    status: str = "PENDING"  # PENDING, SOLD, UNSOLD
    highest_bid: int = 0
    highest_bidder: Optional[str] = None
    sold_price: int = 0
    sold_to: Optional[str] = None
    is_auctioned: bool = False
    
    def to_dict(self):
        return {
            'name': self.name,
            'category': self.category,
            'image_path': self.image_path,
            'base_price': self.base_price,
            'status': self.status,
            'highest_bid': self.highest_bid,
            'highest_bidder': self.highest_bidder,
            'sold_price': self.sold_price,
            'sold_to': self.sold_to,
            'is_auctioned': self.is_auctioned
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class Team:
    name: str
    owner_name: str
    budget: int = 20000
    remaining_balance: int = 20000
    purchased_players: List[Dict] = field(default_factory=list)
    
    def to_dict(self):
        return {
            'name': self.name,
            'owner_name': self.owner_name,
            'budget': self.budget,
            'remaining_balance': self.remaining_balance,
            'purchased_players': self.purchased_players
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            owner_name=data['owner_name'],
            budget=data['budget'],
            remaining_balance=data['remaining_balance'],
            purchased_players=data.get('purchased_players', [])
        )

@dataclass
class AuctionState:
    current_player: Optional[Player] = None
    players: List[Player] = field(default_factory=list)
    players_by_category: Dict[str, List[Player]] = field(default_factory=dict)
    current_category_index: int = 0  # 0=A, 1=B, 2=C, 3=D
    categories: List[str] = field(default_factory=lambda: ['A', 'B', 'C', 'D'])
    teams: Dict[str, Team] = field(default_factory=dict)
    auction_history: List[Dict] = field(default_factory=list)
    auction_order: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            'current_player': self.current_player.to_dict() if self.current_player else None,
            'players': [p.to_dict() for p in self.players],
            'players_by_category': {cat: [p.to_dict() for p in players] for cat, players in self.players_by_category.items()},
            'current_category_index': self.current_category_index,
            'categories': self.categories,
            'teams': {name: team.to_dict() for name, team in self.teams.items()},
            'auction_history': self.auction_history,
            'auction_order': self.auction_order
        }
    
    @classmethod
    def from_dict(cls, data):
        state = cls()
        if data.get('current_player'):
            state.current_player = Player.from_dict(data['current_player'])
        state.players = [Player.from_dict(p) for p in data.get('players', [])]
        state.players_by_category = {
            cat: [Player.from_dict(p) for p in players] 
            for cat, players in data.get('players_by_category', {}).items()
        }
        state.current_category_index = data.get('current_category_index', 0)
        state.categories = data.get('categories', ['A', 'B', 'C', 'D'])
        state.teams = {name: Team.from_dict(team) for name, team in data.get('teams', {}).items()}
        state.auction_history = data.get('auction_history', [])
        state.auction_order = data.get('auction_order', [])
        return state