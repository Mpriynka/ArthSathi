# ArthSathi --- AI-Powered Financial Inclusion Companion

> **Learn. Understand. Act safely. Grow.**

ArthSathi is a multilingual, AI-powered financial inclusion companion
designed for rural communities in India. It combines personalized
financial education, trusted financial knowledge, document
understanding, goal tracking, digital-payment awareness, and safety
guardrails into a single assistant that adapts to each user's financial
context.

The platform is designed to work with **NGOs and community volunteers**
who can help onboard users, run learning initiatives, view aggregate
community-level insights, and intervene when a situation requires human
assistance.

------------------------------------------------------------------------

## 1. Problem

Financial inclusion is not only a problem of access to financial
services. Many people face a combination of:

-   Limited financial literacy.
-   Language and communication barriers.
-   Low familiarity with digital financial services.
-   Difficulty understanding financial documents.
-   Lack of personalized financial guidance.
-   Fear of fraud, scams, and making costly mistakes.
-   Limited access to trusted human financial guidance.

Most financial education systems provide generic information. However,
two people may have completely different financial needs depending on
their occupation, income pattern, existing banking access, goals,
language, and level of financial knowledge.

**ArthSathi addresses this personalization and trust gap.**

------------------------------------------------------------------------

## 2. Vision

ArthSathi aims to make financial knowledge:

**Accessible → Personalized → Understandable → Safe → Actionable**

Instead of simply answering:

> "What is a bank account?"

ArthSathi should help a user move through:

> **What is it? → Is it relevant to me? → What should I know? → What
> should I be careful about? → What is my next safe step?**

The goal is not to replace banks, financial institutions, government
services, or human advisors. The goal is to help users become more
informed and confident when interacting with them.

------------------------------------------------------------------------

# 3. Target Users

## Primary Users

Rural and underserved users who want to improve their understanding and
use of formal financial services.

Examples include:

-   First-time banking users.
-   Users with limited digital-payment experience.
-   People learning about government financial schemes.
-   Users who want to start saving.
-   Users trying to understand insurance or pension products.
-   Users who need help understanding financial documents.
-   Users who want to set and track financial goals.

## Community Users

### NGOs and Volunteers

NGOs and volunteers act as the human support layer.

They can help with:

-   Assisted onboarding.
-   Community financial-literacy campaigns.
-   Learning support.
-   Identifying common knowledge gaps.
-   Escalating complex or high-risk cases to humans.

The system is designed so that community-level analytics can be useful
without exposing users' private financial information.

------------------------------------------------------------------------

# 4. Core Product

ArthSathi is built around five principles:

### 1. Understand Me

Create a user financial persona during onboarding and continuously
improve it as the user interacts with the system.

### 2. Teach Me

Explain financial concepts in simple language using text or voice.

### 3. Help Me Act

Provide relevant, grounded information and guide the user toward a safe
next step.

### 4. Protect Me

Use safety, compliance, privacy, and grounding mechanisms to reduce
harmful or unreliable financial guidance.

### 5. Help Me Progress

Let users set goals, track progress, complete learning activities, and
build financial habits.

------------------------------------------------------------------------

# 5. Key Features

## 5.1 Personalized Financial Profile

During onboarding, users answer a small set of profiling questions.

The profile can contain information such as:

-   Preferred language.
-   Occupation.
-   Income pattern.
-   Financial-literacy level.
-   Banking familiarity.
-   Digital-payment familiarity.
-   Financial goals.
-   Learning progress.
-   Relevant preferences and accessibility needs.

The profile is used as context when generating personalized responses.

### Example

A user who is new to digital payments may receive:

-   Basic UPI education.
-   Scam-awareness guidance.
-   Simple explanations of payment flows.

A more experienced user may instead receive:

-   Goal-based savings guidance.
-   More advanced digital-finance education.
-   Relevant financial planning concepts.

------------------------------------------------------------------------

# 6. Agentic Architecture

ArthSathi uses **LangGraph** to orchestrate specialized agents.

``` text
                         USER
                          │
              ┌───────────┼───────────┐
              │           │           │
             Text        Voice      Document
              │           │           │
              └───────────┼───────────┘
                          ▼
                 Intent / Context Router
                          │
                          ▼
                 LangGraph Orchestrator
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
  Teaching Agent    Advisor Agent    Safety Agent
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                  Profile / Memory Agent
                          │
                          ▼
                 Knowledge + Tool Layer
                          │
             ┌────────────┴────────────┐
             │                         │
          Qdrant                    MCP Tools
             │                         │
             └────────────┬────────────┘
                          ▼
                    Final Response
                          │
                          ▼
                  Goals / Progress
                          │
                          ▼
                  Updated User State
```

