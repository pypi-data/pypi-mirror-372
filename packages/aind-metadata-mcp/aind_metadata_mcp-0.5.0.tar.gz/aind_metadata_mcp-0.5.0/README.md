# AIND Metadata MCP Server

An MCP (Model Context Protocol) server that provides access to AIND (Allen Institute for Neural Dynamics) metadata and data assets through a comprehensive set of tools and resources.

## Features

This MCP server provides tools for:

- **Data Retrieval**: Query MongoDB collections with filters and projections
- **Aggregation**: Execute complex MongoDB aggregation pipelines
- **Schema Exploration**: Access detailed schema examples and documentation
- **NWB File Access**: Load and explore NWB (Neurodata Without Borders) files
- **Data Summaries**: Generate AI-powered summaries of data assets

## Installation

Install uv if you haven't already - following [this documentation](https://docs.astral.sh/uv/getting-started/installation/)

Install the MCP server using uv:

```bash
uv tool install aind-metadata-mcp
```

Or using pip:

```bash
pip install aind-metadata-mcp
```

## Configuration

### For Cline (VSCode Extension)


In order to ensure that the MCP server runs in your preferred client, you will have to download the `aind-metadata-mcp` package to your console. If space is an issue, please set `UV_CACHE_DIR` and `UV_TOOL_DIR` to locations that have capacity before proceeding with the next step.

1. Simpler version of install
   Run `uv tool install aind-metadata-mcp` on your terminal and proceed below to configuring your MCP clients. 
2. If the above step didn't work:

Create virtual environment with python 3.11 in IDE

```bash
# Instructions for Conda
conda create -n <my_env> python=3.11
conda activate <my_env>

# Instructions for virtual environment
py -3.11 -m venv .venv
# Windows startup
.venv\Scripts\Activate.ps1 
# Mac/ Linux startup
source .venv/bin/activate 
```

Run the following commands in your IDE terminal.

```bash
pip install uv
uvx aind-metadata-mcp
```

If all goes well, and you see the following notice - `Starting MCP server 'aind_data_access' with transport 'stdio'`-, you should be good for the set up in your client of choice!

## Instructions for use in MCP clients

JSON Config files to add MCP servers in clients should be structured like this

```bash
{
    "mcpServers": {

    }
}
```

Insert the following lines into the mcpServers dictionary

```bash

"aind_data_access": {
      "disabled": false,
      "timeout": 300,
      "type": "stdio",
      "command": "aind-metadata-mcp"
}
```

Note that after configuring the JSON files, it will take a few minutes for the serve to populate in the client.

### Claude Desktop App

- Click the three lines at the top left of the screen.
- File > Settings > Developer > Edit config

### Cline in VSCode

- Ensure that Cline is downloaded to VScode
- Click the three stacked rectangles at the top right of the Cline window
- Installed > Configure MCP Servers
- Close and reopen VSCode

### Github Copilot in VSCode

- Command palette (ctr shift p)
- Search for MCP: Add server
- Select `Manual Install` / `stdio`
- When prompted for a command, input `uvx aind-data-access`
- Name your server
- Close and reopen VSCode
- In Copilot chat -> Select agent mode -> Click the three stacked rectangles to configure tools
- In order to enable the agent to reply with context of the AIND API, you'll have to manually add the .txt files (under resources) in this repository

### For use in Code Ocean

* Locate the [following capsule](https://codeocean.allenneuraldynamics.org/capsule/7008682/tree), to spin up Cline and Co-pilot with the aind-metadata-mcp pre-installed.
* Refer the the [code ocean MCP server](https://github.com/codeocean/codeocean-mcp-server) for additional support
* Either pin version 4.2, or 4.4
