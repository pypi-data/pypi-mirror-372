"""FastAPI-based webhook server."""

import asyncio
import logging
from typing import Dict, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
import uvicorn

from .entities import (
    ProviderWebhookConfig,
    WebhookConfig,
    WebhookPayloadParser,
    WebhookProvider,
)
from .parsers.github_parser import GitHubWebhookParser
from .services import WebhookActionExecutorService, WebhookProcessingService


class WebhookServer:
    """FastAPI-based webhook server that supports multiple providers."""

    def __init__(
        self,
        config: WebhookConfig,
        processing_service: WebhookProcessingService,
        executor_service: WebhookActionExecutorService,
    ):
        self.config = config
        self.processing_service = processing_service
        self.executor_service = executor_service
        self.logger = logging.getLogger(__name__)

        # Initialize FastAPI app
        self.app = FastAPI(
            title="DooService Webhook Server",
            description="Multi-provider webhook server for repository event handling",
            version="1.0.0",
        )

        # Initialize payload parsers
        self.parsers: Dict[WebhookProvider, WebhookPayloadParser] = {
            WebhookProvider.GITHUB: GitHubWebhookParser(),
            # Additional parsers can be added here
            # WebhookProvider.GITLAB: GitLabWebhookParser(),
            # WebhookProvider.BITBUCKET: BitbucketWebhookParser(),
        }

        # Setup routes
        self._setup_routes()

        # Background task for executing actions
        self._action_executor_task = None

    def _setup_routes(self) -> None:
        """Setup FastAPI routes for webhook endpoints."""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "service": "webhook-server"}

        @self.app.get("/")
        async def root():
            """Root endpoint with server information."""
            return {
                "service": "DooService Webhook Server",
                "version": "1.0.0",
                "supported_providers": [p.value for p in self.parsers],
                "endpoints": [
                    f"/webhooks/{provider.value.lower()}" for provider in self.parsers
                ],
            }

        # Dynamic webhook endpoints for each provider
        for provider in self.parsers:
            endpoint_path = f"/webhooks/{provider.value.lower()}"
            self.app.post(endpoint_path)(self._create_webhook_handler(provider))

    def _create_webhook_handler(self, provider: WebhookProvider):
        """Create a webhook handler for a specific provider."""

        async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
            """Handle webhook requests for the provider."""
            try:
                # Get provider config
                provider_config = self._get_provider_config(provider)
                if not provider_config or not provider_config.enabled:
                    raise HTTPException(
                        status_code=404, detail=f"Provider {provider.value} not enabled"
                    )

                # Read request data
                headers = dict(request.headers)
                body = await request.body()

                try:
                    payload = await request.json()
                except (ValueError, TypeError, KeyError):
                    payload = {}

                # Verify signature if required
                if provider_config.verify_signature and provider_config.secret:
                    parser = self.parsers[provider]
                    signature = headers.get("x-hub-signature-256", "")  # GitHub format

                    if not parser.verify_signature(
                        body, signature, provider_config.secret
                    ):
                        self.logger.warning(
                            "Invalid signature for %s webhook", provider.value
                        )
                        raise HTTPException(status_code=401, detail="Invalid signature")

                # Parse webhook payload
                parser = self.parsers[provider]
                parsed_payload = parser.parse(headers, payload)

                if not parsed_payload:
                    self.logger.info(
                        "Unsupported event type for %s webhook", provider.value
                    )
                    return {"status": "ignored", "reason": "unsupported event type"}

                self.logger.info(
                    "Received %s webhook: %s for %s:%s",
                    provider.value,
                    parsed_payload.event_type.value,
                    parsed_payload.repository_name,
                    parsed_payload.branch,
                )

                # Process webhook in background
                background_tasks.add_task(
                    self._process_webhook_background, parsed_payload
                )

                return {
                    "status": "accepted",
                    "provider": provider.value,
                    "event_type": parsed_payload.event_type.value,
                    "repository": parsed_payload.repository_name,
                    "branch": parsed_payload.branch,
                }

            except HTTPException:
                raise
            except (ValueError, RuntimeError) as e:
                self.logger.error("Error handling %s webhook: %s", provider.value, e)
                raise HTTPException(
                    status_code=500, detail="Internal server error"
                ) from e

        return webhook_handler

    async def _process_webhook_background(self, payload) -> None:
        """Process webhook payload in background."""
        try:
            result = self.processing_service.process_webhook_event(payload)

            if result.success:
                self.logger.info(
                    "Successfully processed webhook: %d actions created",
                    len(result.processed_actions),
                )
            else:
                self.logger.error("Failed to process webhook: %s", result.error)

        except (ValueError, RuntimeError) as e:
            self.logger.error("Error in background webhook processing: %s", e)

    def _get_provider_config(
        self, provider: WebhookProvider
    ) -> Optional[ProviderWebhookConfig]:
        """Get configuration for a specific provider."""
        for config in self.config.providers:
            if config.provider == provider:
                return config
        return None

    async def start_server(self) -> None:
        """Start the webhook server."""
        self.logger.info(
            "Starting webhook server on %s:%d",
            self.config.server.host,
            self.config.server.port,
        )

        # Start background action executor
        self._start_action_executor()

        # Configure uvicorn
        uvicorn_config = uvicorn.Config(
            app=self.app,
            host=self.config.server.host,
            port=self.config.server.port,
            log_level="info",
            access_log=True,
        )

        # Add SSL if configured
        if self.config.server.ssl_cert and self.config.server.ssl_key:
            uvicorn_config.ssl_certfile = self.config.server.ssl_cert
            uvicorn_config.ssl_keyfile = self.config.server.ssl_key

        # Create and run server
        server = uvicorn.Server(uvicorn_config)
        await server.serve()

    def _start_action_executor(self) -> None:
        """Start background task for executing webhook actions."""

        async def action_executor_loop():
            """Background loop for executing pending actions."""
            while True:
                try:
                    executed = self.executor_service.execute_pending_actions()
                    if executed:
                        self.logger.info("Executed %d webhook actions", len(executed))

                    # Wait before next execution cycle
                    await asyncio.sleep(5)  # Check every 5 seconds

                except (ValueError, RuntimeError) as e:
                    self.logger.error("Error in action executor loop: %s", e)
                    await asyncio.sleep(10)  # Wait longer on error

        # Start the background task
        self._action_executor_task = asyncio.create_task(action_executor_loop())

    async def stop_server(self) -> None:
        """Stop the webhook server and cleanup resources."""
        self.logger.info("Stopping webhook server")

        if self._action_executor_task:
            self._action_executor_task.cancel()
            import contextlib

            with contextlib.suppress(asyncio.CancelledError):
                await self._action_executor_task

        self.logger.info("Webhook server stopped")


class WebhookServerFactory:
    """Factory for creating webhook server instances."""

    @staticmethod
    def create_server(
        config: WebhookConfig,
        processing_service: WebhookProcessingService,
        executor_service: WebhookActionExecutorService,
    ) -> WebhookServer:
        """
        Create a configured webhook server instance.

        Args:
            config: Webhook configuration
            processing_service: Service for processing webhook events
            executor_service: Service for executing webhook actions

        Returns:
            Configured WebhookServer instance
        """
        return WebhookServer(config, processing_service, executor_service)
