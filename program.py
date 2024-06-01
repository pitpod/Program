# -*- coding: utf-8 -*-
import sys
import os
import calendar
import pandas as pd
import configparser
from configparser import ConfigParser
from pdf_print import ReportlabView
from datetime import datetime, timedelta
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QMessageBox
from view_class import Database, ViewModel
from Ui_main_window import Ui_MainWindow
from config import ConfWindow
from pdf_print import ReportlabView
from program_sub import Subwindow
from reportlab.lib import colors

class Application(QMainWindow):
    def __init__(self, parent=None):
        super(Application, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.pdf = ReportlabView()
        self.sub = Subwindow(self)
        self.conf = ConfWindow(self)
        self.sd = SerialData()

        """ メインウィンドウをセンターに
        """
        desktop_x = QDesktopWidget().availableGeometry().width()
        desktop_y = QDesktopWidget().availableGeometry().height()
        self.ui.lineEdit_year.setText(str(datetime.today().year))
        self.ui.comboBox_month.setCurrentText(str(datetime.today().month))
        self.reload()
        self.ui.hr_times.triggered.connect(lambda:self.sub.hr_times())
        self.ui.config.triggered.connect(lambda:self.conf.conf_window())
        self.ui.reload.triggered.connect(lambda:self.table_data())
        self.ui.print.triggered.connect(lambda:self.pdf.pdf_write(self.chargetext, self.yearNo, self.monthNo, self.riding_name, self.sat, self.sun, self.header2, self.hr_pd.astype(int)))
        self.ui.version.triggered.connect(lambda:self.version("バージョン : 1.0.0"))
        self.ui.comboBox_month.currentIndexChanged.connect(lambda:self.table_data())
        self.ui.comboBox.currentIndexChanged.connect(lambda:self.table_data())
        self.ui.reload_button.clicked.connect(lambda:self.table_data())
        # self.ui.reload_button.clicked.connect(lambda:self.reload())

    def version(self, ms_text):
        """バージョン表示
        Args:
            ms_text (TEXT): バージョン情報の表示
        """
        msgBox = QMessageBox()
        msgBox.setText(ms_text)
        msgBox.setIcon(QMessageBox.Icon.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def reload(self):
        self.read_ini()
        self.table_data()

    def read_ini(self):
        """コンフィグファイルの読込
        """
        cur_month = self.ui.comboBox_month.currentText()
        this_month = str(datetime.today().month)
        if cur_month == this_month:
            cur_month = this_month
        ini_cur_path = os.path.dirname(__file__)
        config_ini = ConfigParser()
        config_ini_path = f"{ini_cur_path}\\config.ini"
        with open(config_ini_path, encoding='utf-8') as fp:
            config_ini.read_file(fp)
            database_class = config_ini['DATABASE_CLASS']
            self.database_name = database_class['database_class_1']
            self.charge_list = config_ini['COMBOBOX_CHARGE']
        charge_name_list = dict(self.charge_list).keys()
        chargetext = self.ui.comboBox.currentText()
        chargeindex = self.ui.comboBox.currentIndex()
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(charge_name_list)
        self.ui.lineEdit_year.setText(str(datetime.today().year))
        if chargetext != '':
            self.ui.comboBox.setCurrentIndex(chargeindex)

    def connectPass(self):
        pass

    def table_data(self):
        """回数チェックテーブルデータの取得
        """
        self.yearNo = self.ui.lineEdit_year.text()
        self.monthNo = self.ui.comboBox_month.currentText()
        self.y_m_d = calendar.monthrange(int(self.yearNo), int(self.monthNo))
        # 月初と月末を取得
        y_m_fd = f'{self.yearNo}/{self.monthNo}/1'
        y_m_ld = f'{self.yearNo}/{self.monthNo}/{self.y_m_d[1]}'
        # 月初のシリアル値
        y_m_fd_No = datetime(int(self.yearNo), int(self.monthNo), 1)
        # 月初の曜日番号
        self.week_num_fd = y_m_fd_No.weekday()
        # 第一週の月曜のシリアル値
        self.firstDayNo = self.sd.excel_serial(y_m_fd)
        self.firstDayNo = self.firstDayNo - self.week_num_fd
        # 月末のシリアル値
        self.lastDayNo = self.sd.excel_serial(y_m_ld)
        ret_pd = []
        sqlStr = f'SELECT name_phonetic, name, riding_horse, date, receipt_number' + \
            f' FROM dayly_log_{self.yearNo}' + \
            f' WHERE date >= {self.firstDayNo} AND date <= {self.lastDayNo} AND riding_horse !="" ' + \
            'ORDER BY name_phonetic IS NULL ASC, name_phonetic, name,date'
        # 事業所別のデータベース設定とプログラム回数の取得用クエリーの設定
        chargename = self.ui.comboBox.currentText()
        self.chargetext = chargename
        if chargename == "ホーシー":
            chargedb = ["dayly-data.db","h_dayly-data.db"]
            sqlstr_hr = 'SELECT receive_no ,times_h FROM program WHERE times_h != 0'
        elif chargename == "児童発達支援":
            chargedb = ["dayly-data.db","h_dayly-data.db"]
            sqlstr_hr = 'SELECT receive_no ,times_h FROM program WHERE times_h != 0'
        elif chargename == "風輪":
            chargedb = ["f_dayly-data.db"]
            sqlstr_hr = 'SELECT receive_no ,times_f FROM program WHERE times_f != 0'
        else:
            QMessageBox.warning(None, "警告", f'"{chargename}"には対応していません。', QMessageBox.Yes)
            return
        # 実施データの取得
        db = Database()
        ret_pd = db.pd_read_attach_query(sqlStr, self.yearNo, chargedb)
        if ret_pd.empty:
            QMessageBox.warning(None, "警告", "当月分のデータがありません。", QMessageBox.Yes)
            return
        self.df = ret_pd.groupby('receipt_number').agg({'name_phonetic':self.name_text,'name':self.name_text, 'date':list})
        self.df = self.df.sort_values('name_phonetic')
        self.df = self.df.drop('name_phonetic', axis=1)
        del db
        # 事業所別プログラム回数の取得
        """
        if chargename == "ホーシー":
            sqlstr_hr = 'SELECT receive_no ,times_h FROM program WHERE times_h != 0'
        elif chargename == "児童発達支援":
            sqlstr_hr = 'SELECT receive_no ,times_h FROM program WHERE times_h != 0'
        elif chargename == "風輪":
            sqlstr_hr = 'SELECT receive_no ,times_f FROM program WHERE times_f != 0'
        """
        hr_times_db = Database(1)
        hr_times_pd = hr_times_db.pd_read_query(sqlstr_hr)
        del hr_times_db

        # プログラム実施リストに無いデータを削除 -----------------------------------------------------
        hr_check_list = hr_times_pd.iloc[:,0].to_list()
        for index2, row in self.df.iterrows():
            if index2 not in hr_check_list:
                self.df = self.df.drop(index=index2)
            else:
                wm = hr_times_pd.query(f'receive_no == "{index2}"')
                # self.df.at[index2,'name'] = f"{row['name']}({wm.iat[0,1]}:{wm.iat[0,2]})"
                self.df.at[index2,'name'] = f"{row['name']}({wm.iat[0,1]})"

        # 先月最終週と今月分のヘッダと列を作成 ----------------------------------------------
        header_serial =[]
        for i in range(self.y_m_d[1] + self.week_num_fd):
            header_serial.append(self.firstDayNo + i)
            self.df[i] = ""
        # 土日の列をリスト化 --------------------------------------------------------------
        self.sat = []
        self.sun = []
        for i in range(1,self.y_m_d[1] + 1):
            temp = datetime(int(self.yearNo), int(self.monthNo), i)
            week_num = temp.weekday()
            if week_num == 5:
                self.sat.append(i + self.week_num_fd)
            elif week_num == 6:
                self.sun.append(i + self.week_num_fd)
        header = ['name','date'] + header_serial
        self.header2 = list(map(self.sd.excel_day, header_serial))
        self.df.columns = header
        # 実施日をマーキング
        row = 0
        riding_day = self.df.iloc[:,1]
        for row, ii in riding_day.items():
            for col in ii:
                prg = ret_pd[(ret_pd['date'] == col) & (ret_pd['receipt_number'] == row)].iloc[:,2]
                prg_split = prg.iloc[-1].split(':')
                self.df.at[row,col] = prg_split[0]

        self.riding_name = self.df.drop('date', axis=1)
        self.hr_pd = pd.DataFrame()
        # hr_times_f = 0
        for index, row in self.riding_name.iterrows():
            hr_times_h = 0
            hr = hr_times_pd.query(f'receive_no == "{index}"')
            if hr.empty:
                times_f = 100
            else:
                hr.reset_index(inplace=True, drop=True)
                times_f = hr.iat[0,1]
                times_h = hr.iat[0,1]

            for colindex, colvalue in row.items():
                if colindex != "name":
                    if colvalue != "":
                        # hr_times_f += 1
                        hr_times_h += 1
                    day = self.sd.excel_date(colindex)
                    self.hr_pd.at[index,colindex] = 0

            tp = row.iat[0].replace('(',f'({hr_times_h}/')
            self.riding_name.replace(row.iat[0],tp, inplace=True)
            if hr_times_h > times_h and times_h != 0:
                for h_day in header_serial:
                    self.hr_pd.at[index,h_day] = -1.0
            elif hr_times_h == times_h and times_h != 0:
                for h_day in header_serial:
                    self.hr_pd.at[index,h_day] = -2.0

        tt = ViewModel(self.ui, self.y_m_d[1], self.week_num_fd, hr_times_h, self.riding_name, self.sat, self.sun, self.header2, self.hr_pd.astype(int))
        self.resize(int(tt.WINDOW_WIDTH*2.8), 800)
        wsize = self.size()
        center = QDesktopWidget().availableGeometry().center()
        center.setX(int(center.x()-wsize.width()/2))
        center.setY(int(center.y()-wsize.height()/2))
        self.move(center)

    def name_text(self, ls):
        return ls.iloc[:1]
class SerialData():
    def excel_date(self, date1):
        temp = datetime(1899, 12, 30)  # Note, not 31st Dec but 30th!
        return(temp + timedelta(days=date1))

    def excel_day(self, date1):
        temp = datetime(1899, 12, 30)  # Note, not 31st Dec but 30th!
        temp_day = temp + timedelta(days=date1)
        # temp_day = temp_day.strftime('%#d')
        temp_day = int(temp_day.strftime('%d'))
        return(temp_day)

    def excel_serial(self, date2):
        date2_sep = date2.split('/')
        day_count = datetime(int(date2_sep[0]), int(date2_sep[1]), int(date2_sep[2]))
        temp = datetime(1899, 12, 30)  # Note, not 31st Dec but 30th!
        return((day_count - temp).days)

def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.abspath('.'), relative)
"""
def re_ini():
    Application.read_ini()
    Application.table_data()
"""
def main():
    app = QApplication(sys.argv)

    cur_path = os.path.dirname(__file__)
    icon_path = f'{cur_path}\image\hr.png'
    app.setWindowIcon(QIcon(icon_path))
    # app.setWindowIcon(QIcon(resource_path('image//logo.png')))
    MainWindow = Application()
    MainWindow.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()