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

  function mediaInfo(item) {
    const m = item && item.media;
    if (!m || !m.src) return null;
    const type = String(m.type || "").toLowerCase();
    if (type !== "video" && type !== "image") return null;
    return { type: type, src: String(m.src), poster: m.poster ? String(m.poster) : "" };
  }

  function resolveMediaUrl(src, mediaBase) {
    if (!src) return "";
    if (/^https?:\/\//i.test(src) || src.charAt(0) === "/") return src;
    const base = (mediaBase || "").replace(/\/+$/, "");
    return base ? base + "/" + src.replace(/^\/+/, "") : src;
  }

  /** Embed when module/item has a toolId unless item.embed_tool === false. */
  function shouldEmbedTool(item, opts) {
    if (item && item.embed_tool === false) return false;
    const toolId = String((item && item.tool_id) || (opts && opts.toolId) || "").trim();
    if (!toolId) return false;
    const base = String((opts && opts.toolsBase) || "").replace(/\/+$/, "");
    if (!base && !(item && item.tool_url)) return false;
    if (item && item.embed_tool === true) return true;
    if (opts && opts.embedTools === false) return false;
    return true;
  }

  function resolveToolEmbedUrl(item, opts) {
    if (!shouldEmbedTool(item, opts)) return null;
    const toolId = String((item && item.tool_id) || (opts && opts.toolId) || "").trim();
    if (!toolId) return null;
    if (item && item.tool_url) return String(item.tool_url);
    const base = String((opts && opts.toolsBase) || "").replace(/\/+$/, "");
    if (!base) return null;
    return base + "/" + encodeURIComponent(toolId) + "/";
  }

  function appendToolEmbed(root, item, opts) {
    const url = resolveToolEmbedUrl(item, opts);
    if (!url) return;
    const toolId =
      String((item && item.tool_id) || (opts && opts.toolId) || "lab").trim() ||
      "lab";
    const wrap = document.createElement("div");
    wrap.className = "stem-tool stem-tool-full";
    wrap.dataset.toolId = toolId;

    const label = document.createElement("div");
    label.className = "stem-tool-label";
    const labelText = document.createElement("span");
    labelText.textContent = "Lab tool — " + toolId + " (scroll the page to use it)";
    const openLink = document.createElement("a");
    openLink.className = "stem-tool-open";
    openLink.href = url;
    openLink.target = "_blank";
    openLink.rel = "noopener noreferrer";
    openLink.textContent = "Open in new tab";
    label.appendChild(labelText);
    label.appendChild(openLink);

    const frame = document.createElement("iframe");
    frame.className = "stem-tool-frame";
    frame.src = url;
    frame.title = "Lab tool: " + toolId;
    frame.setAttribute("loading", "lazy");
    frame.setAttribute("referrerpolicy", "no-referrer-when-downgrade");
    frame.setAttribute("allow", "fullscreen");
    // Cross-origin tools cannot report height; use a tall full embed so the
    // outer page scrolls instead of a clipped iframe viewport.
    const fromItem = Number(item && item.tool_embed_height_px);
    const fromOpts = Number(opts && opts.toolEmbedHeightPx);
    const px = Number.isFinite(fromItem) && fromItem > 400
      ? fromItem
      : Number.isFinite(fromOpts) && fromOpts > 400
        ? fromOpts
        : 3600;
    const heightPx = Math.round(px);
    frame.style.height = heightPx + "px";
    frame.style.minHeight = heightPx + "px";
    wrap.appendChild(label);
    wrap.appendChild(frame);
    root.appendChild(wrap);
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
    const media = mediaInfo(item);
    const videoStem = media && media.type === "video";
    const imageStem = media && media.type === "image";
    const hideQuestionText = !!(videoStem || imageStem || opts.hidePrompt);

    let timer = null;
    let countdownId = null;
    let pendingValue = null;
    let committed = false;

    let unlockSoundHandlers = null;

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
      if (unlockSoundHandlers) {
        document.removeEventListener("pointerdown", unlockSoundHandlers, true);
        document.removeEventListener("keydown", unlockSoundHandlers, true);
        unlockSoundHandlers = null;
      }
      const vid = root.querySelector("video.stem-video");
      if (vid) {
        try {
          vid.pause();
        } catch (e) {
          /* ignore */
        }
      }
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

    if (videoStem) {
      const wrap = document.createElement("div");
      wrap.className = "stem-media stem-media-video";
      const video = document.createElement("video");
      video.className = "stem-video";
      video.setAttribute("playsinline", "");
      video.setAttribute("webkit-playsinline", "");
      video.setAttribute("controls", "");
      video.setAttribute("controlsList", "nodownload noplaybackrate noremoteplayback");
      video.setAttribute("disablePictureInPicture", "");
      video.setAttribute("preload", "auto");
      video.setAttribute("autoplay", "");
      // Browsers only allow autoplay when muted; we unmute on first tap.
      video.muted = true;
      video.defaultMuted = true;
      video.setAttribute("muted", "");
      video.autoplay = true;
      video.setAttribute("aria-label", "Question stem video");
      if (media.poster) {
        video.poster = resolveMediaUrl(media.poster, opts.mediaBase);
      }
      const source = document.createElement("source");
      source.src = resolveMediaUrl(media.src, opts.mediaBase);
      source.type = "video/mp4";
      video.appendChild(source);
      video.addEventListener("contextmenu", (e) => e.preventDefault());

      const unmuteBtn = document.createElement("button");
      unmuteBtn.type = "button";
      unmuteBtn.className = "stem-unmute";
      unmuteBtn.textContent = "Tap for sound";
      unmuteBtn.setAttribute("aria-label", "Unmute question video");

      function playStem() {
        const p = video.play();
        if (p && typeof p.catch === "function") {
          p.catch(() => {});
        }
      }

      function unlockSound(ev) {
        if (ev) ev.preventDefault();
        video.muted = false;
        video.removeAttribute("muted");
        try {
          video.currentTime = 0;
        } catch (e) {
          /* ignore */
        }
        playStem();
        unmuteBtn.hidden = true;
        wrap.classList.remove("is-muted");
        document.removeEventListener("pointerdown", onDocUnlock, true);
        document.removeEventListener("keydown", onDocUnlock, true);
      }

      function onDocUnlock(ev) {
        if (video.muted) unlockSound(ev);
      }
      unlockSoundHandlers = onDocUnlock;

      unmuteBtn.addEventListener("click", unlockSound);
      wrap.appendChild(video);
      wrap.appendChild(unmuteBtn);
      wrap.classList.add("is-muted");
      root.appendChild(wrap);

      const startMutedAutoplay = () => {
        playStem();
      };
      if (video.readyState >= 2) startMutedAutoplay();
      else video.addEventListener("loadeddata", startMutedAutoplay, { once: true });

      document.addEventListener("pointerdown", onDocUnlock, true);
      document.addEventListener("keydown", onDocUnlock, true);
    } else if (imageStem) {
      const wrap = document.createElement("div");
      wrap.className = "stem-media stem-media-image";
      const img = document.createElement("img");
      img.className = "stem-image";
      img.src = resolveMediaUrl(media.src, opts.mediaBase);
      img.alt = "Question stem figure";
      img.draggable = false;
      img.addEventListener("contextmenu", (e) => e.preventDefault());
      wrap.appendChild(img);
      root.appendChild(wrap);
    }

    if (!hideQuestionText) {
      const prompt = document.createElement("p");
      prompt.className = "prompt";
      prompt.textContent = item.prompt || "";
      root.appendChild(prompt);
    }

    const form = document.createElement("form");
    form.className = "answer-form" + (autoCommit ? " auto-commit" : "") + (hideQuestionText ? " stem-only" : "");
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
        // Always show choice text — only the question prompt is hidden for video/image stems.
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
      if (hideQuestionText) {
        const saHint = document.createElement("p");
        saHint.className = "stem-hint";
        saHint.textContent = "Type your answer after watching the stem.";
        form.appendChild(saHint);
      }
      const input = document.createElement("input");
      input.type = "text";
      input.name = "answer";
      input.className = "short-answer";
      input.autocomplete = "off";
      input.setAttribute("aria-label", "Your answer");
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
    appendToolEmbed(root, item, opts);

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
    shouldEmbedTool,
    renderItem,
    formatChoiceLabel,
    formatCorrectLabel,
  };
})(window);
