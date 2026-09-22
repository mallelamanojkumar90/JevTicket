# JevTicket

Visual learning project for building a **Jev by TypeSafe AI** support-ticket router.

```mermaid
flowchart LR
    Ticket[Support ticket text] --> Jev[Jev typed decisions]
    Jev --> Category[Category]
    Jev --> Urgency[Urgency]
    Jev --> Severity[Severity]
    Category --> Route[Python route]
    Severity --> Escalate[Python escalation]
    Route --> Queue[Support queue]
    Escalate --> Outcome[Escalation flag]
```

## Big Picture

```mermaid
flowchart TB
    subgraph Input["Input"]
        A[Customer message]
    end

    subgraph JevLayer["Jev decision layer"]
        B[Choice: category]
        C[Noul: urgency probability]
        D[Score: severity]
    end

    subgraph PythonLayer["Python business logic"]
        E[Validate typed output]
        F[Route to team]
        G[Escalate if severity is 4 or 5]
    end

    subgraph Interfaces["Ways to use it"]
        H[Terminal app]
        I[Streamlit UI]
        J[Evaluation runner]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> E
    D --> E
    E --> F
    E --> G
    F --> H
    F --> I
    F --> J
    G --> H
    G --> I
    G --> J
```

## Decision Flow

```mermaid
sequenceDiagram
    participant User
    participant App as Python app
    participant Jev
    participant Router as Python router

    User->>App: Enter support ticket
    App->>Jev: Send ticket as state
    Jev-->>App: Choice category
    Jev-->>App: Noul urgency probability
    Jev-->>App: Score severity
    App->>Router: Pass typed decision object
    Router-->>App: Team, queue, escalation
    App-->>User: Display analysis and route
```

## Jev Decisions

| Question | Jev type | Example output | Meaning |
| --- | --- | --- | --- |
| Which team should handle this? | `Choice` | `BILLING` | One label from a fixed list |
| Is it urgent? | `Noul` | `0.82` | Probability of yes |
| How severe is it? | `Score` | `4 / 5` | Ordered severity level |

## Routing Flow

```mermaid
flowchart TD
    A[Category from Jev] --> B{Category}
    B -->|BILLING| C[billing-support]
    B -->|TECHNICAL| D[technical-support]
    B -->|SALES| E[sales]
    B -->|GENERAL| F[general-support]

    G[Severity from Jev] --> H{Displayed severity}
    H -->|1, 2, 3| I[No escalation]
    H -->|4, 5| J[Escalate]
```

## Project Map

```mermaid
flowchart LR
    app[app.py] --> client[jev_client.py]
    ui[streamlit_app.py] --> client
    client --> models[models.py]
    app --> router[router.py]
    ui --> router

    eval[evaluate.py] --> client
    eval --> data[evaluation_data.py]
    eval --> metrics[metrics.py]
    eval --> cal[calibration.py]
    data --> labels[data/labeled_tickets.json]

    tests[tests] --> models
    tests --> router
    tests --> metrics
    tests --> cal
    tests --> data
```

## Files At A Glance

| File | Role |
| --- | --- |
| `app.py` | Terminal demo |
| `streamlit_app.py` | Browser UI |
| `jev_client.py` | TypeSafe SDK and Jev questions |
| `models.py` | Typed categories, severity rubric, decision model |
| `router.py` | Team routing and escalation rule |
| `evaluate.py` | Runs labeled evaluation |
| `metrics.py` | Accuracy, precision, recall, F1 |
| `calibration.py` | Confidence calibration |
| `data/labeled_tickets.json` | 50 labeled examples |
| `tests/` | Unit tests |

## Quick Start

```mermaid
flowchart LR
    A[Create venv] --> B[Install requirements]
    B --> C[Add TYPESAFE_API_KEY]
    C --> D[Run terminal app]
    C --> E[Run Streamlit UI]
    C --> F[Run evaluation]
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create `.env`:

```text
TYPESAFE_API_KEY=your_typesafe_api_key_here
```

## Run

| Use case | Command |
| --- | --- |
| Terminal demo | `python app.py` |
| Streamlit UI | `python -m streamlit run streamlit_app.py` |
| Full evaluation | `python evaluate.py` |
| Small evaluation smoke test | `python evaluate.py --limit 5` |
| Unit tests | `python -m unittest discover` |

## Example Output

```text
Input:
Payment was deducted twice from my account.

Ticket Analysis
Category: BILLING
Urgent: NO
Urgency probability: 0.1234
Severity: 4 / 5

Routing Decision
Team: Billing
Queue: billing-support
Escalate: YES
Route to the billing support team.
```

## Evaluation Flow

```mermaid
flowchart TB
    A[50 labeled tickets] --> B[Call Jev for each ticket]
    B --> C[Predictions]
    C --> D[Compare with labels]
    D --> E[Category metrics]
    D --> F[Urgency metrics]
    D --> G[Severity metrics]
    D --> H[Escalation metrics]
    D --> I[Calibration analysis]
```

Metrics reported:

| Area | Metrics |
| --- | --- |
| Category | accuracy, precision, recall, F1 |
| Urgency | accuracy, precision, recall, F1 |
| Severity | accuracy, precision, recall, F1, within-one accuracy |
| Escalation | accuracy, precision, recall, F1 |
| Confidence | calibration bins, expected calibration error |

## Calibration Flow

```mermaid
flowchart LR
    A[Jev confidence] --> B[Confidence bins]
    C[Correctness] --> B
    B --> D[Average confidence]
    B --> E[Actual accuracy]
    D --> F[Expected calibration error]
    E --> F
```

Calibration asks whether confidence matches reality. If Jev is about `80%` confident, a well-calibrated system should be correct about `80%` of the time in that bin.

## Learning Notes

```mermaid
flowchart TB
    A[Jev is used for decisions] --> B[Typed outputs]
    B --> C[Application code uses those outputs]
    C --> D[Metrics evaluate behavior]
    D --> E[Calibration evaluates confidence]
```

- Jev decisions are typed: `Choice`, `Noul`, and `Score`.
- Python does the deterministic routing and escalation.
- `.env` stores the TypeSafe API key and must not be committed.
- The TypeSafe SDK reports `Score` indexes as `0..4`; this project converts them to `1..5`.
- The 50 labeled tickets are for evaluation, not training.
