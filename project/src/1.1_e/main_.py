from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from urllib3.exceptions import MaxRetryError 
import time, os, glob, re, shutil, sys
from configparser import ConfigParser
from general_functions import logdir, logfile
import logging
from general_functions import root_location

print('#########################', file=logfile)
config = ConfigParser()
config.read('config.ini')
dl_dir_o = os.path.abspath(os.path.join(os.getcwd(), root_location + '/Downloads/'))
backup_location = config.get('options', 'backup_location')
nas = config.get('options', 'nas')
if nas == '1':
    nas_loc = config.get('options', 'nas_location')


def webdriver_create(dldir):
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.acceptInsecureCerts", True)
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", dldir)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "applicatoin/octet-stream, application/octet-stream")
    options = Options()
    headless_active = config.get('selenium', 'headless')
    if headless_active == '1':
       options.headless = True
    driver = webdriver.Firefox(firefox_profile=fp, options=options)
    return driver


def conn_test(custlog, driver):
    try:
        osbiz_login(custlog, driver)
        connection = True
        return connection
    except (NoSuchElementException, WebDriverException, MaxRetryError):
        try:
            time.sleep(2)
            driver.find_element_by_name('j_username').send_keys(sysusername)
            time.sleep(1)
            driver.find_element_by_name('j_password').send_keys(syspassword)
            time.sleep(1)
            driver.find_element_by_id('submitButton').click()
            time.sleep(1)
            connection = True
            return connection
        except (NoSuchElementException, WebDriverException, MaxRetryError):
            try:
                sys_check = driver.find_element_by_xpath('/html/body/div/table/tbody/tr[1]/td[2]/div[2]').text
                if sys_check == 'OpenScape Office Assistant':
                    print('OpenScape office systems are not currently supported. Moving to next customer.',
                          file=custlog)
                    connection = False
                    return connection
                else:
                    print('Connection failed..Next customer.', file=custlog)
                    connection = False
                    return connection
            except (NoSuchElementException, WebDriverException, MaxRetryError):
                print('Connection failed..Next customer.', file=custlog)
                connection = False
                return connection


def osbiz_login(custlog, driver):
    time.sleep(1)
    try:
        driver.get(url)
    except WebDriverException:
        print('Connection failed..Next customer', file=custlog)
        driver.quit()
    time.sleep(1)
    driver.refresh()
    time.sleep(2)
    driver.find_element_by_name('j_username').send_keys(sysusername)
    time.sleep(1)
    driver.find_element_by_name('j_password').send_keys(syspassword)
    time.sleep(1)
    driver.find_element_by_id('submitButton').click()
    time.sleep(3)

    try:
        driver.find_element_by_id('UserNError')
        print('Password incorrect, moving onto next customer. This will be logged.')
        print('Password incorrect', file=custlog)
        print(ncust, 'login failed', file=logfile)
        failedlogins = open('failedlogins.log', 'a', encoding='utf-8')
        print(ncust, 'login failed', file=failedlogins)
        failedlogins.close()

    except NoSuchElementException:
        print('Logged in')
        print('Logged in', file=custlog)


def osbiz_logoff(custlog, driver):
    print('Logging off..')
    print('Logging off..', file=custlog)
    time.sleep(1)
    try:
        driver.find_element_by_xpath('/html/body/div[5]/div[5]/div[2]').click()
    except NoSuchElementException:
        print('Issue logging off..continuing')
        print('Issue logging off..continuing', file=custlog)
    time.sleep(1)


def osbiz_logoff_fail(driver):
    print('Logging off..')
    time.sleep(1)
    try:
        driver.find_element_by_xpath('/html/body/div[5]/div[5]/div[2]').click()
    except NoSuchElementException:
        print('Backup AND/OR logoff for ', ncust, ' failed.')
        print('Backup AND/OR logoff for ', ncust, ' failed.', file=logfile)


def run_all(db_id):
    dldir = create_dldir(db_id)
    driver = webdriver_create(dldir)
    driver.set_window_size(1890, 1050)
    from models import process_all
    global ncust, url, sysusername, syspassword
    ncust, url, sysusername, syspassword = process_all(db_id)
    if ncust is not None:
        custlogn = ncust + '.log'
        custlog = open(custlogn, 'w+', encoding='utf-8')
        print('EXP_CUSTOMER_NAME=', ncust, file=custlog)
        connection = conn_test(custlog, driver)
        if not connection:
            driver.quit()
            pass
        else:
            system_os = os_sys_check(custlog, driver)
            if system_os == 'S':
                s_series(custlog, driver)
                print('Backup complete', file=custlog)
            elif system_os == 'X':
                x_series(custlog, driver)
                print('Backup complete', file=custlog)
            time.sleep(1)
            print('#########################', file=logfile)
            custlog.close()
            driver.quit()
            backup_absolute1 = backup_location + '\\' + ncust
            move_backup(custlogn, backup_absolute1)
    elif ncust is None:
        logging.info('Backups complete.')
        driver.quit()


