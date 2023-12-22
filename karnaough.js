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

function copy(button, value) {
    const copyText = document.createElement("input");
    copyText.value = value;
    button.appendChild(copyText);
    copyText.select();
    document.execCommand("copy");
    button.removeChild(copyText);
    button.style.setProperty("--opacity", 1);
    setTimeout(() => {
        button.style.setProperty("--opacity", 0);
    }, 2000);
}

let editable = urlParams.get('editable');
if (editable == 1) {
    editable = true;
    karnaughMap.classList.add("editable");
    const copyOnes = document.createElement("button");
    copyOnes.innerHTML = "Copy ones";
    copyOnes.addEventListener("click", (e) => {
        copy(e.target, ones.join(";"))
    })
    const copyWildcards = document.createElement("button");
    copyWildcards.innerHTML = "Copy wildcards";
    copyWildcards.addEventListener("click", (e) => {
        copy(e.target, wildcards.join(";"))
    })
    const box = document.createElement("div");
    box.appendChild(copyOnes);
    box.appendChild(copyWildcards);
    document.getElementById("container").appendChild(box);
}
else {
    editable = false
}

let vars = [];
try {
    vars = urlParams.get('vars');
    vars = vars.split(";")
    if (vars.length != amount) throw new Error;
}
catch {
    vars = [];
    for (let i = amount-1; i >= 0; i--) {
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

function updateURLParams() {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    urlParams.set("ones", ones.join(";"));
    urlParams.set("wildcards", wildcards.join(";"));
    history.replaceState(null, null, "?"+urlParams.toString());
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
            newCell.className = "one";
        } else if (wildcards.includes(idx)) {
            newCell.innerHTML = "<div class='content'>-</div>";
            newCell.className = "wildcard";
        }
        else {
            newCell.innerHTML = "<div class='content'>0</div>";
            newCell.className = "zero";
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

        if (!editable) { continue; }
        newCell.addEventListener("click", (e) => {
            const cell = e.target;
            if (cell.tagName == "DIV") {
                cell.parentElement.click();
                return;
            }
            const value = cell.getElementsByTagName("div")[0];
            if(value.innerHTML == "0") {
                value.innerHTML = "1";
                cell.className = "one";
                ones.push(idx);
            } else if(value.innerHTML == "1") {
                value.innerHTML = "-";
                cell.className = "wildcard";
                ones.pop(ones.indexOf(idx));
                wildcards.push(idx);
            } else if(value.innerHTML == "-") {
                value.innerHTML = "0";
                cell.className = "zero";
                wildcards.pop(ones.indexOf(idx));
            }
            updateURLParams();
        });
    }
    karnaughMap.appendChild(newRow);
}