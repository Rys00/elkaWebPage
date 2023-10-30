const quineFunctions = document.getElementById("quineFunctions");
var quineFunctionsCount = 0;
document.getElementById("addQuineFunction").addEventListener("click", function (e) {
    e.preventDefault();
    addQuineFunction();
});

function addQuineFunction() {
    quineFunctionsCount += 1;
    document.getElementById("quineFunctionAmount").value = quineFunctionsCount
    const quineFunction = document.createElement("div");
    quineFunction.innerHTML = `
    <h4>Funkcja ${quineFunctionsCount}:</h4>
    <div class="item">
        Lista jedynek funkcji (oddzielaj ";"):
        <input type="text" name="ones${quineFunctionsCount}" id="ones${quineFunctionsCount}">
    </div>
    <div class="item">
        Nieokreślone wartości (oddzielaj ";"):
        <input type="text" name="wildcards${quineFunctionsCount}" id="wildcards${quineFunctionsCount}">
    </div>
    `;
    quineFunctions.appendChild(quineFunction);
}

addQuineFunction()