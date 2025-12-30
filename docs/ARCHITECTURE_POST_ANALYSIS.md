# Post Analysis & Style-Based Generation - Architecture & Logic Flow

## Overview

This document outlines the logic flow and architecture for adding post analysis capabilities to the Threads Automation system. The goal is to analyze the user's past posts and use those patterns to generate new posts that match their authentic style.

---

## Table of Contents

1. [Current Architecture](#current-architecture)
2. [Proposed Architecture](#proposed-architecture-phase-1-basic-post-analysis)
3. [Logic Flow: Post Analysis & Generation](#logic-flow-post-analysis--generation)
4. [Use Cases & Decision Points](#use-cases--decision-points)
5. [Architecture Decisions](#architecture-decisions)
6. [Scalability Considerations](#scalability-considerations)
7. [Error Handling & Edge Cases](#error-handling--edge-cases)
8. [Implementation Phases](#implementation-phases)
9. [Data Flow Diagram](#data-flow-diagram)
10. [Key Questions to Resolve](#key-questions-to-resolve)
11. [Recommendations for Phase 1](#recommendations-for-phase-1)
12. [Next Steps](#next-steps)

---

## Current Architecture

### Current System Flow

```
┌─────────────────┐
│  Notion Client  │
│  (Briefs DB)    │
└────────┬────────┘
         │
         │ Fetch Briefs
         ▼
┌─────────────────┐
│ PostGenerator   │
│                 │
│  ┌───────────┐  │
│  │ Brand     │  │
│  │ Profile   │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Prompt    │  │
│  │ Builder   │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │
         │ Build Prompt
         ▼
┌─────────────────┐
│   GPT Client    │
│  (OpenAI API)   │
└────────┬────────┘
         │
         │ Generated Text
         ▼
┌─────────────────┐
│   Validation    │
│  (Length, etc)  │
└────────┬────────┘
         │
         │ Valid Post
         ▼
┌─────────────────┐
│  User Approval  │
└────────┬────────┘
         │
         │ Approved
         ▼
┌─────────────────┐
│  Threads API    │
│   (Post)        │
└─────────────────┘
```

### Current Components

1. **NotionClient** - Fetches briefs from Notion database
2. **BrandProfile** - Loads static brand guidelines from markdown file
3. **PromptBuilder** - Combines brief + brand profile into GPT prompt
4. **GPTClient** - Generates post text via OpenAI API
5. **PostGenerator** - Orchestrates the generation flow
6. **ThreadsAPI** - Posts content to Threads (currently only supports posting, not fetching)

---

## Proposed Architecture (Phase 1: Basic Post Analysis)

### Dual Generation Modes (A/B Choice)

The system will support two parallel generation paths. Users can choose between:

- **Path A: Notion Briefs** (Default) - Generate from Notion database briefs
- **Path B: Post Analysis** (Alternative) - Generate by analyzing past posts

### Path A: Notion Briefs Flow (Default - Unchanged)

```
┌─────────────────┐
│  Notion Client  │
│  (Briefs DB)    │
└────────┬────────┘
         │
         │ Fetch Briefs
         ▼
┌─────────────────┐
│ PostGenerator   │
│                 │
│  ┌───────────┐  │
│  │ Brand     │  │
│  │ Profile   │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Prompt    │  │
│  │ Builder   │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │
         │ Build Prompt
         ▼
┌─────────────────┐
│   GPT Client    │
│  (OpenAI API)   │
└────────┬────────┘
         │
         │ Generated Text
         ▼
┌─────────────────┐
│   Validation    │
│  (Length, etc)  │
└────────┬────────┘
         │
         │ Valid Post
         ▼
┌─────────────────┐
│  User Approval  │
└────────┬────────┘
         │
         │ Approved
         ▼
┌─────────────────┐
│  Threads API    │
│   (Post)        │
└─────────────────┘
```

### Path B: Post Analysis Flow (Alternative)

```
┌─────────────────┐
│  Threads API    │
│  (Fetch Posts)  │
└────────┬────────┘
         │
         │ Fetch User's Posts
         ▼
┌─────────────────┐
│ PostAnalyzer    │
│                 │
│  • Extract      │
│    patterns     │
│  • Analyze      │
│    structure    │
│  • Identify     │
│    style        │
└────────┬────────┘
         │
         │ Analysis Results
         ▼
┌─────────────────┐
│ PostGenerator   │
│                 │
│  ┌───────────┐  │
│  │ Brand     │  │
│  │ Profile   │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Prompt    │  │
│  │ Builder   │  │
│  │ (Style-   │  │
│  │  Based)   │  │
│  └─────┬─────┘  │
└────────┼────────┘
         │
         │ Style-Based Prompt
         ▼
┌─────────────────┐
│   GPT Client    │
│  (OpenAI API)   │
└────────┬────────┘
         │
         │ Generated Text
         ▼
┌─────────────────┐
│   Validation    │
│  (Length, etc)  │
└────────┬────────┘
         │
         │ Valid Post
         ▼
┌─────────────────┐
│  User Approval  │
└────────┬────────┘
         │
         │ Approved
         ▼
┌─────────────────┐
│  Threads API    │
│   (Post)        │
└─────────────────┘
```

### Mode Selection Logic

```
User selects generation mode:
│
├─── Mode A: Notion Briefs (--mode briefs or default)
│    │
│    └───> Use existing flow (Path A)
│
└─── Mode B: Post Analysis (--mode analysis)
     │
     └───> Use new analysis flow (Path B)
```

---

## Logic Flow: Post Analysis & Generation

### Mode Selection

**User Choice:**
```
IF --mode briefs OR no mode specified:
    USE Path A: Notion Briefs (default flow)
ELSE IF --mode analysis:
    USE Path B: Post Analysis (new flow)
```

### Path A: Notion Briefs Flow (Default)

This flow remains **unchanged** from the current implementation:
1. Fetch briefs from Notion
2. Build prompt with brief + brand profile
3. Generate post via GPT
4. Validate and approve
5. Post to Threads

### Path B: Post Analysis Flow (Alternative)

#### Step 1: Fetch User's Past Posts

**Decision Point:** Should we fetch posts every time, or cache them?

**Logic:**
```
IF mode == "analysis":
    IF cached_analysis exists AND cache_age < threshold:
        USE cached_analysis
    ELSE:
        CALL ThreadsAPI.get_user_threads(limit=25)
        IF posts_fetched:
            STORE posts in memory
            PROCEED to analysis
        ELSE:
            LOG error: "Could not fetch posts for analysis"
            EXIT with error (no fallback - user chose analysis mode)
```

**Considerations:**
- API rate limits (how many posts can we fetch?)
- Cache strategy (in-memory vs file-based)
- Error handling (if analysis fails, should we fallback to briefs or error out?)

---

#### Step 2: Analyze Post Patterns (Path B Only)

**What to Extract:**

1. **Structural Patterns**
   - Average post length
   - Use of bullets/lists (•, →, etc.)
   - Paragraph breaks
   - Numbered lists

2. **Content Patterns**
   - Common opening phrases/sentences
   - Common ending patterns (questions, CTAs)
   - Question frequency
   - Direct vs conversational tone

3. **Style Indicators**
   - First/second person usage
   - Sentence structure (short vs long)
   - Use of specific symbols
   - Formatting preferences

**Analysis Logic:**
```
FOR each post in posts:
    EXTRACT text content
    ANALYZE structure (bullets, breaks, length)
    EXTRACT first sentence (opening pattern)
    EXTRACT last sentence (ending pattern)
    COUNT questions
    DETECT tone indicators

AGGREGATE results:
    CALCULATE averages (length, question frequency)
    IDENTIFY top 5 opening patterns
    IDENTIFY top 5 ending patterns
    IDENTIFY structural preferences
    SELECT top 5 example posts

RETURN analysis dictionary
```

**Analysis Output Structure:**
```json
{
    "avg_length": 387,
    "common_starters": [
        "Digital transformation doesn't start with...",
        "A website is not a...",
        ...
    ],
    "common_endings": [
        "Where does your data actually go?",
        "Build the system first...",
        ...
    ],
    "structure_patterns": {
        "uses_bullets": 0.6,  // 60% of posts use bullets
        "uses_questions": 0.8,  // 80% end with questions
        "uses_numbers": 0.2,
        "paragraph_breaks": 0.4
    },
    "tone_indicators": {
        "conversational": 0.7,
        "direct": 0.5,
        "question_heavy": 0.3
    },
    "example_posts": [
        "Full post text 1...",
        "Full post text 2...",
        ...
    ]
}
```

---

#### Step 3: Build Style-Based Prompt (Path B Only)

**Prompt Building Logic:**
```
IF mode == "analysis":
    BASE_PROMPT = build_style_prompt(post_analysis, brand_profile)
    
    ADD section: "STYLE EXAMPLES TO MATCH"
    ADD top 5 example posts
    ADD common opening patterns
    ADD common ending patterns
    ADD structural preferences
    ADD instruction: "Generate a post matching this style"
    
    RETURN style_based_prompt
```

**Prompt Structure (Path B):**
```
Brand Context:
[Brand Profile Content]

📝 STYLE EXAMPLES TO MATCH:
Generate a post that matches the style, tone, and structure of these examples:

Example 1:
[Post text 1]

Example 2:
[Post text 2]
...

Common opening patterns:
• [Pattern 1]
• [Pattern 2]

Common ending patterns:
• [Pattern 1]
• [Pattern 2]

Structure preferences:
• Often uses bullet points
• Frequently ends with questions

Match the writing style, tone, and structure while creating original content.

[Standard Requirements: length, no emojis, etc.]
```

**Note:** Path B does NOT use Notion briefs - it generates posts purely based on style analysis.

---

#### Step 4: Generate Post

**Generation Logic (Both Paths):**
```
IF mode == "briefs":
    PROMPT = build_post_prompt(brief, brand_profile)
ELSE IF mode == "analysis":
    PROMPT = build_style_prompt(post_analysis, brand_profile)

CALL GPTClient.generate_post(prompt)

IF generation_successful:
    VALIDATE content (length, format)
    IF valid:
        RETURN generated_post
    ELSE:
        IF length_error AND retry_enabled:
            RETRY with stricter length requirements
        ELSE:
            RETURN error
ELSE:
    RETURN error
```

**Key Difference:**
- **Path A:** Prompt includes brief topic/content from Notion
- **Path B:** Prompt includes style examples but no specific topic (GPT generates topic based on style)

---

## Use Cases & Decision Points

### Use Case 1: User Chooses Notion Briefs Mode (Path A - Default)

**Scenario:** User wants to generate posts from Notion database briefs

**Logic:**
```
User runs: python scripts/generate_and_post.py --mode briefs
OR: python scripts/generate_and_post.py (default)

SYSTEM:
    FETCH briefs from Notion
    FOR each brief:
        BUILD prompt (brief + brand profile)
        GENERATE post
        VALIDATE
        PRESENT for approval
```

**Behavior:** Works exactly as current system - no changes

---

### Use Case 2: User Chooses Post Analysis Mode (Path B)

**Scenario:** User wants to generate posts by analyzing their past posts

**Logic:**
```
User runs: python scripts/generate_and_post.py --mode analysis

SYSTEM:
    FETCH user's past posts from Threads API
    IF posts_fetched:
        ANALYZE posts for patterns
        BUILD style-based prompt (analysis + brand profile)
        GENERATE post (no brief needed)
        VALIDATE
        PRESENT for approval
    ELSE:
        ERROR: "Could not fetch posts. Use --mode briefs instead."
```

**Behavior:** Completely separate flow - does not use Notion briefs

---

### Use Case 3: First-Time User (No Past Posts) - Path B

**Scenario:** User chooses analysis mode but has no posts yet

**Logic:**
```
IF mode == "analysis" AND posts_fetched is empty:
    ERROR: "No past posts found. Cannot use analysis mode."
    SUGGEST: "Use --mode briefs to generate from Notion briefs instead"
    EXIT
```

**No Fallback:** User must choose a different mode

---

### Use Case 4: User with 5-10 Posts - Path B

**Scenario:** Limited post history in analysis mode

**Logic:**
```
IF mode == "analysis" AND post_count < 10:
    ANALYZE all available posts
    USE all posts as examples (no filtering)
    APPLY analysis with lower confidence thresholds
    WARN: "Limited post history - patterns may be less reliable"
```

**Consideration:** With fewer posts, patterns may be less reliable, but still proceed

---

### Use Case 5: User with 25+ Posts - Path B

**Scenario:** Rich post history in analysis mode

**Logic:**
```
IF mode == "analysis" AND post_count >= 25:
    ANALYZE top 25 most recent posts
    IDENTIFY strongest patterns
    USE top 5 examples (most representative)
    APPLY analysis with higher confidence
```

**Consideration:** Recent posts may be more relevant than older ones

---

### Use Case 6: API Limitations - Path B

**Scenario:** Threads API doesn't support fetching posts (or requires different permissions)

**Logic:**
```
IF mode == "analysis" AND API_call_fails:
    CHECK error_type:
        IF permission_error:
            ERROR: "threads_basic permission required for analysis mode"
            SUGGEST: "Update API permissions or use --mode briefs"
        IF endpoint_not_found:
            ERROR: "Post fetching not supported by API"
            SUGGEST: "Use --mode briefs instead"
        IF rate_limit:
            WAIT with exponential backoff
            RETRY up to 3 times
            IF still failing:
                ERROR: "Rate limit exceeded. Try again later."
```

**No Fallback:** User must fix API issue or use briefs mode

---

## Architecture Decisions

### Decision 1: When to Fetch Posts?

**Option A: On-Demand (Every Generation)**
- **Pros:** Always fresh, reflects latest style
- **Cons:** API calls every time, slower, rate limits

**Option B: Cached (Fetch Once, Reuse)**
- **Pros:** Faster, fewer API calls
- **Cons:** May become stale, need cache invalidation logic

**Recommendation:** **Hybrid Approach**
- Fetch on first use
- Cache in memory for session
- Optional: Cache to file with timestamp
- Refresh if cache_age > 24 hours OR user requests refresh

---

### Decision 2: How Many Posts to Analyze?

**Option A: Fixed Number (25)**
- Simple, predictable
- May miss patterns in larger history

**Option B: All Available**
- More comprehensive
- Slower, may include outdated style

**Option C: Time-Based (Last 30 days)**
- Most relevant, reflects current style
- Requires date filtering (if API supports it)

**Recommendation:** **Start with Fixed (25), Scale to Time-Based**
- Phase 1: Analyze last 25 posts
- Phase 2: Add date filtering if API supports
- Phase 3: Add smart selection (most engaged posts)

---

### Decision 3: Analysis Granularity

**Option A: Simple (Basic Patterns Only)**
- Opening/ending phrases
- Structure preferences
- Example posts

**Option B: Advanced (Deep Analysis)**
- Sentiment analysis
- Topic clustering
- Engagement correlation
- Writing style metrics

**Recommendation:** **Start Simple, Build Up**
- Phase 1: Basic patterns (openings, endings, structure)
- Phase 2: Add tone analysis
- Phase 3: Add engagement-based weighting (if data available)

---

### Decision 4: Prompt Integration Strategy

**Option A: Append Examples**
- Add examples at end of prompt
- Simple, clear

**Option B: Interleave Context**
- Mix style context throughout prompt
- More complex, may confuse GPT

**Option C: Separate Style Section**
- Dedicated "Style Matching" section
- Clear separation, easy to debug

**Recommendation:** **Option C (Separate Section)**
- Clear structure
- Easy to enable/disable
- Simple to debug and iterate

---

## Scalability Considerations

### Future Enhancements (Not Phase 1)

1. **Multi-User Analysis**
   - Analyze posts from multiple accounts
   - Compare styles
   - Learn from top performers

2. **Engagement-Based Analysis**
   - Weight analysis by post engagement
   - Learn what works, not just what exists
   - Requires engagement metrics from API

3. **Topic-Specific Style**
   - Different styles for different topics
   - Match style to brief topic/pillar
   - Requires topic classification

4. **Temporal Style Evolution**
   - Track style changes over time
   - Adapt to recent trends
   - Detect style drift

5. **Competitor Analysis**
   - Analyze competitor posts
   - Learn successful patterns
   - Requires public API access

6. **A/B Testing Integration**
   - Test different style matches
   - Measure performance
   - Optimize generation

---

## Error Handling & Edge Cases

### Edge Case 1: No Posts Available (Path B)

**Handling:**
```
IF mode == "analysis" AND posts_fetched is empty:
    ERROR: "No posts found. Cannot use analysis mode."
    EXIT with clear error message
    SUGGEST: Use --mode briefs instead
```

**Note:** Path A (briefs) is unaffected - this only applies to analysis mode

---

### Edge Case 2: All Posts Too Short/Long

**Handling:**
```
IF avg_length < 100 OR avg_length > 500:
    LOG: "Post length patterns may not be reliable"
    USE brand profile length guidelines instead
    STILL use style patterns (openings, endings)
```

---

### Edge Case 3: Inconsistent Style

**Handling:**
```
IF style_variance is high:
    USE most common patterns only
    FOCUS on structural preferences
    REDUCE reliance on specific phrases
```

---

### Edge Case 4: API Rate Limits

**Handling:**
```
IF rate_limit_error:
    WAIT with exponential backoff
    RETRY up to 3 times
    IF still failing:
        USE cached analysis if available
        OR fallback to standard generation
```

---

## Implementation Phases

### Phase 1: Basic Post Analysis (Start Here)

**Scope:**
- **Keep Path A unchanged** - No modifications to existing brief-based flow
- **Add Path B** - New analysis-based generation mode
- Fetch user's last 25 posts (Path B only)
- Extract basic patterns (openings, endings, structure)
- Build style-based prompts (Path B only)
- Simple caching (in-memory)

**Components:**
1. `ThreadsAPI.get_user_threads()` - Fetch posts (Path B)
2. `PostAnalyzer` - Analyze patterns (Path B)
3. `PromptBuilder.build_style_prompt()` - Style-based prompt (Path B)
4. `PostGenerator.generate_from_analysis()` - Analysis generation method (Path B)
5. CLI mode selection: `--mode briefs` or `--mode analysis`

**Testing:**
- **Path A:** Ensure no regressions (existing tests should pass)
- **Path B:** Test with user who has posts
- **Path B:** Test with user who has no posts (should error clearly)
- **Path B:** Test with API limitations (mock failures, clear errors)
- **Mode Selection:** Test CLI flag parsing

---

### Phase 2: Enhanced Analysis

**Scope:**
- Add tone analysis
- Add engagement weighting (if available)
- File-based caching
- Cache invalidation

---

### Phase 3: Advanced Features

**Scope:**
- Topic-specific styles
- Temporal analysis
- Multi-account support

---

## Data Flow Diagram

### Path A: Notion Briefs Flow

```
┌──────────────┐
│ User Action  │
│ --mode briefs│
│ (or default) │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│  Notion Client  │
│  Fetch Briefs   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ PostGenerator    │
│ (Brief Mode)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ PromptBuilder    │
│ (Brief + Brand)  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ GPTClient        │
│ .generate()     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Generated Post  │
│ (From Brief)    │
└─────────────────┘
```

### Path B: Post Analysis Flow

```
┌──────────────┐
│ User Action  │
│ --mode       │
│ analysis     │
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│ ThreadsAPI      │
│ .get_user_      │
│  threads(25)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ PostAnalyzer    │
│ .analyze_posts()│
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Analysis Dict   │
│ (patterns,      │
│  examples)      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ PostGenerator   │
│ (Analysis Mode) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ PromptBuilder   │
│ (Style + Brand) │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ GPTClient       │
│ .generate()     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Generated Post  │
│ (Style-Matched) │
└─────────────────┘
```

### Mode Selection

```
┌──────────────┐
│ User Command │
└──────┬───────┘
       │
       ├─── --mode briefs ────> Path A
       │
       ├─── --mode analysis ───> Path B
       │
       └─── (no mode) ──────────> Path A (default)
```

---

## Key Questions to Resolve

1. **API Capabilities:**
   - Does Threads API support fetching user's own posts?
   - What permissions are required? (`threads_basic`?)
   - What's the rate limit?
   - What fields are available? (text, date, engagement?)

2. **Caching Strategy:**
   - In-memory only? Or file-based?
   - How long to cache? (24 hours? Session-based?)
   - Cache invalidation trigger?

3. **Mode Selection:**
   - CLI flag: `--mode briefs` vs `--mode analysis`
   - Default to briefs mode
   - Clear error messages if analysis mode fails

4. **Analysis Depth:**
   - Start with basic patterns only?
   - Or include tone/sentiment from day one?

5. **User Control:**
   - CLI flag: `--mode briefs` (default) or `--mode analysis`
   - Clear documentation of what each mode does
   - Future: Allow custom example files for analysis mode?

---

## Recommendations for Phase 1

### Start Small, Build Smart

1. **Keep Path A Unchanged:**
   - Path A (Notion Briefs) remains exactly as it is today
   - No modifications to existing brief-based generation
   - Default behavior unchanged

2. **Build Path B as Separate Mode:**
   - New `PostAnalyzer` class (single responsibility)
   - New `PromptBuilder.build_style_prompt()` method (separate from brief prompt)
   - New `PostGenerator.generate_from_analysis()` method
   - Clear separation between Path A and Path B

3. **Minimal Viable Analysis (Path B):**
   - Fetch last 25 posts
   - Extract: openings, endings, structure preferences
   - Include top 5 examples in prompt
   - In-memory caching only

4. **Error Handling (Path B):**
   - If fetching fails → clear error message, suggest using Path A
   - If analysis fails → clear error message, exit gracefully
   - No silent fallbacks - user chose analysis mode for a reason

5. **Simple Architecture:**
   - Mode selection via CLI flag: `--mode briefs` or `--mode analysis`
   - Default to `briefs` if no mode specified
   - Clear separation of concerns between modes

6. **Testing Strategy:**
   - Test Path A (ensure no regressions)
   - Test Path B with real API (if available)
   - Test Path B with mocked API responses
   - Test Path B error scenarios (no posts, API failures)
   - Test with 0, 5, 25, 50 posts

7. **User Experience:**
   - Clear CLI documentation for both modes
   - Show which mode is being used in logs
   - For Path B: Show analysis summary in logs
   - Clear error messages with suggestions

---

## Next Steps

1. **Verify API Capabilities:**
   - Test `GET /me/threads` endpoint
   - Check required permissions
   - Document available fields

2. **Design PostAnalyzer Interface:**
   - Define input/output structure
   - Plan analysis algorithms
   - Design caching interface

3. **Plan Prompt Enhancement:**
   - Design prompt section structure
   - Test with GPT to ensure clarity
   - Iterate on example formatting

4. **Build Incrementally:**
   - Start with fetching only
   - Add basic analysis
   - Integrate with prompt
   - Test end-to-end

---

## Summary

This architecture keeps the system simple for Phase 1 while leaving room for future enhancements. The key is starting with basic pattern extraction and style matching, then building more sophisticated analysis as we learn what works.

**Core Principles:**
1. **Path A (Briefs) remains unchanged** - Default behavior is preserved
2. **Path B (Analysis) is a separate, optional mode** - Users explicitly choose it
3. **Clear error handling** - If Path B fails, provide clear errors and suggestions
4. **No silent fallbacks** - User chose analysis mode for a reason, don't silently switch to briefs

