# Kiro AI Prompt — Informatica Workflow XML Extraction for End-to-End AutoSys Migration Validation1

## IMPORTANT — UNDERSTAND THE OBJECTIVE BEFORE CODING

Do not start coding immediately.

First inspect the actual Informatica workflow XML files and understand their real XML structure, namespaces, references, shortcuts, object relationships, and hierarchy.

The ultimate objective is to build an **end-to-end Mainframe Non-Mod vs RDS Mod migration validation**.

The Informatica XML extraction is only one stage.

The eventual end-to-end relationship is:

```text
AutoSys Box
    ↓
AutoSys Job
    ↓
AutoSys Command / Script
    ↓
Script File
    ↓
Parameter File
    ↓
Informatica Workflow
    ↓
Workflow Parameters / Variables
    ↓
Actual Session
    ↓
Mapping
    ↓
Source
    ↓
Target
```

We will eventually perform this for both:

```text
Mainframe / Non-Mod
RDS / Mod
```

and compare the complete execution flow.

---

# 1. CURRENT TASK

I have a folder containing Informatica `workflow.xml` files.

Build a Python parser that recursively reads all XML files and extracts detailed workflow information into CSV.

The parser must first inspect the actual XML structure before deciding how to extract the fields.

The required information includes:

```text
folder_name
workflow_name
workflow_parameters
workflow_variables

task_type
task_name
task_reference

session_name
session_order
execution_level

mapping_name

source
target
source_file_path
target_file_path
file_path

session_parameter_file
session_parameters

predecessor
successor
condition

source_connection
target_connection
```

Also extract other useful Informatica metadata that is available in the XML.

---

# 2. VERY IMPORTANT — DO NOT ASSUME XML STRUCTURE

Do not assume the XML has a simple structure such as:

```xml
<Workflow>
    <Session>
        <Mapping>
            <Source>
            <Target>
```

First inspect actual XML files.

Identify:

* Root element
* XML namespaces
* Folder/repository structure
* Workflow object
* Task objects
* Session objects
* Mapping references
* Source definitions
* Target definitions
* Parameter definitions
* Variable definitions
* Workflow links
* Dependency definitions
* Shortcut/reference structures
* Object IDs
* Repository references
* Any nested relationships

Then explain the discovered structure before implementing the parser.

---

# 3. CRITICAL — ACTUAL SESSION NAME

This is the most important requirement.

Do NOT assume that the workflow task name is the actual Session name.

Do NOT assume that a name beginning with:

```text
Shortcut_
```

is the Session name.

Do NOT remove `Shortcut_`.

Do NOT add/remove prefixes or suffixes.

Do NOT derive the Session name from the task name.

Do NOT derive the Session name from the mapping name.

Do NOT guess the Session name.

Instead, follow the **actual XML references/relationships** to find the underlying Session object and extract the exact Session name stored there.

Conceptually:

```text
Workflow
    ↓
Workflow Task
    ↓
Task Reference / Shortcut / Object Reference
    ↓
Referenced Object
    ↓
Actual Session Definition
    ↓
Exact Session Name
```

For example, the XML may contain something like:

```text
Workflow Task
    ↓
Reference ID = ABC123

Another XML object
    ↓
ID = ABC123
    ↓
Name = <actual session name>
```

The parser must resolve the reference and retrieve the exact `Name` from the actual Session object.

The actual Session name could be anything.

For example:

```text
s_customer_load
Session_Customer
CUSTOMER_SESSION
sess_001
ABC_LOAD
```

These are examples only.

Never assume a naming convention.

---

# 4. SESSION RESOLUTION

Create separate fields where the information exists:

```text
task_name
task_reference
session_reference
session_name
session_resolution_status
session_resolution_reason
```

The important distinction is:

```text
task_name
```

= the actual workflow task name as represented in the workflow.

```text
session_name
```

= the exact name of the underlying Session object resolved from the XML.

For example, if a task references another object, follow the reference.

If resolved:

```text
session_resolution_status = Resolved
```

If not:

```text
session_resolution_status = Unresolved
```

and:

```text
session_resolution_reason =
Unable to resolve Session reference <reference>
```

Do NOT substitute the task name when the actual Session cannot be resolved.

It is better to return `Unresolved` than to guess.

---

# 5. DO NOT NORMALIZE THE ACTUAL SESSION NAME

The actual Session name must be preserved exactly as found in the XML.

Do not:

