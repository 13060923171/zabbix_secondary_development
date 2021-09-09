import datetime
import time

oneday = datetime.timedelta(days=1)
today = datetime.date.today()
yesterday_one = today - oneday
yesterday_two = yesterday_one - oneday
yesterday_three = yesterday_two - oneday
yesterday_four = yesterday_three - oneday
yesterday_five = yesterday_four - oneday
yesterday_six = yesterday_five - oneday
yesterday_seven = yesterday_six - oneday

seven_day = str(yesterday_six)[-2:] + "-" + str(yesterday_six)[-5:-3].replace('01','Jan').replace('02','Feb').replace('03','Mar').replace('04','Apr').replace('05','May').replace('06','Jun').replace('07','Jul').replace('08','Aug').replace('09','Sep').replace('10','Oct').replace('11','Nov').replace('12','Dec')
six_day = str(yesterday_five)[-2:] + "-" + str(yesterday_five)[-5:-3].replace('01','Jan').replace('02','Feb').replace('03','Mar').replace('04','Apr').replace('05','May').replace('06','Jun').replace('07','Jul').replace('08','Aug').replace('09','Sep').replace('10','Oct').replace('11','Nov').replace('12','Dec')
five_day = str(yesterday_four)[-2:] + "-" + str(yesterday_four)[-5:-3].replace('01','Jan').replace('02','Feb').replace('03','Mar').replace('04','Apr').replace('05','May').replace('06','Jun').replace('07','Jul').replace('08','Aug').replace('09','Sep').replace('10','Oct').replace('11','Nov').replace('12','Dec')
four_day = str(yesterday_three)[-2:] + "-" + str(yesterday_three)[-5:-3].replace('01','Jan').replace('02','Feb').replace('03','Mar').replace('04','Apr').replace('05','May').replace('06','Jun').replace('07','Jul').replace('08','Aug').replace('09','Sep').replace('10','Oct').replace('11','Nov').replace('12','Dec')
three_day = str(yesterday_two)[-2:] + "-" + str(yesterday_two)[-5:-3].replace('01','Jan').replace('02','Feb').replace('03','Mar').replace('04','Apr').replace('05','May').replace('06','Jun').replace('07','Jul').replace('08','Aug').replace('09','Sep').replace('10','Oct').replace('11','Nov').replace('12','Dec')
two_day = str(yesterday_one)[-2:] + "-" + str(yesterday_one)[-5:-3].replace('01','Jan').replace('02','Feb').replace('03','Mar').replace('04','Apr').replace('05','May').replace('06','Jun').replace('07','Jul').replace('08','Aug').replace('09','Sep').replace('10','Oct').replace('11','Nov').replace('12','Dec')
one_day = str(today)[-2:] + "-" + str(today)[-5:-3].replace('01','Jan').replace('02','Feb').replace('03','Mar').replace('04','Apr').replace('05','May').replace('06','Jun').replace('07','Jul').replace('08','Aug').replace('09','Sep').replace('10','Oct').replace('11','Nov').replace('12','Dec')


