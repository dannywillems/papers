/* In-browser runner for the embedded Python sources.
 *
 * Every embedded Python file (details[data-lang="python"]) gets a Run
 * button. On the first run this loads Pyodide (CPython compiled to
 * WebAssembly) from a pinned CDN version, writes all of the page's
 * Python files into Pyodide's in-memory filesystem, and puts the
 * conventional import roots (any src/ directory, plus each file's own
 * directory) on sys.path, so imports work exactly as in the repository.
 *
 * Test files (test_*.py or *_test.py) run under pytest, which Pyodide
 * ships as a bundled package; any other file runs as __main__.
 */
(() => {
  const PYODIDE_VERSION = "0.28.3";
  const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
  const FS_ROOT = "/paper/";

  interface EmbeddedFile {
    readonly path: string;
    readonly text: string;
  }

  type StatusSetter = (text: string) => void;

  let pyodidePromise: Promise<PyodideInterface> | null = null;

  function pythonBlocks(): HTMLDetailsElement[] {
    return Array.from(
      document.querySelectorAll<HTMLDetailsElement>(
        '.paper-code details[data-lang="python"]',
      ),
    );
  }

  function fileOf(block: HTMLDetailsElement): EmbeddedFile {
    const code = block.querySelector("pre code");
    return {
      path: block.dataset["path"] ?? "",
      text: code?.textContent ?? "",
    };
  }

  /* Import roots: each file's own directory, and for a conventional
   * src/ layout everything up to and including "src". */
  function sourceRoots(paths: readonly string[]): string[] {
    const roots = new Set<string>();
    for (const path of paths) {
      const slash = path.lastIndexOf("/");
      if (slash >= 0) {
        roots.add(path.slice(0, slash));
      }
      const srcRoot = /^(.*?src)\//.exec(path)?.[1];
      if (srcRoot !== undefined) {
        roots.add(srcRoot);
      }
    }
    return [...roots];
  }

  function loadScript(url: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = url;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`failed to load ${url}`));
      document.head.appendChild(script);
    });
  }

  async function initPyodide(
    setStatus: StatusSetter,
  ): Promise<PyodideInterface> {
    setStatus("Loading the Python runtime (Pyodide, about 10 MB)...");
    if (!window.loadPyodide) {
      await loadScript(`${PYODIDE_BASE}pyodide.js`);
    }
    if (!window.loadPyodide) {
      throw new Error("Pyodide failed to initialise");
    }
    const py = await window.loadPyodide({ indexURL: PYODIDE_BASE });

    const files = pythonBlocks().map(fileOf);
    for (const file of files) {
      const full = FS_ROOT + file.path;
      py.FS.mkdirTree(full.slice(0, full.lastIndexOf("/")));
      py.FS.writeFile(full, file.text);
    }

    const roots = sourceRoots(files.map((file) => file.path)).map(
      (root) => FS_ROOT + root,
    );
    py.runPython(
      "import sys\n" +
        `for _root in ${JSON.stringify(roots)}:\n` +
        "    if _root not in sys.path:\n" +
        "        sys.path.insert(0, _root)\n",
    );

    setStatus("Fetching the Python packages used by the code...");
    for (const file of files) {
      try {
        await py.loadPackagesFromImports(file.text);
      } catch {
        /* A file that does not parse must not block the others. */
      }
    }
    return py;
  }

  function ensurePyodide(setStatus: StatusSetter): Promise<PyodideInterface> {
    if (!pyodidePromise) {
      const loading = initPyodide(setStatus);
      /* Allow a retry after a failed load (e.g. a network hiccup). */
      loading.catch(() => {
        pyodidePromise = null;
      });
      pyodidePromise = loading;
    }
    return pyodidePromise;
  }

  function isTestFile(path: string): boolean {
    return /(^|\/)test_[^/]+\.py$/.test(path) || /_test\.py$/.test(path);
  }

  function programFor(path: string): string {
    const target = JSON.stringify(FS_ROOT + path);
    if (isTestFile(path)) {
      return (
        "import pytest\n" +
        `_rc = pytest.main(["-q", "-p", "no:cacheprovider", ${target}])\n` +
        'print("pytest exit code:", _rc)\n'
      );
    }
    return `import runpy\nrunpy.run_path(${target}, run_name="__main__")\n`;
  }

  async function run(
    path: string,
    btn: HTMLButtonElement,
    status: HTMLSpanElement,
    out: HTMLPreElement,
  ): Promise<void> {
    const setStatus: StatusSetter = (text) => {
      status.textContent = text;
    };
    const append = (text: string): void => {
      out.hidden = false;
      out.textContent += `${text}\n`;
    };

    btn.disabled = true;
    out.textContent = "";
    out.hidden = true;
    try {
      const py = await ensurePyodide(setStatus);
      py.setStdout({ batched: append });
      py.setStderr({ batched: append });
      setStatus(`Running ${path} ...`);
      await py.runPythonAsync(programFor(path));
      if (out.hidden) {
        append("(no output)");
      }
      setStatus("Done.");
    } catch (error) {
      append(error instanceof Error ? error.message : String(error));
      setStatus("Failed.");
    } finally {
      btn.disabled = false;
    }
  }

  function init(): void {
    for (const block of pythonBlocks()) {
      const pre = block.querySelector("pre");
      const path = block.dataset["path"];
      if (!pre || !path) {
        continue;
      }

      const controls = document.createElement("div");
      controls.className = "run-controls";

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "run-btn";
      btn.textContent = "Run";
      controls.appendChild(btn);

      const status = document.createElement("span");
      status.className = "run-status";
      controls.appendChild(status);

      const out = document.createElement("pre");
      out.className = "run-output";
      out.hidden = true;

      block.insertBefore(controls, pre);
      block.appendChild(out);

      btn.addEventListener("click", () => {
        void run(path, btn, status, out);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