* Strip prefixes
* Strip suffixes
* Remove `Shortcut_`
* Change case
* Replace characters
* Construct a name
* Infer a name from another field

The value should be the exact Session object's name.

---

# 6. FOLDER NAME

Extract the actual Informatica folder/repository folder.

Column:

```text
folder_name
```

Use the XML/repository information if available.

If the folder is referenced indirectly, resolve the reference.

Do not assume the folder name is the XML filename.

---

# 7. WORKFLOW NAME

Extract the exact workflow name from the actual Workflow object.

Column:

```text
workflow_name
```

Do not derive it from the XML filename unless the XML does not contain a workflow name.

---

# 8. SOURCE XML TRACEABILITY

Every output row must include:

```text
source_xml_file
source_xml_path
```

where appropriate.

This is required for troubleshooting and future migration validation.

---

# 9. WORKFLOW PARAMETERS

Extract all workflow-level parameters.

Columns:

```text
workflow_parameter_name
workflow_parameter_value
```

Preserve all parameters.

If multiple parameters exist, retain them all.

If necessary, represent them as key/value pairs:

```text
$SourceDir=/prod/input;
$TargetDir=/prod/output;
$Environment=PROD
```

Do not lose parameter information.

---

# 10. WORKFLOW VARIABLES

Extract workflow variables separately where Informatica distinguishes them from parameters.

Column:

```text
workflow_variables
```

Preserve variable names and values.

---

# 11. ALL WORKFLOW TASKS

Extract every workflow task.

Possible task types include:

```text
Session
Command
Decision
Assignment
Timer
Event Wait
Email
Worklet
Other
```

Do not extract only Session tasks.

Create:

```text
task_type
task_name
```

Non-session tasks should also retain dependency information where available.

---

# 12. SESSION TASKS

For every Session task:

1. Identify the task.
2. Identify any task reference/shortcut.
3. Follow the reference.
4. Find the actual Session object.
5. Extract the exact Session name.
6. Resolve mapping information.
7. Extract session configuration.

Required fields:

```text
session_name
session_order
execution_level
mapping_name
session_parameter_file
session_parameters
```

---

# 13. SESSION ORDER

Determine the execution order based on workflow dependencies/links.

Do not simply use XML node order.

Example:

```text
S1
 ↓
S2
 ↓
S3
```

should produce:

```text
S1 = 1
S2 = 2
S3 = 3
```

If parallel branches exist:

```text
       S2
      /
S1
      \
       S3
```

do not invent a false sequential order.

Use an execution level where appropriate:

```text
S1 = Level 1
S2 = Level 2
S3 = Level 2
```

Consider including:

```text
execution_level
```

in addition to:

```text
session_order
```

---

# 14. PREDECESSOR

Extract all predecessor tasks.

Column:

```text
predecessor
```

Example:

```text
s_extract
```

For multiple predecessors:

```text
s_extract; s_validate
```

Do not discard dependencies.

---

# 15. SUCCESSOR

Extract all successor tasks.

Column:

```text
successor
```

For multiple successors:

```text
s_load; s_archive
```

---

# 16. WORKFLOW CONDITION

Extract the actual condition associated with workflow links.

Column:

```text
condition
```

Examples may include:

```text
SUCCESS
$Session.Status = 0
Actual Informatica expression
```

Preserve the actual condition.

---

# 17. MAPPING NAME

Resolve the Mapping associated with the actual Session.

Column:

```text
mapping_name
```

Do not assume:

```text
session_name == mapping_name
```

Follow the XML relationship.

If Mapping is referenced indirectly, resolve the reference.

---

# 18. SOURCES

Extract all sources associated with the Mapping/Session.

Column:

```text
source
```

If there are multiple sources:

```text
SRC_CUSTOMER; SRC_ADDRESS; SRC_PHONE
```

Preserve all sources.

---

# 19. TARGETS

Extract all targets.

Column:

```text
target
```

If multiple targets:

```text
TGT_CUSTOMER; TGT_AUDIT
```

Preserve all targets.

---

# 20. SOURCE FILE PATH

If the source is file-based, extract:

```text
source_file_path
```

Example:

```text
$SOURCE_DIR/customer.csv
```

If the XML contains a variable rather than an actual path, preserve the original expression.

Do not guess the final path.

Parameter resolution will happen in a later stage.

---

# 21. TARGET FILE PATH

Extract:

```text
target_file_path
```

