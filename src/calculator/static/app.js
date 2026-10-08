const input = document.getElementById("expression");
const resultBox = document.getElementById("result");
const historyList = document.getElementById("history");

function append(text) {
  input.value += text;
  input.focus();
}

function showResult(text, isError = false) {
  resultBox.textContent = text;
  resultBox.classList.toggle("error", isError);
}

async function calculate() {
  const expression = input.value.trim();
  if (!expression) {
    return;
  }
  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression }),
    });
    const data = await response.json();
    if (!response.ok) {
      showResult(data.detail || "Ошибка вычисления", true);
      return;
    }
    showResult("= " + data.result_text);
    await loadHistory();
  } catch (error) {
    showResult("Сервер недоступен", true);
  }
}

async function loadHistory() {
  try {
    const response = await fetch("/api/history?limit=50");
    if (!response.ok) {
      return;
    }
    const data = await response.json();
    renderHistory(data.items);
  } catch (error) {
    /* сервер недоступен — оставляем историю как есть */
  }
}

function renderHistory(items) {
  historyList.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("li");
    empty.className = "empty";
    empty.textContent = "Пока пусто";
    historyList.appendChild(empty);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    const expr = document.createElement("span");
    expr.className = "expr";
    expr.textContent = item.expression;
    const val = document.createElement("span");
    val.className = "val";
    val.textContent = "= " + item.result;
    li.appendChild(expr);
    li.appendChild(val);
    li.addEventListener("click", () => {
      input.value = item.expression;
      input.focus();
    });
    historyList.appendChild(li);
  }
}

async function clearHistory() {
  try {
    await fetch("/api/history", { method: "DELETE" });
  } finally {
    await loadHistory();
  }
}

document.querySelectorAll("[data-insert]").forEach((button) => {
  button.addEventListener("click", () => append(button.dataset.insert));
});

document.getElementById("clear").addEventListener("click", () => {
  input.value = "";
  showResult("");
  input.focus();
});

document.getElementById("backspace").addEventListener("click", () => {
  input.value = input.value.slice(0, -1);
  input.focus();
});

document.getElementById("equals").addEventListener("click", calculate);
document.getElementById("clear-history").addEventListener("click", clearHistory);

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    calculate();
  }
});

loadHistory();
