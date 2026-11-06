# Design Specification: MCP Central Storage & Dependency Gateway (Spring Boot 3)

**Date:** 2026-11-07  
**Status:** Approved  
**Author:** Pair Programming (User & Antigravity)  
**Target Repository:** `D:\mcp-central-server` (Independent Spring Boot Project)  
**Client Project:** `D:\mcp-server-test` (Tauri Rust Desktop + Vue Web Studio)

---

## 1. Executive Summary & Goals

Based on the technical blueprint defined in `D:\mcp-server-test\docs\architecture\mcp-full-scenario-workflow.md`, this specification defines the implementation of the enterprise **Central Java Server** as a completely separated, standalone backend service running on port `8080`.

### Key Objectives
1. **Complete Architectural Separation:** The Central Server resides in an independent directory `D:\mcp-central-server`, isolating enterprise storage and dependencies from client workstations.
2. **Central Storage & Migration:** Migrate all 11 existing pre-packaged MCP `.zip` bundles from `D:\mcp-server-test\storage\packages\` into `D:\mcp-central-server\storage\mcp-packages\`.
3. **Embedded H2 Database & Metadata Engine:** Store package metadata, tool schemas, environment variable definitions, and version histories using Spring Data JPA with an H2 file-based database (`mcp_central.mv.db`) and Web H2 Console.
4. **Automated Seed Initialization:** On initial startup, automatically parse `catalog.json` and initialize the H2 database so that all 11 packages and their tools are immediately ready to serve.
5. **API Contract Fulfillment:** Implement all Central Server endpoints per `mcp-full-scenario-workflow.md`:
   - `POST /api/v1/mcp/upload` (Multipart ZIP upload with Zip-Slip protection)
   - `POST /api/v1/mcp/import-git` (GitHub URL repository import)
   - `GET /api/v1/catalog` and `GET /api/v1/mcp/packages` (Catalog query with search/category filter)
   - `GET /api/v1/mcp/packages/{id}` (Package and tool schema details)
   - `GET /api/v1/mcp/download/{id}` (Source code ZIP download)
   - `GET /api/v1/mcp/packages/{id}/wheels` (Dependency Gateway wheels bundle download)
   - `DELETE /api/v1/mcp/packages/{id}` (Central server purge)
6. **Mock Nexus Dependency Gateway:** When client requests `{id}/wheels`, inspect cache in `storage/wheels-cache/{id}-wheels.zip`. If absent, automatically resolve requirements and package valid binary `.whl` files offline so that client `uv pip install --no-index` succeeds without needing an external corporate Nexus instance during test and dev.
7. **Client Alignment:** Client workstations in `D:\mcp-server-test` communicate exclusively via HTTP REST calls to `http://localhost:8080` for package discovery and downloads.

---

## 2. Directory Structure & Boundaries

### 2.1 Backend Project: `D:\mcp-central-server\`
```
D:\mcp-central-server\
├── pom.xml                                   # Maven POM (Spring Boot 3.4.x, Java 21)
├── mvnw / mvnw.cmd                           # Maven Wrapper
├── run_server.bat                            # Single-click launcher
├── data/
│   └── mcp_central.mv.db                     # Persistent H2 Database
├── storage/
│   ├── mcp-packages/                         # 11 source code ZIPs (postgres.zip, etc.)
│   └── wheels-cache/                         # Cached wheels ZIPs ({id}-wheels.zip)
└── src/
    ├── main/
    │   ├── java/com/company/mcp/
    │   │   ├── McpCentralServerApplication.java
    │   │   ├── config/
    │   │   │   ├── CorsConfig.java           # Cross-Origin support for Web Studio
    │   │   │   └── StorageProperties.java    # Configurable paths & Nexus URL
    │   │   ├── controller/
    │   │   │   ├── McpPackageController.java # Upload, Import Git, Download, Delete
    │   │   │   └── McpCatalogController.java # /api/v1/catalog & /api/v1/mcp/packages
    │   │   ├── dto/
    │   │   │   ├── GitImportRequest.java
    │   │   │   ├── CatalogResponse.java
    │   │   │   └── PackageDetailResponse.java
    │   │   ├── entity/
    │   │   │   ├── McpPackage.java
    │   │   │   ├── McpTool.java
    │   │   │   └── McpEnvRequirement.java
    │   │   ├── repository/
    │   │   │   ├── McpPackageRepository.java
    │   │   │   └── McpToolRepository.java
    │   │   └── service/
    │   │       ├── PackageStorageService.java
    │   │       ├── DependencyGatewayService.java
    │   │       └── CatalogSeedService.java   # Auto-seeds H2 from catalog.json
    │   └── resources/
    │       ├── application.yml
    │       └── catalog-seed.json             # Seed data bundled into resources
    └── test/
        └── java/com/company/mcp/
            └── McpCentralServerTests.java    # MockMvc Integration Tests
```

