import time
from general_functions import logfile
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import datetime
import threading


def run_reports_x(custlog, driver):
    time.sleep(5)
    sw_version_check_t = threading.Thread(target=sw_version_check_x, args=(custlog, driver,))
    sw_version_check_t.start()
    time.sleep(.1)
    last_backup_t = threading.Thread(target=last_backup_x, args=(custlog, driver,))
    last_backup_t.start()
    time.sleep(.1)
    tile_check_t = threading.Thread(target=tile_check_x, args=(custlog, driver,))
    tile_check_t.start()
    sw_version_check_t.join()
    tile_check_t.join()
    last_backup_t.join()
    sdhc_status_x(custlog, driver)
    time.sleep(1)
    swa_a = sw_assurance_check_x(custlog, driver,)
    if swa_a=='fail':
        sw_assurance_check_lm_x(custlog, driver,)
    time.sleep(1)


def sw_assurance_check_x(custlog, driver):  # CHECK IF EXPIRED SHOWS
    print('<', current_date(), '>', file=logfile)
    print('<', current_date(), '>', file=custlog)
    print('DATE_FORMAT=DD/MM/YYYY HH:MM.SS', file=logfile)
    print('DATE_FORMAT=DD/MM/YYYY HH:MM.SS', file=custlog)
    time.sleep(10)
    try:
        swa = driver.find_element_by_xpath('//*[@id="swMsg"]').text
        if swa == '':
            exp_sw = driver.find_element_by_xpath('//*[@id="swState"]').text
            if exp_sw == 'Software support expired.':
                print('Software support: expired', file=logfile)
                print('Software support: expired', file=custlog)
                swa_a = 'success'
                return swa_a
            else:
                print('Software support: expiration date not found. Recheck after backup completed.', file=logfile)
                print('Software support: expiration date not found. Recheck after backup completed.', file=custlog)
                swa_a = 'fail'
                return swa_a
        else:
            print(swa, file=logfile)
            print('SSP_STATUS: ', swa, file=custlog)
            swa_a = 'success'
            return swa_a
    except NoSuchElementException:
        print('Software support: expiration date not found. Recheck after backup completed.', file=logfile)
        print('Software support: expiration date not found. Recheck after backup completed.', file=custlog)
        swa_a = 'fail'
        return swa_a


def sw_version_check_x(custlog, driver):
    swv = driver.find_element_by_xpath('//*[@id="swVersion"]').text
    if swv == '':
        print('Error finding version. Recheck after backup completed.', file=logfile)
    else:
        print('Software version: ', swv, file=logfile)
        print('Software version: ', swv, file=custlog)
    try:
        ucv = driver.find_element_by_xpath('//*[@id="swOcabVersion"]').text
        if ucv == '':
            print('Error finding OCAB version. Recheck after backup completed.', file=logfile)
        else:
            print('OCAB version: ', ucv, file=logfile)
            print('OCAB version: ', ucv, file=custlog)
    except NoSuchElementException:
        print('OCAB not found. Recheck after backup completed.', file=logfile)


def current_date():
    cdate = datetime.datetime.now()
    cdate = str(cdate)
    cdate1 = datetime.datetime.strptime(cdate, '%Y-%m-%d %H:%M:%S.%f')
    ukform = cdate1.strftime('%d/%m/%Y %H:%M.%S')
    return ukform


def check_num(char):
    return char.isdigit()


def lm_assurance_test_x(custlog, driver):
    try:
        print('Testing..')
        lm_test = driver.find_element_by_xpath('//*[@id="autContentHead"]').text
        print('Phrase ', lm_test, 'found.')
        return lm_test
    except NoSuchElementException:
        while True:
            time.sleep(2)
            print('Test failed. Retesting..')
            time.sleep(1)
            lm_retest = driver.find_element_by_xpath('//*[@id="autContentHead"]').text
            return lm_retest


def expiration_days_x(driver):
    e_d = driver.find_element_by_xpath('//*[@id="DownloadCenter"]/table[2]/tbody/tr[13]/td[5]').text
    return e_d


