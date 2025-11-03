# Research Findings: llm-tool-calling

**Last Updated**: 2025-11-03

---

## Theme 1: Historical Evolution of Tool Calling in LLMs

### Early Foundations (2021-2022)

#### WebGPT - December 2021 (Source #3)
- **First major implementation**: OpenAI's WebGPT fine-tuned GPT-3 to use a text-based web-browsing environment
- **Approach**: Model learned through imitation learning and human feedback to search and navigate the web
- **Performance**: Answers preferred by humans 56% vs human demonstrators, 69% vs top Reddit answers
- **Significance**: Demonstrated LLMs could learn to use external tools effectively with proper training

#### TALM - May 2022 (Source #4)
- **Innovation**: Tool Augmented Language Models combined text-only approach with non-differentiable tools
- **Training method**: Iterative "self-play" technique to bootstrap performance from few tool demonstrations
- **Key achievement**: Enabled out-of-distribution inferences where non-augmented LMs failed
- **Problem addressed**: Access to ephemeral, changing, or private data unavailable at training time

#### ReAct - October 2022 (Source #1)
- **Core concept**: Interleaved reasoning traces and actions in a synergistic cycle
- **Reasoning traces**: Help model induce, track, and update action plans while handling exceptions
- **Actions**: Allow interfacing with external sources (knowledge bases, APIs, environments)
- **Results**: 34% and 10% improvement over baselines on ALFWorld and WebShop with only 1-2 examples
- **Impact**: Addressed hallucination and error propagation in chain-of-thought reasoning

#### Toolformer - February 2023 (Source #2)
- **Breakthrough**: Self-supervised learning for tool use requiring only "handful of demonstrations for each API"
- **Autonomy**: Model learns independently when to call tools, what arguments to use, and how to incorporate results
- **Tools integrated**: Calculator, Q&A system, search engines, translation, calendar
- **Performance**: Substantially improved zero-shot performance, competitive with much larger models
- **Key distinction**: No extensive task-specific supervision or human-annotated examples required

### Commercial Implementation Era (2023-2024)

#### OpenAI Function Calling - June 13, 2023 (Source #6)
- **Models**: gpt-4-0613 and gpt-3.5-turbo-0613 introduced with function calling
- **Method**: Models fine-tuned to detect when functions needed and respond with JSON adhering to function signature
- **Impact**: "New way to more reliably connect GPT's capabilities with external tools and APIs"
- **Use cases**: Chatbots calling external tools, natural language to function calls, structured data extraction
- **Additional benefits**: 75% cost reduction on embeddings, 25% on gpt-3.5-turbo input tokens

#### Open-Source Adoption - 2024 (Sources #11, #12)
- **Mistral (March 2024)**: Integrated parallel function calling support into models
- **Mistral 7B v0.3**: Function calling available out-of-the-box for open-source LLMs
- **Llama 3.1 (2024)**: Native function calling support in 8B, 70B, and 405B models
- **Llama 3.1 features**: 128K context length, multilingual, state-of-the-art tool use
- **Significance**: First openly available model (405B) rivaling top proprietary models for tool use

### Current State (2025)

#### Anthropic Claude Updates (Source #8)
- **January 2025**: Released bash_20250124 and text_editor_20250124 independent from computer use
- **October 2025**: Launched Agent Skills (skills-2025-10-02 beta) - organized folders of instructions and scripts
- **Advanced features**: Fine-grained tool streaming, tool use clearing, context management

#### Google Gemini Evolution (Source #10)
- **Gemini 2.X simplification**: No need for special function declarations, just pass functions with comments
- **Previous workflow eliminated**: No manual API call handling and response cycling required
- **Automatic function calling**: Python SDK handles everything automatically
- **Thinking mode**: Improved function call performance through reasoning before suggesting calls

---

## Theme 2: Technical Mechanisms - How It Works

### Structured Output Generation (Source #13)

#### Token-Level Control
- **Logit biasing**: First step to guarantee valid tokens are generated
- **Process**: Each logit is a score representing likelihood of next token from vocabulary
- **Token masking**: Schema built into state machine, masks invalid tokens at each generation step
- **Result**: Ensures output conforms to JSON structure requirements