------------------------------------------------------------------------

# 7. Specialized Agents

## 7.1 Knowledge / Intent Router

The router determines:

-   What the user is asking.
-   Which domain the request belongs to.
-   Which agent should handle it.
-   What user context is relevant.
-   Whether additional tools are required.

Example:

``` text
"मुझे UPI सुरक्षित तरीके से कैसे इस्तेमाल करना चाहिए?"

        ↓

Intent: Digital Payment Safety

        ↓

Teaching Agent
        +
Safety Agent

        ↓

Retrieve trusted UPI safety information

        ↓

Simple Marathi/Hindi explanation
```

------------------------------------------------------------------------

## 7.2 Teaching Agent

Responsible for financial education.

Typical tasks:

-   Explain financial concepts.
-   Simplify complex terminology.
-   Answer educational questions.
-   Create learning paths.
-   Explain financial documents.
-   Provide quizzes or learning activities.
-   Adapt explanations to the user's knowledge level.

The Teaching Agent should prioritize **clarity over complexity**.

------------------------------------------------------------------------

## 7.3 Advisor / Action Agent

Responsible for turning information into an actionable next step.

Examples:

-   Help a user understand how to start using digital payments.
-   Explain what documents may be required for a service.
-   Help break a savings goal into smaller milestones.
-   Help a user identify relevant financial topics to learn next.

The agent should provide **information and guided next steps**, not
unrestricted financial recommendations.

------------------------------------------------------------------------

## 7.4 Profile / Memory Agent

The Profile Agent manages the evolving user persona.

It determines what useful information should be retained for future
personalization.

Example:

``` json
{
  "language": "Marathi",
  "financial_literacy": "beginner",
  "digital_payment_familiarity": "low",
  "occupation": "farmer",
  "income_pattern": "seasonal",
  "goals": [
    "emergency_fund",
    "education"
  ]
}
```

### Memory policy

The system should not allow an LLM to arbitrarily store everything a
user says.

A memory policy should determine:

-   What information is useful.
-   What information requires consent.
-   What information should expire.
-   What information should never be stored.
-   Which memories can be used for personalization.

This reduces unnecessary data collection and improves privacy.

------------------------------------------------------------------------

## 7.5 Safety & Compliance Agent

The Safety Agent is responsible for reducing unsafe or unsupported
financial guidance.

It can check for:

-   Unsupported financial claims.
-   Fabricated scheme information.
-   Unverified eligibility statements.
-   Unsafe recommendations.
-   Suspicious documents or inputs.
-   Prompt injection attempts.
-   Inconsistent numerical information.
-   Missing or weak source grounding.

High-risk or uncertain situations can be escalated to an NGO volunteer
or another human support channel.

------------------------------------------------------------------------

# 8. Trusted RAG Architecture

Financial information should not rely only on the LLM's internal
knowledge.

ArthSathi uses **Retrieval-Augmented Generation (RAG)** over trusted
financial sources.

Potential sources include:

-   Financial education material.
-   Government financial-scheme information.
-   Banking and digital-payment safety information.
-   Insurance and pension education.
-   Fraud-awareness material.
-   Other verified institutional sources.

``` text
Trusted Documents
       │
       ▼
Document Processing
       │
       ▼
Chunking + Metadata
       │
       ▼
Embeddings
       │
       ▼
Qdrant
       │
       ▼
Metadata Filtering
       │
       ▼
Semantic Retrieval
       │
       ▼
LLM + User Context
       │
       ▼
Grounded Response
```

------------------------------------------------------------------------

# 9. Qdrant Metadata Filtering

Qdrant is used as the vector database.

Retrieval can be filtered using metadata such as:

``` text
topic
language
source
document_version
effective_date
user_stage
memory_type
user_id
```

For user-specific memory, metadata filtering helps ensure that only
information belonging to the relevant user is retrieved.

This provides an additional boundary against irrelevant or cross-user
retrieval.

------------------------------------------------------------------------

# 10. Financial Knowledge vs User Memory

These should be treated as separate conceptual data domains.

## Financial Knowledge

Contains trusted external information:

``` text
Government schemes
Banking education
Digital-payment safety
Insurance education
Pension education
Fraud awareness
```

## User Memory

Contains user-specific information:

``` text
Preferences
Learning progress
Goals
Relevant financial context
Past interactions
Personalization signals
```

The separation helps prevent accidental mixing of public financial
knowledge and private user information.

