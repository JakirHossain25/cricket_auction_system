import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from auction_controller import AuctionController

class PlayerCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(350, 350)
        self.image_label.setMaximumSize(500, 500)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 3px solid #00ff00;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #00ff00;
                padding: 8px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        layout.addWidget(self.name_label)
        
        self.category_badge = QLabel()
        self.category_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.category_badge)
        
        self.base_price_label = QLabel()
        self.base_price_label.setAlignment(Qt.AlignCenter)
        self.base_price_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #ffaa00;
                padding: 5px;
                background-color: #1e1e1e;
                border-radius: 5px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        layout.addWidget(self.base_price_label)
        
        self.status_badge = QLabel()
        self.status_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_badge)
        
        self.bid_label = QLabel("বর্তমান দর: ৳০")
        self.bid_label.setAlignment(Qt.AlignCenter)
        self.bid_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: #ffaa00;
                padding: 8px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        layout.addWidget(self.bid_label)
        
        self.bidder_label = QLabel("সর্বোচ্চ দরদাতা: কেউ নাই")
        self.bidder_label.setAlignment(Qt.AlignCenter)
        self.bidder_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #cccccc;
                padding: 5px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        layout.addWidget(self.bidder_label)
        
        self.setLayout(layout)
        
    def update_player(self, player):
        if os.path.exists(player.image_path):
            pixmap = QPixmap(player.image_path)
            scaled_pixmap = pixmap.scaled(
                500, 500, 
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)
        
        self.name_label.setText(player.name.upper())
        
        category_colors = {
            'A': '#ff4444',
            'B': '#ff8800',
            'C': '#44ff44',
            'D': '#4488ff'
        }
        self.category_badge.setText(f"ক্যাটাগরি {player.category}")
        self.category_badge.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 20px;
                background-color: {category_colors.get(player.category, '#333')};
                color: #fff;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }}
        """)
        
        self.base_price_label.setText(f"বেস প্রাইস: ৳{player.base_price:,}")
        
        status_styles = {
            'PENDING': ('background-color: #ffaa00; color: #000;', 'নিলাম চলছে'),
            'SOLD': ('background-color: #44ff44; color: #000;', 'বিক্রি হয়েছে ✓'),
            'UNSOLD': ('background-color: #ff4444; color: #fff;', 'বিক্রি হয়নি ✗')
        }
        style, text = status_styles.get(player.status, ('background-color: #666;', player.status))
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 20px;
                {style}
                font-family: 'Arial', 'Microsoft Sans Serif';
            }}
        """)
        
        self.bid_label.setText(f"বর্তমান দর: ৳{player.highest_bid:,}")
        self.bidder_label.setText(f"সর্বোচ্চ দরদাতা: {player.highest_bidder or 'কেউ নাই'}")
        
    def update_bid(self, amount, owner):
        self.bid_label.setText(f"বর্তমান দর: ৳{amount:,}")
        self.bidder_label.setText(f"সর্বোচ্চ দরদাতা: {owner}")

