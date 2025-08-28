"""Opper chat model implementation for LangChain."""

import os
from typing import Any, Dict, List, Optional, Type, Union, TYPE_CHECKING

from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from opperai import Opper
else:
    try:
        from opperai import Opper
    except ImportError:
        Opper = Any  # Fallback for testing


class ChatOpperAI(BaseChatModel):
    """Opper chat model that leverages LangChain's native structured output patterns.
    
    This integration provides:
    - LangChain's standard with_structured_output() pattern
    - Simplified schema handling
    - Integration with LangChain state management
    - Opper's tracing and metrics capabilities
    
    Setup:
        Install ``langchain-opperai`` and set environment variable ``OPPER_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-opperai
            export OPPER_API_KEY="your-api-key"

    Key init args — completion params:
        task_name: Name for the Opper task
        model_name: Model to use with Opper
        instructions: Instructions for the model

    Key init args — client params:
        opper_client: Opper client instance
        parent_span_id: Parent span ID for tracing

    Instantiate:
        .. code-block:: python

            from langchain_opperai import ChatOpperAI

            llm = ChatOpperAI(
                task_name="chat",
                model_name="anthropic/claude-3.5-sonnet",
                instructions="You are a helpful AI assistant.",
            )

    Invoke:
        .. code-block:: python

            messages = [
                ("system", "You are a helpful assistant"),
                ("human", "What is the capital of France?"),
            ]
            llm.invoke(messages)

        .. code-block:: none

            AIMessage(content='The capital of France is Paris.')

    Structured output:
        .. code-block:: python

            from pydantic import BaseModel

            class Joke(BaseModel):
                setup: str
                punchline: str

            structured_llm = llm.with_structured_output(Joke)
            structured_llm.invoke("Tell me a joke about cats")

        .. code-block:: none

            Joke(setup='Why don't cats play poker in the jungle?', punchline='Too many cheetahs!')

    """

    opper_client: Optional[Any] = None
    api_key: Optional[str] = Field(default=None, description="Opper API key (for testing purposes)")
    task_name: str = Field(default="chat", description="Name for the Opper task")
    model_name: str = Field(default="anthropic/claude-3.5-sonnet", description="Model to use with Opper")
    instructions: str = Field(
        default="You are a helpful AI assistant. Provide clear, structured responses.",
        description="Instructions for the model"
    )
    parent_span_id: Optional[str] = Field(default=None, description="Parent span ID for tracing")
    provider_ref: Optional["OpperProvider"] = Field(default=None, description="Reference to provider for dynamic trace access")
    
    # LangChain integration
    _output_parser: Optional[PydanticOutputParser] = None
    _structured_schema: Optional[Type[BaseModel]] = None
    
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.opper_client is None:
            # Try to get API key from instance field first (for testing), then environment
            api_key = self.api_key or os.getenv("OPPER_API_KEY")
            if not api_key:
                raise ValueError("OPPER_API_KEY environment variable is required or api_key parameter must be provided")
            self.opper_client = Opper(http_bearer=api_key)
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for this model."""
        return "opper"

    def _get_current_trace_id(self) -> Optional[str]:
        """Get the current trace ID, preferring provider's current trace over static parent_span_id."""
        if self.provider_ref and self.provider_ref.current_trace_id:
            return self.provider_ref.current_trace_id
        return self.parent_span_id
    
    def _debug_trace_info(self) -> Dict[str, Any]:
        """Get debug information about trace state."""
        return {
            "model_static_parent": self.parent_span_id,
            "provider_current_trace": self.provider_ref.current_trace_id if self.provider_ref else None,
            "effective_trace_id": self._get_current_trace_id(),
            "has_provider_ref": self.provider_ref is not None
        }
    
    def with_structured_output(
        self,
        schema: Union[Dict, Type[BaseModel]],
        **kwargs: Any,
    ) -> "ChatOpperAI":
        """Implement LangChain's standard with_structured_output method for Opper.

        This method leverages Opper's native output_schema support directly.
        """
        # More flexible schema validation to handle Pydantic v1 and v2
        if isinstance(schema, dict):
            raise ValueError("Dictionary schemas are not yet supported, please use a Pydantic BaseModel class")
        
        # Check if it's a class and has the right base classes (works for both Pydantic v1 and v2)
        if not isinstance(schema, type):
            raise ValueError("Schema must be a Pydantic BaseModel class")
        
        # Check if it has the expected Pydantic methods/attributes
        if not (hasattr(schema, '__fields__') or hasattr(schema, 'model_fields')):
            raise ValueError("Schema must be a Pydantic BaseModel class")
        
        # Create new instance with structured output configuration
        new_instance = self.__class__(
            opper_client=self.opper_client,
            task_name=self.task_name,
            model_name=self.model_name,
            instructions=self.instructions,
            parent_span_id=self.parent_span_id,
            provider_ref=self.provider_ref,
            **kwargs
        )
        
        # Set up native structured output support
        new_instance._structured_schema = schema
        new_instance._output_parser = PydanticOutputParser(pydantic_object=schema)
        
        return new_instance
    
    def _prepare_input_for_opper(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Prepare input for Opper call as structured dictionary.
        
        This method provides a simple, flexible approach that lets the client
        control the input format while following Opper's best practices.
        Always returns a structured dict input for Opper.
        """
        if not messages:
            return {"input": ""}
        
        # Get the last message and check for additional kwargs
        last_message = messages[-1]
        
        # Build structured input dictionary
        input_data = {
            "input": last_message.content  # Primary input content
        }
        
        # Add conversation history for multi-message scenarios
        if len(messages) > 1:
            input_data["conversation_history"] = [
                {
                    "role": "user" if hasattr(msg, '__class__') and msg.__class__.__name__ == "HumanMessage"
                           else "assistant" if hasattr(msg, '__class__') and msg.__class__.__name__ == "AIMessage"
                           else "system",
                    "content": msg.content,
                    **(msg.additional_kwargs if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs else {})
                }
                for msg in messages[:-1]  # All messages except the last one
            ]
        
        # Add additional kwargs from the last message as structured context
        if hasattr(last_message, 'additional_kwargs') and last_message.additional_kwargs:
            input_data["context"] = last_message.additional_kwargs
        
        return input_data

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate response using Opper with structured output support."""
        
        try:
            # Prepare input using LangChain conventions
            input_data = self._prepare_input_for_opper(messages)
            
            # Use Opper's native structured output if schema is specified
            output_schema = self._structured_schema
            
            # Make the Opper call with native schema support
            result = self.opper_client.call(
                name=self.task_name,
                instructions=self.instructions,
                input=input_data,
                output_schema=output_schema,  # Direct Opper schema support
                model=self.model_name,
                parent_span_id=self._get_current_trace_id(),  # Use dynamic trace ID
                **kwargs
            )
            
            # Handle structured vs unstructured responses
            if self._structured_schema and self._output_parser:
                # For structured output, return the parsed Pydantic object
                try:
                    # Opper returns structured data directly in json_payload
                    structured_data = result.json_payload
                    
                    # Check if structured_data is valid (not Unset or None)
                    if (structured_data is None or 
                        not hasattr(structured_data, 'get') or 
                        str(type(structured_data).__name__) == 'Unset'):
                        raise ValueError("No structured data returned from Opper")
                    
                    # Validate and create Pydantic instance
                    parsed_output = self._structured_schema(**structured_data)
                    
                    # Create AI message with structured content
                    ai_message = AIMessage(
                        content=str(parsed_output),
                        additional_kwargs={
                            "parsed": parsed_output,
                            "span_id": getattr(result, 'span_id', None),
                            "structured": True,
                            **(structured_data if isinstance(structured_data, dict) else {})
                        }
                    )
                    
                except Exception as e:
                    # Fallback to text parsing if direct structured parsing fails
                    text_content = self._extract_text_response(result)
                    parsed_output = self._output_parser.parse(text_content)
                    
                    ai_message = AIMessage(
                        content=str(parsed_output),
                        additional_kwargs={
                            "parsed": parsed_output,
                            "span_id": getattr(result, 'span_id', None),
                            "structured": True,
                            "fallback_parsed": True,
                            "raw_content": text_content
                        }
                    )
            else:
                # For unstructured output, extract text response
                text_content = self._extract_text_response(result)
                
                # Safely extract additional kwargs from json_payload
                extra_kwargs = {}
                if hasattr(result, 'json_payload') and result.json_payload is not None:
                    payload = result.json_payload
                    if hasattr(payload, 'get') and isinstance(payload, dict):
                        extra_kwargs = payload
                    elif hasattr(payload, '__dict__'):
                        # Handle case where payload is an object with attributes
                        try:
                            extra_kwargs = {k: v for k, v in payload.__dict__.items() 
                                          if not k.startswith('_')}
                        except:
                            extra_kwargs = {}
                
                ai_message = AIMessage(
                    content=text_content,
                    additional_kwargs={
                        "span_id": getattr(result, 'span_id', None),
                        "structured": False,
                        **extra_kwargs
                    }
                )
            
            generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[generation])
            
        except Exception as e:
            # Add more detailed error information for debugging
            error_details = {
                "error_message": str(e),
                "error_type": type(e).__name__,
                "has_result": locals().get('result') is not None,
                "result_type": type(locals().get('result', None)).__name__ if locals().get('result') is not None else None,
                "has_json_payload": hasattr(locals().get('result', None), 'json_payload') if locals().get('result') is not None else False,
                "json_payload_type": type(getattr(locals().get('result', None), 'json_payload', None)).__name__ if hasattr(locals().get('result', None), 'json_payload') else None,
            }
            raise ValueError(f"Error calling Opper with structured output: {str(e)}\nDebug info: {error_details}")
    
    def _extract_text_response(self, opper_result: Any) -> str:
        """Extract text response from Opper result."""
        # First priority: Check for direct message attribute (Opper's standard response field)
        if hasattr(opper_result, 'message') and opper_result.message:
            return str(opper_result.message)
        
        # Second priority: Check json_payload for structured fields
        if hasattr(opper_result, 'json_payload'):
            payload = opper_result.json_payload
            
            # Check if payload is a valid dict-like object (not Unset or None)
            if payload is not None and hasattr(payload, 'get') and hasattr(payload, 'values'):
                # Common response fields in order of preference
                for field in ["message", "response", "answer", "output", "result", "content"]:
                    if field in payload and isinstance(payload[field], str):
                        return payload[field]
                
                # Fallback to first substantial string field
                try:
                    for value in payload.values():
                        if isinstance(value, str) and len(value) > 10:
                            return value
                except (AttributeError, TypeError):
                    # Handle cases where payload.values() might fail
                    pass
        
        # Final fallback
        return str(opper_result) if opper_result else "No response generated"

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generate."""
        return self._generate(messages, stop, run_manager, **kwargs)


class OpperProvider:
    """Provider that leverages LangGraph's native patterns effectively.
    
    Features:
    - Simple architecture using LangGraph conventions
    - Direct integration with Opper's native structured output
    - State-driven configuration
    - Seamless tool calling integration

    Setup:
        Install ``langchain-opperai`` and set environment variable ``OPPER_API_KEY``.

        .. code-block:: bash

            pip install langchain-opperai
            export OPPER_API_KEY="your-api-key"

    Instantiate:
        .. code-block:: python

            from langchain_opperai import OpperProvider

            provider = OpperProvider()

    Create chat model:
        .. code-block:: python

            chat_model = provider.create_chat_model(
                task_name="chat",
                model_name="anthropic/claude-3.5-sonnet",
                instructions="You are a helpful AI assistant.",
            )

    Create structured model:
        .. code-block:: python

            from pydantic import BaseModel

            class Response(BaseModel):
                answer: str
                confidence: float

            structured_model = provider.create_structured_model(
                task_name="structured_chat",
                instructions="Provide structured responses.",
                output_schema=Response,
            )

    With tracing:
        .. code-block:: python

            provider.start_trace("conversation", "User wants help with X")
            
            # Models will now use this trace
            result = chat_model.invoke("Help me with X")
            
            provider.end_trace("Provided help successfully")
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the provider."""
        self.api_key = api_key or os.getenv("OPPER_API_KEY")
        if not self.api_key:
            raise ValueError("OPPER_API_KEY must be provided or set as environment variable")
        
        self.client = Opper(http_bearer=self.api_key)
        self.current_trace_id = None
    
    def create_chat_model(
        self,
        task_name: str = "chat",
        model_name: str = "anthropic/claude-3.5-sonnet",
        instructions: str = "You are a helpful AI assistant. Provide clear, structured responses.",
    ) -> "ChatOpperAI":
        """Create a new Opper chat model."""
        
        return ChatOpperAI(
            opper_client=self.client,
            task_name=task_name,
            model_name=model_name,
            instructions=instructions,
            parent_span_id=self.current_trace_id,
            provider_ref=self,  # Pass provider reference for dynamic trace access
        )
    
    def create_structured_model(
        self,
        task_name: str,
        instructions: str,
        output_schema: Type[BaseModel],
        model_name: str = "anthropic/claude-3.5-sonnet",
    ) -> "ChatOpperAI":
        """Create a model with structured output using LangChain's native pattern.
        
        This method creates a model that leverages both Opper's native structured
        output and LangChain's with_structured_output() pattern.
        
        Args:
            task_name: Name for the Opper task
            instructions: Instructions for the model
            output_schema: Pydantic model class for structured output
            model_name: Model to use (default: anthropic/claude-3.5-sonnet)
            
        Returns:
            ChatOpperAI instance configured for structured output
        """
        base_model = self.create_chat_model(
            task_name=task_name,
            model_name=model_name,
            instructions=instructions,
        )
        
        return base_model.with_structured_output(output_schema)
    
    def start_trace(self, name: str, input_data: Any = None) -> str:
        """Start a new trace for tracking the workflow.
        
        Creates a parent span that will contain all subsequent model calls.
        All models created by this provider will use this span as their parent.
        """
        span = self.client.spans.create(
            name=name,
            input=str(input_data) if input_data else None
        )
        self.current_trace_id = span.id
        return span.id
    
    def end_trace(self, output_data: Any = None):
        """End the current trace."""
        if self.current_trace_id:
            self.client.spans.update(
                span_id=self.current_trace_id,
                output=str(output_data) if output_data else None
            )
            self.current_trace_id = None
    
    def add_metric(self, span_id: str, dimension: str, value: float, comment: str = ""):
        """Add a metric to a span."""
        self.client.span_metrics.create_metric(
            span_id=span_id,
            dimension=dimension,
            value=value,
            comment=comment
        )


# Forward reference resolution - import after class definition
def _rebuild_model():
    """Rebuild the model to resolve forward references."""
    try:
        ChatOpperAI.model_rebuild()
    except ImportError:
        # OpperProvider not yet available, will be resolved later
        pass

# Call rebuild when module is imported
_rebuild_model()
