# Employee Attendance System — Attendance Status Assignment

## 1. Problem Statement

You are given a set of employee master data, organization-level attendance settings, shift assignments, holiday calendars, leave records, default rules, and raw employee punch/swipe data.

Your task is to build an **Attendance Processing Engine** that determines the attendance status of every employee for every applicable calendar date.

The solution should use the available input entities and apply the organization's attendance rules to determine the final attendance status.

The objective is not simply to count punches. The objective is to determine attendance by combining:

- Employee information
- Organization-level rules
- Shift assignment
- Holidays
- Week-offs
- Leave
- Employee punches
- Special-executive rules
- Birthday and anniversary rules

---

# 2. Expected Output

Generate an Attendance dataset with the following schema:

| Column | Description |
|---|---|
| `ID` | Globally unique Attendance record ID |
| `Org_ID` | Organization |
| `Employee_ID` | Employee identifier within organization |
| `Date` | Attendance date |
| `Shift_ID` | Applicable shift record |
| `Shift_Start_Date` | Start date of the applicable shift period |
| `Shift_End_Date` | End date of the applicable shift period |
| `Punch_In_Time` | First relevant punch for the attendance day |
| `Punch_Out_Time` | Last relevant punch for the attendance day |
| `Attendance_Status` | Final calculated attendance status |

The final `Attendance_Status` must contain only one of:

```text
PRESENT
HALF-DAY
ABSENT
FULL DAY LEAVE
HALF DAY LEAVE + PRESENT
HALF DAY LEAVE + HALF DAY ABSENT
HOLIDAY
WEEK-OFF
BIRTHDAY
ANNIVERSARY
```

`COMP-OFF` is **not** part of this exercise.

Comp-off is considered an operational override between an employee and manager and is outside the scope of this assignment.

---

# 3. Input Data

Students should use the following generated input datasets.

## Organization

Contains:

- `Org_ID`
- `Org_Name`
- `Head_Office_Address`
- `Country`

## Employee

Contains:

- `ID`
- `Employee_ID`
- `Org_ID`
- `Employee_Name`
- `Gender`
- `Date_Of_Joining`
- `Date_of_Birth`
- `Date_Of_Anniversary`

## Organization_Level_Settings

Contains:

- `Org_ID`
- `Buffer_In_Time`
- `Buffer_Out_Time`
- `Grace_Period`
- `Is_Single_Punch_Enabled`
- `Is_Birthday_Enabled`
- `Is_Anniversary_Enabled`

## Shift

Contains:

- `Shift_ID`
- `Org_ID`
- `Employee_ID`
- `Shift_Type`
- `Shift_Start_Date`
- `Shift_End_Date`
- `Shift_Start_Time`
- `Shift_End_Time`

Possible shift types:

```text
Regular Shift
Morning Shift
Afternoon Shift
Night Shift
Week Off
```

## Holiday_Calendar

Contains:

- `ID`
- `Org_ID`
- `Holiday_Date`
- `Holiday_Type`

## Default_Rules

Contains:

- `Rule_ID`
- `Org_ID`
- `Special_Executive_ID`

A `Special_Executive_ID` is an `Employee_ID` belonging to that organization.

## Leave

Contains:

- `ID`
- `Org_ID`
- `Employee_ID`
- `Leave_Start_Date`
- `Leave_End_Date`
- `Leave_Type`

Possible leave types:

```text
Full Day Leave
Half Day Leave
```

## Employee_Punch

Contains:

- `ID`
- `Org_ID`
- `Employee_ID`
- `Punch_Date`
- `Punch_Time`
- `Medium`

Possible punch mediums:

```text
WebApp
MobileApp
POS
```

---

# 4. Important Employee Identity Rule

`Employee_ID` is unique only within an organization.

Therefore:

```text
(Org_ID, Employee_ID)
```

must be treated as the employee's business key.

For example:

| Org_ID | Employee_ID |
|---:|---:|
| 1 | 1 |
| 2 | 1 |

These represent two different employees.

Do not use `Employee_ID` alone when joining or looking up records.

---

# 5. Attendance Granularity

The Attendance table should contain one logical attendance record per:

```text
(Org_ID, Employee_ID, Date)
```

for each date in the processing period.

