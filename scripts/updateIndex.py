import os
import datetime
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


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
Returns current date in pacific time.
"""
def getDatePT(dateTime):
    hour = int(dateTime[11:13])
    if hour < 7:
        return str(datetime.date.today() - timedelta(days=1))
    return str(datetime.date.today())


""""
Returns list of dishes on the specified date and for the specified meal. Takes in the current hour to compute the correct date.
"""
def getDishes(date, meal):
    foodsActual = db.collection(u'FoodsActual')
    if meal == 'lunch': 
        meals = foodsActual.where(u'Date', u'==', u"" + date +"").where(u'Meal', u'==', u'lunch').order_by('Index')
    elif meal == 'brunch':
        meals = foodsActual.where(u'Date', u'==', u"" + date +"").where(u'Meal', u'==', u'brunch').order_by('Index')
    else:
        meals = foodsActual.where(u'Date', u'==', u"" + date +"").where(u'Meal', u'==', u'dinner').order_by('Index')
    docs = meals.stream()
    final = []
    for doc in docs:
        final.append((doc.to_dict()['Dish']).lower())
    return final #implement meal logic


"""
Creates string of HTML to be inserted, which is comprised of the first two dishes listed.
"""
def writeEntrees(dishes):
    entrees = """
        <p class="p-4 text-xl">
            %s
        </p>
        <p class="p-4 text-xl">
            %s
        </p>
        """ 
    return(entrees % (dishes[0], dishes[1]))

"""
Creates string of HTML to be inserted, which is comprised of all but the first two dishes listed.
"""
def writeSides(dishes):
    sides = ""
    new = ""
    newish = ""
    for side in dishes[2:]:
        new = """
        <p class="p-4 text-xl">
            %s
        </p>
        """
        newish = new % side
        sides = sides + newish
    return(sides)

"""
Creates new index.html file comprised of the proper meal and dishes.
"""
def writeFile(dishes, meal):
    f = open('pbulic/index.html','w')
    message = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>entree.today</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="output.css" rel="stylesheet"> 
        <link rel="shortcut icon" type="image/x-icon" href="favicon.ico">
        <script>if(!sessionStorage.getItem("_swa")&&document.referrer.indexOf(location.protocol+"//"+location.host)!== 0){fetch("https://counter.dev/track?"+new URLSearchParams({referrer:document.referrer,screen:screen.width+"x"+screen.height,user:"NoahSchechter",utcoffset:"-7"}))};sessionStorage.setItem("_swa","1");</script>
    </head>
    <body>
       <div class="bg-no-repeat bg-cover bg-opacity-20 sm:bg-right-bottom"
        style="background-image: url(FinalFinalFinal50.png)">
        <div class="p-4 md:grid md:grid-cols-5">
            <div class="md:col-start-2 md:col-end-5"> 
                <div>
                    <h1 class="heading text-6xl font-bold md:text-center" id="top">%s</h1>
                    <div id="info" class="md:text-center md:text-xl italic">
                    %s
                    </div>
                </div>
                <div class="py-6" >
                    <h1 class="heading py-2 font-bold md:text-center" id="entree_header" align="center">ENTREES</h1>
                    <div id="entrees" class="md:text-center md:text-xl">
                        %s
                    </div>
                </div>
                <div  class="py-6" >
                    <h1 class="heading font-bold py-2 md:text-center" id="sides_header" align="center">SIDES</h1>
                    <div  id="sides" class="md:text-center md:text-xl">
                        %s
                    </div>
                </div>
                <div class="footer pt-8 text-xs" align="center">
                    <p class="text-xs"><i>Background image recolored from original by Ward & Blohme, Architects. Memorial Church. August 1, 1911. Sourced from <u><a href="https://searchworks.stanford.edu/view/zy932bd0293">Stanford Library</a></u>. <a target="_blank" href="https://icons8.com/icon/59873/restaurant">Restaurant</a> icon by <a target="_blank" href="https://icons8.com">Icons8</a>.</i></p>
                    <p align="center" class="pt-4 text-xs"><u><a href="about.html">About</a></U></p>
                    <p align="center" class="pt-4 text-xs">Built by <a href="https://noah.garden">Noah Schechter</a>.</p>
                </div>
            </div>
        </div>
    </div> 
    </body>
</html>
"""
    info = ""
    if meal == 'brunch':
        info = 'This is supposed to be the lunch part of brunch. Expect breakfast food too.'
    whole = message % (meal.upper(), info, writeEntrees(dishes), writeSides(dishes))
    f.write(whole)
    f.close()


def writeAPI(date, meal, dishes):
    f = open('public/api.json','w')
    message = """{"date": %s, "meal": %s, "entrees": %s, "sides": %s}"""
    full = message % (date, meal, dishes[0:2], dishes[2:])
    f.write(full)
    f.close()

def deployFile():
    os.system("npm install -g firebase-tools")
    key = os.environ.get('FIREBASE_TOKEN')
    os.system(f'firebase deploy --token {key}')
    
if __name__ == "__main__":
    dateTime = str(datetime.datetime.utcnow())
    date = getDatePT(dateTime)
    meal = getMeal(dateTime)
    dishes = getDishes(date, meal)
    writeFile(dishes, meal)
    writeAPI(date, meal, dishes)
    deployFile()