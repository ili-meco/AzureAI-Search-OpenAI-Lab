# Module 3: Building Search Indexes

## Introduction

Search indexes are the core data structures in Azure AI Search, similar to tables in a database. An index contains documents (similar to rows) and fields (similar to columns), with specific data types and attributes that determine how the field can be used in search scenarios.

In this module, you will learn how to design and create effective search indexes for different scenarios.

## Learning Objectives

By the end of this module, you will be able to:

- Design an effective index schema
- Create indexes through the Azure portal
- Create indexes programmatically using REST APIs
- Configure advanced index features like scoring profiles

## Index Schema Design Best Practices

### Understanding Field Attributes

Each field in an index has attributes that determine its behavior:

| Attribute | Description |
|-----------|-------------|
| **key** | Designates a field as the document identifier (required) |
| **retrievable** | Field can be returned in search results |
| **filterable** | Field can be used in filter expressions |
| **sortable** | Field can be used to sort results |
| **facetable** | Field can be used in faceted navigation |
| **searchable** | Field's content is included in full-text search |
| **analyzer** | Specifies which language analyzer to use for the field |

### Supported Data Types

- `Edm.String`
- `Edm.Int32`
- `Edm.Int64`
- `Edm.Double`
- `Edm.Boolean`
- `Edm.DateTimeOffset`
- `Edm.GeographyPoint`
- `Collection(Edm.String)` and other collection types
- `Edm.ComplexType` (for nested structures)

### Index Design Principles

1. **Include only the fields you need**:
   - Reduces index size
   - Improves performance
   - Lowers costs

2. **Choose field attributes carefully**:
   - `filterable` and `facetable` increase index size
   - `searchable` fields require additional storage for inverted indexes

3. **Use appropriate data types**:
   - Numeric fields for range filters
   - String fields for exact matching

4. **Plan for multilingual content**:
   - Define language-specific fields
   - Apply appropriate analyzers

5. **Consider vector search requirements**:
   - Vector fields for semantic search

## Step 1: Creating an Index Using the Azure Portal

### Task: Create a Simple Index

1. Navigate to your Azure AI Search service in the Azure portal

2. Select **Indexes** from the left menu, then click **+ Add index**

3. Configure basic settings:
   - **Index name**: `products-index`
   - **Key field name**: `id`

4. Add the following fields:

   | Field Name | Type | Attributes |
   |------------|------|------------|
   | `id` | `Edm.String` | Key, Retrievable |
   | `name` | `Edm.String` | Retrievable, Searchable |
   | `description` | `Edm.String` | Retrievable, Searchable |
   | `category` | `Edm.String` | Retrievable, Filterable, Facetable |
   | `price` | `Edm.Double` | Retrievable, Filterable, Sortable |
   | `rating` | `Edm.Double` | Retrievable, Filterable, Sortable |
   | `tags` | `Collection(Edm.String)` | Retrievable, Filterable, Searchable, Facetable |

5. Configure searchable fields with appropriate analyzers:
   - For `name` and `description`: Select "English - Microsoft" analyzer

6. Click **Create** to create the index

### Understanding Analyzers

Analyzers determine how text is processed during indexing and searching:

1. **Language analyzers**: Optimize for specific languages (e.g., English, Spanish)
2. **Specialized analyzers**: Handle specific content types (e.g., pattern analyzer for pattern matching)
3. **Custom analyzers**: Combine tokenizers, token filters, and char filters

## Step 2: Creating an Index Using REST API

### Task: Create an Index Programmatically

For production environments, indexes are typically created programmatically. Let's create the same index using the REST API:

1. Use a tool like Postman or curl to send a PUT request:

```http
PUT https://<your-search-service-name>.search.windows.net/indexes/products-index?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "products-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "retrievable": true
    },
    {
      "name": "name",
      "type": "Edm.String",
      "retrievable": true,
      "searchable": true,
      "analyzer": "en.microsoft"
    },
    {
      "name": "description",
      "type": "Edm.String",
      "retrievable": true,
      "searchable": true,
      "analyzer": "en.microsoft"
    },
    {
      "name": "category",
      "type": "Edm.String",
      "retrievable": true,
      "filterable": true,
      "facetable": true
    },
    {
      "name": "price",
      "type": "Edm.Double",
      "retrievable": true,
      "filterable": true,
      "sortable": true
    },
    {
      "name": "rating",
      "type": "Edm.Double",
      "retrievable": true,
      "filterable": true,
      "sortable": true
    },
    {
      "name": "tags",
      "type": "Collection(Edm.String)",
      "retrievable": true,
      "filterable": true,
      "searchable": true,
      "facetable": true
    }
  ]
}
```

