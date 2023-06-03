#!python3
# -*- coding: utf-8 -*-

import sys
import os.path

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader
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
BACKGROUND_BASE_COLOR_B = QtGui.QColor(240, 240, 240)
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


# 列ごとに表示するItem
class DataItem(object):

    def __init__(self, name="",
                 check=False,
                 progress=0,
                 status=Status.WAITING,
                 comment=""):

        self.name = name
        self.check = check
        self.progess = progress
        self.status = status
        self.comment = comment

    def data(self, column):
        if column == 0:
            return self.name
        elif column == 1:
            return self.check
        elif column == 2:
            return self.progess
        elif column == 3:
            return STATUS_BG_COLOR[self.status]
        elif column == 4:
            return self.comment

    def setData(self, column, value):

        if column == 0:
            self.name = value
        elif column == 1:
            self.check = value
        elif column == 2:
            self.progess = value
        elif column == 3:
            self.status = value
        elif column == 4:
            self.comment = value


class TableDelegate(QtWidgets.QItemDelegate):

    def __init__(self, parent=None):
        super(TableDelegate, self).__init__(parent)

    def editorEvent(self, event, model, option, index):

        if index.column() == 1:
            if self.getCheckBoxRect(option).contains(event.pos().x(), event.pos().y()):
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    currentValue = model.items[index.row()].data(index.column())
                    model.setData(index, not currentValue)
                    return True
        return False

    def createEditor(self, parent, option, index):
        """
        編集したいCellに対して、編集用のWidgetsを作成する
        """
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

    def paint(self, painter, option, index):

        # 背景色を指定する
        data = index.data()

        bgColor = BACKGROUND_BASE_COLOR_A
        if (index.row() % 2) != 0:
            bgColor = BACKGROUND_BASE_COLOR_B

        if option.state & QtWidgets.QStyle.State_Selected:
            bgColor = BACKGROUND_SELECTED
        if option.state & QtWidgets.QStyle.State_HasFocus:
            bgColor = BACKGROUND_FOCUS

        brush = QtGui.QBrush(bgColor)
        painter.fillRect(option.rect, brush)

        if index.column() in [0, 4]:
            painter.setFont(QtGui.QFont("メイリオ", 9))
            painter.setPen(FONT_BASE_COLOR)
            painter.drawText(option.rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, index.data())

        # 各列ごとの表示物を描画する
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


class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)
        self.items = []

    def headerData(self, col, orientation, role):

        HEADER = ['名前', 'チェック', '進行状況', 'ステータス', '備考']

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return HEADER[col]

        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return str(col + 1).zfill(3)

    def addItem(self, item):

        self.items.append(item)
        self.layoutChanged.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        u"""行数を返す"""
        return len(self.items)

    def columnCount(self, parent):
        u"""カラム数を返す"""
        return 5

    def setData(self, index, value, role=QtCore.Qt.EditRole):

        if role == QtCore.Qt.EditRole:
            index.data(QtCore.Qt.UserRole).setData(index.column(), value)
            self.headerDataChanged.emit(QtCore.Qt.Vertical, index.row(), index.row())
            self.dataChanged.emit(index, index)

    def data(self, index, role=QtCore.Qt.DisplayRole):

        if not index.isValid():
            return None

        if role == QtCore.Qt.DisplayRole:
            return self.items[index.row()].data(index.column())

        if role == QtCore.Qt.UserRole:
            return self.items[index.row()]

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled


class UISample(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(UISample, self).__init__(parent)

        self.tableView = QtWidgets.QTableView()
        self.setCentralWidget(self.tableView)

        self.model = TableModel()
        self.tableView.setModel(self.model)
        self.delegate = TableDelegate()
        self.tableView.setItemDelegate(self.delegate)

        # CellのサイズをSizeHintの値で固定する
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # Tableに表示したいオブジェクトを登録
        dataA = DataItem('AAAA', False, 0, Status.WAITING, 'ほげほげほげほげほげほげ\nふがふがふが\nほむほむほむ')
        dataB = DataItem('BBBB', False, 0, Status.FINISH, 'てすとてすと')
        dataC = DataItem('CCCC', False, 0, Status.ERROR, 'はろーはろー')
        dataD = DataItem('DDDD', False, 0, Status.RUN, 'ーーーーーーー')
        self.model.addItem(dataA)
        self.model.addItem(dataB)
        self.model.addItem(dataC)
        self.model.addItem(dataD)

        self.resize(800, 400)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    a = UISample()
    a.show()
    sys.exit(app.exec_())
