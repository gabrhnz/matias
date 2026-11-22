(function () {
  const registerForm = document.getElementById("register-form");
  const returnForm = document.getElementById("return-form");
  const codeForm = document.getElementById("code-form");
  if (!registerForm || !codeForm) return;
  const note = document.getElementById("auth-note");
  const preview = document.getElementById("preview");
  const previewCode = document.getElementById("preview-code");
  const title = document.getElementById("auth-title");
  const switchMode = document.getElementById("switch-mode");
  let email = "";
  let profile = null;
  let returning = false;

  function say(text) {
    note.hidden = !text;
    note.textContent = text || "";
  }

  async function send(address) {
    const response = await fetch("/api/entrar/codigo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: address }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "No pudimos enviar el código");
    email = address;
    registerForm.hidden = true;
    returnForm.hidden = true;
    switchMode.hidden = true;
    codeForm.hidden = false;
    title.textContent = "Código";
    preview.hidden = !data.previewCode;
    if (data.previewCode) previewCode.textContent = data.previewCode;
    else say("Mira el correo del representante.");
    document.getElementById("code").focus();
  }

  registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    say("");
    profile = {
      guardian_name: document.getElementById("guardian-name").value.trim(),
      student_name: document.getElementById("student-name").value.trim(),
      grade: Number(document.getElementById("grade").value),
      school: document.getElementById("school").value.trim(),
    };
    const button = registerForm.querySelector("button");
    button.disabled = true;
    try {
      await send(document.getElementById("email").value.trim());
    } catch (error) {
      say(error.message);
      button.disabled = false;
    }
  });

  returnForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    say("");
    profile = null;
    const button = returnForm.querySelector("button");
    button.disabled = true;
    try {
      await send(document.getElementById("return-email").value.trim());
    } catch (error) {
      say(error.message);
      button.disabled = false;
    }
  });

  document.getElementById("back-email").addEventListener("click", function () {
    codeForm.hidden = true;
    preview.hidden = true;
    switchMode.hidden = false;
    say("");
    if (returning) {
      returnForm.hidden = false;
      title.textContent = "Entrar";
    } else {
      registerForm.hidden = false;
      title.textContent = "Crear cuenta";
    }
  });

  switchMode.addEventListener("click", function () {
    returning = !returning;
    say("");
    registerForm.hidden = returning;
    returnForm.hidden = !returning;
    title.textContent = returning ? "Entrar" : "Crear cuenta";
    switchMode.textContent = returning ? "Crear cuenta" : "Ya entré antes";
  });

  codeForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const button = codeForm.querySelector("button[type=submit]");
    button.disabled = true;
    say("");
    const body = {
      email: email,
      code: document.getElementById("code").value.trim(),
    };
    if (profile) {
      body.guardian_name = profile.guardian_name;
      body.student_name = profile.student_name;
      body.grade = profile.grade;
      body.school = profile.school;
    }
    try {
      const response = await fetch("/api/entrar/verificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Ese código no coincide");
      localStorage.removeItem("matilab.progress");
      localStorage.removeItem("matilab.repaso");
      if (data.student) localStorage.setItem("matilab.student", JSON.stringify(data.student));
      window.location.href = "/progreso";
    } catch (error) {
      say(error.message);
      button.disabled = false;
    }
  });
})();
