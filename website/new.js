const firebaseConfig = {
  apiKey: "AIzaSyB_TJfc_ao1rlA4TgzGSnscWgL9_KcMQuM",
  authDomain: "bettermenu-75f1f.firebaseapp.com",
  databaseURL: "https://bettermenu-75f1f-default-rtdb.firebaseio.com",
  projectId: "bettermenu-75f1f",
  storageBucket: "bettermenu-75f1f.appspot.com",
  messagingSenderId: "606440182954",
  appId: "1:606440182954:web:fa55eeb32609e0578eacd3",
  measurementId: "G-TDTH4NEZKH"
};


import { initializeApp } from "https://www.gstatic.com/firebasejs/9.4.0/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/9.4.0/firebase-firestore.js";
import { where, query, orderBy, limit, getDocs, collection } from "https://www.gstatic.com/firebasejs/9.4.0/firebase-firestore.js";  


const app = initializeApp(firebaseConfig);

const db = getFirestore(app);
const dateTime = new Date();

function makeTime() {
  var year = dateTime.getFullYear();
  var month = parseInt(dateTime.getMonth()) + 1;
  if (parseInt(month) < 10) {
    month = 0 + String(month)
  }
  var day = dateTime.getDate();
  if (parseInt(day) < 10) {
    day = 0 + String(day)
  }
  const date = String(year) + '-' + String(month) + '-' + String(day);
  return String(date);
}


function whatMeal() {
  var hours = dateTime.getHours();
  if (hours < 17) {
    return "lunch";
  }
  return "dinner";
}


var date = makeTime()


async function build(meal, course) {
  var dishes =[]
  if (course == "entrees") {
    dishes = await getDocs(query(collection(db, "FoodsActual"), where('Date', '==', `${date}`), where('Meal', '==', `${meal}`), orderBy('Index'), limit(2)));
  }
  else if (course == "sides") {
    dishes = await getDocs(query(collection(db, "FoodsActual"), where('Date', '==', `${date}`), where('Meal', '==', `${meal}`), where('Index', '>=', 2)));
  }
  else {
    dishes = [1]
  }
  let contents = document.getElementById(`${course}`); 
  dishes.forEach(dish => {
    let food = document.createElement("p");
    food.innerText = dish.data().Dish.toLowerCase();
    food.className = "p-4 text-xl";
    contents.appendChild(food);
  });
}


function construct(meal) {
  if (meal == "lunch" && (dateTime.getDay() == 6 || dateTime.getDay() == 0)) {
      let top = document.getElementById("top");
      top.innerText = "BRUNCH";
      let contents = document.getElementById("info");
      let food = document.createElement("p");
      food.innerText = "This is supposed to be the lunch part of brunch. Expect breakfast food too. ";
      contents.appendChild(food);
    }
  else if
  else {
    let top = document.getElementById("top");
    top.innerText = `${meal.toUpperCase()}`;
  }
  let entree_header = document.getElementById("entree_header");
  entree_header.innerText = 'ENTREES';
  build(meal, "entrees")
  let sides_header = document.getElementById("sides_header");
  sides_header.innerText = "SIDES";
  build(meal, "sides")
  }

construct(whatMeal());
