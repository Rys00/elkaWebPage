const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const karnaughMap = document.getElementById("karnaughMap");


let amount = 4;
amount = urlParams.get('amount');
if (amount == null) {
    amount = 4
} else {
    amount = parseInt(amount);
}

let direction = "";
direction = urlParams.get('direction');
if (direction == null) {
    direction = "vertical"
}

let vars = [];
try {
    vars = urlParams.get('vars');
    vars = vars.split(";")
    if (vars.length != amount) throw new Error;
}
catch {
    vars = [];
    for (let i = amount; i > 0; i--) {
        vars.push(`x${i}`)
    }
}

let ones = [];
ones = urlParams.get('ones');
if (ones == null) {
    ones = []
} else {
    ones = ones.split(";")
}

let wildcards = [];
wildcards = urlParams.get('wildcards');
if (wildcards == null) {
    wildcards = []
} else {
    wildcards = wildcards.split(";")
}

let horizontal = parseInt(amount/2)
let vertical = parseInt(amount/2)
if (direction == "horizontal") {horizontal += amount % 2}
else {vertical += amount % 2}

function getGrayCodes(exponential) {
    if (exponential <= 0) return [];
    let codes = ["0", "1"];
    if (exponential == 1) return codes;
    for (let i = 1; i < exponential; i++) {
        let newCodes = [];
        codes = codes.reverse();
        for (let j = 0; j < codes.length; j++) {
            newCodes = ["0"+codes[j], ...newCodes, "1"+codes[j]];
        }
        codes = [...newCodes];
    }
    return codes
}

let horizontalCodes = getGrayCodes(horizontal);
let verticalCodes = getGrayCodes(vertical);

let axisColor = ["#f99", "#9f9", "#99f"]
let horizontalAxis = [];
let verticalAxis = [];
for (let i = 2; i<=horizontal; i++) {
    horizontalAxis.push(2**i)
}
for (let i = 2; i<=vertical; i++) {
    verticalAxis.push(2**i)
}

let newRow = document.createElement("tr");
let newCell = document.createElement("td");
let varsTop = ""
for (let i = vertical; i < amount; i++) {
    varsTop += ` ${vars[i]}`;
}
let varsLeft = ""
for (let i = 0; i < vertical; i++) {
    varsLeft += ` ${vars[i]}`;
}
newCell.setAttribute("varsTop", varsTop);
newCell.setAttribute("varsLeft", varsLeft);
newRow.appendChild(newCell);
for(let j = 0; j < 2**horizontal; j++) {
    let newCell = document.createElement("td");
    newCell.innerHTML = horizontalCodes[j];
    newRow.appendChild(newCell);
}
karnaughMap.appendChild(newRow);

for(let i = 0; i < 2**vertical; i++) {
    newRow = document.createElement("tr");
    newCell = document.createElement("td");
    newCell.innerHTML = verticalCodes[i];
    newRow.appendChild(newCell);
    for(let j = 0; j < 2**horizontal; j++) {
        newCell = document.createElement("td");

        let idx = `${parseInt(verticalCodes[i]+horizontalCodes[j], 2)}`;
        if (ones.includes(idx)) {
            newCell.innerHTML = "<div class='content'>1</div>";
            newCell.classList.add("one");
        } else if (wildcards.includes(idx)) {
            newCell.innerHTML = "<div class='content'>-</div>";
            newCell.classList.add("wildcard");
        }
        else {
            newCell.innerHTML = "<div class='content'>0</div>";
            newCell.classList.add("zero");
        }
        newCell.setAttribute("idx", idx);

        for (let a = 0; a < horizontalAxis.length; a++) {
            if (j != 0 && j % horizontalAxis[a] == 0) {
                newCell.classList.add("left");
                newCell.style.setProperty("--accentLeft", axisColor[a]);
            }
        }
        for (let a = 0; a < verticalAxis.length; a++) {
            if (i != 0 && i % verticalAxis[a] == 0) {
                newCell.classList.add("top");
                newCell.style.setProperty("--accentTop", axisColor[a]);
            }
        }
        
        newRow.appendChild(newCell);
    }
    karnaughMap.appendChild(newRow);
}