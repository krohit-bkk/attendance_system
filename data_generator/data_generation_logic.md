# Employee Attendance System — Data Generation Knowledge & Logic

This document captures the agreed data model, business rules, generation logic, relationships, and design decisions for the Employee Attendance System dummy-data generator.

The generator lives in:

```text
Attendance_System/
└── data_generator/
    ├── app.py
    └── output/
```

All generation logic is kept in `data_generator/app.py`. Generated CSV files are written under `data_generator/output/`.

---

# 1. General Generation Principles

## 1.1 Deterministic generation

A common random seed is used:

```python
SEED = 42
```

The generator should remain reproducible for the same configuration.

## 1.2 Date format

Dates use:

```text
yyyy-MM-dd
```

Example:

```text
2026-03-02
```

## 1.3 Employee identity

`Employee_ID` is **not globally unique**. It is unique only within an organization.

Therefore, the effective employee business key is:

```text
(Org_ID, Employee_ID)
```

Any employee-specific dictionary, lookup, join, or grouping must use both `Org_ID` and `Employee_ID`.

For example:

| Org_ID | Employee_ID | Meaning |
|---:|---:|---|
| 1 | 1 | Employee 1 of Organization 1 |
| 2 | 1 | Employee 1 of Organization 2 |

These are two different employees.

---

# 2. Entity: Organization

## Schema

| Column | Description |
|---|---|
| `Org_ID` | Organization identifier |
| `Org_Name` | Organization name |
| `Head_Office_Address` | Dummy head-office address |
| `Country` | Organization's country |

## Generation rules

Generate 10 organizations.

```text
Org_ID   : 1–10
Org_Name : Company A–Company J
```

Countries are randomly selected from:

- India
- United States
- Germany
- Thailand
- Singapore
- Australia
- Canada
- Japan
- Netherlands
- United Kingdom

Output:

```text
organization.csv
```

---

# 3. Entity: Employee

## Schema

| Column | Description |
|---|---|
| `ID` | Globally unique primary key |
| `Employee_ID` | Employee identifier within organization |
| `Org_ID` | Organization |
| `Employee_Name` | Employee name |
| `Gender` | Male/Female |
| `Date_Of_Joining` | Date employee joined |
| `Date_of_Birth` | Employee date of birth |
| `Date_Of_Anniversary` | Optional anniversary date |

## Generation rules

For each organization:

- Generate a random employee count between 15 and 500.
- `ID` is globally unique and incremental.
- `Employee_ID` is unique only within the organization.
- Employee names do not need to be unique.
- Gender is randomly selected.
- `Date_Of_Joining` is generated between `2020-01-01` and `2025-12-31`.
- `Date_of_Birth` is generated between `1980-01-01` and `2005-12-31`.
- `Date_Of_Anniversary` is NULL for approximately 60% of employees.
- Otherwise, anniversary is generated between `2010-01-01` and `2025-12-31`.

Output:

```text
employee.csv
```

---

# 4. Entity: Organization_Level_Settings

Organization-level attendance configuration is kept separately from Shift.

## Schema

| Column | Description |
|---|---|
| `Org_ID` | Organization |
| `Buffer_In_Time` | Allowed early-arrival buffer - How early an employee is allowed in a shift?|
| `Buffer_Out_Time` | Allowed late-departure buffer - How late an employee can stay in a shift?|
| `Grace_Period` | Attendance grace period - Relaxation for full day attendance |
| `Is_Single_Punch_Enabled` | Whether one punch can qualify for attendance |
| `Is_Birthday_Enabled` | Whether birthday attendance rule is enabled |
| `Is_Anniversary_Enabled` | Whether anniversary attendance rule is enabled |

## Generation rules

For each organization:

- `Buffer_In_Time`: random 15–90 minutes.
- `Buffer_Out_Time`: random 15–90 minutes.
- `Grace_Period`: random 0–30 minutes.
- `Is_Single_Punch_Enabled`: enabled for approximately 30% of organizations.
- `Is_Birthday_Enabled`: enabled for approximately 70% of organizations.
- `Is_Anniversary_Enabled`: enabled for approximately 50% of organizations.

These settings are organization-level rules and are therefore not duplicated in Shift.

Output:

```text
organization_level_settings.csv
```

---

# 5. Entity: Shift

## Schema

