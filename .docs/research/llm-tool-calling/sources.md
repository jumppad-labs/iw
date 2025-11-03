# Sources for llm-tool-calling

**Last Updated**: 2025-11-03

## Academic Papers

1. **[Yao et al., 2022] "ReAct: Synergizing Reasoning and Acting in Language Models"**
   - URL: https://arxiv.org/abs/2210.03629
   - Published: October 6, 2022 (final v3: March 10, 2023)
   - Key Contribution: Introduced interleaved reasoning and action approach for LLMs to interface with external tools

2. **[Schick et al., 2023] "Toolformer: Language Models Can Teach Themselves to Use Tools"**
   - URL: https://arxiv.org/abs/2302.04761
   - Published: February 9, 2023 (Meta AI, presented at NeurIPS 2023)
   - Key Contribution: Self-supervised learning approach for LLMs to learn tool use with minimal demonstrations

3. **[Nakano et al., 2021] "WebGPT: Browser-assisted question-answering with human feedback"**
   - URL: https://arxiv.org/abs/2112.09332
   - Published: December 17, 2021 (OpenAI)
   - Key Contribution: Early implementation of LLM with web browsing capabilities using text-based environment

4. **[Parisi et al., 2022] "TALM: Tool Augmented Language Models"**
   - URL: https://arxiv.org/abs/2205.12255
   - Published: May 24, 2022
   - Key Contribution: Text-only approach to augment LMs with non-differentiable tools using iterative self-play

## Technical Documentation - OpenAI

5. **OpenAI Function Calling Documentation**
   - URL: https://platform.openai.com/docs/guides/function-calling
   - Current as of 2025
   - Content: Official API documentation for function calling with GPT-4 and GPT-3.5-Turbo

6. **OpenAI Function Calling Announcement (June 2023)**
   - URL: https://openai.com/index/function-calling-and-other-api-updates/
   - Date: June 13, 2023
   - Content: Original announcement introducing function calling for gpt-4-0613 and gpt-3.5-turbo-0613

## Technical Documentation - Anthropic

7. **Claude Tool Use Documentation**
   - URL: https://docs.claude.com/en/docs/build-with-claude/tool-use
   - Current as of 2025
   - Content: Official documentation for Claude's tool use API, including client and server tools

8. **Claude API Release Notes**
   - URL: https://docs.claude.com/en/release-notes/api
   - Current as of 2025
   - Content: Recent updates including Agent Skills, fine-grained tool streaming, tool use clearing

## Technical Documentation - Google

9. **Gemini Function Calling Documentation**
   - URL: https://ai.google.dev/gemini-api/docs/function-calling
   - Current as of 2025
   - Content: Official Gemini API documentation for function calling with control modes (AUTO, ANY, NONE, VALIDATED)

10. **Gemini 2.X Simplified Function Calling**
    - URL: https://atamel.dev/posts/2025/04-08_simplified_function_calling_gemini/
    - Date: April 8, 2025
    - Content: Analysis of simplified function calling in Gemini 2.X models

## Open-Source Models

11. **Meta Llama 3.1 Announcement**
    - URL: https://ai.meta.com/blog/meta-llama-3-1/
    - Date: 2024
    - Content: Introduction of Llama 3.1 with native function calling support

12. **Mistral Function Calling Documentation**
    - URL: https://docs.mistral.ai/capabilities/function_calling
    - Current as of 2024
    - Content: Official Mistral AI documentation for function calling capabilities

## Technical Articles and Guides

13. **"How to build function calling and JSON mode for open-source and fine-tuned LLMs"**
    - URL: https://www.baseten.co/blog/how-to-build-function-calling-and-json-mode-for-open-source-and-fine-tuned-llms/
    - Content: Technical explanation of structured output generation mechanisms (logit biasing, token masking)

14. **"How JSON Schema Works for LLM Tools & Structured Outputs"**
    - URL: https://blog.promptlayer.com/how-json-schema-works-for-structured-outputs-and-tool-integration/
    - Content: Detailed explanation of JSON Schema as a standard for tool definitions

15. **"Fine Tuning LLMs for Function Calling"**
    - URL: https://parlance-labs.com/education/fine_tuning/pawel.html
    - Date: 2024
    - Content: Comprehensive guide on training methodologies for function calling

16. **"Enhancing Function-Calling Capabilities in LLMs" (arXiv paper)**
    - URL: https://arxiv.org/html/2412.01130v2
    - Date: December 2024
    - Content: Recent research on strategies for prompt formats, data integration, and multilingual translation

## Community Resources

17. **awesome-llm-json (GitHub)**
    - URL: https://github.com/imaurer/awesome-llm-json
    - Content: Curated resource list for generating JSON using LLMs via function calling, tools, CFG

18. **Google Gemini Cookbook - Function Calling**
    - URL: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb
    - Content: Practical examples and implementation patterns for Gemini function calling
