# ENDI – Enhanced Natural-language Directed Intelligence

### Reference Architecture for a Terminal AI Assistant

## 1. Purpose

This document describes a **technology-agnostic reference architecture** for building a command-driven terminal assistant capable of orchestrating workflows and tools.

The assistant is designed to support:

- command-based workflows
- conversational interactions
- tool invocation (filesystem, shell, APIs, etc.)
- multi-step reasoning tasks

The architecture intentionally avoids coupling to specific frameworks, models, or vendors so implementation details can evolve independently.

---

# Design Principles for ENDI

The following principles guide architectural and implementation decisions for ENDI.

## Human-in-the-Loop

ENDI is designed to **assist rather than replace human operators**. Critical operations should require explicit user intent and confirmation.

## Modularity

ENDI should be composed of **independent, well-defined components**. Commands, workflows, tools, and agents should be separable modules that can evolve independently.

## Deterministic Operations Where Possible

Whenever tasks can be implemented deterministically, they should be. AI-driven reasoning should augment workflows rather than replace predictable automation.

## Observability

All operations performed by ENDI should be **transparent and traceable**. Users should be able to see which tools were executed, what inputs were used, and what results were produced.

## Extensibility

ENDI should be easy to extend with new commands, tools, workflows, and integrations without requiring modification of the core system.

## Safety by Default

Potentially destructive operations should require confirmation or safeguards. ENDI should favor conservative behavior over aggressive automation.

## Provider Independence

The architecture should avoid tight coupling to specific service providers, infrastructure platforms, or language models.

## Clear Separation of Concerns

Each layer of the system should have a clearly defined responsibility:

- CLI interface handles user interaction
- command router dispatches tasks
- orchestration engine coordinates reasoning
- tools perform operations

---

# Non-Goals (Scope Boundaries)

To prevent scope creep, ENDI intentionally excludes several capabilities from the initial design. These non-goals help keep the project focused and prevent unnecessary complexity during early development.

## Not a Full IDE Replacement

ENDI is designed as a **terminal assistant**, not a graphical development environment. It should augment developer workflows rather than replace editors, IDEs, or existing development tooling.

## Not a Fully Autonomous System

ENDI should assist and automate workflows, but **humans remain in control**. The system should not independently execute destructive operations, modify critical infrastructure, or deploy changes without explicit user intent or confirmation.

## Not a Platform-Specific Tool

ENDI should remain **platform-agnostic**. It should not be tightly coupled to a specific cloud provider, infrastructure platform, version control system, or CI/CD solution.

## Not a General-Purpose Chatbot

ENDI is intended to be a **task-oriented assistant for operational and development workflows**, not a generic conversational chatbot.

## Not a Replacement for Existing Automation Systems

ENDI should integrate with automation systems rather than replace them. Systems such as CI/CD pipelines, infrastructure provisioning tools, and monitoring platforms should continue to perform the underlying automation.

## Not a Black-Box Automation Engine

Actions performed by ENDI should remain **observable and understandable**. Users should always be able to see what tools are executed and why.

## Not a Security Boundary

ENDI should not be treated as a security enforcement mechanism. Security controls, access policies, and infrastructure permissions must remain enforced by the underlying platforms.

## Not a Large Monolithic Application

ENDI should remain **modular and extensible**, allowing commands, tools, and workflows to evolve independently rather than forming a tightly coupled system.

---

# 2. High-Level Architecture

```
Terminal
   │
   ▼
CLI Interface
   │
   ▼
Command Router
   │
   ├── Deterministic Workflows (/commands)
   │
   └── Conversational Agent
            │
            ▼
     Orchestration Engine
            │
            ▼
        Tool Layer
            │
            ▼
   External Systems / APIs / Files
```

### Responsibilities

| Component | Responsibility |
|---|---|
| Terminal | User interaction |
| CLI Interface | Input/output handling |
| Command Router | Maps commands to workflows |
| Workflows | Deterministic operations |
| Conversational Agent | Open-ended reasoning |
| Orchestration Engine | Multi-step agent execution |
| Tool Layer | Operational capabilities |
| External Systems | Infrastructure, APIs, repositories |

---

# 3. Interaction Model

The assistant supports **two interaction styles**.

## Command Mode

Explicit workflows triggered by commands.

Example:

```
/analyze-cost stack.yaml
/deploy staging
/scan-security repo/
```

