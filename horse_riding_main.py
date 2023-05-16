import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from Ui_splash import Ui_Splash

# SPLASH SCREE
class Splash(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_Splash()
        self.ui.setupUi(self)

        # UI ==> INTERFACE CODES
        ########################################################################

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
    window = Splash()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()