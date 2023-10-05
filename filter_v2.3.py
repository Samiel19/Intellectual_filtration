import copy
import fnmatch
import math
import os
import shutil
import sys
import matplotlib.pyplot as plt
import pandas

from PyQt6 import QtCore, QtWidgets

# Costants using for additional filtration according data params

COEFF_BIG = 2
COEFF = 0.6
BREAK_POINT = 0.05
ST_DEV = False
DEVIDER = 0
COUNTER = 0
ADDITIONAL_FILT = False


def devider_calc(unfiltered_data):
    amp = max(unfiltered_data) - min(unfiltered_data)
    devider = (amp / 20) ** (1 - 4 * amp)
    return devider


def marker_data_maker(unfiltered_data):
    """Fuction for marker data calculation.
       Takes data array, size 2xN, where N is array len.
    """
    marker_data = [
        (unfiltered_data[index] - unfiltered_data[index + 1]) / DEVIDER
        for index in range(len(unfiltered_data) - 1)
                   ]
    marker_data.append(unfiltered_data[-1])
    return marker_data


def first_minus_filtration(alone_minus):
    """First minus filtration.
       Takes data array, size 2xN, where N is array len.
    """
    cache_mark = []
    minus = 0
    marker_data = marker_data_maker(alone_minus)
    checker = copy.deepcopy(alone_minus)
    for index, _ in enumerate(alone_minus) and enumerate(marker_data):
        if index == 0:
            if (marker_data[index] < 0 and marker_data[index + 1] > 0
               and (abs(marker_data[index]) >= 1
               or abs(marker_data[index + 1]) >= 1)):
                minus += 1
                cache_mark.append(index)
                d = (alone_minus[index + 2]) / 3
                alone_minus[index] = d
                alone_minus[index + 1] = 2 * d
        elif 0 < index < len(alone_minus) - 1:
            if ((marker_data[index] < 0 and marker_data[index - 1] >= 0)
               and (abs(marker_data[index]) >= 1
               or abs(marker_data[index + 1]) >= 1
               or abs(marker_data[index - 1]) >= 1)):
                if (abs(marker_data[index - 1]) >= abs(marker_data[index + 1])
                   and alone_minus[index - 2] == checker[index - 2]):
                    minus += 1
                    cache_mark.append(index)
                    d = (alone_minus[index + 1] - alone_minus[index - 2]) / 3
                    alone_minus[index - 1] = alone_minus[index - 2] + d
                    alone_minus[index] = alone_minus[index - 2] + 2 * d

                elif (abs(marker_data[index - 1]) < abs(marker_data[index + 1])
                      and alone_minus[index - 1] == checker[index - 1]):
                    minus += 1
                    cache_mark.append(index)
                    d = (alone_minus[index + 2] - alone_minus[index - 1]) / 3
                    alone_minus[index] = alone_minus[index - 1] + d
                    alone_minus[index + 1] = alone_minus[index - 1] + 2 * d
        elif index == len(alone_minus) - 1:
            if (marker_data[index] < 0 and marker_data[index - 1] > 0
               and (abs(marker_data[index]) >= 1
               or abs(marker_data[index - 1]) >= 1)
               and (index - 2) not in cache_mark):
                minus += 1
                cache_mark.append(index)
                d = (0 - alone_minus[index - 2]) / 3
                alone_minus[index - 1] = alone_minus[index - 2] + d
                alone_minus[index] = alone_minus[index - 2] + 2 * d
    global COUNTER
    if minus > 0:
        if COUNTER > 10:
            COUNTER = 0
            first_minus = alone_minus
            return first_minus
        COUNTER += 1
        marker_data = marker_data_maker(alone_minus)
        first_minus_filtration(alone_minus)
    COUNTER = 0
    first_minus = alone_minus
    return first_minus


