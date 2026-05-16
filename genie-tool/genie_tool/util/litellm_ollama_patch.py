# -*- coding: utf-8 -*-
# =====================
# Monkey patch for litellm Ollama chunk parser bug
#
# This fixes a bug where litellm cannot parse Ollama chunks with empty response strings.
# See: https://github.com/BerriAI/litellm/issues/23155
# =====================
def patch_litellm_ollama_parser():
    """
    Patch litellm's Ollama chunk parser to handle empty response chunks.

    Ollama sends empty response chunks as "heartbeat" at the start of streaming.
    The original litellm parser raises an exception when encountering these chunks.
    This patch modifies the parser to skip empty chunks gracefully.
    """
    try:
        from litellm.llms.ollama.completion.transformation import OllamaTextCompletionResponseIterator
        from litellm.types.utils import GenericStreamingChunk

        # Store the original method
        original_chunk_parser = OllamaTextCompletionResponseIterator.chunk_parser

        def patched_chunk_parser(self, chunk: dict) -> GenericStreamingChunk:
            """Patched chunk parser that handles empty response chunks."""
            try:
                if "error" in chunk:
                    raise Exception(f"Ollama Error - {chunk}")

                text = ""
                is_finished = False
                finish_reason = None
                if chunk["done"] is True:
                    text = ""
                    is_finished = True
                    finish_reason = "stop"
                    prompt_eval_count = chunk.get("prompt_eval_count", None)
                    eval_count = chunk.get("eval_count", None)

                    from litellm.types.llms.openai import ChatCompletionUsageBlock
                    usage = None
                    if prompt_eval_count is not None and eval_count is not None:
                        usage = ChatCompletionUsageBlock(
                            prompt_tokens=prompt_eval_count,
                            completion_tokens=eval_count,
                            total_tokens=prompt_eval_count + eval_count,
                        )
                    return GenericStreamingChunk(
                        text=text,
                        is_finished=is_finished,
                        finish_reason=finish_reason,
                        usage=usage,
                    )
                elif chunk.get("response"):  # Changed from chunk["response"] to chunk.get("response")
                    text = chunk["response"]
                    return GenericStreamingChunk(
                        text=text,
                        is_finished=is_finished,
                        finish_reason="stop",
                        usage=None,
                    )
                else:
                    # Handle empty response chunks (Ollama sends these as "heartbeat" at stream start)
                    # Just skip and return an empty chunk
                    return GenericStreamingChunk(
                        text="",
                        is_finished=False,
                        finish_reason=None,
                        usage=None,
                    )
            except Exception as e:
                raise e

        # Apply the patch
        OllamaTextCompletionResponseIterator.chunk_parser = patched_chunk_parser
        return True
    except ImportError:
        return False
