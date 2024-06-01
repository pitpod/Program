# -*- coding: utf-8 -*-
import os
import configparser
from configobj import ConfigObj
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5 import QtWidgets as Qw
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDesktopWidget, QMessageBox, QDialog
from Ui_config import Ui_Dialog

class ConfWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ConfWindow, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.tabWidget.setCurrentIndex(0)
        ini_cur_path = os.path.dirname(__file__)
        config_ini = configparser.ConfigParser()
        self.config_ini_path = f"{ini_cur_path}\\config.ini"

        with open(self.config_ini_path, encoding='utf-8') as fp:
            config_ini.read_file(fp)
            database_folder = config_ini['DATA_FOLDER']
            self.database_path = database_folder.get('dbfile')
            color = config_ini['COLOR']
            self.color_B = color.get('color_B')
            self.color_C = color.get('color_C')
            self.color_D = color.get('color_D')
            self.color_E = color.get('color_E')
            self.color_F = color.get('color_F')

        B = (int(self.color_B[2:4],16),int(self.color_B[4:6],16),int(self.color_B[6:8],16))
        C = (int(self.color_C[2:4],16),int(self.color_C[4:6],16),int(self.color_C[6:8],16))
        D = (int(self.color_D[2:4],16),int(self.color_D[4:6],16),int(self.color_D[6:8],16))
        E = (int(self.color_E[2:4],16),int(self.color_E[4:6],16),int(self.color_E[6:8],16))
        F = (int(self.color_F[2:4],16),int(self.color_F[4:6],16),int(self.color_F[6:8],16))

        # ラジオボタンのグループ登録用オブジェクト
        self.radioGroup = QtWidgets.QButtonGroup()
        self.radioGroup.addButton(self.ui.color_week, 1)
        self.radioGroup.addButton(self.ui.color_month, 2)
        self.radioGroup.addButton(self.ui.color_sat, 3)
        self.radioGroup.addButton(self.ui.color_sun, 4)
        self.ui.color_week.setChecked(True)

        self.ui.color_week.clicked.connect(lambda:self.radio_click(D))
        self.ui.color_month.clicked.connect(lambda:self.radio_click(E))
        self.ui.color_sat.clicked.connect(lambda:self.radio_click(B))
        self.ui.color_sun.clicked.connect(lambda:self.radio_click(C))

        self.ui.html_color.setText(self.color_D)
        self.scene = Qw.QGraphicsScene()
        self.ui.graphicsView_1.setScene(self.scene)

        gv = self.ui.graphicsView_1
        self.slider_R1 = self.ui.horizontalSlider_R1
        self.slider_R1.valueChanged.connect(lambda:self.colorValue(gv))

        self.slider_G1 = self.ui.horizontalSlider_G1
        self.slider_G1.valueChanged.connect(lambda:self.colorValue(gv))

        self.slider_B1 = self.ui.horizontalSlider_B1
        self.slider_B1.valueChanged.connect(lambda:self.colorValue(gv))


        brush = QtGui.QBrush(QtGui.QColor(D[0], D[1], D[2]))
        brush.setStyle(QtCore.Qt.SolidPattern)
        gv.setBackgroundBrush(brush)

        """ 設定ファイルを読み込んでカラーセット
            デフォルトは週間
        """
        self.radio_click(D)

        """ データベースフォルダパス読込
        """
        self.ui.pushButton_write.clicked.connect(lambda:self.conf_write())

    def radio_click(self, bcde):
        self.color_radio_id = self.radioGroup.checkedId()
        if self.color_radio_id == 1:
            color_num = self.color_D[2:8]
        elif self.color_radio_id == 2:
            color_num = self.color_E[2:8]
        elif self.color_radio_id == 3:
            color_num = self.color_B[2:8]
        elif self.color_radio_id == 4:
            color_num = self.color_C[2:8]
        self.ui.html_color.setText(color_num)
        self.slider_R1.setValue(bcde[0])
        self.slider_G1.setValue(bcde[1])
        self.slider_B1.setValue(bcde[2])

    def colorValue(self, gv):
        self.gv = gv
        R1 = self.slider_R1.value()
        G1 = self.slider_G1.value()
        B1 = self.slider_B1.value()
        self.ui.lineEdit_R1.setText(str(R1))
        self.ui.lineEdit_G1.setText(str(G1))
        self.ui.lineEdit_B1.setText(str(B1))
        color = (176,224,0)
        html_color = '#%02X%02X%02X' % (color[0],color[1],color[2])
        c = html_color
        color = (int(c[1:3],16),int(c[3:5],16),int(c[5:7],16))
        brush = QtGui.QBrush(QtGui.QColor(R1, G1, B1))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.gv.setBackgroundBrush(brush)
        # brush = QtGui.QBrush(QColor(0, 0, 0))
        # brush.setStyle(QtCore.Qt.SolidPattern)
        # setColor(self.backgroundRole(), QColor('#000'))
        # self.ui.graphicsView.setBackgroundBrush(brush)

    def conf_window(self):
        config_ini = configparser.ConfigParser()
        ini_cur_path = os.path.dirname(__file__)
        self.config_ini_path = f"{ini_cur_path}\\config.ini"
        with open(self.config_ini_path, encoding='utf-8') as fp:
            config_ini.read_file(fp)
            database_folder = config_ini['DATA_FOLDER']
            self.database_path = database_folder.get('dbfile')
        self.ui.lineEdit.setText(self.database_path)
        self.show()

    def conf_write(self):
        data_path = QFileDialog.getExistingDirectory(self, 'データベースフォルダ', os.path.expanduser('~'))
        user_path = os.path.expanduser('~')
        f_path = data_path[len(user_path)+1:]
        if f_path == '':
            pass
        else:
            self.ui.lineEdit.setText(f_path)
            config = ConfigObj(self.config_ini_path, encoding='utf-8')
            config['DATA_FOLDER']['dbfile'] = f_path
            config.write()

    def closeEvent(self, a0: QCloseEvent) -> None:
        return super().closeEvent(a0)
