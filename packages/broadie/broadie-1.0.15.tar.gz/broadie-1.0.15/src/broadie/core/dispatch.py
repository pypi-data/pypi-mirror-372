"""
Post-processing dispatcher for schema-validated agent outputs.
Handles rendering and delivery to multiple destinations using existing infrastructure.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from broadie.core.destinations import DestinationResolver
from broadie.core.renderer_agent import RendererAgent
from broadie.core.renderers import RendererFactory

logger = logging.getLogger(__name__)


class EnvelopeDispatcher:
    """
    Dispatcher for processing validated envelopes and delivering to destinations.
    Integrates with existing DestinationResolver while adding rendering capabilities.
    """
    
    def __init__(
        self, 
        destination_resolver: DestinationResolver,
        renderer_agent: Optional[RendererAgent] = None
    ):
        """
        Initialize dispatcher.
        
        Args:
            destination_resolver: Existing destination resolver for delivery
            renderer_agent: Optional renderer agent for LLM-based rendering
        """
        self.destination_resolver = destination_resolver
        self.renderer_agent = renderer_agent
        self.renderer_factory = RendererFactory()
        
    async def dispatch(
        self, 
        envelope: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Dispatch envelope to all enabled destinations.
        
        Args:
            envelope: Validated envelope structure
            context: Additional context for delivery
            
        Returns:
            Dispatch results summary
        """
        # Get enabled destinations
        enabled_destinations = self._get_enabled_destinations()
        
        if not enabled_destinations:
            logger.warning("No enabled destinations found for dispatch")
            return {
                "success": False,
                "message": "No enabled destinations configured",
                "results": {}
            }
        
        # Process each destination
        dispatch_results = {}
        tasks = []
        
        for dest_name, dest_config in enabled_destinations.items():
            task = asyncio.create_task(
                self._dispatch_to_destination(envelope, dest_name, dest_config, context),
                name=f"dispatch_{dest_name}"
            )
            tasks.append((dest_name, task))
        
        # Wait for all dispatches to complete
        for dest_name, task in tasks:
            try:
                result = await task
                dispatch_results[dest_name] = result
            except Exception as e:
                logger.error(f"Dispatch failed for {dest_name}: {e}")
                dispatch_results[dest_name] = {
                    "success": False,
                    "error": str(e),
                    "destination_type": "unknown"
                }
        
        # Calculate summary
        successful_dispatches = sum(1 for result in dispatch_results.values() if result.get("success", False))
        total_dispatches = len(dispatch_results)
        
        return {
            "success": successful_dispatches > 0,
            "total_destinations": total_dispatches,
            "successful_dispatches": successful_dispatches,
            "failed_dispatches": total_dispatches - successful_dispatches,
            "results": dispatch_results,
            "envelope": envelope
        }
    
    async def _dispatch_to_destination(
        self, 
        envelope: Dict[str, Any], 
        dest_name: str, 
        dest_config: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dispatch envelope to a specific destination."""
        dest_type = dest_config.get("type", "api")
        
        try:
            # Render envelope for destination type
            rendered_content = await self._render_for_destination(envelope, dest_type)
            
            # Prepare delivery context
            delivery_context = context or {}
            delivery_context.update({
                "destination": dest_config,
                "envelope": envelope,
                "rendered": True
            })
            
            # Use existing DestinationResolver for delivery
            delivery_result = await self.destination_resolver.send(
                message=rendered_content,
                destination_type=dest_name,
                context=delivery_context
            )
            
            return {
                "success": delivery_result.success,
                "destination_name": dest_name,
                "destination_type": dest_type,
                "rendered_format": type(rendered_content).__name__,
                "delivery_time": getattr(delivery_result, 'delivery_time', 0.0),
                "attempts": getattr(delivery_result, 'attempts', 1),
                "error_message": getattr(delivery_result, 'error_message', None)
            }
            
        except Exception as e:
            logger.error(f"Failed to dispatch to {dest_name}: {e}")
            return {
                "success": False,
                "destination_name": dest_name,
                "destination_type": dest_type,
                "error": str(e),
                "rendered_format": "none"
            }
    
    async def _render_for_destination(self, envelope: Dict[str, Any], dest_type: str) -> Any:
        """Render envelope for specific destination type."""
        try:
            # Try RendererAgent first (LLM-based rendering)
            if self.renderer_agent:
                logger.debug(f"Using RendererAgent for {dest_type}")
                return await self.renderer_agent.render_envelope(envelope, dest_type)
            
            # Fall back to factory-based rendering
            renderer = self.renderer_factory.create_renderer(dest_type)
            if renderer:
                logger.debug(f"Using factory renderer for {dest_type}")
                return renderer.render(envelope)
            
            # Ultimate fallback to generic renderer
            logger.debug(f"Using generic renderer for {dest_type}")
            fallback_renderer = self.renderer_factory.create_fallback_renderer(dest_type)
            return fallback_renderer.render(envelope)
            
        except Exception as e:
            logger.error(f"Rendering failed for {dest_type}: {e}")
            # Last resort - return envelope as JSON string
            import json
            return json.dumps(envelope, indent=2)
    
    def _get_enabled_destinations(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled destinations from resolver."""
        enabled = {}
        
        for dest_name in self.destination_resolver.list_destinations():
            dest_config = self.destination_resolver.destinations.get_destination(dest_name)
            if dest_config and dest_config.enabled:
                enabled[dest_name] = {
                    "type": dest_config.type.value if hasattr(dest_config.type, 'value') else str(dest_config.type),
                    "target": dest_config.target,
                    "enabled": dest_config.enabled,
                    "settings": getattr(dest_config, 'settings', {})
                }
        
        return enabled
    
    async def test_dispatch(self, test_envelope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test dispatch functionality with sample envelope."""
        if test_envelope is None:
            test_envelope = {
                "agent": "test_dispatcher",
                "timestamp": "2025-01-01T12:00:00Z",
                "schema": "test_schema",
                "payload": {
                    "message": "This is a test dispatch",
                    "status": "success"
                },
                "metadata": {
                    "should_send": True,
                    "tier_label": "INFO"
                }
            }
        
        return await self.dispatch(test_envelope)


def create_envelope_dispatcher(
    destination_resolver: DestinationResolver,
    renderer_agent: Optional[RendererAgent] = None
) -> EnvelopeDispatcher:
    """
    Create an EnvelopeDispatcher instance.
    
    Args:
        destination_resolver: Existing destination resolver
        renderer_agent: Optional renderer agent for enhanced rendering
        
    Returns:
        Configured EnvelopeDispatcher
    """
    return EnvelopeDispatcher(destination_resolver, renderer_agent)


async def dispatch_envelope(
    envelope: Dict[str, Any],
    destinations: Dict[str, Any],
    destination_resolver: DestinationResolver,
    renderer_agent: Optional[RendererAgent] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function for dispatching envelopes.
    
    Args:
        envelope: Validated envelope to dispatch
        destinations: Destination configuration
        destination_resolver: Resolver for handling delivery
        renderer_agent: Optional renderer agent
        context: Additional context
        
    Returns:
        Dispatch results
    """
    dispatcher = EnvelopeDispatcher(destination_resolver, renderer_agent)
    return await dispatcher.dispatch(envelope, context)