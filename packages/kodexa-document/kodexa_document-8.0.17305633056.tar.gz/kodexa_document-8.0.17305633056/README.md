# Kodexa Document Python SDK

The Kodexa Document Python SDK provides a powerful framework for working with structured documents in the Kodexa Document Database (KDDB) format. This library enables developers to create, load, manipulate, and query documents with a hierarchical node structure.

## Overview

The Kodexa Document Python SDK is designed to provide a robust document object model with persistence capabilities. At its core is the `Document` class, which represents a document as a hierarchical tree of content nodes. The SDK uses SQLite as its underlying storage mechanism through the KDDB (Kodexa Document Database) format.

Key features include:

- Document creation and manipulation through a hierarchical node structure
- Persistence to and from KDDB files
- Powerful selector language (similar to XPath) for querying document content
- Feature and tag management for document nodes
- Support for document metadata and source tracking

## Installation

```bash
pip install kodexa-document
```

Or using Poetry:

```bash
poetry add kodexa-document
```

## Working with KDDB Files

KDDB (Kodexa Document Database) is the default storage format for Kodexa documents. It provides high-performance storage and the ability to handle very large document objects. KDDB files are SQLite databases with a specific schema designed for efficient document storage and retrieval.

### Reading KDDB Files

To read a document from a KDDB file:

```python
from kodexa_document import Document

# Load a document from a KDDB file
document = Document.from_kddb("path/to/document.kddb")

# Access the document content
root_node = document.get_root()
print(root_node.get_all_content())

# Query the document using selectors
paragraphs = document.select("//paragraph")
for paragraph in paragraphs:
    print(paragraph.content)
```

You can also load a KDDB file from a bytes object:

```python
# Load from bytes
with open("path/to/document.kddb", "rb") as f:
    kddb_bytes = f.read()
    
document = Document.from_kddb(kddb_bytes)
```

The `from_kddb` method accepts the following parameters:

- `source` (str or bytes): Path to a KDDB file or bytes containing KDDB data
- `detached` (bool, optional): Whether to load the document in detached mode (default: True)
- `inmemory` (bool, optional): Whether to load the document in memory for faster processing (default: False)

### Writing KDDB Files

To save a document to a KDDB file:

```python
# Save to a file
document.to_kddb("path/to/output.kddb")

# Or get the KDDB as bytes
kddb_bytes = document.to_kddb()
```

The `to_kddb` method accepts an optional `path` parameter. If provided, the document will be written to the specified file. If not provided, the method will return a bytes object containing the KDDB data.

### In-Memory Processing

For faster processing of documents, you can use the `inmemory` parameter when loading a KDDB file:

```python
# Load document in memory for faster processing
document = Document.from_kddb("path/to/document.kddb", inmemory=True)

# Process the document...

# Save the document back to disk
document.to_kddb("path/to/output.kddb")
```

## Creating Documents

You can create new documents from scratch or from text:

```python
# Create a new empty document
from kodexa_document import Document
document = Document()

# Create a root node
root_node = document.create_node(node_type="document")
document.content_node = root_node

# Add child nodes
paragraph = document.create_node(node_type="paragraph", content="This is a paragraph.")
root_node.add_child(paragraph)

# Create a document from text
text_document = Document.from_text("This is a sample document.")
print(text_document.get_root().content)

# Create a document with separated content
separated_document = Document.from_text("This is a sample document.", separator=" ")
# This creates a document with each word as a separate child node
print(len(separated_document.get_root().get_children()))  # Outputs: 5
```

## Document Structure

A Kodexa document consists of:

- A root content node (`document.content_node` or `document.get_root()`)
- A hierarchical structure of content nodes
- Metadata about the document (`document.metadata`)
- Source information (`document.source`)

Each content node can have:

- Content (text)
- Features (metadata attached to nodes)
- Child nodes
- Tags (special features for marking up content)

## Working with Content Nodes

Content nodes form the hierarchical structure of a document:

```python
# Access the root node
root = document.get_root()

# Get all children
children = root.get_children()

# Access content
content = root.content

# Get all content (including from children)
all_content = root.get_all_content()

# Add a child node
new_node = document.create_node(node_type="paragraph", content="New paragraph")
root.add_child(new_node)
```

## Using Selectors

The SDK provides a powerful selector language (similar to XPath) for querying document content:

```python
# Select all paragraph nodes
paragraphs = document.select("//paragraph")

# Select nodes with specific content
important_nodes = document.select("//paragraph[contains(., 'important')]")

# Select the first matching node
first_table = document.select_first("//table")

# Select nodes with specific features
tagged_nodes = document.select("//*[hasFeature('tag', 'highlight')]")
```

## Working with Features and Tags

Features are metadata attached to content nodes:

```python
# Add a feature to a node
node.add_feature("category", "section", "introduction")

# Check if a node has a feature
if node.has_feature("category", "section"):
    # Do something

# Get feature value
category = node.get_feature_value("category", "section")
```

Tags are special features used for marking up content:

```python
# Tag a node
node.tag("highlight", tag_uuid="unique-id-123")

# Tag content matching a pattern
node.tag("person", content_re="John|Jane")

# Check if a node has tags
if node.has_tags():
    # Do something

# Get all tags on a node
tags = node.get_tags()
```

## Persistence Layer

The SDK uses SQLite as its persistence layer through the `SqliteDocumentPersistence` class. This class handles all database operations for storing and retrieving documents, nodes, and features.

The persistence layer is automatically created when you create a document or load a document from a KDDB file. You can access it through the `get_persistence()` method:

```python
# Access the persistence layer
persistence = document.get_persistence()

# Close the document and clean up resources
document.close()
```

## Converting Between Formats

The SDK supports converting between different formats:

```python
# Convert to/from JSON
json_str = document.to_json()
json_document = Document.from_json(json_str)

# Convert to/from dictionary
doc_dict = document.to_dict()
dict_document = Document.from_dict(doc_dict)

# Convert to/from MessagePack (KDXA format)
msgpack_bytes = document.to_msgpack()
msgpack_document = Document.from_msgpack(msgpack_bytes)

# Save to KDXA file
document.to_kdxa("document.kdxa")

# Load from KDXA file
kdxa_document = Document.from_kdxa("document.kdxa")
```

## Example: Processing a KDDB File

Here's a complete example of loading a KDDB file, processing its content, and saving it back:

```python
from kodexa_document import Document

# Load a document from a KDDB file
document = Document.from_kddb("input.kddb")

# Get the root node
root = document.get_root()

# Select all paragraph nodes
paragraphs = root.select("//paragraph")

# Tag paragraphs containing specific text
for paragraph in paragraphs:
    if "important" in paragraph.get_all_content():
        paragraph.tag("important")

# Add a document-level label
document.add_label("processed")

# Save the modified document
document.to_kddb("output.kddb")

# Clean up resources
document.close()
```

## Advanced Features

### External Data

You can store arbitrary data with a document:

```python
# Store external data
document.set_external_data({"key": "value"})

# Store external data with a specific key
document.set_external_data({"status": "processed"}, "metadata")

# Retrieve external data
data = document.get_external_data()
metadata = document.get_external_data("metadata")

# Get all external data keys
keys = document.get_external_data_keys()
```

### Processing Steps

You can track processing steps applied to a document:

```python
from kodexa_document.model import ProcessingStep

# Create processing steps
step1 = ProcessingStep(name="Extract Text")
step2 = ProcessingStep(name="Tag Entities")

# Add child steps
step1.add_child(step2)

# Set steps on the document
document.set_steps([step1, step2])

# Retrieve steps
steps = document.get_steps()
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
