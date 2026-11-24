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
  const figure = document.getElementById("figure");

  const order = [data.startProblemId || data.problems[0].id];
  let step = 0;
  let picked = "";
  let busy = false;
  let answered = false;
  let pendingNext = null;
  let leaving = false;
  const session = [];
  let exampleDrawn = false;
  let lastProgress = null;

  function problem() {
    const id = order[step];
    for (let index = 0; index < data.problems.length; index += 1) {
      if (data.problems[index].id === id) return data.problems[index];
    }
    return data.problems[0];
  }

  function drawFigure(item) {
    if (!item.scene) {
      figure.hidden = true;
      figure.innerHTML = "";
      prompt.classList.remove("is-caption");
      return;
    }
    figure.hidden = false;
    figure.innerHTML = window.MatiLabFigures.draw(item.scene);
    prompt.classList.add("is-caption");
  }

  function drawExample() {
    if (exampleDrawn) return;
    exampleDrawn = true;
    const slot = document.getElementById("example-figure");
    if (!slot || !data.exampleScene) return;
    slot.hidden = false;
    slot.innerHTML = window.MatiLabFigures.draw(data.exampleScene);
  }

  function render() {
    const item = problem();
    picked = "";
    answered = false;
    busy = false;
    pendingNext = null;
    prompt.textContent = item.prompt;
    drawFigure(item);
    drawExample();
    stepLabel.textContent = "Práctica " + (step + 1) + " de " + data.total;
    stepBar.style.width = (step / data.total) * 100 + "%";
    choices.innerHTML = "";
    hint.hidden = true;
    feedback.hidden = true;
    feedback.classList.remove("is-soft");
    checkButton.disabled = true;
    checkButton.hidden = item.kind === "choice";
    hintButton.hidden = !item.hint;
    numberField.hidden = item.kind !== "number";
    numberInput.value = "";
    numberInput.disabled = false;
    numberInput.classList.remove("is-miss");
    if (item.kind === "choice") {
      item.choices.forEach(function (choice) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "choice";
        const mini = item.scene ? window.MatiLabFigures.miniPie(choice.label) : "";
        if (mini) button.insertAdjacentHTML("beforeend", mini);
        button.append(document.createTextNode(choice.label));
        button.dataset.id = choice.id;
        button.addEventListener("click", function () {
          if (answered || busy) return;
          picked = choice.id;
          choices.querySelectorAll(".choice").forEach(function (node) {
            node.classList.toggle("is-picked", node === button);
          });
          check();
        });
        choices.appendChild(button);
      });
    }
    prompt.focus();
  }

  function answerValue() {
    return problem().kind === "number" ? numberInput.value.trim() : picked;
  }

  function history() {
    const previous = [];
    for (let index = 0; index < step; index += 1) {
      previous.push({ id: order[index], correct: session[index] });
    }
    return previous;
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
          history: history(),
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "No pudimos comprobar");
      answered = true;
      session.push(Boolean(result.correct));
      if (result.progress) {
        lastProgress = result.progress;
        window.MatiLab.remember(data.id, result.progress);
      }
      showResult(result);
      if (typeof result.streak === "number") window.MatiLab.setStreak(result.streak);
    } catch (error) {
      busy = false;
      checkButton.disabled = problem().kind === "choice";
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
    pendingNext = result.nextProblemId || null;
    if (result.correct) {
      feedback.classList.remove("is-soft");
      feedbackTitle.textContent = "Correcto";
      feedbackBody.textContent = result.explain;
    } else {
      feedback.classList.add("is-soft");
      feedbackTitle.textContent = "Incorrecto";
      feedbackBody.textContent = result.explain;
    }
    nextButton.hidden = false;
    nextButton.textContent = "Seguir";
    choices.querySelectorAll(".choice").forEach(function (node) {
      node.disabled = true;
    });
    numberInput.disabled = true;
    const selected = choices.querySelector(".is-picked");
    if (selected) selected.classList.add(result.correct ? "is-right" : "is-miss");
    if (!result.correct && problem().kind === "number") numberInput.classList.add("is-miss");
    nextButton.focus();
  }

  function goNext() {
    if (leaving || !answered) return;
    leaving = true;
    const nextId = pendingNext;
    pendingNext = null;
    if (!nextId || order.indexOf(nextId) !== -1) {
      finish();
      return;
    }
    order.push(nextId);
    step += 1;
    leaving = false;
    render();
  }

  function finish() {
    practice.hidden = true;
    done.hidden = false;
    const correctCount = session.filter(Boolean).length;
    const fallback = session.length ? Math.round((correctCount / session.length) * 100) : 0;
    const points = lastProgress && typeof lastProgress.score === "number" ? lastProgress.score : fallback;
    const needed = data.passScore || 75;
    const passed = points >= needed;
    score.textContent = points + " sobre 100";
    const note = document.getElementById("pass-note");
    const ids = data.moduleLessonIds || [];
    const saved = window.MatiLab.loadProgress();
    const moduleOk = ids.length > 0 && ids.every(function (id) {
      if (id === data.id) return passed;
      const state = saved[id];
      return Boolean(state && state.passed);
    });
    if (moduleOk) note.textContent = "Aprobaste el módulo.";
    else if (passed) note.textContent = "Aprobaste esta lección. El módulo pide 75 sobre 100 en cada una.";
    else note.textContent = "Para aprobar el módulo necesitas al menos 75 sobre 100.";
    if (!passed) {
      nextLink.hidden = false;
      nextLink.href = "/leccion/" + data.id + (data.gradeQs || "");
      nextLink.textContent = "Intentar otra vez";
      return;
    }
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
  nextButton.addEventListener("click", goNext);

  render();
})();
