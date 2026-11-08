# Design Specification: CodeGraph (Rust Native Codebase Knowledge Graph Engine)

**Date:** 2026-11-04  
**Status:** Approved  
**Author:** Pair Programming (User & Antigravity)  
**Target Repository:** `D:\codegraph` (Independent Rust Repository)

---

## 1. Executive Summary & Goals

CodeGraph is a lightweight, high-performance, and completely offline Codebase Knowledge Graph engine written in Rust. It analyses source code repositories deterministically using Tree-sitter AST parsing without relying on external cloud APIs or LLM tokens.

### Key Objectives
1. **Zero External Runtime:** Compiles to a single native executable (`codegraph.exe`) with no Python or Node.js runtime dependencies.
2. **Phase 1 Languages:**
   - **Rust** (`.rs`): Structs, Enums, Traits, Impls, Functions, Modules, and `use` imports.
   - **TypeScript & JavaScript** (`.ts`, `.tsx`, `.js`, `.jsx`): Classes, Interfaces, Types, Functions, and `import`/`export`.
   - **Vue SFC** (`.vue`): `<script>` block extraction (Composition & Options API).
   - **Project Manifests** (`Cargo.toml`, `package.json`): External dependencies and crate linking.
3. **Graph Topology & Queries:**
   - **God Nodes:** Weighted degree centrality to identify architectural hubs.
   - **Impact Analysis (`affected`):** Reverse dependency traversal to locate all components impacted by changes to a given symbol.
   - **Path Finding (`path`):** Shortest path (BFS) between two nodes to trace call/dependency chains.
4. **Outputs:**
   - `codegraph-out/graph.json`: Machine-readable graph structure.
   - `codegraph-out/REPORT.md`: Architectural summary report in Markdown.
   - `codegraph-out/graph.html`: Standalone, interactive visual graph viewer (no external server required).

---

## 2. Architecture & Data Structures

### 2.1 Graph Schema

#### Node Model
```rust
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum NodeKind {
    File,
    Module,
    Struct,
    Enum,
    Trait,
    Function,
    Class,
    Interface,
    Package,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Node {
    pub id: String,                  // Unique qualified identifier (e.g., "src/lib.rs::Engine")
    pub label: String,               // Display name (e.g., "Engine")
    pub kind: NodeKind,
    pub file_path: String,           // Relative file path (normalized forward slashes)
    pub line_range: (usize, usize),  // 1-based [start_line, end_line]
    pub in_degree: usize,
    pub out_degree: usize,
}
```

#### Edge Model
```rust
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum Relation {
    Defines,      // Container (File/Module) defines Symbol
    Imports,      // File/Module imports another File/Symbol
    Calls,        // Function/Method calls another Function
    Implements,   // Struct implements Trait/Interface
    References,   // Symbol references Type or Variable
    DependsOn,    // Project depends on Package
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Edge {
    pub source: String,       // Node id
    pub target: String,       // Node id
    pub relation: Relation,
    pub confidence: f32,      // 1.0 for deterministic AST, 0.8 for resolved heuristics
}
```

### 2.2 System Components

```
D:\codegraph\
├── Cargo.toml
└── src/
    ├── main.rs              # CLI entry point (clap v4)
    ├── model/
    │   └── mod.rs           # Node, Edge, Relation, GraphDataset
    ├── scanner/
    │   └── mod.rs           # Directory walker (ignore crate) respecting .gitignore
    ├── extractor/
    │   ├── mod.rs           # Extractor trait & symbol registry
    │   ├── rust_lang.rs     # Tree-sitter Rust AST extractor
    │   ├── ts_lang.rs       # Tree-sitter TypeScript/JavaScript/Vue extractor
    │   └── manifest.rs      # Cargo.toml and package.json parser
    ├── graph/
    │   ├── mod.rs           # In-memory graph builder & resolver
    │   ├── topology.rs      # Degree centrality & God-node computation
    │   └── traversal.rs     # Shortest path (BFS) & Reverse impact traversal
    └── export/
        ├── json.rs          # Serializes GraphDataset to graph.json
        ├── report.rs        # Generates REPORT.md summary
        └── html.rs          # Generates standalone interactive graph.html
```

---

## 3. Two-Pass Extraction & Resolution Pipeline

1. **Pass 1: Discovery & Local AST Extraction**
   - The scanner filters files using `ignore::WalkBuilder` to ignore `.git`, `target`, `node_modules`, `dist`, and binary formats.
   - Files are parsed concurrently with `rayon`.
   - Each extractor returns local nodes (definitions) and unresolved references (calls, imports).
   - All definitions are registered into a global `SymbolRegistry: HashMap<String, Vec<NodeId>>`.

2. **Pass 2: Symbol Resolution & Graph Assembly**
   - For every unresolved reference in a file:
     - Check file-local imports/use statements for matching aliases or qualified paths.
     - Fall back to global unique symbol lookup in `SymbolRegistry`.
     - Create an `Edge` if the target node exists in the registry.
   - Compute `in_degree` and `out_degree` for every node in the assembled graph.

---

## 4. CLI Interface Specifications

The tool is invoked via `codegraph <subcommand>`:

1. **`scan [path]` (default: `.`)**
   - Scans target directory.
   - Outputs:
     - `codegraph-out/graph.json`
     - `codegraph-out/REPORT.md`
     - `codegraph-out/graph.html`
2. **`god-nodes [--top N]` (default: 10)**
   - Reads existing `graph.json` or runs an in-memory scan.
   - Prints the top N most central nodes with in/out degree breakdown.
3. **`affected <symbol>`**
   - Performs a reverse reachability traversal from `<symbol>`.
   - Outputs all upstream callers, referencing structs, and importing files.
4. **`path <source> <target>`**
   - Performs a breadth-first search (BFS) on directed/undirected edges.
   - Prints the shortest connection path between `<source>` and `<target>`.

---

## 5. Interactive Web Visualization (`graph.html`)

- Self-contained, single-file HTML (embedded JS/CSS, no CDN required, operates 100% offline).
- Built with an embedded Canvas/SVG network renderer.
- Features:
  - Interactive pan & zoom.
  - Search bar to locate nodes instantly.
  - Click-to-highlight connected neighbors (incoming and outgoing).
  - Node color coding by `NodeKind` (Rust struct vs TS function vs File).

---

## 6. Verification & Quality Assurance Strategy

1. **Unit Tests:**
   - `test_rust_extractor`: Verify parsing of structs, impls, traits, and functions from string fixtures.
   - `test_ts_extractor`: Verify parsing of classes, interfaces, functions, and imports.
   - `test_vue_extractor`: Verify `<script setup>` extraction from Vue components.
   - `test_traversal`: Verify BFS shortest path and reverse affected traversal on synthetic graphs.
2. **Integration Verification:**
   - Run `codegraph scan` against a known multi-crate Rust & Vue project (such as `D:\mcp-server-test`).
   - Validate that `graph.json`, `REPORT.md`, and `graph.html` are created accurately with expected node counts.
