# Understanding DAG (Directed Acyclic Graph) in Signify

> **Tier 1 (The Thinking Brain):** Autonomous Goal Planner that creates execution step graphs (DAGs), inspects tools, and adapts plans on the fly.

---

## 1. What is a DAG? (Simple Explanation)

**DAG** stands for:
* **D (Directed):** Every step has a clear, one-way direction (an arrow $\rightarrow$ pointing forward).
* **A (Acyclic):** There are **no endless loops or circles**. You never get stuck in $A \rightarrow B \rightarrow C \rightarrow A$.
* **G (Graph):** A visual map of steps, nodes, and dependencies.

### ☕ Everyday Analogy: Making Chai (Tea)

```
[Step 1: Boil Water & Milk]
           │
     ┌─────┴──────────────┐
     ▼                    ▼
[Step 2: Add Ginger]   [Step 3: Add Sugar]  <-- (Can happen in parallel!)
     └─────┬──────────────┘
           ▼
[Step 4: Strain into Cup]  <-- (Waits for Step 2 & 3 to finish)
           │
           ▼
[Step 5: Drink Chai]
```

* **Directed:** You cannot drink the tea before boiling it.
* **Acyclic (No Loop):** Once you drink the chai (Step 5), you don't magically loop back to raw milk. It cleanly finishes.
* **Dependencies:** Step 4 knows it cannot run until both Step 2 and Step 3 are complete.

---

## 2. Why Signify Uses a DAG

In **Signify**, translating Indian Sign Language into speech and text isn't a single monolithic operation. It requires multiple specialized AI tools working in harmony:

```
[Step 1: Environmental Calibration & User Consent]
                         │
                         ▼
[Step 2: 21 3D Landmark Extraction & Classification]
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[Step 3: VerbX English TTS]      [Step 4: VerbX Cross-Lingual Translation]
                                                  │
                                                  ▼
                                         [Step 5: VerbX Hindi TTS]
```

### The 4 Major Benefits of DAG in Signify:

1. **Step Dependency Management:**
   * Step 5 (Hindi Voice) **cannot run** until Step 4 finishes translating the text to Hindi.
   * Step 4 **cannot run** until Step 2 determines which sign was recognized.
   * The DAG enforces this exact order automatically.

2. **Parallel Execution (Sub-120ms Latency):**
   * Steps 3 (English Speech) and 4 (Hindi Translation) can execute simultaneously, saving precious milliseconds during real-time conversations.

3. **Autonomous Dynamic Replanning (Anti-Hallucination):**
   * If a user makes an ambiguous gesture or scratches their face, Step 2 confidence drops below $0.65$.
   * Instead of crashing or guessing, the Autonomous Planner **prunes (skips) Steps 3, 4, and 5** so no false speech is emitted.
   * It dynamically inserts an honest `UNCERTAIN` notification step on the screen.

4. **100% Immutable Audit Trail:**
   * Every step in the DAG logs its latency, inputs, tool name, and output status into an SQLite database (`SessionStepRecord`).

---

## 3. Do Agentic AI Applications Need a DAG?

**YES. For real-world, production Agentic AI, a DAG is essential.**

| Without a DAG (Naive Agent) | With a DAG (Signify's Thinking Brain) |
| :--- | :--- |
| **Random Tool Guessing:** The agent randomly chooses tools on the fly without a plan. | **Structured Plan:** Synthesizes an ordered, verifiable execution path before running. |
| **Infinite Loop Hazard:** LLMs or agents can get stuck repeating the same API call forever, burning budget and hanging. | **Mathematically Guaranteed Termination:** Being *Acyclic* prevents any recursive loops. |
| **No Safety Pruning:** If an intermediate tool fails, downstream tools execute with corrupt data (hallucinations). | **Adaptive Replanning:** Cuts downstream branches when safety or confidence checks fail. |
| **Black-Box Confusion:** Difficult to debug which tool caused an error. | **Clear Observability:** Every node has isolated timing, inputs, and outputs. |

---

## 4. Code Implementation in Signify

Signify implements its DAG in [`backend/app/services/orchestration/planner.py`](file:///c:/Users/tanuu/Downloads/Signify/backend/app/services/orchestration/planner.py):

* **Plan Step Definition (`PlanStep`):**
  ```python
  class PlanStep(BaseModel):
      step_id: int
      name: str
      tool_name: str
      action: str
      parameters: Dict[str, Any]
      depends_on: List[int]     # Defines DAG edges/dependencies
      status: str = "PENDING"   # PENDING, RUNNING, COMPLETED, SKIPPED, ADAPTED
  ```

* **Goal Execution Plans:**
  * **`SIGN_TO_BILINGUAL_SPEECH`:** 5-step DAG transforming hand landmarks into English and Hindi speech.
  * **`SPEECH_TO_SIGN_AND_TEXT`:** 3-step DAG transcribing voice, compiling ISL grammar, and matching authenticated video clips.
  * **`EMERGENCY_TRIAGE`:** Fast 2-step urgent broadcast DAG for clinical/hospital environments.

* **Dynamic Replanning Trigger:**
  ```python
  # If vision classification is uncertain (<0.65), prune speech steps:
  if res.status != "RECOGNIZED" or res.confidence < 0.65:
      replan_occurred = True
      for future_step in plan.steps:
          if "Speech" in future_step.name:
              future_step.status = "SKIPPED"  # Prune to prevent hallucination!
  ```

