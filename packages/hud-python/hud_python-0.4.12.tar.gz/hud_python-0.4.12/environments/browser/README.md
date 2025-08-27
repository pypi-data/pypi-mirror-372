# Browser MCP Environment

A browser automation environment for the HUD platform demonstrating best practices for building MCP (Model Context Protocol) environments with evaluation systems.

**Key Feature**: This environment is **hot-reloadable** - it maintains state (running services, browser sessions, launched apps) across server restarts during development.

## Quick Start

### Build & Deploy
```bash
# Build the Docker image
cd environments/browser
docker build -t hud-browser .

# Run with stdio (recommended for HUD SDK v3)
docker run --rm -i -p 8080:8080 hud-browser
```

### Hot-Reloadable Architecture

This environment uses a persistent context server architecture that maintains state across MCP server restarts:

- **Context Server**: Runs as a separate process holding ServiceManager and state
- **MCP Server**: Connects via Unix socket, can restart without losing services
- **State Preservation**: X11, VNC, running apps, and service states persist
- **Development Friendly**: Edit code and restart MCP server instantly

#### Docker Architecture

The environment uses a single CMD that follows the proven text_2048 pattern:

```dockerfile
CMD ["sh", "-c", "\
    # Start services in background \
    python -m hud_controller.context_server & \
    x11vnc ... & \
    # Run MCP server in foreground \
    exec hud-controller mcp \
"]
```

This pattern ensures:
- Background services (`&`) start once and persist
- Only the `exec` command gets wrapped by watchfiles
- Services survive hot-reloads during development

## Deployment to Registry

### 1. Publish to Docker Registry

#### Docker Hub
```bash
# Build and push to Docker Hub
docker build -t your-username/hud-browser:latest .
docker push your-username/hud-browser:latest
```

#### GitHub Container Registry (GHCR)
```bash
# Login and push to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u your-username --password-stdin
docker build -t ghcr.io/your-org/hud-browser:latest .
docker push ghcr.io/your-org/hud-browser:latest
```

### 2. Use via HUD Cloud Orchestrator

```python
import os
import hud
from hud.clients import MCPClient
from hud.agents import ClaudeAgent

BASE_URL = "https://mcp.hud.so/v3/mcp"
HUD_API_KEY = os.getenv("HUD_API_KEY")

async def main():
    with hud.trace() as run_id:
        # Configure MCP client to connect to the cloud orchestrator
        config = {
            "mcp_config": {
                "browser": {
                    "url": f"{BASE_URL}/v3/mcp",
                    "headers": {
                        "Authorization": f"Bearer {HUD_API_KEY}",
                        "Mcp-Image": "your-username/hud-browser:latest",  # Your published image
                        "Run-Id": run_id,
                    },
                }
            }
        }

        client = MCPClient.from_dict(config)
        agent = ClaudeAgent(
            client=client,
            model="claude-sonnet-4-20250514",
            allowed_tools=["computer", "setup", "evaluate"]
        )

        # Use your environment in the cloud
        await agent.run("Set up the todo app and evaluate completion")
```

### 3. Local Development (stdio)

For local testing and development:

```python
# Local Docker with stdio transport
config = {
    "mcp_config": {
        "browser": {
            "command": "docker",
            "args": ["run", "--rm", "-i", "-p", "8080:8080", "hud-browser"]
        }
    }
}
```

See the HUD documentation for complete working examples.

## Environment Design Strategy

### Core Principles for MCP Environments

1. **Clean Protocol Separation**
   - All logging to stderr, only JSON-RPC to stdout
   - Use `@mcp.initialize` for progress notifications
   - Register shutdown cleanup with `@mcp.shutdown`

2. **Evaluation System Architecture**
   - **Class-based problems** with inheritance for reusability
   - **App-centric evaluation** - backends provide `/api/eval/*` endpoints
   - **Hub pattern for discovery (`@setup.tool`, `@evaluate.tool`, problems registry)**
   - **MCP resources** for runtime introspection

3. **Service Management**
   - Start core services (X11, VNC) before MCP initialization
   - Use progress notifications for long-running setup
   - Graceful error handling with meaningful messages

4. **Tool Design**
   - `setup` and `evaluate` tools with dual interfaces:
     - Direct: `{"function": "tool_name", "args": {...}}`
     - Problem-based: `{"name": "problem_name"}`
   - Environment context objects for unified API access
   - Factory patterns for runtime instantiation

### Environment Variables Strategy

Set these in your environment/Docker configuration:

#### Required
- `DISPLAY=:1` - X11 display number for GUI automation
- `PYTHONUNBUFFERED=1` - Prevent output buffering for real-time logs

#### Optional
- `BROWSER_URL` - Initial navigation URL (default: google.com)
- `LOG_LEVEL` - Logging verbosity (`DEBUG`, `INFO`, `WARNING`)

#### MCP-Specific
- Set in client configuration, not container:
  - Progress tokens for initialization feedback
  - Tool allowlists for security
  - Transport method (stdio vs HTTP)

### Common Pitfalls & Solutions

1. **stdout Contamination**
   ```bash
   # ❌ Wrong - X11 warnings go to stdout
   Xvfb :1 -screen 0 1024x768x24
   
   # ✅ Correct - Redirect stderr
   Xvfb :1 -screen 0 1024x768x24 2>/dev/null
   ```

2. **"Invalid request parameters" for tools/list**
   - Ensure your client sends `InitializedNotification` after receiving `InitializeResult`
   - The MCP protocol requires this handshake before tools are available

3. **No tools registered**
   - Check that tools requiring X11 are registered AFTER X11 is ready
   - Add tools via `mcp.add_tool(instance)` once prerequisites are ready
   - Verify initialization completes before restoring handler

4. **Evaluation fails unexpectedly**
   - Ensure apps are launched before running evaluations
   - Check that app backend APIs are responding (`/api/eval/health`)
   - Verify problem setup completed successfully before evaluation
   - Use clean state between test runs (`reset` then `seed`)

5. **Progress notifications not working**
   - Ensure `progressToken` is provided in `InitializeRequest`
   - Use `@mcp.initialize` decorator correctly
   - Send progress updates between 0-100 with meaningful messages

### Architecture Pattern

```
Docker Container
├── MCP Server (FastMCP)     # Protocol implementation
│   ├── Tools                # setup, evaluate, computer, etc.
│   └── Resources            # Dynamic registry discovery
├── Context Server           # Persistent state management
│   └── PersistentContext    # Maintains services & browser state
├── Services
│   ├── X11 (Xvfb)          # Virtual display
│   ├── VNC + Websockify    # Remote access
│   └── Apps                # Web applications
└── Evaluation System
    ├── Evaluators          # @evaluator decorated classes
    ├── Setup Tools         # @setup decorated classes
    ├── Problems            # @problem decorated classes
    └── Context             # Unified environment API
```

## File Structure Overview

```
browser/
├── Dockerfile              # Multi-stage build with integrated startup
├── apps/                   # Launchable web applications
│   ├── todo/              # Example app with evaluation APIs
│   └── 2048/              # 2048 game app
├── src/hud_controller/     # MCP server implementation
│   ├── server.py          # FastMCP server + resource definitions
│   ├── services.py        # Service management
│   ├── context.py         # Environment context
│   ├── context_server.py  # Persistent context server
│   ├── persistent_context.py # State persistence wrapper
│   ├── evaluators/        # Evaluation system
│   ├── setup/            # Setup system
│   └── problems/         # Problem definitions
└── README.md             # This file
```

## Development Workflow

### Hot-Reload Development with `hud dev`

For rapid iteration without Docker rebuilds:

```bash
# Navigate to the environment directory
cd environments/browser

# Start hot-reload development proxy
hud dev . --build

# This will:
# - Build/use hud-browser:dev image
# - Mount ./src for instant code updates
# - Run with reloaderoo for auto-restart
# - Provide HTTP endpoint for Cursor
```

Add the URL from output to Cursor settings or click the deeplink. Now you can edit code in `src/` and changes apply instantly!

#### How Hot-Reloading Works

This environment uses a persistent context server pattern:

1. **Context Server**: A separate Python process maintains state (services, browser, apps)
2. **Socket Communication**: MCP server connects via Unix socket `/tmp/hud_browser_ctx.sock`
3. **State Preservation**: X11, VNC, browser sessions, and launched apps persist across reloads
4. **Automatic Recovery**: On reload, the server reconnects to existing services

This means you can:
- Edit code and have changes apply immediately
- Keep browser sessions and apps running
- Maintain VNC connections
- Preserve test state between iterations

### Traditional Development Steps

1. **Start with apps** - Build your web applications independently
2. **Add evaluation APIs** - Extend app backends with `/api/eval/*` endpoints
3. **Create evaluators** - Build `@evaluator` classes that consume app APIs
4. **Build setup tools** - Create `@setup` classes for environment preparation
5. **Define problems** - Combine setup + evaluation using inheritance
6. **Test integration** - Use MCP tools to verify evaluation flow
7. **Containerize** - Package in Docker with proper service orchestration