### 2.2 Client Project: `D:\mcp-server-test\`
- Acts as **Local Desktop Host & Web Studio**:
  - `apps/desktop/`: Rust Tauri Client running on `http://127.0.0.1:8000`.
  - `frontend/`: Vue 3 Web Studio connecting to Central Server `http://localhost:8080` (or local gateway).
  - `bin/uv.exe`: Python virtualenv and package installer.
  - The legacy `storage/packages/` folder is cleared or relocated to the central server.

---

## 3. Database Schema & JPA Entity Model

### 3.1 Entity Relationship Diagram

```mermaid
erDiagram
    MCP_PACKAGE ||--o{ MCP_TOOL : contains
    MCP_PACKAGE ||--o{ MCP_ENV_REQUIREMENT : requires

    MCP_PACKAGE {
        string id PK "Unique Package Identifier (e.g. postgres)"
        string name "Display Name"
        string version "Semantic Version"
        string vendor "Author or Vendor"
        string category "Category (Database, DevOps, etc.)"
        string icon "PrimeIcon or Icon Class"
        double rating "Rating score (0.0 - 5.0)"
        string downloads "Download count string (e.g. 110.4k)"
        string summary "Short summary"
        string description "Detailed description"
        string runtime "Default: python"
        string package_file "Stored filename in storage/mcp-packages/"
        string sha256 "SHA-256 Checksum"
        timestamp created_at
        timestamp updated_at
    }

    MCP_TOOL {
        bigint id PK "Auto Increment"
        string package_id FK "Refers to MCP_PACKAGE.id"
        string name "Tool function name"
        string description "Tool functionality description"
        string parameters_schema "JSON Schema string of parameters"
    }

    MCP_ENV_REQUIREMENT {
        bigint id PK "Auto Increment"
        string package_id FK "Refers to MCP_PACKAGE.id"
        string key_name "Environment variable key"
        string label "Display label"
        string default_value "Default fallback value"
        boolean required "Mandatory flag"
        string var_type "string | secret | number"
    }
```

---

## 4. API Specifications & Request/Response Contracts

### 4.1 Catalog Endpoints
* **`GET /api/v1/catalog`** and **`GET /api/v1/mcp/packages`**
  - Query parameters: `q` (search string), `category` (category filter)
  - Status: `200 OK`
  - Response:
    ```json
    {
      "total": 11,
      "servers": [
        {
          "id": "postgres",
          "name": "PostgreSQL Database Engine",
          "version": "1.2.0",
          "vendor": "Antigravity Systems",
          "icon": "pi pi-database",
          "category": "In-House Tools",
          "summary": "Read and execute SQL queries against PostgreSQL instances.",
          "description": "Standard PostgreSQL MCP server...",
          "tools": [
            {
              "name": "postgres_execute_query",
              "description": "Executes SQL query against Postgres database",
              "parameters": {}
            }
          ],
          "envRequirements": [
            {
              "key": "DATABASE_URL",
              "label": "Connection String",
              "default": "postgresql://postgres:postgres@localhost:5432/mcp_test",
              "required": true
            }
          ]
        }
      ]
    }
    ```

* **`GET /api/v1/mcp/packages/{id}`**
  - Returns the single package metadata with its tool definitions and environment requirements.

### 4.2 Package Upload & Git Import Endpoints
* **`POST /api/v1/mcp/upload`**
  - Consumes: `multipart/form-data`
  - Request Parts:
    - `file`: MultipartFile (`.zip` format)
    - `name`: (Optional) Display name override
    - `description`: (Optional) Description override
    - `env_requirements`: (Optional) JSON array string
  - Processing:
    1. Validate non-empty `.zip`.
    2. Check Zip-Slip vulnerability (reject `../` or absolute path prefixes).
    3. Verify and read `manifest.json`.
    4. Compute SHA-256 hash.
    5. Save to `storage/mcp-packages/{id}.zip`.
    6. Upsert metadata in H2 database.
  - Status: `201 Created` or `200 OK`