2. Verify the index was created by sending a GET request:

```http
GET https://<your-search-service-name>.search.windows.net/indexes/products-index?api-version=2023-11-01
api-key: <your-admin-api-key>
```

3. For managed identity authentication instead of API keys, use:

```http
GET https://<your-search-service-name>.search.windows.net/indexes/products-index?api-version=2023-11-01
Authorization: Bearer <access-token>
```

## Step 3: Adding Scoring Profiles

Scoring profiles customize how results are ranked in response to search queries.

### Task: Create a Scoring Profile

1. Add a scoring profile to your index:

```http
PUT https://<your-search-service-name>.search.windows.net/indexes/products-index?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "products-index",
  "fields": [
    // ... existing fields ...
  ],
  "scoringProfiles": [
    {
      "name": "featured",
      "text": {
        "weights": {
          "name": 5,
          "description": 1
        }
      },
      "functions": [
        {
          "type": "magnitude",
          "fieldName": "rating",
          "boost": 2,
          "interpolation": "linear"
        },
        {
          "type": "freshness",
          "fieldName": "lastUpdated",
          "boost": 1,
          "interpolation": "logarithmic",
          "freshness": {
            "boostingDuration": "P30D"
          }
        }
      ],
      "functionAggregation": "sum"
    }
  ],
  "defaultScoringProfile": "featured"
}
```

2. This scoring profile:
   - Boosts the `name` field 5x more than the `description` field
   - Considers higher-rated products more relevant
   - Boosts recently updated products

## Step 4: Advanced Index Features

### Synonym Maps

Synonym maps help users find relevant content even when using different terms:

```http
PUT https://<your-search-service-name>.search.windows.net/synonymmaps/product-synonyms?api-version=2023-11-01
Content-Type: application/json
api-key: <your-admin-api-key>

{
  "name": "product-synonyms",
  "synonyms": "laptop, notebook, computer\nphone, smartphone, mobile"
}
```

Then attach to searchable fields:

```json
{
  "name": "description",
  "type": "Edm.String",
  "searchable": true,
  "analyzer": "en.microsoft",
  "synonymMaps": ["product-synonyms"]
}
```

### Custom Analyzers

Create custom analyzers for specialized content:

```json
"analyzers": [
  {
    "name": "my-custom-analyzer",
    "tokenizer": "standard",
    "tokenFilters": ["lowercase", "asciifolding"],
    "charFilters": []
  }
]
```

Then use in field definitions:

```json
{
  "name": "description",
  "type": "Edm.String",
  "searchable": true,
  "analyzer": "my-custom-analyzer"
}
```

## Lab Exercise: Building Effective Indexes

### Exercise 1: Design an Index for a Document Repository

Design an index schema for a document repository with the following requirements:

- Store information about PDF and Word documents
- Include metadata like title, author, creation date, file size
- Support full-text search within document content
- Enable filtering by document type, author, and date ranges
- Support faceted navigation for document categories
- Implement customized relevance based on recency and document popularity

Document your index schema, including:
- Field names and data types
- Field attributes
- Any scoring profiles
- Any custom analyzers or synonym maps

### Exercise 2: Create and Test Your Index

1. Create the index you designed using either the Azure portal or REST API
2. Test your index by adding a few sample documents
3. Execute search queries to verify functionality:
   - Full-text search for specific content
   - Filtering by document metadata
   - Sorting by relevance and other fields
   - Faceted navigation

## Next Steps

In the next module, you'll learn how to create and configure indexers to automatically populate your search indexes from various data sources.

## Additional Resources

- [Create a basic index in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-what-is-an-index)
- [Index attributes reference](https://learn.microsoft.com/en-us/azure/search/index-add-attributes)
- [Scoring profiles for relevance tuning](https://learn.microsoft.com/en-us/azure/search/index-add-scoring-profiles)
- [Language analyzers in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-language-support)
- [Create custom analyzers for Azure AI Search](https://learn.microsoft.com/en-us/azure/search/index-add-custom-analyzers)