The processing period is inclusive of both the configured start date and end date.

The expected result should therefore represent the attendance state of each employee for each applicable date, including days where the employee has no punch records.

---

# 6. The Central Question

For every employee and every date, answer:

> **What was this employee's attendance status on this date?**

The answer should be derived from the available data rather than from a single input table.

---

# 7. Step 1 — Identify the Applicable Shift

For each employee/date combination:

1. Find the Shift record applicable to the employee.
2. Use `(Org_ID, Employee_ID)` to identify the employee.
3. Determine whether the date falls within `Shift_Start_Date` and `Shift_End_Date`.
4. Determine the applicable shift type and shift start/end times.

If the applicable shift is:

```text
Week Off
```

the expected status will normally be:

```text
WEEK-OFF
```

No punch processing is required to classify a normal week-off.

---

# 8. Step 2 — Identify Holidays

Check the Holiday_Calendar for:

```text
Org_ID + Date
```

If the date is a holiday for the organization, it is a candidate for:

```text
HOLIDAY
```

Holiday processing should be organization-specific.

A holiday for Organization 1 does not automatically mean that the same date is a holiday for Organization 2.

---

# 9. Step 3 — Identify Leave

Check whether the employee has an applicable leave record for the date.

A leave record may span multiple days.

For example:

```text
2026-03-02 -> 2026-03-04
Full Day Leave
```

applies to:

```text
2026-03-02
2026-03-03
2026-03-04
```

A half-day leave record represents:

```text
HALF DAY LEAVE
```

for that date.

Students should correctly expand multi-day full-day leave ranges when determining daily attendance.

---

# 10. Step 4 — Identify Special Executives

Use Default_Rules to determine whether the employee is a special executive.

A special executive does not follow normal shift-based attendance requirements.

The default rule for a special executive is:

```text
PRESENT
```

even when normal punch records are absent.

However, special executives **can apply for leave**.

Therefore, the implementation must not simply classify every special executive as PRESENT without considering applicable leave and the final status-priority rules.

---

# 11. Step 5 — Identify Birthday and Anniversary

Use Employee data and Organization_Level_Settings.

## Birthday

If:

```text
Employee.Date_of_Birth
```

matches the attendance date by month and day, and:

```text
Is_Birthday_Enabled = True
```

then the date is a candidate for:

```text
BIRTHDAY
```

The year of birth should not be compared.

For example:

```text
Date_of_Birth = 1990-03-15
Attendance Date = 2026-03-15
```

is a birthday.

## Anniversary

If:

```text
Employee.Date_Of_Anniversary
```

matches the attendance date by month and day, and:

```text
Is_Anniversary_Enabled = True
```

then the date is a candidate for:

```text
ANNIVERSARY
```

The anniversary year should not be compared.

NULL anniversary values should not produce anniversary attendance.

---

# 12. Step 6 — Find Relevant Punches

For working days, identify the employee's punches relevant to the assigned shift.

The raw Punch data can contain:

- zero punches
- one punch
- multiple punches
- punches before shift start
- punches after shift end
- punches around breaks
- punches for overnight shifts

The organization's:

```text
Buffer_In_Time
Buffer_Out_Time
```

should be used to determine the relevant attendance window.

---

# 13. Buffer-In Rule

`Buffer_In_Time` represents how early an employee can punch and still have the punch considered relevant to the shift.

Example:

```text
Shift Start = 06:30
Buffer In   = 02:00
```

The earliest relevant punch is:

```text
04:30
```

A punch before 04:30 should not normally be treated as the employee's shift-entry punch.

---

# 14. Buffer-Out Rule

`Buffer_Out_Time` represents how late an employee can punch and still have the punch considered relevant to the shift.

Example:

```text
Shift End = 15:30
Buffer Out = 01:00
```

The latest relevant punch is:

```text
16:30
```

A punch after 16:30 should not normally be treated as the employee's shift-exit punch.

---

# 15. Punch-In and Punch-Out

The **relevant swipe window** would be from:
```text
[Shift Start Date-Time - Buffer_In_Time]
```
to:
```text
[Shift End Date-Time + Buffer_Out_Time]
```

