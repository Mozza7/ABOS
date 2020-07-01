import os.path

root_location = os.getcwd()
logdir = os.path.abspath(os.path.join(os.getcwd(), 'log'))
logfile = open('info.log', 'a', encoding='utf-8')
failedlogins = open('failed-logins.log', 'a', encoding='utf-8')

if __name__=='__main__':
    pass