------------------------------------------------------------------------

# 11. Document Understanding

Users can upload financial documents and ask questions about them.

Example documents:

-   Bank statements.
-   Insurance documents.
-   Loan-related documents.
-   Government-scheme documents.
-   Financial forms.
-   Other supported financial documents.

### Processing pipeline

``` text
Document Upload
      │
      ▼
File Validation
      │
      ▼
OCR / Text Extraction
      │
      ▼
Document Classification
      │
      ▼
PII / Sensitive Data Detection
      │
      ▼
Chunking
      │
      ▼
Embeddings
      │
      ▼
Qdrant / Temporary Context
      │
      ▼
RAG
      │
      ▼
Simple Explanation
```

For numerical information, extracted values should be validated rather
than allowing the LLM to freely invent or infer them.

------------------------------------------------------------------------

# 12. Multilingual Voice Interface

ArthSathi is designed for:

-   English.
-   Hindi.
-   Marathi.

Users can communicate through either text or voice.

### Voice pipeline

``` text
User Speech
    │
    ▼
STT / ASR
    │
    ▼
Text
    │
    ▼
LangGraph + Agents
    │
    ▼
Response Text
    │
    ▼
TTS
    │
    ▼
Spoken Response
```

Where device capabilities permit, small quantized speech models can be
deployed on-device to reduce latency and improve privacy. A server-side
fallback can be used for devices that cannot support the required
models.

The system should not assume that every device can run the same speech
model.

------------------------------------------------------------------------

# 13. Goal Setting and Tracking

Financial literacy becomes more useful when it leads to measurable
progress.

Users can create goals such as:

``` text
Goal:
Save ₹10,000 for education

Target:
₹10,000

Current:
₹3,000

Remaining:
₹7,000

Target Date:
Defined by user

Progress:
30%
```

Goals can be:

-   User-created.
-   Suggested based on the user's learning journey.
-   Broken into smaller milestones.
-   Tracked over time.
-   Used to personalize future learning.

------------------------------------------------------------------------

# 14. Community Gamification

ArthSathi can provide an optional anonymous locality-based leaderboard.

Users should **not** be ranked based on:

-   Income.
-   Wealth.
-   Account balance.
-   Savings amount.
-   Other sensitive financial attributes.

Instead, the leaderboard can reward:

-   Learning modules completed.
-   Financial-safety quizzes.
-   Goal consistency.
-   Knowledge improvement.
-   Learning streaks.

Example:

``` text
Village Learning Board

1. Anonymous User — 18 lessons
2. Anonymous User — 16 lessons
3. You              — 14 lessons

Your Goal Consistency: 82%
Safety Knowledge: +24%
```

This makes financial learning engaging without turning financial status
into a competition.

------------------------------------------------------------------------

# 15. NGO and Volunteer Layer

ArthSathi is designed for community deployment.

``` text
                 NGO / VOLUNTEER
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Onboarding     Campaigns    Human Support
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                  Community Users
```

## NGO capabilities

### Assisted Onboarding

Volunteers can help users create their profiles.

### Learning Campaigns

NGOs can encourage users to complete relevant learning modules.

### Aggregate Insights

The platform can show community-level learning gaps such as:

``` text
UPI Safety             62%
Banking Basics         48%
Insurance Awareness    31%
Government Schemes     21%
```

These insights should be aggregated and privacy-preserving.

### Human Escalation

Complex or high-risk cases can be routed to a human.

Examples:

-   Suspicious financial documents.
-   Potential fraud.
-   Complex claims.
-   Disputed transactions.
-   Unclear eligibility.
-   Situations where the AI lacks sufficient confidence.

------------------------------------------------------------------------

# 16. MCP Tool Layer

ArthSathi uses an extensible MCP-based tool layer so capabilities can be
added without tightly coupling them to individual agents.

Potential tools include:

``` text
MCP Tools
│
├── Financial Calculator
├── OCR / Document Parser
├── Knowledge Search
├── Eligibility Checker
├── Goal Calculator
├── Translation
├── Financial Safety Checker
├── Reminder / Notification
└── NGO Escalation
```

Agents can invoke tools based on the request.

For example:

``` text
Advisor Agent
    │
    ├── Goal Calculator
    ├── Eligibility Tool
    └── Knowledge Search
```

while:

``` text
Teaching Agent
    │
    ├── Document Parser
    ├── Knowledge Search
    └── Translation
```

This makes the architecture extensible.

------------------------------------------------------------------------

# 17. Safety and Privacy

Financial applications require stronger safeguards than a
general-purpose chatbot.

