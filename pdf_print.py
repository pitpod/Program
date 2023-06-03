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
        self.sat = sat
        self.sun = sun

        headers = ['氏名（週:月）']
        headers = headers + header2
        hr_pd_full = df
        hr_pd_full.columns = headers

        nu_lines = int((210 - 10) / 7)  # 1ページの行数
        row_len = len(df)               # 総行数

        # ページ数 ---------------------------------
        pages = int(row_len / nu_lines)
        if (row_len % nu_lines) != 0:
            pages = pages + 1
        # ------------------------------------------

        # 縦型A4のCanvasを準備
        save_pdfname = QFileDialog.getSaveFileName(self, 'Save File', '')
        save_pdfpass = save_pdfname[0]
        self.cv = canvas.Canvas(save_pdfpass, pagesize=landscape(A4))
        # cv = canvas.Canvas(save_pdfpass, pagesize=portrait(A4))
        # フォント登録
        pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

        # 列幅を設定 ------------------------------------------------------
        # col_len = len(hr_pd_full.columns)
        col_len = len(headers)
        col_width = [35*mm]
        for n in range(col_len - 1):
            col_width.append(7*mm)
        # ----------------------------------------------------------------

        for i in range(pages):
            if i == 0:
                hr_1p = hr_pd_full.iloc[:nu_lines,:]
                hr_pdf_1p = hr_1p.T.reset_index().T.values.tolist()
                hr_times_1p = hr_pd.iloc[:nu_lines,:]
                self.table = self.pdf_table(hr_times_1p, hr_1p, hr_pdf_1p, col_width, nu_lines)
            elif i == pages:
                self.cv.showPage()
                hr_2p = hr_pd_full.iloc[nu_lines*(i + 1) + 1:,:]
                hr_pdf_2p = hr_2p.T.reset_index().T.values.tolist()
                hr_times_2p = hr_pd.iloc[nu_lines*(i + 1) + 1:,:]
                self.table = self.pdf_table(hr_times_2p, hr_2p, hr_pdf_2p, col_width, nu_lines)
            else:
                self.cv.showPage()
                hr_3p = hr_pd_full.iloc[(nu_lines*i + 1):nu_lines*(i + 1) + 1,:]
                hr_pdf_3p = hr_3p.T.reset_index().T.values.tolist()
                hr_times_3p = hr_pd.iloc[(nu_lines*i + 1):nu_lines*(i + 1) + 1,:]
                self.table = self.pdf_table(hr_times_3p, hr_3p, hr_pdf_3p, col_width, nu_lines)

        # -----------------------------------------------------------------------------

        # 線の太さ
        self.cv.setLineWidth(1)
        # 線を描画(始点x、始点y、終点x、終点y)
        # フォントサイズ定義
        font_size = 12
        self.cv.setFont('HeiseiKakuGo-W5', font_size)

        self.cv.line(65*mm, 286*mm, 145*mm, 286*mm)

        # 保存
        self.cv.save()

        msgBox = QMessageBox()
        msgBox.setText("書き出しました")
        msgBox.setIcon(QMessageBox.Icon.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()

    def pdf_table(self, hr_pd_times, hr_pd_p, hr_pd_pdf_1p, col_width, nu_lines):
        bg_sat = []
        bg_sun = []
        bg_hr = []
        # --------------------------------------------------------------------------------------------------------
        table = Table(hr_pd_pdf_1p, colWidths= col_width, rowHeights=7*mm)
        # table = Table(hr_pd_pdf, colWidths=25*mm, rowHeights=5*mm)
        idx = 1
        hr_pd_p = hr_pd_times.iloc[:nu_lines,:]
        for index, row in hr_pd_p.iterrows():
            for col in row:
                if col != 0:
                    bg_hr.append(('BACKGROUND', (col, idx), (col, idx), colors.CMYKColor(0,0,0.3,0)))
                if col == -1:
                    bg_hr.append(('BACKGROUND', (1, idx), (-1, idx), colors.CMYKColor(0.3,0,0.3,0)))
            idx += 1

        for i in self.sat:
            bg_sat.append(('BACKGROUND', (i, 0), (i, -1), colors.CMYKColor(0.3,0,0,0)))

        for i in self.sun:
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
        origin = 210 -10 - 7*(len(hr_pd_p))
        table.wrapOn(self.cv, 10*mm, origin*mm) # table位置
        table.drawOn(self.cv, 10*mm, origin*mm)
        return table