These commands route to deterministic workflows.

Benefits:

- predictable
- repeatable
- automation-friendly

---

## Conversational Mode

Free-form queries handled by the agent.

Example:

```
> explain this infrastructure stack
> why is this deployment failing?
> optimize this configuration
```

Requests go through the orchestration engine which may:

- reason about the request
- call tools
- gather information
- return results

---

# 4. CLI Interface

The CLI layer is responsible for:

- interactive prompt
- command parsing
- output formatting
- session management

Typical responsibilities:

```
read input
display responses
parse commands
route requests
```

Possible capabilities:

- command history
- multiline input
- colored output
- progress indicators

---

# 5. Command Router

The router determines how input should be handled.

Typical routing logic:

```
if input starts with "/"
    → execute workflow
else
    → send to agent
```

This hybrid model separates deterministic operations from AI-driven reasoning.

| Input | Handler |
|---|---|
| `/command` | Workflow |
| free text | Agent |

---

# 6. Workflow Layer

Workflows represent **structured operations**.

Examples:

| Workflow | Purpose |
|---|---|
| analyze_cost | estimate infrastructure cost |
| generate_template | create infrastructure template |
| scan_security | detect security issues |
| deploy_environment | deploy infrastructure |
| summarize_repo | summarize repository |

Workflow characteristics:

- deterministic steps
- optional AI assistance
- tool usage
- structured inputs and outputs

Example flow:

```
User command
   ↓
Validate input
   ↓
Execute workflow steps
   ↓
Invoke tools
   ↓
Return structured result
```

---

# 7. Conversational Agent

The conversational agent handles **unstructured tasks**.

Capabilities may include:

- reasoning over user intent
- calling tools
- multi-step problem solving
- summarization
- diagnostics

Example request:

```
> why did our deployment fail?
```

Possible agent process:

1. inspect configuration
2. check logs
3. run diagnostic commands
4. analyze results
5. generate explanation

---

# 8. Orchestration Engine

The orchestration engine manages **agent execution cycles**.

Typical loop:

```
Receive request
   ↓
Interpret intent
   ↓
Select action
   ↓
Execute tool
   ↓
Observe result
   ↓
Repeat if necessary
```

Responsibilities include:

- tool selection
- reasoning coordination
- workflow orchestration
- response synthesis

---

# 9. Tool Layer

Tools represent **capabilities the agent can invoke**.

## Filesystem Tools

```
read_file
write_file
list_directory
search_files
```

## Shell Tools

```
execute_command
run_tests
execute_build
run_deployment
```

## Version Control Tools

```
get_status
create_branch
commit_changes
open_pull_request
```

## Infrastructure Tools

```
analyze_infrastructure
estimate_cost
validate_configuration
check_compliance
```

## External Service Tools

```
query_metrics
retrieve_logs
fetch_configuration
call_internal_api
```

Tools should produce structured outputs and predictable behavior.

---

# 10. Tool Design Principles

Tools should follow several principles.

### Deterministic

Avoid ambiguous outcomes.

### Observable

Log inputs, outputs, and failures.

### Composable

Allow agents to combine tools to perform complex tasks.

### Secure

Prevent unsafe operations.

---

# 11. State and Context

The assistant may maintain session context.

Possible context elements:

- working directory
- recent commands
- loaded configuration
- repository metadata
- infrastructure state

Maintaining context allows the agent to reason across interactions.

---

# 12. Safety Controls

Terminal assistants should implement safeguards.

Examples include:

### Execution confirmation

Before destructive operations.

Example:

```
Confirm deletion of resources? (y/n)
```

### Restricted commands

Prevent unsafe shell execution.

### Sandboxing

Limit filesystem or network access.

### Audit logs

Track actions taken by the assistant.

---

# 13. Extensibility

The architecture should support extension.

## New Workflows

Commands can be added without modifying core components.

Example structure:

```
commands/
   cost/
   security/
   infrastructure/
```

## New Tools

Tools should be independently defined and registered.

## Multiple Agents

Specialized agents may be introduced.

Example roles:

```
Infrastructure Agent
Security Agent
Cost Optimization Agent
Development Agent
```

---

# 14. Observability

Monitoring the assistant improves reliability.

Recommended telemetry:

- commands executed
- tools invoked
- execution duration
- reasoning traces
- errors and failures

---

# 15. Example User Session