ArthSathi follows several principles:

## Data Minimization

Store only information required for personalization and product
functionality.

## Consent-Aware Memory

Users should be able to control what is remembered where appropriate.

## Source Grounding

Financial claims should be backed by retrieved trusted sources.

## Source Freshness

Knowledge metadata should include information such as:

``` text
source
publication_date
effective_date
last_verified
document_version
```

This helps prevent old information from being treated as current.

## PII Protection

Uploaded documents and conversations may contain sensitive information.
The system should detect and protect PII during processing.

## Human Escalation

The AI should not be forced to answer every question.

When uncertainty or risk is high:

``` text
AI
 ↓
Safety Check
 ↓
High Risk / Low Confidence
 ↓
Human Support
```

------------------------------------------------------------------------

# 18. Observability and Logging

The system should maintain structured logs for debugging, evaluation,
and system reliability.

A request trace can capture:

``` text
Request ID
   │
   ├── User intent
   ├── Selected agent
   ├── Retrieved sources
   ├── Tool calls
   ├── Model response
   ├── Safety checks
   ├── Latency
   └── Final response
```

Important metrics include:

-   Retrieval latency.
-   Agent latency.
-   Tool latency.
-   Tool failures.
-   LLM token usage.
-   Retrieval quality.
-   Safety flags.
-   User feedback.
-   Goal completion.
-   Escalation frequency.

Sensitive user data should not be unnecessarily copied into logs.

------------------------------------------------------------------------

# 19. Technology Stack

  Layer                  Technology
  ---------------------- --------------------------------------------
  Frontend               React, TypeScript
  Backend                Python, FastAPI
  Agent orchestration    LangGraph
  LLM                    Compatible LLM / local or hosted model
  RAG                    Embeddings + Qdrant
  Vector database        Qdrant
  Application database   MongoDB
  Tool protocol          MCP
  Document processing    OCR + PDF/document parsers
  Voice input            STT / ASR
  Voice output           TTS
  On-device inference    Quantized models where supported
  Observability          Structured application, agent and LLM logs

------------------------------------------------------------------------

# 20. High-Level System Architecture

``` text
┌──────────────────────────────────────────────────────────────┐
│                        USER EXPERIENCE                       │
│                                                              │
│     Text     Voice     Marathi     Hindi     English         │
│                         Documents                            │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                  PERSONALIZATION LAYER                      │
│                                                              │
│  Financial Persona │ Goals │ Learning State │ Preferences   │
│  Consent │ Memory Policy │ Interaction History             │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATOR                    │
│                                                              │
│              Intent + Context + Agent Routing                │
└─────────────┬──────────────────────┬─────────────────────────┘
              │                      │
              ▼                      ▼
┌──────────────────────┐   ┌──────────────────────────────────┐
│    SPECIALIZED       │   │          SAFETY LAYER            │
│       AGENTS         │   │                                  │
│                      │   │ Grounding │ Validation │ PII      │
│ Teaching             │   │ Risk Checks │ Guardrails          │
│ Advisor              │   │ Human Escalation                  │
│ Profile              │   └──────────────────────────────────┘
│ Knowledge Router     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                      MCP TOOL LAYER                          │
│                                                              │
│ OCR │ Calculator │ Eligibility │ Document Parser │ Goals     │
│ Translation │ Knowledge Search │ Safety │ Escalation         │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│                                                              │
│ Qdrant                         MongoDB                       │
│ ├── Financial knowledge        ├── User profile              │
│ ├── Document embeddings        ├── Goals                     │
│ └── User-memory vectors        ├── Preferences               │
│                                └── Interaction state          │
└──────────────────────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 21. Example Interaction

### User

> "मुझे UPI इस्तेमाल करना है लेकिन मुझे डर लगता है कि कहीं पैसे गलत जगह न चले जाएं।"

### Step 1 --- Intent

``` text
Digital Payment + Safety Education
```

### Step 2 --- Profile

System checks:

``` text
Language: Marathi/Hindi
Digital payment familiarity: Low
Learning stage: Beginner
```

### Step 3 --- Routing

``` text
Teaching Agent
       +