def move_backup(custlogn, backup_absolute1):
    logging.info('Thread move_backup_t: starting')
    try:
        shutil.move(custlogn, backup_absolute1)
    except shutil.Error:
        os.remove(backup_absolute1 + '\\' + custlogn)
        shutil.move(custlogn, backup_absolute1)
    logging.info('Thread move_backup_t: finished')


def backup_full(custlog, driver):
    time.sleep(2)
    driver.find_element_by_id('pnav_menuAPBackup').click()
    time.sleep(4)
    driver.find_element_by_id('navDiv_BackupImmediate').click()
    time.sleep(5)
    try:
        https_s = driver.find_element_by_id('typ3')
        https_r = https_s.find_element_by_xpath('..')
        https_r.find_element_by_name('rdDevice').click()
        time.sleep(1)
        driver.find_element_by_id('btn1').click()
        time.sleep(1)
        logging.info('Backup started for: %s', ncust)
        print('Backup started for', ncust, file=custlog)
        time.sleep(5)
    except NoSuchElementException:
        print('Error..')
        driver.quit()
    backup_100_test(driver)


def os_sys_check(custlog, driver):
    # This is to check what model system is in use; S, X1, X3, X5, X8 so on
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#tblTileSystem > table > tbody > tr:nth-child(1) > td:nth'
                                                        '-child(1) > img')))

    img_src_o = driver.find_element_by_css_selector('#tblTileSystem > table > tbody > tr:nth-child(1) '
                                        '> td:nth-child(1) > img').get_attribute('src')
    img_src = re.sub('.*(?=imgs/)', '', img_src_o)

    if img_src == 'imgs/OSBiz_S_logo.png':
        print('OpenScape Business S')
        print('OpenScape Business S', file=custlog)
        system_os = 'S'
        return system_os

    elif img_src == 'imgs/OSBiz_X1_logo.png':
        print('OpenScape Business X1')
        print('OpenScape Business X1', file=custlog)
        system_os = 'X'
        return system_os

    elif img_src == 'imgs/OSBiz_X3_logo.png':
        print('OpenScape Business X3')
        print('OpenScape Business X3', file=custlog)
        system_os = 'X'
        return system_os

    elif img_src == 'imgs/OSBiz_X5_logo.png':
        print('OpenScape Business X5')
        print('OpenScape Business X5', file=custlog)
        system_os = 'X'
        return system_os

    elif img_src == 'imgs/OSBiz_X8_logo.png':
        print('OpenScape Business X8')
        print('OpenScape Business X8', file=custlog)
        system_os = 'X'
        return system_os

    else:
        print('Error finding system type')
        print('Error finding system type', file=custlog)
        system_os = 'E'
        return system_os


def x_series(custlog, driver):
    from reports import run_reports_x
    run_reports_x(custlog, driver)
    backup_full(custlog, driver)
    osbiz_logoff(custlog, driver)


def s_series(custlog, driver):
    from reports import run_reports_s
    run_reports_s(custlog, driver)
    backup_full(custlog, driver)
    osbiz_logoff(custlog, driver)


def file_downloaded_check():
    backuptar = glob.glob('*.tar.part')[:1]
    print(backuptar)
    if not backuptar:
        while True:
            time.sleep(.250)
            if glob.glob('*.tar.part')[:1]:
                break
    if not glob.glob('*.tar.part')[:1]:
        print('Files downloaded')
        print('Files downloaded', file=logfile)
        backup_move()
        if glob.glob('*.tar')[:1]:
            os.remove('*.tar')
        if glob.glob('*.txt')[:1]:
            os.remove('*.txt')

    elif glob.glob('*.tar.part')[:1]:
        while True:
            if not glob.glob('*.tar.part')[:1]:
                break
        if not glob.glob('*.tar.part')[:1]:
            print('Files downloaded')
            print('Files downloaded', file=logfile)
            backup_move()
            tar_check = glob.glob('*.tar')
            for i in tar_check:
                try:
                    os.remove(i)
                except:
                    pass
            txt_check = glob.glob('*.txt')
            for i in txt_check:
                try:
                    os.remove(i)
                except:
                    pass


