import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui import AuctionUI

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application-wide attributes
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    window = AuctionUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()