from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from urllib.request import urlretrieve
from multiprocessing import Pool


class AutoEvolutionScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.brands = []
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
            self.brands.append(
                {
                    "name": link.get_attribute("title"),
                    "cars": [],
                    "url": link.get_attribute("href"),
                }
            )
        return self.brands

    def get_cars_for_brand(self, brand):
        if not os.path.isdir(brand["name"]):
            os.mkdir(brand["name"])
        else:
            return  # If the folder exists, skip!
        self.driver.get(brand["url"])
        cars = self.driver.find_elements(By.CSS_SELECTOR, ".carmod")
        links = []
        for car in cars:
            link = car.find_element(By.CSS_SELECTOR, "a")
            title = link.get_attribute("title").replace(" specs and photos", "")
            title = title[title.find("  ") + 1 :]
            links.append((title, link.get_attribute("href")))
        for model, link in links:
            if not os.path.isdir(brand["name"] + "/" + model):
                os.mkdir(brand["name"] + "/" + model)
            self.driver.get(link)
            time.sleep(1)
            generations = self.driver.find_elements(By.CSS_SELECTOR, ".fsz17")
            gens = []
            for gen in generations:
                title = gen.get_attribute("title")
                title = title[title.find(brand["name"]) :]
                gens.append((title, gen.get_attribute("href")))
            for name, generation in gens:
                if not os.path.isdir(brand["name"] + "/" + model + "/" + name):
                    os.mkdir(brand["name"] + "/" + model + "/" + name)
                elif os.listdir(brand["name"] + "/" + model + "/" + name):
                    continue  # We already have images saved
                self.driver.get(generation)
                image_base_link = self.driver.find_element(
                    By.CSS_SELECTOR, ".s_gallery"
                ).get_attribute(
                    "href"
                )  # Add .jpg at the end!
                image_base_link = image_base_link[: image_base_link.find("_") + 1]
                pics_number = (
                    self.driver.find_element(By.CSS_SELECTOR, ".galbig")
                    .find_element(By.TAG_NAME, "span")
                    .text
                ).split()[0]
                image_links = [
                    image_base_link + str(i + 1) for i in range(int(pics_number))
                ]
                for image in image_links:
                    try:
                        urlretrieve(
                            image + ".jpg",
                            brand["name"]
                            + "/"
                            + model
                            + "/"
                            + name
                            + "/"
                            + image.split("/")[-1]
                            + ".jpg",
                        )
                    except:
                        try:
                            print("Trying jpeg")
                            urlretrieve(
                                image + ".jpeg",
                                brand["name"]
                                + "/"
                                + model
                                + "/"
                                + name
                                + "/"
                                + image.split("/")[-1]
                                + ".jpeg",
                            )
                        except Exception as e:
                            print(f"Skipped {image + '.jpeg'}, error: {e}")
                        pass
        return self.brands


def retrieve_brand(brand):
    print(f"Retrieving {brand['name']}")
    scraper = AutoEvolutionScraper()
    scraper.get_cars_for_brand(brand)


if __name__ == "__main__":
    aes = AutoEvolutionScraper()
    brands = aes.get_brands()
    with Pool(8) as p:
        p.map(retrieve_brand, brands)
