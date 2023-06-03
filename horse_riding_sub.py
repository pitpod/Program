import sys
import pandas as pd
from PyQt5  import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy
from PyQt5.QtWidgets import  QDesktopWidget, QMessageBox, QDialog
from view_class import MyTableModel, Database, ViewModel
from view_class import Database
from Ui_name_list import Ui_riding_list_window
# from Ui_riding_times import Ui_SubWindow
class Subwindow(QMainWindow):
    def __init__(self, parent=None):
        super(Subwindow, self).__init__(parent)
        self.ui = Ui_riding_list_window()
        self.ui.setupUi(self)
        self.ui.writeButton.clicked.connect(self.check_data)

    def hr_times(self):
        self.show()
        hr_times_db = Database(1)
        sqlStr = "SELECT DISTINCT rn.receive_no, rn.name, rn.name_phonetic, hr.weekly, hr.monthly FROM receipt_number as rn LEFT OUTER JOIN horse_riding as hr ON hr.receive_no = rn.receive_no ORDER BY rn.name_phonetic ASC"
        ret_hr_times = hr_times_db.pd_read_query(sqlStr)
        self.vm = ViewModel(self.ui, ret_hr_times)

    def check_data(self):
        if not self.vm.wr_list:
            msg = QMessageBox()
            msg.setWindowTitle("メッセージボックス")
            msg.setText("変更がありません")
            msg.setStandardButtons(QMessageBox.Ok)
            x = msg.exec_()
        else:
            self.write_data()

    def write_data(self):
        hr_times_db = Database("name_list-3.db")
        hr_df = pd.DataFrame(self.vm.wr_list)
        hr_times_df = hr_df.drop(hr_df.columns[[1, 2]], axis=1)
        for col, row in hr_times_df.iterrows():
            re_no = row.iat[0]
            re_weekly = row.iat[1]
            if str(re_weekly) == "nan":
                re_weekly = 0
            re_monthly = row.iat[2]
            if str(re_monthly) == "nan":
                re_monthly = 0
            sqlstr = f'SELECT receive_no FROM horse_riding WHERE receive_no = "{re_no}"'
            ret = hr_times_db.database_fech(sqlstr)
            if re_weekly != 0 or re_monthly != 0:
                if ret:
                    sqlstr = f'UPDATE horse_riding SET weekly = {re_weekly}, monthly = {re_monthly} WHERE receive_no = "{re_no}"'
                    hr_times_db.database_write(sqlstr)
                else:
                    sqlstr = f'INSERT INTO horse_riding(receive_no, weekly, monthly) VALUES("{re_no}",{re_weekly}, {re_monthly})'
                    hr_times_db.database_write(sqlstr)
            else:
                if ret:
                    sqlstr = f'DELETE FROM horse_riding WHERE receive_no = "{re_no}"'
                    hr_times_db.database_write(sqlstr)

class ViewModel():
    def __init__(self, ui, df = []) -> None:
        self.df = df
        # self.sat = sat
        # self.sun = sun
        # self.header2 = header2
        # self.hr_pd = hr_pd
        # self.col_list = self.hr_pd.columns.to_list()
        # self.lastdayNo = lastdayNo
        # self.week_num = week_num
        self.ui = ui
        self.tableview()

    def tableview(self):
        headers = ['受給者番号','名前','なまえ', '週', '月']
        tableData0 = self.df.to_numpy()
        # self.delegate = TableDelegate(self.sat, self.sun, self.week_num, self.hr_pd)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.ui.tableView_name.setFont(font)
        # self.ui.tableView_name.setItemDelegate(self.delegate)
        self.wr_list = []
        model = MyTableModel(tableData0, headers, self.wr_list)
        self.ui.tableView_name.setModel(model)

        pol = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        pol.setHorizontalStretch(0)
        self.ui.tableView_name.setSizePolicy(pol)

        col_width_0 = 0
        col_width = 40
        # self.ui.tableView_name.setColumnWidth(0,col_width_0)
        for i in range(5):
            if i <= 2:
                col_width = 80
            else:
                col_width = 40
            self.ui.tableView_name.setColumnWidth(i,col_width)
            col_width_0 = col_width_0 + col_width
        # window_width = col_width * i + col_width_0
        # self.ui.tableView_name.setFixedSize(col_width_0,800)

class MyTableModel(QAbstractTableModel):
    def __init__(self, list, headers = [], write_list = [], parent = None):
        QAbstractTableModel.__init__(self, parent)
        self.list = list
        self.headers = headers
        self.write_list = write_list

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
            value = self.list[row][column]
            if str(value) == "nan":
                value = 0
            if column >= 3:
                value = int(value)
            return value
            # return self.list[row][column]

        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            value = self.list[row][column]
            if str(value) == "nan":
                value = 0
            if column >= 3:
                value = int(value)
            return value

    def setData(self, index, value, role = Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            self.list[row][column] = value
            self.dataChanged.emit(index, index)
            self.write_list.append(self.list[row])
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


def main():
    app = QApplication(sys.argv)
    SubWindow = Subwindow()
    SubWindow.show()

    """ メインウィンドウをセンターに
    """
    wsize = SubWindow.size()
    center = QDesktopWidget().availableGeometry().center()
    center.setX(int(center.x()-wsize.width()/2))
    center.setY(int(center.y()-wsize.height()/2))
    SubWindow.move(center)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()