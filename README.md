# Kiro AI Prompt — Dynamic Mainframe Non-Mod vs RDS Mod Validation

I already have a CSV containing the **Full Outer Join** between Mainframe Non-Mod AutoSys jobs and RDS Mod/Migrated AutoSys jobs.

I now need to improve the validation implementation.

The most important requirement is that the validation must be **dynamic based on the actual columns present in the input CSV**.

Do not hard-code only a small list of validation columns such as machine, job condition, or script path.

---

# 1. INPUT CSV

The input is an already-created Full Outer Join CSV.

It contains:

* Mainframe/Non-Mod columns
* RDS/Mod columns
* All existing job attributes

Typical examples could be:

```text
left_box_name
right_box_name

left_job_name
right_job_name

left_machine_name
right_machine_name

left_job_condition
right_job_condition

left_alarm_if_terminated
right_alarm_if_terminated

left_script_path
right_script_path

left_owner
right_owner

left_priority
right_priority

left_run_calendar
right_run_calendar

...
```

However, these are examples only.

The actual CSV may contain many more columns.

---

# 2. FIRST REQUIREMENT — INSPECT ALL COLUMNS

Before writing the validation logic, inspect the actual input DataFrame columns.

Identify all:

```text
left_* columns
right_* columns
```

For example:

```text
left_machine_name
right_machine_name
```

is a corresponding pair.

Likewise:

```text
left_alarm_if_terminated
right_alarm_if_terminated
```

is a corresponding pair.

Likewise:

```text
left_owner
right_owner
```

is a corresponding pair.

The code must automatically discover these pairs.

Do NOT maintain a manually hard-coded list like:

```python
validation_columns = [
    "machine_name",
    "job_condition",
    "script_path"
]
```

Instead dynamically identify the pairs from the actual CSV.

---

# 3. COLUMN PAIRING LOGIC

For every `left_` column:

1. Remove the `left_` prefix.
2. Look for the corresponding `right_` column.

Example:

```text
left_machine_name
right_machine_name
```

Base column:

```text
machine_name
```

Create:

```text
machine_name_validation
```

Another example:

```text
left_alarm_if_terminated
right_alarm_if_terminated
```

Create:

```text
alarm_if_terminated_validation
```

Another example:

```text
left_priority
right_priority
```

Create:

```text
priority_validation
```

The same logic should work for any additional columns found in the CSV.

---

# 4. VALIDATION COLUMN — ONLY ONE COLUMN PER ATTRIBUTE

For every left/right pair, create exactly **ONE validation column**.

Do NOT create:

```text
machine_validation
machine_reason
```

Do NOT create:

```text
alarm_if_terminated_validation
alarm_if_terminated_reason
```

Instead create only:

```text
machine_validation
alarm_if_terminated_validation
```

The validation result and the mismatch reason must be stored in the same column.

---

# 5. VALIDATION COLUMN VALUES

If the left and right values match:

```text
Matched
```

If they do not match, do NOT put:

```text
Not Matched
```

Instead put the actual reason directly into the validation column.

Example:

```text
machine_validation
```

Value:

```text
Matched
```

or:

```text
machine_name mismatch: left='server1', right='server2'
```

---

# 6. EXAMPLE — MACHINE

Input:

```text
left_machine_name  = server1
right_machine_name = server1
```

Output:

```text
machine_validation = Matched
```

If:

```text
left_machine_name  = server1
right_machine_name = server2
```

Output:

```text
machine_validation =
machine_name mismatch: left='server1', right='server2'
```

Do NOT create:

```text
machine_validation = Not Matched
machine_reason = ...
```

Only:

```text
machine_validation = machine_name mismatch: ...
```

---

# 7. EXAMPLE — ALARM_IF_TERMINATED

If the input contains:

```text
left_alarm_if_terminated  = Y
right_alarm_if_terminated = Y
```

Output:

```text
alarm_if_terminated_validation = Matched
```

If:

```text
left_alarm_if_terminated  = Y
right_alarm_if_terminated = N
```

Output:

```text
alarm_if_terminated_validation =
alarm_if_terminated mismatch: left='Y', right='N'
```

This must work even if this column was not explicitly known when the Python code was written.

---

# 8. EXAMPLE — OWNER

If:

```text
left_owner  = ABC
right_owner = ABC
```

Then:

```text
owner_validation = Matched
```

If:

```text
left_owner  = ABC
right_owner = XYZ
```

Then:

```text
owner_validation =
owner mismatch: left='ABC', right='XYZ'
```

---

# 9. EXAMPLE — SCRIPT PATH

If:

```text
left_script_path  = /root/dev/test1/abc.sh
right_script_path = /root/dev/test1/abc.sh
```

Then:

```text
script_path_validation = Matched
```

If:

```text
left_script_path  = /root/dev/test1/abc.sh
right_script_path = /root/dev1/test1/abc.sh
```

Then:

```text
script_path_validation =
script_path mismatch: left='/root/dev/test1/abc.sh', right='/root/dev1/test1/abc.sh'
```

Do not hide small differences.

---

# 10. NULL / BLANK / EMPTY VALUES

Handle NULL and blank values carefully.

The comparison logic must explicitly define how these are treated.

At minimum:

* Trim leading/trailing whitespace.
* Treat actual null/NaN consistently.
* Do not treat `0` as blank.
* Do not treat `0` and null as equal.
* Do not modify the original values.
* Preserve the original left/right columns.

If both are null/blank according to the defined normalization rule:

```text
Matched
```

If only one side is null/blank:

```text
<column> mismatch: left='<value>', right='<value>'
```

---

# 11. JOB NAME SPECIAL RULE

Job names may have migration-specific naming differences.

For example:

```text
left_job_name  = EMP_CMD
right_job_name = EMP_MOD_CMP
```

The RDS Mod side may contain `_MOD`, `_CMP`, or other migration-specific suffixes.

Implement a configurable job-name normalization/mapping function.

For example:

```python
normalize_job_name()
```

The original values must remain unchanged.

Only the validation comparison should use normalized values.

Do not hard-code only:

```text
EMP_CMD
EMP_MOD_CMP
```

because the real CSV contains many jobs.

---

# 12. JOB CONDITION / DEPENDENCY SPECIAL VALIDATION

Job conditions require additional logic because they represent AutoSys dependencies.

For example:

```text
BOX1:

J1
J2
J3
J4

BOX2:

J5 -> J4
J6 -> J5
J7 -> J6
```

The effective dependency chain is:

```text
J4 -> J5 -> J6 -> J7
```

The validation must compare Mainframe and RDS dependency relationships.

It must support:

* Same-box dependencies
* Cross-box dependencies
* Multiple dependencies
* Dependency chains
* Branching dependencies
* Migration job-name mappings

If the dependency relationship differs, the appropriate validation column should contain the actual reason.

For example:

```text
job_condition_validation =
dependency mismatch: job='J7', left_dependency='J6', right_dependency='J5'
```

If equivalent:

```text
job_condition_validation = Matched
```

---

# 13. EXECUTION ORDER

Where dependency information is available, derive the execution order from the dependency graph rather than relying only on the physical CSV row order.

Example:

```text
J4 -> J5 -> J6 -> J7
```

means:

```text
J4 before J5
J5 before J6
J6 before J7
```

Compare the Mainframe and RDS dependency/order relationships.

If they are equivalent:

```text
order_validation = Matched
```

If different:

```text
order_validation =
execution order mismatch: left='J4 -> J5 -> J6 -> J7', right='J4 -> J5 -> J7'
```

---

# 14. BOX VALIDATION

If the CSV contains:

```text
left_box_name
right_box_name
```

create:

```text
box_name_validation
```

If equal:

```text
Matched
```

If different:

```text
box_name mismatch: left='BOX1', right='BOX2'
```

Support configurable box mappings if migration rules allow different box names.

---

# 15. MISSING JOBS

Because the input is a Full Outer Join, handle jobs that exist only on one side.

If:

```text
left_job_name  = EMP_CMD
right_job_name = null
```

then:

```text
job_validation =
Job exists only on Mainframe/Non-Mod side
```

If:

```text
left_job_name  = null
right_job_name = EMP_MOD_CMP
```

then:

```text
job_validation =
Job exists only on RDS/Mod side
```

---

# 16. OVERALL VALIDATION STATUS

Create one overall column:

```text
validation_status
```

This column can contain:

```text
Matched
Not Matched
```

Rules:

If every applicable validation passes:

```text
validation_status = Matched
```

If any validation fails:

```text
validation_status = Not Matched
```

