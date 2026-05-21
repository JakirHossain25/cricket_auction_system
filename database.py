
import json
import os
from typing import List, Dict, Optional
from models import Player, Team, AuctionState

class Database:
    def __init__(self, db_path='auction_data.json'):
        self.db_path = db_path
        self.load_data()
    
    def load_data(self):
        """Load auction data from JSON file"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.state = AuctionState.from_dict(data)
            except:
                self.state = AuctionState()
        else:
            self.state = AuctionState()
    
    def save_data(self):
        """Save auction data to JSON file"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.state.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_all_players(self) -> List[Player]:
        return self.state.players
    
    def get_players_by_category(self, category: str) -> List[Player]:
        return self.state.players_by_category.get(category, [])
    
    def save_player(self, player: Player):
        for i, p in enumerate(self.state.players):
            if p.name == player.name:
                self.state.players[i] = player
                break
        else:
            self.state.players.append(player)
        
        if player.category not in self.state.players_by_category:
            self.state.players_by_category[player.category] = []
        
        for i, p in enumerate(self.state.players_by_category[player.category]):
            if p.name == player.name:
                self.state.players_by_category[player.category][i] = player
                break
        else:
            self.state.players_by_category[player.category].append(player)
        
        self.save_data()
    
    def get_team(self, team_name: str) -> Optional[Team]:
        return self.state.teams.get(team_name)
    
    def save_team(self, team: Team):
        self.state.teams[team.name] = team
        self.save_data()
    
    def get_all_teams(self) -> Dict[str, Team]:
        return self.state.teams
    
    def set_current_player(self, player: Player):
        self.state.current_player = player
        self.save_data()
    
    def get_current_player(self) -> Optional[Player]:
        return self.state.current_player
    
    def add_auction_history(self, record: Dict):
        self.state.auction_history.append(record)
        self.save_data()
    
    def get_auction_history(self) -> List[Dict]:
        return self.state.auction_history
    
    def add_to_auction_order(self, player_name: str):
        self.state.auction_order.append(player_name)
        self.save_data()
    
    def get_auction_order(self) -> List[str]:
        return self.state.auction_order
    
    def get_current_category_index(self) -> int:
        return self.state.current_category_index
    
    def set_current_category_index(self, index: int):
        self.state.current_category_index = index
        self.save_data()
    
    def reset_auction(self):
        self.state = AuctionState()
        self.save_data()