"""源自lx.inference, 添加了base_url"""

import abc
from collections.abc import Iterator, Mapping, Sequence
import concurrent.futures
import dataclasses
import enum
import json
import textwrap
from typing import Any

import httpx
import openai
import yaml

from langextract import data
from langextract import exceptions
from langextract import schema


@dataclasses.dataclass(frozen=True)
class ScoredOutput:
    """Scored output."""

    score: float | None = None
    output: str | None = None

    def __str__(self) -> str:
        if self.output is None:
            return f'Score: {self.score:.2f}\nOutput: None'
        formatted_lines = textwrap.indent(self.output, prefix='  ')
        return f'Score: {self.score:.2f}\nOutput:\n{formatted_lines}'


class InferenceOutputError(exceptions.LangExtractError):
    """Exception raised when no scored outputs are available from the language model."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class BaseLanguageModel(abc.ABC):
    """An abstract inference class for managing LLM inference.

    Attributes:
      _constraint: A `Constraint` object specifying constraints for model output.
    """

    def __init__(self, constraint: schema.Constraint = schema.Constraint()):
        """Initializes the BaseLanguageModel with an optional constraint.

        Args:
          constraint: Applies constraints when decoding the output. Defaults to no
            constraint.
        """
        self._constraint = constraint

    @abc.abstractmethod
    def infer(
            self, batch_prompts: Sequence[str], **kwargs
    ) -> Iterator[Sequence[ScoredOutput]]:
        """Implements language model inference.

        Args:
          batch_prompts: Batch of inputs for inference. Single element list can be
            used for a single input.
          **kwargs: Additional arguments for inference, like temperature and
            max_decode_steps.

        Returns: Batch of Sequence of probable output text outputs, sorted by
          descending
          score.
        """


class InferenceType(enum.Enum):
    ITERATIVE = 'iterative'
    MULTIPROCESS = 'multiprocess'


@dataclasses.dataclass(init=False)
class OpenAILanguageModel(BaseLanguageModel):
    """Language model inference using OpenAI's API with structured output."""

    base_url: str | httpx.URL | None = None
    model_id: str = 'gpt-4o-mini'
    api_key: str | None = None
    organization: str | None = None
    format_type: data.FormatType = data.FormatType.JSON
    temperature: float = 0.0
    max_workers: int = 10
    _client: openai.OpenAI | None = dataclasses.field(
        default=None, repr=False, compare=False
    )
    _extra_kwargs: dict[str, Any] = dataclasses.field(
        default_factory=dict, repr=False, compare=False
    )

    def __init__(
            self,
            base_url: str | httpx.URL | None = None,
            model_id: str = 'gpt-4o-mini',
            api_key: str | None = None,
            organization: str | None = None,
            format_type: data.FormatType = data.FormatType.JSON,
            temperature: float = 0.0,
            max_workers: int = 10,
            **kwargs,
    ) -> None:
        """Initialize the OpenAI language model.

        Args:
          model_id: The OpenAI model ID to use (e.g., 'gpt-4o-mini', 'gpt-4o').
          api_key: API key for OpenAI service.
          organization: Optional OpenAI organization ID.
          format_type: Output format (JSON or YAML).
          temperature: Sampling temperature.
          max_workers: Maximum number of parallel API calls.
          **kwargs: Ignored extra parameters so callers can pass a superset of
            arguments shared across back-ends without raising ``TypeError``.
        """
        self.base_url = base_url
        self.model_id = model_id
        self.api_key = api_key
        self.organization = organization
        self.format_type = format_type
        self.temperature = temperature
        self.max_workers = max_workers
        self._extra_kwargs = kwargs or {}

        if not self.api_key:
            raise ValueError('API key not provided.')

        # Initialize the OpenAI client
        self._client = openai.OpenAI(
            base_url=base_url,
            api_key=self.api_key, organization=self.organization
        )

        super().__init__(
            constraint=schema.Constraint(constraint_type=schema.ConstraintType.NONE)
        )

    def _process_single_prompt(self, prompt: str, config: dict) -> ScoredOutput:
        """Process a single prompt and return a ScoredOutput."""
        try:
            # Prepare the system message for structured output
            system_message = ''
            if self.format_type == data.FormatType.JSON:
                system_message = (
                    'You are a helpful assistant that responds in JSON format.'
                )
            elif self.format_type == data.FormatType.YAML:
                system_message = (
                    'You are a helpful assistant that responds in YAML format.'
                )

            # Create the chat completion using the v1.x client API
            response = self._client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': prompt},
                ],
                temperature=config.get('temperature', self.temperature),
                max_tokens=config.get('max_output_tokens'),
                top_p=config.get('top_p'),
                n=1,
            )

            # Extract the response text using the v1.x response format
            output_text = response.choices[0].message.content

            return ScoredOutput(score=1.0, output=output_text)

        except Exception as e:
            raise InferenceOutputError(f'OpenAI API error: {str(e)}') from e

    def infer(
            self, batch_prompts: Sequence[str], **kwargs
    ) -> Iterator[Sequence[ScoredOutput]]:
        """Runs inference on a list of prompts via OpenAI's API.

        Args:
          batch_prompts: A list of string prompts.
          **kwargs: Additional generation params (temperature, top_p, etc.)

        Yields:
          Lists of ScoredOutputs.
        """
        config = {
            'temperature': kwargs.get('temperature', self.temperature),
        }
        if 'max_output_tokens' in kwargs:
            config['max_output_tokens'] = kwargs['max_output_tokens']
        if 'top_p' in kwargs:
            config['top_p'] = kwargs['top_p']

        # Use parallel processing for batches larger than 1
        if len(batch_prompts) > 1 and self.max_workers > 1:
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=min(self.max_workers, len(batch_prompts))
            ) as executor:
                future_to_index = {
                    executor.submit(
                        self._process_single_prompt, prompt, config.copy()
                    ): i
                    for i, prompt in enumerate(batch_prompts)
                }

                results: list[ScoredOutput | None] = [None] * len(batch_prompts)
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        results[index] = future.result()
                    except Exception as e:
                        raise InferenceOutputError(
                            f'Parallel inference error: {str(e)}'
                        ) from e

                for result in results:
                    if result is None:
                        raise InferenceOutputError('Failed to process one or more prompts')
                    yield [result]
        else:
            # Sequential processing for single prompt or worker
            for prompt in batch_prompts:
                result = self._process_single_prompt(prompt, config.copy())
                yield [result]

    def parse_output(self, output: str) -> Any:
        """Parses OpenAI output as JSON or YAML.

        Note: This expects raw JSON/YAML without code fences.
        Code fence extraction is handled by resolver.py.
        """
        try:
            if self.format_type == data.FormatType.JSON:
                return json.loads(output)
            else:
                return yaml.safe_load(output)
        except Exception as e:
            raise ValueError(
                f'Failed to parse output as {self.format_type.name}: {str(e)}'
            ) from e
