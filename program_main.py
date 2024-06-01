import sys
import os
from PyQt5 import QtCore, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore as Qc
from PyQt5 import QtGui as Qg
from PyQt5 import QtWidgets as Qw
from Ui_splash import Ui_Splash
from program import Application

# SPLASH SCREE
class Splash(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_Splash()
        self.ui.setupUi(self)
        cur_path = os.path.dirname(__file__)
        logo_path = f'{cur_path}\image\yuyu_logo.png'

        self.view = self.ui.logo_image
        self.scene = Qw.QGraphicsScene()
        self.ui.logo_image.setScene(self.scene)

        # タイマーで app.exec_() が実行された後に MyFuncNext を呼び出し。
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1, lambda:self.logoimage(logo_path))

        # UI ==> INTERFACE CODES
        ########################################################################

        self.ui.dropShadowFrame.setStyleSheet("QFrame {    \n"
"    background-color: rgb(100, 100, 100);    \n"
"    color: rgb(220, 255, 220);\n"
"    border-radius: 10px;\n"
"}")
        # REMOVE TITLE BAR
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # DROP SHADOW EFFECT
        """_summary_
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)
        """

        # QTIMER ==> START
        self.counter = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

        # CHANGE DESCRIPTION

        # Initial Text
        self.ui.label_description.setText("<strong>WELCOME</strong> TO MY APPLICATION")

        # Change Texts
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>LOADING</strong> DATABASE"))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.label_description.setText("<strong>LOADING</strong> USER INTERFACE"))

        # SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        # ==> END ##
    def logoimage(self, im_path):
        self.scene.clear()
        pic_Item = Qw.QGraphicsPixmapItem(Qg.QPixmap(im_path))
        self.scene.addItem(pic_Item)

        self.ui.logo_image.setScene(self.scene)
        self.ui.logo_image.fitInView(self.scene.sceneRect(), Qc.Qt.KeepAspectRatio)
    # ==> APP FUNCTIONS
    ########################################################################
    def progress(self):

        # global counter

        # SET VALUE TO PROGRESS BAR
        self.ui.progressBar.setValue(self.counter)
        # CLOSE SPLASH SCREE AND OPEN APP
        if self.counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = Application()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()
            return self.counter

        # INCREASE COUNTER
        self.counter += 1

def main():
    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon(resource_path('logo.png')))
    cur_path = os.path.dirname(__file__)
    icon_path = f'{cur_path}\image\hr.png'
    app.setWindowIcon(QIcon(icon_path))
    window = Splash()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()