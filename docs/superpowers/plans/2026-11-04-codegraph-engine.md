# CodeGraph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a native, offline Codebase Knowledge Graph engine in Rust from scratch, supporting AST parsing for Rust, TypeScript/JavaScript, and Vue SFC, with graph metrics, impact analysis, and interactive HTML export.

**Architecture:** A modular 5-tier architecture: (1) Scanner with `.gitignore` and minified JS exclusion, (2) Tree-sitter AST extractors for Rust and TS/Vue, (3) Two-pass symbol resolution into an in-memory directed graph, (4) Graph topology algorithms (weighted centrality, BFS shortest path, reverse impact traversal), and (5) Exporters generating `graph.json`, `REPORT.md`, and an embedded standalone `graph.html`.

**Tech Stack:** Rust 1.90+, `tree-sitter`, `tree-sitter-rust`, `tree-sitter-typescript`, `ignore`, `rayon`, `serde`, `serde_json`, `clap` v4.

**Spec:** [docs/superpowers/specs/2026-11-04-codegraph-design.md](file:///D:/mcp-server-test/docs/superpowers/specs/2026-11-04-codegraph-design.md)

## Global Constraints

- Standalone workspace location: `D:\codegraph`.
- Zero cloud/LLM runtime dependencies; 100% offline deterministic processing.
- Automatically exclude `*.min.js`, `*.bundle.js`, `dist/`, `build/`, `target/`, and `node_modules/`.
- Single self-contained `graph.html` output containing all CSS/JS inline (no external CDN required).
- All file paths in graph model normalized to forward slashes (`/`).

## Review Focus

1. **Circular references between modules:** Cyclic dependency loops must not cause infinite loops in BFS or reverse DFS traversal.
2. **Ambiguous symbol resolution:** Multiple functions or structs with identical names across different files must resolve using file context or remain clearly disambiguated.
3. **Vue `<script setup>` syntax:** Vue Single File Components with `<script setup lang="ts">` must correctly extract TypeScript definitions without tripping on template/style tags.
4. **Syntax error resiliency:** Files containing incomplete or malformed syntax must produce partial AST nodes rather than crashing the scan.
5. **Path separator cross-platform handling:** Windows backslashes `\` in paths must be normalized to `/` in Node IDs to ensure cross-platform reproducibility.

---

### Task 1: Project Scaffolding & Core Graph Data Model

**Files:**
- Create: `D:\codegraph\Cargo.toml`
- Create: `D:\codegraph\src\lib.rs`
- Create: `D:\codegraph\src\model\mod.rs`
- Test: `D:\codegraph\tests\test_model.rs`

**Interfaces:**
- Produces:
  ```rust
  pub enum NodeKind { File, Module, Struct, Enum, Trait, Function, Class, Interface, Package }
  pub enum Relation { Defines, Imports, Calls, Implements, References, DependsOn }
  pub struct Node { pub id: String, pub label: String, pub kind: NodeKind, pub file_path: String, pub line_range: (usize, usize), pub in_degree: usize, pub out_degree: usize }
  pub struct Edge { pub source: String, pub target: String, pub relation: Relation, pub confidence: f32 }
  pub struct GraphDataset { pub nodes: Vec<Node>, pub edges: Vec<Edge> }
  ```

- [ ] **Step 1: Create repository directory and initialized Cargo.toml**
- [ ] **Step 2: Write failing test in `tests/test_model.rs` testing JSON serialization and deserialization of `GraphDataset`**
- [ ] **Step 3: Implement data models in `src/model/mod.rs` and re-export in `src/lib.rs`**
- [ ] **Step 4: Run `cargo test --test test_model` and verify it passes**

---

### Task 2: File Scanner with Ignore & Language Filtering

**Files:**
- Create: `D:\codegraph\src\scanner\mod.rs`
- Test: `D:\codegraph\tests\test_scanner.rs`

**Interfaces:**
- Consumes: Models
- Produces:
  ```rust
  #[derive(Debug, PartialEq, Eq, Clone)]
  pub enum Language { Rust, TypeScript, JavaScript, Vue, CargoToml, PackageJson }
  pub struct SourceFile { pub path: String, pub language: Language }
  pub fn scan_directory(root: &std::path::Path) -> Result<Vec<SourceFile>, std::io::Error>;
  ```

- [ ] **Step 1: Write failing test in `tests/test_scanner.rs` with temporary directory containing `.rs`, `.ts`, `.vue`, `.min.js`, and `.git`**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement `scan_directory` using `ignore::WalkBuilder` with filter rules ignoring `.min.js`, `target`, `node_modules`**
- [ ] **Step 4: Run `cargo test --test test_scanner` and verify it passes**

---

### Task 3: Rust AST Extractor (Tree-sitter)

**Files:**
- Create: `D:\codegraph\src\extractor\mod.rs`
- Create: `D:\codegraph\src\extractor\rust_lang.rs`
- Test: `D:\codegraph\tests\test_rust_extractor.rs`

**Interfaces:**
- Produces:
  ```rust
  pub struct RawSymbol { pub name: String, pub kind: NodeKind, pub line_range: (usize, usize) }
  pub struct RawReference { pub source_symbol: Option<String>, pub target_name: String, pub relation: Relation }
  pub struct ExtractedFile { pub file_path: String, pub symbols: Vec<RawSymbol>, pub references: Vec<RawReference> }
  pub fn extract_rust(file_path: &str, content: &str) -> Result<ExtractedFile, String>;
  ```

- [ ] **Step 1: Write failing test in `tests/test_rust_extractor.rs` containing struct, enum, fn, and use statement**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement Tree-sitter Rust AST extractor queries in `src/extractor/rust_lang.rs`**
- [ ] **Step 4: Run `cargo test --test test_rust_extractor` and verify it passes**

---

### Task 4: TypeScript, JavaScript & Vue SFC Extractor

**Files:**
- Create: `D:\codegraph\src\extractor\ts_lang.rs`
- Test: `D:\codegraph\tests\test_ts_extractor.rs`

**Interfaces:**
- Produces:
  ```rust
  pub fn extract_typescript(file_path: &str, content: &str, is_vue: bool) -> Result<ExtractedFile, String>;
  ```

- [ ] **Step 1: Write failing test in `tests/test_ts_extractor.rs` for TS classes, interfaces, import statements, and Vue `<script>` blocks**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement `extract_typescript` using `tree-sitter-typescript` (extracting `<script>` block when `is_vue = true`)**
- [ ] **Step 4: Run `cargo test --test test_ts_extractor` and verify it passes**

---

### Task 5: Two-Pass Symbol Resolution & Graph Assembly

**Files:**
- Create: `D:\codegraph\src\graph\mod.rs`
- Test: `D:\codegraph\tests\test_graph_builder.rs`

**Interfaces:**
- Consumes: `Vec<ExtractedFile>`
- Produces:
  ```rust
  pub fn build_graph(files: Vec<ExtractedFile>) -> GraphDataset;
  ```

- [ ] **Step 1: Write failing test in `tests/test_graph_builder.rs` with cross-file references between two files**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement Pass 1 (registry indexing) and Pass 2 (reference linking + in/out degree counting) in `src/graph/mod.rs`**
- [ ] **Step 4: Run `cargo test --test test_graph_builder` and verify it passes**

---

### Task 6: Graph Algorithms (Centrality, God Nodes, Shortest Path, Impact Analysis)

**Files:**
- Create: `D:\codegraph\src\graph\topology.rs`
- Create: `D:\codegraph\src\graph\traversal.rs`
- Test: `D:\codegraph\tests\test_algorithms.rs`

**Interfaces:**
- Produces:
  ```rust
  pub struct GodNode { pub id: String, pub label: String, pub score: f32, pub in_degree: usize, pub out_degree: usize }
  pub fn compute_god_nodes(graph: &GraphDataset, top_n: usize) -> Vec<GodNode>;
  pub fn find_shortest_path(graph: &GraphDataset, start_id: &str, end_id: &str) -> Option<Vec<String>>;
  pub fn find_affected(graph: &GraphDataset, target_id: &str) -> Vec<String>;
  ```

- [ ] **Step 1: Write failing test in `tests/test_algorithms.rs` on a synthetic diamond & cyclic graph structure**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement weighted degree centrality in `topology.rs` and BFS / reverse DFS in `traversal.rs` with cycle detection**
- [ ] **Step 4: Run `cargo test --test test_algorithms` and verify it passes**

---

### Task 7: Exporters (JSON, Markdown Report & Standalone Interactive HTML)

**Files:**
- Create: `D:\codegraph\src\export\json.rs`
- Create: `D:\codegraph\src\export\report.rs`
- Create: `D:\codegraph\src\export\html.rs`
- Test: `D:\codegraph\tests\test_exporters.rs`

**Interfaces:**
- Produces:
  ```rust
  pub fn export_all(graph: &GraphDataset, out_dir: &std::path::Path) -> Result<(), std::io::Error>;
  ```

- [ ] **Step 1: Write failing test in `tests/test_exporters.rs` verifying creation of `graph.json`, `REPORT.md`, and `graph.html`**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement JSON export, Markdown report generator, and standalone HTML with embedded canvas/SVG interactive visualizer**
- [ ] **Step 4: Run `cargo test --test test_exporters` and verify it passes**

---

### Task 8: CLI Interface (`codegraph`) & End-to-End Integration

**Files:**
- Create: `D:\codegraph\src\main.rs`
- Test: `D:\codegraph\tests\test_e2e.rs`

**Interfaces:**
- Subcommands:
  - `codegraph scan [path]`
  - `codegraph god-nodes [--top N]`
  - `codegraph affected <symbol>`
  - `codegraph path <source> <target>`

- [ ] **Step 1: Write failing integration test in `tests/test_e2e.rs` executing CLI commands against a mini fixture project**
- [ ] **Step 2: Run test and verify failure**
- [ ] **Step 3: Implement `clap` derive parser and wire up all subcommands in `src/main.rs`**
- [ ] **Step 4: Run `cargo test` and verify all tests pass across the entire workspace**
- [ ] **Step 5: Run `codegraph scan .` against real code and verify output**
