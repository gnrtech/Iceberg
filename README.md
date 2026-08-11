# Kiro AI Prompt — Mainframe Non-Mod vs RDS Mod Job Comparison and Validation

I have already extracted two sets of AutoSys job data:

* **Mainframe Non-Mod** jobs
* **RDS Mod/Migrated** jobs

Both datasets have already been extracted into CSV files and a **Full Outer Join** has already been performed.

Now I need to build a **Python/Pandas validation process** on the resulting full-joined CSV.

The purpose is to compare the Mainframe Non-Mod jobs against the RDS Mod jobs and identify whether the migrated jobs have the **same jobs, dependencies, conditions, machine information, scripts, boxes, and execution order**, while allowing known migration-specific naming differences.

---

# 1. INPUT

The input is an already-created **Full Outer Join CSV**.

The CSV contains columns from both sides.

For example, it may contain columns like:

```text
left_box_name
left_job_name
left_machine_name
left_job_condition
left_script_path
left_order
...

right_box_name
right_job_name
right_machine_name
right_job_condition
right_script_path
right_order
...
```

The actual column names may be slightly different.

### Important

Before implementing the validation logic:

1. Read the actual CSV.
2. Inspect the column names.
3. Identify the Mainframe/Non-Mod columns.
4. Identify the RDS/Mod columns.
5. Do not assume that the sample column names above are exactly the actual names.

Make the implementation configurable so column mappings can easily be changed.

---

# 2. VERY IMPORTANT — PRESERVE THE INPUT DATA

The final output must contain:

```text
ALL ORIGINAL INPUT COLUMNS
+
NEW VALIDATION COLUMNS
```

Do NOT remove any existing input columns.

Do NOT rename existing input columns.

Do NOT modify existing input values.

Do NOT create a simplified output containing only validation columns.

If the input has 100 columns, the final output should contain those same 100 columns plus the newly generated validation columns.

For example:

```text
Input:

left_box
left_job
left_machine
left_condition
left_script
right_box
right_job
right_machine
right_condition
right_script
...

Output:

left_box
left_job
left_machine
left_condition
left_script
right_box
right_job
right_machine
right_condition
right_script
...

validation_status
validation_reason
machine_validation
job_validation
job_condition_validation
script_path_validation
dependency_validation
box_validation
order_validation
```

---

# 3. PRESERVE ROW COUNT

The validation process must operate on the already-created full-joined dataset.

Do not perform another join that changes the row count.

If the input contains:

```text
50,000 rows
```

the final output should contain:

```text
50,000 rows
```

unless there is a clearly documented duplicate-handling requirement.

Each input row should produce exactly one validation result row.

---

# 4. MAIN OBJECTIVE

For every joined row, compare the corresponding Mainframe Non-Mod and RDS Mod values.

If everything that should match is equivalent:

```text
validation_status = Matched
```

If any validation fails:

```text
validation_status = Not Matched
```

The `validation_reason` must explain **exactly what is different**.

Do not use a generic reason such as:

```text
Mismatch
```

Instead use something like:

```text
machine_name mismatch: left='server1', right='server2'
```

or:

```text
job_condition mismatch: left='1', right='0'
```

or:

```text
script_path mismatch: left='/root/dev/test1/abc.sh', right='/root/dev1/test1/abc.sh'
```

---

# 5. JOB EXISTENCE VALIDATION

Because the input is a Full Outer Join, jobs may exist on only one side.

## Case 1 — Job exists only on Mainframe

Example:

```text
left_job_name  = EMP_CMD
right_job_name = null
```

Result:

```text
validation_status = Not Matched
job_validation = Not Matched
validation_reason = Job exists only on Mainframe/Non-Mod side
```

## Case 2 — Job exists only on RDS

Example:

```text
left_job_name  = null
right_job_name = EMP_MOD_CMP
```

Result:

```text
validation_status = Not Matched
job_validation = Not Matched
validation_reason = Job exists only on RDS/Mod side
```

Use clear validation categories such as:

```text
missing_in_mod
extra_in_mod
```

---

# 6. JOB NAME VALIDATION

There is a known migration naming difference.

For example:

Mainframe:

```text
EMP_CMD
```

RDS:

```text
EMP_MOD_CMP
```

The RDS side may have additional `_MOD`, `_CMP`, or other known migration-specific suffixes.

The validation must support configurable job-name normalization/mapping.

Do NOT automatically mark a job as mismatched merely because of an expected migration naming convention.

For example:

```text
EMP_CMD
EMP_MOD_CMP
```