#### State Machine Approach
- **Schema parsing**: When schema added to LLM call, model server builds it into state machine
- **Vocabulary filtering**: Most vocabulary tokens invalid at certain points during structured generation
- **Progressive constraint**: Each token choice narrows available next tokens based on schema

### Fine-Tuning Methodology (Source #15)

#### Training Approaches
- **Base vs instruction-tuned**: Fine-tune on instruction-tuned models to preserve general capabilities
- **Exception**: Base models acceptable for forced function-calling scenarios without general chat needs
- **LoRA (Low-Rank Adaptation)**: Sufficient for function-tuning, applied on linear layers
- **Resource efficiency**: LoRA preferred for limited data, faster iterations, less resource demand
- **Example timing**: Qwen2.5-Coder-7B-Instruct fine-tuned in ~5 hours on four A10 GPUs (24GB VRAM each)

#### Function Output Format Choices
- **Python syntax**: Easier for models trained extensively with Python
- **JSON schema**: Better for complex nested parameter types and OpenAI API compatibility
- **Special tokens**: "function call" token can be added to vocabulary for easier parsing and constrained generation

#### Training Data Requirements
- **Balanced distribution**: Even distribution prevents overusing or ignoring specific functions
- **Sufficient examples**: Model must see enough to generalize function invocation correctly
- **Instruction integration**: Combining instruction-following data with function-calling tasks significantly enhances capabilities
- **Performance results**: Fine-tuned models can surpass GPT-4 and GPT-4o in structural completeness, tool selection accuracy, and parameter accuracy

### Model Decision-Making

#### How Models Choose to Call Tools
- **Fine-tuning approach**: Models specifically trained to recognize when tool use would help
- **Pattern recognition**: Learns from training data which queries benefit from external tools
- **Confidence signaling**: Outputs specific format (tool_use block, function call JSON) when deciding to use tool
- **Multiple tools**: Can select most appropriate tool from available options based on query

#### Reasoning vs Acting (Source #1)
- **Interleaved cycle**: Reasoning traces and actions work synergistically, not separately
- **Reasoning enables**: Inducing action plans, tracking progress, updating plans, handling exceptions
- **Actions enable**: Gathering fresh information from external sources to inform reasoning
- **Result**: Human-like task-solving trajectories superior to reasoning-only approaches

---

## Theme 3: Current Standards and Formats

### JSON Schema as Universal Standard (Source #14)

#### Purpose and Benefits
- **Definition**: Vocabulary for describing structure and content of JSON data
- **Acts as blueprint**: Specifies data types, required fields, format constraints, validation rules
- **Common language**: Ensures seamless data exchange between LLM and tools
- **Predictability**: Makes LLM output conform to specific format, machine-readable and predictable
- **De facto standard**: Supported by OpenAI, Anthropic, Google, and open-source models

#### Implementation
- **Function description**: Describe functions in API calls using JSON schema for arguments
- **Developer control**: Define schemas for input parameters to control structure and content
- **Automated generation**: Python introspection + Pydantic can automatically generate schemas from function signatures
- **Consistency**: Minimizes manual effort while maintaining consistency

### OpenAI Function Calling Format (Sources #5, #6)

#### Function Definition Structure
- **name**: Identifier for the function
- **description**: Clear explanation of what function does
- **parameters**: JSON Schema object defining inputs
  - type: Data type of parameter
  - properties: Detailed parameter definitions
  - required: Array of mandatory parameter names
- **Fine-tuned models**: gpt-4-0613 and gpt-3.5-turbo-0613 specifically trained for this format

#### Response Format
- Model outputs JSON object with:
  - Function name to call
  - Arguments as JSON object adhering to defined schema
- Stop reason indicates function call intent
- Developer executes function and returns results
- Model uses results to formulate final response

### Anthropic Claude Tool Use Format (Source #7)

#### Tool Definition Structure
```
tools: [
  {
    name: "tool_identifier",
    description: "What the tool does",
    input_schema: {
      type: "object",
      properties: {...},
      required: [...]
    }
  }
]
```

#### Unique Features
- **Versioned tools**: e.g., web_search_20250305 for compatibility
- **Client tools**: Developer executes, returns results via tool_result blocks
- **Server tools**: Claude executes automatically, results incorporated in response
- **stop_reason**: Value of `tool_use` signals intent to use tool
- **Parallel execution**: Multiple tools can be called simultaneously
- **Sequential chaining**: Tools can depend on prior results

