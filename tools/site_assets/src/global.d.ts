/* Ambient type declarations for the third-party globals the site
 * assets use. Pyodide and highlight.js are loaded from CDN script
 * tags, not from npm, so their APIs are declared here (only the
 * subset actually used). */

interface PyodideFileSystem {
  mkdirTree(path: string): void;
  writeFile(path: string, data: string): void;
}

interface PyodideOutputOptions {
  batched(output: string): void;
}

interface PyodideInterface {
  FS: PyodideFileSystem;
  runPython(code: string): unknown;
  runPythonAsync(code: string): Promise<unknown>;
  loadPackagesFromImports(code: string): Promise<unknown>;
  setStdout(options: PyodideOutputOptions): void;
  setStderr(options: PyodideOutputOptions): void;
}

interface HljsMode {
  className?: string;
  begin?: RegExp | string;
  end?: RegExp | string;
  relevance?: number;
  contains?: (HljsMode | "self")[];
}

interface HljsKeywords {
  $pattern?: RegExp | string;
  keyword?: string;
  built_in?: string;
  literal?: string;
}

interface HljsLanguage {
  name?: string;
  keywords?: HljsKeywords;
  contains?: (HljsMode | "self")[];
}

interface HljsApi {
  registerLanguage(
    name: string,
    definition: (hljs: HljsApi) => HljsLanguage,
  ): void;
  highlightElement(element: Element): void;
  COMMENT(
    begin: RegExp | string,
    end: RegExp | string,
    modeOptions?: Partial<HljsMode>,
  ): HljsMode;
  QUOTE_STRING_MODE: HljsMode;
}

interface Window {
  loadPyodide?(options: { indexURL: string }): Promise<PyodideInterface>;
  hljs?: HljsApi;
}