def sw_assurance_check_lm_x(custlog, driver):
    try:
        driver.find_element_by_xpath('//*[@id="pnav_menuAPLicense"]').click()
        time.sleep(3)
        print('WARNING: If your system date is incorrect, '
              'SW assurance expiration date WILL be incorrect.')
        print('WARNING: If your system date is incorrect, '
              'SW assurance expiration date WILL be incorrect.', file=logfile)
        print('WARNING: If your system date is incorrect, '
              'SW assurance expiration date WILL be incorrect.', file=custlog)
        time.sleep(10)
        lm_test = lm_assurance_test_x(custlog, driver)
        if lm_test == "License information":
            while False:
                time.sleep(5)
        else:
            expday = expiration_days_x(driver)
            print('SW Assurance', expday, '. Getting date..')
            print('SW Assurance', expday, '. Getting date..', file=logfile)
            print('SW Assurance', expday, '. Getting date..', file=custlog)
            exp_num = ''.join(filter(check_num, expday))
            expiration_date = datetime.datetime.now().date() + datetime.timedelta(days=int(exp_num))
            # next line converts to UK format. give options to choose format once complete
            exp_date_uk = expiration_date.strftime('%d/%m/%Y')
            print('Software support: ', exp_date_uk, '(Format: DD/MM/YYYY)')
            print('Software support: ', exp_date_uk, '(Format: DD/MM/YYYY)', file=logfile)
            print('SSP_STATUS: ', exp_date_uk, file=custlog)
    except NoSuchElementException:
        print('Software assurance expiration date cannot be found. Error.', file=logfile)
        print('SSP_STATUS: Software assurance expiration date cannot be found. Error.', file=custlog)


def sdhc_status_x(custlog, driver):
    time.sleep(2)
    try:
        driver.find_element_by_xpath('//*[@id="tblTileSystem"]/table/tbody/tr[9]/td[1]').click()
        time.sleep(5)
        sdhcstatus1 = driver.find_element_by_xpath('//*[@id="tdDetails"]/table/tbody/tr[1]/td/'
                                                   'fieldset[2]/table/tbody/tr[1]/td[2]/div').text

        print('SDHC card status: ', sdhcstatus1)
        print('SDHC card status: ', sdhcstatus1, file=logfile)
        print('SDHC card status: ', sdhcstatus1, file=custlog)

    except NoSuchElementException:

        try:
            driver.find_element_by_xpath('//*[@id="pnav_menuAPAdvancedAdministration"]').click()
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="navGroup_Applications.Common.AdvancedAdministration.Maintenance.'
                                         'folder.title"]').click()
            time.sleep(.5)
            driver.find_element_by_xpath('//*[@id="navSpan_Applications.Common.AdvancedAdministration.Maintenance.'
                                         'Actions.title"]').click()
            time.sleep(2)
            driver.find_element_by_id('mnItem2').click()
            time.sleep(.5)
            driver.find_element_by_id('mnItem5').click()
            time.sleep(5)
            sdhcstatus2 = driver.find_element_by_xpath('//*[@id="tdDetails"]/table/tbody/tr[1]/td/'
                                                       'fieldset[2]/table/tbody/tr[1]/td[2]/div').text
            print('SDHC card status: ', sdhcstatus2)
            print('SDHC card status: ', sdhcstatus2, file=logfile)
            print('SDHC card status: ', sdhcstatus2, file=custlog)
        except NoSuchElementException:
            print('SDHC status cannot be found')
    time.sleep(1)
    try:
        driver.find_element_by_id('imgClose').click()
    except NoSuchElementException:
        sdhc_status_x(custlog, driver)
        print('SDHC report error.. trying again')
    time.sleep(3)
    try:
        driver.find_element_by_id('pnav_menuAPHome').click()
    except ElementClickInterceptedException:
        time.sleep(2)
        try:
            driver.find_element_by_xpath('//*[@id="imgClose"]').click()
        except ElementClickInterceptedException:
            print('Error getting SDHC status..', file=custlog)
    driver.refresh()
    time.sleep(2)


def last_backup_x(custlog, driver):
    time.sleep(3)
    lst_bckup = driver.find_element_by_xpath('//*[@id="tblTileSystem"]/table/tbody/tr[10]/td').text
    print(lst_bckup)
    print('Last backup: ', lst_bckup, file=custlog)