### Google Gemini Function Calling Format (Source #9)

#### Declaration Format
- **Subset of OpenAPI schema**: Uses select OpenAPI schema format elements
- **Required fields**: name, description, parameters object
- **Parameters**: Define inputs with type, description, optional enum constraints
- **Example properties**: brightness (integer), color_temp (string with enum)

#### Control Modes (function_calling_config)
1. **AUTO (Default)**: Model decides between natural language or function call
2. **ANY**: Model constrained to always predict function call, guaranteed schema adherence
   - Optional: allowed_function_names filtering
3. **NONE**: Model prohibited from making function calls
4. **VALIDATED (Preview)**: Predicts function calls or natural language while ensuring schema compliance

#### Advanced Capabilities
- **Automatic function calling (Python only)**: Pass Python functions directly as tools
  - SDK converts functions to declarations automatically
  - Executes function calls when requested
  - Handles response cycling without manual intervention
- **Parallel calling**: Multiple functions at once for independent operations
- **Compositional calling**: Sequential chaining where one output feeds another input

### JSON Mode vs Function Calling (Sources #13, #14)

#### JSON Mode
- **Purpose**: LLM guaranteed to return JSON in specified format
- **Use case**: Structured output for data extraction, formatting
- **Control**: Developer dictates format and data types of response
- **No function selection**: Model doesn't choose which function to call

#### Function Calling
- **Purpose**: LLM intelligently outputs JSON containing arguments for external functions
- **Use case**: Real-time data access, dynamic tool selection
- **Intelligence**: Model decides when and which function to call
- **Integration**: Connects LLM capabilities with external tools and APIs

---

## Theme 4: Provider-Specific Implementations

### OpenAI Approach (Sources #5, #6)

#### Key Characteristics
- **Function-centric**: Terminology emphasizes "functions" over "tools"
- **Fine-tuned models**: Specifically trained on function calling format
- **JSON output**: Model generates function call as JSON with name and arguments
- **Developer executes**: Application code responsible for actual function execution
- **Reliability improvement**: "More reliably connect GPT's capabilities" compared to prompt-only approaches
- **Model versions**: gpt-4-0613, gpt-3.5-turbo-0613 and later

#### Workflow
1. Developer provides function definitions with schemas
2. User sends query
3. Model decides if function call needed
4. Model outputs JSON with function name and arguments
5. Developer executes function with provided arguments
6. Developer sends results back to model
7. Model formulates final response to user

### Anthropic Claude Approach (Sources #7, #8)

#### Key Characteristics
- **Tool-centric**: Terminology uses "tools" rather than "functions"
- **Dual execution model**: Both client tools and server tools
- **Server tools unique**: Anthropic executes tools like web_search directly
- **Versioned tools**: Tools have version identifiers for stability (e.g., web_search_20250305)
- **Agent Skills**: Organized folders of instructions, scripts, and resources loaded dynamically
- **Fine-grained streaming**: Tool calls can be streamed at individual granularity

#### Client Tool Workflow
1. Developer provides tools via tools parameter
2. Claude assesses if tools can help with query
3. API returns stop_reason of tool_use with tool_use content blocks
4. Developer executes tool and returns tool_result blocks
5. Claude uses results to formulate response

#### Server Tool Workflow
1. Developer specifies server tools in request
2. Claude assesses if server tool can help
3. Claude executes tool automatically (e.g., web search)
4. Results automatically incorporated into response
5. No developer execution step required

#### Advanced Features (2025)
- **Tool use clearing**: Context management for long conversations (context-management-2025-06-27)
- **Fine-grained streaming**: Stream tool parameters without buffering or JSON validation
- **Agent Skills**: Specialized capabilities organized as skill packages

### Google Gemini Approach (Sources #9, #10)

#### Key Characteristics
- **OpenAPI compatibility**: JSON Schema compatible, Python function definitions with docstrings
- **Simplified in 2.X**: Direct function passing with comments, no special declarations
- **Automatic execution (Python)**: SDK feature that handles complete cycle automatically
- **Control modes**: Four distinct modes (AUTO, ANY, NONE, VALIDATED) for fine-grained control
- **Thinking mode**: Optional reasoning step before suggesting function calls

