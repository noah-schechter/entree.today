import os
import datetime
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def getMeal():
    dateTime = str(datetime.datetime.utcnow())
    hour = int(dateTime[11:13])
    if hour - 7 > 16 or hour - 7 < 0:
        return 'dinner'
    else:
        if datetime.datetime.today().weekday() > 4:
            return 'brunch'
    return 'lunch'
    
def getDatePDT(meal):
    if meal == 'lunch' or meal == 'brunch':
        return str(datetime.date.today())
    else:
        return str(datetime.date.today() - timedelta(days=1))


#returns ordered list of dishes
def getDishes(meal):
    dateNowStr = getDatePDT(meal)
    foodsActual = db.collection(u'FoodsActual')
    print(dateNowStr)
    if meal == 'lunch': 
        meals = foodsActual.where(u'Date', u'==', u"" + dateNowStr +"").where(u'Meal', u'==', u'lunch').order_by('Index')
    elif meal == 'brunch':
        meals = foodsActual.where(u'Date', u'==', u"" + dateNowStr +"").where(u'Meal', u'==', u'brunch').order_by('Index')
    else:
        meals = foodsActual.where(u'Date', u'==', u"" + dateNowStr +"").where(u'Meal', u'==', u'dinner').order_by('Index')
    docs = meals.stream()
    final = []
    for doc in docs:
        final.append((doc.to_dict()['Dish']).lower())
    return final #implement meal logic

def writeEntrees(dishes):
    entrees = """
        <p class="p-4 text-xl">
            %s
        </p>
        <p class="p-4 text-xl">
            %s
        </p>
        """ 
    print(dishes)
    return(entrees % (dishes[0], dishes[1]))

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

#Will (once implemented) write new html file to become new homepage 
def writeFile(dishes, meal):
    f = open('public/index.html','w')
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

def deployFile():
    os.system("npm install -g firebase-tools")
    key = os.environ.get('FIREBASE_TOKEN')
    os.system(f'firebase deploy --token {key}')
    
if __name__ == "__main__":
    meal = getMeal()
    print(meal)
    dishes = getDishes(meal)
    print(dishes)
    writeFile(dishes, meal)
    deployFile()