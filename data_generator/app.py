import os
import random
import string
import pandas as pd
import holidays
from datetime import datetime, timedelta
from pandas import DataFrame

# Prepare the output location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# For reproducibility
SEED = 42

#  -------------------- Helper functions --------------------
# File writer utility
def file_writer(*, label: str, df: DataFrame, file_name: str) -> None:
    output_file = os.path.join(OUTPUT_DIR, file_name)
    df.to_csv(output_file, index=False)
    print(f"Written {label} file at : [{output_file}]")


# Random date generator between date range 
def random_date(start_date, end_date):
    """
    Generate random date between start_date and end_date.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta_days = (end - start).days
    random_days = random.randint(0, delta_days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")


# Creates list of work-weeks and week_off_weeks
def generate_shift_weeks(start_date: str, end_date: str):
    # Note: Start date must be a Monday
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start

    work_weeks = []
    week_off_weeks = []

    while current <= end:
        # Monday-Friday
        work_start = current
        work_end = current + timedelta(days=4)
        # Saturday-Sunday
        off_start = current + timedelta(days=5)
        off_end = current + timedelta(days=6)

        work_weeks.append((
            work_start.strftime("%Y-%m-%d"),
            work_end.strftime("%Y-%m-%d")
        ))
        week_off_weeks.append((
            off_start.strftime("%Y-%m-%d"),
            off_end.strftime("%Y-%m-%d")
        ))

        current += timedelta(days=7)
    return work_weeks, week_off_weeks


#  -------------------- Business logic functions --------------------

# Generates dummy organizations
def generate_organizations():
    """
    Generate dummy organization data and write it to CSV.
    """

    # Reproducible random data
    random.seed(SEED)

    countries = [
        "India",
        "United States",
        "Germany",
        "Thailand",
        "Singapore",
        "Australia",
        "Canada",
        "Japan",
        "Netherlands",
        "United Kingdom"
    ]

    organizations = []
    for idx, company_suffix in enumerate(string.ascii_uppercase[:10], start=1):
        org_name = f"Company {company_suffix}"
        pin_code = random.randint(100000, 999999)
        address = f"Address for Head Office, {org_name}, Pin/Zip Code: {pin_code}"
        country = random.choice(countries)
        organizations.append({
            "Org_ID": idx,
            "Org_Name": org_name,
            "Head_Office_Address": address,
            "Country": country
        })

    # Create dataframe
    df = pd.DataFrame(organizations)

    file_writer(label="organization", df=df, file_name="organization.csv")
    print(df.head(5))
    return df


# Generate employees for the organization
def generate_employees(*, org_df: DataFrame):
    """
    Generate dummy employee data.
    """
    random.seed(SEED)

    first_names = [
        "Alex", "Jordan", "Taylor", "Morgan", "Casey",
        "Avery", "Riley", "Parker", "Jamie", "Skyler",
        "Cameron", "Quinn", "Reese", "Dakota", "Emerson"
    ]
    last_names = [
        "Smith", "Johnson", "Brown", "Williams", "Jones",
        "Garcia", "Miller", "Davis", "Wilson", "Moore",
        "Taylor", "Anderson", "Thomas", "Jackson", "White"
    ]

    employees = []
    employee_pk = 1

    for _, org in org_df.iterrows():
        org_id = org["Org_ID"]

        # Random employee count between 15 and 500
        employee_count = random.randint(15, 500)
        employee_id = 1

        # for emp_num in range(1, employee_count + 1):
        while employee_id <= employee_count:
            employee_name = (
                f"{random.choice(first_names)} "
                f"{random.choice(last_names)}"
            )
            gender = random.choice(["Male", "Female"])
            doj = random_date("2020-01-01", "2025-12-31")
            dob = random_date("1980-01-01", "2005-12-31")

            # 60% null anniversary
            if random.random() < 0.60:
                anniversary = None
            else:
                anniversary = random_date("2010-01-01", "2025-12-31")

            employees.append({
                "ID": employee_pk,
                "Employee_ID": employee_id,
                "Org_ID": org_id,
                "Employee_Name": employee_name,
                "Gender": gender,
                "Date_Of_Joining": doj,
                "Date_of_Birth": dob,
                "Date_Of_Anniversary": anniversary
            })
            # Increment the counters
            employee_pk += 1
            employee_id += 1 

    df = pd.DataFrame(employees)
    file_writer(label="Employee", df=df, file_name="employee.csv")
    print(df.head(5))
    return df


# Generate organization level settings
def generate_organization_level_settings(*, org_df: DataFrame):
    """
    Generate organization scoped attendance settings.
    """

    random.seed(SEED)
    settings = []
    org_ids = org_df["Org_ID"].tolist()

    # 30% companies with single punch enabled
    single_punch_enabled_orgs = set(
        random.sample(org_ids, max(1, int(len(org_ids) * 0.30)))
    )

    # 70% companies with birthday leaves enabled
    birthday_enabled_orgs = set(
        random.sample(org_ids, max(1, int(len(org_ids) * 0.70)))
    )

    # 50% companies with anniversary leaves enabled
    anniversary_enabled_orgs = set(
        random.sample(org_ids, max(1, int(len(org_ids) * 0.50)))
    )

    for _, org in org_df.iterrows():
        org_id = org["Org_ID"]
        buffer_in_minutes = random.randint(15, 90)
        buffer_out_minutes = random.randint(15, 90)
        grace_minutes = random.randint(0, 30)
        settings.append({
            "Org_ID": org_id,
            "Buffer_In_Time": f"{buffer_in_minutes // 60:02d}:{buffer_in_minutes % 60:02d}",
            "Buffer_Out_Time": f"{buffer_out_minutes // 60:02d}:{buffer_out_minutes % 60:02d}",
            "Grace_Period": f"{grace_minutes // 60:02d}:{grace_minutes % 60:02d}",
            "Is_Single_Punch_Enabled": org_id in single_punch_enabled_orgs,
            "Is_Birthday_Enabled": org_id in birthday_enabled_orgs,
            "Is_Anniversary_Enabled": org_id in anniversary_enabled_orgs
        })

    df = pd.DataFrame(settings)
    file_writer(
        label="Organization Level Settings",
        df=df,
        file_name="organization_level_settings.csv"
    )

    print(df.head(5))
    return df


# Generate employee shifts
def generate_shifts(
    *,
    org_df: DataFrame,
    emp_df: DataFrame,
    start_date: str,
    end_date: str,
):
    """
    Generate employee shift mappings.
    """
    random.seed(SEED)
    shifts = []
    shift_id = 1

    # Select 3 orgs with only regular shifts
    regular_shift_orgs = set(
        random.sample(
            org_df["Org_ID"].tolist(),
            3
        )
    )

    shift_timings = {
        "Regular Shift": ("09:00", "18:00"),
        "Morning Shift": ("06:30", "15:30"),
        "Afternoon Shift": ("14:30", "23:30"),
        "Night Shift": ("22:30", "07:30"),
        "Week Off": (None, None)
    }

    # Get work week and week-off week
    work_weeks, week_off_weeks = generate_shift_weeks(start_date=start_date, end_date=end_date)

    allowed_shift_types = [
        "Morning Shift",
        "Afternoon Shift",
        "Night Shift"
    ]

    invalid_transitions = {
        "Morning Shift": ["Afternoon Shift"],
        "Afternoon Shift": ["Night Shift"],
        "Night Shift": ["Morning Shift"]
    }

    allowed_transitions = {
        "Morning Shift": ["Morning Shift", "Night Shift"],
        "Afternoon Shift": ["Morning Shift", "Afternoon Shift"],
        "Night Shift": ["Afternoon Shift", "Night Shift"]
    }

    for _, employee in emp_df.iterrows():
        org_id = employee["Org_ID"]
        employee_id = employee["Employee_ID"] 
        previous_shift = None

        for week_index in range(len(work_weeks)):
            # Working Shift Entry
            if org_id in regular_shift_orgs:
                shift_type = "Regular Shift"
            else:
                # First shift completely random
                if previous_shift is None:
                    shift_type = random.choice(allowed_shift_types)
                else:
                    shift_type = random.choice(allowed_transitions[previous_shift])

            shift_start_time, shift_end_time = shift_timings[shift_type]

            shifts.append({
                "Shift_ID": shift_id,
                "Org_ID": org_id,
                "Employee_ID": employee_id,
                "Shift_Type": shift_type,
                "Shift_Start_Date": work_weeks[week_index][0],
                "Shift_End_Date": work_weeks[week_index][1],
                "Shift_Start_Time": shift_start_time,
                "Shift_End_Time": shift_end_time
            })
            shift_id += 1
            previous_shift = shift_type

            # Week Off Entry
            shifts.append({
                "Shift_ID": shift_id,
                "Org_ID": org_id,
                "Employee_ID": employee_id,
                "Shift_Type": "Week Off",
                "Shift_Start_Date": week_off_weeks[week_index][0],
                "Shift_End_Date": week_off_weeks[week_index][1],
                "Shift_Start_Time": None,
                "Shift_End_Time": None
            })
            shift_id += 1

    df = pd.DataFrame(shifts)

    file_writer(
        label="Shift",
        df=df,
        file_name="shift.csv"
    )

    print(df.head(10))
    return df


# Generate holiday calendar
def generate_holiday_calendar(
    *,
    org_df: DataFrame,
    year: int,
):
    """
    Generate organization holiday calendar.
    """

    random.seed(SEED)
    holiday_rows = []
    holiday_id = 1

    # Country mapping for holidays package
    country_mapping = {
        "India": "IN",
        "United States": "US",
        "Germany": "DE",
        "Thailand": "TH",
        "Singapore": "SG",
        "Australia": "AU",
        "Canada": "CA",
        "Japan": "JP",
        "Netherlands": "NL",
        "United Kingdom": "UK"
    }

    for _, org in org_df.iterrows():
        org_id = org["Org_ID"]
        country = org["Country"]
        country_code = country_mapping.get(country)

        if not country_code:
            continue

        # National Holidays
        country_holidays = holidays.country_holidays(
            country_code,
            years=year
        )

        national_holiday_dates = sorted(
            [ holiday_date.strftime("%Y-%m-%d") for holiday_date in country_holidays.keys() ]
        )

        for holiday_date in national_holiday_dates:
            holiday_rows.append({
                "ID": holiday_id,
                "Org_ID": org_id,
                "Holiday_Date": holiday_date,
                "Holiday_Type": "National Holiday"
            })

            holiday_id += 1

        # Restricted Holidays
        restricted_holiday_count = random.randint(3, 8)
        restricted_holidays = random.sample(
            national_holiday_dates,
            min(restricted_holiday_count, len(national_holiday_dates))
        )

        for holiday_date in restricted_holidays:
            holiday_rows.append({
                "ID": holiday_id,
                "Org_ID": org_id,
                "Holiday_Date": holiday_date,
                "Holiday_Type": "Restricted Holiday"
            })
            holiday_id += 1

    df = pd.DataFrame(holiday_rows)
    df = df.sort_values(
        by=["Org_ID", "Holiday_Date", "Holiday_Type"]
    ).reset_index(drop=True)

    file_writer(
        label="Holiday Calendar",
        df=df,
        file_name="holiday_calendar.csv"
    )

    print(df.head(10))
    return df


# Generate default attendance rules
def generate_default_rules(*, emp_df: DataFrame):
    """
    Generate organization level default rules.
    Marks 1-3% employees from each organization as special executives.
    """

    random.seed(SEED)
    rules = []
    rule_id = 1

    # Group employees by organization
    grouped_employees = emp_df.groupby("Org_ID")
    for org_id, org_employee_df in grouped_employees:
        employee_ids = org_employee_df["Employee_ID"].tolist()
        employee_count = len(employee_ids)

        # Choose 1-3% employees
        percentage = random.uniform(0.01, 0.03)
        special_executive_count = max(
            1,
            int(employee_count * percentage)
        )

        special_executive_ids = random.sample(
            employee_ids,
            min(special_executive_count, employee_count)
        )

        for employee_id in special_executive_ids:
            rules.append({
                "Rule_ID": rule_id,
                "Org_ID": org_id,
                "Special_Executive_ID": employee_id
            })
            rule_id += 1

    df = pd.DataFrame(rules)

    df = df.sort_values(
        by=["Org_ID", "Special_Executive_ID"]
    ).reset_index(drop=True)

    file_writer(
        label="Default Rules",
        df=df,
        file_name="default_rules.csv"
    )

    print(df.head(10))
    return df


# Generate employee leaves
def generate_leaves(
    *,
    emp_df: DataFrame,
    shift_df: DataFrame,
):
    """
    Generate employee leave data.
    """

    random.seed(SEED)
    leaves = []
    leave_id = 1

    # Build working-day lookup
    working_days_lookup = {}
    working_shift_df = shift_df[
        shift_df["Shift_Type"] != "Week Off"
    ]

    for _, row in working_shift_df.iterrows():
        employee_id = row["Employee_ID"]
        start = datetime.strptime(
            row["Shift_Start_Date"],
            "%Y-%m-%d"
        )
        end = datetime.strptime(
            row["Shift_End_Date"],
            "%Y-%m-%d"
        )

        current = start
        while current <= end:
            working_days_lookup.setdefault(
                employee_id,
                []
            ).append(
                current.strftime("%Y-%m-%d")
            )
            current += timedelta(days=1)

    # Iterate employee-wise
    for _, employee in emp_df.iterrows():
        org_id = employee["Org_ID"]
        employee_id = employee["Employee_ID"]
        working_days = sorted(
            working_days_lookup.get(
                employee_id,
                []
            )
        )
        if not working_days:
            continue

        # Daily leave probability evaluation
        day_index = 0
        while day_index < len(working_days):
            current_day = working_days[day_index]

            # 0.5% probability
            leave_probability = random.random()
            if leave_probability <= 0.005:
                leave_type = random.choices(
                    ["Full Day Leave", "Half Day Leave"],
                    weights=[80, 20],
                    k=1
                )[0]

                # HALF DAY LEAVE
                if leave_type == "Half Day Leave":
                    leaves.append({
                        "ID": leave_id,
                        "Org_ID": org_id,
                        "Employee_ID": employee_id,
                        "Leave_Start_Date": current_day,
                        "Leave_End_Date": current_day,
                        "Leave_Type": "Half Day Leave"
                    })
                    leave_id += 1
                    day_index += 1

                # FULL DAY LEAVE
                else:
                    leave_duration = random.randint(1, 3)
                    leave_start = current_day
                    leave_end = current_day
                    temp_index = day_index
                    assigned_days = []
                    while (
                        temp_index < len(working_days)
                        and len(assigned_days) < leave_duration
                    ):
                        assigned_days.append(
                            working_days[temp_index]
                        )
                        leave_end = working_days[temp_index]
                        temp_index += 1

                    leaves.append({
                        "ID": leave_id,
                        "Org_ID": org_id,
                        "Employee_ID": employee_id,
                        "Leave_Start_Date": leave_start,
                        "Leave_End_Date": leave_end,
                        "Leave_Type": "Full Day Leave"
                    })

                    leave_id += 1
                    day_index = temp_index
            else:
                day_index += 1

    df = pd.DataFrame(leaves)
    if not df.empty:
        df = df.sort_values(
            by=[
                "Org_ID",
                "Employee_ID",
                "Leave_Start_Date"
            ]
        ).reset_index(drop=True)

    file_writer(
        label="Leave",
        df=df,
        file_name="leave.csv"
    )

    print(df.head(10))
    return df


# Generate employee punches
# def generate_employee_punches(
#     *,
#     emp_df: DataFrame,
#     shift_df: DataFrame,
#     start_date: str,
#     end_date: str
# ):
#     """
#     Generate employee punch/swipe data.
#     """