#### Gemini 1.X Workflow (Traditional)
1. Declare functions available to model
2. Create tool of function declarations
3. Pass tool to model and generate content
4. Look for function call requests in responses
5. Make API calls if function call requests found
6. Pass responses back to model
7. Get final text response

#### Gemini 2.X Workflow (Simplified)
1. Declare functions with comments
2. Pass functions directly to model
3. SDK handles detection, execution, and cycling automatically
4. Receive final response

#### Control Mode Use Cases
- **AUTO**: General chatbot interactions, model decides best approach
- **ANY**: Forced tool use, ensure function always called (e.g., structured data extraction)
- **NONE**: Disable tool use temporarily while keeping definitions available
- **VALIDATED**: Ensure schema compliance while allowing natural language fallback

### Open-Source Models (Sources #11, #12)

#### Llama 3.1 (Meta)
- **Native support**: Function calling built-in, no fine-tuning needed
- **Model sizes**: 8B, 70B, 405B all support function calling
- **Context length**: 128K tokens
- **JSON output**: Generates structured JSON for tool calls
- **Chat template**: Specific format for tool calling in 8B model
- **Performance**: 405B rivals top proprietary models for tool use
- **Availability**: AWS, Google Cloud, Azure, Databricks, Groq

#### Mistral Models
- **Official support**: March 13, 2024 - parallel function calling integrated
- **Mistral 7B v0.3**: Function calling out-of-the-box
- **Format**: Structured JSON with function name and arguments
- **Community models**: Fine-tuned versions available on HuggingFace (e.g., Trelis variants)
- **Developer execution**: User responsible for executing functions, model only generates calls
- **Documentation**: Comprehensive official docs at docs.mistral.ai

#### General Open-Source Characteristics
- **July 2024 state**: Strongest open-source models support function calling out-of-the-box
- **Fine-tuning approach**: Community often fine-tunes base models for better function calling
- **JSON generation**: Focus on reliable structured output
- **Provider-specific formats**: Often compatible with OpenAI format for ecosystem compatibility

---

## Theme 5: Workflow Components

### Tool Definition Phase

#### Components Required (Multiple Sources)
- **Tool identifier**: Unique name for the tool
- **Description**: Clear explanation of tool purpose and capabilities
- **Input schema**: JSON Schema defining parameters
  - Parameter names
  - Data types
  - Required vs optional
  - Constraints (enum, ranges, formats)
- **Output specification** (optional): Expected return format

#### Best Practices
- **Clear descriptions**: Model relies on descriptions to choose appropriate tool
- **Specific parameter names**: Use descriptive names (e.g., location_city not loc)
- **Constraints**: Define enums, ranges, patterns to guide model
- **Examples in description**: Include usage examples when helpful
- **Version control**: Use versioned identifiers for stability

### Tool Invocation Phase

#### Model Decision Process
1. **Query analysis**: Model analyzes user request
2. **Tool relevance assessment**: Determines if any tool can help
3. **Tool selection**: Chooses most appropriate tool from available options
4. **Parameter extraction**: Extracts values from query to populate parameters
5. **Validation**: Ensures extracted values match schema constraints
6. **Output generation**: Produces tool call in provider-specific format

#### Multiple Tool Handling
- **Parallel invocation**: Multiple independent tools called simultaneously
- **Sequential chaining**: One tool's output feeds into another's input
- **Conditional calling**: Tools called based on previous results

### Parameter Extraction and Validation

#### Extraction Process (Source #13)
- **Natural language parsing**: Model extracts values from user's natural language query
- **Type conversion**: Converts extracted values to appropriate data types
- **Default values**: Uses defaults when parameters optional and not provided
- **Contextual inference**: Uses conversation context to infer missing values

#### Validation Mechanisms
- **Schema compliance**: Output validated against JSON Schema
- **Type checking**: Ensures data types match schema requirements
- **Required fields**: Verifies all required parameters present
- **Constraint verification**: Checks enums, ranges, patterns
- **Refinement**: Some implementations prompt model to refine if validation fails

### Result Handling Phase

