"""
RendererAgent implementation as a specialized SubAgent.
Handles LLM-based rendering of envelopes to destination-specific formats.
"""

import json
import logging
from typing import Any, Dict, Optional

from broadie.core.agent import AgentConfig
from broadie.core.subagent import SubAgent
from broadie.core.renderers import RendererFactory

logger = logging.getLogger(__name__)


class RendererAgent(SubAgent):
    """
    Specialized SubAgent for rendering envelopes to destination-specific formats.
    Uses LLM to intelligently format structured data for different channels.
    """
    
    def build_config(self) -> AgentConfig:
        """Build default configuration for renderer agent."""
        return AgentConfig(
            name="renderer_agent",
            description="Specialized agent for rendering structured data to destination-specific formats",
            instruction="""You are a specialized rendering assistant. Your job is to convert structured data into the requested format.

When given an envelope containing agent output and a destination type, you must:
1. Analyze the payload structure and content
2. Format it appropriately for the destination type
3. Return ONLY the requested format with no additional text

For Slack destinations:
- Return valid Slack Block Kit JSON
- Use appropriate blocks (header, section, context, etc.)
- Include emojis and formatting for readability
- Handle different data types appropriately

For Email destinations:
- Return HTML content suitable for email
- Include proper structure and formatting
- Make content scannable and professional

For Markdown destinations:
- Return clean markdown format
- Use appropriate headers, code blocks, and formatting
- Optimize for web display

IMPORTANT: Return only the formatted content in the requested format. No explanations or additional text.""",
            model_provider="google",
            model_name="gemini-2.0-flash",
            temperature=0.1,  # Low temperature for consistent formatting
            tools=[]  # No tools needed for rendering
        )
    
    def __init__(self, parent_agent: Optional["Agent"] = None, **kwargs):
        """Initialize RendererAgent."""
        super().__init__(parent_agent=parent_agent, **kwargs)
        self.renderer_factory = RendererFactory()
    
    async def render_envelope(
        self, 
        envelope: Dict[str, Any], 
        destination_type: str
    ) -> Any:
        """
        Render envelope for specific destination type.
        
        Args:
            envelope: The universal envelope structure
            destination_type: Target destination type (slack, email, markdown, api)
            
        Returns:
            Rendered content in destination-specific format
        """
        try:
            # For API destinations, return envelope as-is
            if destination_type.lower() == "api":
                return envelope
            
            # Try specialized renderer first
            renderer = self.renderer_factory.create_renderer(destination_type)
            if renderer:
                logger.debug(f"Using specialized renderer for {destination_type}")
                return renderer.render(envelope)
            
            # Fall back to LLM-based rendering
            logger.debug(f"Using LLM rendering for {destination_type}")
            return await self._llm_render(envelope, destination_type)
            
        except Exception as e:
            logger.error(f"Rendering failed for {destination_type}: {e}")
            # Use generic fallback
            fallback_renderer = self.renderer_factory.create_fallback_renderer(destination_type)
            return fallback_renderer.render(envelope)
    
    async def _llm_render(self, envelope: Dict[str, Any], destination_type: str) -> Any:
        """Use LLM to render envelope for destination type."""
        # Create rendering prompt
        prompt = self._build_render_prompt(envelope, destination_type)
        
        # Get LLM response
        response = await self.process_message(prompt)
        
        # Try to parse response based on destination type
        if destination_type.lower() == "slack":
            return self._parse_slack_response(response)
        elif destination_type.lower() == "email":
            return self._parse_email_response(response)
        else:
            return response  # Return as markdown/text
    
    def _build_render_prompt(self, envelope: Dict[str, Any], destination_type: str) -> str:
        """Build prompt for LLM rendering."""
        envelope_json = json.dumps(envelope, indent=2)
        
        if destination_type.lower() == "slack":
            return f"""Convert this data to Slack Block Kit JSON:

{envelope_json}

Return only valid Slack Block Kit JSON with appropriate formatting, emojis, and structure. Make it visually appealing and informative."""
        
        elif destination_type.lower() == "email":
            return f"""Convert this data to HTML email content:

{envelope_json}

Return HTML that is well-formatted for email with proper structure, headers, and styling. Include both the content and appropriate subject line."""
        
        else:  # markdown
            return f"""Convert this data to clean Markdown:

{envelope_json}

Return well-formatted Markdown with appropriate headers, code blocks, and structure optimized for web display."""
    
    def _parse_slack_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response as Slack Block Kit JSON."""
        try:
            # Try to extract JSON from response
            if response.strip().startswith('{'):
                return json.loads(response.strip())
            else:
                # Look for JSON within the response
                start_idx = response.find('{')
                if start_idx != -1:
                    # Find matching closing bracket
                    bracket_count = 0
                    for i, char in enumerate(response[start_idx:], start_idx):
                        if char == '{':
                            bracket_count += 1
                        elif char == '}':
                            bracket_count -= 1
                            if bracket_count == 0:
                                json_str = response[start_idx:i+1]
                                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback to simple block format
        return {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{response}```"
                    }
                }
            ]
        }
    
    def _parse_email_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response as email content."""
        # Try to extract subject and HTML
        lines = response.split('\n')
        subject = "Agent Response"
        html_content = response
        
        # Look for subject line
        for line in lines:
            if line.lower().startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
                break
        
        # Clean up HTML content (remove subject line if found)
        if 'subject:' in response.lower():
            html_lines = [line for line in lines if not line.lower().startswith('subject:')]
            html_content = '\n'.join(html_lines).strip()
        
        return {
            "subject": subject,
            "html": html_content,
            "text": self._html_to_text(html_content)
        }
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text for email."""
        # Simple HTML to text conversion
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def test_rendering(self, destination_types: list = None) -> Dict[str, Any]:
        """Test rendering capabilities with sample data."""
        if destination_types is None:
            destination_types = ["slack", "email", "markdown", "api"]
        
        # Create test envelope
        test_envelope = {
            "agent": "test_agent",
            "timestamp": "2025-01-01T12:00:00Z",
            "schema": "test_schema",
            "payload": {
                "status": "success",
                "message": "This is a test message",
                "data": {
                    "key1": "value1",
                    "key2": [1, 2, 3],
                    "key3": {"nested": "data"}
                }
            },
            "metadata": {
                "should_send": True,
                "tier_label": "INFO"
            }
        }
        
        results = {}
        for dest_type in destination_types:
            try:
                rendered = await self.render_envelope(test_envelope, dest_type)
                results[dest_type] = {
                    "success": True,
                    "result": rendered
                }
            except Exception as e:
                results[dest_type] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results


def create_renderer_agent(parent_agent: Optional["Agent"] = None) -> RendererAgent:
    """
    Create a RendererAgent instance.
    
    Args:
        parent_agent: Parent agent that will use this renderer
        
    Returns:
        Configured RendererAgent
    """
    return RendererAgent(parent_agent=parent_agent)