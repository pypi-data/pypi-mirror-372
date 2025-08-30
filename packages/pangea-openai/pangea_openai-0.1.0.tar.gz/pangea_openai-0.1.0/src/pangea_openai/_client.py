from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI, OpenAI
from openai._compat import cached_property
from pangea.asyncio.services import AIGuardAsync
from pangea.services import AIGuard
from typing_extensions import override

from pangea_openai.resources.responses.responses import AsyncPangeaResponses, PangeaResponses

__all__ = ("PangeaOpenAI", "AsyncPangeaOpenAI")


class PangeaOpenAI(OpenAI):
    def __init__(
        self,
        *,
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.ai_guard_client = AIGuard(token=pangea_api_key)
        self.pangea_input_recipe = pangea_input_recipe
        self.pangea_output_recipe = pangea_output_recipe

    @cached_property
    @override
    def responses(self) -> PangeaResponses:
        return PangeaResponses(self)


class AsyncPangeaOpenAI(AsyncOpenAI):
    def __init__(
        self,
        *,
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.ai_guard_client = AIGuardAsync(token=pangea_api_key)
        self.pangea_input_recipe = pangea_input_recipe
        self.pangea_output_recipe = pangea_output_recipe

    @cached_property
    @override
    def responses(self) -> AsyncPangeaResponses:
        return AsyncPangeaResponses(self)
