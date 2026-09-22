# JevTicket

Phase 8 of a small support-ticket decision app for learning Jev by TypeSafe AI.

This phase proves the first useful app workflow:

```text
support ticket -> Jev questions -> category + urgency + severity -> Python router -> support queue + escalation
```

## What Phase 4 Does

The app sends one test support ticket to Jev:

```text
Payment was deducted twice from my account.
```

It asks Jev three typed questions:

- a `Choice` question: which category is this ticket?
- a `Noul` question: does this ticket require urgent attention?
- a `Score` question: how severe is this ticket on a 1 to 5 scale?

The allowed categories are:

- `BILLING`
- `TECHNICAL`
- `SALES`
- `GENERAL`

The Python application prints the selected category. If Jev returns confidence or probabilities for the choice, the app prints those too.

For urgency, Jev returns a yes-probability from `0` to `1`. The app displays:

- `Urgent: YES` when the probability is at least `0.5`
- `Urgent: NO` when the probability is below `0.5`

`Noul` returns a probability, not a separate confidence value.

For severity, Jev returns a probability-weighted score over the five rubric levels. The SDK reports level indexes as `0..4`, and the app converts them to the learning scale `1..5`. The app displays the nearest integer as `Severity: n / 5` and also prints any score probability/confidence values returned by Jev.

Then normal Python code routes the ticket:

- `BILLING` -> `billing-support`
- `TECHNICAL` -> `technical-support`
- `SALES` -> `sales`
- `GENERAL` -> `general-support`

Normal Python code also decides escalation:

- displayed severity `4` or `5` -> escalate
- displayed severity `1`, `2`, or `3` -> do not escalate

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and set your TypeSafe API key:

```text
TYPESAFE_API_KEY=your_typesafe_api_key_here
```

## Run

Terminal version:

```powershell
python app.py
```

Streamlit UI:

```powershell
python -m streamlit run streamlit_app.py
```

Expected shape of the output:

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

If Jev returns confidence or probabilities through the API response, they will be printed after the category. The app does not invent probability values.

## Jev-Specific Code

The Jev-specific part is in `jev_client.py`.

It sends:

- `state`: the ticket text
- `questions`: one typed SDK `Choice` question named `category`
- `questions`: one typed SDK `Noul` question named `urgent`
- `questions`: one typed SDK `Score` question named `severity`
- `criteria`: the four allowed category labels and their meanings

The rest is normal Python:

- loading `.env`
- creating a TypeSafe SDK client
- validating the returned category
- routing the ticket in `router.py`
- deciding escalation in normal Python
- printing the result

## Streamlit UI

Phase 5 adds `streamlit_app.py`. It uses the same `JevClient` and `route_ticket` logic as the terminal app, then displays the results with Streamlit metrics and probability charts.

## Labeled Test Tickets

Phase 6 adds `data/labeled_tickets.json` with 50 hand-labeled support tickets. Each example includes:

- `ticket_id`
- `message`
- expected `category`
- expected `urgent` label
- expected `severity` on the `1..5` scale

The dataset is for later evaluation. It is not used to train Jev or change Jev's decisions.

## Evaluation Metrics

Phase 7 adds `evaluate.py` and `metrics.py`.

Run the full labeled evaluation:

```powershell
python evaluate.py
```

Run a smaller smoke evaluation:

```powershell
python evaluate.py --limit 5
```

The evaluation calls Jev for each labeled ticket, then reports:

- category macro accuracy, precision, recall, and F1
- urgency accuracy, precision, recall, and F1
- severity macro accuracy, precision, recall, and F1
- escalation accuracy, precision, recall, and F1
- severity within-one accuracy

## Calibration Analysis

Phase 8 adds confidence calibration analysis. Calibration asks:

```text
When Jev says it is about 80% confident, is it correct about 80% of the time?
```

`evaluate.py` now also prints calibration bins and expected calibration error for:

- category confidence
- urgency confidence derived from the predicted side of the `Noul` probability
- severity confidence

Lower expected calibration error is better. With only 50 tickets, treat this as a learning exercise and rough diagnostic rather than a statistically stable benchmark.

## Tests

The router is deterministic, so it can be tested without calling Jev:

```powershell
python -m unittest discover
```

## Documentation Notes

Jev is in early access and requires an API key. The current documented HTTP endpoint is:

```text
POST https://api.typesafe.ai/v1/systemone
```

The official Python package is `typesafe-sdk`. The app uses `TYPESAFE_API_KEY` and `TYPESAFE_DEFAULT_MODEL`, matching the TypeSafe SDK environment variable names.