#     random.seed(SEED)
#     punches = []
#     punch_id = 1
#     punch_mediums = [
#         "WebApp",
#         "MobileApp",
#         "POS"
#     ]

#     # Shift timing lookup
#     shift_lookup = {}
#     for _, shift in shift_df.iterrows():
#         if shift["Shift_Type"] == "Week Off":
#             continue
#         employee_id = shift["Employee_ID"]
#         shift_start_date = datetime.strptime(
#             shift["Shift_Start_Date"],
#             "%Y-%m-%d"
#         )
#         shift_end_date = datetime.strptime(
#             shift["Shift_End_Date"],
#             "%Y-%m-%d"
#         )

#         current_date = shift_start_date
#         while current_date <= shift_end_date:
#             current_date_str = current_date.strftime("%Y-%m-%d")
#             shift_lookup[
#                 (employee_id, current_date_str)
#             ] = {
#                 "Org_ID": shift["Org_ID"],
#                 "Shift_Type": shift["Shift_Type"],
#                 "Shift_Start_Time": shift["Shift_Start_Time"],
#                 "Shift_End_Time": shift["Shift_End_Time"]
#             }
#             current_date += timedelta(days=1)

#     # Iterate employee/day
#     start = datetime.strptime(
#         start_date,
#         "%Y-%m-%d"
#     )
#     end = datetime.strptime(
#         end_date,
#         "%Y-%m-%d"
#     )