| Column | Description |
|---|---|
| `Shift_ID` | Shift record identifier |
| `Org_ID` | Organization |
| `Employee_ID` | Employee within organization |
| `Shift_Type` | Shift classification |
| `Shift_Start_Date` | Start of assigned shift period |
| `Shift_End_Date` | End of assigned shift period |
| `Shift_Start_Time` | Daily shift start |
| `Shift_End_Time` | Daily shift end |

## Shift types

- `Regular Shift`
- `Morning Shift`
- `Afternoon Shift`
- `Night Shift`
- `Week Off`

## Shift timings

| Shift Type | Start | End |
|---|---:|---:|
| Regular Shift | `09:00` | `18:00` |
| Morning Shift | `06:30` | `15:30` |
| Afternoon Shift | `14:30` | `23:30` |
| Night Shift | `22:30` | (date+1) `07:30` |
| Week Off | NULL | NULL |

## Important design decision

The following values are intentionally **not** stored in Shift:

- `Buffer_In_Time`
- `Buffer_Out_Time`
- `Grace_Period`
- `Is_Single_Punch_Enabled`
- `Is_Birthday_Enabled`
- `Is_Anniversary_Enabled`

They belong to `Organization_Level_Settings`.

## Generation granularity

Shift records are generated at weekly granularity.

Working days are Monday–Friday and week-offs are Saturday–Sunday.

For the current sample period:

```text
2026-03-01 to 2026-04-04
```

the working weeks are:

```text
2026-03-02 to 2026-03-06
2026-03-09 to 2026-03-13
2026-03-16 to 2026-03-20
2026-03-23 to 2026-03-27
2026-03-30 to 2026-04-03
```

The generator should not create records outside the requested inclusive date range.

## Shift assignment

Approximately three organizations use only `Regular Shift` for working days.

Other organizations use randomized combinations of:

- Morning Shift
- Afternoon Shift
- Night Shift

Shift repetition is allowed.

The following transitions are explicitly forbidden:

```text
Morning   -> Afternoon
Afternoon -> Night
Night     -> Morning
```

Allowed examples:

```text
Morning   -> Morning
Morning   -> Night

Afternoon -> Afternoon
Afternoon -> Morning

Night     -> Night
Night     -> Afternoon
```

The first working shift should be selected randomly. Subsequent working shifts are selected using the transition rules.

---

# 6. Entity: Holiday_Calendar

## Schema

| Column | Description |
|---|---|
| `ID` | Holiday record identifier |
| `Org_ID` | Organization |
| `Holiday_Date` | Holiday date |
| `Holiday_Type` | Holiday classification |

## Holiday types

Examples:

```text
National Holiday
Restricted Holiday
```

## Generation logic

The organization's country is used to determine national holidays.

The Python `holidays` package can be used to obtain country-specific national holidays.

The year is derived from the generation period:

```python
year = int(start_date[0:4])
```

Restricted holidays are generated separately because there is no universal country-independent classification.

The organization relationship is maintained through `Org_ID`.

---

# 7. Entity: Default_Rules

## Schema

| Column | Description |
|---|---|
| `Rule_ID` | Rule identifier |
| `Org_ID` | Organization |
| `Special_Executive_ID` | `Employee_ID` of special executive |

## Special executives

Approximately 1–3% of employees from each organization are randomly selected as special executives.

They represent top executives who do not follow normal shift-based attendance.

The downstream default attendance behavior is:

```text
Special Executive -> Present
```

even when normal punch records are absent.

## Important rule

Special executives **can still apply for leave**.

They must not be excluded from Leave generation.

---

# 8. Entity: Leave

## Schema

| Column | Description |
|---|---|
| `ID` | Leave identifier |
| `Org_ID` | Organization |
| `Employee_ID` | Employee |
| `Leave_Start_Date` | Leave start |
| `Leave_End_Date` | Leave end |
| `Leave_Type` | Leave classification |

## Leave types

```text
Full Day Leave
Half Day Leave
```

## Generation probability

Leave generation uses approximately:

```text
0.5% probability per employee per working day
```

Week-off days are skipped.

Holidays are not explicitly excluded from leave generation.

## Full-day leave

A full-day leave can cover multiple consecutive dates in one row.

Example:

| Org_ID | Employee_ID | Leave_Start_Date | Leave_End_Date | Leave_Type |
|---:|---:|---|---|---|
| 1 | 3 | 2026-03-02 | 2026-03-04 | Full Day Leave |

## Half-day leave

Each half-day leave is represented by one row per day.

Example:

| Org_ID | Employee_ID | Leave_Start_Date | Leave_End_Date | Leave_Type |
|---:|---:|---|---|---|
| 1 | 3 | 2026-03-02 | 2026-03-02 | Half Day Leave |
| 1 | 3 | 2026-03-03 | 2026-03-03 | Half Day Leave |

Overlapping leave records are currently allowed.

Special executives can also receive leave records.

Output:

```text
leave.csv
```

---

# 9. Entity: Employee_Punch

## Schema

| Column | Description |
|---|---|
| `ID` | Punch identifier |
| `Org_ID` | Organization |
| `Employee_ID` | Employee |
| `Punch_Date` | Date of punch |
| `Punch_Time` | Time of punch |
| `Medium` | Punch medium |

## Punch mediums

```text
WebApp
MobileApp
POS
```

---

# 10. Employee Punch Generation Philosophy

The Punch generator should simulate **organic employee behavior**, not merely produce uniformly random timestamps.

A completely uniform distribution across a large ±4-hour window can generate unrealistic data.

Employees generally have more relevant activity around:

1. Start of shift
2. During the working period
3. End of shift

Therefore, punches are generated using three behavioral segments.

---

# 11. Punch Window

For every working shift, the raw punch-generation window is:

```text
4 hours before shift start
        through
4 hours after shift end
```

For a `09:00–18:00` shift:

```text
04:00 -------- 09:00 ---------------- 18:00 -------- 22:00
     START              MIDDLE               END
```

The boundaries are derived dynamically from the actual shift times.

---

# 12. Punch Segments

## 12.1 Start segment

Represents arrival-related punches.

Example:

```text
08:45
08:58
09:03
09:12
```

## 12.2 Middle segment

Represents activity during the working period.

Example:

```text
12:15
12:45
13:30
15:10
```

## 12.3 End segment

Represents departure-related activity.

Example:

```text
17:45
17:58
18:05
18:20
```

---

# 13. Punch Count

For every employee and working day:

```python
punch_count = random.randint(0, 20)
```

This intentionally allows:

- 0 punches
- 1 punch
- multiple punches

The generated count is the potential number of punches before missing-start/end behavior is applied.

---

# 14. Organic Punch Distribution

The punch count is not divided equally between the three segments.

Current segment weights are:

| Segment | Weight |
|---|---:|
| Start | 30% |
| Middle | 40% |
| End | 30% |

For example, 10 potential punches could result in:

```text
Start   = 3
Middle  = 5
End     = 2
```

or:

```text
Start   = 2
Middle  = 4
End     = 4
```

or another randomized combination.

Within each segment, individual timestamps are randomized.

This provides organic variation while retaining realistic concentration around shift boundaries.

---

# 15. Missing Start/End Swipes

Missing swipes are deliberately simulated because they are required to test Attendance processing.

There are two categories of employees.

## 15.1 Normal employees

Normal employees have a small daily probability of missing a start or end swipe.

Current conceptual probabilities:

```text
Missing start ≈ 3%
Missing end   ≈ 3%
```

These probabilities are applied independently on working days.

Therefore, a normal employee may occasionally produce:

```text
Start + Middle
```

with no end swipe, or:

```text
Middle + End
```

with no start swipe.

## 15.2 Miss-prone employees

Approximately 1–5% of employees from each organization are designated as miss-prone.

Each selected employee is assigned one behavior:

```text
START_MISS_PRONE
```

or:

```text
END_MISS_PRONE
```

This does **not** mean the employee permanently misses that swipe.

Instead, the employee has a higher daily probability of missing it.

Current conceptual probabilities:

```text
START_MISS_PRONE:
    Start miss ≈ 65%
    End miss   ≈ normal probability

END_MISS_PRONE:
    End miss   ≈ 65%
    Start miss ≈ normal probability
```

This produces a spectrum:

```text
Perfect employee
       ↓
Occasionally misses
       ↓
Frequently misses
```

rather than a permanent missing-punch condition.

---

# 16. Why Missing Punches Matter

The generator should naturally produce scenarios such as:

## No punches

```text
No punch records
```

Potential downstream outcomes include:

```text
Absent
Leave
Holiday
Birthday
Anniversary
Executive Present
```

depending on Attendance rules.

## Single punch

```text
09:05
```

Potentially:

```text
Present
Half Day
Absent
```

depending on organization settings and Attendance rules.

## Missing start

```text
12:10
13:00
17:55
```

