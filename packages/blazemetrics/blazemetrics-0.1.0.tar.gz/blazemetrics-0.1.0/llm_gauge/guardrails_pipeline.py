from typing import Iterable, AsyncIterable, Dict, Any, List, Iterator, Optional, Callable
import asyncio
from concurrent.futures import ProcessPoolExecutor
from functools import partial

from .guardrails import Guardrails


def _check_chunk(texts: List[str], cfg: Dict[str, Any]) -> Dict[str, Any]:
    gr = Guardrails(
        blocklist=cfg.get("blocklist", []),
        regexes=cfg.get("regexes", []),
        case_insensitive=cfg.get("case_insensitive", True),
        redact_pii=cfg.get("redact_pii", True),
        safety=cfg.get("safety", True),
        json_schema=cfg.get("json_schema"),
    )
    return gr.check(texts)


def monitor_tokens_sync(
    tokens: Iterable[str],
    guardrails: Guardrails,
    every_n_tokens: int = 20,
    joiner: str = "",
) -> Iterator[Dict[str, Any]]:
    buffer: List[str] = []
    for tok in tokens:
        buffer.append(tok)
        if len(buffer) >= every_n_tokens:
            text = joiner.join(buffer)
            yield guardrails.check([text])
            buffer.clear()
    if buffer:
        text = joiner.join(buffer)
        yield guardrails.check([text])


async def monitor_tokens_async(
    tokens: AsyncIterable[str],
    guardrails: Guardrails,
    every_n_tokens: int = 20,
    joiner: str = "",
) -> AsyncIterable[Dict[str, Any]]:
    buffer: List[str] = []
    async for tok in tokens:
        buffer.append(tok)
        if len(buffer) >= every_n_tokens:
            text = joiner.join(buffer)
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, guardrails.check, [text])
            yield result
            buffer.clear()
    if buffer:
        text = joiner.join(buffer)
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, guardrails.check, [text])
        yield result


def map_large_texts(
    texts: List[str],
    guardrails: Guardrails,
    processes: Optional[int] = None,
    chunk_size: int = 1000,
) -> List[Dict[str, Any]]:
    cfg = {
        "blocklist": guardrails.blocklist,
        "regexes": guardrails.regexes,
        "case_insensitive": guardrails.case_insensitive,
        "redact_pii": guardrails.redact_pii,
        "safety": guardrails.safety,
        "json_schema": guardrails.json_schema,
    }
    chunks: List[List[str]] = [texts[i:i+chunk_size] for i in range(0, len(texts), chunk_size)]
    if not chunks:
        return []
    worker = partial(_check_chunk, cfg=cfg)
    results: List[Dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=processes) as ex:
        for res in ex.map(worker, chunks):
            results.append(res)
    return results


def enforce_stream_sync(
    tokens: Iterable[str],
    guardrails: Guardrails,
    every_n_tokens: int = 20,
    joiner: str = "",
    replacement: str = "[REDACTED]",
    safety_threshold: float = 0.7,
    on_violation: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Iterator[str]:
    buffer: List[str] = []
    for tok in tokens:
        buffer.append(tok)
        if len(buffer) >= every_n_tokens:
            text = joiner.join(buffer)
            res = guardrails.check([text])
            if on_violation:
                on_violation(res)
            if any(res.get("blocked", [])) or any(res.get("regex_flagged", [])) or max(res.get("safety_score", [0.0])) >= safety_threshold:
                yield replacement
                break
            yield text
            buffer.clear()
    if buffer:
        yield joiner.join(buffer) 