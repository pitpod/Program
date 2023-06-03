import pandas as pd
import calendar
from datetime import datetime
from datetime import date
from datetime import timedelta

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, A3, portrait, landscape
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

class ReportlabView(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

    def pdf_write(self, lastdayNo, week_num, df = [], sat = [], sun = [], header2=[], hr_pd=[]):

        headers = ['氏名']
        headers = headers + header2
        """_summary_
        last = len(hr_pd) - 1
        start_date = hr_pd.iloc[0,0]
        start_date_array = start_date.split("-")
        start_year = start_date_array[0]
        start_month = start_date_array[1]
        start_month_last = calendar.monthrange(int(start_year), int(start_month))[1]

        end_date = hr_pd.iloc[last,0]
        end_date_array = end_date.split("-")
        end_month = end_date_array[1]
        at_record_range = start_month_last - 20 + 20
        self.dt = date(int(start_year), int(start_month), 21)
        date_list = []
        columns1 = ["日付", "出勤", "退勤", "休憩", "就業時間", "備考"]
        total_wt = 0

        for i in range(at_record_range):
            date_key = f'{self.dt}'
            d_t = pd.to_datetime(date_key)
            week_day = self.get_day_of_week_jp(d_t)
            date_time = d_t.strftime('%#d日')
            df_array = hr_pd.query('日付 == @date_key')
            if hr_pd.query('日付 == @date_key').empty == False:
                s_t = pd.to_datetime(df_array.at[df_array.index[0],"出勤"])
                start_time = s_t.strftime('%#H:%M')
                e_t = pd.to_datetime(df_array.at[df_array.index[0],"退勤"])
                end_time = e_t.strftime('%#H:%M')
                rest_time = df_array.at[df_array.index[0],"休憩"]
                rt = timedelta(minutes=int(rest_time))
                wt = pd.to_datetime(df_array.at[df_array.index[0],'退勤']) - pd.to_datetime(df_array.at[df_array.index[0],'出勤'])
                wt = wt.seconds - rt.seconds
                total_wt = total_wt + wt
                work_time = self.get_h_m_s(wt)
                remarks = df_array.at[df_array.index[0],"備考"]
                if str(remarks) == "nan":
                    remarks = ""
                list_row = [f'{date_time}{week_day}', f'{start_time}', f'{end_time}', f'{rest_time}', work_time , remarks]
            else:
                list_row = [f'{date_time}{week_day}', "", "", "", "", ""]
            date_list.append(list_row)
            self.dt = self.dt + timedelta(days=1)
        """
        # hr_pd_full = pd.DataFrame(data=df, columns=headers)
        # hr_pd_full['承認'] = ""
        row_len = len(df)
        hr_pd_full = df
        hr_pd_full.columns = headers
        row_count = int((210 - 10) / 7)
        pages = int(row_len / row_count)
        if (row_len % row_count) != 0:
            pages = pages + 1
        for i in range(pages):
            print(i)
        hr_pd_1p = hr_pd_full.iloc[:row_count,:]
        hr_pd_pdf_1p = hr_pd_1p.T.reset_index().T.values.tolist()

        hr_pd_2p = hr_pd_full.iloc[(row_count + 1):row_count*2 + 1,:]
        hr_pd_pdf_2p = hr_pd_2p.T.reset_index().T.values.tolist()

        # 縦型A4のCanvasを準備
        save_pdfname = QFileDialog.getSaveFileName(self, 'Save File', '')
        save_pdfpass = save_pdfname[0]
        cv = canvas.Canvas(save_pdfpass, pagesize=landscape(A4))
        # cv = canvas.Canvas(save_pdfpass, pagesize=portrait(A4))
        # フォント登録
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
        col_len = len(hr_pd_1p.columns)
        col_width = [25*mm]
        for n in range(col_len - 1):
            col_width.append(7*mm)
        bg_sat = []
        bg_sun = []
        bg_hr = []

        self.table = self.pdf_table(sat, sun, hr_pd, hr_pd_pdf_1p, col_width, row_count)
        # --------------------------------------------------------------------------------------------------------
        """
        table = Table(hr_pd_pdf_1p, colWidths= col_width, rowHeights=7*mm)
        # table = Table(hr_pd_pdf, colWidths=25*mm, rowHeights=5*mm)
        idx = 1
        hr_pd_1 = hr_pd.iloc[:row_count,:]
        for index, row in hr_pd_1.iterrows():
            for col in row:
                if col != 0:
                    bg_hr.append(('BACKGROUND', (col, idx), (col, idx), colors.CMYKColor(0,0,0.3,0)))
            idx += 1

        for i in sat:
            bg_sat.append(('BACKGROUND', (i, 0), (i, -1), colors.CMYKColor(0.3,0,0,0)))

        for i in sun:
            bg_sun.append(('BACKGROUND', (i, 0), (i, -1), colors.CMYKColor(0,0.3,0,0)))

        style = [
            ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 10), # フォント
            ('BOX', (0, 0), (-1, -1), 1, colors.black),       # 罫線
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBEFORE', (1, 0), (-1, 0), 0.5, colors.black),
            ('INNERGRID', (0, 1), (-1, -1), 0.5 , colors.black),
            ('WIDTH', (1,0), (1, -1), 10*mm),
            ('ALIGN', (1,0), (-1, -1), 'CENTER'),
            ('ALIGN', (0,0),(0,0), 'CENTER')
        ]
        style = style + bg_sat + bg_sun + bg_hr
        table.setStyle(TableStyle(style))
        """
        # -----------------------------------------------------------------------------
        origin = 210 -10 - 7*(len(hr_pd_1p))
        # origin = 297 -10 - 5*(len(hr_pd_full))
        self.table.wrapOn(cv, 10*mm, origin*mm) # table位置
        self.table.drawOn(cv, 10*mm, origin*mm)

        # 線の太さ
        cv.setLineWidth(1)
        # 線を描画(始点x、始点y、終点x、終点y)
        # フォントサイズ定義
        font_size = 12
        cv.setFont('HeiseiKakuGo-W5', font_size)

        cv.line(65*mm, 286*mm, 145*mm, 286*mm)
        # sheet_title = f"タイムシート期間:{start_month}月21日~{end_month}月20日"
        # cv.drawString(65*mm, (286 + 1)*mm, sheet_title)
        """
        line_start = 278
        line_height = 7
        all_time = '就業時間(全時間):'
        line_title = ['氏名：松本幸治',
                      '就業先会社名：所属会社名：株式会社ながさきUUカンパニー',
                      '就業先担当者：',
                      f'{all_time}{self.get_h_m_s(total_wt)}']
        for i in range(4):
            cv.line(10*mm, line_start*mm, 130*mm, line_start*mm)
            cv.drawString(10*mm, (line_start + 1)*mm, f'{line_title[i]}')
            line_start = line_start - line_height
        """
        # --------------------------------------------------------------------------------------------------------

        # 保存
        cv.showPage()
        # --------------------------------------------------------------------------------------------------------
        table = Table(hr_pd_pdf_2p, colWidths= col_width, rowHeights=7*mm)
        idx = 1
        hr_pd_2 = hr_pd.iloc[(row_count + 1):row_count*2 + 1,:]
        bg_hr = []
        for index, row in hr_pd_2.iterrows():
            for col in row:
                if col != 0:
                    bg_hr.append(('BACKGROUND', (col, idx), (col, idx), colors.CMYKColor(0,0,0.3,0)))
            idx += 1

        for i in sat:
            bg_sat.append(('BACKGROUND', (i, 0), (i, -1), colors.CMYKColor(0.3,0,0,0)))

        for i in sun:
            bg_sun.append(('BACKGROUND', (i, 0), (i, -1), colors.CMYKColor(0,0.3,0,0)))

        style = [
            ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 10), # フォント
            ('BOX', (0, 0), (-1, -1), 1, colors.black),       # 罫線
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBEFORE', (1, 0), (-1, 0), 0.5, colors.black),
            ('INNERGRID', (0, 1), (-1, -1), 0.5 , colors.black),
            ('WIDTH', (1,0), (1, -1), 10*mm),
            ('ALIGN', (1,0), (-1, -1), 'CENTER'),
            ('ALIGN', (0,0),(0,0), 'CENTER')
        ]
        style = style + bg_sat + bg_sun + bg_hr
        table.setStyle(TableStyle(style))
        origin = 210 -10 - 7*(len(hr_pd_2p))
        # origin = 297 -10 - 5*(len(hr_pd_full))
        table.wrapOn(cv, 10*mm, origin*mm) # table位置
        table.drawOn(cv, 10*mm, origin*mm)

        # 線の太さ
        cv.setLineWidth(1)
        # 線を描画(始点x、始点y、終点x、終点y)
        # フォントサイズ定義
        font_size = 12
        cv.setFont('HeiseiKakuGo-W5', font_size)

        cv.line(65*mm, 286*mm, 145*mm, 286*mm)
        # --------------------------------------------------------------------------------------------------------

        cv.save()

        msgBox = QMessageBox()
        msgBox.setText("書き出しました")
        msgBox.setIcon(QMessageBox.Icon.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def pdf_table(self, sat, sun, hr_pd, hr_pd_pdf_1p, col_width, row_count):
        bg_sat = []
        bg_sun = []
        bg_hr = []
        # --------------------------------------------------------------------------------------------------------
        table = Table(hr_pd_pdf_1p, colWidths= col_width, rowHeights=7*mm)
        # table = Table(hr_pd_pdf, colWidths=25*mm, rowHeights=5*mm)
        idx = 1
        hr_pd_1 = hr_pd.iloc[:row_count,:]
        for index, row in hr_pd_1.iterrows():
            for col in row:
                if col != 0:
                    bg_hr.append(('BACKGROUND', (col, idx), (col, idx), colors.CMYKColor(0,0,0.3,0)))
            idx += 1

        for i in sat:
            bg_sat.append(('BACKGROUND', (i, 0), (i, -1), colors.CMYKColor(0.3,0,0,0)))

        for i in sun:
            bg_sun.append(('BACKGROUND', (i, 0), (i, -1), colors.CMYKColor(0,0.3,0,0)))

        style = [
            ('FONT', (0, 0), (-1, -1), 'HeiseiKakuGo-W5', 10), # フォント
            ('BOX', (0, 0), (-1, -1), 1, colors.black),       # 罫線
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBEFORE', (1, 0), (-1, 0), 0.5, colors.black),
            ('INNERGRID', (0, 1), (-1, -1), 0.5 , colors.black),
            ('WIDTH', (1,0), (1, -1), 10*mm),
            ('ALIGN', (1,0), (-1, -1), 'CENTER'),
            ('ALIGN', (0,0),(0,0), 'CENTER')
        ]
        style = style + bg_sat + bg_sun + bg_hr
        table.setStyle(TableStyle(style))
        return table