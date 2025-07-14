from typing import Any, Optional, cast

from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorQuery
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from approaches.approach import Approach, DataPoints, ExtraInfo, ThoughtStep
from approaches.promptmanager import PromptManager
from core.authentication import AuthenticationHelper


class RetrieveThenReadApproach(Approach):
    """
    Simple retrieve-then-read implementation, using the AI Search and OpenAI APIs directly. It first retrieves
    top documents from search, then constructs a prompt with them, and then uses OpenAI to generate a completion
    (answer) with that prompt.
    """

    def __init__(
        self,
        *,
        search_client: SearchClient,
        auth_helper: AuthenticationHelper,
        openai_client: AsyncOpenAI,
        chatgpt_model: str,
        chatgpt_deployment: Optional[str],  # Not needed for non-Azure OpenAI
        embedding_model: str,
        embedding_deployment: Optional[str],  # Not needed for non-Azure OpenAI or for retrieval_mode="text"
        embedding_dimensions: int,
        sourcepage_field: str,
        content_field: str,
        query_language: str,
        query_speller: str,
        prompt_manager: PromptManager,
        reasoning_effort: Optional[str] = None,
    ):
        self.search_client = search_client
        self.chatgpt_deployment = chatgpt_deployment
        self.openai_client = openai_client
        self.auth_helper = auth_helper
        self.chatgpt_model = chatgpt_model
        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions
        self.chatgpt_deployment = chatgpt_deployment
        self.embedding_deployment = embedding_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        self.query_language = query_language
        self.query_speller = query_speller
        self.prompt_manager = prompt_manager
        self.answer_prompt = self.prompt_manager.load_prompt("ask_answer_question.prompty")
        self.extract_keywords_prompt = self.prompt_manager.load_prompt("chat_extract_keywords.prompty")
        self.reasoning_effort = reasoning_effort
        self.include_token_usage = True

    async def run(
        self,
        messages: list[ChatCompletionMessageParam],
        session_state: Any = None,
        context: dict[str, Any] = {},
    ) -> dict[str, Any]:
        q = messages[-1]["content"]
        if not isinstance(q, str):
            raise ValueError("The most recent message content must be a string.")
        overrides = context.get("overrides", {})
        auth_claims = context.get("auth_claims", {})
        use_text_search = overrides.get("retrieval_mode") in ["text", "hybrid", None]
        use_vector_search = overrides.get("retrieval_mode") in ["vectors", "hybrid", None]
        use_semantic_ranker = True if overrides.get("semantic_ranker") else False
        use_query_rewriting = True if overrides.get("query_rewriting") else False
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top", 3)
        minimum_search_score = overrides.get("minimum_search_score", 0.0)
        minimum_reranker_score = overrides.get("minimum_reranker_score", 0.0)
        filter = self.build_filter(overrides, auth_claims)

        reasoning_model_support = self.GPT_REASONING_MODELS.get(self.chatgpt_model)
        if reasoning_model_support and (not reasoning_model_support.streaming): # changed to remove "should_stream" since not in scope
            raise Exception(
                f"{self.chatgpt_model} does not support streaming. Please use a different model or disable streaming."
            )

        # Step 1: Exract keywords
        
        user_query = self.prompt_manager.render_prompt(
            self.extract_keywords_prompt, {"user_query": q}
        )
        
        chat_completion_keywords: ChatCompletion = await self.openai_client.chat.completions.create(
            messages=user_query,
            # Azure OpenAI takes the deployment name as the model name
            model=self.chatgpt_deployment if self.chatgpt_deployment else self.chatgpt_model,
            temperature=0.0,  # No creativity for generating keywords
            max_tokens=100,
            n=1
        )

        # code copy + pasted from chatapproach.py, get_user_query. And slightly changed. Changed NO_RESPONSE to 0
        
        response_message = chat_completion_keywords.choices[0].message

        if query_text := response_message.content:
            if query_text.strip() == 0: # 0 means no response
                query_text == user_query
        else:
            query_text = user_query

        # If retrieval mode includes vectors, compute an embedding for the query
        vectors: list[VectorQuery] = []
        if use_vector_search:
            vectors.append(await self.compute_text_embedding(query_text))

        results = await self.search(
            top,
            query_text,
            filter,
            vectors,
            use_text_search,
            use_vector_search,
            use_semantic_ranker,
            use_semantic_captions,
            minimum_search_score,
            minimum_reranker_score,
            use_query_rewriting,
        )

        # Process results
        text_sources = self.get_sources_content(results, use_semantic_captions, use_image_citation=False)
        messages = self.prompt_manager.render_prompt(
            self.answer_prompt,
            self.get_system_prompt_variables(overrides.get("prompt_template"))
            | {"user_query": q, "text_sources": text_sources},
        )

        chat_completion = cast(
            ChatCompletion,
            await self.create_chat_completion(
                self.chatgpt_deployment,
                self.chatgpt_model,
                messages=messages,
                overrides=overrides,
                response_token_limit=self.get_response_token_limit(self.chatgpt_model, 1024),
            ),
        )

        extra_info = ExtraInfo(
            DataPoints(text=text_sources),
            thoughts=[
                ThoughtStep(
                    "Search using user query",
                    query_text,
                    {
                        "use_semantic_captions": use_semantic_captions,
                        "use_semantic_ranker": use_semantic_ranker,
                        "use_query_rewriting": use_query_rewriting,
                        "top": top,
                        "filter": filter,
                        "use_vector_search": use_vector_search,
                        "use_text_search": use_text_search,
                    },
                ),
                ThoughtStep(
                    "Search results",
                    [result.serialize_for_results() for result in results],
                ),
                self.format_thought_step_for_chatcompletion(
                    title="Prompt to generate answer",
                    messages=messages,
                    overrides=overrides,
                    model=self.chatgpt_model,
                    deployment=self.chatgpt_deployment,
                    usage=chat_completion.usage,
                ),
            ],
        )

        return {
            "message": {
                "content": chat_completion.choices[0].message.content,
                "role": chat_completion.choices[0].message.role,
            },
            "context": extra_info,
            "session_state": session_state,
        }
