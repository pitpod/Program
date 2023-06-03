import sys
import os
import pandas as pd
import sqlite3
import configparser
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QAbstractTableModel
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

CURRENT_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

# CHECKBOX Image ---- #
CHECK_IMG = CURRENT_PATH + "/icons/appbar.checkmark.thick.svg"
UNCHECK_IMG = CURRENT_PATH + "/icons/appbar.checkmark.thick.unchecked.svg"

# Painter COLOR ----- #
BACKGROUND_BASE_COLOR_A = QtGui.QColor(255, 255, 255)
BACKGROUND_BASE_COLOR_B = QtGui.QColor(240, 150, 150)
BACKGROUND_BASE_COLOR_C = QtGui.QColor(200, 200, 255)
BACKGROUND_BASE_COLOR_D = QtGui.QColor(255, 230, 230)
BACKGROUND_BASE_COLOR_E = QtGui.QColor(230, 255, 230)
STATUS_FONT_COLOR = QtGui.QColor(255, 255, 255)

BACKGROUND_SELECTED = QtGui.QColor(204, 230, 255)
BACKGROUND_FOCUS = QtGui.QColor(240, 248, 255)

FONT_BASE_COLOR = QtGui.QColor(0, 0, 0)

STATUS_BG_COLOR = {
    Status.WAITING: StatusItem("待機中", QtGui.QColor(0, 0, 205)),
    Status.RUN: StatusItem("実行中", QtGui.QColor(148, 0, 211)),
    Status.FINISH: StatusItem("完了", QtGui.QColor(46, 139, 87)),
    Status.ERROR: StatusItem("エラー", QtGui.QColor(255, 0, 0))
}
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
        headers = ['氏名（週:月）']
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

        col_width_0 = 80
        col_width = 10
        self.ui.tableView.setColumnWidth(0,col_width_0)
        for i in range(1, self.lastdayNo + self.week_num + 1):
            self.ui.tableView.setColumnWidth(i,col_width)
        # window_width = col_width * i + col_width_0
        # self.ui.tableView.setFixedSize(window_width + 200,800)

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
    """
    def editorEvent(self, event, model, option, index):

        if index.column() == 1:
            if self.getCheckBoxRect(option).contains(event.pos().x(), event.pos().y()):
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    currentValue = model.items[index.row()].data(index.column())
                    model.setData(index, not currentValue)
                    return True
        return False

    def createEditor(self, parent, option, index):
        # 編集したいCellに対して、編集用のWidgetsを作成する
        if index.column() == 0:
            return QtWidgets.QLineEdit(parent)

        if index.column() == 2:
            spin = QtWidgets.QSpinBox(parent)
            spin.setMinimum(0)
            spin.setMaximum(100)
            return spin

        if index.column() == 4:
            return QtWidgets.QTextEdit(parent)

    def setEditorData(self, editor, index):

        if index.column() == 0:
            value = index.model().data(index)
            editor.setText(value)

        if index.column() == 2:
            value = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setValue(value)

        if index.column() == 4:
            value = index.model().data(index)
            editor.setText(value)

    def setModelData(self, editor, model, index):

        value = None
        if index.column() == 0:
            value = editor.text()

        if index.column() == 2:
            value = editor.value()

        if index.column() == 4:
            value = editor.toPlainText()

        if value is not None:
            model.setData(index, value)
    """
    def paint(self, painter, option, index):

        # 背景色を指定する
        bgColor = BACKGROUND_BASE_COLOR_A
        if index.column() in self.sun:
            bgColor = BACKGROUND_BASE_COLOR_B
        if index.column() in self.sat:
            bgColor = BACKGROUND_BASE_COLOR_C
        data = index.data()
        # print(index.row())
        # hr_list = self.hr_pd.iloc[1,:].astype('int').to_list()
        # if index.row() in [3, 10, 28]:
        hr_list = self.hr_pd.iloc[index.row(),:].to_list()
        in_col = index.column()
        if index.column() != 0:
            if index.column() in hr_list:
                bgColor = BACKGROUND_BASE_COLOR_D
            if hr_list[0] == -1:
                bgColor = BACKGROUND_BASE_COLOR_E

        # if index.column() >= 10 and index.row() == 2:
        #     bgColor = BACKGROUND_BASE_COLOR_D
        # if (index.row() % 2) != 0:
        #     bgColor = BACKGROUND_BASE_COLOR_B

        # if (index.column() % 2) != 0:
        #    bgColor = BACKGROUND_BASE_COLOR_B

        if option.state & QtWidgets.QStyle.State_Selected:
            bgColor = BACKGROUND_SELECTED
        if option.state & QtWidgets.QStyle.State_HasFocus:
            bgColor = BACKGROUND_FOCUS

        brush = QtGui.QBrush(bgColor)
        painter.fillRect(option.rect, brush)

        #if index.column() in [0, 4]:
        painter.setFont(QtGui.QFont("MS ゴシック", 8))
        painter.setPen(FONT_BASE_COLOR)
        painter.drawText(option.rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, index.data())

        # 各列ごとの表示物を描画する
        """
        if index.column() == 1:
            if data:
                pix = QtGui.QPixmap(CHECK_IMG)
            else:
                pix = QtGui.QPixmap(UNCHECK_IMG)

            rect = self.getCheckBoxRect(option)
            painter.drawPixmap(rect, pix)
        if index.column() == 2:
            bar = QtWidgets.QStyleOptionProgressBar()
            bar.rect = option.rect
            bar.rect.setHeight(option.rect.height() - 1)
            bar.rect.setTop(option.rect.top() + 1)
            bar.minimum = 0
            bar.maximum = 100
            bar.progress = int(data)
            bar.textVisible = True
            bar.text = str(data) + '%'
            bar.textAlignment = QtCore.Qt.AlignCenter
            QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_ProgressBar, bar, painter)

        # Status表示
        if index.column() == 3:
            statusSizeX = 60
            statusSizeY = 20
            brush = QtGui.QBrush(data.color)
            painter.setPen(QtCore.Qt.NoPen)
            rect = QtCore.QRect(option.rect.left() + (option.rect.width() / 2) - (statusSizeX / 2),
                                option.rect.top() + (option.rect.height() / 2) - (statusSizeY / 2),
                                statusSizeX,
                                statusSizeY)
            painter.setBrush(brush)
            painter.drawRoundRect(rect)
            painter.setPen(STATUS_FONT_COLOR)
            painter.setFont(QtGui.QFont("メイリオ", 9))
            painter.drawText(rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, data.name)
    def getCheckBoxRect(self, option, imgSize=30):

        return QtCore.QRect(option.rect.left() + (option.rect.width() / 2) - (imgSize / 2),
                            option.rect.top() + (option.rect.height() / 2) - (imgSize / 2),
                            imgSize,
                            imgSize)
    def sizeHint(self, option, index):

        if index.column() == 1:
            return self.getCheckBoxRect(option).size()

        if index.column() == 2:
            return QtCore.QSize(200, 30)

        if index.column() == 3:
            return QtCore.QSize(90, 30)

        if index.column() == 4:
            document = QtGui.QTextDocument(index.data())
            document.setDefaultFont(option.font)
            return QtCore.QSize(document.idealWidth() + 50, 15 * (document.lineCount() + 1))

        return super(TableDelegate, self).sizeHint(option, index)
    """

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
        # self.database_name = db_name
        self.path = os.path.expanduser('~')
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
            sub_dbpath = f'{self.path}/{self.dbfolder}/{db}'
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