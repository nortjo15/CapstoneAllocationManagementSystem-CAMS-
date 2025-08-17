// Get references to the HTML elements
console.log("JavaScript file loaded successfully!");  

var i = 0;
function buttonClick() {
    document.getElementById('inc').value = ++i;
}

function createRound() {
}

const popUpForm = document.getElementById("popUpForm");
var button = document.getElementById("createRound");
//Form Pop-Up//
//button.onclick = () => {window.open('hello!')};//

//button function//
button.addEventListener("click", function() {
  document.getElementById("popUpForm").style.display = "block";
 
});