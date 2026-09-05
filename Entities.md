# Entities and Relationships

### Organization

| Column | Description |
|---|---|
| `Org_ID` | Organization identifier |
| `Org_Name` | Organization name |
| `Head_Office_Address` | Dummy head-office address |
| `Country` | Organization's country |


### Employee

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


### Organization_Level_Settings

| Column | Description |
|---|---|
| `Org_ID` | Organization |
| `Buffer_In_Time` | Allowed early-arrival buffer - How early an employee is allowed in a shift?|
| `Buffer_Out_Time` | Allowed late-departure buffer - How late an employee can stay in a shift?|
| `Grace_Period` | Attendance grace period - Relaxation for full day attendance |
| `Is_Single_Punch_Enabled` | Whether one punch can qualify for attendance |
| `Is_Birthday_Enabled` | Whether birthday attendance rule is enabled |
| `Is_Anniversary_Enabled` | Whether anniversary attendance rule is enabled |


### Shift

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


### Holiday_Calendar

| Column | Description |
|---|---|
| `ID` | Holiday record identifier |
| `Org_ID` | Organization |
| `Holiday_Date` | Holiday date |
| `Holiday_Type` | Holiday classification |



### Default_Rules

| Column | Description |
|---|---|
| `Rule_ID` | Rule identifier |
| `Org_ID` | Organization |
| `Special_Executive_ID` | `Employee_ID` of special executive |


### Leave

| Column | Description |
|---|---|
| `ID` | Leave identifier |
| `Org_ID` | Organization |
| `Employee_ID` | Employee |
| `Leave_Start_Date` | Leave start |
| `Leave_End_Date` | Leave end |
| `Leave_Type` | Leave classification |


### Employee_Punch

| Column | Description |
|---|---|
| `ID` | Punch identifier |
| `Org_ID` | Organization |
| `Employee_ID` | Employee |
| `Punch_Date` | Date of punch |
| `Punch_Time` | Time of punch |
| `Medium` | Punch medium |


   


## Entity Relationships

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