import base64
from google_images_download import google_images_download
import click
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import binascii
import requests

def get_image(url):
    resp = requests.get(url)
    return resp.content


def save_images(directory, base_name, images):
    for i, image in enumerate(images):
        if image.startswith('data:image/jpeg;base64'):
            try:
                imgdata = base64.b64decode(image.split('base64,')[-1])
            except binascii.Error as e:
                print(f'Failed {i}th image. {e}')
                continue
        elif image.startswith('http'):
            try:
                imgdata = get_image(image)
            except Exception as e:
                print('Unable to download'.format(e))
                print(e)
        else:
            print(f'wrong image {i}')
            continue
        filename = f'{directory}/{base_name}_{i}.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)
        if i % 50 == 0:
            print(f'completed {i} images')
    print(f'{len(images)} to {directory}')


def get_images(keyword, limit):
    GOOGLE_URL = "https://www.google.co.in/search?q=%s&source=lnms&tbm=isch"
    query = keyword.split()
    query = '+'.join(query)
    url = GOOGLE_URL % query
    # options = webdriver.ChromeOptions()

    browser = webdriver.Firefox()#chrome_options=options)

    browser.get(url)
    time.sleep(1)

    elem = browser.find_element_by_tag_name("body")

    # scroll to fire the infinite scroll event and load more images
    no_of_pages_down = 10 if limit < 300 else 100
    while no_of_pages_down:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        no_of_pages_down -= 1

    time.sleep(2)
    encoded_images = []
    #rg_i Q4LuWd 
    images = browser.find_elements_by_class_name("tx8vtf")
    for image in images:
        val = image.get_attribute('src')
        if val:
            encoded_images.append(val)
    browser.close()
    return encoded_images[:limit]


@click.command()
@click.option('--keyword', type=str)
@click.option('--limit', type=int, default=80)
@click.option('--dest', type=str)
def main(keyword, limit, dest):
    encoded_images = get_images(keyword, limit)
    print(f'Downloaded {len(encoded_images)}')
    base_name = keyword.replace(' ', '_')
    save_images(dest, base_name, encoded_images)

if __name__ == "__main__":
    main()