class TeamWidget(QWidget):
    def __init__(self, owner_name, team_name, budget, controller, parent=None):
        super().__init__(parent)
        self.owner_name = owner_name
        self.team_name = team_name
        self.budget = budget
        self.controller = controller
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        owner_label = QLabel(self.owner_name.upper())
        owner_label.setAlignment(Qt.AlignCenter)
        owner_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #00ff00;
                padding: 3px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        layout.addWidget(owner_label)
        
        team_label = QLabel(self.team_name)
        team_label.setAlignment(Qt.AlignCenter)
        team_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #ffffff;
                padding: 3px;
                background-color: #1e1e1e;
                border-radius: 5px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        layout.addWidget(team_label)
        
        self.budget_label = QLabel()
        self.budget_label.setAlignment(Qt.AlignCenter)
        self.budget_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #ffaa00;
                padding: 3px;
                font-weight: bold;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        layout.addWidget(self.budget_label)
        
        self.bid_button = QPushButton("বিড দিন (৳)")
        self.bid_button.setStyleSheet("""
            QPushButton {
                background-color: #00ff00;
                color: #000000;
                font-weight: bold;
                padding: 6px;
                border-radius: 5px;
                font-size: 11px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
        """)
        self.bid_button.clicked.connect(self.place_bid)
        layout.addWidget(self.bid_button)
        
        players_label = QLabel("ক্রয়কৃত খেলোয়াড় (৳):")
        players_label.setStyleSheet("color: #00ff00; font-size: 10px; font-family: 'Arial', 'Microsoft Sans Serif';")
        layout.addWidget(players_label)
        
        self.players_list = QListWidget()
        self.players_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 5px;
                color: #ccc;
                font-size: 10px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        self.players_list.setMaximumHeight(120)
        layout.addWidget(self.players_list)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            TeamWidget {
                background-color: #2d2d2d;
                border: 1px solid #00ff00;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        self.update_team_info()
        
    def update_team_info(self):
        team = self.controller.db.get_team(self.team_name)
        if team:
            self.budget_label.setText(f"বাকি: ৳{team.remaining_balance:,}")
            self.players_list.clear()
            for player in team.purchased_players:
                self.players_list.addItem(f"{player['name'][:20]} - ৳{player['price']:,}")
        
    def place_bid(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"বিড দিন - {self.owner_name}")
        dialog.setModal(True)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #00ff00;
                font-size: 12px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
                font-size: 12px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
            QPushButton {
                background-color: #00ff00;
                color: #000;
                padding: 6px;
                border-radius: 5px;
                font-weight: bold;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"মালিক: {self.owner_name}"))
        layout.addWidget(QLabel(f"টিম: {self.team_name}"))
        
        current_player = self.controller.get_current_player()
        if current_player:
            layout.addWidget(QLabel(f"খেলোয়াড়: {current_player.name}"))
            layout.addWidget(QLabel(f"বেস প্রাইস: ৳{current_player.base_price:,}"))
            layout.addWidget(QLabel(f"বর্তমান দর: ৳{current_player.highest_bid:,}"))
            
            min_bid = current_player.highest_bid + max(50, int(current_player.highest_bid * 0.1))
            layout.addWidget(QLabel(f"ন্যূনতম দর: ৳{min_bid:,}"))
            
            bid_input = QLineEdit()
            bid_input.setPlaceholderText("দরের পরিমাণ লিখুন (৳)")
            layout.addWidget(bid_input)
            
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            dialog.setLayout(layout)
            
            if dialog.exec_() == QDialog.Accepted:
                try:
                    amount = int(bid_input.text())
                    if amount >= min_bid:
                        if self.controller.update_bid(amount, self.owner_name):
                            QMessageBox.information(self, "সফল", f"৳{amount:,} টাকার বিড সফলভাবে হয়েছে!")
                            self.update_team_info()
                        else:
                            QMessageBox.warning(self, "ত্রুটি", "পর্যাপ্ত পয়েন্ট নেই অথবা ভুল দর!")
                    else:
                        QMessageBox.warning(self, "ত্রুটি", f"ন্যূনতম দর ৳{min_bid:,} টাকা হতে হবে!")
                except ValueError:
                    QMessageBox.warning(self, "ত্রুটি", "অনুগ্রহ করে সঠিক সংখ্যা লিখুন!")

class AuctionUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = AuctionController()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_initial_data()
        
    def setup_ui(self):
        self.setWindowTitle("ক্রিকেট খেলোয়াড় নিলাম ব্যবস্থা - সুজাপুর টুর্নামেন্ট")
        
        # Get screen geometry and maximize window
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        self.showMaximized()  # Open in maximized mode
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QWidget {
                background-color: #0a0a0a;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                font-weight: bold;
            }
            QMessageBox {
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        self.player_card = PlayerCard()
        left_layout.addWidget(self.player_card)
        
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        info_layout = QHBoxLayout()
        
        self.remaining_label = QLabel()
        self.remaining_label.setStyleSheet("color: #00ff00; font-size: 12px; font-family: 'Arial', 'Microsoft Sans Serif';")
        info_layout.addWidget(self.remaining_label)
        
        self.category_label = QLabel()
        self.category_label.setStyleSheet("color: #ffaa00; font-size: 12px; font-family: 'Arial', 'Microsoft Sans Serif';")
        info_layout.addWidget(self.category_label)
        
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)
        
        control_layout = QHBoxLayout()
        buttons = [
            ("পরবর্তী খেলোয়াড়\n(NEXT PLAYER)", self.next_player, "#00ff00"),
            ("বিক্রি হয়েছে\n(MARK SOLD)", self.mark_sold, "#44ff44"),
            ("বিক্রি হয়নি\n(MARK UNSOLD)", self.mark_unsold, "#ff4444"),
            ("রিসেট\n(RESET PLAYER)", self.reset_player, "#ffaa00")
        ]
        
        for text, callback, color in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #000;
                    font-weight: bold;
                    padding: 12px;
                    border-radius: 5px;
                    font-size: 13px;
                    font-family: 'Arial', 'Microsoft Sans Serif';
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            control_layout.addWidget(btn)
        
        left_layout.addLayout(control_layout)
        
        export_btn = QPushButton("ফলাফল এক্সপোর্ট করুন\n(EXPORT RESULTS)")
        export_btn.clicked.connect(self.export_results)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4488ff;
                color: #fff;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                font-size: 13px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        left_layout.addWidget(export_btn)
        
        left_panel.setLayout(left_layout)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        teams_label = QLabel("টিমসমূহ (TEAMS)")
        teams_label.setAlignment(Qt.AlignCenter)
        teams_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00ff00;
                padding: 8px;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        right_layout.addWidget(teams_label)
        
        self.team_widgets = {}
        self.teams_grid = QGridLayout()
        right_layout.addLayout(self.teams_grid)
        
        right_panel.setLayout(right_layout)
        
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        
        central_widget.setLayout(main_layout)
        
        self.statusBar().showMessage("প্রস্তুত | খেলোয়াড় নিলাম শুরু করতে প্রস্তুত")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #00ff00;
                font-weight: bold;
                font-family: 'Arial', 'Microsoft Sans Serif';
            }
        """)
        
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Space"), self, self.next_player)
        QShortcut(QKeySequence("S"), self, self.mark_sold)
        QShortcut(QKeySequence("U"), self, self.mark_unsold)
        QShortcut(QKeySequence("R"), self, self.reset_player)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Escape"), self, self.exit_fullscreen)
        
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.showMaximized()
        else:
            self.showFullScreen()
            
    def exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.showMaximized()
            
    def load_initial_data(self):
        self.controller.initialize_teams()
        
        row = 0
        col = 0
        teams_data = [
            ("Jakir", "Jakir's Warriors"),
            ("Fayaz", "Fayaz's Kings"),
            ("Sohag", "Sohag's Tigers"),
            ("Sabbir", "Sabbir's Eagles")
        ]
        
        for owner, team_name in teams_data:
            team_widget = TeamWidget(owner, team_name, 20000, self.controller)
            self.team_widgets[owner] = team_widget
            self.teams_grid.addWidget(team_widget, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        self.controller.player_changed.connect(self.on_player_changed)
        self.controller.bid_updated.connect(self.on_bid_updated)
        self.controller.player_sold.connect(self.on_player_sold)
        self.controller.team_updated.connect(self.on_team_updated)
        self.controller.category_changed.connect(self.on_category_changed)
        
        self.next_player()
        
    def on_player_changed(self, player):
        self.player_card.update_player(player)
        animation = QPropertyAnimation(self.player_card, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        self.statusBar().showMessage(f"বর্তমান নিলাম: {player.name} (ক্যাটাগরি {player.category})", 3000)
        
    def on_bid_updated(self, amount, owner):
        self.player_card.update_bid(amount, owner)
        self.statusBar().showMessage(f"{owner} দর দিলেন: ৳{amount:,}", 2000)
        
    def on_player_sold(self, player, price, owner):
        self.statusBar().showMessage(f"{player.name} বিক্রি হয়েছে {owner} এর কাছে ৳{price:,} টাকায়!", 5000)
        
    def on_team_updated(self, team):
        for widget in self.team_widgets.values():
            widget.update_team_info()
            
    def on_category_changed(self, category):
        self.category_label.setText(f"বর্তমান ক্যাটাগরি: {category}")
        
    def next_player(self):
        if not self.controller.has_more_players():
            remaining = self.controller.get_remaining_players_count()
            if remaining == 0:
                QMessageBox.information(self, "নিলাম সম্পন্ন", "সমস্ত খেলোয়াড়ের নিলাম সম্পন্ন হয়েছে!")
                return
        
        player = self.controller.get_next_player_by_category_rotation()
        if player:
            remaining = self.controller.get_remaining_players_count()
            self.remaining_label.setText(f"বাকি খেলোয়াড়: {remaining}")
            self.player_card.update_player(player)
        else:
            QMessageBox.information(self, "নিলাম সম্পন্ন", "আর কোনো খেলোয়াড় নাই!")
            
    def mark_sold(self):
        if self.controller.mark_sold():
            player = self.controller.get_current_player()
            QMessageBox.information(self, "সফল", f"{player.name} বিক্রি হয়েছে {player.sold_to} এর কাছে ৳{player.highest_bid:,} টাকায়!")
            self.update_all_teams()
            self.next_player()
        else:
            QMessageBox.warning(self, "ত্রুটি", "বিক্রি চিহ্নিত করা যাচ্ছে না। বৈধ দর নেই অথবা খেলোয়াড় ইতিমধ্যে প্রক্রিয়াকৃত!")
            
    def mark_unsold(self):
        if self.controller.mark_unsold():
            player = self.controller.get_current_player()
            QMessageBox.information(self, "সফল", f"{player.name} বিক্রি হয়নি হিসেবে চিহ্নিত করা হয়েছে!")
            self.next_player()
        else:
            QMessageBox.warning(self, "ত্রুটি", "বিক্রি হয়নি চিহ্নিত করা যাচ্ছে না!")
            
    def reset_player(self):
        if self.controller.reset_player():
            player = self.controller.get_current_player()
            self.player_card.update_player(player)
            QMessageBox.information(self, "সফল", f"{player.name} রিসেট করা হয়েছে!")
        else:
            QMessageBox.warning(self, "ত্রুটি", "এই খেলোয়াড় রিসেট করা যাবে না (ইতিমধ্যে নিলাম হয়েছে)!")
            
    def update_all_teams(self):
        for team_widget in self.team_widgets.values():
            team_widget.update_team_info()
            
    def export_results(self):
        try:
            filename = self.controller.export_results_to_pdf()
            QMessageBox.information(self, "এক্সপোর্ট সম্পন্ন", f"পিডিএফ রিপোর্ট সফলভাবে তৈরি হয়েছে!\n\nফাইল: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "ত্রুটি", f"রিপোর্ট তৈরি করতে সমস্যা হয়েছে:\n{str(e)}")