## Testing & Debugging

### Local Testing
```bash
# Test app evaluation APIs directly
curl http://localhost:5000/api/eval/health
curl http://localhost:5000/api/eval/stats

# Test MCP evaluation flow
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"setup","arguments":{"config":{"name":"todo_basic_usage"}}}}' | docker run -i --rm hud-browser
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"evaluate","arguments":{"config":{"name":"todo_basic_usage"}}}}' | docker run -i --rm hud-browser
```

### Debug Logging
```bash
# Monitor all logs (stderr)
docker run -i --rm hud-browser 2>debug.log

# Monitor specific services
docker run -i --rm hud-browser 2>&1 | grep -E "(X11|VNC|MCP)"
```

### VNC Access
```bash
# Launch with VNC access for GUI debugging
docker run -d --rm -p 8080:8080 --name browser-debug hud-browser
# Open http://localhost:8080/vnc.html
```

## Using MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is an interactive developer tool for testing and debugging MCP servers. You can use it to test the browser environment locally.

### Installation
The Inspector runs directly through `npx` without requiring installation:

```bash
# Make sure you have Node.js installed first
npx @modelcontextprotocol/inspector --help
```

### Testing with MCP Inspector

#### Option 1: Running with Docker (Recommended)
```bash
# From the browser directory
npx @modelcontextprotocol/inspector docker run --rm -i -p 8080:8080 hud-browser
```

#### Option 2: Running Python module directly
```bash
# First install the package locally
cd environments/browser
pip install -e .

# Then run with the Inspector
npx @modelcontextprotocol/inspector python -m hud_controller
```

### Using the Inspector

Once connected, the Inspector provides several interactive features:

1. **Resources Tab**: View available resources like evaluators, setup tools, and problems
   - Explore `/evaluators`, `/setup`, `/problems` resources
   - Check their metadata and configurations

2. **Tools Tab**: Test the available tools
   - **setup**: Configure and initialize problems
     ```json
     {
       "config": {
         "name": "todo_basic_usage"
       }
     }
     ```
   - **evaluate**: Run evaluations
     ```json
     {
       "config": {
         "name": "todo_basic_usage"
       }
     }
     ```
   - **computer**: Perform browser automation actions
     ```json
     {
       "action": "screenshot"
     }
     ```

3. **Notifications Pane**: Monitor logs and server notifications
   - View initialization progress
   - See debug messages and errors
   - Track tool execution results

### Development Workflow with Inspector

1. **Start Development**
   - Launch Inspector with your server
   - Verify tools are properly registered
   - Check that resources are available

2. **Test Setup and Evaluation**
   - Use the setup tool to initialize a problem
   - Take screenshots to verify the browser state
   - Run evaluations to test your evaluation logic
   - Monitor logs for any issues

3. **Test Browser Automation**
   - Use the computer tool for actions like:
     - `screenshot` - Capture current state
     - `left_click` - Click at coordinates
     - `type` - Enter text
     - `key` - Press keyboard keys
   - Verify actions work as expected

4. **Debug Issues**
   - Check the Notifications pane for errors
   - Verify services are running (X11, VNC)
   - Ensure apps are launched properly
   - Test evaluation API endpoints directly

### Example Testing Session

```bash
# 1. Start the Inspector with the browser environment
npx @modelcontextprotocol/inspector docker run --rm -i -p 8080:8080 hud-browser

# 2. In the Inspector UI:
# - Go to Tools tab
# - Test setup tool with: {"config": {"name": "todo_basic_usage"}}
# - Test computer tool with: {"action": "screenshot"}
# - Test evaluate tool with: {"config": {"name": "todo_basic_usage"}}

# 3. Monitor the Notifications pane for progress and results
```

The Inspector is particularly useful for:
- Verifying your MCP server implementation
- Testing tool schemas and responses
- Debugging evaluation logic
- Understanding the server's resource structure
- Monitoring real-time logs and notifications

## Extending to New Environments

When creating new MCP environments:

1. **Copy this structure** as a template
2. **Replace apps/** with your domain-specific applications
3. **Implement your evaluators** following the `@evaluator` pattern
4. **Create domain setup tools** with the `@setup` pattern
5. **Define problems** using class inheritance for reusability
6. **Update service dependencies** in `services.py` as needed
7. **Extend Dockerfile** with your environment's requirements

For hot-reloadability:
- Keep complex objects out of the persistent context
- Only store simple, picklable state
- Recreate tools and clients on each server start

See `src/hud_controller/README.md` for detailed implementation guidance. 