If variable-based, preserve the variable expression.

---

# 22. GENERIC FILE PATH

If the XML contains a file path but it cannot clearly be classified as source or target, preserve:

```text
file_path
```

Do not incorrectly assign it.

---

# 23. SESSION PARAMETER FILE

Extract the Session parameter file/reference.

Column:

```text
session_parameter_file
```

Example:

```text
/config/customer.par
```

or:

```text
$PMRootDir/Param/customer.par
```

Preserve exactly what is available in the XML.

---

# 24. SESSION PARAMETERS

Extract all session-level parameters.

Column:

```text
session_parameters
```

Preserve all relevant key/value pairs.

---

# 25. PARAMETER RESOLUTION IS A LATER STAGE

Do not try to fully resolve parameter values if the parameter file is not available yet.

For example, if XML contains:

```text
$SOURCE_DIR/customer.csv
```

preserve:

```text
source_file_path = $SOURCE_DIR/customer.csv
```

Later we will provide the actual parameter files and scripts.

Then we will resolve:

```text
$SOURCE_DIR
    ↓
Parameter file value
    ↓
Actual runtime path
```

The XML extraction must preserve the original variable references so that this later resolution is possible.

---

# 26. CONNECTION INFORMATION

Where available, extract:

```text
source_connection
target_connection
```

and other useful connection metadata.

Never extract passwords, tokens, secrets, private keys, or credentials.

---

# 27. OTHER SESSION CONFIGURATION

Inspect for additional useful fields such as:

```text
session_log_file
session_log_directory
commit_interval
pre_sql
post_sql
error_handling
recovery_strategy
partitioning
integration_service
operating_system_profile
```

If these exist in the actual XML, include them as additional columns.

Do not restrict extraction to only the fields explicitly listed in this prompt.

---

# 28. MULTIPLE SOURCES AND TARGETS

A Session/Mapping may contain multiple sources and targets.

Preserve all values.

Preferred representation:

```text
source = Source1; Source2; Source3

target = Target1; Target2
```

Do not lose data.

---

# 29. WORKFLOW DEPENDENCY GRAPH

Build the dependency graph from actual XML links.

Support:

* Sequential dependencies
* Parallel branches
* Multiple predecessors
* Multiple successors
* Conditional paths
* Branches
* Merges

Store:

```text
predecessor
successor
condition
execution_level
```

---

# 30. NON-SESSION TASKS

Do not discard:

```text
Command
Decision
Assignment
Email
Timer
Event Wait
Worklet
```

Include:

```text
task_type
task_name
predecessor
successor
condition
execution_level
```

Session-specific fields can remain blank.

---

# 31. XML NAMESPACE HANDLING

Properly detect and handle XML namespaces.

Do not assume simple XPath without namespaces.

The implementation should work with:

* Default namespaces
* Prefixed namespaces
* Multiple namespaces

---

# 32. XML REFERENCE RESOLUTION

This is a core requirement.

The parser must resolve references between XML objects.

Look for structures involving:

```text
ID
Reference
Object
Ref
Shortcut
Task
Session
Folder
Workflow
Repository
```

The exact names depend on the actual Informatica XML.

Follow references until the actual object is found.

This applies to:

```text
Session
Mapping
Folder
Workflow
Source
Target
```

where required.

---

# 33. NO GUESSING

If a relationship cannot be resolved:

Do NOT infer it from naming conventions.

Do NOT construct a value.

Do NOT silently use a nearby field.

Instead report:

```text
resolution_status = Unresolved
resolution_reason = ...
```

This is especially important for Session resolution.

---

# 34. OUTPUT — ONE ROW PER LOGICAL TASK/SESSION

The primary CSV should generally contain one row per workflow task/session.

Workflow-level information can repeat across rows.

Example:

```text
folder_name
workflow_name
task_type
task_name
session_name
mapping_name
source
target
...
```

---

# 35. REQUIRED OUTPUT COLUMNS

At minimum:

```text
source_xml_file
source_xml_path

folder_name
workflow_name

task_type
task_name
task_reference

session_reference
session_name
session_resolution_status
session_resolution_reason

workflow_parameter_name
workflow_parameter_value
workflow_variables

session_order
execution_level

mapping_name

source
target
source_file_path
target_file_path
file_path

session_parameter_file
session_parameters

source_connection
target_connection

predecessor
successor
condition
```

Add additional columns when useful fields exist in the XML.

---

