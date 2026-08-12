# Kiro AI Prompt — Informatica Workflow XML to CSV Extraction

I have a folder containing multiple **Informatica workflow XML files**.

I need a complete **Python XML parser** that reads all Informatica workflow XML files from the input folder and extracts detailed workflow/session/mapping/source/target/parameter information into CSV.

The XML structure may vary between files, so **do not assume the XML tags or hierarchy from the examples below**.

First inspect the actual XML files and identify the Informatica XML structure, namespaces, attributes, and relationships. Then implement the parser based on the actual structure.

---

# 1. OBJECTIVE

Convert Informatica workflow XML files into a structured CSV containing, at minimum:

```text
folder_name
workflow_name
workflow_parameter_name
workflow_parameter_value
session_order
session_name
session_task_type
mapping_name
source
target
file_path
session_parameter_file
session_parameters
workflow_variables
predecessor
successor
condition
```

The parser should extract as much relevant information as available from the XML.

The final CSV should have **one logical row per workflow session/task**, with workflow-level and session-level information associated with that row.

---

# 2. INPUT

The input is a directory containing multiple XML files.

Example:

```text
/input/informatica/
    workflow1.xml
    workflow2.xml
    workflow3.xml
    workflow4.xml
```

The program should recursively scan the input directory so XML files inside subdirectories are also processed.

For example:

```text
/input/informatica/
    folder1/
        workflow1.xml
        workflow2.xml

    folder2/
        workflow3.xml
```

The parser must process all `.xml` files.

---

# 3. FIRST — INSPECT THE XML STRUCTURE

Before implementing the extraction logic:

1. Read sample XML files.
2. Identify the root element.
3. Identify XML namespaces.
4. Identify workflow elements.
5. Identify folder/repository information.
6. Identify workflow names.
7. Identify workflow variables.
8. Identify workflow parameters.
9. Identify tasks.
10. Identify session tasks.
11. Identify session order.
12. Identify mappings.
13. Identify source definitions.
14. Identify target definitions.
15. Identify source/target file paths.
16. Identify session parameter files.
17. Identify session parameter values.
18. Identify workflow links/dependencies.
19. Identify predecessor/successor relationships.
20. Identify dependency conditions.
21. Identify any other useful workflow metadata.

Do not hard-code the XML tags until the actual XML structure has been inspected.

---

# 4. FOLDER NAME

Extract the Informatica folder/repository folder name if it exists in the XML.

Output:

```text
folder_name
```

Example:

```text
folder_name = CUSTOMER_DATA
```

If the folder name is not explicitly stored in the XML, derive it from the appropriate source such as:

* XML metadata
* Repository folder attribute
* Parent directory name

Do not blindly use the XML filename as the folder name unless that is actually how the source data is structured.

---

# 5. WORKFLOW NAME

Extract the workflow name.

Output:

```text
workflow_name
```

Example:

```text
workflow_name = wf_customer_load
```

If the XML contains workflow-level metadata, preserve it where useful.

---

# 6. WORKFLOW PARAMETERS

Extract all workflow-level parameters and variables.

Create:

```text
workflow_parameter_name
workflow_parameter_value
```

If multiple workflow parameters exist, determine the best representation.

Prefer one of the following approaches depending on the XML structure:

### Option A — Multiple parameter columns

If the parameter names are stable:

```text
workflow_parameter_$Source
workflow_parameter_$Target
workflow_parameter_$Environment
```

### Option B — Structured value

If parameters are dynamic:

```text
workflow_parameters
```

with a readable representation such as:

```text
$Source=/data/input;
$Target=/data/output;
$Environment=PROD
```

Use the approach that works best for the actual XML structure.

Do not lose any workflow parameters.

---

# 7. WORKFLOW VARIABLES

Extract workflow variables separately from workflow parameters where the XML distinguishes them.

Output:

```text
workflow_variables
```

Example:

```text
$$SOURCE_DIR=/data/source;
$$TARGET_DIR=/data/target;
$$ENV=PROD
```

Preserve parameter names and values.

---

# 8. WORKFLOW TASKS

Identify all tasks inside each workflow.

Possible task types may include:

```text
Session
Command
Decision
Assignment
Event Wait
Timer
Email
Worklet
Other Informatica task types
```

Do not assume only Session tasks exist.

Extract:

```text
session_task_type
```

or preferably:

```text
task_type
```

Example:

```text
task_type = Session
```

---

# 9. SESSION NAME

For every Session task, extract:

```text
session_name
```

Example:

```text
session_name = s_customer_load
```

