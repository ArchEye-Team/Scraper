import urllib.request
from pathlib import Path
from urllib.parse import urlparse, unquote

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


def find_by_xpath(driver, xpath, timeout=10):
    return WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located((By.XPATH, xpath))
    )


def find_by_css(driver, selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def find_all_by_css(driver, selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    )


def login(driver, user_login, user_password):
    driver.get('https://photobuildings.com/')

    find_by_xpath(driver, '/html/body/table/tbody/tr[2]/td/ul/li[8]/a').click()

    find_by_xpath(driver, '//*[@id="username"]').send_keys(user_login)
    find_by_xpath(driver, '//*[@id="password"]').send_keys(user_password)
    find_by_xpath(driver, '//*[@id="remember"]').click()

    find_by_xpath(driver, '//*[@id="loginbtn"]').click()


def search(driver, style):
    driver.get('https://photobuildings.com/search.php')

    Select(find_by_xpath(driver, '//*[@id="sid"]')).select_by_visible_text(style)
    Select(find_by_xpath(driver, '/html/body/table/tbody/tr[3]/td/form/table/tbody/tr[22]/td[2]/select')
           ).select_by_visible_text('Рейтингу')

    find_by_xpath(driver, '/html/body/table/tbody/tr[3]/td/form/table/tbody/tr[23]/td[2]/input').click()


def process_photo_page(driver, photo_page_link, save_folder):
    original_window = driver.current_window_handle
    photo_page_link.click()
    driver.switch_to.window(driver.window_handles[1])

    source_url = find_by_css(driver, '#ph').get_attribute('src')

    filename = Path(save_folder) / unquote(Path(urlparse(source_url).path).name)

    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', 'Firefox')

    opener.retrieve(source_url, str(filename))

    driver.close()
    driver.switch_to.window(original_window)


def process_result_pages(driver, save_folder):
    while True:
        driver.refresh()

        photo_page_links = find_all_by_css(driver, 'a.prw')

        for photo_page_link in photo_page_links:
            process_photo_page(driver, photo_page_link, save_folder)

        try:
            next_page_link = find_by_xpath(driver, '//*[@id="NextLink"]')
            next_page_link.click()
        except TimeoutException:
            break


if __name__ == '__main__':
    driver = webdriver.Firefox()

    login(driver, user_login='login', user_password='pass')

    search(driver, style='Барочно-классический')

    process_result_pages(driver, save_folder='C:\\repos\\Scraper\\results\\baroque_classic')
