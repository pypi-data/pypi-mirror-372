# Lazy BigQuery (zbq)

A lightweight, enhanced wrapper around Google Cloud BigQuery and Storage with Polars integration and seamless pandas compatibility. Simplifies querying and data operations with a unified interface, supporting read, write, insert, delete operations on BigQuery tables, and advanced file upload/download with pattern matching, parallel processing, and comprehensive error handling.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [BigQuery Operations](#bigquery-operations)
  - [Storage Operations](#storage-operations)
- [Parameter Substitution & Security](#parameter-substitution--advanced-features)
- [Common Use Cases & Examples](#common-use-cases--practical-examples)
- [Advanced Configuration](#advanced-configuration)
- [Error Handling](#error-handling)
- [Performance Tips](#performance-tips)
- [API Reference](#api-reference)
- [Authentication & Setup](#authentication--setup)

## Key Features

### BigQuery Operations  
- **Secure parameterization** - Native `@param_name` syntax with SQL injection protection
- **Type-safe parameters** - Automatic type detection for strings, numbers, booleans, arrays
- **Dual DataFrame support** - Native Polars with seamless pandas conversion via `.to_pandas()`
- **Dry run mode** - Preview queries with parameters before execution
- **Performance optimized** - Built on Polars for speed, converts to pandas when needed
- **Enterprise ready** - Context managers, timeouts, comprehensive error handling

### Storage Operations  
- **Single file uploads** - Direct file upload with `upload_file()` or enhanced `upload()` auto-detection
- **Advanced pattern matching** - Multiple include/exclude patterns, regex support, case-insensitive
- **Parallel processing** - Configurable thread pools for better performance
- **Progress tracking** - Built-in progress bars with tqdm and custom callbacks
- **Dry-run mode** - Preview operations without executing
- **Retry logic** - Automatic retry with exponential backoff for failed operations
- **Detailed results** - Comprehensive statistics including file counts, bytes transferred, duration, errors

## Installation

```bash
pip install zbq
```

## Get Started in 30 Seconds

```python
from zbq import zclient, zstorage

# 1. Query BigQuery (returns Polars DataFrame)
df = zclient.read("SELECT * FROM `project.dataset.table` LIMIT 10")
print(df)

# 2. Upload a single file to Google Cloud Storage
result = zstorage.upload_file("./data.csv", "my-bucket/folder")
print(f"Uploaded: {result.uploaded_files} files")

# 3. Secure parameterized query
customers = zclient.read(
    "SELECT * FROM customers WHERE region = @region AND active = @active",
    parameters={"region": "US", "active": True}
)

# 4. Write data back to BigQuery
zclient.write(customers, "project.dataset.filtered_customers", write_type="truncate")
```

## Quick Start

### BigQuery Operations

```python
from zbq import zclient

# Check/set project (optional - auto-detected by default)
print(f"Using project: {zclient.project_id}")
# zclient.project_id = "my-project-id"  # Override if needed

# Simple query (returns Polars DataFrame)
df = zclient.read("SELECT * FROM `project.dataset.table` LIMIT 1000")
print(df)

# Convert to pandas DataFrame if needed
pandas_df = zclient.read("SELECT * FROM `project.dataset.table` LIMIT 1000").to_pandas()
print(type(pandas_df))  # <class 'pandas.core.frame.DataFrame'>

# Parameterized query (recommended) - works with both Polars and pandas
df = zclient.read(
    "SELECT * FROM @table_name WHERE region = @region LIMIT @limit",
    parameters={
        "table_name": "project.dataset.table",
        "region": "US", 
        "limit": 1000
    }
)  # Returns Polars DataFrame

# Same query as pandas DataFrame
pandas_df = zclient.read(
    "SELECT * FROM @table_name WHERE region = @region LIMIT @limit",
    parameters={
        "table_name": "project.dataset.table",
        "region": "US", 
        "limit": 1000
    }
).to_pandas()  # Returns pandas DataFrame

# Write DataFrame to BigQuery
result = zclient.write(
    df=df,
    full_table_path="project.dataset.new_table", 
    write_type="truncate",  # or "append"
    warning=True,           # Interactive prompt for truncate operations
    create_if_needed=True,  # Create table if it doesn't exist
    timeout=300            # Custom timeout (optional)
)

# Write operation examples
# Append to existing table (safe, no data loss)
result = zclient.write(df, "project.dataset.table", write_type="append")

# Truncate table (replaces all data - shows warning prompt)
result = zclient.write(
    df, 
    "project.dataset.table", 
    write_type="truncate",
    warning=True  # Prompts: "You are about to overwrite a table. Continue? (y/n)"
)

# Truncate without warning (programmatic use)
result = zclient.write(
    df, 
    "project.dataset.table", 
    write_type="truncate",
    warning=False  # No interactive prompt
)

# Create table if it doesn't exist
result = zclient.write(
    df,
    "project.dataset.new_table",
    create_if_needed=True   # Creates table with DataFrame schema
)

# Fail if table doesn't exist (strict mode)
result = zclient.write(
    df,
    "project.dataset.existing_table", 
    create_if_needed=False  # Raises error if table doesn't exist
)

# CRUD operations with parameters
zclient.insert(
    "INSERT INTO @table_name (col1, col2) VALUES (@val1, @val2)",
    parameters={"table_name": "project.dataset.table", "val1": "data", "val2": 123}
)
zclient.update(
    "UPDATE @table_name SET col = @new_value WHERE id = @target_id",
    parameters={"table_name": "project.dataset.table", "new_value": "updated", "target_id": 1}
)
zclient.delete(
    "DELETE FROM @table_name WHERE id IN (@ids)",
    parameters={"table_name": "project.dataset.table", "ids": [1, 2, 3]}
)

# Context manager support - automatic cleanup
with zclient as client:
    # Test query with dry_run first
    client.read(
        "SELECT * FROM @table WHERE date >= @start_date",
        parameters={"table": "project.dataset.table1", "start_date": "2024-01-01"},
        dry_run=True
    )
    
    # Execute actual queries
    df1 = client.read(
        "SELECT * FROM @table WHERE date >= @start_date",
        parameters={"table": "project.dataset.table1", "start_date": "2024-01-01"}
    )
    df2 = client.read("SELECT * FROM table2") 
    result = client.write(df1, "project.dataset.output_table")
# Client automatically cleaned up after context
```

### Parameter Substitution & Advanced Features

#### Secure Parameter Handling
zbq uses BigQuery's native parameterized queries for complete SQL injection protection:

```python
from zbq import zclient

# Basic secure parameterization
df = zclient.read(
    """SELECT * FROM `project.dataset.table` 
    WHERE region = @region AND status = @status""",
    parameters={
        "region": "US",           # Securely parameterized as STRING
        "status": "active"        # Securely parameterized as STRING  
    }
)

# Multiple data types with automatic type detection
df = zclient.read(
    """SELECT * FROM hotels 
    WHERE hotel_id = @id 
    AND price > @min_price 
    AND is_available = @available
    AND last_updated > @date""",
    parameters={
        "id": 123,                    # BigQuery INT64 parameter
        "min_price": 99.99,          # BigQuery FLOAT64 parameter
        "available": True,            # BigQuery BOOL parameter
        "date": None                 # BigQuery STRING parameter (NULL)
    }
)

# Table identifiers (handled separately for security)
df = zclient.read(
    "SELECT * FROM @table WHERE region = @region",
    parameters={
        "table": "project.dataset.hotels",  # Validated and backtick-quoted
        "region": "US"                      # Securely parameterized
    }
)
```

#### Array Parameters for Lists and IN Clauses
Use BigQuery's native ArrayQueryParameter for secure list handling:

```python
# IN clause with string array
df = zclient.read(
    "SELECT * FROM hotels WHERE hotel_code IN UNNEST(@codes)",
    parameters={
        "codes": ['ABC', 'DEF', 'GHI']  # BigQuery ARRAY<STRING> parameter
    }
)

# Numeric array for IN clauses
df = zclient.read(
    "SELECT * FROM bookings WHERE booking_id IN UNNEST(@ids)", 
    parameters={
        "ids": [123, 456, 789]  # BigQuery ARRAY<INT64> parameter
    }
)

# Boolean arrays
df = zclient.read(
    "SELECT * FROM table WHERE flag IN UNNEST(@flags)",
    parameters={
        "flags": [True, False, True]  # BigQuery ARRAY<BOOL> parameter
    }
)

# Empty arrays (handled safely)
df = zclient.read(
    "SELECT * FROM table WHERE id IN UNNEST(@empty_ids)",
    parameters={
        "empty_ids": []  # BigQuery ARRAY<STRING> parameter (empty)
    }
)
```

#### Security Features
zbq provides complete protection against SQL injection attacks:

```python
# All user inputs are safely parameterized
user_input = "'; DROP TABLE users; --"  # Malicious input
df = zclient.read(
    "SELECT * FROM users WHERE name = @user_name",
    parameters={
        "user_name": user_input  # Safely handled as STRING parameter
    }
)
# The malicious input is treated as a literal string value, not SQL code

# Table identifiers are validated separately
safe_table = "project.dataset.users"
df = zclient.read(
    "SELECT * FROM @table WHERE active = @status",
    parameters={
        "table": safe_table,    # Validated and safely quoted
        "status": True          # Securely parameterized as BOOL
    }
)
```

#### Dry Run Mode
Preview your final query with secure parameters before execution:

```python
# Preview query with dry_run
result = zclient.read(
    """SELECT * FROM @table
    WHERE region = @region 
    AND hotel_codes IN UNNEST(@codes)
    AND rating >= @min_rating""",
    parameters={
        "table": "project.dataset.hotels",
        "region": "US",
        "codes": ['ABC', 'DEF'], 
        "min_rating": 4
    },
    dry_run=True  # Shows query and parameters, returns None
)

# Output:
# DRY RUN - Query that would be executed:
# --------------------------------------------------
# Query: SELECT * FROM `project.dataset.hotels`
# WHERE region = @region 
# AND hotel_codes IN UNNEST(@codes)
# AND rating >= @min_rating
# Parameters:
#   @region (STRING): US
#   @codes (STRING): ['ABC', 'DEF']
#   @min_rating (INT64): 4
# --------------------------------------------------
```

### Pandas Integration
While zbq uses Polars internally for optimal performance, you can easily work with pandas DataFrames:

```python
import pandas as pd
from zbq import zclient

# Get pandas DataFrame directly
df = zclient.read("SELECT * FROM `project.dataset.table`").to_pandas()
print(type(df))  # <class 'pandas.core.frame.DataFrame'>

# Works with all zbq features
pandas_df = zclient.read(
    """SELECT * FROM hotels 
    WHERE region = @region 
    AND hotel_codes IN (@codes)
    @condition""",
    parameters={
        "region": "US",
        "codes": ['ABC', 'DEF'], 
        "condition": "AND rating >= 4"
    }
).to_pandas()

# Dry run also works with pandas conversion
result = zclient.read(
    "SELECT * FROM @table WHERE status = @status",
    parameters={"table": "project.dataset.bookings", "status": "confirmed"},
    dry_run=True
)  # Returns None (dry run), but would convert to pandas when executed

# Mixed workflows - leverage both libraries' strengths
polars_df = zclient.read("SELECT * FROM large_table")  # Fast Polars processing

# Use Polars for heavy data transformation
processed_df = polars_df.filter(pl.col("amount") > 1000).group_by("category").sum()

# Convert to pandas for specific analysis or visualization
pandas_df = processed_df.to_pandas()

# Use pandas for plotting, ML libraries, etc.
import matplotlib.pyplot as plt
pandas_df.plot(kind='bar')
plt.show()

# Write back to BigQuery (accepts both Polars and pandas)
zclient.write(pandas_df, "project.dataset.analysis_results")  # Polars handles conversion internally
```

#### Why This Approach Works Well
- **Performance**: Polars handles the heavy lifting (SQL execution, data processing)
- **Compatibility**: Convert to pandas only when needed for specific libraries
- **Flexibility**: Use the best tool for each step in your workflow
- **Memory efficiency**: Polars' lazy evaluation optimizes the query execution

### Timeout Configuration
Control query execution timeouts for long-running operations:

```python
from zbq import zclient, BigQueryHandler

# Using default timeout (300 seconds / 5 minutes)
df = zclient.read("SELECT * FROM large_table")

# Custom timeout for specific query (10 minutes)
df = zclient.read(
    "SELECT * FROM very_large_table WHERE complex_calculation = @param",
    parameters={"param": "value"},
    timeout=600  # 10 minutes
)

# Set default timeout for all operations in a session
custom_client = BigQueryHandler(
    project_id="my-project",
    default_timeout=1200  # 20 minutes default
)

# All operations with this client use 20-minute timeout
df = custom_client.read("SELECT * FROM massive_dataset")

# Override default with specific timeout
df = custom_client.read("SELECT * FROM quick_query", timeout=30)  # 30 seconds

# Timeout works with all operations
custom_client.insert(
    "INSERT INTO @table VALUES (@val1, @val2)",
    parameters={"table": "my_table", "val1": "data", "val2": 123},
    timeout=300
)

# Handle timeout errors
try:
    df = zclient.read("SELECT * FROM enormous_table", timeout=60)
except TimeoutError as e:
    print(f"Query timed out: {e}")
    # Maybe try with longer timeout or different approach
```

### Storage Operations

#### Single File Upload/Download
```python
from zbq import zstorage

# Upload a single file directly (NEW!)
result = zstorage.upload_file(
    local_file_path="./report.xlsx",
    bucket_path="my-bucket",                # Uploads to bucket root as "report.xlsx"
)

# Upload single file to specific folder with custom name
result = zstorage.upload_file(
    local_file_path="./data/sales_2024.xlsx",
    bucket_path="my-bucket/reports/2024",   # Uploads to "reports/2024/" folder
    blob_name="january_sales.xlsx"          # Custom name in bucket
)

# Enhanced upload() method now handles both files AND directories
result = zstorage.upload(
    local_dir="./report.xlsx",              # File path (not directory)
    bucket_path="my-bucket/reports"         # Automatically detects it's a file
)
print(f"Single file upload: {result.uploaded_files} file, {result.total_bytes:,} bytes")

# Upload single file with error handling
try:
    result = zstorage.upload_file("./important_data.csv", "my-bucket/data")
    if result.uploaded_files == 1:
        print("File uploaded successfully!")
    else:
        print(f"Upload failed: {result.errors}")
except Exception as e:
    print(f"Upload error: {e}")
```

#### Basic Directory Upload/Download
```python
from zbq import zstorage

# Simple directory upload with pattern - files go to bucket root
result = zstorage.upload(
    local_dir="./data",
    bucket_path="my-bucket",
    include_patterns="*.xlsx"  # Upload only Excel files
)

# Upload to specific folder in bucket
result = zstorage.upload(
    local_dir="./data", 
    bucket_path="my-bucket/reports/2024",  # Upload to reports/2024/ folder
    include_patterns="*.xlsx"
)

print(f"Uploaded {result.uploaded_files}/{result.total_files} files")
print(f"Total size: {result.total_bytes:,} bytes in {result.duration:.2f}s")

# Context manager support for batch operations
with zstorage as storage:
    # Mix single file and directory uploads
    result1 = storage.upload_file("./summary.pdf", "my-bucket/reports")
    result2 = storage.upload("./data1", "my-bucket/folder1", include_patterns="*.csv")
    result3 = storage.upload("./data2", "my-bucket/folder2", include_patterns="*.json")
    result4 = storage.download("my-bucket/archive", "./downloads", include_patterns="*.parquet")
# Storage client automatically cleaned up

# Simple download from bucket root
result = zstorage.download(
    bucket_path="my-bucket", 
    local_dir="./downloads",
    include_patterns="*.csv"  # Download only CSV files
)

# Download from specific folder in bucket
result = zstorage.download(
    bucket_path="my-bucket/data/exports",  # Download from data/exports/ folder
    local_dir="./downloads",
    include_patterns="*.csv"
)
```

#### Advanced Pattern Matching
```python
# Multiple include patterns
result = zstorage.upload(
    local_dir="./reports",
    bucket_path="my-bucket/reports", 
    include_patterns=["*.xlsx", "*.csv", "*.json"],  # Multiple file types
    exclude_patterns=["temp_*", "*_backup.*"],       # Exclude temporary/backup files
    case_sensitive=False  # Case-insensitive matching
)

# Regex patterns for complex matching
result = zstorage.upload(
    local_dir="./logs",
    bucket_path="my-bucket/logs",
    include_patterns=r"log_\d{4}-\d{2}-\d{2}\.txt",  # Match log_YYYY-MM-DD.txt
    use_regex=True
)
```

#### Parallel Processing & Progress Tracking
```python
# Automatic progress bar (shows for multiple files)
result = zstorage.upload(
    local_dir="./large-dataset", 
    bucket_path="my-bucket",
    include_patterns="*.xlsx",
    parallel=True,                    # Enable parallel uploads
    max_retries=5                     # Retry failed uploads
)
# Shows: "Uploading: 75%|███████▌  | 15/20 [00:30<00:10, 0.5files/s]"

# Custom progress callback (optional)
def progress_callback(completed, total):
    percentage = (completed / total) * 100
    print(f"Custom progress: {completed}/{total} files ({percentage:.1f}%)")

result = zstorage.upload(
    local_dir="./large-dataset", 
    bucket_path="my-bucket",
    progress_callback=progress_callback,
    show_progress=False               # Disable built-in progress bar
)

# Handle results
if result.failed_files > 0:
    print(f"WARNING: {result.failed_files} files failed to upload:")
    for error in result.errors:
        print(f"  - {error}")

print(f"Successfully uploaded {result.uploaded_files} files")
print(f"Total: {result.total_bytes:,} bytes in {result.duration:.2f}s")
```

#### Dry Run & Preview
```python
# Preview what would be uploaded without actually uploading
result = zstorage.upload(
    local_dir="./data",
    bucket_path="my-bucket", 
    include_patterns="*.parquet",
    dry_run=True  # Preview only
)

print(f"Would upload {result.total_files} files ({result.total_bytes:,} bytes)")

# Progress bar control
result = zstorage.upload(
    local_dir="./data",
    bucket_path="my-bucket",
    include_patterns="*.xlsx", 
    show_progress=True     # Force show progress bar even for single files
)

result = zstorage.upload(
    local_dir="./data",
    bucket_path="my-bucket", 
    include_patterns="*.xlsx",
    show_progress=False    # Never show progress bar
)
```

#### Advanced Download with Filtering
```python  
# Download with path filtering and patterns
result = zstorage.download(
    bucket_path="my-data-bucket/reports/2024",  # Only files under this path
    local_dir="./downloaded-reports", 
    include_patterns=["*.xlsx", "*.pdf"],
    exclude_patterns="*_draft.*",     # Skip draft files
    parallel=True,
    max_results=500                   # Limit number of files to list
)
```

## Advanced Configuration

### Project Configuration
zbq automatically detects your Google Cloud project but also provides flexible project management:

```python
from zbq import zclient, zstorage

# Check current project (auto-detected)
print(f"Current project: {zclient.project_id}")

# Manual project override
zclient.project_id = "my-specific-project"
zstorage.project_id = "my-storage-project"  # Can be different

# Verify the change
print(f"BigQuery project: {zclient.project_id}")
print(f"Storage project: {zstorage.project_id}")

# Project-specific operations
df = zclient.read("SELECT * FROM dataset.table")  # Uses my-specific-project
```

#### Project Detection Order
zbq uses the following order to determine your project ID:

1. **Manual setting**: `zclient.project_id = "project"`
2. **Constructor parameter**: `BigQueryHandler(project_id="project")`
3. **gcloud config**: From `gcloud config get-value project`
4. **Environment variable**: `GOOGLE_CLOUD_PROJECT`

```python
# Different ways to set project
from zbq import BigQueryHandler, StorageHandler

# Method 1: Constructor (recommended for apps)
bq = BigQueryHandler(project_id="my-project")

# Method 2: Property setter (good for interactive use)
bq = BigQueryHandler()  # Auto-detects project
bq.project_id = "different-project"  # Override if needed

# Method 3: Environment variable
import os
os.environ["GOOGLE_CLOUD_PROJECT"] = "env-project"
bq = BigQueryHandler()  # Uses env-project

# Method 4: gcloud config (system default)
# Run: gcloud config set project my-default-project
bq = BigQueryHandler()  # Uses my-default-project
```

#### Multi-Project Workflows
```python
# Work with multiple projects simultaneously
prod_client = BigQueryHandler(project_id="prod-project")
dev_client = BigQueryHandler(project_id="dev-project")

# Different data sources
prod_df = prod_client.read("SELECT * FROM prod_dataset.table")
dev_df = dev_client.read("SELECT * FROM dev_dataset.table")

# Cross-project operations
result = prod_client.write(dev_df, "prod_dataset.migrated_table")
```

### Custom Logging
```python
from zbq import setup_logging, StorageHandler, BigQueryHandler

# Configure logging
logger = setup_logging("DEBUG")  # DEBUG, INFO, WARNING, ERROR

# Create handlers with custom settings
storage = StorageHandler(
    project_id="my-project",
    log_level="INFO", 
    max_workers=8  # More parallel workers
)

bq = BigQueryHandler(
    project_id="my-project",
    default_timeout=600,  # 10 minute timeout
    log_level="DEBUG"
)
```

### Error Handling
```python
from zbq import ZbqAuthenticationError, ZbqOperationError, ZbqConfigurationError

# BigQuery error handling
try:
    df = zclient.read(
        "SELECT * FROM @table WHERE column = @value",
        parameters={"table": "project.dataset.table", "value": "test"}
    )
except ZbqAuthenticationError:
    print("Authentication failed. Run: gcloud auth application-default login")
except ZbqConfigurationError:
    print("Configuration error. Check your project settings.")
except ZbqOperationError as e:
    print(f"BigQuery operation failed: {e}")
except TimeoutError as e:
    print(f"Query timed out: {e}")
    print("Consider increasing timeout or optimizing the query")

# Parameter validation errors
try:
    df = zclient.read(
        "SELECT * FROM table WHERE id = @user_id",
        parameters={}  # Missing required parameter
    )
except ZbqOperationError as e:
    if "Missing values for parameters" in str(e):
        print(f"Parameter error: {e}")
        # Handle missing parameters
    else:
        print(f"Other operation error: {e}")

# Write operation errors
try:
    zclient.write(
        empty_df, 
        "project.dataset.table",
        write_type="truncate"
    )
except ValueError as e:
    if "Missing required argument" in str(e):
        print("DataFrame is empty or table path is missing")
    else:
        print(f"Write validation error: {e}")
except ZbqOperationError as e:
    print(f"Write operation failed: {e}")

# Storage operations error handling
try:
    result = zstorage.upload("./data", "my-bucket", include_patterns="*.csv")
except ZbqAuthenticationError:
    print("Authentication failed. Run: gcloud auth application-default login")
except ZbqConfigurationError:
    print("Configuration error. Check your project settings.")
except ZbqOperationError as e:
    print(f"Storage operation failed: {e}")

# Comprehensive error handling for production use
def safe_bigquery_operation():
    try:
        # Your BigQuery operations here
        df = zclient.read("SELECT * FROM large_table", timeout=300)
        return df
    
    except ZbqAuthenticationError:
        print("Authentication Error")
        print("Run: gcloud auth application-default login")
        return None
        
    except ZbqConfigurationError as e:
        print("Configuration Error")
        print(f"Check project settings: {e}")
        return None
        
    except TimeoutError:
        print("Query Timeout")
        print("Try increasing timeout or optimizing query")
        return None
        
    except ZbqOperationError as e:
        print("BigQuery Operation Error") 
        print(f"Details: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return None
```

### Working with Results
```python
from zbq import UploadResult, DownloadResult

# Upload with detailed result handling
result: UploadResult = zstorage.upload(
    local_dir="./data",
    bucket_name="my-bucket",
    include_patterns=["*.json", "*.csv"]
)

# Detailed statistics
print(f"""
Upload Summary:
Total files: {result.total_files}
Uploaded: {result.uploaded_files} 
Skipped: {result.skipped_files}
Failed: {result.failed_files}
Total size: {result.total_bytes:,} bytes
Duration: {result.duration:.2f} seconds
""")

# Handle errors
if result.errors:
    print("Errors encountered:")
    for error in result.errors[:5]:  # Show first 5 errors
        print(f"  - {error}")
    if len(result.errors) > 5:
        print(f"  ... and {len(result.errors) - 5} more errors")
```

## Pattern Matching Guide

### Glob Patterns (Default)
- `*.xlsx` - All Excel files
- `data_*.csv` - CSV files starting with "data_" 
- `report_????_??.pdf` - Reports with specific naming pattern
- `**/*.json` - All JSON files in subdirectories (recursive)
- `[!.]*.txt` - Text files not starting with dot

### Regex Patterns
```python
# Enable regex with use_regex=True
zstorage.upload(
    local_dir="./logs",
    bucket_name="my-bucket", 
    include_patterns=[
        r"access_log_\d{4}-\d{2}-\d{2}\.log",  # access_log_2024-01-01.log
        r"error_log_\d{8}\.log"                # error_log_20240101.log  
    ],
    use_regex=True
)
```

### Complex Filtering
```python
# Include multiple types, exclude temp files
zstorage.upload(
    local_dir="./workspace",
    bucket_name="my-bucket",
    include_patterns=["*.py", "*.json", "*.md", "*.yml"],
    exclude_patterns=["__pycache__/*", "*.pyc", "temp_*", ".git/*"],
    case_sensitive=False
)
```

## Authentication & Setup

1. **Install Google Cloud SDK**:
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Or set environment variables**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json" 
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   ```

## Requirements

- Python ≥ 3.11
- Google Cloud project with BigQuery and/or Storage APIs enabled
- Appropriate IAM permissions for your operations


## Performance Tips

### BigQuery Operations
1. **Use parameterized queries** for better performance and security:
   ```python
   # Good: Parameters are processed efficiently
   df = zclient.read("SELECT * FROM table WHERE id = @id", parameters={"id": 123})
   
   # Avoid: String concatenation
   df = zclient.read(f"SELECT * FROM table WHERE id = {user_id}")
   ```

2. **Set appropriate timeouts** for query complexity:
   ```python
   # Quick queries: shorter timeout
   df = zclient.read("SELECT COUNT(*) FROM table", timeout=30)
   
   # Complex analytics: longer timeout
   df = zclient.read("SELECT * FROM huge_table", timeout=1800)  # 30 minutes
   ```

3. **Optimize DataFrame conversions**:
   ```python
   # Efficient: Convert only when needed
   polars_df = zclient.read("SELECT * FROM table")
   processed_df = polars_df.filter(pl.col("amount") > 1000)  # Fast Polars operations
   pandas_df = processed_df.to_pandas()  # Convert at the end
   
   # Less efficient: Convert immediately
   pandas_df = zclient.read("SELECT * FROM table").to_pandas()
   # Now all operations use slower pandas
   ```

4. **Use dry_run for query optimization**:
   ```python
   # Preview complex queries before execution
   zclient.read(complex_query, parameters=params, dry_run=True)
   # Review the generated SQL for optimization opportunities
   ```

5. **Batch operations efficiently**:
   ```python
   # Good: Single client for multiple operations
   with zclient as client:
       df1 = client.read("SELECT * FROM table1")
       df2 = client.read("SELECT * FROM table2")
       client.write(result_df, "output_table")
   
   # Avoid: Creating new clients repeatedly
   ```

6. **Memory management for large datasets**:
   ```python
   # Process large datasets in chunks
   for i in range(0, total_records, chunk_size):
       chunk_df = zclient.read(
           "SELECT * FROM table LIMIT @limit OFFSET @offset",
           parameters={"limit": chunk_size, "offset": i}
       )
       # Process chunk...
   ```

### Storage Operations
1. **Use parallel processing** for multiple files: `parallel=True`
2. **Adjust thread count** based on your system: `max_workers=8`
3. **Use dry-run** to preview large operations first
4. **Filter early** with specific patterns to avoid processing unwanted files
5. **Monitor progress** with callback functions for long operations
6. **Use `upload_file()` for single files** instead of directory patterns when possible

## API Reference

### BigQuery Methods

#### `zclient.read(query, timeout=None, parameters=None, dry_run=False)`
Execute a SELECT query and return results as a Polars DataFrame.
- **query** (str): SQL query with optional `@param_name` placeholders
- **timeout** (int, optional): Query timeout in seconds (default: 300)  
- **parameters** (dict, optional): Parameter values for `@param_name` substitution
- **dry_run** (bool, optional): Print query without executing (default: False)
- **Returns**: `pl.DataFrame` or `None` if dry_run=True

#### `zclient.insert/update/delete(query, timeout=None, parameters=None, dry_run=False)`
Execute INSERT, UPDATE, or DELETE operations.
- Same parameters as `read()`
- **Returns**: `pl.DataFrame` with status information

#### `zclient.write(df, full_table_path, write_type="append", warning=True, create_if_needed=True, timeout=None)`
Write DataFrame to BigQuery table.
- **df** (`pl.DataFrame` or `pd.DataFrame`): Data to write
- **full_table_path** (str): Complete table path "project.dataset.table"
- **write_type** (str): "append" or "truncate" (default: "append")
- **warning** (bool): Show interactive prompt for truncate operations (default: True)
- **create_if_needed** (bool): Create table if it doesn't exist (default: True)
- **timeout** (int, optional): Operation timeout in seconds
- **Returns**: Operation status

### Parameter Types Support
- **Strings**: BigQuery `STRING` parameters (automatically quoted and escaped)
- **Integers**: BigQuery `INT64` parameters  
- **Floats**: BigQuery `FLOAT64` parameters
- **Booleans**: BigQuery `BOOL` parameters
- **None**: BigQuery `STRING` parameters with NULL value
- **Lists/Tuples**: BigQuery `ARRAY<type>` parameters (use with UNNEST())
- **Timestamps**: BigQuery `TIMESTAMP` parameters (datetime objects)
- **Table identifiers**: Separately validated and backtick-quoted (not parameterized)

## Common Use Cases & Practical Examples

### Data Pipeline: File Processing
```python
from zbq import zclient, zstorage
import polars as pl

# Complete data pipeline example
def process_daily_files(date_str):
    """Process daily CSV files and load to BigQuery"""
    
    # 1. Upload today's files to staging
    upload_result = zstorage.upload(
        local_dir=f"./data/{date_str}",
        bucket_path="my-bucket/staging",
        include_patterns="*.csv"
    )
    
    print(f"Uploaded {upload_result.uploaded_files} files for {date_str}")
    
    # 2. Process and validate the data
    df = zclient.read(f"""
        SELECT 
            customer_id,
            order_date,
            amount,
            status
        FROM temp_external_table
        WHERE order_date = @date
        AND amount > 0
    """, parameters={"date": date_str})
    
    # 3. Data quality checks with Polars
    invalid_orders = df.filter(pl.col("customer_id").is_null()).height
    if invalid_orders > 0:
        print(f"Warning: {invalid_orders} orders with missing customer_id")
    
    # 4. Load clean data to production table
    clean_df = df.filter(pl.col("customer_id").is_not_null())
    
    result = zclient.write(
        df=clean_df,
        full_table_path="prod.orders.daily_orders",
        write_type="append",
        create_if_needed=True
    )
    
    print(f"Loaded {len(clean_df)} orders to BigQuery")
    
    return len(clean_df)

# Run pipeline
orders_processed = process_daily_files("2024-01-15")
```

### Backup & Restore Operations
```python
from zbq import zclient, zstorage
from datetime import datetime

def backup_table_to_storage(table_path, backup_bucket):
    """Export BigQuery table to Cloud Storage"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export table data
    df = zclient.read(f"SELECT * FROM {table_path}")
    
    # Save locally first
    local_file = f"./backup_{timestamp}.parquet"
    df.write_parquet(local_file)
    
    # Upload to storage
    result = zstorage.upload_file(
        local_file_path=local_file,
        bucket_path=f"{backup_bucket}/backups",
        blob_name=f"{table_path.replace('.', '_')}_{timestamp}.parquet"
    )
    
    if result.uploaded_files == 1:
        print(f"Table {table_path} backed up successfully")
        # Clean up local file
        import os
        os.remove(local_file)
    else:
        print(f"Backup failed: {result.errors}")
    
    return result

def restore_table_from_backup(backup_file, target_table):
    """Restore table from backup file"""
    
    # Download backup file
    zstorage.download(
        bucket_path=f"my-bucket/backups/{backup_file}",
        local_dir="./restore",
        include_patterns=backup_file
    )
    
    # Load and restore
    df = pl.read_parquet(f"./restore/{backup_file}")
    
    result = zclient.write(
        df=df,
        full_table_path=target_table,
        write_type="truncate",
        warning=False  # Skip warning for restore operations
    )
    
    print(f"Restored {len(df)} records to {target_table}")

# Usage
backup_result = backup_table_to_storage("prod.sales.transactions", "backup-bucket")
# restore_table_from_backup("prod_sales_transactions_20240115_143022.parquet", "dev.sales.transactions")
```

### Report Generation & Distribution
```python
from zbq import zclient, zstorage
import polars as pl

def generate_monthly_report(year, month):
    """Generate monthly sales report and distribute"""
    
    # Generate comprehensive report data
    report_df = zclient.read("""
        SELECT 
            region,
            product_category,
            SUM(revenue) as total_revenue,
            COUNT(DISTINCT customer_id) as unique_customers,
            AVG(order_value) as avg_order_value,
            COUNT(*) as total_orders
        FROM sales_data 
        WHERE EXTRACT(YEAR FROM order_date) = @year 
        AND EXTRACT(MONTH FROM order_date) = @month
        GROUP BY region, product_category
        ORDER BY total_revenue DESC
    """, parameters={"year": year, "month": month})
    
    # Save report in multiple formats
    report_name = f"monthly_report_{year}_{month:02d}"
    
    # Save as Excel for business users
    pandas_df = report_df.to_pandas()
    excel_file = f"./reports/{report_name}.xlsx"
    pandas_df.to_excel(excel_file, index=False)
    
    # Save as Parquet for analysts
    parquet_file = f"./reports/{report_name}.parquet"
    report_df.write_parquet(parquet_file)
    
    # Upload both formats to shared storage
    excel_result = zstorage.upload_file(
        local_file_path=excel_file,
        bucket_path="company-reports/monthly",
        blob_name=f"{report_name}.xlsx"
    )
    
    parquet_result = zstorage.upload_file(
        local_file_path=parquet_file,
        bucket_path="company-reports/monthly", 
        blob_name=f"{report_name}.parquet"
    )
    
    # Store report metadata in BigQuery
    metadata_df = pl.DataFrame({
        "report_name": [report_name],
        "report_date": [f"{year}-{month:02d}-01"],
        "total_revenue": [report_df.select(pl.sum("total_revenue")).item()],
        "total_customers": [report_df.select(pl.sum("unique_customers")).item()],
        "generated_at": [datetime.now()],
        "excel_uploaded": [excel_result.uploaded_files == 1],
        "parquet_uploaded": [parquet_result.uploaded_files == 1]
    })
    
    zclient.write(
        df=metadata_df,
        full_table_path="analytics.reports.monthly_metadata", 
        write_type="append"
    )
    
    print(f"Generated report for {year}-{month:02d}")
    print(f"Excel: {'Success' if excel_result.uploaded_files == 1 else 'Failed'}")
    print(f"Parquet: {'Success' if parquet_result.uploaded_files == 1 else 'Failed'}")
    
    return report_df

# Generate reports for Q1 2024
for month in [1, 2, 3]:
    generate_monthly_report(2024, month)
```

### Data Quality Monitoring
```python
from zbq import zclient
import polars as pl

def monitor_data_quality(table_name):
    """Comprehensive data quality monitoring"""
    
    # Run multiple quality checks in parallel
    quality_checks = {}
    
    # 1. Basic statistics
    stats_df = zclient.read(f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT customer_id) as unique_customers,
            MIN(order_date) as earliest_date,
            MAX(order_date) as latest_date,
            AVG(order_value) as avg_order_value,
            STDDEV(order_value) as stddev_order_value
        FROM {table_name}
        WHERE DATE(order_date) = CURRENT_DATE()
    """)
    
    # 2. Data completeness
    completeness_df = zclient.read(f"""
        SELECT 
            'customer_id' as column_name,
            COUNTIF(customer_id IS NULL) as null_count,
            COUNT(*) as total_count,
            ROUND(COUNTIF(customer_id IS NOT NULL) / COUNT(*) * 100, 2) as completeness_pct
        FROM {table_name}
        WHERE DATE(order_date) = CURRENT_DATE()
        
        UNION ALL
        
        SELECT 
            'order_value' as column_name,
            COUNTIF(order_value IS NULL) as null_count,
            COUNT(*) as total_count,
            ROUND(COUNTIF(order_value IS NOT NULL) / COUNT(*) * 100, 2) as completeness_pct
        FROM {table_name}
        WHERE DATE(order_date) = CURRENT_DATE()
    """)
    
    # 3. Anomaly detection
    anomalies_df = zclient.read(f"""
        SELECT 
            customer_id,
            order_value,
            order_date,
            'high_value' as anomaly_type
        FROM {table_name}
        WHERE DATE(order_date) = CURRENT_DATE()
        AND order_value > (
            SELECT AVG(order_value) + 3 * STDDEV(order_value) 
            FROM {table_name}
            WHERE DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        )
        
        UNION ALL
        
        SELECT 
            customer_id,
            order_value,
            order_date,
            'negative_value' as anomaly_type
        FROM {table_name}
        WHERE DATE(order_date) = CURRENT_DATE()
        AND order_value < 0
    """)
    
    # Process results
    total_rows = stats_df.item(0, "total_rows")
    avg_completeness = completeness_df.select(pl.mean("completeness_pct")).item()
    anomaly_count = len(anomalies_df)
    
    # Quality score calculation
    quality_score = min(100, avg_completeness - (anomaly_count / total_rows * 100))
    
    # Store monitoring results
    monitoring_df = pl.DataFrame({
        "check_date": [datetime.now().date()],
        "table_name": [table_name],
        "total_rows": [total_rows],
        "avg_completeness": [avg_completeness],
        "anomaly_count": [anomaly_count],
        "quality_score": [quality_score],
        "passed": [quality_score >= 95]
    })
    
    zclient.write(
        df=monitoring_df,
        full_table_path="monitoring.data_quality.daily_checks",
        write_type="append"
    )
    
    # Alert if quality issues
    if quality_score < 95:
        print(f"Data quality alert for {table_name}")
        print(f"   Quality score: {quality_score:.1f}%")
        print(f"   Anomalies found: {anomaly_count}")
        print(f"   Avg completeness: {avg_completeness:.1f}%")
    else:
        print(f"Data quality check passed for {table_name}")
    
    return {
        "quality_score": quality_score,
        "total_rows": total_rows,
        "anomalies": anomaly_count
    }

# Monitor key tables
results = monitor_data_quality("prod.orders.daily_transactions")
```

### Storage Methods

#### `zstorage.upload_file(local_file_path, bucket_path, blob_name=None, max_retries=3)`
Upload a single file to Google Cloud Storage.
- **local_file_path** (str | Path): Path to the local file to upload
- **bucket_path** (str): GCS bucket path (e.g., "my-bucket" or "my-bucket/folder/")
- **blob_name** (str, optional): Custom name for the blob (defaults to filename)
- **max_retries** (int): Number of retry attempts for failed upload (default: 3)
- **Returns**: `UploadResult` with detailed statistics

#### `zstorage.upload(local_dir, bucket_path, include_patterns=None, exclude_patterns=None, **kwargs)`
Upload files or a single file to Google Cloud Storage with pattern matching.
- **local_dir** (str | Path): Local directory OR single file path to upload
- **bucket_path** (str): GCS bucket path
- **include_patterns** (str | List[str], optional): Patterns to include (ignored for single files)
- **exclude_patterns** (str | List[str], optional): Patterns to exclude (ignored for single files)
- **case_sensitive** (bool): Whether pattern matching is case sensitive (default: True)
- **use_regex** (bool): Use regex patterns instead of glob patterns (default: False)
- **dry_run** (bool): Preview operation without executing (default: False)
- **parallel** (bool): Use parallel uploads for multiple files (default: True)
- **max_retries** (int): Number of retry attempts (default: 3)
- **Returns**: `UploadResult` with detailed statistics

#### `zstorage.download(bucket_path, local_dir, include_patterns=None, **kwargs)`
Download files from Google Cloud Storage with pattern matching.
- **bucket_path** (str): GCS bucket path to download from
- **local_dir** (str): Local directory to download files to
- **include_patterns** (str | List[str], optional): Patterns to include
- **exclude_patterns** (str | List[str], optional): Patterns to exclude
- **parallel** (bool): Use parallel downloads (default: True)
- **max_results** (int): Maximum number of blobs to list (default: 1000)
- **Returns**: `DownloadResult` with detailed statistics

### Constructor Options

#### `BigQueryHandler(project_id="", default_timeout=300, log_level="INFO")`
Create a custom BigQuery client.
- **project_id** (str, optional): GCP project ID (auto-detected if empty)
- **default_timeout** (int): Default timeout for all operations in seconds (default: 300)
- **log_level** (str): Logging level - "DEBUG", "INFO", "WARNING", "ERROR" (default: "INFO")

#### `StorageHandler(project_id="", log_level="INFO", max_workers=4)`
Create a custom Storage client.
- **project_id** (str, optional): GCP project ID (auto-detected if empty)
- **log_level** (str): Logging level (default: "INFO")
- **max_workers** (int): Thread pool size for parallel operations (default: 4)

## Contributing

Issues and pull requests welcome at the project repository.

## License

See LICENSE file for details.