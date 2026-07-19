/* Lean 4 grammar for highlight.js.
 *
 * highlight.js ships no Lean language, so the embedded Lean sources
 * would otherwise render as plain text. This registers a small grammar
 * covering the constructs used in the papers: declarations, tactics,
 * doc comments (including nested block comments), attributes, strings,
 * and #-commands. It must be loaded after highlight.min.js and before
 * the highlighting pass runs.
 */
(() => {
  const hljs = window.hljs;
  if (!hljs) {
    return;
  }

  hljs.registerLanguage("lean", (h: HljsApi): HljsLanguage => {
    const keywords: HljsKeywords = {
      $pattern: /[A-Za-z_][A-Za-z0-9_?!']*/,
      keyword:
        "abbrev attribute axiom by calc class def deriving do else end " +
        "example extends from fun have if import in inductive instance " +
        "lemma let macro macro_rules match mutual namespace " +
        "noncomputable notation open partial private protected return " +
        "section set_option show sorry structure syntax then theorem " +
        "universe unsafe variable where with " +
        // Common tactics, so proof scripts read as structured code.
        "intro intros cases rcases obtain refine exact rfl rw simp " +
        "simp_all induction subst injection constructor by_cases " +
        "by_contra apply omega decide trivial assumption",
      literal: "true false none",
    };

    const docComment = h.COMMENT(/\/--/, /-\//, { relevance: 10 });
    const moduleComment = h.COMMENT(/\/-!/, /-\//);
    const blockComment = h.COMMENT(/\/-/, /-\//, { contains: ["self"] });
    const lineComment = h.COMMENT(/--/, /$/);

    return {
      name: "Lean 4",
      keywords,
      contains: [
        docComment,
        moduleComment,
        blockComment,
        lineComment,
        h.QUOTE_STRING_MODE,
        { className: "meta", begin: /@\[/, end: /\]/ },
        { className: "meta", begin: /#[a-z_]+\b/ },
        { className: "type", begin: /\b[A-Z][A-Za-z0-9_]*/ },
        { className: "number", begin: /\b\d+\b/ },
      ],
    };
  });
})();