The detailed reason must remain in the individual validation columns.

For example:

```text
machine_validation =
machine_name mismatch: left='server1', right='server2'

alarm_if_terminated_validation =
Matched

script_path_validation =
script_path mismatch: left='/root/dev/test1/abc.sh', right='/root/dev1/test1/abc.sh'

validation_status =
Not Matched
```

---

# 17. OVERALL VALIDATION REASON

Do NOT create a separate reason column for every attribute.

However, create one overall:

```text
validation_reason
```

that combines all failed validation messages.

Example:

```text
validation_reason =
machine_name mismatch: left='server1', right='server2';
script_path mismatch: left='/root/dev/test1/abc.sh', right='/root/dev1/test1/abc.sh'
```

If everything matches:

```text
validation_reason = Matched
```

This gives us both:

1. Individual validation result/reason
2. Overall summary reason

---

# 18. IMPORTANT — DO NOT CREATE DUPLICATE REASON COLUMNS

Do NOT create:

```text
machine_validation
machine_reason

alarm_if_terminated_validation
alarm_if_terminated_reason

script_path_validation
script_path_reason
```

Instead:

```text
machine_validation
alarm_if_terminated_validation
script_path_validation
```

Each validation column contains either:

```text
Matched
```

or the actual mismatch explanation.

---

# 19. DYNAMIC VALIDATION COLUMN GENERATION

The implementation should work approximately like this:

```python
for left_column in left_columns:

    base_column = left_column.replace("left_", "", 1)

    right_column = f"right_{base_column}"

    if right_column not in df.columns:
        continue

    validation_column = f"{base_column}_validation"

    # Compare left and right values

    # If equivalent:
    #     validation_column = "Matched"
    #
    # Otherwise:
    #     validation_column =
    #         f"{base_column} mismatch: left='{left_value}', right='{right_value}'"
```

But do not blindly apply generic comparison to columns that require special business logic.

Create special handlers for:

```text
job_name
job_condition
dependency
script_path
box
machine
order
```

For all other ordinary left/right attributes, use the generic comparison.

---

# 20. SPECIAL VS GENERIC VALIDATION

Use two types of validation.

### Generic attributes

For example:

```text
owner
priority
alarm_if_terminated
run_calendar
notification
description
```

Use normal left/right comparison.

Example:

```text
left_alarm_if_terminated  = Y
right_alarm_if_terminated = N
```

Result:

```text
alarm_if_terminated_validation =
alarm_if_terminated mismatch: left='Y', right='N'
```

### Special attributes

Use dedicated logic for:

```text
job_name
job_condition
dependency
script_path
box
machine
order
```

because these may require normalization or dependency analysis.

---

# 21. DO NOT MISS ANY COLUMN

This is critical.

After reading the CSV, print/log:

```text
Total input columns:
Total left columns:
Total right columns:
Matched left/right column pairs:
Left-only columns:
Right-only columns:
Validation columns created:
```

For example:

```text
Total input columns: 120
Left columns: 55
Right columns: 55
Matched pairs: 55
Left-only columns: 5
Right-only columns: 5
Validation columns created: 55
```

This allows us to verify that attributes such as:

```text
alarm_if_terminated
```

were not accidentally missed.

---

# 22. LEFT-ONLY / RIGHT-ONLY COLUMNS

If a left column has no corresponding right column, do not silently ignore it.

Report it in the logs/summary:

```text
Left-only column:
left_some_attribute
```

Likewise:

```text
Right-only column:
right_some_attribute
```

Do not create a validation column for an unmatched column unless explicitly required.

But clearly report these columns so we know they were not compared.

---

# 23. FINAL OUTPUT STRUCTURE

The final DataFrame must be:

```text
ORIGINAL INPUT COLUMNS
+
DYNAMIC VALIDATION COLUMNS
+
OVERALL validation_status
+
OVERALL validation_reason
```

For example:

```text
left_job_name
right_job_name
left_machine_name
right_machine_name
left_alarm_if_terminated
right_alarm_if_terminated
left_script_path
right_script_path
...

job_name_validation
machine_name_validation
alarm_if_terminated_validation
script_path_validation
job_condition_validation
dependency_validation
box_name_validation
order_validation
...

validation_status
validation_reason
```

All original columns must remain unchanged.

---

# 24. ROW COUNT