The **relevant raw punches** are the ones which lie in the relevant swipe window and only these punches should be considered while calculating the employee's `Punch_In_Time` and `Punch_Out_Time`. 

For the applicable shift, determine:

```text
Punch_In_Time
Punch_Out_Time
```

from the relevant raw punches.

A basic interpretation is:

```text
Punch_In_Time  = first relevant punch
Punch_Out_Time = last relevant punch
```

The raw Punch table should remain unchanged. Do not add an IN/OUT classification to the source Punch data.

---

# 16. Overnight Shift

A Night Shift can cross midnight.

Example:

```text
Shift Start = 22:30
Shift End   = 07:30
```

For a shift beginning on:

```text
2026-03-02
```

the actual shift interval is:

```text
2026-03-02 22:30
        ->
2026-03-03 07:30
```

Therefore, a punch recorded on `2026-03-03` may still belong to the Night Shift that started on `2026-03-02`.

Students must not incorrectly treat the two times as a same-day interval.

---

# 17. Normal Full-Day/Half-Day Attendance

You can calculate the **effective shift duration** (in hours) as:

```text
Effective_Shift_Duration = [Shift End Date-Time] - [Shift Start Date-Time] - [Grace Period]
Half_Day_Duration = Effective_Shift_Duration/2 + 1
```

Similarly, the attendance duration for an employee would be:
```text
Effective_Attendance_Duration = [Punch_Out_Time] - [Punch_In_Time]
```

A normal working day with sufficient attendance should result in:

```text
IF 
       Effective_Attendance_Duration >= Effective_Shift_Duration, then "PRESENT"
ELSE IF 
       Effective_Attendance_Duration >= Half_Day_Duration, then "HALF DAY"
ELSE 
       "ABSENT"
```

A typical example:

```text
Shift:
09:00 -> 18:00

Punches:
08:55
12:20
13:10
17:58
```

The employee has both start and end activity and sufficient working duration.

---

# 18. Missing Punches

The generated Punch data deliberately contains incomplete attendance scenarios.

Students should handle at least:

### No punch

```text
No punches for the employee/date
```

### Single punch

```text
09:05
```

### Missing start

```text
12:10
13:00
17:55
```

### Missing end

```text
08:55
12:15
13:05
```

The correct status depends on the organization's attendance rules.

---

# 19. Single-Punch Rule

The organization-level setting:

```text
Is_Single_Punch_Enabled
```

controls how a single punch should be treated.

If enabled, a single punch may qualify as attendance.

If disabled, a single punch should not automatically be treated as a full-day Present.

Students should use this setting rather than hardcoding a single-punch behavior.

---

# 20. Grace Period

The organization has:

```text
Grace_Period
```

which should be considered when evaluating whether the employee has completed the expected shift duration.

Example:

```text
Shift duration = 9 hours
Grace Period   = 30 minutes
```

The grace period should be incorporated into the student's calculation of whether the employee qualifies for a full-day attendance.

The exact implementation should be clearly documented in the solution.

---

<del>

# 21. Half-Day Attendance

`HALF-DAY` is an attendance status and is different from `HALF DAY LEAVE`.

### HALF-DAY

Means the employee was expected to work but the calculated attendance satisfies only the half-day criteria.

### HALF DAY LEAVE

Means the employee has an approved half-day leave record.

Students must keep these two concepts separate.

</del>

---

# 22. Full-Day Leave

If the employee has an applicable:

```text
Full Day Leave
```

record for the date, the expected status is:

```text
FULL DAY LEAVE
```

The employee may have punch records even on a leave date. Students should not assume that the existence of punches automatically invalidates a leave record.

The final precedence between leave and punches should be implemented consistently and documented.

---

# 23. Half-Day Leave

If the employee has an applicable:

```text
Half Day Leave
```

record for the date, the expected status is:

```text
IF "HALF DAY LEAVE" + Effective_Attendance_Duration >= Half_Day_Duration:
       STATUS = "HALF DAY LEAVE + PRESENT" 
ELSE: 
       STATUS = "HALF DAY LEAVE + ABSENT" 
```

---

# 24. Absent

A working-day employee should generally be:

```text
ABSENT
```

when:

- the day is not a holiday,
- the day is not a week-off,
- the employee does not have applicable leave,
- the employee is not covered by a special attendance rule,
- and the employee does not satisfy the required attendance condition.

