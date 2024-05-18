# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import sqlite3
import configparser
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QColor
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from reportlab.lib.units import mm
from enum import IntEnum, auto

class Status(IntEnum):
    WAITING = auto()
    RUN = auto()
    FINISH = auto()
    ERROR = auto()

class StatusItem:
    def __init__(self, name, color):
        self.name = name
        self.color = color

""" iniファイル読込
"""
ini_cur_path = os.path.dirname(__file__)
config_ini = configparser.ConfigParser()
config_ini_path = f"{ini_cur_path}\\config.ini"
with open(config_ini_path, encoding='utf-8') as fp:
    config_ini.read_file(fp)
    color = config_ini['COLOR']
    color_B = color.get('color_B')
    color_C = color.get('color_C')
    color_D = color.get('color_D')
    color_E = color.get('color_E')
    color_F = color.get('color_F')

# Painter COLOR ----- #
color_A = (33, 255, 255, 255)
html_color = '#%02X%02X%02X%02X' % (color_A[0],color_A[1],color_A[2],color_A[3])
BACKGROUND_BASE_COLOR_A = QColor(html_color)
# color_B = (247, 201, 221)
# html_color = '#%02X%02X%02X' % (color_B[0],color_B[1],color_B[2])
BACKGROUND_BASE_COLOR_B = QColor(f'#{color_B}')
# color_C = (186, 227, 249)
# html_color = '#%02X%02X%02X' % (color_C[0],color_C[1],color_C[2])
BACKGROUND_BASE_COLOR_C = QColor(f'#{color_C}')
# color_D = (255, 251, 199)
# html_color = '#%02X%02X%02X' % (color_D[0],color_D[1],color_D[2])
BACKGROUND_BASE_COLOR_D = QColor(f'#{color_D}')
# BACKGROUND_BASE_COLOR_E = QtGui.QColor(190, 223, 194)
# color_E = (190, 223, 194)
# html_color = '#%02X%02X%02X' % (color_E[0],color_E[1],color_E[2])
BACKGROUND_BASE_COLOR_E = QColor(f'#{color_E}')

BACKGROUND_BASE_COLOR_F = QColor(f'#{color_F}')

STATUS_FONT_COLOR = QColor(255, 255, 255, 160)

BACKGROUND_SELECTED = QColor(204, 230, 255)
BACKGROUND_FOCUS = QColor(240, 248, 255)

FONT_BASE_COLOR = QColor(0, 0, 0)

class ViewModel():
    def __init__(self, ui, lastdayNo, week_num, hr_times_month, df = [], sat = [], sun = [], header2=[], hr_pd=[]) -> None:
        self.df = df
        self.sat = sat
        self.sun = sun
        self.header2 = header2
        self.hr_pd = hr_pd
        self.col_list = self.hr_pd.columns.to_list()
        self.lastdayNo = lastdayNo
        self.week_num = week_num
        self.hr_times_month = hr_times_month
        self.ui = ui
        self.tableview()

    def tableview(self):
        headers = ['氏名（実施:上限）']
        # for i in range(1, self.lastdayNo + 1):
        #     headers.append(i)
        headers = headers + self.header2
        tableData0 = self.df.to_numpy()
        self.delegate = TableDelegate(self.sat, self.sun, self.week_num, self.hr_pd)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.ui.tableView.setFont(font)
        self.ui.tableView.setItemDelegate(self.delegate)
        model = MyTableModel(tableData0, headers)
        self.ui.tableView.setModel(model)

        pol = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pol.setHorizontalStretch(1)
        self.ui.tableView.setSizePolicy(pol)

        col_width_0 = 100
        col_width = 10
        self.ui.tableView.setColumnWidth(0,col_width_0)
        for i in range(1, self.lastdayNo + self.week_num + 1):
            self.ui.tableView.setColumnWidth(i,col_width)
        window_width = col_width * i + col_width_0
        # self.ui.tableView.setFixedSize(window_width + 200, 800)

class MyTableModel(QAbstractTableModel):
    def __init__(self, list, headers = [], parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.list = list
        self.headers = headers

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        return len(self.list[0])

    def flags(self, index):
        if index.column() == 6:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            return self.list[row][column]

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.list[row][column]
            return value

    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            self.list[row][column] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.headers):
                    return self.headers[section]
                else:
                    return "not implemented"
            else:
                # return "%d" % section
                return f'{section + 1}'

