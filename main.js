const quineFunctions = document.getElementById("quineFunctions");
const quineFunctionAmount = document.getElementById("quineFunctionAmount");
console.log(quineFunctionAmount.value);
document.getElementById("addQuineFunction").addEventListener("click", function () {addQuineFunction();});
document.getElementById("removeQuineFunction").addEventListener("click", function () {removeQuineFunction();});

function addQuineFunction() {
    quineFunctionAmount.value = parseInt(quineFunctionAmount.value)+1
    let i = quineFunctionAmount.value
    const quineFunction = document.createElement("div");
    quineFunction.innerHTML = `
    <h4>Funkcja ${i}:</h4>
    <div class="item">
        Lista jedynek funkcji (oddzielaj ";"):
        <input type="text" name="ones${i}" id="ones${i}">
    </div>
    <div class="item">
        Nieokreślone wartości (oddzielaj ";"):
        <input type="text" name="wildcards${i}" id="wildcards${i}">
    </div>
    `;
    quineFunctions.appendChild(quineFunction);
}

function removeQuineFunction() {
    quineFunctionAmount.value = parseInt(quineFunctionAmount.value)-1
    quineFunctions.removeChild(quineFunctions.lastChild);
}

let copy = parseInt(quineFunctionAmount.value)
quineFunctionAmount.value = 0
for(let i = 0; i < copy; i++) {
    addQuineFunction()
}

quineFunctionAmount.addEventListener("change", function() {
    quineFunctions.innerHTML = ""
    let copy = parseInt(quineFunctionAmount.value)
    quineFunctionAmount.value = 0
    for(let i = 0; i < copy; i++) {
        addQuineFunction()
    }
});