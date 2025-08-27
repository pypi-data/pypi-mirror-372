# [UPDATE] prompts/graph_extraction_prompt.md
Extract entities (nodes) and their relationships from the following text.
Format the output strictly as a JSON object.
**The entire JSON output MUST be enclosed in a single markdown code block starting with ```json and ending with ```.**

---
**Ontology Schema (You MUST respect this schema for all labels and relationship types):**
{ontology_schema}
---

**User Guidance (Additional instructions):**
{user_guidance}
---

JSON Structure Example:
```json
{{
    "nodes": [
        {{"label": "Person", "properties": {{"name": "John Doe", "title": "Engineer"}}}},
        {{"label": "Company", "properties": {{"name": "Acme Corp", "industry": "Tech"}}}}
    ],
    "relationships": [
        {{"source_node_label": "Person", "source_node_identifying_value": "John Doe",
            "target_node_label": "Company", "target_node_identifying_value": "Acme Corp",
            "type": "WORKS_AT", "properties": {{"role": "Engineer"}}}}
    ]
}}