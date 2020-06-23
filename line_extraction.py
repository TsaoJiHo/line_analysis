import pandas as pd
import pathlib

DATA_FOLDER_PATH = pathlib.Path('./data')

def is_date(row):
    weeks = ('（一）', '（二）', '（三）', '（四）', '（五）', '（六）', '（日）')
    return len(row) == 1 and len(row[0]) == 13 and row[0][-3:] in weeks

def create_dataframe(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        rows = f.readlines()
        date = ''
        d = {'date': [], 'time': [], 'name': [], 'text': []}
        for i, row in enumerate(rows):
            row = row.split()
            rows[i] = row
            # get date
            if is_date(row):
                date = row[0]
            # get uniform list
            is_uniform_format = len(row) > 0 and row[0][0:2] in ('下午', '上午')
            if is_uniform_format and row[1][-5:] != '已收回訊息' and row[1][-5:] != '的相簿刪除':
                uniform_format = []
                uniform_format.append(date)
                uniform_format.append(row[0])
                uniform_format.append(row[1])
                uniform_format.append(row[2:])
                j = 1
                if j + i < len(rows):
                    while(len(rows[i+j].split()) == 1 and not is_date(rows[i+j].split())):
                        uniform_format[3].append(rows[j+i].replace('\n', ''))
                        j += 1
                # create dataframe
                d['date'].append(uniform_format[0])
                d['time'].append(uniform_format[1])
                d['name'].append(uniform_format[2])
                d['text'].append(uniform_format[3])
        df = pd.DataFrame(d)
        df.to_csv(file_path.with_suffix('.csv'), index=False)

def load_dataframe():
    dataframes = []
    for path in DATA_FOLDER_PATH.rglob('*csv'):
        dataframes.append(pd.read_csv(path))
    return dataframes

def main():
    for path in DATA_FOLDER_PATH.rglob('*txt'):
        create_dataframe(path)

if __name__ == "__main__":
    main()
