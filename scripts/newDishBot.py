#Firestore INIT
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import datetime
dateTime = str(datetime.datetime.utcnow())

cred = credentials.Certificate('/Users/noahschechter/Documents/Web/PrettyMenu/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
foodsActual = db.collection(u'FoodsActual')

"""
Returns boolean indicating if a dish has been served since approx April 2022. 
False indicates the dish is new, true indicates the dish has been served before.
"""
def isDuplicate(dish):
    duplicates = foodsActual.where(u'Dish', u'==', u"" + dish +"")
    duplicates = duplicates.stream()
    count = 0
    for duplicate in duplicates:
        count +=1
    if count > 0:
        return True
    return False


"""
Returns current date in pacific time.
"""
def getDatePT(dateTime):
    hour = int(dateTime[11:13])
    if hour < 7:
        return str(datetime.date.today() - timedelta(days=1))
    return str(datetime.date.today())


"""
Returns meal (lunch or dinner) based on time of day. If its before 4 pm, returns lunch (or brunch if a weekend). Otherwise returns dinner.
"""
def getMeal(dateTime):
    hour = int(dateTime[11:13])
    if hour == 23 or (hour >= 0 and hour < 7):
        return 'dinner'
    elif datetime.datetime.today().weekday() > 4:
            return 'brunch'
    return 'lunch'


"""
Returns list of dishes on the specified date and for the specified meal. Takes in the current hour to compute the correct date.
"""
def getDishesTweet(date, meal):
    foodsActual = db.collection(u'FoodsActual')
    if meal == 'lunch' or meal == 'brunch':  #will display the lunch. parts of brunch
        meals = foodsActual.where(u'Date', u'==', u"" + date +"").where(u'Meal', u'==', u'lunch').order_by('Index')
    else:
        meals = foodsActual.where(u'Date', u'==', u"" + date +"").where(u'Meal', u'==', u'dinner').order_by('Index')
    docs = meals.stream()
    final = []
    for doc in docs:
        dish = doc.to_dict()['Dish']
        if dish not in final: #Protect against displaying duplicates in databse, because WayScript likes to scrape twice sometimes.
            final.append(dish)
    return final #implement meal logic

#Figure out how to make a Twitter bot here.
def tweet(dish):
    print(dish) #This is placeholder language until i build the bort
        
if __name__ == "__main__":
    dateTime = str(datetime.datetime.utcnow())
    date = getDatePT(dateTime)
    meal = getMeal(dateTime)
    dishes = getDishesTweet(date, meal) 
    for dish in dishes:
        if not isDuplicate(dish):
            tweet(dish)
#Note: this shares a lot of code with updateIndex.py. I can merge them, 
# but will need two alternate getDishes functions, because the one in updateIndex.py
#makes things lowercase, which prevents me from properly querying them. 
# I'll use this doc for testing, then paste in the getDishesTweet and the following lines into the updateIndex.py:
"""
dishes = getDishesTweet(date, meal) 
    for dish in dishes:
        if not isDuplicate(dish):
            tweet(dish)
"""