#### Developer Responsibilities
- **Function execution**: Actually run the function with provided arguments
- **Error handling**: Catch and report errors appropriately
- **Result formatting**: Format results for model consumption
- **Context management**: Track tool call history in conversation

#### Model Integration
- **Result incorporation**: Model receives tool results as additional context
- **Synthesis**: Combines tool results with its knowledge to formulate response
- **Citation**: Can reference tool results in final answer
- **Follow-up calls**: May request additional tool calls based on results

### Error Handling and Recovery

#### Common Error Scenarios
- **Invalid parameters**: Model extracts incorrect or incompatible values
- **Tool unavailable**: Requested tool not accessible or times out
- **Execution failure**: Tool runs but returns error
- **Schema violation**: Output doesn't match expected format

#### Recovery Strategies
- **Retry with refinement**: Ask model to correct parameters and try again
- **Fallback**: Model provides answer without tool use
- **Error explanation**: Model explains why tool use failed to user
- **Alternative tools**: Try different tool that might accomplish same goal

---

## Theme 6: Comparative Analysis

### Training Requirements

| Provider | Approach | Training Method |
|----------|----------|----------------|
| OpenAI | Fine-tuned | Models specifically trained on function calling format |
| Anthropic | Fine-tuned | Trained on tool use patterns, both client and server tools |
| Google Gemini | Fine-tuned | Trained to understand JSON Schema and function declarations |
| Llama 3.1 | Native | Built-in support, 405B trained for state-of-the-art tool use |
| Mistral | Native + Fine-tuned | Official support, community fine-tuned variants available |

### Format Compatibility

| Provider | Schema Format | Output Format | Notes |
|----------|--------------|---------------|-------|
| OpenAI | JSON Schema | JSON object | Industry standard format |
| Anthropic | JSON Schema (input_schema) | tool_use blocks | Client/server tool distinction |
| Google Gemini | OpenAPI subset | JSON object | Python function support |
| Llama 3.1 | JSON Schema | JSON object | Often OpenAI-compatible |
| Mistral | JSON Schema | JSON object | OpenAI-compatible format |

### Unique Features Comparison

#### OpenAI
- First major commercial implementation (June 2023)
- Established format widely adopted as de facto standard
- Strong ecosystem and third-party integrations

#### Anthropic Claude
- **Server tools**: Unique execution model where Anthropic runs tools
- **Agent Skills**: Organized skill packages with instructions and scripts
- **Fine-grained streaming**: Stream individual tool call parameters
- **Versioned tools**: Stability through version identifiers

#### Google Gemini
- **Automatic function calling (Python)**: SDK handles complete cycle
- **Control modes**: Fine-grained control (AUTO, ANY, NONE, VALIDATED)
- **Simplified 2.X approach**: Direct function passing without declarations
- **Thinking mode**: Optional reasoning before function calls

#### Llama 3.1
- **Largest open model**: 405B parameters rivals proprietary models
- **True open-source**: No API required, can self-host
- **128K context**: Large context window for complex workflows
- **Multilingual**: Native support for multiple languages

#### Mistral
- **Open-source pioneer**: Early open-source support (March 2024)
- **Parallel calling**: Built-in parallel function calling
- **7B efficiency**: Small model with function calling capability
- **Community ecosystem**: Active fine-tuning community

### Performance Characteristics

#### Reliability (Source #15)
- **Fine-tuned models**: Generally more reliable than prompt-only approaches
- **Structural completeness**: Properly fine-tuned models can exceed GPT-4
- **Tool selection accuracy**: Training significantly improves appropriate tool selection
- **Parameter accuracy**: Fine-tuning improves parameter extraction accuracy

#### Speed and Efficiency
- **Smaller models**: Llama 8B, Mistral 7B faster but potentially less accurate
- **Larger models**: GPT-4, Claude Opus, Llama 405B slower but more reliable
- **Streaming support**: Claude's fine-grained streaming reduces perceived latency
- **Auto-execution**: Gemini Python SDK and Claude server tools reduce round trips

### Use Case Suitability

#### Production APIs (OpenAI, Anthropic, Gemini)
- **Pros**: Reliable, well-documented, actively maintained, no infrastructure needed
- **Cons**: Cost per call, rate limits, data privacy considerations
- **Best for**: Customer-facing applications, rapid prototyping, SaaS products

