import csv
from datetime import timedelta, date
from tkinter import *
from tkinter import filedialog

from arrow import arrow
from chardet import UniversalDetector
from ics import Calendar, Event
from pytz import timezone


def get_file_encoding(file_path: str) -> dict:
    detector = UniversalDetector()
    with open(file_path, mode = "rb") as f:
        for line in f.readlines():
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result


def get_csv_file():
    root.update()
    _file_name = filedialog.askopenfilename(
        initialdir = "",
        title = "Select file",
        filetypes = (
            ("comma separated values", "*.csv"),
            ("all files", "*.*")))

    print(_file_name)
    return _file_name


def read_csv_file(_file_path):
    _file_encoding = get_file_encoding(_file_path)
    print(_file_encoding)

    _content = []
    reader = csv.DictReader(open(_file_path, 'r', encoding = _file_encoding.get('encoding')))
    for line in reader:
        _content.append(line)

    print(_content)
    return _content


def parse_date(date_str: str, time_str: str, adjust = False, whole_day = False):
    date_split = date_str.split('.')
    time_split = time_str.split(':')
    if adjust:
        currDate = date(
            int(date_split[2]),
            int(date_split[1]),
            int(date_split[0])
        ) - timedelta(days = 1)
        return arrow.Arrow(
            currDate.year,
            currDate.month,
            currDate.day,
            hour = 23,
            minute = 59,
            second = 59,
            tzinfo = timezone("Europe/Berlin") if not whole_day else None)
    else:
        return arrow.Arrow(
            int(date_split[2]),
            int(date_split[1]),
            int(date_split[0]),
            hour = int(time_split[0]),
            minute = int(time_split[1]),
            second = int(time_split[2]),
            tzinfo = timezone("Europe/Berlin") if not whole_day else None)


def create_ics_file(csv_list: list):
    c = Calendar()
    event_entry: dict
    for event_entry in csv_list:
        e = Event()

        is_whole_day = False
        if event_entry.get('Ganztägiges Ereignis') == 'ja':
            is_whole_day = True

        e.name = event_entry.get("Betreff")
        e.begin = parse_date(event_entry.get("Beginnt am"), event_entry.get('Beginnt um'), whole_day = is_whole_day)
        e.end = parse_date(event_entry.get("Endet am"), event_entry.get('Endet um'), whole_day = is_whole_day)
        e.classification = event_entry.get("Kategorien")
        e.location = event_entry.get("Ort")
        e.description = event_entry.get("Beschreibung")

        # if event_entry.get("Erinnerung Ein/Aus") == "Ein":
        #     if not is_whole_day:
        #         e.alarms = [
        #             AudioAlarm(
        #                 timedelta(minutes=-15),
        #                 0,
        #                 timedelta(minutes=1),
        #             )]
        #     else:
        #         e.alarms = [
        #             AudioAlarm(
        #                 timedelta(hours=-12),
        #                 0,
        #                 timedelta(minutes=1),
        #             )]

        if is_whole_day:
            if event_entry.get('Endet um') == '00:00:00':
                e.end = parse_date(event_entry.get("Endet am"), event_entry.get('Endet um'), True,
                                   whole_day = is_whole_day)
            e.make_all_day()

        c.events.add(e)

    return c


def file_save(_ics_file, file_name = None):
    if file_name is None:
        ics_save_file = filedialog.asksaveasfilename(defaultextension = ".ics")
    else:
        ics_save_file = file_name

    if ics_save_file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    # text2save = str(_ics_file.get(1.0, END))  # starts from `1.0`, not `0.0`
    open(ics_save_file, 'w').writelines(_ics_file)


def parse_file(temp_file_path, save_file = None):
    root = Tk()
    root.withdraw()

    csv_content = read_csv_file(temp_file_path)
    ics_file = create_ics_file(csv_content)
    file_save(ics_file, file_name = save_file)