def backup_move():
    backup_absolute = backup_location+'/'+ncust
    src_tar = '*.tar'
    src_txt = '*.txt'
    print(src_tar, 'AND', src_txt, 'AND', ncust)
    tar_list = glob.glob(src_tar)
    txt_list = glob.glob(src_txt)
    if not os.path.exists(backup_absolute):
        os.makedirs(backup_absolute)
    try:
        for single_file_tar in tar_list:
            print(single_file_tar)
            shutil.move(single_file_tar, backup_absolute)
        for single_file_txt in txt_list:
            print(single_file_txt)
            shutil.move(single_file_txt, backup_absolute)
    except PermissionError:
        time.sleep(5)
        try:
            for single_file_tar1 in tar_list:
                print(single_file_tar1)
                shutil.move(single_file_tar1, backup_absolute)
            for single_file_txt1 in txt_list:
                print(single_file_txt1)
                shutil.move(single_file_txt1, backup_absolute)
        except shutil.Error:
            try:
                for single_file_txt1 in txt_list:
                    print(single_file_txt1)
                    shutil.move(single_file_txt1, backup_absolute)
            except shutil.Error:
                print('Txt already exists in destination')
            try:
                for single_file_tar1 in tar_list:
                    print(single_file_tar1)
                    shutil.move(single_file_tar1, backup_absolute)
            except shutil.Error:
                print('Tar already exists in destination')


def backup_100_test(driver):
    percentage = driver.find_element_by_xpath('//*[@id="divPercent"]').text
    if percentage == '100%':
        time.sleep(1)
        if percentage == '100%':
            logging.info('Download percentage: %s', percentage)
        else:
            time.sleep(1)
            backup_100_test(driver)
        logging.info('Download complete: %s', ncust)
        logging.info('Downloading files..: %s', ncust)
        file_downloaded_check()
        logging.info('Files downloaded: %s', ncust)
        try:
            driver.find_element_by_xpath('//*[@id="btn1"]').click()
        except NoSuchElementException:
            pass
    else:
        logging.info('Download percentage: %s', percentage)

        time.sleep(2.5)
        backup_100_test(driver)


def cleanup_start():
    import shutil
    if os.getcwd() == dl_dir_o:
        pass
    else:
        os.chdir(dl_dir_o)
    old_files = glob.glob('*')
    for i in old_files:
        try:
            shutil.rmtree(i)
        except NotADirectoryError:
            pass
    os.chdir(root_location)


def email_report():
    latestlog_loc = logdir + '/info-latest.log'
    fromaddress = config.get('email', 'from')
    toaddress = config.get('email', 'to')
    smtp_server_addr = config.get('email_server', 'smtp_server_addr')
    smtp_server_port = config.get('email_server', 'smtp_server_port')
    tls_t = config.get('email_server', 'tls')
    if tls_t == '1':
        tls = True
    else:
        tls = False
    smtp_pword = config.get('email_server', 'smtp_pword')

    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders
    msg = MIMEMultipart()
    msg['From'] = fromaddress
    msg['To'] = toaddress
    msg['Subject'] = 'Auto-backup OpenScape'
    logged = open(latestlog_loc)
    bodymsg = logged.read()
    msg.attach(MIMEText(bodymsg, 'plain'))
    attachment = open(latestlog_loc, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename=latestlog.txt")
    msg.attach(p)
    s = smtplib.SMTP(smtp_server_addr, smtp_server_port)
    if tls is True:
        s.starttls()
    s.login(fromaddress, smtp_pword)
    text = msg.as_string()
    s.sendmail(fromaddress, toaddress, text)
    s.quit()
    print('Email report sent')


def onedrive_run_check():
    import psutil
    for p in psutil.process_iter(attrs=['pid', 'name']):
        if "onedrive.exe" in (p.info['name']).lower():
            pass
        else:
            print('OneDrive.exe is not running, please run OneDrive.exe to '
                'sync your backups. -This is not an error')


def create_dldir(db_id):
    os.chdir(dl_dir_o)
    directory_ = 'dir' + str(db_id)
    if not os.path.exists(directory_):
        os.makedirs(directory_)
    dldir = os.path.abspath(os.path.join(os.getcwd(), directory_))
    print(dldir)
    os.chdir(dldir)
    return dldir


def offline_move():
    # This is used to move files AFTER program is complete. This is used when the storage location is marked as NAS,
    # this will keep trying to move the files until they can be moved; in case the storage location is offline.
    os.chdir(backup_location)
    srcfiles = glob.glob('*')

    def files_move():
        for i in srcfiles:
            try:
                try:
                    shutil.copytree(i, nas_loc+'/'+i)
                except NotADirectoryError:
                    shutil.copyfile(i, nas_loc+'/'+i)
            except IOError:
                time.sleep(300)
                files_move()
    files_move()


if __name__=='__main__':
    from general_functions import root_location
    cleanup_start()
    logformat = "%(asctime)s: %(message)s"
    logging.basicConfig(format=logformat, level=logging.INFO,
                        datefmt="%H:%M:%S")
    if config.get('options', 'multicore_on') == '1':  # Change to 'YES' to use
        cores = int(config.get('options', 'cores'))
        from multicore import core_init
        core_init(cores)
    else:
        db_id = 0
        dldir = 'Downloads'
        run_all(db_id)
    if config.get('email', 'email_on') == '1':
        email_report()
    if config.get('options', 'onedrive') == '1':
        onedrive_run_check()
    cleanup_start()
    offline_move()
    sys.exit()
