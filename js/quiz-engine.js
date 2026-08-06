/**
 * Quiz UI — select an answer; if it stays unchanged for dwellMs (default 1s), lock and continue.
 * Optional per-question countdown; on timeout → incorrect and auto-advance (report_only).
 */
(function (global) {
  const DEFAULT_DWELL_MS = 1000;
  const DEFAULT_LIMITS_S = { easy: 30, medium: 45, hard: 60 };

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function formatChoiceLabel(item, selected) {
    if (selected == null) return "—";
    const type = global.QCAdaptive.normalizeType(item.type);
    if (type === "true_false") return selected ? "True" : "False";
    if (type === "multiple_choice" && item.choices) {
      const i = Number(selected);
      return item.choices[i] != null ? item.choices[i] : String(selected);
    }
    return String(selected);
  }

  function formatCorrectLabel(item) {
    const type = global.QCAdaptive.normalizeType(item.type);
    if (type === "true_false") return item.answer ? "True" : "False";
    if (type === "multiple_choice" && item.choices) {
      return item.choices[item.answer] != null ? item.choices[item.answer] : String(item.answer);
    }
    return String(item.answer);
  }

  function readSelected(form, type) {
    if (type === "multiple_choice") {
      const checked = form.querySelector('input[name="answer"]:checked');
      if (!checked) return null;
      return Number(checked.value);
    }
    if (type === "true_false") {
      const checked = form.querySelector('input[name="answer"]:checked');
      if (!checked) return null;
      return checked.value === "true";
    }
    const input = form.querySelector('input[name="answer"]');
    const v = input ? String(input.value || "").trim() : "";
    return v === "" ? null : v;
  }

  function markPending(form, selectedKey) {
    form.querySelectorAll(".choice").forEach((label) => {
      const input = label.querySelector('input[name="answer"]');
      const key = input ? input.value : "";
      label.classList.toggle("pending", String(key) === String(selectedKey));
      label.classList.remove("locked");
    });
  }

  function markLocked(form) {
    form.querySelectorAll(".choice").forEach((label) => {
      const input = label.querySelector('input[name="answer"]');
      label.classList.toggle("locked", !!(input && input.checked));
      label.classList.remove("pending");
    });
  }

  function resolveTimeLimitMs(content, item, difficulty) {
    const t = (content && content.timing) || {};
    if (t.enabled === false) return null;
    if (item && item.time_limit_s != null) {
      const s = Number(item.time_limit_s);
      return Number.isFinite(s) && s > 0 ? Math.round(s * 1000) : null;
    }
    const limits = Object.assign({}, DEFAULT_LIMITS_S, t.limits_s || {});
    const d = difficulty || (item && item.difficulty) || "medium";
    const sec = limits[d] != null ? Number(limits[d]) : Number(limits.medium) || 45;
    return Number.isFinite(sec) && sec > 0 ? Math.round(sec * 1000) : null;
  }

  function resolveWarnBeforeMs(content) {
    const t = (content && content.timing) || {};
    const s = t.warn_before_s != null ? Number(t.warn_before_s) : 10;
    return Number.isFinite(s) && s > 0 ? Math.round(s * 1000) : 10000;
  }

  function fmtCountdown(msLeft) {
    const s = Math.max(0, Math.ceil(msLeft / 1000));
    if (s >= 60) {
      const m = Math.floor(s / 60);
      const r = s % 60;
      return m + ":" + String(r).padStart(2, "0");
    }
    return String(s) + "s";
  }

  function commitAnswer(root, form, item, type, selected, opts, silent, meta) {
    meta = meta || {};
    const timedOut = !!meta.timedOut;
    const correct = timedOut ? false : global.QCAdaptive.grade(item, selected);
    form.querySelectorAll("input, button").forEach((el) => {
      el.disabled = true;
    });
    markLocked(form);

    if (typeof opts.onGraded === "function") {
      opts.onGraded({ selected, correct, item, timedOut });
    }

    if (silent) {
      if (typeof opts.onContinue === "function") {
        opts.onContinue({ selected, correct, item, timedOut });
      }
      return;
    }

    const feedback = document.createElement("div");
    feedback.className = "feedback " + (correct ? "ok" : "err");
    const why =
      item.choice_rationales && type === "multiple_choice" && item.choice_rationales[selected] != null
        ? item.choice_rationales[selected]
        : item.explain || "";
    feedback.innerHTML =
      "<p><strong>" +
      (timedOut ? "Time’s up" : correct ? "Correct" : "Not quite") +
      "</strong></p>" +
      "<p>" +
      (timedOut
        ? "No answer in time."
        : "You chose: " +
          escapeHtml(formatChoiceLabel(item, selected)) +
          (correct ? "" : "<br>Correct answer: " + escapeHtml(formatCorrectLabel(item)))) +
      "</p>" +
      (why ? "<p class=\"explain\">" + escapeHtml(why) + "</p>" : "");
    const nextRow = document.createElement("div");
    nextRow.className = "actions";
    const nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "btn primary";
    nextBtn.textContent = opts.nextLabel || "Continue";
    nextRow.appendChild(nextBtn);
    feedback.appendChild(nextRow);
    root.appendChild(feedback);
    nextBtn.addEventListener("click", () => {
      if (typeof opts.onContinue === "function") {
        opts.onContinue({ selected, correct, item, timedOut });
      }
    });
  }

  function renderItem(root, item, opts) {
    opts = opts || {};
    const silent = opts.feedback === "report_only";
    const dwellMs = opts.dwellMs != null ? Number(opts.dwellMs) : DEFAULT_DWELL_MS;
    const timeLimitMs = opts.timeLimitMs != null ? Number(opts.timeLimitMs) : null;
    const warnBeforeMs = opts.warnBeforeMs != null ? Number(opts.warnBeforeMs) : 10000;
    root.innerHTML = "";
    root.hidden = false;

    const type = global.QCAdaptive.normalizeType(item.type);
    const autoCommit = silent && (type === "multiple_choice" || type === "true_false");

    let timer = null;
    let countdownId = null;
    let pendingValue = null;
    let committed = false;

    function clearDwell() {
      if (timer != null) {
        clearTimeout(timer);
        timer = null;
      }
    }

    function clearCountdown() {
      if (countdownId != null) {
        clearInterval(countdownId);
        countdownId = null;
      }
    }

    function cleanup() {
      clearDwell();
      clearCountdown();
    }

    if (timeLimitMs != null && timeLimitMs > 0) {
      const timerEl = document.createElement("div");
      timerEl.className = "q-timer";
      timerEl.setAttribute("role", "timer");
      timerEl.setAttribute("aria-live", "polite");
      const bar = document.createElement("div");
      bar.className = "q-timer-bar";
      const fill = document.createElement("div");
      fill.className = "q-timer-fill";
      bar.appendChild(fill);
      const label = document.createElement("div");
      label.className = "q-timer-label";
      timerEl.appendChild(label);
      timerEl.appendChild(bar);
      root.appendChild(timerEl);
      // Countdown starts after the form is mounted (see startCountdown below).
      opts._timerUi = { timerEl, fill, label };
    }

    const prompt = document.createElement("p");
    prompt.className = "prompt";
    prompt.textContent = item.prompt || "";
    root.appendChild(prompt);

    const form = document.createElement("form");
    form.className = "answer-form" + (autoCommit ? " auto-commit" : "");
    form.setAttribute("novalidate", "");

    if (type === "multiple_choice") {
      const group = document.createElement("div");
      group.className = "choices";
      (item.choices || []).forEach((choice, ci) => {
        const label = document.createElement("label");
        label.className = "choice";
        const input = document.createElement("input");
        input.type = "radio";
        input.name = "answer";
        input.value = String(ci);
        label.appendChild(input);
        const span = document.createElement("span");
        span.textContent = choice;
        label.appendChild(span);
        group.appendChild(label);
      });
      form.appendChild(group);
    } else if (type === "true_false") {
      const group = document.createElement("div");
      group.className = "choices";
      [
        { v: "true", t: "True" },
        { v: "false", t: "False" },
      ].forEach((opt) => {
        const label = document.createElement("label");
        label.className = "choice";
        const input = document.createElement("input");
        input.type = "radio";
        input.name = "answer";
        input.value = opt.v;
        label.appendChild(input);
        const span = document.createElement("span");
        span.textContent = opt.t;
        label.appendChild(span);
        group.appendChild(label);
      });
      form.appendChild(group);
    } else {
      const input = document.createElement("input");
      input.type = "text";
      input.name = "answer";
      input.className = "short-answer";
      input.autocomplete = "off";
      form.appendChild(input);
    }

    function armDwell(selected) {
      if (committed || selected == null) return;
      const key =
        type === "true_false" ? String(selected) : type === "multiple_choice" ? String(selected) : String(selected);
      pendingValue = key;
      if (type === "multiple_choice" || type === "true_false") {
        markPending(form, type === "true_false" ? (selected ? "true" : "false") : String(selected));
      }
      clearDwell();
      timer = setTimeout(() => {
        if (committed) return;
        const latest = readSelected(form, type);
        if (latest == null) return;
        const latestKey =
          type === "true_false" ? String(latest) : type === "multiple_choice" ? String(latest) : String(latest);
        if (latestKey !== pendingValue) return;
        committed = true;
        cleanup();
        commitAnswer(root, form, item, type, latest, opts, silent, {});
      }, dwellMs);
    }

    if (autoCommit) {
      form.querySelectorAll('input[name="answer"]').forEach((input) => {
        input.addEventListener("change", () => {
          if (committed) return;
          armDwell(readSelected(form, type));
        });
      });
    } else {
      const actions = document.createElement("div");
      actions.className = "actions";
      const submit = document.createElement("button");
      submit.type = "submit";
      submit.className = "btn primary";
      submit.textContent = silent ? "Submit" : "Check answer";
      actions.appendChild(submit);
      form.appendChild(actions);

      form.addEventListener("submit", (e) => {
        e.preventDefault();
        if (committed) return;
        const selected = readSelected(form, type);
        if (selected == null) return;
        committed = true;
        cleanup();
        commitAnswer(root, form, item, type, selected, opts, silent, {});
      });

      if (silent && type === "short_answer") {
        const input = form.querySelector('input[name="answer"]');
        if (input) {
          input.addEventListener("input", () => {
            if (committed) return;
            armDwell(readSelected(form, type));
          });
        }
      }
    }

    root.appendChild(form);

    if (opts._timerUi && timeLimitMs != null && timeLimitMs > 0) {
      const ui = opts._timerUi;
      delete opts._timerUi;
      const started = performance.now();
      const deadline = started + timeLimitMs;
      function tick() {
        if (committed) return;
        const left = deadline - performance.now();
        const pct = Math.max(0, Math.min(100, (left / timeLimitMs) * 100));
        ui.fill.style.width = pct + "%";
        ui.label.textContent = fmtCountdown(left);
        ui.timerEl.classList.toggle("warn", left <= warnBeforeMs && left > 5000);
        ui.timerEl.classList.toggle("critical", left <= 5000);
        if (left <= 0) {
          cleanup();
          if (committed) return;
          committed = true;
          commitAnswer(root, form, item, type, null, opts, silent, { timedOut: true });
        }
      }
      tick();
      countdownId = setInterval(tick, 200);
    }
  }

  global.QCQuiz = {
    DEFAULT_DWELL_MS,
    DEFAULT_LIMITS_S,
    resolveTimeLimitMs,
    resolveWarnBeforeMs,
    renderItem,
    formatChoiceLabel,
    formatCorrectLabel,
  };
})(window);
