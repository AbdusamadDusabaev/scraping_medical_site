import time
import requests
from bs4 import BeautifulSoup
from connect import get_injury_groups_parent_id
from connect import insert_into_table_injury_groups, insert_into_table_injuries
from connect import insert_into_treatment_descriptions, insert_into_methods_of_treatment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions


ua_chrome = " ".join(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                      "AppleWebKit/537.36 (KHTML, like Gecko)",
                      "Chrome/108.0.0.0 Safari/537.36"])
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={ua_chrome}")
options.add_argument("--headless")
headers = {"user-agent": ua_chrome}
domain = "https://surgeryreference.aofoundation.org"
start_url = "https://surgeryreference.aofoundation.org/orthopedic-trauma/adult-trauma"
image_count = 0
timeout = 50
position_count = 0


def convert_to_natural_language(tag):
    tag = str(tag)
    tag = tag.replace("</div>", "</div>\n").replace("</p>", "</p>\n")
    tag = tag.replace("</li>", "</li>\n").replace("</h3>", "</h3>\n")
    result = BeautifulSoup(tag, "lxml")
    result = result.text.strip().replace('"', "'")
    return result.strip()


def download_image(link):
    global image_count
    image_count += 1
    response = requests.get(link)
    image = response.content
    if ".jpg" in link:
        image_format = "jpg"
    elif ".png" in link:
        image_format = "png"
    else:
        image_format = "svg"
    path = f"images/{image_count}.{image_format}"
    with open(path, "wb") as file:
        file.write(image)
    return path


