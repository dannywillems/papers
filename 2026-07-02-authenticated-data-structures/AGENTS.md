# Human section

This section MUST only be modified by HUMANS. AI agents are NOT authorized to modify this section.

This paper will be about authenticated data structures (ADS), in particular the ones
that can be used to solve the problems the repository
[incrementalmerkletree](https://github.com/zcash/incrementalmerkletree) aims to
solve.
The paper started with [this
issue](https://github.com/dannywillems/dannywillems.github.io/issues/535) on my
personal blog. When I was going through the Zcash repository, I was wondering if
there were any class of structures in the litterature that would be solving the
exact same problems.
The paper is written with AI assistance. It first takes the context of the
issue, and a human verifies the output over time.

The motivation of this paper is to provide formal definitions of ADS, their
properties and multiple instances of structures with these properties. Python
implementations will be given, in addition to code in Lean.
The set of definitions and Lean code will be structured as libraries, so it can
be reused later by other authors or agents.

AI tools will be used to scrap the bibliography, and to automate the paper
redaction.
