# Cricket Player Auction System 🏏

একটি সম্পূর্ণ ডেস্কটপ অ্যাপ্লিকেশন যা ক্রিকেট টুর্নামেন্টের জন্য খেলোয়াড় নিলাম পরিচালনা করে। সুজাপুর টুর্নামেন্টের জন্য বিশেষভাবে ডিজাইন করা।

## 📌 Overview

This application provides a complete solution for managing cricket player auctions with an intuitive interface, real-time bidding system, and comprehensive reporting features. Perfect for local tournaments, club auctions, and cricket league management.

## 🎯 Key Features

- **Multi-Category System**: Players categorized into A, B, C, D with different base prices
- **4-Team Management**: Complete team budget tracking and player purchase history
- **Real-time Bidding**: Live bid updates with automatic increment rules
- **PDF Reports**: Generate professional auction reports with all details
- **Image Support**: Display player photos with automatic scaling
- **Keyboard Shortcuts**: Full keyboard control for faster auction management
- **Data Persistence**: Automatic save/load of auction state
- **Fullscreen Mode**: Optimized for projector/large screen display

## 🏗️ Architecture

- **Frontend**: PyQt5 for modern GUI
- **Backend**: Python for business logic
- **Database**: JSON-based lightweight storage
- **Reporting**: ReportLab for PDF generation

## 🎮 Auction Process

1. **Category Rotation**: A → B → C → D → A (fair distribution)
2. **Bid Rules**: Minimum increment of 50 or 10% of current bid
3. **Budget Management**: Teams can't exceed their allocated budget
4. **Auction History**: Complete record with timestamps

## 💻 Technical Stack

- **Language**: Python 3.8+
- **GUI Framework**: PyQt5
- **PDF Generation**: ReportLab
- **Data Storage**: JSON
- **Build Tool**: PyInstaller

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/cricket-auction-system.git

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