An employee with zero punches is therefore a key test case for ABSENT.

---

# 25. Week-Off

If the employee's applicable Shift record is:

```text
Week Off
```

the status should be:

```text
WEEK-OFF
```

This status is based on the assigned shift/calendar, not on the absence of punches.

---

# 26. Holiday

If the employee's organization has a Holiday_Calendar entry for the date, the date is a candidate for:

```text
HOLIDAY
```

Holiday is organization-specific.

Students should consider what happens if punch or leave records also exist on a holiday and document the chosen precedence.

---

# 27. Birthday

If all of the following are true:

```text
Attendance date = employee's birthday month/day
Is_Birthday_Enabled = True
```

the date is a candidate for:

```text
BIRTHDAY
```

The birthday rule is organization-specific.

Students should document how they handle a birthday that coincides with:

- Week-off
- Holiday
- Leave
- Special-executive status
- Normal working-day attendance

---

# 28. Anniversary

If all of the following are true:

```text
Attendance date = employee's anniversary month/day
Is_Anniversary_Enabled = True
```

the date is a candidate for:

```text
ANNIVERSARY
```

NULL anniversary values should not produce this status.

Students should document how they handle an anniversary that coincides with:

- Week-off
- Holiday
- Leave
- Special-executive status
- Normal working-day attendance

---

# 29. Status Priority

Attendance rules can overlap.

For example, the same date could potentially be:

```text
Birthday
+
Holiday
+
Leave
```

or:

```text
Special Executive
+
Birthday
```

Therefore, the Attendance engine needs a deterministic status-priority strategy.

### Initial recommendation

Use the following priority as a starting point for discussion:

```text
1. FULL DAY LEAVE
2. HALF DAY LEAVE + PRESENT
3. HALF DAY LEAVE + ABSENT
4. HOLIDAY
5. WEEK-OFF
6. BIRTHDAY
7. ANNIVERSARY
8. Special Executive -> PRESENT
9. Normal punch-based attendance:
       PRESENT
       HALF-DAY
       ABSENT
```

This is a **proposed initial priority**, not an immutable business rule.

Students should understand why precedence is required and document any alternative ordering they choose.

A particularly important business decision is whether Birthday/Anniversary should override Holiday/Week-Off or whether Holiday/Week-Off should take precedence.

---

# 30. Suggested Processing Model

Students are encouraged to think of the solution as a decision engine rather than a collection of independent IF statements.

Conceptually:

```text
Employee + Date
       |
       v
Find applicable Shift
       |
       +---- Week Off? -------- YES ---> WEEK-OFF
       |
       NO
       |
       v
Check Leave
       |
       +---- Full Day Leave ---> FULL DAY LEAVE
       |
       +---- Half Day Leave --> HALF DAY LEAVE
       |
       v
Check Holiday
       |
       +---- Holiday ---------> HOLIDAY
       |
       v
Check Birthday / Anniversary
       |
       v
Check Special Executive
       |
       v
Find relevant punches
       |
       +---- No punches ------> ABSENT
       |
       +---- One punch -------> Apply Single Punch Rule
       |
       v
Calculate attendance duration
       |
       +---- Meets criteria --> PRESENT
       |
       +---- Partial ---------> HALF-DAY
       |
       +---- Does not qualify -> ABSENT
```

The exact order should follow the documented status-priority decision.

---

# 31. Attendance Duration

For a normal working day, students should calculate the employee's effective attendance duration using the relevant punch-in and punch-out timestamps.

At minimum, the solution should correctly handle:

- Normal same-day shifts
- Overnight shifts
- Missing start punch
- Missing end punch
- Single punch
- Multiple punches
- Punches outside nominal shift boundaries but inside the organization's buffer

Students should clearly document how they calculate duration when a start or end punch is missing.

---

# 32. Do Not Assume Punch Count Equals Working Duration

The raw Punch table may contain many punches.

For example:

```text
08:55
09:10
12:15
13:05
17:55
18:10
```

These are raw events.

The Attendance engine should not simply calculate:

```text
last punch - first punch
```

without first determining which punches are relevant to the employee's assigned shift.

The employee's shift and organization-level buffers are essential context.

