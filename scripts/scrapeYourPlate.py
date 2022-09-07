#Selenium INIT
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


#Chrome Driver INIT
s=Service(executable_path='chromedriver') #Fix this to correct location if running in local machine.
browser = webdriver.Chrome(service=s, options=options)
url = 'https://rdeapps.stanford.edu/dininghallmenu/'
#driver = webdriver.Chrome('chromedriver')


#Firestore INIT
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


import datetime


#Select location_ID as Location
def chooseLocation(location_ID):
    browser.find_element(By.NAME, 'ctl00$MainContent$lstLocations').click()
    browser.find_element(By.XPATH, '//*[@id="MainContent_lstLocations"]/option[' + str(location_ID) + ']').click()


#Select meal_ID as Meal
def chooseMeal(meal_ID):
    browser.find_element(By.NAME, 'ctl00$MainContent$lstMealType').click()
    browser.find_element(By.XPATH, '//*[@id="MainContent_lstMealType"]/option[' + str(meal_ID) + ']').click()


#Processes ingredient text and returns list of high-level ingredients (with lower-level ones inccluded in ingredient strigns)
def process(ingredients):
    out = []
    last = 0
    search = 0
    i = 0
    while i < len(ingredients):
        if search == 0 and ingredients[i] == ",":
            out.append(ingredients[last:i])
            last = i + 2
        elif ingredients[i] == '(':
            search += 1
        elif ingredients[i] == ')':
            search -= 1 
        else:
            pass
        i += 1
    return out
        

#scrapes text into dictionary bigIngredientList. Each key is a dish with values as a nested list of ingredients and index.
def scrape():
    bigIngredientList = {}
    dishes = browser.find_elements(By.CSS_SELECTOR, "div.clsMenuItem")
    i = 0
    for dish in dishes:
        name = dish.find_element(By.CSS_SELECTOR, "span.clsLabel_Name")        
        ingredients = dish.find_element(By.CSS_SELECTOR, "span.clsLabel_Ingredients").text
        vegetarian = False
        if "clsV_Row" in dish.get_attribute("class"):
            vegetarian = True
        vegan = False
        if "clsVGN_Row" in dish.get_attribute("class"):
            vegan = True
        gluten_free = False
        if "clsGF_Row" in dish.get_attribute("class"):
            gluten_free = True
        start = ingredients.find(':')
        ingredients = ingredients[start + 2:]
        ingredients = process(ingredients)
        if name.text not in bigIngredientList:
            bigIngredientList[name.text] = [ingredients, i, vegetarian, vegan, gluten_free]
        i += 1 #We're not getting index==0 foods
    return bigIngredientList


#adds bigIngredientList to Firebase
def add_new_meal(bigIngredientList, meal_ID):
    #today = date.today()
    dateNow = datetime.date.today() 
    meal = whatMeal(meal_ID)
    for ingredient in bigIngredientList:
        #Checks for duplicates and abandons adding the dish if there is a duplicate.
        duplicates = db.collection('FoodsActual').where(u'Date', u'==', u"" + str(dateNow) +"").where(u'Meal', u'==', u"" + meal + "").where(u'Dish', u'==', u"" + ingredient + "")
        docs = duplicates.stream()
        count = 0
        for doc in docs:
            count += 1
        if count == 0:
            db.collection('FoodsActual').add({'Date':str(dateNow), 
                                    'Meal':meal, 
                                    'Dish':ingredient, 
                                    'Ingredients':bigIngredientList[ingredient][0], 
                                    'Index':bigIngredientList[ingredient][1],
                                    'Vegetarian':bigIngredientList[ingredient][2],
                                    'Vegan':bigIngredientList[ingredient][3],
                                    'Gluten Free':bigIngredientList[ingredient][4]})


def whatMeal(meal_ID):
    if meal_ID == 2:
        meal = 'breakfast'
    elif meal_ID== 3:
        meal = 'lunch'
    elif meal_ID == 4:
        meal = 'dinner'
    elif meal_ID == 5:
        meal = 'brunch'
    return meal

"""
#For eventual inclusion of all dining halls.
def whatLocation(location_ID):
    if location_ID == 2:
       location = 'Arrillaga'
    elif meal_ID== 3:
        meal = 'lunch'
    elif meal_ID == 4:
        meal = 'dinner'
    elif meal_ID == 5:
        meal = 'brunch'
    return meal
"""



if __name__ == "__main__":
    browser.get(url)
    for location_ID in range(2,3): #To be improved with all locations, perhaps
        chooseLocation(location_ID)
        for meal_ID in range(2,6):
            chooseMeal(meal_ID)
            #add_new_meal(scrape(), meal_ID)
    browser.close()