The final output must have the same number of rows as the input Full Outer Join.

Do not perform another join that changes the row count.

Example:

```text
Input rows  = 50,000
Output rows = 50,000
```

---

# 25. SUMMARY

Generate summary statistics after validation.

At minimum:

```text
Total rows
Matched rows
Not Matched rows
```

And for every dynamically created validation column:

```text
column_name
Matched count
Mismatch count
```

Example:

```text
machine_name_validation
Matched       = 9,500
Mismatch      = 500

alarm_if_terminated_validation
Matched       = 9,800
Mismatch      = 200

script_path_validation
Matched       = 9,700
Mismatch      = 300
```

Also show:

```text
Left-only columns
Right-only columns
Paired columns
Validation columns created
```

---

# 26. FINAL IMPLEMENTATION REQUIREMENT

Provide complete executable Python/Pandas code.

The code must:

1. Read the existing Full Outer Join CSV.
2. Inspect all actual columns.
3. Dynamically identify `left_*` and `right_*` pairs.
4. Create one validation column for every comparable pair.
5. Put `Matched` into the validation column when values match.
6. Put the actual mismatch reason directly into that validation column when values differ.
7. Do NOT create separate reason columns for each attribute.
8. Create one overall `validation_status`.
9. Create one overall `validation_reason`.
10. Preserve every original input column.
11. Preserve original input values.
12. Preserve the original row count.
13. Handle missing jobs.
14. Handle migration-specific job-name mappings.
15. Handle AutoSys job conditions.
16. Handle cross-box dependencies.
17. Handle execution order.
18. Handle script path differences.
19. Handle NULL/blank values correctly.
20. Dynamically include columns such as `alarm_if_terminated` and any other attributes present in the CSV.
21. Report left-only and right-only columns.
22. Generate validation summary counts.
23. Write the final result to a NEW CSV without modifying the original input CSV.

The key design principle is:

```text
DO NOT HARD-CODE THE VALIDATION COLUMNS.

FIRST DISCOVER ALL LEFT/RIGHT COLUMN PAIRS.
THEN CREATE VALIDATION COLUMNS DYNAMICALLY.

For every validation column:

MATCH    -> "Matched"
MISMATCH -> "<actual mismatch reason>"

Do NOT use:
"Mismatched" + separate reason column.
```

=======
1==>
Coding (Quality Code, Abides to Coding Principles, Ownership of the code) 1) High quality code 2) Code meets functionality 3) Unit tested (automated) 4) Code review and evidence 5) Mentoring team members during coding & code review 6) Doneness criteria met

 Writes clean and well-organized code, making it easy to understand and maintain.
 Consistently adheres to coding standards, ensuring code consistency across the project.
 Effectively applies design patterns to improve code structure and maintainability.
 Implemented unit tests for 2 repos (ODS Data & Streaming Core) with 90% code coverage.
 For Each PR , will will provide proper description of the change and will attach test document.
 Ensure that all unit tests are automated and integrated into the CI/CD pipeline.
 Actively participates in code reviews, providing constructive feedback to improve code quality.
 




2==>
Design & Architecture (Quality of Design, Abides to the Design Principles, Abides to the Architectural Guidelines, UML based design, Maintains a consistent, clean and efficient approach to coding) 1) Architecture & Design practices addressing performance, maintenance, enhancement, feature addition, non functional requirements etc. 2) Clean, simple and consistent design 3) Well documented design & architecture 4) Good OO practices including usage of design patterns as needed 5) Reuse (as applicable)

I have diligently applied architectural practices that address key aspects such as performance, maintenance, and scalability. By conducting thorough performance assessments and integrating optimization strategies, I have ensured that the architecture supports current and future requirements
My design approach emphasizes simplicity and consistency, aiming to create clean and understandable architectures.
I  prioritize comprehensive documentation for all design and architectural elements. 
My documentation includes detailed descriptions of design decisions, architecture diagrams, and usage guidelines. This practice ensures that team members have a clear understanding of the system’s structure and functionality, which facilitates smoother onboarding and knowledge transfer.
I  consistently apply good object-oriented (OO) practices and utilize design patterns as appropriate. By adhering to principles such as encapsulation, inheritance, and polymorphism
I have actively sought opportunities for code and design reuse to enhance efficiency and reduce redundancy.
Each project will maintain seperate utils package to define common functionalites 