#     for _, employee in emp_df.iterrows():
#         employee_id = employee["Employee_ID"]
#         current_date = start
#         while current_date <= end:
#             current_date_str = current_date.strftime(
#                 "%Y-%m-%d"
#             )
#             shift_info = shift_lookup.get(
#                 (employee_id, current_date_str)
#             )

#             # Skip week-offs / no shift days
#             if not shift_info:
#                 current_date += timedelta(days=1)
#                 continue

#             shift_start_time = shift_info[
#                 "Shift_Start_Time"
#             ]
#             shift_end_time = shift_info[
#                 "Shift_End_Time"
#             ]

#             org_id = shift_info["Org_ID"]

#             # Generate random number of punches
#             punch_count = random.randint(0, 20)

#             # No punches
#             if punch_count == 0:
#                 current_date += timedelta(days=1)
#                 continue

#             # Build allowed punch window
#             shift_start_datetime = datetime.strptime(
#                 f"{current_date_str} {shift_start_time}",
#                 "%Y-%m-%d %H:%M"
#             )

#             # Handle overnight shifts
#             shift_end_datetime = datetime.strptime(
#                 f"{current_date_str} {shift_end_time}",
#                 "%Y-%m-%d %H:%M"
#             )

#             if shift_end_datetime <= shift_start_datetime:
#                 shift_end_datetime += timedelta(days=1)

