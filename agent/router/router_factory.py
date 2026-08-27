from .router import (
    BaseRouter,
    KeywordRouter,
    LLMRouter,
)


class RouterFactory:

    _routers: dict[str, type[BaseRouter]] = {
        "keyword": KeywordRouter,
        "llm": LLMRouter,
    }

    @classmethod
    def create(cls, router_type: str) -> BaseRouter:

        if not router_type:
            raise ValueError(
                "Router type must be given."
            )

        router_type = router_type.lower().strip()

        if not router_type in cls._routers:
            raise ValueError(
                f"Router not found: {router_type}."
                f"Available routers: {list(cls._routers.keys())}"
            )

        router_class = cls._routers[router_type]
        return router_class()