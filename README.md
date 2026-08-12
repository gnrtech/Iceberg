# Project Context — AutoSys to Informatica End-to-End Migration Validation

Before writing any code, first understand the complete objective and architecture described below.

Do NOT implement anything yet.

First analyze this requirement, understand the relationships between the systems, identify the required data flow, and summarize your understanding back to me.

---

## 1. BUSINESS OBJECTIVE

We are migrating existing jobs from a **Mainframe/Non-Mod environment** to an **RDS/Mod environment**.

We need to validate that the migrated RDS/Mod implementation is functionally equivalent to the original Mainframe/Non-Mod implementation.

The comparison should ultimately happen at the **end-to-end job level**, not simply by comparing individual files.

The final objective is to understand:

```text
AutoSys Job
    ↓
Script / Command
    ↓
Parameter File
    ↓
Informatica Workflow
    ↓
Workflow Parameters
    ↓
Session
    ↓
Mapping
    ↓
Source
    ↓
Target
```

and compare the Mainframe Non-Mod side against the RDS Mod side.

---

# 2. WHY WE ARE DOING THIS

AutoSys is used to schedule and execute jobs.

Those AutoSys jobs may call:

* Shell scripts
* Parameter files
* Informatica workflows
* Other commands

The Informatica workflow then contains:

* Sessions
* Mappings
* Sources
* Targets
* Workflow parameters
* Session parameters
* Dependencies
* Conditions

Therefore, comparing only AutoSys jobs is not enough.

Similarly, comparing only Informatica XML files is not enough.

We need to follow the entire execution chain.

---

# 3. END-TO-END RELATIONSHIP

The expected relationship is approximately:

```text
AutoSys Box
    ↓
AutoSys Job
    ↓
AutoSys Command / Script
    ↓
Shell Script
    ↓
Parameter File
    ↓
Informatica Workflow
    ↓
Workflow Parameters
    ↓
Session
    ↓
Mapping
    ↓
Source / Target
```

The actual structure may vary, so inspect the source data rather than assuming this exact chain.

---

# 4. AUTOSYS DATA

We already have AutoSys job information.

The AutoSys data contains information such as:

```text
Box Name
Job Name
Machine
Command
Condition
Job Type
Order
Other Job Attributes
```

We have Mainframe Non-Mod and RDS Mod versions.

The two sides have already been extracted and full-joined for comparison.

The AutoSys comparison needs to identify:

* Same jobs
* Missing jobs
* Extra jobs
* Box differences
* Machine differences
* Command/script differences
* Job condition differences
* Dependency differences
* Execution-order differences
* Other relevant job attribute differences

---

# 5. AUTOSYS DEPENDENCIES

AutoSys jobs can depend on other jobs.

Dependencies can exist:

* Within the same box
* Across boxes

Example:

```text
BOX1

J1
J2 → J1
J3 → J2
J4 → J3
```

Another box:

```text
BOX2

J5 → J4
J6 → J5
J7 → J6
```

The actual dependency chain is:

```text
J1 → J2 → J3 → J4 → J5 → J6 → J7
```

The comparison must understand these dependencies and execution order.

---

# 6. SCRIPT FILES

AutoSys jobs may call shell scripts.

Example:

```text
AutoSys Job
    ↓
/root/dev/run_customer.sh
```

We will provide the actual script files.

The script may contain:

* Informatica workflow name
* Parameter file path
* Environment variables
* Directory paths
* Commands
* Runtime parameters
* Other configuration

Example:

```bash
WORKFLOW=WF_CUSTOMER
PARAM_FILE=/config/customer.par
```

The script therefore acts as another link in the execution chain.

---

# 7. PARAMETER FILES

We will also provide the actual parameter files.

Example:

```text
/config/customer.par
```

Contents may contain:

```text
SOURCE_DIR=/prod/customer/input
TARGET_DIR=/prod/customer/output
ENV=PROD
FILE_NAME=customer.csv
```

