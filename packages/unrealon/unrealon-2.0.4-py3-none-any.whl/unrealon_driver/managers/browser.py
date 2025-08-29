"""
Clean browser manager using unrealon_browser.
"""

from typing import Optional
from pydantic import Field

from unrealon_browser import BrowserManager as CoreBrowserManager, BrowserConfig
from .base import BaseManager, ManagerConfig


class BrowserManagerConfig(ManagerConfig):
    """Browser manager configuration."""

    headless: bool = Field(default=True, description="Run headless")
    parser_name: str = Field(..., description="Parser name for browser")


class BrowserManager(BaseManager):
    """Clean browser manager wrapper."""

    def __init__(self, config: BrowserManagerConfig):
        super().__init__(config, "browser")
        self.config: BrowserManagerConfig = config
        self.browser: Optional[CoreBrowserManager] = None

    async def _initialize(self) -> bool:
        """Initialize browser manager (but not the actual browser yet)."""
        try:
            # Don't initialize the actual browser here - do it lazily on first use
            # This prevents browser from starting in daemon mode until needed
            self.logger.info("Browser manager ready (browser will start on first use)")
            return True

        except Exception as e:
            self.logger.error(f"Browser manager initialization failed: {e}")
            return False

    async def _shutdown(self):
        """Shutdown browser."""
        if self.browser:
            await self.browser.close_async()
            self.browser = None

    async def _ensure_browser_initialized(self) -> bool:
        """Ensure browser is initialized (lazy initialization)."""
        if self.browser is not None:
            return True
            
        try:
            self.logger.info("🚀 Starting browser (lazy initialization)...")
            
            # Create browser config
            browser_config = BrowserConfig(parser_name=self.config.parser_name)

            # Create browser manager
            self.browser = CoreBrowserManager(browser_config)

            # Initialize browser
            await self.browser.initialize_async()
            
            self.logger.info("✅ Browser started successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Browser initialization failed: {e}")
            self.browser = None
            return False

    async def navigate(self, url: str) -> bool:
        """Navigate to URL (with lazy browser initialization)."""
        # Ensure browser is initialized
        if not await self._ensure_browser_initialized():
            raise RuntimeError("Failed to initialize browser")

        try:
            await self.browser.navigate_async(url)
            self.stats.record_operation(True, 0.0)
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            self.stats.record_operation(False, 0.0)
            return False

    async def get_html(self) -> Optional[str]:
        """Get page HTML (with lazy browser initialization)."""
        # Ensure browser is initialized
        if not await self._ensure_browser_initialized():
            raise RuntimeError("Failed to initialize browser")

        try:
            html = await self.browser.get_page_content_async()
            self.stats.record_operation(True, 0.0)
            return html
        except Exception as e:
            self.logger.error(f"Get HTML failed: {e}")
            self.stats.record_operation(False, 0.0)
            return None