#             # Allow punches:
#             # 4 hours before shift start
#             # 4 hours after shift end
#             punch_window_start = (
#                 shift_start_datetime
#                 - timedelta(hours=4)
#             )
#             punch_window_end = (
#                 shift_end_datetime
#                 + timedelta(hours=4)
#             )

#             total_seconds = int(
#                 (
#                     punch_window_end
#                     - punch_window_start
#                 ).total_seconds()
#             )

#             punch_timestamps = []
#             for _ in range(punch_count):
#                 random_seconds = random.randint(
#                     0,
#                     total_seconds
#                 )
#                 punch_datetime = (
#                     punch_window_start
#                     + timedelta(seconds=random_seconds)
#                 )
#                 punch_timestamps.append(
#                     punch_datetime
#                 )

#             # Sort punches chronologically
#             punch_timestamps.sort()

#             # Save punches
#             for punch_datetime in punch_timestamps:
#                 punches.append({
#                     "ID": punch_id,
#                     "Org_ID": org_id,
#                     "Employee_ID": employee_id,
#                     "Punch_Date": punch_datetime.strftime("%Y-%m-%d"),
#                     "Punch_Time": punch_datetime.strftime("%H:%M"),
#                     "Medium": random.choice(punch_mediums)
#                 })
#                 punch_id += 1
#             current_date += timedelta(days=1)