These values must eventually be resolved.

For example:

```text
Workflow XML:
$InputDir/customer.csv

Parameter file:
InputDir=/prod/customer/input

Resolved value:
/prod/customer/input/customer.csv
```

The goal is to determine the **actual runtime value**, not just the variable name.

---

# 8. INFORMATICA WORKFLOW XML

We also have Informatica `workflow.xml` files.

These XML files contain workflow-level information.

We need to extract information such as:

```text
Folder Name
Workflow Name
Workflow Parameters
Workflow Variables
Tasks
Session Name
Session Order
Mapping Name
Sources
Targets
Source File Paths
Target File Paths
Session Parameter File
Session Parameters
Predecessors
Successors
Conditions
Connection Information
Other relevant configuration
```

The XML structure must first be inspected.

Do not assume XML tags without examining the actual files.

---

# 9. INFORMATICA WORKFLOW DEPENDENCIES

A workflow can contain multiple sessions.

Example:

```text
Workflow WF_CUSTOMER

S1
 ↓
S2
 ↓
S3
 ↓
S4
```

The extracted information should preserve:

```text
Session Order
Predecessor
Successor
Condition
```

Parallel branches must also be preserved.

Example:

```text
       S2
      /
S1
      \
       S3
```

---

# 10. MAPPING INFORMATION

Each Informatica session may reference a mapping.

Example:

```text
Workflow
    ↓
Session S1
    ↓
Mapping M_CUSTOMER
    ↓
Source
    ↓
Target
```

We need to extract the actual mapping name and associate it with the correct session.

---

# 11. SOURCE AND TARGET

We need to know the actual source and target used by each mapping/session.

Example:

```text
Source:
CUSTOMER_SRC

Target:
CUSTOMER_TARGET
```

If the source or target is a file, also extract the file path.

Example:

```text
Source:
customer.csv

Source path:
/prod/input/customer/customer.csv
```

---

# 12. PARAMETER RESOLUTION

This is extremely important.

The XML may contain variables instead of actual values.

For example:

```text
XML:
$SOURCE_DIR/customer.csv
```

The parameter file may contain:

```text
SOURCE_DIR=/prod/customer/input
```

The final resolved value should be:

```text
/prod/customer/input/customer.csv
```

Therefore, we need to eventually build a parameter-resolution layer:

```text
XML variable
     ↓
Workflow parameter
     ↓
Parameter file
     ↓
Script/environment variable
     ↓
Actual runtime value
```

The exact precedence must be determined from the actual implementation and files.

Do not assume precedence without inspecting the data.

---

# 13. SCRIPT PARAMETER RESOLUTION

The same concept applies to shell scripts.

Example:

```text
AutoSys command:

/scripts/run_customer.sh -p /config/customer.par
```

The script may contain:

```text
WORKFLOW=WF_CUSTOMER
```

The parameter file contains:

```text
SOURCE_DIR=/prod/customer/input
```

We need to eventually resolve:

```text
AutoSys Job
    ↓
run_customer.sh
    ↓
customer.par
    ↓
WF_CUSTOMER
    ↓
SOURCE_DIR
    ↓
/prod/customer/input
```

---

# 14. MAINFRAME VS RDS

We will have equivalent information for both environments.

Conceptually:

```text
MAINFRAME / NON-MOD
        VS
RDS / MOD
```

For each side we want to construct:

```text
AutoSys Job
Box
Condition
Script
Parameter File
Workflow
Session
Mapping
Source
Target
Actual Parameters
```

Then compare the two end-to-end structures.

---

# 15. MIGRATION-SPECIFIC NAMING

The RDS/Mod side may have naming differences.

For example:

```text
Mainframe:
EMP_CMD

RDS:
EMP_MOD_CMP
```

These may represent the same migrated job.

Similarly, paths may differ:

```text
Mainframe:
/root/dev/test1/abc.sh

RDS:
/root/dev1/test1/abc.sh
```