---

# 33. Important Edge Cases

The solution should be tested against at least the following scenarios:

| Scenario | Expected area to test |
|---|---|
| Normal full-day attendance | `PRESENT` |
| No punches on working day | `ABSENT` |
| One punch | Single-punch rule |
| Missing start punch | Partial attendance |
| Missing end punch | Partial attendance |
| Multiple punches | First/last relevant punch |
| Early punch | Buffer-In |
| Late punch after shift | Buffer-Out |
| Night shift crossing midnight | Overnight handling |
| Full-day leave | `FULL DAY LEAVE` |
| Half-day leave | `HALF DAY LEAVE` |
| Week-off | `WEEK-OFF` |
| Organization holiday | `HOLIDAY` |
| Enabled birthday | `BIRTHDAY` |
| Enabled anniversary | `ANNIVERSARY` |
| Special executive without punches | `PRESENT` |
| Special executive on leave | Leave precedence |
| Birthday on holiday | Status precedence |
| Anniversary on week-off | Status precedence |
| Holiday with punches | Status precedence |
| Leave with punches | Status precedence |

---

# 34. Expected Solution Characteristics

There is no requirement that every student implement the same code structure.

However, a good solution should:

- Correctly join data using organization and employee identity.
- Handle dates consistently.
- Handle overnight shifts correctly.
- Respect organization-level configuration.
- Distinguish raw punches from derived attendance.
- Handle missing punches.
- Handle zero and multiple punches.
- Apply leave and holiday rules.
- Handle birthdays and anniversaries.
- Handle special executives.
- Produce exactly one attendance result per employee/date.
- Produce one of the allowed Attendance statuses.
- Be deterministic when run against the same input.
- Clearly document status precedence and assumptions.

---

# 35. Deliverables

Each student should submit:

## 35.1 Attendance output

A CSV/table containing:

```text
ID
Org_ID
Employee_ID
Date
Shift_ID
Shift_Start_Date
Shift_End_Date
Punch_In_Time
Punch_Out_Time
Attendance_Status
```

## 35.2 Processing code

Code that reads the generated input datasets and produces the Attendance output.

## 35.3 Explanation

A short explanation covering:

1. How the applicable Shift is identified.
2. How relevant punches are identified.
3. How overnight shifts are handled.
4. How missing punches are handled.
5. How Single Punch is handled.
6. How Grace Period is applied.
7. How leave is handled.
8. How holidays are handled.
9. How birthdays and anniversaries are handled.
10. How special executives are handled.
11. What status precedence is used and why.

---

# 36. Evaluation Criteria

Students can be evaluated on:

| Area | What is being evaluated |
|---|---|
| Data understanding | Correct understanding of all input entities |
| Joins | Correct use of `(Org_ID, Employee_ID)` |
| Shift handling | Correct shift/date matching |
| Overnight shifts | Correct cross-midnight processing |
| Punch processing | Correct identification of relevant punches |
| Configuration | Correct use of organization-level settings |
| Leave | Correct full/half-day leave handling |
| Holidays | Correct organization-specific holiday handling |
| Special rules | Birthday, anniversary, executive handling |
| Edge cases | Missing/single/multiple punches |
| Status logic | Correct final status |
| Precedence | Clear and deterministic overlapping-rule handling |
| Code quality | Readability, modularity, maintainability |
| Output quality | Correct schema and one record per employee/date |

---

# 37. Scope Exclusions

The following are intentionally outside the scope of this assignment:

- Comp-off
- Manager approval workflows
- Employee-manager approval hierarchy
- Payroll calculations
- Overtime calculations
- Salary deductions
- Shift swapping workflows
- Leave approval workflows
- Manual attendance overrides
- Biometric-device integration
- Real-time attendance processing

The assignment focuses specifically on:

> **Deriving daily employee attendance status from the supplied master, configuration, shift, leave, holiday, rule, and raw punch data.**

---

# 38. Final Objective

Build an Attendance engine that can take imperfect, realistic employee data and answer the following reliably:

> **Given an organization, employee, and date, what is the employee's attendance status, and what evidence from the available data led to that status?**

The solution should be explainable, deterministic, and robust enough to handle normal attendance as well as realistic edge cases.
