import sys
import os
import pyautogui
from datetime import datetime, timedelta
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy
from Ui_main_window import Ui_MainWindow

class Application(QMainWindow):
    def __init__(self, parent=None):
        super(Application, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

def table_data():
    yearNo = "2023"
    chargeName = "h_"
    firstDayNo = "1"
    lastDayNo = "31"
    sqlStr = f'SELECT name,riding_horse,date,receipt_number FROM dayly_log_{yearNo}' + \
            f' WHERE charge = "{chargeName}" ' + \
            f' AND date >= {firstDayNo} AND date <= {lastDayNo} ORDER BY name_phonetic IS NULL ASC,name_phonetic,name,date'
    pass

def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath('.'), relative)

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path('logo.png')))
    # window = Splash()
    MainWindow = Application()
    MainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()