3==>
Successful Delivery 1) Timeliness of deliverables 2) Proactive reporting including escalations of issues/ risks 3) Cost consciousness

I have consistently demonstrated a strong commitment to meeting project deadlines by effectively managing my time and resources. 
I have maintained a proactive stance on reporting progress and potential issues. By providing regular updates and addressing concerns early, I have ensured that stakeholders are well-informed and that any risks or obstacles are managed promptly.
I am mindful of cost implications throughout the project lifecycle. By carefully managing resources and seeking cost-effective solutions.
4==>
Technical mentoring 1) Mentoring and grooming junior team members
 
 I have actively mentored junior team members by providing clear guidance, support, and constructive feedback on their work.
 Shared insights and best practices related to technologies and processes, ensuring that junior team members understand and can apply them effectively

5==>
Motivating team members 1)Encouraging a participative work culture and flexibility in dealing with different personalities/ situations.

I actively encourage team members to take initiative and contribute to decision-making processes. 
By soliciting input from everyone and valuing their contributions, I have empowered team members to take ownership of their tasks and feel more invested in the team's success. This participative approach has fostered a sense of camaraderie and collective responsibility
I have prioritized open and transparent communication within the team, which has been crucial in fostering a collaborative work culture. 
By actively listening to feedback and encouraging dialogue, I have been able to address concerns promptly and keep the team aligned on our goals. This has also facilitated better problem-solving and a more supportive team dynamic.


6==>
Technical/ functional expertise 1) Knowledge of relevant technologies used in project, application, business/ domain of the customer 2) Analytical skills 3) Problem solving capabilities 4) Understanding of application & business requirements to support decision making at project execution

I take up training and upskilling every quarter to stay relevant for my role
Maintained up-to-date knowledge of how these technologies integrate with the application and meet the needs of the business/domain
I have effectively used analytical tools and techniques to interpret complex data sets and derive actionable insights.
Developed and implemented solutions that resolved issues and improved project performance.
Effectively communicated requirements to stakeholders and team members, facilitating smooth project execution.

7==>
Quality Process Compliance/Orientation 1) Process documentation 2) Causal analysis 3) Support SEPG to define standards 4) Process metrics (All the above are related to technical/ technology areas)

Will maintain process document for each project in GH Docs, ensuring it is comprehensive and easily understandable.
Regularly reviewed and validated documentation to ensure it accurately reflects current processes and practices.
Ensured that all documentation is readily accessible to team members and stakeholders, facilitating compliance and process adherence.
Developed and implemented corrective actions based on causal analysis findings to prevent recurrence of issues 
Actively participated in discussions and workshops with the SEPG to help define and refine technical standards.

8==>
Revenue / Profit Realization 1) Timely Realization of entire revenue 2) Gross Profit Margin Target achievement 3) Cost Control through pyramid management & other actions 4) Timely submission of filled timesheet by the team members

9==>
Meeting or exceeding client expectations 1) Feedback from customer (if applicable) on overall performance (communication, technical, responsiveness, teamwork etc.) 2) Enabling growth in the existing customer/ account/ project 3) Contributions to a successful partnership (feedback, ideas, alternate ways of doing things etc.)



=====
1)
Meeting or exceeding client expectations 1) Feedback from customer (if applicable) on overall performance (communication, technical, responsiveness, teamwork etc.) 2) Enabling growth in the existing customer/ account/ project 3) Contributions to a successful partnership (feedback, ideas, alternate ways of doing things etc.)
Collaborating closely with clients to understand their needs and develop mutually beneficial solutions
Providing constructive feedback and suggestions for improvement, helping to identify and address potential issues

2)
Revenue / Profit Realization 1) Timely Realization of entire revenue 2) Gross Profit Margin Target achievement 3) Cost Control through pyramid management & other actions 4) Timely submission of filled timesheet by the team members
Submitting my timesheet on time and in full each week
Double-checking my hours worked and accuracy of information


3)
Quality Process Compliance/Orientation 1) Process documentation 2) Causal analysis 3) Support SEPG to define standards 4) Process metrics (All the above are related to technical/ technology areas)

	Will maintain process document for each project in GH Docs, ensuring it is comprehensive and easily understandable.
	Regularly reviewed and validated documentation to ensure it accurately reflects current processes and practices.
	Ensured that all documentation is readily accessible to team members and stakeholders, facilitating compliance and process adherence.
	Developed and implemented corrective actions based on causal analysis findings to prevent recurrence of issues 
	Actively participated in discussions and workshops with the SEPG to help define and refine technical standards.


