use serde_json::json;
use std::path::Path;
use std::process::Stdio;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::process::Command;

pub struct StdioMcpClient;

impl StdioMcpClient {
    /// Executes a tool call on a Python MCP server script via Stdio JSON-RPC 2.0
    pub async fn execute_tool(
        python_path: &Path,
        server_script: &Path,
        tool_name: &str,
        arguments: &serde_json::Value,
    ) -> Result<serde_json::Value, String> {
        let mut child = Command::new(python_path)
            .arg(server_script)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to spawn MCP server process: {}", e))?;

        let mut stdin = child.stdin.take().ok_or("Failed to open stdin")?;
        let stdout = child.stdout.take().ok_or("Failed to open stdout")?;

        let request = json!({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        });

        let mut req_str = request.to_string();
        req_str.push('\n');

        stdin
            .write_all(req_str.as_bytes())
            .await
            .map_err(|e| format!("Failed to write to stdin: {}", e))?;

        let mut reader = BufReader::new(stdout).lines();
        // Wait for response line with a timeout
        let response_line = tokio::time::timeout(std::time::Duration::from_secs(10), reader.next_line())
            .await
            .map_err(|_| "MCP tool execution timed out (10s)".to_string())?
            .map_err(|e| format!("Failed to read stdout: {}", e))?
            .ok_or("MCP server closed stdout without responding")?;

        let resp_json: serde_json::Value =
            serde_json::from_str(&response_line).map_err(|e| format!("Invalid JSON response: {}", e))?;

        if let Some(err) = resp_json.get("error") {
            return Err(format!("MCP error: {}", err));
        }

        Ok(resp_json.get("result").cloned().unwrap_or(serde_json::Value::Null))
    }
}