```
$ assistant

> /generate-template service-api
Template generated.

> /analyze-cost template.yaml
Estimated monthly cost: $312

> why would this deployment fail?
Agent: Inspecting configuration...
Agent: Found missing environment variable.

> /deploy staging
Deployment started.
```

---

# 16. Future Enhancements

Possible extensions include:

## Multi-agent collaboration

Different agents handling specialized domains.

## Automation triggers

Allow the assistant to react to events.

Examples:

```
deployment failure
cost spike
security alert
```

## Integrations

Potential integrations include:

- infrastructure platforms
- CI/CD pipelines
- monitoring systems
- version control platforms

---

# 17. Design Philosophy

This architecture emphasizes:

- modularity
- separation of concerns
- extensibility
- provider independence

Core components such as the orchestration engine, language model, or tools can be replaced without redesigning the entire system.

---

# 18. Project Folder Structure

A modular project structure helps keep the CLI assistant maintainable as the number of commands, tools, and workflows grows.

Example structure:

```
assistant/

   cli/
      main.py
      prompt.py
      router.py

   commands/
      analyze_cost/
         command.py
         workflow.py

      security_scan/
         command.py
         workflow.py

      deploy/
         command.py
         workflow.py

   agent/
      agent.py
      orchestrator.py
      reasoning.py

   tools/
      filesystem/
         read_file.py
         write_file.py

      shell/
         execute_command.py

      infrastructure/
         analyze_stack.py

   context/
      session_context.py

   plugins/
      registry.py

   observability/
      logging.py
      tracing.py

   safety/
      guardrails.py

   config/
      settings.py

   tests/

   main.py
```

Principles behind this structure:

- isolate workflows from command parsing
- separate tools from orchestration
- keep infrastructure integrations independent
- allow plugins and commands to be added easily

---

# 19. Workflow Lifecycle

Workflows follow a consistent lifecycle so they remain predictable and observable.

Typical lifecycle:

```
Initialize
   ↓
Validate Input
   ↓
Plan Actions
   ↓
Execute Steps
   ↓
Collect Results
   ↓
Generate Output
   ↓
Finalize
```

## Initialize

Prepare context and dependencies.

Examples:

- load configuration
- identify working directory
- gather session context

## Validate Input

Ensure required parameters are present.

Examples:

- file paths
- environment identifiers
- repository locations

## Plan Actions

Optional planning stage.

The system determines which tools or steps are required.

Example:

```
analyze infrastructure
retrieve pricing data
calculate estimate
```

## Execute Steps

Tools and operations are executed.

These may include:

- filesystem operations
- shell commands
- API calls

## Collect Results

Aggregate outputs from executed steps.

## Generate Output

Produce structured output for the CLI.

Possible formats:

- text summary
- table
- structured JSON

## Finalize

Clean up temporary state and log results.

---

# 20. Tool Interface Specification

Tools should follow a consistent interface so they can be easily registered and used by agents or workflows.

Example conceptual interface:

```
Tool
   name
   description
   input_schema
   execute()
   output_schema
```

Typical behavior:

```
Receive parameters
Execute operation
Return structured result
```

Example tool contract:

```
input
   parameters

execution
   perform operation

output
   status
   result
   metadata
```

Structured outputs allow the orchestration engine to reason about results.

---

# 21. Command Plugin Architecture

Commands should be implemented as plugins so the assistant can grow without modifying core logic.

Plugin responsibilities:

- define command name
- validate command arguments
- trigger workflow

Example command definition:

```
Command
   name
   description
   arguments
   handler
```

Example discovery structure:

```
commands/
   analyze_cost/
   security_scan/
   deploy/
```

The system loads commands dynamically through a registry.

Benefits:

- independent command development
- simplified testing
- modular expansion

---

# 22. Agent Memory and Context Model

The assistant may maintain contextual state during a session.

Possible context layers:

## Session Context

Information specific to the current terminal session.

Examples:

- working directory
- active repository
- recent commands

## Workflow Context

Temporary state within a workflow execution.

Examples:

- intermediate results
- tool outputs
- execution status

## System Context

Global configuration and metadata.

Examples:

- environment configuration
- available tools
- enabled commands

Maintaining layered context prevents unnecessary recomputation.

---

# 23. Security Model for Tools

Because the assistant can execute operations on the system, security controls are essential.

## Permission Model

Tools may require different permission levels.

Examples:

```
read_only
filesystem_write
shell_execution
network_access
```

## Confirmation Mechanisms

Sensitive operations should require confirmation.

For terminal confirmation summaries, the CLI intentionally renders a safe, deterministic
allowlist of fields (for example: intent, targets, capabilities, backend) instead of printing
all fields present in runtime summary payloads.

This has two user-facing effects:

- confirmation panels stay stable and easy to scan
- sensitive/raw-text fields are excluded by default

Implementation note (ENDI): confirmation summary rendering is allowlist-driven in
`src/endi/presentation.py` using ordered labels. If a new summary schema field should be
visible to users, it must be explicitly added to that ordered field/label mapping.

Example:

```
Delete infrastructure resources?
Confirm (y/n)
```

## Sandboxed Execution

Where possible, operations should execute in controlled environments.

Possible safeguards:

- restricted directories
- command allowlists
- environment isolation

## Audit Logging

All actions should be logged.

Logs may include:

- command issued
- tools executed
- parameters
- execution outcome

This improves traceability and accountability.

---

# 24. Observability and Diagnostics

To operate reliably, the assistant should expose internal telemetry.

Recommended signals:

```
command_execution
workflow_duration
tool_invocations
errors
agent_reasoning
```

Observability enables:

- debugging failures
- analyzing performance
- improving workflows

---

# 25. Evolution Strategy

The architecture supports gradual evolution.

Possible future directions:

## Specialized Agents

Multiple agents focused on different domains.

Examples:

- infrastructure diagnostics
- cost optimization
- security analysis

## Autonomous Operations

Allow the assistant to react to system events.

Examples:

```
deployment failure
cost anomaly
security alert
```

## Knowledge Integration

The assistant may access internal documentation or configuration repositories.

---

This document describes a foundational architecture for building a terminal-based AI assistant. It intentionally separates interaction, orchestration, and operational capabilities so the system can evolve without major redesign.

---

# 26. Core Capabilities

ENDI is intended to function as a **company-aware terminal intelligence layer** with role-oriented workflows and tools. Its core capabilities should remain stable even as role-specific commands and integrations evolve.

## 26.1 Command-Based Workflow Execution

ENDI must support explicit command-driven workflows invoked from the terminal.

Examples:

```
/analyze-cost stack.yaml
/deploy staging
/scan-security repo/
```

These workflows should be deterministic, validated, and automation-friendly.

## 26.2 Natural-Language Task Interpretation

ENDI must support natural-language interaction and translate user intent into actionable execution paths.

Examples:

```
> why is this deployment failing?
> summarize this repository
> analyze this configuration
```

This capability makes ENDI accessible beyond strictly command-oriented usage.

## 26.3 Tool Orchestration

ENDI must be able to invoke tools that perform real operational work.

Representative categories include:

- filesystem operations
- shell and system execution
- infrastructure analysis
- company system integrations
- repository and project inspection

## 26.4 Multi-Step Task Execution

ENDI must support tasks that require multiple execution steps, including chained reasoning and tool invocation.

Examples include diagnostics, deployment investigation, repository analysis, and structured review workflows.

## 26.5 Context Awareness

ENDI must maintain session, environment, and workflow context so users can interact naturally without repeating unnecessary details.

## 26.6 Safe Operational Execution

ENDI must perform actions safely and transparently, including confirmations for destructive operations, auditability, and conservative defaults.

## 26.7 Extensible Capability Framework

ENDI must support the addition of new commands, workflows, tools, agents, and integrations without requiring modification of the core runtime.

## 26.8 Company Knowledge Integration

As ENDI evolves, it should support integration with company knowledge and systems so it can act as a company-aware assistant rather than only a local terminal helper.

---

# 27. Workflow Specification

A workflow is a structured execution plan triggered by a command or system action.

Conceptually:

```
Workflow
  metadata
  inputs
  context
  steps
  postconditions
  outputs
```

## 27.1 Metadata

Each workflow should define:

- name
- description
- trigger
- version

## 27.2 Inputs

Workflows define the parameters required for execution. Inputs may come from explicit command arguments, session context, or inferred project context.

## 27.3 Context

Workflows may consume resolved context such as working directory, active repository, recent session history, and environment information.

## 27.4 Steps

A workflow is composed of ordered execution steps. A step may be one of the following:

- agent
- tool
- script
- decision

## 27.5 Multi-Agent Review Chains

