import pandas as pd

crime = pd.read_csv('sample_Chicago_Crimes.csv')

# 删除存在nan值的行
crime.dropna(inplace=True)

# 删除2017年数据
crime = crime[crime['Year'] != 2017]

# 删除无效列
delete_list = ['Unnamed: 0.1', 'Unnamed: 0', 'Case Number', 'IUCR', 'Location', 'X Coordinate', 'Y Coordinate', 'Updated On']
crime_analyse = crime.drop(columns=delete_list)

# 取犯罪数量最高的10种类别
crime_analyse = crime_analyse.groupby("Location Description").filter(lambda x: len(x) >= 5404)

# 取犯罪发生最多的10个位置
crime_analyse = crime_analyse.groupby("Primary Type").filter(lambda x: len(x) >= 8825)

# 将时间数据转化成datatime
crime_analyse.Date = pd.to_datetime(crime_analyse.Date, format='%m/%d/%Y %I:%M:%S %p')

# 将索引设置为日期
crime_analyse.index = pd.DatetimeIndex(crime_analyse.Date)

from datetime import datetime

# 分段时间

crime_analyse['Time'] = crime_analyse['Date'].dt.time

def timing(pick_time):
  if pick_time>datetime.strptime('00:00:00','%H:%M:%S').time() and pick_time<datetime.strptime('6:00:00','%H:%M:%S').time():
    return 0
  elif pick_time>=datetime.strptime('6:00:00','%H:%M:%S').time() and pick_time<=datetime.strptime('12:00:00','%H:%M:%S').time():
    return 1
  elif pick_time>=datetime.strptime('12:00:00','%H:%M:%S').time() and pick_time<=datetime.strptime('18:00:00','%H:%M:%S').time():
    return 2
  else:
    return 3
crime_analyse['Slot'] = crime_analyse['Time'].apply(timing)
crime_analyse.drop(columns=['Time'], inplace=True)
crime_analyse.reset_index(drop=True, inplace=True)

crime_analyse.to_csv('Chicago_crimes.csv')