## Missing end

```text
08:55
12:15
13:05
```

## Normal day

```text
08:55
12:20
13:10
17:58
```

These cases are important for testing the downstream Attendance engine.

---

# 17. Overnight Shift Handling

Night Shift is:

```text
22:30 -> 07:30 next day
```

The end datetime must therefore be treated as the following calendar day.

Conceptually:

```python
shift_start_datetime = datetime.strptime(
    f"{current_date_str} {shift_start_time}",
    "%Y-%m-%d %H:%M"
)

shift_end_datetime = datetime.strptime(
    f"{current_date_str} {shift_end_time}",
    "%Y-%m-%d %H:%M"
)

if shift_end_datetime <= shift_start_datetime:
    shift_end_datetime += timedelta(days=1)
```

Punch generation uses these datetime values when constructing the punch window.

A punch belonging to a night shift can therefore have a `Punch_Date` on the next calendar day.

The Attendance generator must account for this when associating punches with shifts.

---

# 18. Shift Lookup Key

The correct Shift lookup key is:

```python
(
    Org_ID,
    Employee_ID,
    Date
)
```

Example:

```python
shift_lookup[
    (
        org_id,
        employee_id,
        current_date_str
    )
]
```

This is mandatory because `Employee_ID` is organization-scoped.

The following is incorrect:

```python
shift_lookup[
    (employee_id, current_date_str)
]
```

It creates collisions such as:

```text
Organization 1 / Employee 1 / 2026-03-02
Organization 2 / Employee 1 / 2026-03-02
```

The corrected lookup distinguishes them:

```text
(1, 1, "2026-03-02")
(2, 1, "2026-03-02")
```

---

# 19. Punch Output Ordering

After generation, Punch records should be sorted by:

```text
Org_ID
Employee_ID
Punch_Date
Punch_Time
```

Then IDs can be re-sequenced:

```python
df["ID"] = range(1, len(df) + 1)
```

This produces deterministic, easy-to-inspect output.

---

# 20. Entity Relationships

The high-level relationship is:

```text
Organization
    |
    +---- Organization_Level_Settings
    |
    +---- Employee
             |
             +---- Shift
             |
             +---- Leave
             |
             +---- Employee_Punch
             |
             +---- Default_Rules
```

Employee identity is generally:

```text
(Org_ID, Employee_ID)
```

rather than `Employee_ID` alone.

---

# 21. Attendance Output — Downstream Entity

The generated input entities will eventually feed the Attendance output.

## Schema

| Column | Description |
|---|---|
| `ID` | Attendance identifier |
| `Org_ID` | Organization |
| `Employee_ID` | Employee |
| `Date` | Attendance date |
| `Shift_ID` | Applicable shift |
| `Shift_Start_Date` | Shift period start |
| `Shift_End_Date` | Shift period end |
| `Punch_In_Time` | Derived first relevant punch |
| `Punch_Out_Time` | Derived last relevant punch |
| `Attendance_Status` | Calculated status |

## Possible Attendance statuses

```text
Present
Leave
Half Day Leave
Absent
Comp-off
Holiday
Anniversary
Birthday
```

The exact priority and calculation rules are to be finalized when the Attendance generator is implemented.

---

# 22. Inputs to Attendance Processing

Attendance will eventually combine:

```text
Organization_Level_Settings
        +
Shift
        +
Holiday_Calendar
        +
Default_Rules
        +
Leave
        +
Employee_Punch
        +
Employee
```

## Organization_Level_Settings

Controls:

- Buffer In
- Buffer Out
- Grace Period
- Single Punch
- Birthday
- Anniversary

## Shift

Controls:

- Expected working period
- Shift boundaries
- Overnight shift interpretation
- Applicable Shift_ID

## Holiday_Calendar

Controls:

```text
Holiday
```

attendance scenarios.

## Leave

Controls:

```text
Leave
Half Day Leave
```

attendance scenarios.

## Default_Rules

Identifies special executives.

## Employee

Provides:

- Date of birth
- Anniversary
- Employee identity

## Employee_Punch

Provides:

- Raw punch events
- Candidate punch-in
- Candidate punch-out
- Worked-duration information
- Missing-punch scenarios

---

# 23. Special Executive Attendance

Special executives are identified through:

```text
Default_Rules.Special_Executive_ID
```

Their default attendance behavior is:

```text
Present
```

even if normal punch records are absent.

However:

```text
Special Executive + Leave
```