may represent the same migrated job.

However:

```text
EMP_CMD
CUSTOMER_LOAD_MOD_CMP
```

should be considered different if there is no valid mapping.

The job-name normalization logic must be implemented as a clearly separated function so additional migration naming rules can easily be added.

Example:

```python
normalize_job_name()
```

The original job names must remain unchanged in the output.

Only the validation should use the normalized values.

---

# 7. BOX VALIDATION

Compare the box information between Mainframe and RDS.

Example:

```text
left_box_name  = BOX1
right_box_name = BOX1
```

Result:

```text
box_validation = Matched
```

If:

```text
left_box_name  = BOX1
right_box_name = BOX2
```

Result:

```text
box_validation = Not Matched

validation_reason =
box mismatch: left='BOX1', right='BOX2'
```

If there are legitimate migration box mappings, make them configurable.

Do not hard-code sample values.

---

# 8. MACHINE VALIDATION

Compare machine/server information.

Example:

```text
left_machine_name  = server1
right_machine_name = server1
```

Result:

```text
machine_validation = Matched
```

Example mismatch:

```text
left_machine_name  = server1
right_machine_name = server2
```

Result:

```text
machine_validation = Not Matched

validation_reason =
machine_name mismatch: left='server1', right='server2'
```

Keep the original machine values unchanged.

---

# 9. JOB CONDITION VALIDATION

Compare the job condition/dependency condition.

Example:

```text
left_job_condition  = 1
right_job_condition = 1
```

Result:

```text
job_condition_validation = Matched
```

Mismatch:

```text
left_job_condition  = 1
right_job_condition = 0
```

Result:

```text
job_condition_validation = Not Matched

validation_reason =
job_condition mismatch: left='1', right='0'
```

If the condition contains job names, normalize those job names using the same migration-aware job mapping before determining equivalence.

For example, if:

```text
Left:
s(EMP_CMD)

Right:
s(EMP_MOD_CMP)
```

and `EMP_CMD -> EMP_MOD_CMP` is a valid migration mapping, this should be considered equivalent.

---

# 10. DEPENDENCY VALIDATION

This is one of the most important requirements.

Dependencies can exist:

* Within the same box
* Between different boxes
* Between Mainframe and migrated RDS equivalents

The validation must compare the dependency relationships, not just the text values.

---

# 11. CROSS-BOX DEPENDENCY EXAMPLE

Consider:

```text
BOX1:

J1
J2
J3
J4
```

and:

```text
BOX2:

J5 -> depends on J4
J6 -> depends on J5
J7 -> depends on J6
```

The dependency chain is:

```text
BOX1                       BOX2

J1
J2
J3
J4
 |
 v
J5
 |
 v
J6
 |
 v
J7
```

The important dependency chain is:

```text
J4 -> J5 -> J6 -> J7
```

The validation must understand that `J5` is dependent on `J4` even though they are in different boxes.

---

# 12. CROSS-BOX DEPENDENCY MISMATCH

Suppose Mainframe has:

```text
J4 -> J5
J5 -> J6
J6 -> J7
```

but RDS has:

```text
J4 -> J5
J5 -> J7
```

Then the validation must detect that:

```text
J6 -> J7
```

is missing/different on the RDS side.

Result:

```text
dependency_validation = Not Matched
```

Reason:

```text
dependency mismatch: job='J7', expected dependency='J6', right-side dependency='J5'
```

The exact wording can be adapted to the actual data.

---

# 13. DEPENDENCY GRAPH

Build dependency relationships from the job conditions.

Conceptually:

```text
dependency_job -> dependent_job
```

For example:

```text
J4 -> J5
J5 -> J6
J6 -> J7
```

Use a graph/topological approach where necessary.

The validation should support arbitrary dependency chains.

For example:

```text
J1 -> J2 -> J3 -> J4 -> J5
```

and branches:

```text
       J2
      /  \
     J3   J4
      \   /
       J5
```

The logic must compare the actual dependency graph on both sides.

---

# 14. EXECUTION ORDER VALIDATION

In addition to comparing direct conditions, validate the effective execution order.

For example:

```text
J4 -> J5 -> J6 -> J7
```

means:

```text
J4 must execute before J5
J5 must execute before J6
J6 must execute before J7
```

If the Mainframe and RDS dependency graphs produce different execution ordering, report it.

Create:

```text
order_validation
```

Example:

```text
order_validation = Matched
```

or:

```text
order_validation = Not Matched
```

Reason example:

```text
execution order mismatch: left='J4 -> J5 -> J6 -> J7', right='J4 -> J5 -> J7'
```

Do not assume that the physical row order in the CSV is the execution order.

The execution order must be derived from the dependency/condition relationships where possible.

---

# 15. SCRIPT/PATH VALIDATION

Compare script paths.

Example:

Mainframe:

```text
/root/dev/test1/abc.sh
```

RDS:

```text
/root/dev/test2/abc.sh
```

If the migration rules say these paths should be equivalent, normalize them using a configurable path mapping.

If not equivalent, report:

```text
script_path_validation = Not Matched
```

Example reason:

```text
script_path mismatch:
left='/root/dev/test1/abc.sh',
right='/root/dev2/test1/abc.sh'
```

The validation should identify even small directory differences.

For example:

```text
Left:
/root/dev/test1/abc.sh

Right:
/root/dev1/test1/abc.sh
```

should detect:

```text
dev != dev1
```

Do not modify the original paths.

---

# 16. MULTIPLE MISMATCHES IN ONE ROW

A single row may have multiple differences.

For example:

```text
machine_name      -> mismatch
job_condition     -> mismatch
script_path       -> mismatch
dependency        -> matched
box               -> matched
```

Do not stop at the first mismatch.

Populate every individual validation column.

Example:

```text
machine_validation       = Not Matched
job_validation           = Matched
job_condition_validation = Not Matched
script_path_validation   = Not Matched
dependency_validation    = Matched
box_validation           = Matched
order_validation         = Matched
```

And:

```text
validation_status = Not Matched
```

The `validation_reason` should contain all mismatch reasons:

```text
machine_name mismatch: left='server1', right='server2';
job_condition mismatch: left='1', right='0';
script_path mismatch: left='/root/dev/test1/abc.sh', right='/root/dev1/test1/abc.sh'
```

---

# 17. NULL AND BLANK HANDLING

Handle null, blank, and empty values carefully.

Do not automatically assume:

```text
NULL == ''
```

unless that is an explicitly defined business rule.

At minimum:

* Trim leading/trailing spaces.
* Preserve original values.
* Normalize values only for comparison.
* Do not convert `0` into null/blank.
* Do not convert meaningful strings into null.
* Handle Pandas `NaN` correctly.
* Make case-sensitive/case-insensitive comparison configurable.

Create reusable functions such as:

```python
normalize_value()
normalize_job_name()
normalize_condition()
normalize_script_path()
```

---

# 18. VALIDATION COLUMNS

Append validation columns to the original DataFrame.

At minimum create:

```text
validation_status
validation_reason

job_validation
box_validation
machine_validation
job_condition_validation
dependency_validation
order_validation
script_path_validation
```

If other relevant attributes exist in the actual CSV, create additional validation columns for them as appropriate.

Do not remove existing columns.

---

# 19. OVERALL VALIDATION STATUS

The overall status should be derived from the individual validations.

If all applicable validations are successful:

```text
validation_status = Matched
```

If any applicable validation fails:

```text
validation_status = Not Matched
```

If the job exists only on one side:

```text
validation_status = Not Matched
```

Do not mark a row as matched just because the job name is present.

All applicable validation rules must pass.

---

# 20. VALIDATION REASON

For matched rows:

```text
validation_reason = Matched
```

For mismatched rows, provide detailed reasons.

Example:

```text
machine_name mismatch: left='server1', right='server2';
script_path mismatch: left='/root/dev/test1/abc.sh', right='/root/dev1/test1/abc.sh'
```

For missing jobs:

```text
Job exists only on Mainframe/Non-Mod side
```

or:

```text
Job exists only on RDS/Mod side
```

For dependency mismatch:

```text
dependency mismatch: job='J7', left_dependency='J6', right_dependency='J5'
```

---

# 21. FINAL OUTPUT

Create a new CSV file.

The final CSV must contain:

```text
Original Full-Join Columns
+
Validation Columns
```

Example:

```python
result_df = input_df.copy()

# Add validation columns

result_df["validation_status"] = ...
result_df["validation_reason"] = ...
result_df["job_validation"] = ...
result_df["box_validation"] = ...
result_df["machine_validation"] = ...
result_df["job_condition_validation"] = ...
result_df["dependency_validation"] = ...
result_df["order_validation"] = ...
result_df["script_path_validation"] = ...

result_df.to_csv(output_file, index=False)
```

Do not overwrite the original input CSV.

Create a separate output file such as:

```text
autosys_job_validation_result.csv
```

---

# 22. SUMMARY REPORT