4)
Technical/ functional expertise 1) Knowledge of relevant technologies used in project, application, business/ domain of the customer 2) Analytical skills 3) Problem solving capabilities 4) Understanding of application & business requirements to support decision making at project execution

	I take up training and upskilling every quarter to stay relevant for my role.
	Maintained up-to-date knowledge of how these technologies integrate with the application and meet the needs of the business/domain
	I have effectively used analytical tools and techniques to interpret complex data sets and derive actionable insights.
	Developed and implemented solutions that resolved issues and improved project performance.
	Effectively communicated requirements to stakeholders and team members, facilitating smooth project execution.

5)
Motivating team members 1)Encouraging a participative work culture and flexibility in dealing with different personalities/ situations.

	I actively encourage team members to take initiative and contribute to decision-making processes. 
	By soliciting input from everyone and valuing their contributions, I have empowered team members to take ownership of their tasks and feel more invested in the team's success. This participative approach has fostered a sense of camaraderie and collective responsibility
	I have prioritized open and transparent communication within the team, which has been crucial in fostering a collaborative work culture. 
	By actively listening to feedback and encouraging dialogue, I have been able to address concerns promptly and keep the team aligned on our goals. This has also facilitated better problem-solving and a more supportive team dynamic.

6)
Technical mentoring 1) Mentoring and grooming junior team members

As a technical mentor I'm helping junior team members develop their skills and knowledge, and to ensure that they are equipped to handle their responsibilities effectively

7)
Successful Delivery 1) Timeliness of deliverables 2) Proactive reporting including escalations of issues/ risks 3) Cost consciousness
	
	I have consistently demonstrated a strong commitment to meeting project deadlines by effectively managing my time and resources. 
	I have maintained a proactive stance on reporting progress and potential issues. By providing regular updates and addressing concerns early, I have ensured that stakeholders are well-informed and that any risks or obstacles are managed promptly.
	I am mindful of cost implications throughout the project lifecycle. By carefully managing resources and seeking cost-effective solutions.

8)
Coding (Quality Code, Abides to Coding Principles, Ownership of the code) 1) High quality code 2) Code meets functionality 3) Unit tested (automated) 4) Code review and evidence 5) Mentoring team members during coding & code review 6) Doneness criteria met

	 Writes clean and well-organized code, making it easy to understand and maintain.
	 Consistently adheres to coding standards, ensuring code consistency across the project.
	 Effectively applies design patterns to improve code structure and maintainability.
	 Implemented unit tests for 2 repos (ODS Data & Streaming Core) with 90% code coverage.
	 For Each PR , will will provide proper description of the change and will attach test document.
	 Ensure that all unit tests are automated and integrated into the CI/CD pipeline.
	 Actively participates in code reviews, providing constructive feedback to improve code quality.

9)
Design & Architecture (Quality of Design, Abides to the Design Principles, Abides to the Architectural Guidelines, UML based design, Maintains a consistent, clean and efficient approach to coding) 1) Architecture & Design practices addressing performance, maintenance, enhancement, feature addition, non functional requirements etc. 2) Clean, simple and consistent design 3) Well documented design & architecture 4) Good OO practices including usage of design patterns as needed 5) Reuse (as applicable)

	I have diligently applied architectural practices that address key aspects such as performance, maintenance, and scalability. By conducting thorough performance assessments and integrating optimization strategies, I have ensured that the architecture supports current and future requirements
	My design approach emphasizes simplicity and consistency, aiming to create clean and understandable architectures.
	I prioritize comprehensive documentation for all design and architectural elements. 
	My documentation includes detailed descriptions of design decisions, architecture diagrams, and usage guidelines. This practice ensures that team members have a clear understanding of the system’s structure and functionality, which facilitates smoother onboarding and knowledge transfer.
	I consistently apply good object-oriented (OO) practices and utilize design patterns as appropriate. By adhering to principles such as encapsulation, inheritance, and polymorphism
	I have actively sought opportunities for code and design reuse to enhance efficiency and reduce redundancy.
	Each project will maintain separate utils package to define common functionalities 