Workflows must support multi-agent patterns such as:

- generator agent
- reviewer agent
- correction agent
- validator agent

This allows agent outputs to be reviewed, corrected, or approved before finalization.

## 27.6 Postconditions

Workflows should define postconditions used to validate successful completion.

Examples:

- output exists
- output matches schema
- reviewer approval obtained
- confidence threshold met

## 27.7 Error Handling

Workflows should define explicit retry and failure handling behavior, including retries, fallback paths, or early abort conditions.

## 27.8 Outputs

Workflows should produce structured outputs suitable for terminal rendering, chaining into subsequent steps, or machine-readable consumption.

---

# 28. Agent Specification

An agent is a reasoning component that interprets input, optionally uses tools, and produces structured output.

Conceptually:

```
Agent
  metadata
  role
  capabilities
  tools
  reasoning configuration
  input schema
  output schema
  constraints
```

## 28.1 Metadata

Each agent should define:

- name
- description
- version

## 28.2 Role

The role defines the agent’s specialization and reasoning perspective.

Examples:

- infrastructure diagnostics specialist
- cost optimization analyst
- security reviewer
- code reviewer

## 28.3 Capabilities

Agents should declare the task categories they are able to perform.

## 28.4 Tool Access

Agents should only be granted the subset of tools they require.

## 28.5 Reasoning Configuration

Agents should define configurable reasoning properties such as tool usage permission, iteration limits, and execution behavior.

## 28.6 Input Schema

Agents should define the shape of the inputs they expect.

## 28.7 Output Schema

Agents should return structured outputs whenever possible.

## 28.8 Constraints

Agents may declare operational constraints such as read-only analysis, no file modification, or no network access.

## 28.9 Validation

Agent outputs may be validated by schema checks, reviewer agents, or workflow postconditions.

---

# 29. Tool Specification

A tool is a deterministic operational capability that can be invoked by agents or workflows.

Conceptually:

```
Tool
  metadata
  description
  permissions
  input_schema
  execution
  output_schema
  error_handling
```

## 29.1 Metadata

Each tool should define:

- name
- description
- version

## 29.2 Description

Each tool should clearly state what it does and when it should be used.

## 29.3 Permissions

Tools should declare required permission levels.

Examples:

- filesystem_read
- filesystem_write
- shell_execution
- network_access
- external_api_access

## 29.4 Input Schema

Tools should define their required inputs and parameter types.

## 29.5 Execution Behavior

Tools should implement deterministic execution logic.

## 29.6 Output Schema

Tools should produce structured outputs whenever possible.

## 29.7 Error Handling

Tools should return predictable structured errors rather than ambiguous free-form failures.

## 29.8 Tool Categories

Representative categories include:

- filesystem tools
- shell tools
- version control tools
- infrastructure tools
- observability tools
- company systems tools

## 29.9 Observability

Tool execution should be logged for debugging, traceability, and auditability.

---

# 30. Tool Registry and Plugin System

ENDI Core should remain minimal while commands, workflows, agents, and tools are delivered as plugins.

## 30.1 ENDI Core Responsibilities

ENDI Core should contain the minimal runtime:

- CLI
- command router
- workflow engine
- agent runtime
- tool registry
- plugin loader
- context system

## 30.2 Plugin Structure

Plugins should package capability domains such as DevOps, development, QA, data, or delivery.

A plugin may provide:

- tools
- agents
- workflows
- commands

## 30.3 Plugin Manifest

Each plugin should declare the capabilities it provides through a manifest.

## 30.4 Plugin Loader

At startup, ENDI should discover plugins, read manifests, and register their capabilities.

## 30.5 Registries

ENDI should expose registries for:

- tools
- agents
- workflows
- commands

These registries provide lookup, discovery, and introspection.

## 30.6 Plugin Isolation

Plugins should communicate through registries rather than direct coupling to each other.

## 30.7 Distribution Model

Plugins may eventually be distributed as internal packages, repositories, or installable organizational extensions.

---

# 31. Context System

The Context System provides ENDI with the information required to interpret requests accurately and maintain continuity across a session.

## 31.1 Design Principles

The context system should be:

- layered
- scoped
- observable
- ephemeral by default
- extensible

## 31.2 Context Layers

### Environment Context

Runtime facts such as:

- current working directory
- shell or OS details
- current branch
- environment variables

### Session Context