Safety Agent
```

### Step 4 --- Retrieval

Retrieve trusted information about:

-   UPI basics.
-   PIN safety.
-   QR-code scams.
-   Payment confirmation.
-   Fraud reporting.

### Step 5 --- Response

The system explains the concept in simple language and gives a small
number of practical safety rules.

### Step 6 --- Progress

The user can complete a short safety-learning activity and optionally
set a goal such as:

> "Learn the basics of safe UPI payments."

The learning state is updated for future personalization.

------------------------------------------------------------------------

# 22. Why an Agentic Architecture?

A single chatbot is not enough for the intended use case because
different tasks require different controls.

For example:

  Task                                  Suitable component
  ------------------------------------- ------------------------
  Explain a concept                     Teaching Agent
  Suggest a next learning/action step   Advisor Agent
  Remember useful user context          Profile Agent
  Find the correct information          Knowledge Router + RAG
  Check risk and grounding              Safety Agent
  Perform calculations or OCR           MCP Tools
  Track progress                        Goal/Progress system

LangGraph provides explicit orchestration and state management across
these components.

------------------------------------------------------------------------

# 23. Why MCP?

MCP provides a standardized interface between agents and external
capabilities.

Instead of implementing tool logic separately inside each agent:

``` text
Agent → MCP → Tool
```

This allows tools to be:

-   Reused across agents.
-   Added independently.
-   Tested separately.
-   Replaced without redesigning the agent layer.
-   Extended as the platform grows.

------------------------------------------------------------------------

# 24. Expected Impact

ArthSathi aims to contribute to financial inclusion through:

### Improved Financial Literacy

Users gain a better understanding of financial concepts, services, and
risks.

### Better Access to Information

Users can discover relevant financial services and government schemes in
a simple format.

### Safer Digital Finance

Users learn practical digital-payment and fraud-prevention practices.

### Personalized Financial Learning

Users receive guidance based on their context rather than a generic
curriculum.

### Measurable Progress

Goals and learning progress make financial education more actionable.

### Stronger Community Support

NGOs and volunteers gain tools to support users and understand aggregate
community learning needs.

------------------------------------------------------------------------

# 25. MVP Scope

To keep the implementation realistic, the first version should focus on
a small number of high-value capabilities.

## MVP

### Languages

-   English
-   Hindi
-   Marathi

### Agents

-   Knowledge / Intent Router
-   Teaching Agent
-   Advisor Agent
-   Profile / Memory Agent
-   Safety & Compliance Agent

### Financial Domains

-   Banking basics.
-   Digital payments.
-   Savings.
-   Government financial schemes.
-   Insurance awareness.
-   Fraud awareness.

### Core capabilities

-   Personalized onboarding.
-   RAG over trusted sources.
-   Voice/text interaction.
-   Financial document understanding.
-   Goal tracking.
-   Safety guardrails.
-   NGO-assisted onboarding.
-   Human escalation.

------------------------------------------------------------------------

# 26. Future Extensions

The architecture is designed to support additional capabilities such as:

-   More Indian languages.
-   Offline-first functionality for low-connectivity environments.
-   More on-device AI inference.
-   Additional government-scheme integrations.
-   More financial-document types.
-   Stronger community learning analytics.
-   Integration with verified financial-service APIs.
-   Personalized financial-literacy assessments.
-   More sophisticated accessibility features.
-   Additional MCP tools.

The goal is to extend the platform without changing its core
architecture.

------------------------------------------------------------------------

# 27. Design Principles

ArthSathi follows these principles:

1.  **Personalize before recommending.**
2.  **Teach before asking users to act.**
3.  **Use trusted sources for financial information.**
4.  **Give one clear and safe next step when possible.**
5.  **Minimize data collection.**
6.  **Keep user memory consent-aware.**
7.  **Never expose private financial information through community
    analytics.**
8.  **Escalate high-risk cases to humans.**
9.  **Prefer simple language over financial jargon.**
10. **Design for real-world rural connectivity, language, and device
    constraints.**

------------------------------------------------------------------------

# 28. Project Summary

**ArthSathi is not simply a financial chatbot.**

It is a personalized financial inclusion layer that connects:

``` text
Financial Education
        +
Personalization
        +
Trusted Knowledge
        +
Voice & Multilingual Access
        +
Safety
        +
Goals
        +
Community Support
        =
Financial Inclusion
```

The core idea is simple:

> **Every person has a different financial starting point. ArthSathi
> helps them understand where they are, learn what matters to them, and
> take the next safe step toward greater financial inclusion.**

------------------------------------------------------------------------

## Project Status

**Hackathon Prototype / Product Concept**

The architecture and feature set are designed for a working prototype,
with the MVP prioritizing personalized RAG, agent orchestration,
multilingual interaction, document understanding, safety controls,
goals, and NGO-assisted community deployment.

## License

Add the project's chosen license here, for example:

``` text
MIT License
```

if the implementation is intended to be released under MIT.