def main():
    global position_count
    injury_parent_id = 0
    methods_of_treatment_parent_id = 0
    treatments_parent_id = 0
    browser = webdriver.Chrome(options=options)
    wait_driver = WebDriverWait(driver=browser, timeout=timeout)
    browser.set_window_size(width=1920, height=1080)
    try:
        response = requests.get(url=start_url, headers=headers)
        bs_object = BeautifulSoup(response.content, "lxml")
        limb_part_objects = bs_object.find(name="div", class_="skeleton").find_all(name="a")
        for limb_part_object in limb_part_objects:
            try:
                limb_part_link = domain + limb_part_object["href"]
                limb_part_name = " ".join(limb_part_object.text.strip().split("_"))
                injury_group_parent_id = get_injury_groups_parent_id(name=limb_part_name)["id"]
                browser.get(url=limb_part_link)
                wait_driver.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "diagnoses__section")))
                response = browser.page_source
                bs_object = BeautifulSoup(response, "lxml")
                injury_group_sections = bs_object.find_all(name="section", class_="diagnoses__section")
                for injury_group_section in injury_group_sections:
                    try:
                        injury_group_name = injury_group_section.h2
                        if injury_group_name is not None:
                            injury_group_name = injury_group_name.text.strip().replace('"', "'")
                            insert_into_table_injury_groups(parent_id=injury_group_parent_id, name=injury_group_name)
                            injuries = injury_group_section.find_all(name="article", class_="diagnos")
                            injury_parent_id += 1
                            for injury in injuries:
                                try:
                                    injury_name = injury.h3.text.strip().replace('"', "'")
                                    injury_link = domain + injury.find(name="a", class_="diagnos__footer-link_default")["href"]
                                    browser.get(url=injury_link)
                                    wait_driver.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "detail__image")))
                                    response = browser.page_source
                                    bs_object = BeautifulSoup(response, "lxml")
                                    injury_image_link = bs_object.find(name="div", class_="detail__image")
                                    if injury_image_link is not None:
                                        injury_image_link = injury_image_link.img["src"]
                                        injury_image = download_image(link=injury_image_link)
                                    else:
                                        injury_image = None
                                    injury_description = str(bs_object.find(name="div", class_="detail__description")).replace('"',
                                                                                                                               "'")
                                    insert_into_table_injuries(parent_id=injury_parent_id, name=injury_name,
                                                               description=injury_description, image=injury_image)
                                    methods_of_treatment_objects = injury.find_all(name="a", class_="diagnos__footer-link_primary")
                                    methods_of_treatment_parent_id += 1
                                    for methods_of_treatment_object in methods_of_treatment_objects:
                                        try:
                                            methods_of_treatment_object_link = domain + methods_of_treatment_object["href"]
                                            browser.get(url=methods_of_treatment_object_link)
                                            wait_driver.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "collapsed__control")))
                                            read_full_description_buttons = browser.find_elements(By.CLASS_NAME, "collapsed__control")
                                            for read_full_description_button in read_full_description_buttons:
                                                browser.execute_script("arguments[0].click();", read_full_description_button)
                                                time.sleep(1)
                                            response = browser.page_source
                                            bs_object = BeautifulSoup(response, "lxml")
                                            methods_of_treatments = bs_object.find_all(name="article", class_="treatment")
                                            for mot in methods_of_treatments:
                                                try:
                                                    mot_name = mot.h2.text.strip().replace('"', "'")
                                                    mot_image_link = mot.find(name="div", class_='treatment__graphic').img["src"]
                                                    mot_image = download_image(link=mot_image_link)
                                                    mot_skill = mot.find(name="a", class_='gauge cursor-pointer').ul
                                                    mot_skill_level = mot_skill.find_all(name="li",
                                                                                         class_="gauge__list-item gauge__list-item_active")
                                                    mot_skill_level = len(mot_skill_level)
                                                    mot_equipment = mot.find_all(name="a", class_='gauge cursor-pointer')[1].ul
                                                    mot_equipment = mot_equipment.find_all(name="li",
                                                                                           class_="gauge__list-item gauge__list-item_active")
                                                    mot_equipment = len(mot_equipment)
                                                    mot_title = str(mot.find(name="div", class_="treatment__copy").h3).replace('"', "'")
                                                    mot_description = str(mot.find(name="div", class_="collapsed__content")).replace('"', "'")
                                                    mot_description = mot_title + "\n" + mot_description
                                                    insert_into_methods_of_treatment(parent_id=methods_of_treatment_parent_id, name=mot_name,
                                                                                     skill_level=mot_skill_level, equipment=mot_equipment,
                                                                                     description=mot_description, image=mot_image)
                                                    treatment_description_link = mot.find(name="a", class_="treatment__footer-link_primary")
                                                    treatment_description_link = domain + treatment_description_link["href"]
                                                    browser.get(url=treatment_description_link)
                                                    wait_driver.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "decks")))
                                                    response = browser.page_source
                                                    bs_object = BeautifulSoup(response, "lxml").find(name="div", class_='decks')
                                                    treatments_parent_id += 1
                                                    phases = bs_object.find_all(name="h2")
                                                    for phase in phases:
                                                        phase = str(phase).replace('"', "'")
                                                        insert_into_treatment_descriptions(parent_id=treatments_parent_id,
                                                                                           name="Phase", image=None,
                                                                                           description=phase)
                                                    treatment_paragraphs = bs_object.find_all(name="div", class_="detail__body")
                                                    for treatment_paragraph in treatment_paragraphs:
                                                        try:
                                                            treatment_description = treatment_paragraph.div.div
                                                            treatment_description = str(treatment_description).replace('"', "'")
                                                            treatment_name = treatment_paragraph.h3
                                                            if treatment_name is not None:
                                                                treatment_name = treatment_name.text.strip().replace('"', "'")
                                                            else:
                                                                treatment_name = treatment_paragraph.b
                                                                if treatment_name is not None:
                                                                    treatment_name = treatment_name.text.strip().replace('"', "'")
                                                            treatment_image = treatment_paragraph.img
                                                            if treatment_image is not None:
                                                                treatment_image_link = treatment_image["src"]
                                                                treatment_image = download_image(link=treatment_image_link)
                                                            insert_into_treatment_descriptions(parent_id=treatments_parent_id,
                                                                                               name=treatment_name, image=treatment_image,
                                                                                               description=treatment_description)
                                                            position_count += 1
                                                            print(f"Обработано {position_count} записей в таблицу treatment_descriptions")
                                                            print()
                                                        except Exception as ex:
                                                            with open("logs.txt", "a", encoding="utf-8") as file:
                                                                file.write(f"{ex}\n")
                                                            continue
                                                except Exception as ex:
                                                    with open("logs.txt", "a", encoding="utf-8") as file:
                                                        file.write(f"{ex}\n")
                                                    continue
                                        except Exception as ex:
                                            with open("logs.txt", "a", encoding="utf-8") as file:
                                                file.write(f"{ex}\n")
                                            continue
                                except Exception as ex:
                                    with open("logs.txt", "a", encoding="utf-8") as file:
                                        file.write(f"{ex}\n")
                                    continue
                    except Exception as ex:
                        with open("logs.txt", "a", encoding="utf-8") as file:
                            file.write(f"{ex}\n")
                        continue
            except Exception as ex:
                with open("logs.txt", "a", encoding="utf-8") as file:
                    file.write(f"{ex}\n")
                continue
    finally:
        browser.close()
        browser.quit()


if __name__ == "__main__":
    print("[INFO] Парсер запущен")
    main()