Current interaction history such as:

- recent commands
- recent prompts
- referenced files
- recent workflow outputs

### Workflow Context

Execution-scoped state such as:

- current workflow id
- step outputs
- retry state
- validation status

### Project Context

Higher-level repository or project understanding such as:

- detected technologies
- key files
- project type
- repository metadata

### Organizational Context

Installed integrations and company-aware capability metadata such as:

- available plugins
- connected systems
- organizational workflow domains

## 31.3 Context Resolution Order

Context should resolve in the following order:

1. explicit user input
2. command arguments or workflow inputs
3. session context
4. project context
5. environment context
6. defaults

## 31.4 Context Safety

Context should be ephemeral by default, minimally exposed to agents, and should avoid uncontrolled storage of sensitive values.

---

# 32. Execution Loop Specification

The execution loop defines the runtime lifecycle of a single ENDI interaction from input to terminal output.

High-level lifecycle:

```
Receive Input
   ↓
Classify Input
   ↓
Resolve Context
   ↓
Select Execution Path
   ↓
Execute
   ↓
Validate Result
   ↓
Update Context
   ↓
Render Output
```

## 32.1 Input Classification

ENDI should classify input into:

- command input
- natural-language input
- system or meta input

## 32.2 Execution Paths

Recommended execution paths:

- core command path
- workflow command path
- natural-language chat path
- optional hybrid path

## 32.3 Workflow Step Execution

Workflow execution should iterate through steps, resolving inputs, executing the step, capturing output, validating results, and updating workflow context.

## 32.4 Agent Subloop

Agent steps should support iterative reasoning with controlled tool use and bounded execution.

## 32.5 Multi-Agent Chains

The execution loop should naturally support workflows composed of multiple agent steps such as generator, reviewer, and corrector patterns.

## 32.6 Postcondition Evaluation

After workflow execution, ENDI should validate postconditions and apply defined failure policies.

## 32.7 Error Handling

Errors should be handled as structured runtime outcomes at the tool, agent, and workflow levels.

## 32.8 Context Update

After execution, ENDI should update session context with useful references, recent workflow information, and non-sensitive interaction state.

## 32.9 Output Rendering

Results should be rendered in human-readable or structured forms depending on command requirements and runtime mode.

## 32.10 Observability

The runtime should emit execution events that support tracing, debugging, and diagnostics.

---

# 33. Command Specification

A command is a user-facing invocation contract that maps terminal input to an executable ENDI behavior.

A command is the interface. The workflow or core action is the implementation.

## 33.1 Command Categories

Recommended command categories:

- core commands
- workflow commands
- utility commands

## 33.2 Command Structure

Each command should conceptually define:

- name
- description
- category
- arguments
- options
- execution target
- confirmation policy
- output mode
- examples

## 33.3 Naming Rules

Commands should be:

- lowercase
- kebab-case
- concise
- intention-revealing

## 33.4 Arguments and Options

Commands may define positional arguments and named options. Missing values may be resolved through the context system when safe and appropriate.

## 33.5 Execution Target

Each command should map to exactly one primary execution target, such as a workflow or a core action.

## 33.6 Confirmation Policy

Sensitive commands should define whether confirmation is required before execution.

## 33.7 Discoverability

Commands should be discoverable through help output, usage examples, and registry introspection.

## 33.8 Validation

Command validation should happen before workflow execution and should fail fast on malformed inputs or unsupported options.

## 33.9 Error Model

Command errors should be clear and structured, including unknown commands, invalid arguments, and unsupported options.

## 33.10 Command Manifests

To support plugin-based extension, commands should be declaratively defined and registerable through manifests or equivalent metadata.

---

# 34. Architectural Direction

ENDI should be implemented as a **workflow-oriented terminal runtime** rather than as a single all-purpose agent.

This means:

- ENDI Core provides the runtime
- workflows orchestrate execution
- agents are invoked as workflow components
- tools perform deterministic operations
- commands expose capability to users

This model supports both:

- a general natural-language assistant
- multi-agent workflows built incrementally on demand as `/commands` are introduced

## 34.1 Recommended Build Sequence

A sensible implementation sequence is:

1. build the foundations
2. build the general natural-language chat
3. build commands one by one
4. add agents and workflows on demand per command
5. introduce richer multi-agent review and validation patterns as needed

This approach preserves architectural flexibility while allowing practical incremental delivery.