must remain possible.

The Attendance engine will need to establish the final precedence between executive rules and leave rules.

---

# 24. Single Punch Attendance

The organization-level setting:

```text
Is_Single_Punch_Enabled
```

determines whether a single punch can qualify for attendance.

The Punch generator deliberately creates single-punch cases.

Conceptually:

```text
One punch
   |
   +-- Single Punch Enabled
   |       -> potentially Present
   |
   +-- Single Punch Disabled
           -> potentially Half Day / Absent
```

The final classification belongs to Attendance processing, not raw Punch generation.

---

# 25. Grace Period

Grace Period is an organization-level setting.

One agreed attendance concept is that calculated worked duration can be evaluated with the organization's Grace Period when determining whether the employee satisfies the expected shift duration.

For example:

```text
Shift duration = 9 hours
Grace Period   = 30 minutes
```

The exact threshold formula should be finalized during Attendance implementation.

---

# 26. Buffer Time

Buffer times define how far outside nominal shift boundaries punches can still be considered relevant to that shift.

Example:

```text
Shift:
06:30 -> 15:30

Buffer In:
02:00

Buffer Out:
01:00
```

Relevant punches may therefore be considered within:

```text
04:30 -> 16:30
```

The Punch generator currently uses a generic ±4-hour raw-generation window.

The downstream Attendance logic can apply organization-specific Buffer In/Out settings when determining which raw punches belong to the shift.

---

# 27. Data Quality Philosophy

The generator should deliberately contain both normal and abnormal cases.

Useful test cases include:

- Employees with no punches
- Employees with one punch
- Employees with multiple punches
- Missing start punches
- Missing end punches
- Early punches
- Late punches
- Early departures
- Overnight punches
- Employees on leave
- Employees on holidays
- Special executives
- Birthday/anniversary candidates
- Week-offs
- Different shift types
- Different organization settings

The objective is not to generate perfect employee behavior.

The objective is to generate **realistic variation that exercises downstream business rules**.

---

# 28. Current Sample Generation Period

Current sample period:

```text
Start Date: 2026-03-01
End Date:   2026-04-04
```

Both endpoints are inclusive.

When weekly Shift records are generated, the generator should not create records beyond `2026-04-04`.

---

# 29. Current Generation Flow

The current generation sequence is:

```python
if __name__ == "__main__":

    start_date = "2026-03-01"
    end_date   = "2026-04-04"

    org_df = generate_organizations()

    emp_df = generate_employees(
        org_df=org_df
    )

    org_settings_df = (
        generate_organization_level_settings(
            org_df=org_df
        )
    )

    shift_df = generate_shifts(
        org_df=org_df,
        emp_df=emp_df,
        start_date=start_date,
        end_date=end_date
    )

    holiday_df = generate_holiday_calendar(
        org_df=org_df,
        year=int(start_date[0:4])
    )

    default_rules_df = generate_default_rules(
        emp_df=emp_df
    )

    leaves_df = generate_leaves(
        emp_df=emp_df,
        shift_df=shift_df
    )

    punch_df = generate_employee_punches(
        emp_df=emp_df,
        shift_df=shift_df,
        start_date=start_date,
        end_date=end_date
    )
```

The next major processing stage is the Attendance generator.

---

# 30. Key Design Decisions

## Employee_ID is organization-scoped

Always use:

```text
(Org_ID, Employee_ID)
```

for employee identity.

## Organization settings are separate from Shift

Do not duplicate organization-level attendance configuration in every Shift row.

## Punches simulate behavior

Uniform random timestamps are insufficient.

Punches should be concentrated behaviorally around:

```text
Start / Middle / End
```

of the shift.

## Missing punches are intentional

Missing start/end swipes are required to properly test Attendance logic.

## Miss-prone employees are probabilistic

The 1–5% miss-prone population has an increased probability of missing a particular side; it does not permanently miss that swipe.

## Raw Punch remains raw

Do not add an `IN`/`OUT` flag to `Employee_Punch` simply to simplify Attendance processing.

Attendance should infer relevant punch-in/punch-out information from raw chronological punches and shift context.

## Overnight shifts require datetime-aware processing

A shift such as:

```text
22:30 -> 07:30
```

must be treated as crossing midnight.

## Imperfect data is intentional

The generator is a testing tool. Missing, incomplete, and irregular punch behavior is valuable because it allows the Attendance engine to be tested against realistic edge cases.
