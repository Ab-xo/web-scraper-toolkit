# Implementation Plan — AI-Powered Query Engine

- [x] 1. Add AI config settings to backend
  - Add `groq_api_key`, `ai_model`, `ai_base_url` fields to `Settings` in `backend/app/config.py`
  - Add `GROQ_API_KEY`, `AI_MODEL`, `AI_BASE_URL` to `backend/.env.example`
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 2. Extend QueryResponse schema
  - Add `ai_powered: bool = False`, `fallback: bool = False`, `summary: str | None = None` to `QueryResponse` in `backend/app/models/schemas.py`
  - _Requirements: 2.1, 5.1, 5.2_

- [x] 3. Build DOM skeleton service

- [x] 3.1 Implement `build_skeleton()` in `backend/app/services/dom_skeleton.py`
  - Strip `<script>`, `<style>`, `<noscript>` tags and all `on*` event attributes
  - Keep only tag name, `id`, and `class` attributes per element
  - Truncate output to 4000 characters with trailing `...` if exceeded
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 3.2 Write property test for skeleton length bound (Property 1)
  - **Property 1: DOM skeleton length is always bounded**
  - **Validates: Requirements 4.1, 4.3**

- [x] 3.3 Write property test for skeleton script/style stripping (Property 2)
  - **Property 2: DOM skeleton contains no script or style content**
  - **Validates: Requirements 4.2**

- [x] 4. Build Groq LLM client

- [x] 4.1 Implement `ask_groq()` in `backend/app/services/groq_client.py`
  - Use `httpx.AsyncClient` to POST to `ai_base_url` with OpenAI chat completions format
  - Send system prompt + user message containing skeleton and intent
  - Parse JSON response to extract `selector` and `summary` fields
  - Raise on HTTP error or malformed JSON
  - _Requirements: 1.1, 2.1, 3.1, 3.3_

- [x] 5. Build AI query engine orchestrator

- [x] 5.1 Implement `run_query()` in `backend/app/services/ai_query_engine.py`
  - If `GROQ_API_KEY` is empty, call rule-based engine and return with `fallback: true`
  - Otherwise call `build_skeleton()` then `ask_groq()`
  - Apply returned selector to full HTML with BeautifulSoup
  - If selector is empty or matches nothing, call rule-based engine with `fallback: true`
  - On any exception from Groq client, call rule-based engine with `fallback: true`
  - Return response with `ai_powered: true` and populated `summary` on success
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.4_

- [x] 5.2 Write property test for missing API key fallback (Property 4)
  - **Property 4: Missing API key always produces fallback response**
  - **Validates: Requirements 3.4, 1.4**

- [x] 5.3 Write property test for results subset correctness (Property 3)
  - **Property 3: AI-powered results are a subset of the document**
  - **Validates: Requirements 1.1, 1.2**

- [x] 5.4 Write property test for summary presence (Property 5)
  - **Property 5: Non-empty results always include a summary**
  - **Validates: Requirements 2.1**

- [x] 6. Wire AI engine into the query router
  - Update `backend/app/routers/query.py` to import and call `ai_query_engine.run_query` instead of `query_engine.run_query`
  - Make the route handler `async` since the AI client uses `await`
  - _Requirements: 1.1_

- [x] 7. Checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Update frontend QueryPanel

- [x] 8.1 Add AI badge and Rule-based badge rendering
  - Show purple "✦ AI" badge when `ai_powered: true`
  - Show gray "Rule-based" badge when `fallback: true`
  - _Requirements: 5.1, 5.2_

- [x] 8.2 Render AI summary block
  - When `summary` is present in the query response, render it in an italicized muted block above the results list
  - _Requirements: 5.3_

- [x] 9. Final checkpoint — ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
