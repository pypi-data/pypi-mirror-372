# ambivo_agents/agents/web_scraper.py
"""
Web Scraper Agent with proxy, Docker, and local execution modes.
Updated with LLM-aware intent detection and conversation history integration.
"""

import asyncio
import json
import logging
import random
import re
import ssl
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional
from urllib.parse import urljoin, urlparse

import urllib3
from requests.adapters import HTTPAdapter

from ..config.loader import get_config_section, load_config
from ..core.docker_shared import DockerSharedManager, get_shared_manager
from ..core.base import (
    AgentMessage,
    AgentRole,
    AgentTool,
    BaseAgent,
    ExecutionContext,
    MessageType,
    StreamChunk,
    StreamSubType,
)
from ..core.history import ContextType, WebAgentHistoryMixin

# Conditional imports for different execution modes
try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import docker

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


@dataclass
class ScrapingTask:
    """Simple scraping task data structure"""

    url: str
    method: str = "playwright"
    extract_links: bool = True
    extract_images: bool = True
    take_screenshot: bool = False
    timeout: int = 45


class SimpleDockerExecutor:
    """Simple Docker executor for scraping tasks"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.docker_image = self.config.get("docker_image", "sgosain/amb-ubuntu-python-public-pod")
        self.timeout = self.config.get("timeout", 60)

        # Initialize Docker shared manager
        self.shared_manager = get_shared_manager()
        self.shared_manager.setup_directories()

        # Get agent-specific subdirectory names from config
        self.output_subdir = self.config.get("output_subdir", "scraper")
        self.temp_subdir = self.config.get("temp_subdir", "scraper")
        self.handoff_subdir = self.config.get("handoff_subdir", "scraper")

        # Set up proper directories using DockerSharedManager
        self.output_dir = self.shared_manager.get_host_path(self.output_subdir, "output")
        self.temp_dir = self.shared_manager.get_host_path(self.temp_subdir, "temp")
        self.handoff_dir = self.shared_manager.get_host_path(self.handoff_subdir, "handoff")

        # Ensure all directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.handoff_dir.mkdir(parents=True, exist_ok=True)

        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
                self.docker_client.ping()
                self.available = True
            except Exception as e:
                logging.warning(f"Docker initialization failed: {e}")
                self.available = False
        else:
            self.available = False

    def execute_scraping_task(self, task: ScrapingTask) -> Dict[str, Any]:
        """Execute a scraping task in Docker"""
        if not self.available:
            return {"success": False, "error": "Docker not available", "url": task.url}

        try:
            # Create scraping script for Docker
            script_content = f"""
import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_url():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            response = await page.goto('{task.url}', timeout={task.timeout * 1000})
            title = await page.title()
            content = await page.inner_text('body')

            # Extract links if requested
            links = []
            if {task.extract_links}:
                link_elements = await page.query_selector_all('a[href]')
                for link in link_elements[:50]:  # Limit to 50 links
                    href = await link.get_attribute('href')
                    text = await link.inner_text()
                    if href and text:
                        links.append({{'url': href, 'text': text[:100]}})

            # Extract images if requested
            images = []
            if {task.extract_images}:
                img_elements = await page.query_selector_all('img[src]')
                for img in img_elements[:25]:  # Limit to 25 images
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt') or ''
                    if src:
                        images.append({{'url': src, 'alt': alt}})

            result = {{
                'success': True,
                'url': '{task.url}',
                'title': title,
                'content': content,  # Full content preserved
                'content_length': len(content),
                'links': links,
                'images': images,
                'status_code': response.status if response else None,
                'method': 'docker_playwright',
                'execution_mode': 'docker'
            }}

            print(json.dumps(result))

        except Exception as e:
            error_result = {{
                'success': False,
                'error': str(e),
                'url': '{task.url}',
                'execution_mode': 'docker'
            }}
            print(json.dumps(error_result))

        finally:
            await browser.close()

