(function () {
  const dataNode = document.getElementById("trial-data");
  if (!dataNode) return;
  const problems = JSON.parse(dataNode.textContent);
  const prompt = document.getElementById("prompt");
  const choices = document.getElementById("choices");
  const feedback = document.getElementById("feedback");
  const feedbackTitle = document.getElementById("feedback-title");
  const feedbackBody = document.getElementById("feedback-body");
  const nextButton = document.getElementById("next-btn");
  const stepLabel = document.getElementById("step-label");
  const stepBar = document.getElementById("step-bar");
  let step = 0;
  let busy = false;
  let answered = false;
  let registerNext = false;
  const session = [];

  function render() {
    const item = problems[step];
    busy = false;
    answered = false;
    registerNext = false;
    prompt.textContent = item.prompt;
    stepLabel.textContent = "Prueba " + (step + 1) + " de " + problems.length;
    stepBar.style.width = (step / problems.length) * 100 + "%";
    choices.innerHTML = "";
    feedback.hidden = true;
    feedback.classList.remove("is-soft");
    nextButton.hidden = false;
    item.choices.forEach(function (choice) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "choice";
      button.textContent = choice.label;
      button.addEventListener("click", function () {
        pick(choice.id, button);
      });
      choices.appendChild(button);
    });
    prompt.focus();
  }

  async function pick(choiceId, button) {
    if (busy || answered) return;
    busy = true;
    choices.querySelectorAll(".choice").forEach(function (node) {
      node.classList.toggle("is-picked", node === button);
      node.disabled = true;
    });
    try {
      const response = await fetch("/api/prueba", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problem_id: problems[step].id, answer: choiceId }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "No pudimos comprobar");
      answered = true;
      session.push(Boolean(result.correct));
      button.classList.add(result.correct ? "is-right" : "is-miss");
      feedback.hidden = false;
      const last = step === problems.length - 1;
      const score = "Acertaste " + session.filter(Boolean).length + " de " + problems.length + ".";
      if (result.correct) {
        feedback.classList.remove("is-soft");
        feedbackTitle.textContent = "Correcto";
        feedbackBody.textContent = last ? result.explain + " " + score : result.explain;
      } else {
        feedback.classList.add("is-soft");
        feedbackTitle.textContent = "¡Vaya!";
        feedbackBody.textContent = last
          ? "Esta vez esa no es la correcta. " + score
          : "Esta vez esa no es la correcta.";
      }
      registerNext = last;
      nextButton.textContent = last ? "Crear cuenta" : "Siguiente";
      nextButton.focus();
    } catch (error) {
      busy = false;
      choices.querySelectorAll(".choice").forEach(function (node) {
        node.disabled = false;
      });
      feedback.hidden = false;
      feedbackTitle.textContent = "Inténtalo otra vez";
      feedbackBody.textContent = "No pudimos comprobar la respuesta. Revisa tu conexión.";
      nextButton.hidden = true;
    }
  }

  nextButton.addEventListener("click", function () {
    if (!answered) return;
    if (registerNext) {
      window.location.href = "/entrar";
      return;
    }
    step += 1;
    render();
  });

  render();
})();