Some differences may be expected migration transformations.

Therefore, the future comparison framework must support configurable normalization/mapping rules.

Do not assume every textual difference means a functional difference.

---

# 16. FINAL END-TO-END OBJECTIVE

Ultimately we want to produce something like:

```text
Mainframe AutoSys Job
        ↓
Mainframe Script
        ↓
Mainframe Parameter File
        ↓
Mainframe Workflow
        ↓
Mainframe Session
        ↓
Mainframe Mapping
        ↓
Mainframe Source
        ↓
Mainframe Target

              VS

RDS AutoSys Job
        ↓
RDS Script
        ↓
RDS Parameter File
        ↓
RDS Workflow
        ↓
RDS Session
        ↓
RDS Mapping
        ↓
RDS Source
        ↓
RDS Target
```

Then determine:

```text
Matched
```

or identify the exact difference.

---

# 17. IMPORTANT — THIS IS NOT JUST AN XML EXTRACTION PROJECT

The Informatica XML-to-CSV extraction is only an **intermediate step**.

The ultimate goal is:

```text
AutoSys
+
Scripts
+
Parameter Files
+
Informatica XML
+
Resolved Parameters
=
End-to-End Job Inventory
```

This inventory will later be used for Mainframe Non-Mod vs RDS Mod migration validation.

Do not design the XML extraction in a way that prevents us from joining it back to AutoSys jobs, scripts, and parameter files.

Every extracted record must have enough information to trace it back to:

```text
source XML
workflow
session
mapping
script
parameter file
AutoSys job
```

where available.

---

# 18. TRACEABILITY

Every piece of extracted information should be traceable to its source.

For example:

```text
source_xml_file
workflow_name
session_name
mapping_name
parameter_file
script_file
autosys_job
```

This is important because if we find a mismatch later, we need to know exactly which original file/value caused it.

---

# 19. FUTURE FINAL DATA MODEL

The eventual end-to-end dataset should conceptually contain fields such as:

```text
autosys_box
autosys_job
autosys_machine
autosys_condition
autosys_command

script_file
script_command
parameter_file

informatica_folder
workflow_name
workflow_parameter
workflow_parameter_value

session_order
session_name
mapping_name

source
source_file_path
target
target_file_path

session_parameters
resolved_parameters

predecessor
successor
workflow_condition
```

There may be many additional fields.

This is a conceptual model only. Inspect the actual source files before finalizing the schema.

---

# 20. DEVELOPMENT APPROACH

Do not implement everything at once.

The project should be developed in stages:

### Stage 1

Understand and extract AutoSys information.

### Stage 2

Understand and extract scripts.

### Stage 3

Understand and extract parameter files.

### Stage 4

Understand and extract Informatica workflow XML.

### Stage 5

Resolve relationships:

```text
AutoSys → Script → Parameter File → Workflow
```

### Stage 6

Resolve:

```text
Workflow → Session → Mapping → Source/Target
```

### Stage 7

Resolve actual parameter values.

### Stage 8

Build the complete end-to-end inventory.

### Stage 9

Compare Mainframe Non-Mod vs RDS Mod.

---

# 21. CURRENT TASK

For now, **DO NOT WRITE THE IMPLEMENTATION**.

First:

1. Understand this complete objective.
2. Explain the end-to-end relationship in your own words.
3. Identify the major entities and relationships.
4. Identify what information needs to be extracted from each source:

   * AutoSys
   * Script files
   * Parameter files
   * Informatica XML
5. Identify the keys that can be used to connect these datasets.
6. Identify any ambiguities or missing information that must be determined from actual files.
7. Propose a logical intermediate data model.
8. Explain how the final end-to-end Mainframe vs RDS comparison can be performed.

Do not assume the XML structure, script format, parameter-file format, or AutoSys format until the actual files are provided.

The immediate goal is to make sure you fully understand the architecture and end-to-end objective before we start implementation.
