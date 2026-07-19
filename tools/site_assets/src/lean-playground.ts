/* "Run in Lean 4 playground" buttons for the embedded Lean sources.
 *
 * A full Lean toolchain cannot run in the browser, so each Lean file
 * opens in the official Lean 4 web playground (live.lean-lang.org),
 * which type-checks the proofs and evaluates #eval commands
 * server-side. The code travels in the #code= URL fragment. The build
 * script inlines project-local imports at build time (the JSON map
 * with id "lean-playground-src"), so every file is self-contained.
 */
(() => {
  const PLAYGROUND = "https://live.lean-lang.org/#code=";

  function isSourceMap(value: unknown): value is Record<string, string> {
    return (
      typeof value === "object" &&
      value !== null &&
      Object.values(value).every((entry) => typeof entry === "string")
    );
  }

  document.addEventListener("DOMContentLoaded", () => {
    const data = document.getElementById("lean-playground-src");
    if (!data) {
      return;
    }
    let parsed: unknown;
    try {
      parsed = JSON.parse(data.textContent ?? "");
    } catch {
      return;
    }
    if (!isSourceMap(parsed)) {
      return;
    }
    const sources = parsed;

    const blocks = document.querySelectorAll<HTMLDetailsElement>(
      '.paper-code details[data-lang="lean"]',
    );
    for (const block of blocks) {
      const path = block.dataset["path"] ?? "";
      const source = sources[path];
      const pre = block.querySelector("pre");
      if (source === undefined || !pre) {
        continue;
      }

      const controls = document.createElement("div");
      controls.className = "run-controls";

      const link = document.createElement("a");
      link.className = "run-btn";
      link.textContent = "Run in Lean 4 playground";
      link.href = PLAYGROUND + encodeURIComponent(source);
      link.target = "_blank";
      link.rel = "noopener";
      controls.appendChild(link);

      const note = document.createElement("span");
      note.className = "run-status";
      note.textContent =
        "Opens live.lean-lang.org with this file (local imports inlined).";
      controls.appendChild(note);

      block.insertBefore(controls, pre);
    }
  });
})();
