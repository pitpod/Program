import sys
import pandas as pd
import sqlite3
import os
from view_class import MyTableModel, Database, ViewModel
from Ui_name_list import Ui_riding_list_window
from Ui_riding_times import Ui_SubWindow

class name_list():
    def __init__(self, parent=None):
        #self.sb = Ui_SubWindow()
        #self.sb.setupUi(self)
        pass

    def hr_times(self):
        hr_times_db = Database("name_list-3.db")
        sqlStr = "SELECT DISTINCT rn.receive_no, rn.name FROM receipt_number as rn LEFT OUTER JOIN horse_riding as hr ON hr.receive_no = rn.receive_no ORDER BY rn.name_phonetic ASC"
        ret_hr_times = hr_times_db.pd_read_query(sqlStr)
        print(ret_hr_times)