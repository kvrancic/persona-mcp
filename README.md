# Persona MCP Server (Alpha)

> **⚠️ Alpha Version**: This is an early release. Advanced features like vector embeddings (ChromaDB) are planned for future updates.

An MCP (Model Context Protocol) server that creates AI personas based on real online content using Retrieval-Augmented Generation (RAG).

## What it Does

This server allows you to:
1. **Initialize a persona** - Automatically gathers and stores online content (articles, interviews, blog posts, etc.)
2. **Ask questions** - Get answers based on the persona's actual public statements
3. **Switch between personas** - Interact with different people

## Current Features (Alpha)

### ✅ Implemented
- **Web Search** - Finds relevant content using Serper API
- **Smart Web Scraping** - Extracts clean text with Crawl4AI (bypasses bot detection)
- **Keyword-based Search** - Fast content matching for question answering
- **Content Storage** - Persistent knowledge base across sessions
- **RAG with Claude** - Grounded responses using retrieved content

### 🔮 Planned (Future Updates)
- **Vector Embeddings (ChromaDB)** - Semantic search instead of keyword matching
- **Advanced Indexing** - Better content chunking and retrieval
- **Async Background Tasks** - Long-running operations with progress tracking

## Architecture

### Current System (Alpha)
1. **MCP Server Interface** - Routes commands (`init_persona`, `ask_persona`, etc.)
2. **Persona State Manager** - Tracks the currently active persona
3. **Data Pipeline** (`init_persona` tool):
   - Search: Uses Serper API to find content about the person
   - Scrape: Extracts clean text from web pages using Crawl4AI
   - Store: Saves content to disk in `./knowledge_base/{person_name}/`
4. **Query Engine** (`ask_persona` tool):
   - Searches content using keyword matching
   - Builds RAG prompt with relevant context
   - Generates response using Anthropic's Claude

## Prerequisites

