# -*- coding: utf-8 -*-
import TsinghuaLearnDownloader
#这里是定期下载网络学堂的公告
#每天早上8：00 向邮箱发送网络学堂的公告
import  os
import  time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

def tick():
    file = open('log.txt', 'a+')
    file.write(str(datetime.now())+'\n')
    file.close()
    print 'Tick! The time is: %s' % datetime.now()


# 周一到周五早上5：30 执行
if __name__ == '__main__':
    login()
    scheduler = BlockingScheduler()
    #scheduler.add_job(tick, 'cron', second='*/10', hour='*')
    scheduler.add_job(tick,
                  'cron',
                  day_of_week='mon-fri',
                  hour=5,
                  minute=30,
                  end_date='2017-12-29')
    print 'Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
       scheduler.shutdown()