def another_plus_filtration(first_minus):
    """Experimenatal fuction for first plus filtration.
       Takes data array, size 2xN, where N is array len.
    """
    marker_data = marker_data_maker(first_minus)
    for index, _ in enumerate(first_minus) and enumerate(marker_data):
        if index == 0:
            first_minus[index] = first_minus[index]
        elif 0 < index:
            try:
                if ((marker_data[index - 1] < 0 and marker_data[index] > 0)
                   and (abs(marker_data[index]) >= 1
                   or abs(marker_data[index - 1]) >= 1)):
                    if first_minus[index - 1] > first_minus[index]:
                        first_minus[index - 1] = (
                            first_minus[index - 2] - first_minus[index]
                            ) / 2
                        first_minus_filtration(first_minus)
                        marker_data = marker_data_maker(first_minus)
                    elif first_minus[index - 1] < first_minus[index]:
                        first_minus[index] = (
                            first_minus[index - 1] - first_minus[index + 1]
                            ) / 2
                        first_minus_filtration(first_minus)
                        marker_data = marker_data_maker(first_minus)
            except IndexError:
                first_minus[index] = first_minus[index]
    another_plus = first_minus
    return another_plus


def first_plus_filtration(first_minus):
    """Fuction for first plus filtration.
       Takes data array, size 2xN, where N is array len.
    """
    marker_data = marker_data_maker(first_minus)
    amp_max = max(first_minus)
    amp_max_index = 0
    AMP_MARKER = 0
    for index, _ in enumerate(first_minus) and enumerate(marker_data):
        if index == 0:
            first_minus[index] = first_minus[index]
        elif 0 < index:
            if ((marker_data[index - 1] < 0 and marker_data[index] > 0)
               and first_minus[index] != amp_max
               and (abs(marker_data[index]) >= 1
               or abs(marker_data[index - 1]) >= 1)):
                first_minus[index] = (
                    first_minus[index - 1] + first_minus[index + 1]
                    ) / 2
            elif first_minus[index] == amp_max:
                amp_max_index = index
    if (abs(marker_data[amp_max_index]) >= 1
       and abs(marker_data[amp_max_index - 1]) >= 1):
        AMP_MARKER += 1
        for index, _ in enumerate(first_minus) and enumerate(marker_data):
            try:
                first_minus[index] = (
                    first_minus[index] + first_minus[index + 1]
                    ) / 2
            except IndexError:
                first_minus[index] = (first_minus[index] + 0) / 2
    if AMP_MARKER > 0:
        first_plus_filtration(first_minus)
    new_max = 0
    for index, _ in enumerate(first_minus):
        if first_minus[index] == max(first_minus):
            new_max = index
    if new_max < amp_max_index:
        first_minus.insert(0, 0)
        first_minus.pop(len(first_minus) - 1)
    if new_max > amp_max_index:
        first_minus.append(0)
        first_minus.pop(0)
    first_plus = first_minus
    return first_plus


def calculator(file):
    """Main calculation function.
       Takes data .xls file or automaticly formed instrument data
       as argument.
    """
    clip_data = pandas.ExcelFile(file)
    sheet_num = len(clip_data.sheet_names) - 1
    instrument_data = pandas.read_excel(
            file,
            sheet_name=sheet_num,
            header=None
            )
    if instrument_data.shape[1] > 3:
        clear_data_col = (instrument_data.dropna(how='all')).iloc[1:, :]
        nan_index = [n for n in clear_data_col.columns
                     if not clear_data_col[n].any()]
        clear_data = clear_data_col.drop(clear_data_col.columns[nan_index],
                                         axis=1)
        lb_at = clear_data[clear_data.columns[2]].to_list()
        ls_at = clear_data[clear_data.columns[3]].to_list()
        i_0 = (lb_at[0] + ls_at[0]) / 2
        a_1 = [math.log10(i_0 / lb_at[index]) for index, _ in enumerate(lb_at)]
        a_2 = [math.log10(i_0 / ls_at[index]) for index, _ in enumerate(ls_at)]
        a = [
            0.5 * (a_2[index] + a_2[index + 1]) - a_1[index] for index, _
            in enumerate(a_1) and enumerate(a_2) if index < len(a_1) - 1
        ]
        a[0], a[-1] = 0, 0
        signal = copy.deepcopy(a)
        time = [20 * i for i in range(len(signal))]
    else:
        time = instrument_data[0].to_list()
        signal = instrument_data[1].to_list()
        a = False
    global DEVIDER
    DEVIDER = devider_calc(signal)
    marker_data_1 = marker_data_maker(unfiltered_data=signal)
    triple_filt_1 = first_minus_filtration(signal)
    last_minus = first_plus_filtration(triple_filt_1)
    if ADDITIONAL_FILT:
        another_plus_filtration(last_minus)
    last_minus[0] = 0
    return {'instrument_data': instrument_data,
            'time': time,
            'signal': a,
            'a': a,
            'marker_data_1': marker_data_1,
            'triple_filt_1': triple_filt_1,
            'last_minus': last_minus}