class TableDelegate(QtWidgets.QItemDelegate):

    def __init__(self, sat, sun, week_num, hr_pd, parent=None):
        super(TableDelegate, self).__init__(parent)
        self.sun = sun
        self.sat = sat
        self.week_num = week_num
        self.hr_pd = hr_pd
        # self.hr_pd = pd.DataFrame()

    def paint(self, painter, option, index):
        # 背景色を指定する
        bgColor = BACKGROUND_BASE_COLOR_A
        data = index.data()
        hr_list = self.hr_pd.iloc[index.row(),:].to_list()
        in_col = index.column()
        if index.column() != 0:
            if index.column() in hr_list:
                bgColor = BACKGROUND_BASE_COLOR_D
            if hr_list[0] == -1:
                bgColor = BACKGROUND_BASE_COLOR_E
            if hr_list[0] == -2:
                bgColor = BACKGROUND_BASE_COLOR_F

        if option.state & QtWidgets.QStyle.State_Selected:
            bgColor = BACKGROUND_SELECTED

        if option.state & QtWidgets.QStyle.State_HasFocus:
            bgColor = BACKGROUND_FOCUS

        # 土日色設定
        if index.column() in self.sun:
            bgColor = BACKGROUND_BASE_COLOR_B
        if index.column() in self.sat:
            bgColor = BACKGROUND_BASE_COLOR_C

        brush = QtGui.QBrush(bgColor)
        painter.fillRect(option.rect, brush)

        #if index.column() in [0, 4]:
        painter.setFont(QtGui.QFont("MS ゴシック", 8))
        painter.setPen(FONT_BASE_COLOR)
        painter.drawText(option.rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, index.data())

class Database():
    def __init__(self, db_name="") -> None:
        ini_cur_path = os.path.dirname(__file__)
        config_ini = configparser.ConfigParser()
        config_ini_path = f"{ini_cur_path}\\config.ini"
        with open(config_ini_path, encoding='utf-8') as fp:
            config_ini.read_file(fp)
            database_ini = config_ini['DATA_FOLDER']
            self.dbfolder = database_ini.get('dbfile')
            database_class = config_ini['DATABASE_CLASS']
            self.database_list = database_class.get('database').split(",")
            self.database_name = database_class.get('database_class_1')
        self.path = os.path.expanduser('~')
        ch_path = f'{self.path}/{self.dbfolder}'
        if os.path.isdir(ch_path) == False:
            self.dbfolder = "Dropbox/yuyu-farm/data"

        if db_name != "":
            self.dbpath = f'{self.path}/{self.dbfolder}/{self.database_name}'
            self.conn = sqlite3.connect(self.dbpath)
            self.cur = self.conn.cursor()

    def pd_read_query(self, sql_text):
        self.sql_text = sql_text
        self.df = pd.read_sql_query(sql=self.sql_text, con=self.conn)
        return self.df

    def pd_read_attach_query(self, sql_text, table_name, databases=[]):
        df_0 = []
        for db in self.database_list:
            sub_dbpath = f'{self.path}/{self.dbfolder}/{db.strip()}'
            self.conn = sqlite3.connect(sub_dbpath)
            self.cur = self.conn.cursor()
            check_sql = f"select * from sqlite_master where type='table'"
            self.cur.execute(check_sql)
            for row in self.cur.fetchall():
                if f'dayly_log_{table_name}' in row:
                    self.sql_text = sql_text
                    self.df = pd.read_sql_query(sql=self.sql_text, con=self.conn)
                    df_0.append(self.df)
            self.cur.close()
            self.conn.close()
        df_concat = pd.concat(df_0)
        return df_concat

    def database_write(self, sql_str):
        self.sql_str = sql_str
        self.cur.execute(self.sql_str)
        self.conn.commit()

    def database_fech(self, sql_str):
        self.sql_str = sql_str
        self.cur.execute(self.sql_str)
        self.conn.commit()
        if self.cur.fetchone() == None:
            fe =  False
        else:
            fe =  True
        return fe

    def tables(self, sql_str):
        self.sql_str = sql_str
        self.cur.execute(self.sql_str)
        return self.cur.fetchall()

    def __delattr__(self, __name: str) -> None:
        self.cur.close()
        self.conn.close()