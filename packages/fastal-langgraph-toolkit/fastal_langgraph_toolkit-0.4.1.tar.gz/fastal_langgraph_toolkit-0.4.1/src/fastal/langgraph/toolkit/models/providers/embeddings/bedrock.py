"""AWS Bedrock embedding provider implementation.

This module provides the AWS Bedrock-specific implementation for text embeddings,
supporting various embedding models available through AWS Bedrock service.
"""

from typing import Any

from ....exceptions import ConfigurationError
from ...base import BaseProvider

try:
    import boto3
    from langchain_aws import BedrockEmbeddings
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False


class BedrockEmbeddingProvider(BaseProvider):
    """AWS Bedrock embedding provider implementation.
    
    Provides text embeddings using models available through AWS Bedrock,
    including Amazon Titan and other foundation model embeddings.
    """

    def __init__(self, provider_config: Any, model_name: str, **kwargs):
        """Initialize the Bedrock embedding provider.
        
        Args:
            provider_config: Bedrock-specific configuration including AWS credentials
            model_name: Model ID in Bedrock (e.g., 'amazon.titan-embed-text-v1')
            **kwargs: Additional parameters to pass to the model
        """
        super().__init__(provider_config)
        self.model_name = model_name
        self.kwargs = kwargs

    def _create_model(self) -> Any:
        """Create the Bedrock embeddings instance.
        
        Returns:
            Configured BedrockEmbeddings instance
            
        Raises:
            ConfigurationError: If Bedrock provider is not available
        """
        if not BEDROCK_AVAILABLE:
            raise ConfigurationError(
                "Bedrock provider not available. Install: uv add langchain-aws boto3"
            )

        # Create boto3 session with appropriate credentials
        session_kwargs = {}

        # Use profile if specified
        if self.config.profile_name:
            session_kwargs['profile_name'] = self.config.profile_name

        # Use explicit credentials if provided
        if self.config.aws_access_key_id:
            session_kwargs.update({
                'aws_access_key_id': self.config.aws_access_key_id,
                'aws_secret_access_key': self.config.aws_secret_access_key,
                'aws_session_token': self.config.aws_session_token,
            })

        session = boto3.Session(**session_kwargs)
        bedrock_client = session.client(
            'bedrock-runtime',
            region_name=self.config.region_name
        )

        # Build model configuration
        model_config = {
            'client': bedrock_client,
            'model_id': self.model_name,
        }

        # Add any additional kwargs
        model_config.update(self.kwargs)

        return BedrockEmbeddings(**model_config)

    def is_available(self) -> bool:
        """Check if Bedrock provider is available (module installed + AWS credentials).
        
        Returns:
            True if Bedrock is available with AWS credentials
        """
        if not BEDROCK_AVAILABLE:
            return False
            
        # Check if we have AWS credentials (either explicit or profile)
        has_credentials = (
            (self.config.aws_access_key_id and self.config.aws_secret_access_key) or
            self.config.profile_name
        )
        
        return has_credentials and bool(self.config.region_name)
    
    async def is_available_async(self) -> bool:
        """Test real AWS Bedrock embeddings API connectivity using configured model.
        
        Tests the actual configured model to detect when models are deprecated.
        
        Returns:
            True if AWS Bedrock embeddings API is reachable with configured model
        """
        if not self.is_available():
            return False
            
        try:
            # Create test client with same configuration as production
            session_kwargs = {}
            
            if self.config.profile_name:
                session_kwargs['profile_name'] = self.config.profile_name
                
            if self.config.aws_access_key_id:
                session_kwargs.update({
                    'aws_access_key_id': self.config.aws_access_key_id,
                    'aws_secret_access_key': self.config.aws_secret_access_key,
                    'aws_session_token': self.config.aws_session_token,
                })
            
            session = boto3.Session(**session_kwargs)
            bedrock_client = session.client(
                'bedrock-runtime',
                region_name=self.config.region_name
            )
            
            # Test with the actual configured model
            test_embeddings = BedrockEmbeddings(
                client=bedrock_client,
                model_id=self.model_name,  # Use configured model
                timeout=5,  # Short timeout for health check
            )
            
            # Send minimal test embedding
            embedding = await test_embeddings.aembed_query("test")
            return bool(embedding and len(embedding) > 0)
            
        except Exception:
            return False
