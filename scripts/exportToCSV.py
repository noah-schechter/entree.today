#Firestore INIT
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("/Users/noahschechter/Documents/Web/PrettyMenu/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
Foods = db.collection(u'Foods')
docs = Foods.stream()

#CSV INIT
import csv



if __name__ == "__main__":
    with open('Foods.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Ingredient', 'Dish', 'Meal', 'Date', 'Index', 'Vegetarian', 'Vegan', 'Gluten-Free'])
        for doc in docs:
            info = doc.to_dict()
            for i in range(0, len(info['Ingredients'])):
                writer.writerow([info['Ingredients'][i], info['Dish'], info['Meal'], info['Date'], info['Index'], info['Vegetarian'], info['Vegan'], info['Gluten Free']])

