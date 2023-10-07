from urllib.parse import urlencode

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

SEARCH_QUERY = 'фотографии зданий в стиле Авангард | Деконструктивизм | Постмодерн | Конструктивизм'
SCRAPED_LINKS_PATH = 'Modern_and_experimental_google_images.txt'
MAX_SCRAPED_LINKS = 1000
DRIVER = webdriver.Firefox()

search_uri = 'https://www.google.com/search?' + urlencode({'q': SEARCH_QUERY})

DRIVER.get(search_uri)

images_button_selectors = ['div.hdtb-mitem:nth-child(2) > a:nth-child(1)', '.IUOThf > a:nth-child(1)']
for selector in images_button_selectors:
    try:
        images_button = DRIVER.find_element(By.CSS_SELECTOR, selector)
        images_button.click()
        break
    except NoSuchElementException:
        continue

links = set()
thumbnails_seen = set()

try:
    while len(links) < MAX_SCRAPED_LINKS:
        DRIVER.execute_script('window.scrollBy(0, document.body.scrollHeight);')
        print('Scrolling down')

        try:
            show_more_results = WebDriverWait(DRIVER, 5).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, 'input.LZ4I'))
            )
            show_more_results.click()
            print('Clicked on show more results')
        except TimeoutException:
            print('Show more results button not found')

        try:
            thumbnails = WebDriverWait(DRIVER, 5).until(
                expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR, 'img.Q4LuWd'))
            )
            print(f'Total thumbnails: {len(thumbnails)}')
        except TimeoutException:
            print('Thumbnails not found on a page')
            break

        prev_links_len = len(links)

        for thumbnail in thumbnails:
            try:
                thumbnail_link = thumbnail.get_attribute('src')
            except StaleElementReferenceException:
                continue

            if thumbnail_link in thumbnails_seen:
                continue
            thumbnails_seen.add(thumbnail_link)

            thumbnail.click()

            try:
                image = WebDriverWait(DRIVER, 5).until(
                    expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'img.iPVvYb'))
                )
                image_link = image.get_attribute('src')
            except TimeoutException:
                # Image encrypted, saving thumbnail instead
                image_link = thumbnail_link

            links.add(image_link)
            print(f'Scraped link {len(links)}: {image_link}')

            if len(links) >= MAX_SCRAPED_LINKS:
                break

        if len(links) == prev_links_len:
            print('No more new images')
            break

finally:
    with open(SCRAPED_LINKS_PATH, 'a') as f:
        for link in links:
            f.write(link + '\n')
    print(f'Wrote {len(links)} links to {SCRAPED_LINKS_PATH}')