asyncio.run(scrape_url())
"""

            # Execute in Docker container
            container = self.docker_client.containers.run(
                image=self.docker_image,
                command=["python", "-c", script_content],
                remove=True,
                mem_limit="512m",
                network_disabled=False,  # Need network for scraping
                stdout=True,
                stderr=True,
                timeout=self.timeout,
            )

            # Parse result
            output = container.decode("utf-8") if isinstance(container, bytes) else str(container)
            result = json.loads(output.strip().split("\n")[-1])

            # Save result to shared output directory
            if result.get("success"):
                self._save_scraping_result(task, result)

            return result

        except Exception as e:
            return {"success": False, "error": str(e), "url": task.url, "execution_mode": "docker"}

    def _save_scraping_result(self, task: ScrapingTask, result: Dict[str, Any]) -> None:
        """Save scraping result to shared output directory"""
        try:
            import hashlib
            import time

            # Create filename based on URL and timestamp
            url_hash = hashlib.md5(task.url.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            filename = f"scraping_result_{url_hash}_{timestamp}.json"

            # Save to shared output directory
            output_file = self.output_dir / filename
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            # Also save to handoff directory for analytics workflow
            handoff_file = self.handoff_dir / filename
            with open(handoff_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            result["saved_files"] = {"output": str(output_file), "handoff": str(handoff_file)}

        except Exception as e:
            logging.warning(f"Failed to save scraping result: {e}")


class WebScraperAgent(BaseAgent, WebAgentHistoryMixin):
    """Unified web scraper agent with proxy, Docker, and local execution modes"""

    def __init__(
        self,
        agent_id: str = None,
        memory_manager=None,
        llm_service=None,
        system_message: str = None,
        **kwargs,
    ):

        if agent_id is None:
            agent_id = f"scraper_{str(uuid.uuid4())[:8]}"

        default_system = """You are a specialized web scraping agent with the following capabilities:
            - Extract content, links, and images from websites using multiple execution modes
            - Support proxy, Docker, and local execution methods for robust scraping
            - Remember URLs and scraping operations from previous conversations
            - Understand context references like "that website" or "scrape it again"
            - Handle batch scraping operations and accessibility checks
            - Provide detailed scraping results with technical information"""

        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESEARCHER,
            memory_manager=memory_manager,
            llm_service=llm_service,
            name="Web Scraper Agent",
            description="Unified web scraper with proxy, Docker, and local execution modes",
            system_message=system_message or default_system,
            **kwargs,
        )

        # Initialize history mixin
        self.setup_history_mixin()

        self.logger = logging.getLogger(f"WebScraperAgent-{agent_id}")

        # Load configuration from YAML
        try:
            config = load_config()
            self.scraper_config = get_config_section("web_scraping", config)
        except Exception as e:
            raise ValueError(f"web_scraping configuration not found in agent_config.yaml: {e}")

        # Initialize execution mode based on config
        self.execution_mode = self._determine_execution_mode()

        # Initialize executors based on availability and config
        self.docker_executor = None
        self.proxy_config = None

        # Initialize Docker executor if configured
        if self.execution_mode in ["docker", "auto"]:
            try:
                docker_config = {
                    **self.scraper_config,
                    "docker_image": self.scraper_config.get("docker_image"),
                    "timeout": self.scraper_config.get("timeout", 60),
                }
                self.docker_executor = SimpleDockerExecutor(docker_config)
            except Exception as e:
                self.logger.warning(f"Docker executor initialization failed: {e}")

        # Initialize proxy configuration if enabled
        if self.scraper_config.get("proxy_enabled", False):
            proxy_url = self.scraper_config.get("proxy_config", {}).get("http_proxy")
            if proxy_url:
                self.proxy_config = self._parse_proxy_url(proxy_url)
                self._configure_ssl_for_proxy()

        # Add tools
        self._add_scraping_tools()

        self.logger.info(f"WebScraperAgent initialized (Mode: {self.execution_mode})")

    async def _llm_analyze_scraping_intent(
        self, user_message: str, conversation_context: str = ""
    ) -> Dict[str, Any]:
        """Use LLM to analyze web scraping intent"""
        if not self.llm_service:
            return self._keyword_based_scraping_analysis(user_message)

        prompt = f"""
        Analyze this user message in the context of web scraping and extract:
        1. Primary intent (scrape_single, scrape_batch, check_accessibility, help_request)
        2. URLs to scrape
        3. Extraction preferences (links, images, content)
        4. Context references (referring to previous scraping operations)
        5. Technical specifications (method, timeout, etc.)

        Conversation Context:
        {conversation_context}

        Current User Message: {user_message}

        Respond in JSON format:
        {{
            "primary_intent": "scrape_single|scrape_batch|check_accessibility|help_request",
            "urls": ["http://example.com"],
            "extraction_preferences": {{
                "extract_links": true,
                "extract_images": true,
                "take_screenshot": false
            }},
            "uses_context_reference": true/false,
            "context_type": "previous_url|previous_operation",
            "technical_specs": {{
                "method": "playwright|requests|auto",
                "timeout": 60
            }},
            "confidence": 0.0-1.0
        }}
        """

        try:
            response = await self.llm_service.generate_response(prompt)
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._extract_scraping_intent_from_llm_response(response, user_message)
        except Exception as e:
            return self._keyword_based_scraping_analysis(user_message)

    def _keyword_based_scraping_analysis(self, user_message: str) -> Dict[str, Any]:
        """Fallback keyword-based scraping intent analysis"""
        content_lower = user_message.lower()

        # Determine intent
        if any(word in content_lower for word in ["batch", "multiple", "several"]):
            intent = "scrape_batch"
        elif any(word in content_lower for word in ["check", "test", "accessible"]):
            intent = "check_accessibility"
        elif any(word in content_lower for word in ["scrape", "extract", "crawl"]):
            intent = "scrape_single"
        else:
            intent = "help_request"

        # Extract URLs
        urls = self.extract_context_from_text(user_message, ContextType.URL)

        return {
            "primary_intent": intent,
            "urls": urls,
            "extraction_preferences": {
                "extract_links": True,
                "extract_images": True,
                "take_screenshot": False,
            },
            "uses_context_reference": any(word in content_lower for word in ["this", "that", "it"]),
            "context_type": "previous_url",
            "technical_specs": {"method": "auto", "timeout": 60},
            "confidence": 0.7,
        }

    async def process_message(
        self, message: AgentMessage, context: ExecutionContext = None
    ) -> AgentMessage:
        """Process message with LLM-based scraping intent detection - FIXED: Context preserved across provider switches"""
        self.memory.store_message(message)

        try:
            user_message = message.content

            # Update conversation state
            self.update_conversation_state(user_message)

            llm_context_from_routing = message.metadata.get("llm_context", {})
            conversation_history_from_routing = llm_context_from_routing.get(
                "conversation_history", []
            )

            if conversation_history_from_routing:
                conversation_history = conversation_history_from_routing
            else:
                conversation_history = await self.get_conversation_history(
                    limit=5, include_metadata=True
                )

            #  Get conversation context AND conversation history
            conversation_context = self._get_scraping_conversation_context_summary()

            # Build LLM context with conversation history
            llm_context = {
                "conversation_history": conversation_history,
                "conversation_id": message.conversation_id,
                "user_id": message.sender_id,
                "agent_type": "web_scraper",
            }

            # Use LLM to analyze intent WITH CONTEXT
            intent_analysis = await self._llm_analyze_scraping_intent_with_context(
                user_message, conversation_context, llm_context
            )

            # Extract kwargs from message metadata (passed from chat interface)
            chat_kwargs = {
                k: v
                for k, v in message.metadata.items()
                if k not in ["chat_interface", "simplified_call"]
            }

            # Route request based on LLM analysis with context
            response_content = await self._route_scraping_with_llm_analysis_with_context(
                intent_analysis, user_message, context, llm_context, chat_kwargs
            )

            response = self.create_response(
                content=response_content,
                recipient_id=message.sender_id,
                session_id=message.session_id,
                conversation_id=message.conversation_id,
            )

            self.memory.store_message(response)
            return response

        except Exception as e:
            error_response = self.create_response(
                content=f"Web Scraper Agent error: {str(e)}",
                recipient_id=message.sender_id,
                message_type=MessageType.ERROR,
                session_id=message.session_id,
                conversation_id=message.conversation_id,
            )
            return error_response

    async def _llm_analyze_scraping_intent_with_context(
        self, user_message: str, conversation_context: str = "", llm_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Use LLM to analyze web scraping intent - FIXED: With conversation context"""
        if not self.llm_service:
            return self._keyword_based_scraping_analysis(user_message)

        prompt = f"""
        Analyze this user message in the context of web scraping and extract:
        1. Primary intent (scrape_single, scrape_batch, check_accessibility, help_request)
        2. URLs to scrape
        3. Extraction preferences (links, images, content)
        4. Context references (referring to previous scraping operations)
        5. Technical specifications (method, timeout, etc.)

        Conversation Context:
        {conversation_context}

        Current User Message: {user_message}

        Respond in JSON format:
        {{
            "primary_intent": "scrape_single|scrape_batch|check_accessibility|help_request",
            "urls": ["http://example.com"],
            "extraction_preferences": {{
                "extract_links": true,
                "extract_images": true,
                "take_screenshot": false
            }},
            "uses_context_reference": true/false,
            "context_type": "previous_url|previous_operation",
            "technical_specs": {{
                "method": "playwright|requests|auto",
                "timeout": 60
            }},
            "confidence": 0.0-1.0
        }}
        """

        try:
            enhanced_system_message = self.get_system_message_for_llm(llm_context)
            response = await self.llm_service.generate_response(
                prompt=prompt, context=llm_context, system_message=enhanced_system_message
            )

            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._extract_scraping_intent_from_llm_response(response, user_message)
        except Exception as e:
            logging.warning(f"LLM scraping intent analysis failed: {e}")
            return self._keyword_based_scraping_analysis(user_message)

    async def _route_scraping_with_llm_analysis_with_context(
        self,
        intent_analysis: Dict[str, Any],
        user_message: str,
        context: ExecutionContext,
        llm_context: Dict[str, Any],
        chat_kwargs: Dict[str, Any] = None,
    ) -> str:
        """Route scraping request based on LLM intent analysis - FIXED: With context preservation"""

        primary_intent = intent_analysis.get("primary_intent", "help_request")
        urls = intent_analysis.get("urls", [])
        extraction_prefs = intent_analysis.get("extraction_preferences", {})
        uses_context = intent_analysis.get("uses_context_reference", False)

        # Resolve context references if needed
        if uses_context and not urls:
            recent_url = self.get_recent_url()
            if recent_url:
                urls = [recent_url]

        # Route based on intent
        chat_kwargs = chat_kwargs or {}

        if primary_intent == "help_request":
            return await self._handle_scraping_help_request_with_context(user_message, llm_context)
        elif primary_intent == "scrape_single":
            return await self._handle_single_scrape(
                urls, extraction_prefs, user_message, **chat_kwargs
            )
        elif primary_intent == "scrape_batch":
            return await self._handle_batch_scrape(
                urls, extraction_prefs, user_message, **chat_kwargs
            )
        elif primary_intent == "check_accessibility":
            return await self._handle_accessibility_check(urls, user_message)
        else:
            return await self._handle_scraping_help_request_with_context(user_message, llm_context)

    async def _handle_scraping_help_request_with_context(
        self, user_message: str, llm_context: Dict[str, Any]
    ) -> str:
        """Handle scraping help requests with conversation context - FIXED: Context preserved"""

        # Use LLM for more intelligent help if available
        if self.llm_service and llm_context.get("conversation_history"):
            enhanced_system_message = self.get_system_message_for_llm(llm_context)
            help_prompt = f"""As a web scraping assistant, provide helpful guidance for: {user_message}

    Consider the user's previous scraping operations and provide contextual assistance."""

            try:
                # Use LLM with conversation context
                intelligent_help = await self.llm_service.generate_response(
                    prompt=help_prompt, context=llm_context, system_message=enhanced_system_message
                )
                return intelligent_help
            except Exception as e:
                logging.warning(f"LLM help generation failed: {e}")

        # Fallback to standard help message
        state = self.get_conversation_state()

        response = (
            "I'm your Web Scraper Agent! I can help you with:\n\n"
            "🕷️ **Web Scraping**\n"
            "- Extract content from web pages\n"
            "- Scrape multiple URLs at once\n"
            "- Extract links and images\n"
            "- Take screenshots\n\n"
            "🔧 **Multiple Execution Modes**\n"
            "- Proxy support (ScraperAPI compatible)\n"
            "- Docker-based secure execution\n"
            "- Local fallback methods\n\n"
            "🧠 **Smart Context Features**\n"
            "- Remembers URLs from previous messages\n"
            "- Understands 'that website' and 'this page'\n"
            "- Maintains conversation state\n\n"
        )

        # Add current context information
        if state.current_resource:
            response += f"🎯 **Current URL:** {state.current_resource}\n"

        response += f"\n🔧 **Current Mode:** {self.execution_mode.upper()}\n"
        response += f"📡 **Proxy Enabled:** {'✅' if self.proxy_config else '❌'}\n"
        response += f"🐳 **Docker Available:** {'✅' if self.docker_executor and self.docker_executor.available else '❌'}\n"

        response += "\n💡 **Examples:**\n"
        response += "• 'scrape https://example.com'\n"
        response += "• 'batch scrape https://site1.com https://site2.com'\n"
        response += "• 'check if https://example.com is accessible'\n"
        response += "\nI understand context from our conversation! 🚀"

        return response

    def _get_scraping_conversation_context_summary(self) -> str:
        """Get scraping conversation context summary"""
        try:
            recent_history = self.get_conversation_history_with_context(
                limit=3, context_types=[ContextType.URL]
            )

            context_summary = []
            for msg in recent_history:
                if msg.get("message_type") == "user_input":
                    extracted_context = msg.get("extracted_context", {})
                    urls = extracted_context.get("url", [])

                    if urls:
                        context_summary.append(f"Previous URL: {urls[0]}")

            return "\n".join(context_summary) if context_summary else "No previous scraping context"
        except:
            return "No previous scraping context"

    async def _route_scraping_with_llm_analysis(
        self, intent_analysis: Dict[str, Any], user_message: str, context: ExecutionContext
    ) -> str:
        """Route scraping request based on LLM intent analysis"""

        primary_intent = intent_analysis.get("primary_intent", "help_request")
        urls = intent_analysis.get("urls", [])
        extraction_prefs = intent_analysis.get("extraction_preferences", {})
        uses_context = intent_analysis.get("uses_context_reference", False)

        # Resolve context references if needed
        if uses_context and not urls:
            recent_url = self.get_recent_url()
            if recent_url:
                urls = [recent_url]

        # Route based on intent
        if primary_intent == "help_request":
            return await self._handle_scraping_help_request(user_message)
        elif primary_intent == "scrape_single":
            return await self._handle_single_scrape(urls, extraction_prefs, user_message)
        elif primary_intent == "scrape_batch":
            return await self._handle_batch_scrape(urls, extraction_prefs, user_message)
        elif primary_intent == "check_accessibility":
            return await self._handle_accessibility_check(urls, user_message)
        else:
            return await self._handle_scraping_help_request(user_message)

    async def _handle_single_scrape(
        self, urls: List[str], extraction_prefs: Dict[str, Any], user_message: str, **kwargs
    ) -> str:
        """Handle single URL scraping"""
        if not urls:
            recent_url = self.get_recent_url()
            if recent_url:
                return f"I can scrape web pages. Did you mean to scrape **{recent_url}**? Please confirm."
            else:
                return (
                    "I can scrape web pages. Please provide a URL to scrape.\n\n"
                    "Example: 'scrape https://example.com'"
                )

        url = urls[0]

        try:
            result = await self._scrape_url(
                url=url,
                extract_links=extraction_prefs.get("extract_links", True),
                extract_images=extraction_prefs.get("extract_images", True),
                take_screenshot=extraction_prefs.get("take_screenshot", False),
                **kwargs,  # Pass through topic, external_handoff_dir, etc.
            )

            if result["success"]:
                return f"""✅ **Web Scraping Completed**

🌐 **URL:** {result['url']}
🔧 **Method:** {result.get('method', 'unknown')}
🏃 **Mode:** {result['execution_mode']}
📊 **Status:** {result.get('status_code', 'N/A')}
📄 **Content:** {result['content_length']:,} characters
⏱️ **Time:** {result['response_time']:.2f}s

**Title:** {result.get('title', 'No title')}

**Content Preview:**
{result.get('content', '')[:self.scraper_config.get('max_content_length', 75000)]}{'...' if len(result.get('content', '')) > self.scraper_config.get('max_content_length', 75000) else ''}

**Links Found:** {len(result.get('links', []))}
**Images Found:** {len(result.get('images', []))}"""
            else:
                return f"❌ **Scraping failed:** {result['error']}"

        except Exception as e:
            return f"❌ **Error during scraping:** {str(e)}"

    async def _handle_batch_scrape(
        self, urls: List[str], extraction_prefs: Dict[str, Any], user_message: str, **kwargs
    ) -> str:
        """Handle batch URL scraping"""
        if not urls:
            return (
                "I can scrape multiple web pages. Please provide URLs to scrape.\n\n"
                "Example: 'scrape https://example1.com and https://example2.com'"
            )

        try:
            result = await self._batch_scrape(urls=urls, method="auto", **kwargs)

            if result["success"]:
                successful = result["successful"]
                failed = result["failed"]
                total = result["total_urls"]

                response = f"""📦 **Batch Web Scraping Completed**

📊 **Summary:**
- **Total URLs:** {total}
- **Successful:** {successful}
- **Failed:** {failed}
- **Mode:** {result['execution_mode']}

"""

                if successful > 0:
                    response += "✅ **Successfully Scraped:**\n"
                    for i, scrape_result in enumerate(result["results"], 1):
                        if scrape_result.get("success", False):
                            response += f"{i}. {scrape_result.get('url', 'Unknown')}\n"

                if failed > 0:
                    response += f"\n❌ **Failed Scrapes:** {failed}\n"
                    for i, scrape_result in enumerate(result["results"], 1):
                        if not scrape_result.get("success", False):
                            response += f"{i}. {scrape_result.get('url', 'Unknown')}: {scrape_result.get('error', 'Unknown error')}\n"

                response += (
                    f"\n🎉 Batch scraping completed with {successful}/{total} successful scrapes!"
                )
                return response
            else:
                return f"❌ **Batch scraping failed:** {result['error']}"

        except Exception as e:
            return f"❌ **Error during batch scraping:** {str(e)}"

    async def _handle_accessibility_check(self, urls: List[str], user_message: str) -> str:
        """Handle accessibility check"""
        if not urls:
            recent_url = self.get_recent_url()
            if recent_url:
                return f"I can check if websites are accessible. Did you mean to check **{recent_url}**?"
            else:
                return "I can check if websites are accessible. Please provide a URL to check."

        url = urls[0]

        try:
            result = await self._check_accessibility(url)

            if result["success"]:
                status = "✅ Accessible" if result.get("accessible", False) else "❌ Not Accessible"
                return f"""🔍 **Accessibility Check Results**

🌐 **URL:** {result['url']}
🚦 **Status:** {status}
📊 **HTTP Status:** {result.get('status_code', 'Unknown')}
⏱️ **Response Time:** {result.get('response_time', 0):.2f}s
📅 **Checked:** {result.get('timestamp', 'Unknown')}

{'The website is accessible and responding normally.' if result.get('accessible', False) else 'The website is not accessible or not responding.'}"""
            else:
                return f"❌ **Accessibility check failed:** {result['error']}"

        except Exception as e:
            return f"❌ **Error during accessibility check:** {str(e)}"

    async def _handle_scraping_help_request(self, user_message: str) -> str:
        """Handle scraping help requests with conversation context"""
        state = self.get_conversation_state()

        response = (
            "I'm your Web Scraper Agent! I can help you with:\n\n"
            "🕷️ **Web Scraping**\n"
            "- Extract content from web pages\n"
            "- Scrape multiple URLs at once\n"
            "- Extract links and images\n"
            "- Take screenshots\n\n"
            "🔧 **Multiple Execution Modes**\n"
            "- Proxy support (ScraperAPI compatible)\n"
            "- Docker-based secure execution\n"
            "- Local fallback methods\n\n"
            "🧠 **Smart Context Features**\n"
            "- Remembers URLs from previous messages\n"
            "- Understands 'that website' and 'this page'\n"
            "- Maintains conversation state\n\n"
        )

        # Add current context information
        if state.current_resource:
            response += f"🎯 **Current URL:** {state.current_resource}\n"

        response += f"\n🔧 **Current Mode:** {self.execution_mode.upper()}\n"
        response += f"📡 **Proxy Enabled:** {'✅' if self.proxy_config else '❌'}\n"
        response += f"🐳 **Docker Available:** {'✅' if self.docker_executor and self.docker_executor.available else '❌'}\n"

        response += "\n💡 **Examples:**\n"
        response += "• 'scrape https://example.com'\n"
        response += "• 'batch scrape https://site1.com https://site2.com'\n"
        response += "• 'check if https://example.com is accessible'\n"
        response += "\nI understand context from our conversation! 🚀"

        return response

    def _extract_scraping_intent_from_llm_response(
        self, llm_response: str, user_message: str
    ) -> Dict[str, Any]:
        """Extract scraping intent from non-JSON LLM response"""
        content_lower = llm_response.lower()

        if "batch" in content_lower or "multiple" in content_lower:
            intent = "scrape_batch"
        elif "scrape" in content_lower:
            intent = "scrape_single"
        elif "check" in content_lower or "accessible" in content_lower:
            intent = "check_accessibility"
        else:
            intent = "help_request"

        return {
            "primary_intent": intent,
            "urls": [],
            "extraction_preferences": {"extract_links": True, "extract_images": True},
            "uses_context_reference": False,
            "context_type": "none",
            "technical_specs": {"method": "auto"},
            "confidence": 0.6,
        }

    def _configure_ssl_for_proxy(self):
        """Configure SSL settings for proxy usage - FIXED VERSION"""
        try:
            # Disable SSL warnings globally for urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # Create a custom SSL context that's more permissive
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # For requests library - create a custom adapter
            class SSLAdapter(HTTPAdapter):
                def init_poolmanager(self, *args, **kwargs):
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    kwargs["ssl_context"] = context
                    return super().init_poolmanager(*args, **kwargs)

            # Store the adapter for later use
            self.ssl_adapter = SSLAdapter()

            self.logger.info("SSL configuration updated for proxy usage")

        except Exception as e:
            self.logger.warning(f"SSL configuration warning: {e}")

    def _determine_execution_mode(self) -> str:
        """Determine execution mode from configuration"""
        # Check if proxy is enabled in config
        if self.scraper_config.get("proxy_enabled", False):
            proxy_url = self.scraper_config.get("proxy_config", {}).get("http_proxy")
            if proxy_url:
                return "proxy"

        # Check if Docker should be used
        if self.scraper_config.get("docker_image"):
            return "docker"

        # Fall back to local execution
        if PLAYWRIGHT_AVAILABLE or REQUESTS_AVAILABLE:
            return "local"

        raise RuntimeError("No scraping execution methods available")

    def _parse_proxy_url(self, proxy_url: str) -> Dict[str, Any]:
        """Parse proxy URL for different usage formats"""
        try:
            parsed = urlparse(proxy_url)
            return {
                "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}",
                "username": parsed.username,
                "password": parsed.password,
                "host": parsed.hostname,
                "port": parsed.port,
                "full_url": proxy_url,
            }
        except Exception as e:
            self.logger.error(f"Failed to parse proxy URL: {e}")
            return {}

    def _add_scraping_tools(self):
        """Add scraping tools"""
        self.add_tool(
            AgentTool(
                name="scrape_url",
                description="Scrape a single URL",
                function=self._scrape_url,
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape"},
                        "method": {
                            "type": "string",
                            "enum": ["auto", "playwright", "requests"],
                            "default": "auto",
                        },
                        "extract_links": {"type": "boolean", "default": True},
                        "extract_images": {"type": "boolean", "default": True},
                        "take_screenshot": {"type": "boolean", "default": False},
                    },
                    "required": ["url"],
                },
            )
        )

        self.add_tool(
            AgentTool(
                name="batch_scrape",
                description="Scrape multiple URLs",
                function=self._batch_scrape,
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "urls": {"type": "array", "items": {"type": "string"}},
                        "method": {"type": "string", "default": "auto"},
                    },
                    "required": ["urls"],
                },
            )
        )

        self.add_tool(
            AgentTool(
                name="check_accessibility",
                description="Quick check if URL is accessible",
                function=self._check_accessibility,
                parameters_schema={
                    "type": "object",
                    "properties": {"url": {"type": "string", "description": "URL to check"}},
                    "required": ["url"],
                },
            )
        )

    def _save_scraped_content_to_file(
        self,
        scraped_data: Dict[str, Any],
        topic: str = "web_scraping",
        external_handoff_dir: str = None,
    ) -> str:
        """Save scraped content to shared file for handoff"""
        import os
        from datetime import datetime

        # Use external handoff directory if provided (for topic isolation)
        if external_handoff_dir:
            handoff_dir = external_handoff_dir
            os.makedirs(handoff_dir, exist_ok=True)
        else:
            # Create handoff directory if it doesn't exist
            try:
                shared_manager = get_shared_manager()
                base_path = getattr(shared_manager, "base_path", None) or getattr(
                    shared_manager, "shared_path", "./docker_shared"
                )
            except:
                base_path = "./docker_shared"

            # Create session-based topic-specific subdirectory for content isolation
            # This ensures all scrapes for the same session/topic go to the same directory
            topic_clean = topic.replace(" ", "_").replace("-", "_")[:50]

            # Use session_id if available, otherwise create session-based identifier
            if hasattr(self, "session_id") and self.session_id:
                session_identifier = self.session_id[:8]  # First 8 chars of session ID
            elif hasattr(self, "user_id") and self.user_id:
                session_identifier = f"{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M')}"
            else:
                session_identifier = datetime.now().strftime("%Y%m%d_%H%M%S")

            topic_subdir = f"scraper_{topic_clean}_{session_identifier}"

            handoff_dir = os.path.join(base_path, "handoff", "scraper", topic_subdir)
            os.makedirs(handoff_dir, exist_ok=True)

        # Create filename with timestamp
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        url_hash = str(hash(scraped_data.get("url", "unknown")))[-6:]
        filename = f"scraped_{topic.replace(' ', '_')}_{url_hash}_{file_timestamp}.json"
        filepath = os.path.join(handoff_dir, filename)

        # Extract meaningful content for the file
        content_summary = {
            "url": scraped_data.get("url", "N/A"),
            "title": scraped_data.get("title", "N/A"),
            "success": scraped_data.get("success", False),
            "scraped_at": datetime.now().isoformat(),
            "topic": topic,
            "content_length": len(str(scraped_data.get("content", ""))),
            "raw_content": scraped_data.get("content", ""),
            "status_code": scraped_data.get("status_code", 0),
            "method": scraped_data.get("method", "unknown"),
            "links": scraped_data.get("links", [])[:10],  # First 10 links
            "images": scraped_data.get("images", [])[:5],  # First 5 images
        }

        # Save to JSON file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content_summary, f, indent=2, ensure_ascii=False)

        return filepath

    async def _scrape_url(self, url: str, method: str = "auto", **kwargs) -> Dict[str, Any]:
        """Unified URL scraping method with file saving"""
        try:
            # Perform the actual scraping
            if (
                self.execution_mode == "docker"
                and self.docker_executor
                and self.docker_executor.available
            ):
                result = await self._scrape_with_docker(url, method, **kwargs)
            elif self.execution_mode == "proxy" and self.proxy_config:
                result = await self._scrape_with_proxy(url, method, **kwargs)
            else:
                result = await self._scrape_locally(url, method, **kwargs)

            # Save successful scrapes to file for handoff
            if result.get("success") and result.get("content"):
                topic = kwargs.get("topic", "web_scraping")
                external_handoff_dir = kwargs.get("external_handoff_dir", None)
                try:
                    filepath = self._save_scraped_content_to_file(
                        result, topic, external_handoff_dir
                    )
                    result["saved_to_file"] = filepath
                    self.logger.info(f"Scraped content saved to: {filepath}")
                except Exception as save_error:
                    self.logger.warning(f"Failed to save scraped content: {save_error}")

            return result

        except Exception as e:
            self.logger.error(f"Scraping error for {url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "method": method,
                "execution_mode": self.execution_mode,
            }

    async def _scrape_with_docker(self, url: str, method: str, **kwargs) -> Dict[str, Any]:
        """Scrape using Docker executor"""
        task = ScrapingTask(
            url=url,
            method=method if method != "auto" else "playwright",
            extract_links=kwargs.get("extract_links", True),
            extract_images=kwargs.get("extract_images", True),
            take_screenshot=kwargs.get("take_screenshot", False),
            timeout=kwargs.get("timeout", self.scraper_config.get("timeout", 60)),
        )

        result = self.docker_executor.execute_scraping_task(task)
        result["execution_mode"] = "docker"
        return result

    async def _scrape_with_proxy(self, url: str, method: str, **kwargs) -> Dict[str, Any]:
        """Scrape using proxy (ScraperAPI style) with SSL verification disabled"""
        if method == "auto":
            method = "playwright" if PLAYWRIGHT_AVAILABLE else "requests"

        if method == "playwright" and PLAYWRIGHT_AVAILABLE:
            return await self._scrape_proxy_playwright(url, **kwargs)
        elif REQUESTS_AVAILABLE:
            return self._scrape_proxy_requests(url, **kwargs)
        else:
            raise RuntimeError("No proxy scraping methods available")

    async def _scrape_proxy_playwright(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape using Playwright with proxy and SSL verification disabled"""
        async with async_playwright() as p:
            browser = None
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    proxy={
                        "server": self.proxy_config["server"],
                        "username": self.proxy_config["username"],
                        "password": self.proxy_config["password"],
                    },
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                        "--ignore-certificate-errors",
                        "--ignore-ssl-errors",
                        "--ignore-certificate-errors-spki-list",
                        "--allow-running-insecure-content",
                    ],
                )

                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent=self.scraper_config.get("default_headers", {}).get(
                        "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    ),
                    ignore_https_errors=True,
                )

                page = await context.new_page()
                start_time = time.time()

                timeout_ms = self.scraper_config.get("timeout", 60) * 1000
                response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                await page.wait_for_timeout(3000)

                response_time = time.time() - start_time

                # Extract content
                title = await page.title()
                content = await page.inner_text("body")

                # Extract links
                links = []
                if kwargs.get("extract_links", True):
                    link_elements = await page.query_selector_all("a[href]")
                    max_links = self.scraper_config.get("max_links_per_page", 100)
                    for link in link_elements[:max_links]:
                        href = await link.get_attribute("href")
                        text = await link.inner_text()
                        if href and text:
                            links.append({"url": urljoin(url, href), "text": text.strip()[:100]})

                # Extract images
                images = []
                if kwargs.get("extract_images", True):
                    img_elements = await page.query_selector_all("img[src]")
                    max_images = self.scraper_config.get("max_images_per_page", 50)
                    for img in img_elements[:max_images]:
                        src = await img.get_attribute("src")
                        alt = await img.get_attribute("alt") or ""
                        if src:
                            images.append({"url": urljoin(url, src), "alt": alt})

                await browser.close()

                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "content": content,  # Full content preserved
                    "content_length": len(content),
                    "links": links,
                    "images": images,
                    "status_code": response.status if response else None,
                    "response_time": response_time,
                    "method": "proxy_playwright",
                    "execution_mode": "proxy",
                }

            except Exception as e:
                if browser:
                    await browser.close()
                raise e

    def _scrape_proxy_requests(self, url: str, **kwargs) -> Dict[str, Any]:
        """Scrape using requests with proxy and SSL verification disabled"""
        proxies = {"http": self.proxy_config["full_url"], "https": self.proxy_config["full_url"]}

        headers = self.scraper_config.get(
            "default_headers",
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )

        start_time = time.time()

        # Create session with custom SSL adapter
        session = requests.Session()

        # Only mount SSL adapter if it exists, otherwise use verify=False
        if hasattr(self, "ssl_adapter"):
            session.mount("https://", self.ssl_adapter)
            session.mount("http://", self.ssl_adapter)

        try:
            response = session.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=self.scraper_config.get("timeout", 60),
                verify=False,  # Disable SSL verification
                allow_redirects=True,
            )
            response.raise_for_status()  # Raise exception for bad status codes
            response_time = time.time() - start_time

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract content
            title = soup.find("title")
            title = title.get_text().strip() if title else "No title"

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            content = soup.get_text()
            content = " ".join(content.split())

            # Extract links and images based on config
            links = []
            images = []

            if kwargs.get("extract_links", True):
                max_links = self.scraper_config.get("max_links_per_page", 100)
                for link in soup.find_all("a", href=True)[:max_links]:
                    href = link["href"]
                    text = link.get_text().strip()[:100]
                    if href and text:  # Only add if both href and text exist
                        links.append({"url": urljoin(url, href), "text": text})

            if kwargs.get("extract_images", True):
                max_images = self.scraper_config.get("max_images_per_page", 50)
                for img in soup.find_all("img", src=True)[:max_images]:
                    src = img["src"]
                    alt = img.get("alt", "")
                    if src:  # Only add if src exists
                        images.append({"url": urljoin(url, src), "alt": alt})

            return {
                "success": True,
                "url": url,
                "title": title,
                "content": content,  # Full content preserved
                "content_length": len(content),
                "links": links,
                "images": images,
                "status_code": response.status_code,
                "response_time": response_time,
                "method": "proxy_requests",
                "execution_mode": "proxy",
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "url": url,
                "error": f"Request failed: {str(e)}",
                "method": "proxy_requests",
                "execution_mode": "proxy",
            }
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": f"Parsing failed: {str(e)}",
                "method": "proxy_requests",
                "execution_mode": "proxy",
            }
        finally:
            session.close()  # Always close the session

    async def _scrape_locally(self, url: str, method: str, **kwargs) -> Dict[str, Any]:
        """Scrape using local methods (no proxy, no Docker)"""
        if method == "auto":
            method = "playwright" if PLAYWRIGHT_AVAILABLE else "requests"

        if method == "playwright" and PLAYWRIGHT_AVAILABLE:
            return await self._scrape_local_playwright(url, **kwargs)
        elif REQUESTS_AVAILABLE:
            return self._scrape_local_requests(url, **kwargs)
        else:
            raise RuntimeError("No local scraping methods available")

    async def _scrape_local_playwright(self, url: str, **kwargs) -> Dict[str, Any]:
        """Local Playwright scraping"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self.scraper_config.get("default_headers", {}).get(
                    "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
            )
            page = await context.new_page()

            start_time = time.time()
            timeout_ms = self.scraper_config.get("timeout", 60) * 1000
            response = await page.goto(url, timeout=timeout_ms)
            response_time = time.time() - start_time

            title = await page.title()
            content = await page.inner_text("body")

            await browser.close()

            return {
                "success": True,
                "url": url,
                "title": title,
                "content": content,  # Full content preserved
                "content_length": len(content),
                "status_code": response.status if response else None,
                "response_time": response_time,
                "method": "local_playwright",
                "execution_mode": "local",
            }

    def _scrape_local_requests(self, url: str, **kwargs) -> Dict[str, Any]:
        """Local requests scraping"""
        headers = self.scraper_config.get(
            "default_headers",
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )

        start_time = time.time()
        response = requests.get(
            url, headers=headers, timeout=self.scraper_config.get("timeout", 60)
        )
        response_time = time.time() - start_time

        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find("title")
        title = title.get_text().strip() if title else "No title"

        for script in soup(["script", "style"]):
            script.decompose()

        content = soup.get_text()
        content = " ".join(content.split())

        return {
            "success": True,
            "url": url,
            "title": title,
            "content": content,  # Full content preserved
            "content_length": len(content),
            "status_code": response.status_code,
            "response_time": response_time,
            "method": "local_requests",
            "execution_mode": "local",
        }

    async def _batch_scrape(
        self, urls: List[str], method: str = "auto", **kwargs
    ) -> Dict[str, Any]:
        """Batch scraping with rate limiting from config"""
        results = []
        rate_limit = self.scraper_config.get("rate_limit_seconds", 1.0)

        for i, url in enumerate(urls):
            try:
                result = await self._scrape_url(url, method, **kwargs)
                results.append(result)

                if i < len(urls) - 1:
                    await asyncio.sleep(rate_limit)

            except Exception as e:
                results.append({"success": False, "url": url, "error": str(e)})

        successful = sum(1 for r in results if r.get("success", False))

        return {
            "success": True,
            "total_urls": len(urls),
            "successful": successful,
            "failed": len(urls) - successful,
            "results": results,
            "execution_mode": self.execution_mode,
        }

    async def _check_accessibility(self, url: str) -> Dict[str, Any]:
        """Check URL accessibility"""
        try:
            result = await self._scrape_url(url, extract_links=False, extract_images=False)
            return {
                "success": True,
                "url": url,
                "accessible": result.get("success", False),
                "status_code": result.get("status_code"),
                "response_time": result.get("response_time", 0),
                "error": result.get("error"),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)

    async def process_message_stream(
        self, message: AgentMessage, context: ExecutionContext = None
    ) -> AsyncIterator[StreamChunk]:
        """Stream web scraping operations - FIXED: Context preserved across provider switches"""
        self.memory.store_message(message)

        try:
            user_message = message.content
            self.update_conversation_state(user_message)

            yield StreamChunk(
                text="**Web Scraper Agent**\n\n",
                sub_type=StreamSubType.STATUS,
                metadata={"agent": "web_scraper", "phase": "initialization"},
            )

            # 🔥 FIX: Get conversation context for streaming
            conversation_context = self._get_scraping_conversation_context_summary()
            conversation_history = await self.get_conversation_history(
                limit=5, include_metadata=True
            )

            yield StreamChunk(
                text="Analyzing scraping request...\n",
                sub_type=StreamSubType.STATUS,
                metadata={"phase": "analysis"},
            )

            llm_context = {
                "conversation_history": conversation_history,  # 🔥 KEY FIX
                "conversation_id": message.conversation_id,
                "streaming": True,
            }

            intent_analysis = await self._llm_analyze_scraping_intent(
                user_message, conversation_context
            )

            primary_intent = intent_analysis.get("primary_intent", "help_request")
            urls = intent_analysis.get("urls", [])

            if primary_intent == "scrape_single":
                yield StreamChunk(
                    text="**Single URL Scraping**\n\n",
                    sub_type=StreamSubType.STATUS,
                    metadata={"intent": "scrape_single"},
                )
                async for chunk in self._stream_single_scrape_with_context(
                    urls, intent_analysis, user_message, llm_context
                ):
                    yield chunk

            elif primary_intent == "scrape_batch":
                yield StreamChunk(
                    text="**Batch URL Scraping**\n\n",
                    sub_type=StreamSubType.STATUS,
                    metadata={"intent": "scrape_batch"},
                )
                async for chunk in self._stream_batch_scrape_with_context(
                    urls, intent_analysis, user_message, llm_context
                ):
                    yield chunk

            elif primary_intent == "check_accessibility":
                yield StreamChunk(
                    text="**Accessibility Check**\n\n",
                    sub_type=StreamSubType.STATUS,
                    metadata={"intent": "check_accessibility"},
                )
                async for chunk in self._stream_accessibility_check_with_context(
                    urls, user_message, llm_context
                ):
                    yield chunk

            else:
                # Stream help response with context
                enhanced_system_message = self.get_system_message_for_llm(llm_context)
                if self.llm_service:
                    help_prompt = f"As a web scraping assistant, help with: {user_message}"

                    # 🔥 FIX: Stream with conversation context
                    async for chunk in self.llm_service.generate_response_stream(
                        help_prompt,
                        context=llm_context,
                        system_message=enhanced_system_message,
                    ):
                        yield StreamChunk(
                            text=chunk,
                            sub_type=StreamSubType.CONTENT,
                            metadata={"type": "help_response"},
                        )
                else:
                    response_content = await self._route_scraping_with_llm_analysis(
                        intent_analysis, user_message, context
                    )
                    yield StreamChunk(
                        text=response_content,
                        sub_type=StreamSubType.CONTENT,
                        metadata={"fallback_response": True},
                    )

        except Exception as e:
            yield StreamChunk(
                text=f"**Web Scraper Error:** {str(e)}",
                sub_type=StreamSubType.ERROR,
                metadata={"error": str(e)},
            )

    async def _stream_accessibility_check_with_context(
        self, urls: list, user_message: str, llm_context: Dict[str, Any]
    ) -> AsyncIterator[str]:
        """Stream accessibility checking with context preservation"""
        try:
            if not urls:
                yield "No URL provided. Please specify a website to check.\n"
                return

            url = urls[0]
            yield f"**Checking Accessibility:** {url}\n\n"

            yield "Testing connection...\n"

            result = await self._check_accessibility(url)

            if result["success"]:
                status = "✅ Accessible" if result.get("accessible", False) else "❌ Not Accessible"
                yield f"**Status:** {status}\n"
                yield f"**HTTP Status:** {result.get('status_code', 'Unknown')}\n"
                yield f"**Response Time:** {result.get('response_time', 0):.2f}s\n"
                yield f"**Checked:** {result.get('timestamp', 'Unknown')}\n\n"

                if result.get("accessible", False):
                    yield "✅ The website is accessible and responding normally.\n"
                else:
                    yield "❌ The website is not accessible or not responding.\n"

                # 🔥 FIX: Use LLM with context for intelligent follow-up suggestions
                if self.llm_service and llm_context.get("conversation_history"):
                    try:
                        enhanced_system_message = self.get_system_message_for_llm(llm_context)
                        follow_up_prompt = f"""Based on the accessibility check result for {url}, provide helpful next steps or troubleshooting suggestions."""

                        yield "\n💡 **Suggestions:**\n"
                        async for chunk in self.llm_service.generate_response_stream(
                            follow_up_prompt,
                            context=llm_context,
                            system_message=enhanced_system_message,
                        ):
                            yield chunk
                    except Exception:
                        pass
            else:
                yield f"❌ **Check failed:** {result['error']}\n"

        except Exception as e:
            yield f"❌ **Accessibility check error:** {str(e)}"

    async def _stream_single_scrape(
        self, urls: list, intent_analysis: dict, user_message: str
    ) -> AsyncIterator[str]:
        """Stream single URL scraping with detailed progress"""
        try:
            if not urls:
                yield "⚠️ No URL provided. Please specify a website to scrape.\n"
                return

            url = urls[0]
            extraction_prefs = intent_analysis.get("extraction_preferences", {})

            yield f"**Target URL:** {url}\n"
            yield f"**Method:** {self.execution_mode.upper()}\n"
            yield f"**Proxy:** {'✅ Enabled' if self.proxy_config else '❌ Disabled'}\n\n"

            yield "Initializing scraper...\n"
            await asyncio.sleep(0.2)

            yield "Connecting to website...\n"
            await asyncio.sleep(0.3)

            yield "Downloading content...\n"
            await asyncio.sleep(0.5)

            # Perform actual scraping
            result = await self._scrape_url(
                url=url,
                extract_links=extraction_prefs.get("extract_links", True),
                extract_images=extraction_prefs.get("extract_images", True),
                take_screenshot=extraction_prefs.get("take_screenshot", False),
            )

            if result["success"]:
                yield "**Scraping Completed Successfully!**\n\n"
                yield f"**Results Summary:**\n"
                yield f"• **URL:** {result['url']}\n"
                yield f"• **Title:** {result.get('title', 'No title')}\n"
                yield f"• **Content:** {result['content_length']:,} characters\n"
                yield f"• **Links:** {len(result.get('links', []))} found\n"
                yield f"• **Images:** {len(result.get('images', []))} found\n"
                yield f"• **Method:** {result.get('method', 'unknown')}\n"
                yield f"• **Time:** {result['response_time']:.2f}s\n\n"

                # Show content preview
                preview_length = self.scraper_config.get("max_content_length", 75000)
                content_preview = result.get("content", "")[:preview_length]
                if content_preview:
                    yield f"📄 **Content Preview:**\n{content_preview}{'...' if len(result.get('content', '')) > preview_length else ''}\n"

            else:
                yield f"❌ **Scraping failed:** {result['error']}\n"

        except Exception as e:
            yield f"❌ **Error during scraping:** {str(e)}"

    async def _stream_batch_scrape(
        self, urls: list, intent_analysis: dict, user_message: str
    ) -> AsyncIterator[str]:
        """Stream batch scraping with per-URL progress"""
        try:
            if not urls:
                yield "⚠️ No URLs provided. Please specify websites to scrape.\n"
                return

            yield f"📦 **Batch Scraping {len(urls)} URLs**\n\n"

            successful = 0
            failed = 0

            for i, url in enumerate(urls, 1):
                yield f"🌐 **URL {i}/{len(urls)}:** {url}\n"

                try:
                    yield f"⏳ Processing...\n"
                    result = await self._scrape_url(url, method="auto")

                    if result.get("success", False):
                        successful += 1
                        yield f"✅ Success - {result['content_length']:,} chars, {result['response_time']:.1f}s\n\n"
                    else:
                        failed += 1
                        yield f"❌ Failed - {result.get('error', 'Unknown error')}\n\n"

                except Exception as e:
                    failed += 1
                    yield f"❌ Error - {str(e)}\n\n"

                # Brief pause between URLs
                if i < len(urls):
                    await asyncio.sleep(0.5)

            yield f"📊 **Batch Complete:** {successful} successful, {failed} failed\n"

        except Exception as e:
            yield f"❌ **Batch scraping error:** {str(e)}"

    async def _stream_accessibility_check(
        self, urls: list, user_message: str
    ) -> AsyncIterator[str]:
        """Stream accessibility checking"""
        try:
            if not urls:
                yield "⚠️ No URL provided. Please specify a website to check.\n"
                return

            url = urls[0]
            yield f"🔍 **Checking Accessibility:** {url}\n\n"

            yield "⏳ Testing connection...\n"

            result = await self._check_accessibility(url)

            if result["success"]:
                status = "✅ Accessible" if result.get("accessible", False) else "❌ Not Accessible"
                yield f"🚦 **Status:** {status}\n"
                yield f"📊 **HTTP Status:** {result.get('status_code', 'Unknown')}\n"
                yield f"⏱️ **Response Time:** {result.get('response_time', 0):.2f}s\n"
                yield f"📅 **Checked:** {result.get('timestamp', 'Unknown')}\n\n"

                if result.get("accessible", False):
                    yield "✅ The website is accessible and responding normally.\n"
                else:
                    yield "❌ The website is not accessible or not responding.\n"
            else:
                yield f"❌ **Check failed:** {result['error']}\n"

        except Exception as e:
            yield f"❌ **Accessibility check error:** {str(e)}"