def plot_maker(y, y_2, x, output_name, a):
    """Plot maker function. Uses y (unfiltered signal),
       y_2 (filtered signal), x (time), outpu_name (file_name),
       and a-flag as arguments. y and y_2 are
       data arrays, size 2xN, where N is array len. x as time should
       have same len, as y and y_2. Output name is name of filtering file.
    """
    if a:
        y_2 = a
    y_max = round(max(y), 5)
    y_2_max = round(max(y_2), 5)
    plt.figure(f'{output_name}')
    plt.plot(x, y, 'r', x, y_2, '--b')
    plt.xlabel("Time, ms")
    plt.ylabel("A, B")
    plt.title(output_name)
    plt.legend(
            [f'Filtered, Max={y_max}',
             f'Unfiltered, Max={y_2_max}']
            )
    plt.grid()
    plt.show()


def plot_maker_mean(
        y, y_2, x,
        output_name,
        a, y_3,
        st_dev_filt,
        st_dev_unfilt,
        mean_max_filt
        ):
    """Plot maker function for mean data. Uses y (unfiltered signal),
       y_2 (filtered signal), x (time), output_name (file_name),
       and a-flag as arguments. y and y_2 are
       data arrays, size 2xN, where N is array len. x as time should
       have same len, as y and y_2. Output name is name of filtering file.
       y_3 is mean file data, st_dev_filt is standart deviation of filtered
       data, st_dev_unfilt is standart deviation of unfiltered dada,
       mean_max_filt is mean maximum of filtered data.
    """
    if a:
        y_2 = a
    y_max = round(max(y), 5)
    y_2_max = round(max(y_2), 5)
    y_3_max = round(max(y_3), 5)
    plt.figure(f'{output_name}')
    plt.plot(x, y, 'r', x, y_2, '--b', x, y_3, 'g')
    plt.xlabel("Time, ms")
    plt.ylabel("A, B")
    plt.title(
        f'{output_name}\nSt_dev_filt = {round(st_dev_filt, 6)}, '
        f'St_dev_unfilt = {round(st_dev_unfilt, 6)}, '
        f'Mean_max = {round(mean_max_filt, 6)}'
        )
    plt.legend(
            [f'Filtered, Max={y_max}',
             f'Unfiltered, Max={y_2_max}',
             f'Filtered_mean, Max={y_3_max}', ]
            )
    plt.grid()
    plt.show()


def mean_calc(file, start):
    """Mean calculating function. Calculating mean signal
       for few measurment arrays.
       Takes .xls file with few filtered and unfiltered arrays and
       start point (int number) as arguments.
    """
    cols = list(range(0, file.shape[1]))[start::7]
    mean_signal = [
        sum([file[col][i] for col in cols]) / len(cols)
        for i in range(len(file))
        ]
    signals = [max(file[col]) for col in cols]
    mean_max = sum(signals) / len(signals)
    st_dev = (sum([(num - mean_max) ** 2
                   for num in signals]) / (len(cols) - 1)) ** 0.5
    return {'mean_signal': mean_signal,
            'st_dev': st_dev,
            'mean_max': mean_max}