* **`POST /api/v1/mcp/import-git`**
  - Consumes: `application/json`
  - Request Body:
    ```json
    {
      "repoUrl": "https://github.com/org/mcp-service",
      "branch": "main",
      "token": "ghp_...",
      "name": "Custom Service",
      "description": "Service imported from GitHub"
    }
    ```
  - Processing:
    1. Parse owner and repository name.
    2. Download repo zipball via GitHub REST API (or generate mock package if offline/mock mode).
    3. Validate Zip-Slip & manifest.
    4. Save to `storage/mcp-packages/{repo}-{branch}.zip` and save entity to H2.
  - Status: `201 Created`

### 4.3 Package Download & Dependency Gateway Endpoints
* **`GET /api/v1/mcp/download/{id}`**
  - Resolves file `storage/mcp-packages/{id}.zip`.
  - Headers: `Content-Type: application/octet-stream`, `Content-Disposition: attachment; filename="{id}.zip"`.
  - Body: Binary stream (~20KB).

* **`GET /api/v1/mcp/packages/{id}/wheels`**
  - **Dependency Gateway Workflow:**
    1. Checks if `storage/wheels-cache/{id}-wheels.zip` exists.
    2. If missing:
       - Inspects `storage/mcp-packages/{id}.zip` for `requirements.txt`.
       - If requirements are present, attempts to fetch wheels from configured `nexus.pypi.url`.
       - If Nexus is offline / mock mode: Generates a mock `.whl` bundle containing matching wheel archives (e.g. `mcp-1.0.0-py3-none-any.whl`, dummy wheels) or packaged pure-Python wheels, then zips them into `storage/wheels-cache/{id}-wheels.zip`.
    3. Streams `{id}-wheels.zip` back to client.

### 4.4 Server Purge Endpoint
* **`DELETE /api/v1/mcp/packages/{id}`**
  - Removes record from H2 database (`mcp_package`, `mcp_tool`, `mcp_env_requirement`).
  - Deletes `storage/mcp-packages/{id}.zip`.
  - Deletes `storage/wheels-cache/{id}-wheels.zip`.
  - Returns: `{"status": "success", "packageId": "{id}", "message": "Purged from central storage"}`.

---

## 5. Security & Zip-Slip Protection

All incoming ZIP archives (via file upload or GitHub import) are subject to strict stream traversal validation:
```java
public static void validateZipSafety(InputStream inputStream) throws IOException {
    try (ZipInputStream zis = new ZipInputStream(inputStream)) {
        ZipEntry entry;
        while ((entry = zis.getNextEntry()) != null) {
            String name = entry.getName();
            if (name.contains("..") || name.startsWith("/") || name.startsWith("\\")) {
                throw new SecurityException("Zip-Slip vulnerability detected: " + name);
            }
        }
    }
}
```

---

## 6. Seed Data & Migration Plan

1. **Physical Migration:**
   - Copy `D:\mcp-server-test\storage\packages\*.zip` (all 11 files) to `D:\mcp-central-server\storage\mcp-packages\`.
   - Copy `D:\mcp-server-test\storage\catalog.json` to `D:\mcp-central-server\src\main\resources\catalog-seed.json`.
2. **Automated H2 Seeding:**
   - On application startup (`ApplicationRunner`), `CatalogSeedService` checks if `McpPackageRepository.count() == 0`.
   - If empty, parses `catalog-seed.json` and inserts all package items, tool schemas, and environment requirements into H2 database.
3. **Client Configuration:**
   - Ensure `frontend/src/features/plugins/stores/pluginStore.ts` and `apps/desktop/src/commands.rs` use `http://localhost:8080` as the central registry endpoint.

---

## 7. Testing & Verification

1. **Unit & MockMvc Tests:**
   - `McpCentralServerTests.java`:
     - Test `GET /api/v1/catalog` returns 11 seeded packages.
     - Test `GET /api/v1/mcp/packages/postgres` returns PostgreSQL tools.
     - Test `GET /api/v1/mcp/download/postgres` streams valid ZIP.
     - Test `GET /api/v1/mcp/packages/postgres/wheels` returns valid wheels ZIP.
     - Test `POST /api/v1/mcp/upload` creates new package.
     - Test `DELETE /api/v1/mcp/packages/{id}` purges package.
2. **End-to-End Build & Launch Test:**
   - Compile via `./mvnw clean package` / `mvn test`.
   - Start server on port `8080` and verify HTTP 200 via PowerShell `Invoke-RestMethod`.
