"""
Persona MCP Server - Main server implementation.

Creates AI personas based on real online content using RAG.
Personas speak in first person and embody authentic characteristics.
"""

from pydantic import BaseModel, Field
from mcp.server.fastmcp import Context, FastMCP
from smithery.decorators import smithery

from .state_manager import PersonaStateManager
from .storage import PersonaStorage
from .search import SerperSearch
from .scraper import WebScraper
from .simple_search import SimpleSearch
from .llm import PersonaLLM


# Configuration schema for session-specific API keys
class ConfigSchema(BaseModel):
    """Configuration for the Persona MCP Server."""
    serper_api_key: str = Field(..., description="Serper API key for web search")
    anthropic_api_key: str = Field(..., description="Anthropic API key for Claude LLM")


# Initialize shared state (persona state manager and storage)
state_manager = PersonaStateManager()
storage = PersonaStorage()
simple_search = SimpleSearch()


@smithery.server(config_schema=ConfigSchema)
def create_server():
    """Create and configure the Persona MCP server."""

    server = FastMCP(
        "Persona MCP Server",
        instructions="""An MCP server that creates AI personas based on real online content.

Initialize a persona with init_persona, then ask questions with ask_persona.
The persona will respond in FIRST PERSON based on their actual public statements."""
    )

    @server.tool()
    async def init_persona(
        person_name: str,
        max_urls: int = 3,
        ctx: Context = None
    ) -> str:
        """
        Initialize a persona by gathering and storing their online content.

        Args:
            person_name: Full name of the person (e.g., "Alex Hormozi")
            max_urls: Maximum URLs to scrape (default: 3, recommended: 1-5)
        """
        try:
            # Get API keys from session config
            config = ctx.session_config
            serper_key = config.serper_api_key

            # Initialize services
            search = SerperSearch(api_key=serper_key)
            scraper = WebScraper()

            # Step 1: Search for content
            await ctx.info(f"🔍 Searching for content about {person_name}...")
            search_results = await search.search_person(person_name, max_results=max_urls * 2)

            if not search_results:
                return f"❌ No content found for {person_name}. Try a different name."

            # Extract URLs
            urls = [result["url"] for result in search_results[:max_urls]]
            await ctx.info(f"📄 Found {len(urls)} URLs to scrape")

            # Step 2: Scrape content
            await ctx.info(f"🕷️ Scraping content from {len(urls)} URLs...")
            scraped_data = await scraper.scrape_multiple(urls)

            # Step 3: Store content
            total_chars = 0
            successful_scrapes = 0

            for url, content in scraped_data.items():
                if content and len(content.strip()) > 100:  # Minimum content length
                    storage.save_content(person_name, url, content)
                    total_chars += len(content)
                    successful_scrapes += 1
                    await ctx.debug(f"✅ Saved {len(content)} chars from {url}")
                else:
                    await ctx.debug(f"⏭️ Skipped {url} (insufficient content)")

            if successful_scrapes == 0:
                return f"❌ Failed to scrape any content for {person_name}. URLs may be inaccessible."

            # Step 4: Set as current persona
            state_manager.set_persona(person_name)

            return f"✅ {person_name} ready! Scraped {successful_scrapes}/{len(urls)} URLs ({total_chars:,} chars)"

        except Exception as e:
            return f"❌ Error initializing persona: {str(e)}"

    @server.tool()
    async def ask_persona(
        question: str,
        ctx: Context = None
    ) -> str:
        """
        Ask a question to the currently active persona.

        Args:
            question: The question to ask
        """
        try:
            # Check if a persona is set
            current_persona = state_manager.get_persona()

            if not current_persona:
                return "❌ No persona is active. Please run init_persona first."

            # Check if persona exists in storage
            if not storage.persona_exists(current_persona):
                return f"❌ {current_persona} hasn't been initialized. Please run init_persona first."

            # Get API key from session config
            config = ctx.session_config
            anthropic_key = config.anthropic_api_key

            # Initialize LLM
            llm = PersonaLLM(api_key=anthropic_key)

            # Load persona content
            await ctx.info(f"📚 Loading content for {current_persona}...")
            content_chunks = storage.load_all_content(current_persona)

            if not content_chunks:
                return f"❌ No content found for {current_persona}."

            # Search for relevant chunks
            await ctx.info(f"🔍 Searching for relevant context...")
            relevant_chunks = simple_search.search(
                question=question,
                content_chunks=content_chunks,
                top_k=3,
                max_chars=4000
            )

            # Generate response
            await ctx.info(f"🤖 Generating response as {current_persona}...")
            response = await llm.generate_response(
                person_name=current_persona,
                question=question,
                context_chunks=relevant_chunks
            )

            return response

        except Exception as e:
            return f"❌ Error generating response: {str(e)}"

    @server.tool()
    def get_current_persona() -> str:
        """
        Get the name of the currently active persona.
        """
        current = state_manager.get_persona()

        if current:
            stats = storage.get_persona_stats(current)
            if stats.get("exists"):
                return f"✅ Current persona: {current}\n📊 {stats['num_documents']} documents, {stats['total_chars']:,} characters"
            else:
                return f"⚠️ Current persona: {current} (not initialized)"
        else:
            return "❌ No persona is currently active"

    @server.tool()
    def switch_persona(person_name: str) -> str:
        """
        Switch to a different persona that has already been initialized.

        Args:
            person_name: Name of the persona to switch to
        """
        # Check if persona exists
        if not storage.persona_exists(person_name):
            return f"❌ {person_name} hasn't been initialized yet. Use init_persona first."

        # Switch to the persona
        state_manager.set_persona(person_name)

        stats = storage.get_persona_stats(person_name)
        return f"✅ Switched to {person_name}\n📊 {stats['num_documents']} documents, {stats['total_chars']:,} characters"

    return server
