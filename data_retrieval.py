from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from urllib.request import urlretrieve


class AutoEvolutionScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.brands = {}
        self.driver.get("https://www.autoevolution.com/cars/")
        self.driver.find_element(
            By.CSS_SELECTOR, ".css-1k09jk"
        ).click()  # Accept cookies

    def get_brands(self):
        brands = self.driver.find_elements(
            By.CSS_SELECTOR, 'div[itemType="https://schema.org/Brand"]'
        )
        for brand in brands:
            link = brand.find_element(By.CSS_SELECTOR, "a")
            self.brands[link.get_attribute("href")] = {
                "name": link.get_attribute("title"),
                "cars": [],
            }
        return self.brands

    def get_cars_for_brand(self, brand_url):
        if not os.path.isdir(self.brands[brand_url]["name"]):
            os.mkdir(self.brands[brand_url]["name"])
        self.driver.get(brand_url)
        cars = self.driver.find_elements(By.CSS_SELECTOR, ".carmod")
        links = []
        for car in cars:
            link = car.find_element(By.CSS_SELECTOR, "a")
            title = link.get_attribute("title").replace(" specs and photos", "")
            title = title[title.find("  ") + 2 :]
            links.append((title, link.get_attribute("href")))
        for model, link in links:
            if not os.path.isdir(self.brands[brand_url]["name"] + "/" + model):
                os.mkdir(self.brands[brand_url]["name"] + "/" + model)
            self.driver.get(link)
            time.sleep(1)
            generations = self.driver.find_elements(By.CSS_SELECTOR, ".fsz17")
            gens = []
            for gen in generations:
                title = gen.get_attribute("title")
                title = title[title.find("  ") + 2 :]
                gens.append((title, gen.get_attribute("href")))
            for name, generation in gens:
                if not os.path.isdir(
                    self.brands[brand_url]["name"] + "/" + model + "/" + name
                ):
                    os.mkdir(self.brands[brand_url]["name"] + "/" + model + "/" + name)
                self.driver.get(generation)
                image_base_link = self.driver.find_element(
                    By.CSS_SELECTOR, ".s_gallery"
                ).get_attribute("href")[
                    :-5
                ]  # Add .jpg at the end!
                pics_number = (
                    self.driver.find_element(By.CSS_SELECTOR, ".galbig")
                    .find_element(By.TAG_NAME, "span")
                    .text
                ).split()[0]
                image_links = [
                    image_base_link + str(i + 1) + ".jpg"
                    for i in range(int(pics_number))
                ]
                for image in image_links:
                    urlretrieve(
                        image,
                        self.brands[brand_url]["name"]
                        + "/"
                        + model
                        + "/"
                        + name
                        + "/"
                        + image.split("/")[-1],
                    )
                print(image_links)
        return self.brands


if __name__ == "__main__":
    aes = AutoEvolutionScraper()
    brands = aes.get_brands()
    for brand in brands.keys():
        aes.get_cars_for_brand(brand)
        break