- Python >=3.10
- `uv` package manager (https://docs.astral.sh/uv/)
- **Serper API key** (get from https://serper.dev/)
- **Anthropic API key** (get from https://console.anthropic.com/)

## Installation

All dependencies are configured in `pyproject.toml`:
- `anthropic` - For Claude LLM (model: claude-sonnet-4-5-20250929)
- `crawl4ai` - For intelligent web scraping with bot detection bypass
- `httpx` - For HTTP requests
- `mcp` and `smithery` - For MCP server framework

**Important**: Crawl4AI uses Playwright browser automation, which requires additional setup:
```bash
python -m playwright install chromium
```

Dependencies are installed automatically when you run the server.

## Running the Server

### Local Development

```bash
uv run dev
```

This starts the server on `http://127.0.0.1:8081` for local testing.

### Interactive Testing with Playground

```bash
uv run playground
```

This will:
1. Start your local server
2. Use ngrok to create a public tunnel
3. Open the Smithery Playground in your browser
4. Prompt you to enter your API keys:
   - **Serper API Key**: Your Serper API key
   - **Anthropic API Key**: Your Anthropic API key

## Available Tools

### 1. `init_persona`

Initialize a persona by gathering and storing their online content.

**Parameters:**
- `person_name` (string, required): Full name of the person (e.g., "Alex Hormozi")
- `max_urls` (integer, optional): Maximum URLs to scrape (default: 3, recommended: 1-5)

**Example:**
```
init_persona person_name="Alex Hormozi" max_urls=3
```

**Returns:**
Success message with statistics (e.g., "✅ Alex Hormozi ready! Scraped 3/3 URLs (45,230 chars)")

**What it does:**
1. Searches web for content using Serper API (~1-2s)
2. Scrapes pages concurrently using Crawl4AI (~2-5s per URL)
3. Stores content as text files in `knowledge_base/`
4. Sets the person as the current active persona

**Time**: ~5-15 seconds depending on `max_urls`. Runs synchronously and returns when complete.

### 2. `ask_persona`

Ask a question to the currently active persona.

**Parameters:**
- `question` (string, required): The question to ask

**Example:**
```
ask_persona question="What's your opinion on building a team?"
```

**What it does:**
1. Loads the persona's stored content
2. Uses keyword matching to find relevant chunks
3. Builds a RAG prompt with the best-matching content
4. Generates a response using Claude that's grounded in the persona's actual statements

**Note**: The keyword search extracts key terms, scores content by overlap, and prioritizes exact phrase matches.

### 3. `get_current_persona`

Get the name of the currently active persona.

**No parameters required.**

### 4. `switch_persona`

Switch to a different persona that has already been initialized.

**Parameters:**
- `person_name` (string, required): Name of the persona to switch to

**Example:**
```
switch_persona person_name="Elon Musk"
```

**Note:** The persona must have been initialized with `init_persona` first.

## Configuration

When connecting to the server (via playground or MCP client), you'll need to provide:

```json
{
  "serper_api_key": "your-serper-api-key-here",
  "anthropic_api_key": "your-anthropic-api-key-here"
}
```

These API keys are:
- **Session-scoped**: Different users can use different API keys
- **Never stored**: Keys are only kept in memory for the session
- **Accessed securely**: Keys are read from `ctx.session_config` in the server

## Testing the Server

### Example Workflow

1. Start the playground:
   ```bash
   uv run playground
   ```

2. Enter your API keys when prompted

3. **Initialize a persona** (completes in ~5-15 seconds):
   ```
   init_persona person_name="Alex Hormozi" max_urls=3
   ```
   Response: `✅ Alex Hormozi ready! Scraped 3/3 URLs (45,230 chars)`

4. **Ask questions** to the persona:
   ```
   ask_persona question="What are your thoughts on marketing?"
   ```

5. **Switch personas** (if you've initialized multiple):
   ```
   switch_persona person_name="Elon Musk"
   ```

## Project Structure

```
persona-mcp-server/
├── src/hello_server/
│   ├── server.py          # Main MCP server with tools
│   ├── state_manager.py   # Persona state tracking
│   ├── search.py          # Serper API integration
│   ├── scraper.py         # Web scraping with Crawl4AI
│   ├── storage.py         # File storage
│   ├── simple_search.py   # Keyword-based search (current)
│   └── llm.py             # Anthropic Claude integration
├── knowledge_base/        # Created automatically, stores persona data
├── pyproject.toml         # Dependencies and configuration
└── README.md              # This file
```

## Knowledge Base Storage

When you initialize a persona, content is stored in:

```
knowledge_base/
└── {person_name}/
    ├── content/          # Scraped text files
    │   └── {hash}.txt
    └── metadata.json     # URL and timestamp mapping
```

This data persists across server restarts, so you don't need to re-scrape when switching personas.

## Deployment

To deploy to Smithery:

1. Create a GitHub repository
2. Push your code:
   ```bash
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
3. Go to https://smithery.ai/new
4. Connect your GitHub repo
5. Click "Deploy"

Users connecting to your deployed server will provide their own API keys in the connection configuration.

## Troubleshooting

### No content found
- Check that the person's name is spelled correctly
- Verify your Serper API key is valid
- Try a more well-known person with more online content

### Failed to scrape content
- Some websites block scraping - this is normal
- The server will skip inaccessible URLs and continue
- Try increasing `max_urls` to scrape more sources

### LLM errors
- Verify your Anthropic API key is valid
- Check your API key has sufficient credits
- Ensure you're using model "claude-sonnet-4-5-20250929"

### Timeout issues
- Reduce `max_urls` to 1-3 for faster initialization
- Check your internet connection
- Some URLs may take longer to scrape (15s timeout per URL)

## API Keys Used

This server requires two API keys that you must provide:

1. **Serper API** (https://serper.dev/)
   - Used for: Web search to find content about personas
   - Free tier: 2,500 queries/month
   - API key format: Alphanumeric string

2. **Anthropic Claude API** (https://console.anthropic.com/)
   - Used for: Generating persona responses with RAG
   - Model: `claude-sonnet-4-5-20250929`
   - Pricing: Pay-per-token (see Anthropic pricing)

**IMPORTANT:** You MUST have these API keys before using the server. The server will not work without them.

## Version History

### Alpha (Current)
- Simple keyword-based search for content retrieval
- Synchronous persona initialization (5-15s)
- Basic web scraping with Crawl4AI
- RAG-based responses using Claude

### Planned for Beta
- ChromaDB vector embeddings for semantic search
- Async background tasks with progress tracking
- Advanced content chunking and retrieval
- Multi-source knowledge aggregation

## References

- **IDEA.md**: Complete architecture and data flow concepts (in parent directory)
- **deployment.md**: Smithery deployment guide (in parent directory)
- **python-mcp-sdk.md**: MCP Python SDK documentation (in parent directory)
- **mcp-documentation.md**: MCP protocol overview (in parent directory)

## License

MIT
