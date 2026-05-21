import os
import random
from typing import List, Optional, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
from models import Player, Team
from database import Database

class AuctionController(QObject):
    player_changed = pyqtSignal(object)
    bid_updated = pyqtSignal(int, str)
    player_sold = pyqtSignal(object, int, str)
    team_updated = pyqtSignal(object)
    status_changed = pyqtSignal(str)
    category_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.current_category = None
        self.available_players_by_category = {}
        
        self.base_prices = {
            'A': 500,
            'B': 300,
            'C': 200,
            'D': 100
        }
        
        # Force reload players from folders (clear existing data)
        self.reload_players_from_folders()
        
    def reload_players_from_folders(self):
        """Delete existing players and reload from image folders"""
        categories = ['A', 'B', 'C', 'D']
        base_path = 'players'
        
        # Clear existing player data
        self.db.state.players = []
        self.db.state.players_by_category = {}
        
        for category in categories:
            category_path = os.path.join(base_path, category)
            if os.path.exists(category_path):
                images = [f for f in os.listdir(category_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                
                for img in images:
                    # Extract player name from image file name only
                    player_name = os.path.splitext(img)[0]
                    # Keep the original filename without any modification
                    player_name = player_name.replace('_', ' ').replace('-', ' ')
                    
                    image_path = os.path.join(category_path, img)
                    base_price = self.base_prices.get(category, 0)
                    player = Player(
                        name=player_name,
                        category=category,
                        image_path=image_path,
                        base_price=base_price,
                        highest_bid=base_price,
                        is_auctioned=False,
                        status='PENDING'
                    )
                    self.db.save_player(player)
        
        self.db.save_data()
        self.prepare_available_players()
    
    def prepare_available_players(self):
        categories = ['A', 'B', 'C', 'D']
        
        for category in categories:
            all_players = self.db.get_players_by_category(category)
            # Filter out already auctioned players
            available = [p for p in all_players if not p.is_auctioned]
            self.available_players_by_category[category] = available
        
        # Debug print
        print("Available players by category:")
        for cat, players in self.available_players_by_category.items():
            print(f"Category {cat}: {[p.name for p in players]}")
    
    def initialize_teams(self):
        team_owners = [
            ("Jakir", "Jakir's Warriors"),
            ("Fayaz", "Fayaz's Kings"),
            ("Sohag", "Sohag's Tigers"),
            ("Sabbir", "Sabbir's Eagles")
        ]
        
        for owner, team_name in team_owners:
            # Check if team already exists
            if not self.db.get_team(team_name):
                team = Team(
                    name=team_name,
                    owner_name=owner,
                    budget=20000,
                    remaining_balance=20000
                )
                self.db.save_team(team)
    
    def get_teams(self):
        return self.db.get_all_teams()
    
    def get_next_player_by_category_rotation(self) -> Optional[Player]:
        """Get next player following A->B->C->D->A rotation"""
        categories = ['A', 'B', 'C', 'D']
        current_index = self.db.get_current_category_index()
        
        # Try each category in rotation starting from current index
        for attempt in range(4):
            category_index = (current_index + attempt) % 4
            category = categories[category_index]
            available_players = self.available_players_by_category.get(category, [])
            
            if available_players:
                # Take the first player from this category
                next_player = available_players.pop(0)
                # Reset player state for new auction
                next_player.highest_bid = next_player.base_price
                next_player.highest_bidder = None
                next_player.status = 'PENDING'
                next_player.is_auctioned = False
                self.current_category = category
                
                # Update available players list
                self.available_players_by_category[category] = available_players
                
                # Move to next category for next time
                next_index = (category_index + 1) % 4
                self.db.set_current_category_index(next_index)
                self.db.set_current_player(next_player)
                
                self.player_changed.emit(next_player)
                self.category_changed.emit(category)
                
                return next_player
        
        return None
    
    def update_bid(self, amount: int, owner_name: str) -> bool:
        current_player = self.db.get_current_player()
        if not current_player or current_player.status != 'PENDING':
            return False
        
        team = None
        for t in self.db.get_all_teams().values():
            if t.owner_name == owner_name:
                team = t
                break
        
        if not team or team.remaining_balance < amount:
            return False
        
        min_increment = max(50, int(current_player.highest_bid * 0.1))
        
        if amount >= current_player.highest_bid + min_increment:
            current_player.highest_bid = amount
            current_player.highest_bidder = owner_name
            self.db.save_player(current_player)
            self.bid_updated.emit(amount, owner_name)
            return True
        
        return False
    
    def mark_sold(self) -> bool:
        current_player = self.db.get_current_player()
        if not current_player or current_player.status != 'PENDING':
            return False
        
        if not current_player.highest_bidder:
            return False
        
        team = None
        for t in self.db.get_all_teams().values():
            if t.owner_name == current_player.highest_bidder:
                team = t
                break
        
        if not team or team.remaining_balance < current_player.highest_bid:
            return False
        
        # Deduct from team balance
        team.remaining_balance -= current_player.highest_bid
        team.purchased_players.append({
            'name': current_player.name,
            'category': current_player.category,
            'price': current_player.highest_bid,
            'base_price': current_player.base_price
        })
        self.db.save_team(team)
        
        # Update player status
        current_player.status = 'SOLD'
        current_player.sold_price = current_player.highest_bid
        current_player.sold_to = current_player.highest_bidder
        current_player.is_auctioned = True
        self.db.save_player(current_player)
        
        # Add to history
        from datetime import datetime
        self.db.add_auction_history({
            'player': current_player.name,
            'category': current_player.category,
            'base_price': current_player.base_price,
            'sold_to': current_player.highest_bidder,
            'price': current_player.highest_bid,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        self.db.add_to_auction_order(current_player.name)
        self.player_sold.emit(current_player, current_player.highest_bid, current_player.highest_bidder)
        self.team_updated.emit(team)
        return True
    
    def mark_unsold(self) -> bool:
        current_player = self.db.get_current_player()
        if not current_player:
            return False
        
        current_player.status = 'UNSOLD'
        current_player.is_auctioned = True
        self.db.save_player(current_player)
        self.db.add_to_auction_order(current_player.name)
        
        from datetime import datetime
        self.db.add_auction_history({
            'player': current_player.name,
            'category': current_player.category,
            'base_price': current_player.base_price,
            'sold_to': 'UNSOLD',
            'price': 0,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'UNSOLD'
        })
        
        self.status_changed.emit('UNSOLD')
        return True
    
    def reset_player(self) -> bool:
        current_player = self.db.get_current_player()
        if not current_player or current_player.is_auctioned:
            return False
        
        current_player.status = 'PENDING'
        current_player.highest_bid = current_player.base_price
        current_player.highest_bidder = None
        current_player.sold_price = 0
        current_player.sold_to = None
        self.db.save_player(current_player)
        self.player_changed.emit(current_player)
        return True
    
    def get_current_player(self) -> Optional[Player]:
        return self.db.get_current_player()
    
    def has_more_players(self) -> bool:
        total_remaining = sum(len(players) for players in self.available_players_by_category.values())
        return total_remaining > 0
    
    def get_remaining_players_count(self) -> int:
        return sum(len(players) for players in self.available_players_by_category.values())
    
    def get_players_by_category_summary(self) -> dict:
        return {
            category: len(players) 
            for category, players in self.available_players_by_category.items()
        }
    
    def export_results_to_pdf(self):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, mm
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from datetime import datetime
            import os
            
            # Try to register a Unicode font that supports Bengali
            # If available, use Arial Unicode MS or similar
            try:
                # Try to find a good Unicode font
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/arialuni.ttf",
                    "C:/Windows/Fonts/ARIALUNI.TTF",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/System/Library/Fonts/Arial.ttf"
                ]
                font_registered = False
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                        font_registered = True
                        break
                if not font_registered:
                    # Fallback to Helvetica (English only)
                    font_name = 'Helvetica'
                else:
                    font_name = 'CustomFont'
            except:
                font_name = 'Helvetica'
            
            filename = f'auction_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            doc = SimpleDocTemplate(filename, pagesize=landscape(A4), 
                                   leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
            styles = getSampleStyleSheet()
            story = []
            
            # Create custom styles with proper font
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#006600'),
                alignment=TA_CENTER,
                spaceAfter=20,
                fontName=font_name
            )
            title = Paragraph("Cricket Player Auction Results", title_style)
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Normal'],
                fontSize=14,
                alignment=TA_CENTER,
                spaceAfter=10,
                fontName=font_name
            )
            subtitle = Paragraph(f"Sujapur Tournament<br/>Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", subtitle_style)
            story.append(subtitle)
            story.append(Spacer(1, 0.3*inch))
            
            # Teams section
            heading_style = ParagraphStyle(
                'HeadingStyle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#cc6600'),
                spaceAfter=10,
                fontName=font_name,
                alignment=TA_CENTER
            )
            story.append(Paragraph("Team Summary", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Teams table
            team_data = [['Owner', 'Team Name', 'Budget', 'Remaining', 'Players']]
            teams = self.db.get_all_teams()
            for team in teams.values():
                team_data.append([
                    team.owner_name,
                    team.name,
                    f"৳{team.budget:,}",
                    f"৳{team.remaining_balance:,}",
                    str(len(team.purchased_players))
                ])
            
            team_table = Table(team_data, colWidths=[80, 100, 70, 70, 50])
            team_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cce6cc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTNAME', (0, 1), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(team_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Purchased players section
            story.append(Paragraph("Purchased Players List", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            for team in teams.values():
                if team.purchased_players:
                    team_heading = Paragraph(f"<b>{team.owner_name} - {team.name}</b>", 
                                            ParagraphStyle('TeamHeading', parent=styles['Normal'], 
                                                          fontName=font_name, fontSize=11, spaceAfter=5))
                    story.append(team_heading)
                    
                    player_data = [['Player Name', 'Category', 'Base Price', 'Purchase Price']]
                    total_spent = 0
                    for player in team.purchased_players:
                        player_data.append([
                            player['name'],
                            player['category'],
                            f"৳{player['base_price']:,}",
                            f"৳{player['price']:,}"
                        ])
                        total_spent += player['price']
                    
                    player_table = Table(player_data, colWidths=[120, 50, 70, 80])
                    player_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9d9d9')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('FONTNAME', (0, 0), (-1, 0), font_name),
                        ('FONTNAME', (0, 1), (-1, -1), font_name),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(player_table)
                    
                    total_text = Paragraph(f"<b>Total Spent: ৳{total_spent:,}</b>",
                                          ParagraphStyle('TotalStyle', parent=styles['Normal'],
                                                        fontName=font_name, fontSize=9, alignment=TA_RIGHT))
                    story.append(total_text)
                    story.append(Spacer(1, 0.15*inch))
            
            # Auction history section
            story.append(Paragraph("Auction History", heading_style))
            story.append(Spacer(1, 0.1*inch))
            
            history_data = [['#', 'Player', 'Cat', 'Base Price', 'Sold Price', 'Buyer', 'Time']]
            history = self.db.get_auction_history()
            for idx, record in enumerate(history, 1):
                price_text = f"৳{record.get('price', 0):,}" if record.get('price', 0) > 0 else 'Unsold'
                buyer_text = record.get('sold_to', '') if record.get('sold_to') != 'UNSOLD' else 'Unsold'
                history_data.append([
                    str(idx),
                    record.get('player', '')[:20],
                    record.get('category', ''),
                    f"৳{record.get('base_price', 0):,}",
                    price_text,
                    buyer_text[:15],
                    record.get('timestamp', '')[-8:] if record.get('timestamp') else ''
                ])
            
            history_table = Table(history_data, colWidths=[30, 100, 30, 65, 65, 70, 60])
            history_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#99ccff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTNAME', (0, 1), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(history_table)
            
            # Build PDF
            doc.build(story)
            return filename
            
        except Exception as e:
            # Fallback to JSON if PDF fails
            from datetime import datetime
            import json
            filename = f'auction_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            results = {
                'teams': {name: team.to_dict() for name, team in self.db.get_all_teams().items()},
                'auction_order': self.db.get_auction_order(),
                'history': self.db.get_auction_history(),
                'export_time': str(datetime.now())
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            return filename