def filter(file, box, choose=False):
    """Main filtration function. Takes .xls file, value of box
       and choose parameters as arguments. Produce filtered file and
       plots.
    """
    data = calculator(file=file)
    time = data['time']
    last_minus = data['last_minus']
    signal = data['signal']
    a = data['a']
    mean_filt = None
    mean_unfilt = None
    if a:
        signal = a
    dict_filt_data = {'Time': time,
                      'Signal_filt': last_minus,
                      'Signal_unfilt': signal, }
    filtered_data = pandas.DataFrame(data=dict_filt_data)
    abs_file_path = os.path.abspath(file)
    path, filename_xlsx = os.path.split(abs_file_path)
    filename = os.path.splitext(filename_xlsx)[0]
    output_name = f"{filename}_filtered"
    if os.path.exists(f'{output_name}.xlsx') and not box:
        list_of_files = os.listdir(path)
        pattern = f'{output_name}*'
        files_count = 0
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, pattern):
                files_count += 1
        cleared_output_name = output_name.replace('.xls', '')
        filtered_data.to_excel(f'{cleared_output_name}_{files_count}.xlsx',
                               index=False,
                               header=None)
    elif (box and os.path.exists('Multifile_clipboard.xlsx')
          or choose):
        if not choose:
            filename = 'Multifile_clipboard_filtered.xlsx'
        else:
            filename = 'Multifile_filtered.xlsx'
        if os.path.exists(filename):
            write_file = pandas.read_excel(
                filename,
                header=None
                )
            write_file['Time'] = time
            write_file['Signal_filt'] = last_minus
            write_file['Signal_unfilt'] = signal
            write_file['Mean_filt'] = [0]*len(signal)
            write_file['Mean_unfilt'] = [0]*len(signal)
            write_file.to_excel(filename,
                                index=False,
                                header=None)
            write_file = pandas.read_excel(
                filename,
                header=None
                )
            mean_filt = mean_calc(
                write_file, 1
               )
            write_file[write_file.shape[1] - 2] = mean_filt['mean_signal']
            mean_unfilt = mean_calc(
                write_file, 2
                )
            write_file[write_file.shape[1] - 1] = mean_unfilt['mean_signal']
            write_file['St_dev_filt'] = ['']*len(signal)
            write_file['St_dev_unfilt'] = ['']*len(signal)
            write_file.at[0, 'St_dev_filt'] = mean_filt['st_dev']
            write_file.at[0, 'St_dev_unfilt'] = mean_unfilt['st_dev']
            write_file.to_excel(filename,
                                index=False,
                                header=None)
        else:
            if not choose:
                filename = 'Multifile_clipboard_filtered.xlsx'
            else:
                filename = 'Multifile_filtered.xlsx'
            filtered_data.to_excel(filename,
                                   index=False,
                                   header=None)
            write_file = pandas.read_excel(
                filename,
                header=None
                )
            write_file['Break_1'] = [0]*len(signal)
            write_file['Break_2'] = [0]*len(signal)
            write_file['Break_3'] = [' ']*len(signal)
            write_file['Break_4'] = [' ']*len(signal)
            write_file.to_excel(filename,
                                index=False,
                                header=None)
    else:
        filtered_data.to_excel(f'{output_name}.xlsx',
                               index=False,
                               header=None)
    if mean_filt:
        plot_maker_mean(a=a,
                        y=last_minus,
                        y_2=signal,
                        x=time,
                        output_name=output_name,
                        y_3=mean_filt['mean_signal'],
                        st_dev_filt=mean_filt['st_dev'],
                        st_dev_unfilt=mean_unfilt['st_dev'],
                        mean_max_filt=mean_filt['mean_max'])
    else:
        plot_maker(a=a,
                   y=last_minus,
                   y_2=signal,
                   x=time,
                   output_name=output_name)


