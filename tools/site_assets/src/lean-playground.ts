/* Lean4Web integration for the embedded Lean sources.
 *
 * A full Lean toolchain cannot run in the browser, so the Lean files
 * are handled by Lean4Web (the official Lean 4 web editor at
 * live.lean-lang.org), which provides editing, syntax highlighting,
 * and server-side type checking, and evaluates #eval commands. The
 * code travels in the #code= URL fragment. The build script inlines
 * project-local imports at build time (the JSON map with id
 * "lean-playground-src"), so every file is self-contained.
 *
 * Each Lean block gets two controls: a button that swaps the static
 * listing for an embedded Lean4Web iframe in place (created lazily,
 * only when asked for), and a link opening the same editor in a new
 * tab.
 */
(() => {
  const PLAYGROUND = "https://live.lean-lang.org/#code=";
  const EMBED_LABEL = "Edit and run here (Lean4Web)";
  const SOURCE_LABEL = "Show the source listing";

  function isSourceMap(value: unknown): value is Record<string, string> {
    return (
      typeof value === "object" &&
      value !== null &&
      Object.values(value).every((entry) => typeof entry === "string")
    );
  }

  function addControls(
    block: HTMLDetailsElement,
    path: string,
    url: string,
  ): void {
    const pre = block.querySelector("pre");
    if (!pre) {
      return;
    }

    const controls = document.createElement("div");
    controls.className = "run-controls";

    let iframe: HTMLIFrameElement | null = null;

    const embedBtn = document.createElement("button");
    embedBtn.type = "button";
    embedBtn.className = "run-btn";
    embedBtn.textContent = EMBED_LABEL;
    embedBtn.addEventListener("click", () => {
      if (!iframe) {
        iframe = document.createElement("iframe");
        iframe.className = "lean-embed";
        iframe.src = url;
        iframe.title = `Lean 4 web editor: ${path}`;
        block.appendChild(iframe);
      } else {
        iframe.hidden = !iframe.hidden;
      }
      pre.hidden = !iframe.hidden;
      embedBtn.textContent = iframe.hidden ? EMBED_LABEL : SOURCE_LABEL;
    });
    controls.appendChild(embedBtn);

    const link = document.createElement("a");
    link.className = "run-btn";
    link.textContent = "Open in a new tab";
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener";
    controls.appendChild(link);

    const note = document.createElement("span");
    note.className = "run-status";
    note.textContent = "live.lean-lang.org, local imports inlined.";
    controls.appendChild(note);

    block.insertBefore(controls, pre);
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
      if (source === undefined) {
        continue;
      }
      addControls(block, path, PLAYGROUND + encodeURIComponent(source));
    }
  });
})();
