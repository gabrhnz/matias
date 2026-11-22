(function () {
  const STUDENT_KEY = "matilab.student";
  const PROGRESS_KEY = "matilab.progress";

  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (char) {
      const value = (Math.random() * 16) | 0;
      return (char === "x" ? value : (value & 0x3) | 0x8).toString(16);
    });
  }

  function read(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function student() {
    const current = read(STUDENT_KEY, null);
    if (current && current.id) return current;
    const created = { id: uuid(), name: "Estudiante", grade: 4 };
    localStorage.setItem(STUDENT_KEY, JSON.stringify(created));
    return created;
  }

  function saveStudent(next) {
    localStorage.setItem(STUDENT_KEY, JSON.stringify(next));
    return next;
  }

  function loadProgress() {
    return read(PROGRESS_KEY, {});
  }

  function remember(lessonId, state) {
    const all = loadProgress();
    all[lessonId] = {
      solved: state.solved || [],
      correct: state.correct || [],
      completed: Boolean(state.completed),
    };
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(all));
    paint();
  }

  function mergeServer(data) {
    if (!data || !data.lessons) return;
    if (data.storage === "supabase") {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(data.lessons));
    } else if (Object.keys(data.lessons).length) {
      const local = loadProgress();
      Object.assign(local, data.lessons);
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(local));
    }
    if (data.student) saveStudent(data.student);
    paint();
  }

  function paint() {
    const all = loadProgress();
    document.querySelectorAll("[data-lesson]").forEach(function (node) {
      const state = all[node.dataset.lesson];
      const total = Number(node.dataset.total || 0);
      const slot = node.querySelector("[data-status]");
      if (!state) return;
      node.classList.toggle("is-complete", Boolean(state.completed));
      if (!slot) return;
      if (state.completed) slot.textContent = state.correct.length + " de " + total + " aciertos";
      else if (state.solved.length) slot.textContent = state.solved.length + " de " + total;
    });
    document.querySelectorAll("[data-module]").forEach(function (section) {
      const items = section.querySelectorAll("[data-lesson]");
      let done = 0;
      items.forEach(function (item) {
        const state = all[item.dataset.lesson];
        if (state && state.completed) done += 1;
      });
      const bar = section.querySelector("[data-bar]");
      const label = section.querySelector("[data-module-label]");
      if (bar) bar.style.width = items.length ? (done / items.length) * 100 + "%" : "0";
      if (label) label.textContent = done + " de " + items.length + " lecciones";
    });
  }

  async function sync() {
    const current = student();
    try {
      const response = await fetch("/api/progreso/" + current.id);
      if (response.ok) mergeServer(await response.json());
    } catch (error) {
      paint();
    }
  }

  const profile = document.getElementById("profile-form");
  if (profile) {
    const current = student();
    const nameInput = document.getElementById("student-name");
    const gradeInput = document.getElementById("student-grade");
    if (current.name && current.name !== "Estudiante") nameInput.value = current.name;
    gradeInput.value = String(current.grade || 4);
    profile.addEventListener("submit", async function (event) {
      event.preventDefault();
      const next = saveStudent({
        id: current.id,
        name: nameInput.value.trim() || "Estudiante",
        grade: Number(gradeInput.value),
      });
      const note = document.getElementById("profile-note");
      note.textContent = "Guardado en este navegador.";
      try {
        const response = await fetch("/api/estudiantes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ student_id: next.id, name: next.name, grade: next.grade }),
        });
        const data = await response.json();
        if (data.storage === "supabase") note.textContent = "Guardado en este navegador y en Supabase.";
      } catch (error) {
        note.textContent = "Guardado en este navegador.";
      }
    });
    fetch("/api/salud")
      .then(function (response) { return response.json(); })
      .then(function (data) {
        const note = document.getElementById("storage-note");
        note.textContent = data.storage === "supabase"
          ? "Supabase está conectado. El progreso de este navegador también se escribe en la base de datos."
          : "Supabase todavía no está conectado. El progreso queda en este navegador.";
      })
      .catch(function () {});
  }

  window.MatiLab = { student: student, saveStudent: saveStudent, remember: remember, loadProgress: loadProgress };
  paint();
  sync();
})();
