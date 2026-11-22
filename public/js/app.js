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

  function readSession() {
    const node = document.getElementById("session-data");
    if (!node) return null;
    try {
      return JSON.parse(node.textContent);
    } catch (error) {
      return null;
    }
  }

  let account = readSession();

  function student() {
    if (account && account.id) return account;
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

  function inProgram(item) {
    return item.dataset.program !== "0";
  }

  function setStreak(value) {
    const count = document.getElementById("streak-count");
    const link = document.getElementById("streak-link");
    if (!count || !link) return;
    if (!account) {
      count.textContent = "Entrar";
      link.classList.add("is-idle");
      link.classList.remove("is-live");
      link.href = "/entrar";
      link.setAttribute("aria-label", "Entrar");
      return;
    }
    const days = Number(value) || 0;
    count.textContent = String(days);
    link.classList.toggle("is-live", days > 0);
    link.classList.toggle("is-idle", days < 1);
    link.href = "/progreso";
    link.setAttribute("aria-label", "Racha de " + days + (days === 1 ? " día" : " días"));
    account.streak = days;
    const big = document.getElementById("dash-days");
    const label = document.getElementById("dash-streak-label");
    if (big) big.textContent = String(days);
    if (label) label.textContent = days === 1 ? "día seguido" : "días seguidos";
  }

  function mergeServer(data) {
    if (!data || !data.lessons) return;
    const local = loadProgress();
    const remote = data.lessons;
    if (data.storage === "supabase") {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(Object.assign({}, local, remote)));
    } else if (Object.keys(remote).length) {
      Object.assign(local, remote);
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(local));
    }
    if (data.student) {
      account = data.student;
      saveStudent(account);
      setStreak(account.streak || 0);
    }
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
      if (state.completed) slot.textContent = state.correct.length + " de " + total;
      else if (state.solved.length) slot.textContent = state.solved.length + " de " + total;
    });
    document.querySelectorAll("[data-module]").forEach(function (section) {
      const items = Array.prototype.filter.call(section.querySelectorAll("[data-lesson]"), inProgram);
      let done = 0;
      items.forEach(function (item) {
        const state = all[item.dataset.lesson];
        if (state && state.completed) done += 1;
      });
      const bar = section.querySelector("[data-bar]");
      const label = section.querySelector("[data-module-label]");
      if (bar) bar.style.width = items.length ? (done / items.length) * 100 + "%" : "0";
      if (label) label.textContent = items.length ? done + " de " + items.length : "Otro grado";
    });
    const lessons = document.getElementById("stat-lessons");
    if (lessons) {
      let done = 0;
      let correct = 0;
      let solved = 0;
      document.querySelectorAll("#dash-lessons [data-lesson]").forEach(function (item) {
        if (!inProgram(item)) return;
        const state = all[item.dataset.lesson];
        if (!state) return;
        solved += (state.solved || []).length;
        correct += (state.correct || []).length;
        if (state.completed) done += 1;
      });
      lessons.textContent = String(done);
      document.getElementById("stat-correct").textContent = String(correct);
      document.getElementById("stat-solved").textContent = String(solved);
      const link = document.getElementById("continue-link");
      const items = document.querySelectorAll("#dash-lessons [data-lesson]");
      const grade = account && account.grade ? String(account.grade) : "";
      let next = null;
      let any = null;
      items.forEach(function (item) {
        if (!inProgram(item) || item.classList.contains("is-complete")) return;
        if (!any) any = item;
        const grades = (item.dataset.grades || "").split(",");
        if (!next && grade && grades.indexOf(grade) !== -1) next = item;
      });
      const chosen = next || any || items[0];
      const anchor = chosen && chosen.querySelector("a");
      if (link && anchor) link.href = anchor.getAttribute("href");
    }
    const hello = document.getElementById("dash-name");
    if (hello && account && account.name) hello.textContent = "Hola, " + account.name;
    const meta = document.getElementById("dash-meta");
    if (meta && account) {
      const bits = [account.guardian_name, account.email, account.school].filter(Boolean);
      meta.textContent = bits.join(" · ");
    }
    const dashIn = document.getElementById("dash-in");
    const dashOut = document.getElementById("dash-out");
    if (dashIn && dashOut) {
      dashIn.hidden = !account;
      dashOut.hidden = Boolean(account);
    }
  }

  async function sync() {
    try {
      const response = await fetch("/api/yo");
      if (response.ok) {
        const data = await response.json();
        if (data.student) {
          account = data.student;
          saveStudent(account);
          setStreak(account.streak || 0);
          mergeServer(data);
          return;
        }
      }
    } catch (error) {
      paint();
      return;
    }
    if (!account) {
      const saved = read(STUDENT_KEY, null);
      if (saved && saved.id && saved.email) {
        try {
          const response = await fetch("/api/progreso/" + saved.id);
          if (response.ok) mergeServer(await response.json());
        } catch (error) {
          paint();
        }
        return;
      }
    }
    paint();
  }

  const profile = document.getElementById("profile-form");
  if (profile && account) {
    const nameInput = document.getElementById("student-name");
    const gradeInput = document.getElementById("student-grade");
    const guardianInput = document.getElementById("guardian-name");
    const schoolInput = document.getElementById("school");
    if (account.name) nameInput.value = account.name;
    if (account.guardian_name) guardianInput.value = account.guardian_name;
    if (account.school) schoolInput.value = account.school;
    gradeInput.value = String(account.grade || 4);
    profile.addEventListener("submit", async function (event) {
      event.preventDefault();
      const note = document.getElementById("profile-note");
      note.textContent = "";
      try {
        const response = await fetch("/api/perfil", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: nameInput.value.trim() || "Estudiante",
            grade: Number(gradeInput.value),
            guardian_name: guardianInput.value.trim(),
            school: schoolInput.value.trim(),
          }),
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "No se guardó");
        account = data.student || account;
        saveStudent(account);
        paint();
        note.textContent = "Listo";
      } catch (error) {
        note.textContent = "Entra otra vez para guardar";
      }
    });
  }

  const logout = document.getElementById("logout-btn");
  if (logout) {
    logout.addEventListener("click", async function () {
      await fetch("/api/salir", { method: "POST" });
      localStorage.removeItem(STUDENT_KEY);
      localStorage.removeItem(PROGRESS_KEY);
      window.location.href = "/";
    });
  }

  window.MatiLab = {
    student: student,
    saveStudent: saveStudent,
    remember: remember,
    loadProgress: loadProgress,
    setStreak: setStreak,
  };
  if (account) setStreak(account.streak || 0);
  paint();
  sync();
})();