# 36. MULTIPLE XML FILES

Recursively process all `.xml` files under the input directory.

Example:

```text
/input/informatica/
    folder1/
        workflow1.xml
        workflow2.xml

    folder2/
        workflow3.xml
```

Combine results into:

```text
informatica_workflow_inventory.csv
```

---

# 37. ERROR HANDLING

If one XML fails, continue processing the remaining files.

Create:

```text
informatica_xml_processing_report.csv
```

with:

```text
source_xml_file
status
error_message
workflow_count
task_count
session_count
resolved_session_count
unresolved_session_count
```

---

# 38. EXTRACTION VALIDATION

For each workflow, validate:

* Workflow name found
* Tasks found
* Session tasks found
* Actual Session references resolved
* Mapping resolved where available
* Sources extracted
* Targets extracted
* Parameter files identified
* Dependencies identified

Flag suspicious cases such as:

```text
Workflow found but zero tasks
Session task found but actual Session unresolved
Session resolved but Mapping unresolved
```

Do not silently produce incomplete information.

---

# 39. SUMMARY

Print:

```text
Total XML files
Successfully processed
Failed files
Total workflows
Total tasks
Total session tasks
Total actual Sessions resolved
Total Sessions unresolved
Total mappings
Total sources
Total targets
Total parameter files
```

---

# 40. SECURITY

Never output:

```text
passwords
secrets
tokens
private keys
credentials
```

Mask or exclude sensitive values.

---

# 41. MODULAR CODE DESIGN

Use modular functions such as:

```python
load_xml_files()
inspect_xml_structure()
extract_namespaces()

extract_folder()
extract_workflow()
extract_workflow_parameters()
extract_workflow_variables()

extract_tasks()
resolve_task_reference()
resolve_session_reference()
extract_actual_session_name()

extract_session()
extract_mapping()
extract_sources()
extract_targets()

extract_file_paths()
extract_parameter_file()
extract_session_parameters()

extract_connections()
extract_dependencies()
calculate_execution_order()

build_output_rows()
generate_processing_report()
generate_summary()
save_csv()
```

Do not put all logic into one large function.

---

# 42. DO NOT HARD-CODE EXAMPLES

Do not hard-code:

```text
Shortcut_to_s_customer_load
s_customer_load
WF_CUSTOMER
m_customer_load
SRC_CUSTOMER
TGT_CUSTOMER
```

These are only examples.

Use the actual XML structure and actual values.

---

# 43. FUTURE END-TO-END INTEGRATION

The extracted Informatica data will later be combined with:

```text
AutoSys CSV
+
Script files
+
Parameter files
+
Informatica workflow CSV
```

The final relationship will be:

```text
AutoSys Box
    ↓
AutoSys Job
    ↓
AutoSys Condition
    ↓
AutoSys Command
    ↓
Script
    ↓
Parameter File
    ↓
Workflow
    ↓
Actual Session
    ↓
Mapping
    ↓
Source
    ↓
Target
    ↓
Resolved Runtime Values
```

Then we will compare:

```text
MAINFRAME NON-MOD
        VS
RDS MOD
```

for migration validation.

---

# 44. TRACEABILITY

Every extracted value should be traceable back to the source XML.

At minimum retain:

```text
source_xml_file
folder_name
workflow_name
task_name
session_name
mapping_name
```

where available.

This will allow us to investigate any migration mismatch later.

---

# 45. CURRENT DELIVERABLE

First inspect the actual XML files.

Before coding, provide:

1. The discovered XML hierarchy.
2. The namespaces.
3. How Workflow objects are represented.
4. How Tasks are represented.
5. How Task references/shortcuts work.
6. How the actual Session object is identified.
7. How the exact Session name is obtained.
8. How Mapping is referenced.
9. How Source/Target are represented.
10. How parameter files are represented.
11. How workflow dependencies are represented.
12. Any ambiguities found.

Then provide the complete executable Python implementation.

## FINAL HARD REQUIREMENT

**The parser must resolve and extract the exact Session name from the actual Session object/reference in the Informatica XML.**

It must NOT:

```text
strip "Shortcut_"
guess the name
construct the name
use the task name as the session name
use the mapping name as the session name
assume a naming convention
```

If the actual Session object cannot be resolved, mark it:

```text
session_resolution_status = Unresolved
```

and explain why.

**Accuracy of the actual Session name and its relationship to the workflow task is more important than producing a populated value.**