#     df = pd.DataFrame(punches)
#     if not df.empty:
#         df = df.sort_values(
#             by=[
#                 "Org_ID",
#                 "Employee_ID",
#                 "Punch_Date",
#                 "Punch_Time"
#             ]
#         ).reset_index(drop=True)

#     file_writer(
#         label="Employee Punch",
#         df=df,
#         file_name="employee_punch.csv"
#     )

#     print(df.head(10))
#     return df

# Generate employee punches
def generate_employee_punches(
    *,
    emp_df: DataFrame,
    shift_df: DataFrame,
    start_date: str,
    end_date: str
):
    """
    Generate employee punch/swipe data with organic punch distribution.
    Punches are distributed across three behavioral segments:
        1. Start of shift
        2. Middle of shift
        3. End of shift

    A small percentage of employees in each organization are designated
    as being more likely to miss either their start or end swipe.
    Normal employees can also occasionally miss start/end swipes.
    """

    random.seed(SEED)

    punches = []
    punch_id = 1

    punch_mediums = [
        "WebApp",
        "MobileApp",
        "POS"
    ]

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    # Percentage of employees in each organization who are
    # more likely to miss a start/end punch.
    MISS_PRONE_EMPLOYEE_MIN_PCT = 0.01
    MISS_PRONE_EMPLOYEE_MAX_PCT = 0.05

    # Normal employees occasionally miss a start/end swipe.
    NORMAL_START_MISS_PROBABILITY = 0.03
    NORMAL_END_MISS_PROBABILITY = 0.03

    # Miss-prone employees have a much higher probability.
    MISS_PRONE_START_PROBABILITY = 0.65
    MISS_PRONE_END_PROBABILITY = 0.65

    # Distribution of punches across the three segments.
    #
    # Start and end get slightly more weight because those are
    # where meaningful attendance swipes normally happen.
    SEGMENT_WEIGHTS = {
        "start": 0.30,
        "middle": 0.40,
        "end": 0.30
    }

    # ------------------------------------------------------------------
    # Identify miss-prone employees
    # ------------------------------------------------------------------

    # Key:
    #   (Org_ID, Employee_ID)
    #
    # Employee_ID is only unique within an organization.
    miss_prone_employees = {}

    for org_id in emp_df["Org_ID"].unique():
        org_employees = emp_df[
            emp_df["Org_ID"] == org_id
        ]

        employee_keys = [
            (
                row["Org_ID"],
                row["Employee_ID"]
            )
            for _, row in org_employees.iterrows()
        ]

        employee_count = len(employee_keys)

        miss_prone_pct = random.uniform(
            MISS_PRONE_EMPLOYEE_MIN_PCT,
            MISS_PRONE_EMPLOYEE_MAX_PCT
        )

        miss_prone_count = max(
            1,
            round(employee_count * miss_prone_pct)
        )

        miss_prone_count = min(
            miss_prone_count,
            employee_count
        )

        selected_employees = random.sample(
            employee_keys,
            miss_prone_count
        )

        for employee_key in selected_employees:

            # Randomly decide whether the employee is more likely
            # to miss their start or end swipe.
            miss_type = random.choice([
                "START_MISS_PRONE",
                "END_MISS_PRONE"
            ])

            miss_prone_employees[
                employee_key
            ] = miss_type

    # ------------------------------------------------------------------
    # Shift timing lookup
    # ------------------------------------------------------------------

    shift_lookup = {}

    for _, shift in shift_df.iterrows():

        if shift["Shift_Type"] == "Week Off":
            continue

        org_id = shift["Org_ID"]
        employee_id = shift["Employee_ID"]

        shift_start_date = datetime.strptime(
            shift["Shift_Start_Date"],
            "%Y-%m-%d"
        )

        shift_end_date = datetime.strptime(
            shift["Shift_End_Date"],
            "%Y-%m-%d"
        )

        current_date = shift_start_date

        while current_date <= shift_end_date:

            current_date_str = current_date.strftime(
                "%Y-%m-%d"
            )

            shift_lookup[
                (
                    org_id,
                    employee_id,
                    current_date_str
                )
            ] = {
                "Shift_Type": shift["Shift_Type"],
                "Shift_Start_Time": shift["Shift_Start_Time"],
                "Shift_End_Time": shift["Shift_End_Time"]
            }

            current_date += timedelta(days=1)

    # ------------------------------------------------------------------
    # Iterate employee/day
    # ------------------------------------------------------------------

    start = datetime.strptime(
        start_date,
        "%Y-%m-%d"
    )

    end = datetime.strptime(
        end_date,
        "%Y-%m-%d"
    )

    for _, employee in emp_df.iterrows():

        org_id = employee["Org_ID"]
        employee_id = employee["Employee_ID"]

        employee_key = (
            org_id,
            employee_id
        )

        miss_type = miss_prone_employees.get(
            employee_key
        )

        current_date = start

        while current_date <= end:

            current_date_str = current_date.strftime(
                "%Y-%m-%d"
            )

            shift_info = shift_lookup.get(
                (
                    org_id,
                    employee_id,
                    current_date_str
                )
            )

            # Skip week-offs / days without a shift.
            if not shift_info:
                current_date += timedelta(days=1)
                continue

            shift_start_time = shift_info[
                "Shift_Start_Time"
            ]

            shift_end_time = shift_info[
                "Shift_End_Time"
            ]

            # ----------------------------------------------------------
            # Determine whether start/end swipe should be missing
            # ----------------------------------------------------------

            if miss_type == "START_MISS_PRONE":
                miss_start = (
                    random.random()
                    < MISS_PRONE_START_PROBABILITY
                )

                miss_end = (
                    random.random()
                    < NORMAL_END_MISS_PROBABILITY
                )

            elif miss_type == "END_MISS_PRONE":
                miss_start = (
                    random.random()
                    < NORMAL_START_MISS_PROBABILITY
                )

                miss_end = (
                    random.random()
                    < MISS_PRONE_END_PROBABILITY
                )

            else:
                miss_start = (
                    random.random()
                    < NORMAL_START_MISS_PROBABILITY
                )

                miss_end = (
                    random.random()
                    < NORMAL_END_MISS_PROBABILITY
                )

            # ----------------------------------------------------------
            # Generate total number of punches
            # ----------------------------------------------------------

            punch_count = random.randint(0, 20)

            if punch_count == 0:
                current_date += timedelta(days=1)
                continue

            # ----------------------------------------------------------
            # Build shift datetimes
            # ----------------------------------------------------------

            shift_start_datetime = datetime.strptime(
                f"{current_date_str} {shift_start_time}",
                "%Y-%m-%d %H:%M"
            )

            shift_end_datetime = datetime.strptime(
                f"{current_date_str} {shift_end_time}",
                "%Y-%m-%d %H:%M"
            )

            # Handle overnight shifts.
            if shift_end_datetime <= shift_start_datetime:
                shift_end_datetime += timedelta(days=1)

            # ----------------------------------------------------------
            # Define punch window
            # ----------------------------------------------------------

            punch_window_start = (
                shift_start_datetime
                - timedelta(hours=4)
            )

            punch_window_end = (
                shift_end_datetime
                + timedelta(hours=4)
            )

            # ----------------------------------------------------------
            # Define three behavioral segments
            # ----------------------------------------------------------

            shift_duration = (
                shift_end_datetime
                - shift_start_datetime
            )

            # Start segment:
            # 4 hours before shift → shift start
            start_segment_start = (
                shift_start_datetime
                - timedelta(hours=4)
            )

            start_segment_end = shift_start_datetime

            # Middle segment:
            # shift start → shift end
            middle_segment_start = shift_start_datetime
            middle_segment_end = shift_end_datetime

            # End segment:
            # shift end → 4 hours after shift
            end_segment_start = shift_end_datetime
            end_segment_end = (
                shift_end_datetime
                + timedelta(hours=4)
            )

            segments = {
                "start": (
                    start_segment_start,
                    start_segment_end
                ),
                "middle": (
                    middle_segment_start,
                    middle_segment_end
                ),
                "end": (
                    end_segment_start,
                    end_segment_end
                )
            }

            # ----------------------------------------------------------
            # Allocate punch count across segments
            # ----------------------------------------------------------

            segment_counts = {
                "start": 0,
                "middle": 0,
                "end": 0
            }

            for _ in range(punch_count):

                segment = random.choices(
                    population=[
                        "start",
                        "middle",
                        "end"
                    ],
                    weights=[
                        SEGMENT_WEIGHTS["start"],
                        SEGMENT_WEIGHTS["middle"],
                        SEGMENT_WEIGHTS["end"]
                    ],
                    k=1
                )[0]

                segment_counts[segment] += 1

            # ----------------------------------------------------------
            # Remove start/end punches when employee misses swipe
            # ----------------------------------------------------------

            if miss_start:
                segment_counts["start"] = 0

            if miss_end:
                segment_counts["end"] = 0

            # ----------------------------------------------------------
            # Generate timestamps within each segment
            # ----------------------------------------------------------

            punch_timestamps = []

            for segment_name, count in segment_counts.items():

                if count == 0:
                    continue

                segment_start, segment_end = segments[
                    segment_name
                ]

                total_seconds = int(
                    (
                        segment_end
                        - segment_start
                    ).total_seconds()
                )

                for _ in range(count):

                    random_seconds = random.randint(
                        0,
                        total_seconds
                    )

                    punch_datetime = (
                        segment_start
                        + timedelta(
                            seconds=random_seconds
                        )
                    )

                    punch_timestamps.append(
                        punch_datetime
                    )

            # ----------------------------------------------------------
            # Sort punches chronologically
            # ----------------------------------------------------------

            punch_timestamps.sort()

            # ----------------------------------------------------------
            # Save punches
            # ----------------------------------------------------------

            for punch_datetime in punch_timestamps:

                punches.append({
                    "ID": punch_id,
                    "Org_ID": org_id,
                    "Employee_ID": employee_id,
                    "Punch_Date": punch_datetime.strftime(
                        "%Y-%m-%d"
                    ),
                    "Punch_Time": punch_datetime.strftime(
                        "%H:%M"
                    ),
                    "Medium": random.choice(
                        punch_mediums
                    )
                })

                punch_id += 1

            current_date += timedelta(days=1)

    # ------------------------------------------------------------------
    # Create DataFrame
    # ------------------------------------------------------------------

    df = pd.DataFrame(punches)

    if not df.empty:

        df = df.sort_values(
            by=[
                "Org_ID",
                "Employee_ID",
                "Punch_Date",
                "Punch_Time"
            ]
        ).reset_index(drop=True)

        # Re-sequence IDs after sorting.
        df["ID"] = range(
            1,
            len(df) + 1
        )

    file_writer(
        label="Employee Punch",
        df=df,
        file_name="employee_punch.csv"
    )

    print(df.head(10))

    return df

if __name__ == "__main__":
    # Known limitation: start_date must be Monday 
    start_date = "2026-03-01"   # in yyyy-MM-dd format
    end_date   = "2026-04-04"   # in yyyy-MM-dd format

    org_df = generate_organizations()
    emp_df = generate_employees(org_df=org_df)
    org_settings_df = generate_organization_level_settings(org_df=org_df)
    shift_df = generate_shifts(org_df=org_df, emp_df=emp_df, start_date=start_date, end_date=end_date)
    holidat_df = generate_holiday_calendar(org_df=org_df, year=int(start_date[0:4]))
    default_rules_df = generate_default_rules(emp_df=emp_df)
    leaves_df = generate_leaves(emp_df=emp_df, shift_df=shift_df)
    employee_punch_df = generate_employee_punches(emp_df=emp_df, shift_df=shift_df, start_date=start_date, end_date=end_date)