In addition to the row-level output CSV, generate summary counts.

At minimum:

```text
Total Jobs
Matched Jobs
Not Matched Jobs
Jobs Only in Mainframe
Jobs Only in RDS
Job Name Mismatches
Box Mismatches
Machine Mismatches
Job Condition Mismatches
Dependency Mismatches
Execution Order Mismatches
Script Path Mismatches
```

Also generate summary by box:

```text
Box
Total
Matched
Not Matched
```

Example:

```text
BOX1
Total       = 100
Matched     = 90
Not Matched = 10

BOX2
Total       = 75
Matched     = 70
Not Matched = 5
```

Also generate mismatch counts by validation type.

---

# 23. CODE STRUCTURE

Keep the Python implementation modular.

Use separate functions similar to:

```python
load_data()

identify_columns()

normalize_value()

normalize_job_name()

normalize_condition()

normalize_script_path()

validate_job()

validate_box()

validate_machine()

validate_job_condition()

validate_dependencies()

validate_execution_order()

validate_script_path()

build_validation_reason()

generate_summary()

save_output()
```

Do not put the entire logic into one large function.

---

# 24. CONFIGURATION

Create a configuration section at the top of the script for:

```python
INPUT_FILE = "..."
OUTPUT_FILE = "..."

LEFT_PREFIX = "left_"
RIGHT_PREFIX = "right_"

JOB_NAME_MAPPINGS = {}
BOX_MAPPINGS = {}
MACHINE_MAPPINGS = {}
PATH_MAPPINGS = {}
```

Migration-specific rules should be configurable rather than hard-coded throughout the code.

---

# 25. IMPORTANT BUSINESS RULE

The comparison is between:

```text
Mainframe Non-Mod
        VS
RDS Mod/Migrated
```

The objective is to determine whether the **migrated RDS jobs preserve the same functional behavior and dependency/order structure** as the original Mainframe jobs.

Therefore:

* Expected migration naming changes should be normalized.
* Expected path/machine/box mappings should be configurable.
* Actual functional differences should be reported.
* Dependency changes must be detected.
* Cross-box dependencies must be detected.
* Execution-order changes must be detected.

---

# 26. EXPECTED RESULT EXAMPLE

Input row:

```text
left_box_name       = BOX1
left_job_name       = EMP_CMD
left_machine_name   = server1
left_job_condition  = 1
left_script_path    = /root/dev/test1/abc.sh

right_box_name      = BOX1
right_job_name      = EMP_MOD_CMP
right_machine_name  = server2
right_job_condition = 1
right_script_path   = /root/dev1/test1/abc.sh
```

Assume:

```text
EMP_CMD -> EMP_MOD_CMP
```

is a valid migration mapping.

Then:

```text
job_validation           = Matched
box_validation            = Matched
machine_validation        = Not Matched
job_condition_validation  = Matched
script_path_validation    = Not Matched
```

Overall:

```text
validation_status = Not Matched
```

Reason:

```text
machine_name mismatch: left='server1', right='server2';
script_path mismatch: left='/root/dev/test1/abc.sh', right='/root/dev1/test1/abc.sh'
```

All original input columns must still appear in the final row.

---

# 27. IMPORTANT — DO NOT MAKE ASSUMPTIONS

Do not hard-code:

```text
server1
server2
BOX1
BOX2
EMP_CMD
EMP_MOD_CMP
/root/dev/test1/abc.sh
```

These are examples only.

First inspect the actual CSV.

Use the actual data and actual column names.

If the CSV structure is different from the examples, adapt the implementation accordingly.

---

# 28. DELIVERABLE

Provide a complete, executable **Python/Pandas implementation** that:

1. Reads the existing full-joined CSV.
2. Inspects/uses the actual column names.
3. Preserves every original column.
4. Preserves the original row count.
5. Handles jobs missing on either side.
6. Handles migration-specific `_MOD`/`_CMP` job naming.
7. Compares job names.
8. Compares boxes.
9. Compares machines.
10. Compares job conditions.
11. Compares script paths.
12. Builds and compares dependency graphs.
13. Handles dependencies across different boxes.
14. Validates execution order.
15. Detects multiple mismatches in the same row.
16. Creates detailed mismatch reasons.
17. Adds validation columns to the original DataFrame.
18. Writes a new final CSV.
19. Generates validation summary counts.
20. Keeps the implementation modular and configurable.

The final output must be:

```text
ORIGINAL FULL-JOIN DATA
+
VALIDATION RESULTS
```

and **not a replacement/simplified dataset**.