def issue_check_x(custlog, driver):
    # tileOK.png & tileWarn.png
    time.sleep(1)
    if driver.find_element_by_css_selector('#imgTileState[src="../imgs/tileOK.png"]'):
        print('No issues - OK tile report', file=logfile)
        print('No issues - OK tile report', file=custlog)
        print('No issues - OK tile report')

    elif driver.find_element_by_css_selector('#imgTileState[src="../imgs/tileWarn.png"]'):
        print('Issues found - searching..', file=logfile)
        print('Issues found - searching..', file=custlog)
        print('Issues found - searching..')
        sys_state_check_x(custlog, driver)
    else:
        print('Tile status unknown', file=logfile)
        print('Tile status unknown', file=custlog)
        print('Tile status unknown')


def sys_state_check_x(custlog, driver):
    sys_state_warn = driver.find_element_by_xpath('//*[@id="sysState"]/div').text
    print(sys_state_warn, file=logfile)
    print(sys_state_warn, file=custlog)
    print(sys_state_warn)
    time.sleep(1)


def notif_tile_x(custlog, driver):
    print('Notifications tile: ')
    notif_tile_tbl = driver.find_element_by_id('tblTileNotifications').text
    print(notif_tile_tbl, file=logfile)
    print(notif_tile_tbl, file=custlog)
    print(notif_tile_tbl)


def licensing_tile_x(custlog, driver):
    print('Licensing tile: ')
    licensing_tile_tbl = driver.find_element_by_id('tblTileLicense').text
    print(licensing_tile_tbl, file=logfile)
    print(licensing_tile_tbl, file=custlog)
    print(licensing_tile_tbl)


def inventory_tile_x(custlog, driver):
    print('Inventory tile: ')
    inventory_tile_tbl = driver.find_element_by_id('tblTileInventory').text
    print(inventory_tile_tbl, file=logfile)
    print(inventory_tile_tbl, file=custlog)
    print(inventory_tile_tbl)


def systeminfo_tile_x(custlog, driver):
    print('System information tile: ')
    systeminfo_tile_tbl = driver.find_element_by_id('tblTileSystem').text
    print(systeminfo_tile_tbl, file=logfile)
    print(systeminfo_tile_tbl, file=custlog)
    print(systeminfo_tile_tbl)


def app_tile_x(custlog, driver):
    print('Applications tile: ')
    app_tile_tbl = driver.find_element_by_id('tblTileAppl').text
    print(app_tile_tbl, file=logfile)
    print(app_tile_tbl, file=custlog)
    print(app_tile_tbl)


def tile_check_x(custlog, driver):
    # In order: System, Applications, Inventory, Licensing, Notifications
    print(' ', file=logfile)
    print(' ', file=custlog)
    print(' ')
    systeminfo_tile_x(custlog, driver)
    print(' ', file=logfile)
    print(' ', file=custlog)
    print(' ')
    app_tile_x(custlog, driver)
    print(' ', file=logfile)
    print(' ', file=custlog)
    print(' ')
    inventory_tile_x(custlog, driver)
    print(' ', file=logfile)
    print(' ', file=custlog)
    print(' ')
    licensing_tile_x(custlog, driver)
    print(' ', file=logfile)
    print(' ', file=custlog)
    print(' ')
    notif_tile_x(custlog, driver)
    print(' ', file=logfile)
    print(' ', file=custlog)
    print(' ')


# BUSINESS S


def run_reports_s(custlog, driver):
    time.sleep(5)
    sw_version_check_t = threading.Thread(target=sw_version_check_x, args=(custlog, driver,))
    sw_version_check_t.start()
    time.sleep(.1)
    last_backup_t = threading.Thread(target=last_backup_x, args=(custlog, driver,))
    last_backup_t.start()
    time.sleep(.1)
    tile_check_t = threading.Thread(target=tile_check_x, args=(custlog, driver,))
    tile_check_t.start()
    sw_version_check_t.join()
    tile_check_t.join()
    last_backup_t.join()
    swa_a = sw_assurance_check_x(custlog, driver)
    if swa_a=='fail':
        sw_assurance_check_lm_x(custlog, driver)
    time.sleep(1)


def last_backup_s(custlog, driver):
    time.sleep(3)
    lst_bckup = driver.find_element_by_xpath('//*[@id="tblTileSystem"]/table/tbody/tr[8]/td').text
    print(lst_bckup)
    print('Last backup: ', lst_bckup, file=custlog)


if __name__=='__main__':
    pass