The session name should come from the actual XML task definition.

---

# 10. SESSION ORDER

Determine the execution order of sessions/tasks within the workflow.

Output:

```text
session_order
```

Example:

```text
1
2
3
4
```

Important:

Do NOT simply use the physical order in which XML nodes appear.

The correct order should preferably be derived from the workflow links/dependencies.

For example:

```text
Session_A
    ↓
Session_B
    ↓
Session_C
```

should result in:

```text
Session_A = 1
Session_B = 2
Session_C = 3
```

If the workflow has parallel branches:

```text
             Session_B
            /
Session_A
            \
             Session_C
```

then:

```text
Session_A = 1
Session_B = 2
Session_C = 2
```

or use a suitable execution level/stage representation.

The parser must preserve the actual dependency relationships.

---

# 11. PREDECESSOR

For every task/session, identify the predecessor task(s).

Output:

```text
predecessor
```

Example:

```text
session_name = s_customer_load
predecessor = s_extract_customer
```

If there are multiple predecessors:

```text
predecessor =
s_extract_customer; s_validate_customer
```

Do not discard multiple dependencies.

---

# 12. SUCCESSOR

Also identify successor tasks.

Output:

```text
successor
```

Example:

```text
successor = s_load_customer
```

For multiple successors:

```text
successor =
s_load_customer; s_archive_customer
```

---

# 13. CONDITION

Extract the workflow link condition if present.

Output:

```text
condition
```

Example:

```text
condition = SUCCESS
```

or:

```text
condition = $Session.Status = 0
```

Preserve the actual condition from the XML.

Do not simplify or remove important expressions.

---

# 14. MAPPING NAME

For every Session task, identify the mapping associated with the session.

Output:

```text
mapping_name
```

Example:

```text
mapping_name = m_customer_load
```

The mapping may be referenced indirectly through session configuration.

Follow the XML relationships to correctly associate:

```text
Workflow
   ↓
Session
   ↓
Mapping
```

Do not assume that the session name and mapping name are the same.

---

# 15. SOURCES

Extract all source objects used by the mapping/session.

Output:

```text
source
```

Examples:

```text
SRC_CUSTOMER
SRC_ADDRESS
SRC_ORDER
```

If multiple sources exist, preserve all of them.

Example:

```text
source =
SRC_CUSTOMER; SRC_ADDRESS; SRC_PHONE
```

Do not create separate rows unnecessarily unless the XML structure requires one row per source.

---

# 16. TARGETS

Extract all target objects.

Output:

```text
target
```

Example:

```text
target = TGT_CUSTOMER
```

For multiple targets:

```text
target =
TGT_CUSTOMER; TGT_CUSTOMER_AUDIT
```

Preserve all target information.

---

# 17. SOURCE FILE PATH

If the source is a file, extract the file path.

Example:

```text
file_path =
/data/source/customer/customer.csv
```

If there are multiple source files, preserve all relevant paths.

If the XML distinguishes source and target file paths, create separate columns:

```text
source_file_path
target_file_path
```

Prefer this approach if the XML provides enough information.

---

# 18. TARGET FILE PATH

Extract target file paths where available.

Example:

```text
target_file_path =
/data/output/customer/customer.csv
```

Do not confuse:

```text
source
target
file_path
```

These may represent different concepts.

Use the actual XML structure to determine the correct mapping.

---

# 19. SESSION PARAMETER FILE

Extract the Session parameter file.

Output:

```text
session_parameter_file
```

Examples:

```text
$PMRootDir/Param/customer.param
```

or:

```text
/config/informatica/customer_session.par
```

If the XML contains the parameter file as an attribute or nested element, correctly follow that relationship.

---

# 20. SESSION PARAMETERS

Extract session-level parameters/configuration.

Output:

```text
session_parameters
```

Examples:

```text
$SourceDir=/data/source;
$TargetDir=/data/target;
$FileName=customer.csv
```

Preserve all available parameters.

If the XML contains many parameter values, do not silently discard them.

Use a readable key/value representation.

---

# 21. SESSION CONFIGURATION

Also inspect the XML for useful session configuration such as:

```text
session log file
session log directory
workflow log
error handling
commit interval
source connection
target connection
source database
target database
pre-SQL
post-SQL
parameter file
operating system profile
integration service
partitioning
recovery strategy
```

If these fields are present and useful, include them as additional CSV columns.

The implementation should be extensible.

---

# 22. CONNECTION INFORMATION

Where available, extract:

```text
source_connection
target_connection
```

or equivalent Informatica connection information.

Examples:

```text
source_connection = ORACLE_PROD
target_connection = SNOWFLAKE_PROD
```

Do not expose credentials/passwords.

If the XML contains sensitive credentials, do NOT output passwords, secrets, tokens, or private keys.

---

# 23. MULTIPLE SOURCES AND TARGETS

A mapping may contain:

```text
Source1
Source2
Source3
```

and:

```text
Target1
Target2
```

The CSV should retain all of them.

Preferred representation:

```text
source =
Source1; Source2; Source3

target =
Target1; Target2
```

Do not lose information.

If source/target details need more granular reporting, optionally generate a second normalized CSV, but the primary requested CSV must contain the complete workflow/session information.

---

# 24. ONE ROW PER SESSION/TASK

The primary output should generally contain:

```text
one row = one workflow session/task
```

Example:

```text
folder_name | workflow_name | session_order | session_name | mapping_name | source | target | ...
```

Example:

```text
CUSTOMER
wf_customer_load
1
s_extract_customer
m_extract_customer
SRC_CUSTOMER
STG_CUSTOMER
...
```

Then:

```text
CUSTOMER
wf_customer_load
2
s_transform_customer
m_transform_customer
STG_CUSTOMER
TGT_CUSTOMER
...
```

---

# 25. NON-SESSION TASKS

If the workflow contains non-session tasks such as:

```text
Command
Decision
Assignment
Email
Timer
Event Wait
Worklet
```

do not silently ignore them.

Depending on the XML structure, include them with:

```text
task_type
task_name
```

and leave session-specific fields blank.

Example:

```text
task_type = Command
task_name = cmd_archive
session_name = null
mapping_name = null
```

This ensures the workflow structure is not lost.

---

# 26. WORKFLOW DEPENDENCY GRAPH

Build the workflow dependency graph.

For example:

```text
s_extract
   ↓
s_validate
   ↓
s_load
```

Store:

```text
predecessor
successor
condition
```

This will allow downstream comparison with other workflow formats later.

If the workflow contains:

```text
s_extract
    ↓
decision
   ↙   ↘
s_load  s_error
```

preserve both branches.

---

# 27. SESSION ORDER / EXECUTION LEVEL

Calculate a deterministic execution level based on dependencies.

For example:

```text
Level 1:
s_extract

Level 2:
s_validate
s_validate_address

Level 3:
s_load
```

Store the numeric level in:

```text
session_order
```

If exact ordering cannot be determined because tasks run in parallel, do not invent an arbitrary order.

Instead, use the same execution level for parallel tasks.

Optionally create:

```text
execution_level
```

if this is clearer than overloading `session_order`.

---

# 28. XML NAMESPACE HANDLING

The parser must properly handle XML namespaces.

Do not assume:

```python
root.find("Workflow")
```

will work.

Inspect namespaces first.

Support XML documents with namespaces such as:

```xml
<Workflow xmlns="...">
```

or prefixed namespaces.

Create reusable namespace-aware helper functions.

---

# 29. XML PARSING

Prefer Python standard library:

```python
xml.etree.ElementTree
```

or `lxml` if the project already uses it.

The parser should:

* Handle malformed XML gracefully.
* Log which file failed.
* Continue processing remaining files.
* Provide an error report.

Example:

```text
workflow1.xml -> SUCCESS
workflow2.xml -> SUCCESS
workflow3.xml -> ERROR
```

Do not stop the entire process because one XML file is invalid.

---

# 30. FILE-LEVEL METADATA

Also add:

```text
source_xml_file
source_xml_path
```

so every CSV row can be traced back to the original XML.

Example:

```text
source_xml_file = wf_customer.xml
```

Do not expose sensitive local filesystem information if unnecessary; use the relative path where appropriate.

---

# 31. OUTPUT COLUMNS

At minimum, the final CSV should contain:

```text
source_xml_file
folder_name
workflow_name
task_type
task_name
workflow_parameter_name
workflow_parameter_value
workflow_variables
session_order
session_name
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

Add other useful columns found in the XML.

Do not remove information simply because it was not listed above.

---

# 32. DYNAMIC EXTRACTION

Do not hard-code only:

```text
session_name
mapping_name
source
target
```

The parser should inspect the XML and extract the actual available fields.

For example, if the XML contains:

```text
IsAbort
IsEnabled
FailParentIfTaskFails
RecoveryStrategy
CommitInterval
```

and these are session-level attributes, consider adding them as columns.

The implementation should be designed so new fields can easily be added.

---

# 33. NULL HANDLING

If a field does not exist for a particular task:

```text
null
```

or empty value may be used.

Do not incorrectly copy a value from another session.

Workflow-level values may be repeated for each session row when appropriate.

For example:

```text
workflow_name
folder_name
workflow_variables
```

can be repeated across all session rows belonging to that workflow.

---

# 34. MULTIPLE XML FILES

Process all XML files and combine the results into one CSV.

Example:

```text
workflow1.xml
workflow2.xml
workflow3.xml
```

Output:

```text
informatica_workflow_inventory.csv
```

Every row must retain:

```text
source_xml_file
```

so we know where it came from.

---

# 35. ERROR REPORT

Create a separate processing summary/error report.

Example:

```text
file_name
status
error_message
workflow_count
session_count
```

Example:

```text
workflow1.xml | SUCCESS | | 1 | 15
workflow2.xml | SUCCESS | | 1 | 8
workflow3.xml | ERROR   | Invalid XML | 0 | 0
```

---

# 36. SUMMARY REPORT

After processing all XML files, print:

```text
Total XML files
Successfully processed
Failed files
Total workflows
Total sessions/tasks
Total mappings
Total sources
Total targets
```

Example:

```text
Total XML files       = 100
Successfully processed = 98
Failed                  = 2
Total workflows        = 98
Total sessions/tasks   = 1,250
Total mappings         = 1,100
Total sources          = 1,500
Total targets          = 1,250
```

---

# 37. IMPORTANT — DO NOT GUESS XML TAGS

The biggest requirement is:

**Inspect the actual Informatica XML files before implementing the parser.**

Do not assume that Informatica XML uses generic tags such as:

```text
<Workflow>
<Session>
<Mapping>
<Source>
<Target>
```

without verifying the actual XML.

Informatica exports may contain nested structures, attributes, namespaces, and references.

Build the parser according to the actual XML structure.

---

# 38. VALIDATION OF EXTRACTION

After generating the CSV, perform basic validation.

For every workflow:

```text
workflow_name
```

should have the expected number of sessions/tasks.

For every Session task:

```text
session_name
```

should be populated.

Where available:

```text
mapping_name
source
target
```

should be populated.

Check for suspicious extraction results such as:

```text
session_count = 0
mapping_count = 0
source_count = 0
target_count = 0
```

and report them.

---

# 39. SAMPLE OUTPUT

The final CSV should conceptually look like:

```text
source_xml_file,
folder_name,
workflow_name,
task_type,
task_name,
session_order,
session_name,
mapping_name,
source,
target,
source_file_path,
target_file_path,
session_parameter_file,
session_parameters,
workflow_variables,
predecessor,
successor,
condition
```

Example:

```text
wf_customer.xml,
CUSTOMER,
wf_customer_load,
Session,
s_extract_customer,
1,
s_extract_customer,
m_extract_customer,
SRC_CUSTOMER,
STG_CUSTOMER,
/data/source/customer.csv,
/data/stage/customer.csv,
/config/customer.par,
$FileName=customer.csv,
$$SOURCE_DIR=/data/source,
,
s_transform_customer,
SUCCESS
```

---

# 40. DELIVERABLE

Create a complete, executable Python implementation that:

1. Recursively reads all Informatica `.xml` files.
2. Inspects the actual XML structure.
3. Handles XML namespaces.
4. Extracts folder name.
5. Extracts workflow name.
6. Extracts workflow parameters.
7. Extracts workflow variables.
8. Extracts all workflow tasks.
9. Extracts task type.
10. Extracts session name.
11. Determines session/execution order from dependencies.
12. Extracts predecessor.
13. Extracts successor.
14. Extracts workflow conditions.
15. Extracts mapping name.
16. Extracts all sources.
17. Extracts all targets.
18. Extracts source file paths.
19. Extracts target file paths.
20. Extracts session parameter file.
21. Extracts session parameters.
22. Extracts connection information where available.
23. Preserves cross-task dependencies.
24. Handles multiple sources/targets.
25. Handles non-session tasks.
26. Handles parallel workflow branches.
27. Handles malformed XML without stopping the entire process.
28. Produces one consolidated CSV.
29. Produces a processing/error report.
30. Produces extraction summary statistics.
31. Includes the original XML filename for traceability.
32. Does not expose credentials, passwords, tokens, or secrets.
33. Is modular and easy to extend for additional Informatica XML fields.

The primary output should be:

```text
informatica_workflow_inventory.csv
```

and the processing report should be:

```text
informatica_xml_processing_report.csv
```

Before writing the parser, inspect the actual XML files and adapt the extraction logic to their real structure.