def filter_full(file):
    """Filtration function for algorithm testing.
       Takes .xls file. Produce filtered file with intermediate data
       and plots.
    """
    data = calculator(file=file)
    time = data['time']
    a = data['a']
    last_minus = data['last_minus']
    signal = data['signal']
    if a:
        signal = a
    dict_filt_data = {'Time': time,
                      'Sig.Un': data['signal'],
                      'Marker1': data['marker_data_1'],
                      'First.Min1': data['triple_filt_1'],
                      'last_minus': data['last_minus'],
                      'Sig.Fil': last_minus, }
    filtered_data = pandas.DataFrame(data=dict_filt_data)
    abs_file_path = os.path.abspath(file)
    path, filename_xlsx = os.path.split(abs_file_path)
    filename = os.path.splitext(filename_xlsx)[0]
    output_name = f"{filename}_filtered_full"
    if os.path.exists(f'{output_name}.xlsx'):
        plt.close()
        list_of_files = os.listdir(path)
        pattern = f'{output_name}*'
        files_count = 0
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, pattern):
                files_count += 1
        cleared_output_name = output_name.replace('.xls', '')
        filtered_data.to_excel(f'{cleared_output_name}_{files_count}.xlsx',
                               index=False,)
    else:
        filtered_data.to_excel(f'{output_name}.xlsx',
                               index=False,)
    plot_maker(a=a,
               y=last_minus,
               y_2=signal,
               x=time,
               output_name=output_name)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 700)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtWidgets.QListWidget(parent=self.centralwidget)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.btnBrowse = QtWidgets.QPushButton(parent=self.centralwidget)
        self.btnBrowse.setObjectName("btnBrowse")
        self.btnBrowse_clipboard = QtWidgets.QPushButton(
            parent=self.centralwidget
            )
        self.btnBrowse_clipboard.setObjectName("btnBrowse_clipboard")
        self.btnBrowse_full_data = QtWidgets.QPushButton(
            parent=self.centralwidget
            )
        self.btnBrowse_full_data.setObjectName("btnBrowse_full_data")
        self.btnBrowse_full_data_cb = QtWidgets.QPushButton(
            parent=self.centralwidget
            )
        self.btnBrowse_full_data_cb.setObjectName("btnBrowse_full_data_cb")
        self.btnBrowse_plt_close = QtWidgets.QPushButton(
            parent=self.centralwidget
            )
        self.btnBrowse_plt_close.setObjectName("btnBrowse_plt_close")
        self.verticalLayout.addWidget(self.btnBrowse)
        self.verticalLayout.addWidget(self.btnBrowse_clipboard)
        self.verticalLayout.addWidget(self.btnBrowse_full_data)
        self.verticalLayout.addWidget(self.btnBrowse_full_data_cb)
        self.verticalLayout.addWidget(self.btnBrowse_plt_close)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.OnefileCkBox = QtWidgets.QCheckBox(text="Записывать в один файл")
        self.CreatedDataBox = QtWidgets.QCheckBox(text="Искуственные данные")
        self.StDevCkBox = QtWidgets.QCheckBox(text="Рассчёт признака по СКО")
        self.AddFiltCkBox = QtWidgets.QCheckBox(text="Дополнительный фильтр")
        self.verticalLayout.addWidget(self.OnefileCkBox)
        self.verticalLayout.addWidget(self.CreatedDataBox)
        self.verticalLayout.addWidget(self.StDevCkBox)
        self.verticalLayout.addWidget(self.AddFiltCkBox)
        self.input_break = QtWidgets.QLineEdit(self)
        self.input_break.move(570, 620)
        self.input_break.setPlaceholderText('Переключение коэфф')
        self.input_coeff = QtWidgets.QLineEdit(self)
        self.input_coeff.move(460, 620)
        self.input_coeff.setPlaceholderText('Min коэфф')
        self.input_coeff_max = QtWidgets.QLineEdit(self)
        self.input_coeff_max.move(350, 620)
        self.input_coeff_max.setPlaceholderText('Max коэфф')
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "IntFiltration"))
        self.btnBrowse.setText(_translate("MainWindow", "Выберите файл"))
        self.btnBrowse_clipboard.setText(
            _translate("MainWindow", "Загрузить из буфера обмена")
            )
        self.btnBrowse_full_data.setText(
            _translate("MainWindow", "Полный рассчёт")
            )
        self.btnBrowse_full_data_cb.setText(
            _translate("MainWindow", "Полный рассчёт (буфер обмена)")
            )
        self.btnBrowse_plt_close.setText(
            _translate("MainWindow", "Закрыть все графики")
            )


class IntFiltApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnBrowse.clicked.connect(self.choose_file)
        self.btnBrowse_clipboard.clicked.connect(self.upload_file)
        self.btnBrowse_full_data.clicked.connect(self.choose_file_full)
        self.btnBrowse_full_data_cb.clicked.connect(self.upload_file_full)
        self.btnBrowse_plt_close.clicked.connect(self.plt_close_all)

    def FolderMaker(self):
        """Folder creation function."""
        self.le = QtWidgets.QLineEdit(self)
        self.le.move(130, 22)

        text, ok = QtWidgets.QInputDialog.getText(self,
                                                  'Хранение серии',
                                                  'Имя папки')
        if ok:
            name = str(text)
            try:
                os.mkdir(name)
            except WindowsError:
                print('Имя должно быть уникальным и не может быть пустым!')
                return self.FolderMaker()
            return name
        else:
            return self.FolderMaker()

    def plt_close_all(self):
        plt.close('all')

    def choose_file(self):
        """Function for calculationg data from .xls file."""
        self.listWidget.clear()  # На случай, если в списке уже есть элементы
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите файл")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории
        uploaded_file = file[0]

        if self.StDevCkBox.isChecked():
            st_dev = True
        else:
            st_dev = False
        global ST_DEV
        ST_DEV = st_dev

        if self.AddFiltCkBox.isChecked():
            add_filt = True
        else:
            add_filt = False
        global ADDITIONAL_FILT
        ADDITIONAL_FILT = add_filt

        if self.input_coeff_max.text() != '':
            coeff_big = float(self.input_coeff_max.text().replace(',', '.'))
        else:
            coeff_big = 2
        global COEFF_BIG
        COEFF_BIG = coeff_big
        if self.input_coeff.text() != '':
            coeff = float(self.input_coeff.text().replace(',', '.'))
        else:
            coeff = 0.6
        global COEFF
        COEFF = coeff
        if self.input_break.text() != '':
            break_point = float(self.input_break.text().replace(',', '.'))
        else:
            break_point = 0.05
        global BREAK_POINT
        BREAK_POINT = break_point

        if file:
            if self.OnefileCkBox.isChecked():
                box_status = True
                choose = True
            else:
                box_status = False
                choose = False
            try:
                filter(file=uploaded_file, box=box_status, choose=choose)
            except FileNotFoundError:
                print('FileNotFoundError')
            except IndexError:
                print('IndexError')
            except KeyError:
                print('KeyError')
            except pandas.errors.EmptyDataError:
                print('EmptyDataError: No columns to parse from file')

    def upload_file(self):
        """Function for calculationg data from clipboard."""
        plt.close('all')

        self.listWidget.clear()
        path = os.path.abspath('.')
        list_of_files = os.listdir(path)
        pattern = '*_clipboard.*'
        box_status = None

        if self.StDevCkBox.isChecked():
            st_dev = True
        else:
            st_dev = False
        global ST_DEV
        ST_DEV = st_dev

        if self.AddFiltCkBox.isChecked():
            add_filt = True
        else:
            add_filt = False
        global ADDITIONAL_FILT
        ADDITIONAL_FILT = add_filt

        if self.input_coeff_max.text() != '':
            coeff_big = float(self.input_coeff_max.text().replace(',', '.'))
        else:
            coeff_big = 2
        global COEFF_BIG
        COEFF_BIG = coeff_big
        if self.input_coeff.text() != '':
            coeff = float(self.input_coeff.text().replace(',', '.'))
        else:
            coeff = 0.6
        global COEFF
        COEFF = coeff
        if self.input_break.text() != '':
            break_point = float(self.input_break.text().replace(',', '.'))
        else:
            break_point = 0.05
        global BREAK_POINT
        BREAK_POINT = break_point

        if self.CreatedDataBox.isChecked():
            box_status = True
            step = 5
        else:
            step = 17
        if self.OnefileCkBox.isChecked():
            filename = 'Multifile_clipboard.xlsx'
            box_status = True
        else:
            box_status = False
            files_count = 0
            for entry in list_of_files:
                if fnmatch.fnmatch(entry, pattern):
                    files_count += 1
            filename = f'{files_count}_clipboard.xlsx'
        buffer = pandas.read_clipboard()
        if not box_status:
            filenames = []
            for i in range(0, buffer.shape[1], step):
                (buffer.iloc[:, i: i+4]).to_excel(
                    f'{int(i / step + 1)}_{filename}',
                    index=False
                    )
                filenames.append(f'{int(i / step + 1)}_{filename}')
            for filename in filenames:
                try:
                    filter(file=filename,
                           box=box_status)
                except FileNotFoundError:
                    print('FileNotFoundError')
                except KeyError:
                    print('KeyError')
                except pandas.errors.EmptyDataError:
                    print('EmptyDataError: No columns to parse from file')
            filenames.clear()
        else:
            m_folder_name = self.FolderMaker()
            try:
                os.remove('Multifile_clipboard.xlsx')
            except WindowsError:
                pass
            if not os.path.exists('Multifile_clipboard.xlsx'):
                buffer.to_excel(filename, index=False)
            clip_data = pandas.ExcelFile('Multifile_clipboard.xlsx')
            sheet_num = len(clip_data.sheet_names) + 1
            sheet_name = f'Sheet{sheet_num}'
            with pandas.ExcelWriter(
                    'Multifile_clipboard.xlsx', mode='a', engine='openpyxl'
                    ) as writer:
                for i in range(0, buffer.shape[1], step):
                    (buffer.iloc[:, i: i+4]).to_excel(
                        writer,
                        sheet_name=f'{int(i / step + 1)}_{sheet_name}',
                        index=False
                        )
            try:
                clip_data = pandas.ExcelFile('Multifile_clipboard.xlsx')
                files = []
                for sheet in clip_data.sheet_names[1:]:
                    files.append(pandas.read_excel(
                        'Multifile_clipboard.xlsx',
                        sheet_name=sheet,
                        header=None,
                        ))
                for index, file in enumerate(files):
                    file.to_excel(
                        f'{index}_{filename}',
                        index=False,
                        header=None
                        )
                    filter(file=f'{index}_{filename}',
                           box=box_status)
                files.clear()
            except FileNotFoundError:
                print('FileNotFoundError')
            except IndexError:
                print('IndexError')
            except KeyError:
                print('KeyError')
            except pandas.errors.EmptyDataError:
                print('EmptyDataError: No columns to parse from file')
            list_of_files = os.listdir(path)
            pattern = '*Multifile*'
            files_count = 0
            for entry in list_of_files:
                if fnmatch.fnmatch(entry, pattern):
                    try:
                        shutil.move(entry, os.path.abspath(m_folder_name))
                    except WindowsError:
                        pass

    def choose_file_full(self):
        """Function for calculationg data from .xls file.
           Produces intermediate data too.
        """
        self.listWidget.clear()
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите файл")
        uploaded_file = file[0]

        if self.StDevCkBox.isChecked():
            st_dev = True
        else:
            st_dev = False
        global ST_DEV
        ST_DEV = st_dev

        if self.AddFiltCkBox.isChecked():
            add_filt = True
        else:
            add_filt = False
        global ADDITIONAL_FILT
        ADDITIONAL_FILT = add_filt

        if self.input_coeff_max.text() != '':
            coeff_big = float(self.input_coeff_max.text().replace(',', '.'))
        else:
            coeff_big = 2
        global COEFF_BIG
        COEFF_BIG = coeff_big
        if self.input_coeff.text() != '':
            coeff = float(self.input_coeff.text().replace(',', '.'))
        else:
            coeff = 0.6
        global COEFF
        COEFF = coeff
        if self.input_break.text() != '':
            break_point = float(self.input_break.text().replace(',', '.'))
        else:
            break_point = 0.05
        global BREAK_POINT
        BREAK_POINT = break_point

        if file:
            try:
                filter_full(file=uploaded_file)
            except FileNotFoundError:
                print('FileNotFoundError')
            except IndexError:
                print('IndexError')
            except KeyError:
                print('KeyError')
            except pandas.errors.EmptyDataError:
                print('EmptyDataError: No columns to parse from file')

    def upload_file_full(self):
        """Function for calculationg data from clipboard.
           Produces intermediate data too.
        """
        self.listWidget.clear()
        path = os.path.abspath('.')
        list_of_files = os.listdir(path)
        pattern = '*_clipboard_full.*'

        if self.StDevCkBox.isChecked():
            st_dev = True
        else:
            st_dev = False
        global ST_DEV
        ST_DEV = st_dev

        if self.AddFiltCkBox.isChecked():
            add_filt = True
        else:
            add_filt = False
        global ADDITIONAL_FILT
        ADDITIONAL_FILT = add_filt

        if self.input_coeff_max.text() != '':
            coeff_big = float(self.input_coeff_max.text().replace(',', '.'))
        else:
            coeff_big = 2
        global COEFF_BIG
        COEFF_BIG = coeff_big
        if self.input_coeff.text() != '':
            coeff = float(self.input_coeff.text().replace(',', '.'))
        else:
            coeff = 0.6
        global COEFF
        COEFF = coeff
        if self.input_break.text() != '':
            break_point = float(self.input_break.text().replace(',', '.'))
        else:
            break_point = 0.05
        global BREAK_POINT
        BREAK_POINT = break_point

        files_count = 0
        for entry in list_of_files:
            if fnmatch.fnmatch(entry, pattern):
                files_count += 1
        buffer = pandas.read_clipboard()
        filename = f'{files_count}_clipboard_full.xlsx'
        buffer.to_excel(filename, index=False)
        try:
            filter_full(file=filename)
        except FileNotFoundError:
            print('FileNotFoundError')
        except IndexError:
            print('IndexError')
        except pandas.errors.EmptyDataError:
            print('EmptyDataError: No columns to parse from file')


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = IntFiltApp()
    window.show()
    app.exec()


if __name__ == '__main__':
    # The measurement data that you load into the program
    # must correspond to the primary data obtained from
    # the Kvant.Z atomic absorption spectrometer.
    # Another way to use this program - uploadig dada
    # as array with time and signal columns.
    main()