#### Self-Hosted Open-Source (Llama, Mistral)
- **Pros**: No per-call cost, data privacy, customizable through fine-tuning
- **Cons**: Infrastructure requirements, maintenance burden, potentially lower reliability
- **Best for**: High-volume use, sensitive data, custom tool ecosystems, research

---

## Theme 7: Key Technical Insights for YouTube Presentation

### What Makes Modern Tool Calling Work

#### 1. Fine-Tuning is Critical
- **Early approaches** (WebGPT, TALM): Required extensive human feedback or self-play
- **Modern approaches** (GPT-4, Claude, Gemini): Specifically fine-tuned on tool-calling patterns
- **Result**: Models "understand" when and how to call tools without complex prompting

#### 2. Structured Output Generation
- **Not just prompting**: Models use token-level control (logit biasing, state machines)
- **Schema enforcement**: JSON Schema guides generation at each token
- **Reliability**: Guarantees valid JSON output conforming to specifications

#### 3. JSON Schema as Universal Language
- **Common standard**: All major providers use JSON Schema or compatible formats
- **Interoperability**: Makes switching providers or supporting multiple providers easier
- **Automation**: Enables automatic schema generation from code

#### 4. Evolution from Academic to Commercial
- **Research phase** (2021-2023): Proved LLMs could learn tool use (WebGPT, TALM, ReAct, Toolformer)
- **Commercial phase** (2023-2024): Productized into reliable APIs (OpenAI June 2023)
- **Open-source phase** (2024-2025): Native support in open models (Llama 3.1, Mistral)
- **Timeline**: ~4 years from research to commodity feature

#### 5. Multiple Valid Approaches
- **Execution models**: Client-side (OpenAI, Gemini), server-side (Claude), automatic (Gemini Python)
- **Control levels**: From full auto to forced calling to disabled
- **Trade-offs**: Simplicity vs control, latency vs reliability

### Live Coding Demonstration Opportunities

#### Interception Points in Tool Calling Flow
1. **Request interception**: Capture API call with tool definitions
2. **Response interception**: Capture model's tool call decision (JSON output)
3. **Execution point**: Where tool actually runs (demonstrate custom tool)
4. **Result interception**: Capture tool execution results
5. **Final response**: Model's answer incorporating tool results

#### Key Concepts to Demonstrate
- **Tool definition**: Show JSON Schema for a simple tool
- **Model decision**: Display when model chooses to call vs not call tool
- **Parameter extraction**: Show how model extracts values from natural language
- **JSON format**: Display the actual tool call JSON structure
- **Round-trip flow**: Complete cycle from query → tool call → execution → result → response

#### Example Tools for Demo
- **Weather API**: Classic example, shows external data integration
- **Calculator**: Demonstrates when model defers to tool for precision
- **Database query**: Shows how natural language converts to structured query
- **Custom tool**: Build live to show how easy it is to add new capabilities

### Common Misconceptions to Address

#### Misconception 1: "The LLM executes the function"
- **Reality**: LLM only generates JSON specifying what to call and with what arguments
- **Developer executes**: Application code actually runs the function (except Claude server tools)

#### Misconception 2: "It's just clever prompting"
- **Reality**: Models are specifically fine-tuned on function calling patterns
- **Evidence**: Dedicated model versions (gpt-4-0613), structured output guarantees

#### Misconception 3: "All implementations are the same"
- **Reality**: Significant differences in execution models, control modes, features
- **Examples**: Claude server tools, Gemini auto-execution, OpenAI developer-executes

#### Misconception 4: "Tool calling is simple to implement from scratch"
- **Reality**: Requires careful fine-tuning, structured output generation, validation
- **Why providers offer it**: Difficult to do reliably without proper training data and methodology

### Key Takeaways for Audience

1. **Tool calling bridges LLM limitations**: Enables access to real-time data, computation, external systems
2. **It's a fine-tuned capability**: Not prompt engineering, requires specific model training
3. **JSON Schema is the standard**: Universal format across providers
4. **Multiple execution models exist**: Client-side, server-side, automatic
5. **Open-source is catching up**: Llama 3.1 rivals proprietary models
6. **Rapid evolution**: From research (2021) to commodity (2025) in 4 years
