import json
from json import JSONDecodeError
from typing import Iterator, Union, Dict

from pydantic import ValidationError

from aisberg.models.chat import ChatCompletionChunk


def parse_chat_line(
    line: str, *, full_chunk: bool = True
) -> Iterator[Union[str, ChatCompletionChunk]]:
    """
    Parse une ligne de stream JSON (commençant par `data:`) et yield un ou plusieurs éléments utilisables.

    Args:
        line (str): Ligne du flux à traiter.
        full_chunk (bool): Contrôle le format de sortie (chunk brut ou contenu transformé).

    Yields:
        Union[str, dict]: Le chunk complet ou un morceau de texte/fonction/tool_call.
    """
    if not line.startswith("data:"):
        return

    data = line[len("data:") :].strip()
    if data == "[DONE]":
        return

    try:
        chunk = ChatCompletionChunk.model_validate(json.loads(data))

        if chunk.object != "chat.completion.chunk":
            raise ValueError(f"Unexpected object type: {chunk['object']}")

        if not chunk.choices:
            return

        if chunk.choices[0].finish_reason == "stop":
            return

        if full_chunk:
            yield chunk
            return

        delta = chunk.choices[0].delta

        if delta.content:
            yield delta.content

        elif delta.function_call:
            yield f"[FUNCTION_CALL]{delta['function_call']}"

        elif delta.tool_calls:
            yield f"[TOOL_CALLS]{delta['tool_calls']}"

        else:
            # Si le chunk ne contient pas de contenu, on ne yield rien
            return

    except JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    except ValidationError as e:
        print(f"Error parsing chunk: {e}")
        return


class WorkflowLineParser:
    def __init__(self, full_chunk: bool = True):
        self.full_chunk = full_chunk
        self._buckets: Dict[str, Dict] = {}
        self.current_event = None

    def __call__(self, line: str) -> Iterator[Union[str, dict]]:
        if line.startswith("event:"):
            self.current_event = line[len("event:") :].strip()
            return

        if not line.startswith("data:"):
            return

        data = line[len("data:") :].strip()
        if data == "[DONE]":
            return

        try:
            payload = json.loads(data)

            # Gestion des events chunk + slices
            if self.current_event == "chunk":
                self._buckets[payload["id"]] = {
                    "totalSlices": payload["totalSlices"],
                    "slices": [None] * payload["totalSlices"],
                }

            elif self.current_event == "chunk_slice":
                bucket = self._buckets.get(payload["id"])
                if bucket:
                    bucket["slices"][payload["index"]] = payload["slice"]

            elif self.current_event == "chunk_end":
                bucket = self._buckets.pop(payload["id"], None)
                if bucket:
                    full_json = "".join(bucket["slices"])
                    try:
                        yield from self._yield_chunk(full_json)
                    except json.JSONDecodeError:
                        raise RuntimeError("Invalid chunk received in workflow.run()")

        except json.JSONDecodeError:
            raise RuntimeError("Invalid format of data received in workflow.run()")

    @staticmethod
    def _yield_chunk(raw: str) -> Iterator[Union[str, dict]]:
        chunk = json.loads(raw)
        yield chunk
