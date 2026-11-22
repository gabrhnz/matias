(function () {
  const dataNode = document.getElementById("lesson-data");
  if (!dataNode || !window.MatiLab) return;
  const data = JSON.parse(dataNode.textContent);
  const prompt = document.getElementById("prompt");
  const choices = document.getElementById("choices");
  const numberField = document.getElementById("number-field");
  const numberInput = document.getElementById("number-input");
  const hintButton = document.getElementById("hint-btn");
  const hint = document.getElementById("hint");
  const checkButton = document.getElementById("check-btn");
  const feedback = document.getElementById("feedback");
  const feedbackTitle = document.getElementById("feedback-title");
  const feedbackBody = document.getElementById("feedback-body");
  const nextButton = document.getElementById("next-btn");
  const stepLabel = document.getElementById("step-label");
  const stepBar = document.getElementById("step-bar");
  const practice = document.getElementById("practice");
  const done = document.getElementById("done");
  const score = document.getElementById("score");
  const nextLink = document.getElementById("next-link");

  let index = 0;
  let picked = "";
  let busy = false;
  let answered = false;
  const session = [];

  function problem() {
    return data.problems[index];
  }

  function render() {
    const item = problem();
    picked = "";
    answered = false;
    busy = false;
    prompt.textContent = item.prompt;
    stepLabel.textContent = "Práctica " + (index + 1) + " de " + data.total;
    stepBar.style.width = (index / data.total) * 100 + "%";
    choices.innerHTML = "";
    hint.hidden = true;
    feedback.hidden = true;
    checkButton.disabled = true;
    checkButton.hidden = false;
    hintButton.hidden = !item.hint;
    numberField.hidden = item.kind !== "number";
    numberInput.value = "";
    if (item.kind === "choice") {
      item.choices.forEach(function (choice) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "choice";
        button.textContent = choice.label;
        button.dataset.id = choice.id;
        button.addEventListener("click", function () {
          if (answered) return;
          picked = choice.id;
          choices.querySelectorAll(".choice").forEach(function (node) {
            node.classList.toggle("is-picked", node === button);
          });
          checkButton.disabled = false;
        });
        choices.appendChild(button);
      });
    }
    prompt.focus();
  }

  function answerValue() {
    return problem().kind === "number" ? numberInput.value.trim() : picked;
  }

  async function check() {
    if (busy || answered || !answerValue()) return;
    busy = true;
    checkButton.disabled = true;
    const person = window.MatiLab.student();
    try {
      const response = await fetch("/api/comprobar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lesson_id: data.id,
          problem_id: problem().id,
          answer: answerValue(),
          student_id: person.id,
          name: person.name,
          grade: person.grade,
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "No pudimos comprobar");
      answered = true;
      session.push(Boolean(result.correct));
      showResult(result);
      if (result.progress) window.MatiLab.remember(data.id, result.progress);
    } catch (error) {
      busy = false;
      checkButton.disabled = false;
      feedback.hidden = false;
      feedbackTitle.textContent = "Inténtalo otra vez";
      feedbackBody.textContent = "No pudimos comprobar la respuesta. Revisa tu conexión.";
      nextButton.hidden = true;
    }
  }

  function showResult(result) {
    checkButton.hidden = true;
    hintButton.hidden = true;
    feedback.hidden = false;
    feedbackTitle.textContent = result.correct ? "Correcto" : "Todavía no";
    feedbackBody.textContent = result.explain;
    nextButton.hidden = false;
    nextButton.textContent = index + 1 === data.total ? "Ver resultado" : "Siguiente";
    const selected = choices.querySelector(".is-picked");
    if (selected) selected.classList.add(result.correct ? "is-right" : "is-miss");
    if (!result.correct && problem().kind === "number") numberInput.classList.add("is-miss");
  }

  function finish() {
    practice.hidden = true;
    done.hidden = false;
    const correctCount = session.filter(Boolean).length;
    score.textContent = "Acertaste " + correctCount + " de " + data.total + " en este intento.";
    if (data.nextId) {
      nextLink.hidden = false;
      nextLink.href = "/leccion/" + data.nextId + data.gradeQs;
      nextLink.textContent = "Siguiente: " + data.nextTitle;
    }
  }

  hintButton.addEventListener("click", function () {
    hint.hidden = false;
    hint.textContent = problem().hint;
  });
  checkButton.addEventListener("click", check);
  numberInput.addEventListener("input", function () {
    if (!answered) checkButton.disabled = numberInput.value.trim() === "";
  });
  numberInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      check();
    }
  });
  nextButton.addEventListener("click", function () {
    if (index + 1 >= data.total) {
      finish();
      return;
    }
    index += 1;
    render();
  });

  render();
})();
