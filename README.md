# JevTicket

JevTicket is a small support-ticket decision and routing app built for learning Jev by TypeSafe AI.

It demonstrates this workflow:

```text
support ticket -> Jev decisions -> Python routing -> evaluation metrics
```

## What It Does

Given a customer-support message, the app asks Jev three typed questions:

- `Choice`: classify the ticket category
- `Noul`: estimate whether the ticket is urgent
- `Score`: rate severity on a 1 to 5 scale

The allowed categories are:

- `BILLING`
- `TECHNICAL`
- `SALES`
- `GENERAL`

Normal Python code then routes the ticket:

- `BILLING` -> `billing-support`
- `TECHNICAL` -> `technical-support`
- `SALES` -> `sales`
- `GENERAL` -> `general-support`

Normal Python code also decides escalation:

- displayed severity `4` or `5` -> escalate
- displayed severity `1`, `2`, or `3` -> do not escalate

## Project Structure

```text
JevTicket/
├── app.py
├── streamlit_app.py
├── jev_client.py
├── models.py
├── router.py
├── config.py
├── evaluation_data.py
├── evaluate.py
├── metrics.py
├── calibration.py
├── data/
│   └── labeled_tickets.json
├── tests/
│   ├── test_calibration.py
│   ├── test_evaluation_data.py
│   ├── test_metrics.py
│   ├── test_models.py
│   └── test_router.py
├── requirements.txt
├── .env.example
└── README.md
```

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

Create a `.env` file from `.env.example`:

```text
TYPESAFE_API_KEY=your_typesafe_api_key_here
```

Never commit `.env`; it is ignored by `.gitignore`.

## Run

Terminal version:

```powershell
python app.py
```

Streamlit UI:

```powershell
python -m streamlit run streamlit_app.py
```

Expected output shape:

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

If Jev returns confidence or probability information, the app prints it. The app does not fabricate confidence values.

## Jev Concepts Used

The Jev-specific code lives in `jev_client.py`.

It sends:

- `state`: the support ticket text
- `Choice`: category decision
- `Noul`: urgency probability
- `Score`: severity rating

The normal Python code handles:

- loading `.env`
- validating returned values
- routing tickets
- deciding escalation
- rendering terminal and Streamlit output
- calculating evaluation metrics

One important detail: the TypeSafe SDK reports `Score` levels as zero-based indexes for the rubric. This project converts them to the learning scale `1..5`.

## Evaluation Dataset

`data/labeled_tickets.json` contains 50 hand-labeled support tickets. Each example includes:

- `ticket_id`
- `message`
- expected `category`
- expected `urgent` label
- expected `severity`

The dataset is used for evaluation only. It does not train Jev or change Jev's decisions.

## Evaluation Metrics

Run the full labeled evaluation:

```powershell
python evaluate.py
```

Run a smaller smoke evaluation:

```powershell
python evaluate.py --limit 5
```

The evaluator reports:

- category accuracy, precision, recall, and F1
- urgency accuracy, precision, recall, and F1
- severity accuracy, precision, recall, and F1
- escalation accuracy, precision, recall, and F1
- severity within-one accuracy

## Calibration Analysis

The evaluator also reports calibration bins and expected calibration error.

Calibration asks:

```text
When Jev says it is about 80% confident, is it correct about 80% of the time?
```

Calibration is calculated for:

- category confidence
- urgency confidence derived from the predicted side of the `Noul` probability
- severity confidence

Lower expected calibration error is better. With only 50 tickets, treat this as a learning diagnostic rather than a final benchmark.

## Tests

Run all tests:

```powershell
python -m unittest discover
```

The tests cover:

- routing logic
- model properties
- labeled dataset validation
- metrics
- calibration

## Dependencies

Core dependencies are intentionally minimal:

- `typesafe-sdk`
- `pydantic`
- `python-dotenv`
- `streamlit`

## Documentation Notes

Jev is in early access and requires a TypeSafe API key.

The official Python package used here is `typesafe-sdk`. The app uses `TYPESAFE_API_KEY` and `TYPESAFE_DEFAULT_MODEL`, matching the TypeSafe SDK environment variable names.
