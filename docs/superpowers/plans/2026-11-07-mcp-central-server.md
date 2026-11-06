# MCP Central Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, enterprise-grade Spring Boot 3 Central Storage & Dependency Gateway server in `D:\mcp-central-server` (Port 8080) with embedded H2 database, automated catalog seeding, Zip-Slip protected upload/git-import, and mock wheels dependency gateway.

**Architecture:** Independent Spring Boot 3.4.x application in `D:\mcp-central-server` acting as Central Registry & Dependency Gateway. Stores metadata in embedded H2 database (`mcp_central.mv.db`), packages in `storage/mcp-packages/`, and cached wheels in `storage/wheels-cache/`. Clients in `D:\mcp-server-test` consume this Central Server exclusively via HTTP REST endpoints.

**Tech Stack:** Java 21, Spring Boot 3.4.x, Spring Data JPA, H2 Database (with H2 Console), Maven, JUnit 5, MockMvc.

**Spec:** `docs/superpowers/specs/2026-11-07-mcp-central-server-design.md`

## Global Constraints
- Target directory: `D:\mcp-central-server\`
- Java version: JDK 21 (Zulu OpenJDK 21)
- Server port: 8080
- Embedded database: H2 file-based (`jdbc:h2:file:./data/mcp_central;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE`)
- Security: Zip-Slip vulnerability detection on all zip extraction / stream operations
- Client repository: `D:\mcp-server-test\` remains pure client host calling `http://localhost:8080`

## Review Focus
1. Zip-Slip directory traversal attempts (`../` or leading slash paths) must throw `SecurityException` and return HTTP 400.
2. Incomplete or corrupted ZIP uploads must return HTTP 400 Bad Request with an informative JSON message without corrupting disk storage.
3. Requests for non-existent package IDs on download or wheels endpoints must return HTTP 404 Not Found.
4. Dependency Gateway (`GET /packages/{id}/wheels`) must generate a valid mock wheels zip containing standard `.whl` files when Nexus is offline, preventing client install failure.
5. Deleting a package (`DELETE /packages/{id}`) must atomically remove the DB record, the source `.zip`, and the cached `{id}-wheels.zip`.

---

### Task 1: Project Scaffolding in `D:\mcp-central-server`

**Files:**
- Create: `D:\mcp-central-server\pom.xml`
- Create: `D:\mcp-central-server\src\main\resources\application.yml`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\McpCentralServerApplication.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\config\CorsConfig.java`
- Create: `D:\mcp-central-server\run_server.bat`

**Interfaces:**
- Produces: Running Spring Boot skeleton with H2 datasource, H2 console on `/h2-console`, and CORS configured for all origins (`*`).

- [ ] **Step 1: Create directory tree for `D:\mcp-central-server`**
- [ ] **Step 2: Create `pom.xml` with dependencies** (Spring Boot 3.4.x, Web, Data JPA, H2, Lombok, Validation, Test)
- [ ] **Step 3: Create `src/main/resources/application.yml`**
- [ ] **Step 4: Create `McpCentralServerApplication.java` and `CorsConfig.java`**
- [ ] **Step 5: Setup Maven wrapper and create `run_server.bat`**
- [ ] **Step 6: Run Maven compile to verify dependency resolution and build success**
  - Run: `mvn clean compile` in `D:\mcp-central-server`
  - Expected: `BUILD SUCCESS`

---

### Task 2: Data Migration & Storage Folder Setup

**Files:**
- Create: `D:\mcp-central-server\storage\mcp-packages\`
- Create: `D:\mcp-central-server\storage\wheels-cache\`
- Create: `D:\mcp-central-server\data\`
- Copy: All 11 `.zip` files from `D:\mcp-server-test\storage\packages\` into `D:\mcp-central-server\storage\mcp-packages\`
- Copy: `D:\mcp-server-test\storage\catalog.json` into `D:\mcp-central-server\src\main\resources\catalog-seed.json`

**Interfaces:**
- Produces: Seed JSON file in classpath and source code ZIP files in `D:\mcp-central-server\storage\mcp-packages\`.

- [ ] **Step 1: Create target storage directories in `D:\mcp-central-server`**
- [ ] **Step 2: Copy MCP zip packages (`postgres.zip`, `excel.zip`, `filesystem.zip`, etc.) from client workspace to central server storage**
- [ ] **Step 3: Copy `catalog.json` to `src/main/resources/catalog-seed.json`**
- [ ] **Step 4: Verify all 11 zip files are intact in `storage/mcp-packages/`**

---

### Task 3: JPA Entities, Repositories, and DTOs

**Files:**
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\entity\McpPackage.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\entity\McpTool.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\entity\McpEnvRequirement.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\repository\McpPackageRepository.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\repository\McpToolRepository.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\dto\CatalogResponse.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\dto\PluginItemDto.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\dto\PluginToolDto.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\dto\GitImportRequest.java`
- Test: `D:\mcp-central-server\src\test\java\com\company\mcp\repository\McpPackageRepositoryTest.java`

