/**
 * Pick next unused item at the current difficulty; shuffle among remaining.
 */
(function (global) {
  function normalizeType(type) {
    if (type === "mcq" || type === "multiple_choice") return "multiple_choice";
    if (type === "short" || type === "short_answer") return "short_answer";
    return type || "multiple_choice";
  }

  function itemsAtDifficulty(bank, difficulty) {
    return ((bank && bank.items) || []).filter((it) => (it.difficulty || "medium") === difficulty);
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function pickNext(content, bank, session, moduleId) {
    const diff = global.QCProgress.currentDifficulty(content, session, moduleId);
    if (!diff) return null;

    const st = global.QCProgress.levelStats(session, moduleId, diff);
    const c = global.QCProgress.cfg(content);
    if (st.cleared || st.exhausted) return null;
    if (st.attempts >= c.maxAttempts) return null;

    const pool = itemsAtDifficulty(bank, diff);
    const remaining = pool.filter((it) => st.used_item_ids.indexOf(it.id) === -1);
    if (!remaining.length) return null;

    const item = shuffle(remaining)[0];
    return {
      item,
      difficulty: diff,
      attempt_index: st.attempts + 1,
      bank_count: pool.length,
    };
  }

  function grade(item, selected) {
    const type = normalizeType(item.type);
    if (type === "true_false") {
      return selected === !!item.answer || selected === item.answer;
    }
    if (type === "multiple_choice") {
      return Number(selected) === Number(item.answer);
    }
    if (type === "short_answer") {
      const expect = String(item.answer || "").trim().toLowerCase();
      return String(selected || "").trim().toLowerCase() === expect;
    }
    return false;
  }

  function bankCounts(bank) {
    const out = { easy: 0, medium: 0, hard: 0 };
    ((bank && bank.items) || []).forEach((it) => {
      const d = it.difficulty || "medium";
      out[d] = (out[d] || 0) + 1;
    });
    return out;
  }

  global.QCAdaptive = {
    normalizeType,
    itemsAtDifficulty,
    pickNext,
    grade,
    bankCounts,
  };
})(window);