**Interfaces:**
- Produces: JPA entities with cascades, Spring Data query methods `findById`, `findByNameContainingIgnoreCaseOrDescriptionContainingIgnoreCase`, and DTO conversions.

- [ ] **Step 1: Write failing DataJpaTest `McpPackageRepositoryTest.java`**
- [ ] **Step 2: Run test to confirm it fails (classes not yet defined)**
- [ ] **Step 3: Implement entities `McpPackage`, `McpTool`, `McpEnvRequirement` and repositories**
- [ ] **Step 4: Implement DTOs conforming to the client contract**
- [ ] **Step 5: Run DataJpaTest and verify it passes**

---

### Task 4: Automated Seed Service & Catalog Endpoints

**Files:**
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\service\CatalogSeedService.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\controller\McpCatalogController.java`
- Test: `D:\mcp-central-server\src\test\java\com\company\mcp\controller\McpCatalogControllerTest.java`

**Interfaces:**
- Consumes: `McpPackageRepository`, `catalog-seed.json`
- Produces:
  - Startup seed routine via `ApplicationRunner`
  - `GET /api/v1/catalog` and `GET /api/v1/mcp/packages` returning `CatalogResponse`
  - `GET /api/v1/mcp/packages/{id}` returning package detail

- [ ] **Step 1: Write MockMvc test `McpCatalogControllerTest.java` testing `/api/v1/catalog` and search**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `CatalogSeedService` to populate H2 on startup from `catalog-seed.json`**
- [ ] **Step 4: Implement `McpCatalogController` with search and category filtering**
- [ ] **Step 5: Run MockMvc test and verify it passes with 11 seeded packages**

---

### Task 5: Package Storage Service & Mock Nexus Dependency Gateway

**Files:**
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\service\PackageStorageService.java`
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\service\DependencyGatewayService.java`
- Test: `D:\mcp-central-server\src\test\java\com\company\mcp\service\PackageStorageServiceTest.java`

**Interfaces:**
- Produces:
  - `PackageStorageService.validateZipSafety(InputStream)` - Zip-Slip guard
  - `PackageStorageService.savePackage(String id, MultipartFile file)`
  - `PackageStorageService.loadPackageResource(String filename)`
  - `PackageStorageService.deletePackage(String id)`
  - `DependencyGatewayService.getOrBuildWheelsZip(String id)` - returns `Path` to `{id}-wheels.zip`

- [ ] **Step 1: Write unit tests in `PackageStorageServiceTest.java` testing Zip-Slip detection and wheel bundle creation**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `PackageStorageService` with strict Zip-Slip and SHA-256 validation**
- [ ] **Step 4: Implement `DependencyGatewayService` with offline mock wheel bundling**
- [ ] **Step 5: Run unit tests and verify they pass**

---

### Task 6: McpPackageController (Upload, Git Import, Download, Wheels, Delete)

**Files:**
- Create: `D:\mcp-central-server\src\main\java\com\company\mcp\controller\McpPackageController.java`
- Test: `D:\mcp-central-server\src\test\java\com\company\mcp\controller\McpPackageControllerTest.java`

**Interfaces:**
- Endpoints:
  - `POST /api/v1/mcp/upload`
  - `POST /api/v1/mcp/import-git`
  - `GET /api/v1/mcp/download/{id}`
  - `GET /api/v1/mcp/packages/{id}/wheels`
  - `DELETE /api/v1/mcp/packages/{id}`

- [ ] **Step 1: Write MockMvc tests covering upload, download, wheels stream, and delete**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `McpPackageController`**
- [ ] **Step 4: Run MockMvc tests and verify all pass**

---

### Task 7: Client Alignment & End-to-End Verification

**Files:**
- Update/Clean: `D:\mcp-server-test\storage\packages` (mark as migrated or remove old zip files)
- Create verification test script: `D:\mcp-central-server\test_e2e_api.ps1`

- [ ] **Step 1: Clean legacy `storage/packages` in `D:\mcp-server-test` to ensure client does not rely on local packages**
- [ ] **Step 2: Start Central Server in background using `mvn spring-boot:run`**
- [ ] **Step 3: Execute `test_e2e_api.ps1` testing: catalog list, package detail, download zip, wheels zip, upload zip, and delete**
- [ ] **Step 4: Confirm all HTTP endpoints return status 200 OK / 201 Created with valid payloads**
- [ ] **Step 5: Stop background server and report completion**
