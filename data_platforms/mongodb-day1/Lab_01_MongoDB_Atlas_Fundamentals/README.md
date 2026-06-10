# Lab 1: MongoDB Atlas - CRUD, Indexing & Aggregation

---

## Lab Overview

| Aspect | Details |
|--------|---------|
| **Duration** | 20-25 minutes |
| **Objective** | Create a MongoDB Atlas cluster, perform CRUD operations, create indexes, and build aggregation pipelines |
| **Tools needed** | Web browser only |
| **Cost** | Free (no credit card required) |

---

## Prerequisites

- [ ] Web browser (Chrome, Firefox, Edge, or Safari)
- [ ] Email address (to create Atlas account)

> **Configuration:** Lab 1 has **no files to edit**. See **[Day 1 Configuration Guide](../CONFIGURATION.md)** for where credentials are used across all labs.

---

## Atlas UI Quick Reference

MongoDB recently updated the Atlas interface. You may see either the **new Data Explorer** or the older **Collections** view. Both work for this lab.

| What you need | Where to find it |
|---------------|------------------|
| Open your data | Left sidebar → **Database** → **Data Explorer** — or from **Clusters**, click **Browse Collections** |
| Select a collection | Left panel: expand cluster → `sample_mflix` → collection (e.g. `movies`) |
| Filter / query documents | **Documents** tab → **query bar** at top → click **Find** |
| Insert a document | **Add Data** dropdown → **Insert Document** |
| Edit / update a document | Hover over document → **pencil** icon — or use **Update** with `$set` |
| Delete a document | Hover over document → **trash** icon → confirm |
| Create an index | **Indexes** tab → **Create Index** |
| Run explain on a query | **Documents** tab → enter filter in query bar → click **Explain** |
| Run an aggregation | **Aggregations** tab → **STAGES** or **TEXT** mode → **Run** |

> **Tip:** There is no separate **Filter** button. Type JSON into the **query bar** and click **Find**.

---

## Theoretical Foundation: MongoDB Basics

### What is MongoDB?

MongoDB is a **NoSQL document database** that stores data in flexible, JSON-like documents instead of traditional tables with rows and columns.

| Relational Database (SQL) | MongoDB (NoSQL) |
|---------------------------|-----------------|
| Table | Collection |
| Row | Document |
| Column | Field |
| JOIN | Embedded documents or `$lookup` |
| Fixed schema | Flexible schema |

### Key Concepts in This Lab

| Concept | What It Is | Why It Matters |
|---------|-----------|----------------|
| **CRUD** | Create, Read, Update, Delete operations | Basic data manipulation |
| **Index** | Data structure that improves query speed | Makes queries 10–100x faster |
| **Aggregation** | Framework for data processing pipelines | Enables analytics and reporting |
| **Explain plan** | Shows how MongoDB executes a query | Helps debug slow queries |

---

## Part 1: Create MongoDB Atlas Account & Cluster (5 minutes)

### Step 1.1: Sign Up for MongoDB Atlas

1. Open your web browser and go to: **https://www.mongodb.com/cloud/atlas**

2. Click the **"Try Free"** button in the top-right corner

3. Create your account using one of these methods:
   - Enter your email and create a password
   - Sign up with Google
   - Sign up with GitHub

> **Important:** You will not need to enter credit card information. The free tier (M0) is completely free.

**Reference:** [Lab01_Step_1.1_Sign_Up_Atlas.pdf](../Lab%20Screenshots/Lab01_Step_1.1_Sign_Up_Atlas.pdf)

---

### Step 1.2: Create Your Free Cluster

After logging in, you will see the Cluster Overview page:

<img src="../Lab%20Screenshots/Lab01_Step_1.2_Cluster_Lab1_Overview.png" alt="Lab1-Cluster overview with Connect and Load sample data options" width="720"/>

1. Look for the **"Create a Cluster"** or **"Build a Cluster"** button

2. Select the **FREE tier option** (labeled **M0** — shared RAM, 512 MB storage)

3. Configure your cluster:

| Setting | What to choose |
|---------|----------------|
| **Cloud Provider** | AWS (or leave default) |
| **Region** | Select a region close to your location |
| **Cluster Name** | `Lab1-Cluster` |

4. Click **"Create Cluster"**

> **Wait time:** Cluster creation takes 3–5 minutes. Wait for the status to change to **Active** (green).

**What you should see after cluster creation:**
- Your cluster named `Lab1-Cluster` appears in the Clusters section
- Buttons for **Connect** and **Edit configuration** are available
- **Add data** section with options including **Load sample data**

---

### Step 1.3: Load Sample Dataset

Once your cluster is active:

1. In the **"Add data"** section, click **"Load sample data"**

<img src="../Lab%20Screenshots/Lab01_Step_1.3_Select_Sample_Dataset_mflix.png" alt="Select sample_mflix dataset to load" width="720"/>

2. A dialog appears showing available sample datasets. Make sure `sample_mflix` is selected (checkmark next to it)

3. Click **"Load sample data"**

4. Wait 1–2 minutes for the data to load

**What you should see after loading:**

<img src="../Lab%20Screenshots/Lab01_Step_1.3_Sample_Dataset_Loaded_Success.png" alt="Sample dataset successfully loaded confirmation" width="720"/>

- A message: **"Sample dataset successfully loaded"**
- Data size shown (e.g. **18.02 MB**)
- **"Browse collections"** button becomes available

5. Click **"Browse collections"** (or open **Data Explorer**) to verify the data loaded

**Expected outcome:**

<img src="../Lab%20Screenshots/Lab01_Step_1.3_Verify_Collections_sample_mflix.png" alt="sample_mflix collections listed in Data Explorer" width="720"/>

You should see the following collections under `sample_mflix`:
- `comments` (~41K documents)
- `embedded_movies` (~3.5K documents)
- `movies` (~21K documents)
- `sessions`
- `theaters` (~1.6K documents)
- `users` (~185 documents)

> **About the data:** The `movies` collection contains over 21,000 movie documents with fields like title, year, plot, genres, and IMDB ratings.

---

## Part 2: CRUD Operations — Create, Read, Update, Delete (5 minutes)

### What are CRUD Operations?

CRUD is the foundation of database interaction. Every application that stores data performs these four basic operations.

| Operation | MongoDB Command | What It Does |
|-----------|-----------------|--------------|
| **Create** | `insertOne()` or `insertMany()` | Adds new documents to a collection |
| **Read** | `find()` or `findOne()` | Retrieves documents from a collection |
| **Update** | `updateOne()` or `updateMany()` | Modifies existing documents |
| **Delete** | `deleteOne()` or `deleteMany()` | Removes documents from a collection |

---

### Step 2.1: CREATE — Insert a New Document

**What we're doing:** Adding a new movie document to the `movies` collection.

**Instructions:**

1. In **Data Explorer**, navigate to: `sample_mflix` → `movies`
   - Click on `sample_mflix` to expand it
   - Click on `movies`
   - Confirm you are on the **Documents** tab

2. Open the insert dialog:
   - Click **Add Data** → **Insert Document**, **or**
   - Click **+ Insert Document** if shown directly

3. Ensure you are in **JSON mode** (curly-braces `{ }` icon)

4. An **Insert Document** modal appears:

<img src="../Lab%20Screenshots/Lab01_Step_2.1_Insert_Document_Modal.png" alt="Insert Document modal with JSON document" width="720"/>

5. Replace the default `{}` with this document:

```json
{
  "title": "Corporate Training 101",
  "year": 2026,
  "runtime": 90,
  "plot": "A team learns MongoDB basics",
  "type": "movie",
  "awards": {
    "wins": 0,
    "nominations": 0
  }
}
```

6. Click **Insert** to save the document

**Expected outcome:**
- A success message: **"1 document has been inserted"**
- Your new document appears in the collection list

---

### Step 2.2: READ — Find Documents with a Filter

**What we're doing:** Finding all movies released after 2010.

**Instructions:**

1. Stay on `sample_mflix` → `movies` (**Documents** tab)

2. Locate the **query bar** above the documents list (there is no separate Filter button):

<img src="../Lab%20Screenshots/Lab01_Step_2.2_Read_Filter_Year_GT_2010.png" alt="Query bar with year greater than 2010 filter and results" width="720"/>

3. In the query bar, type or paste:

```json
{"year": {"$gt": 2010}}
```

4. Click **Find** or press **Ctrl+Enter** / **Cmd+Enter**

**Expected outcome:**
- The document list refreshes to show only movies from 2011 onwards
- Older movies (e.g. from the 1990s) are no longer shown

**Understanding the filter:**

| Operator | Meaning | Example |
|----------|---------|---------|
| `$gt` | Greater than | `{"year": {"$gt": 2010}}` → year > 2010 |
| `$gte` | Greater than or equal | `{"year": {"$gte": 2010}}` → year ≥ 2010 |
| `$lt` | Less than | `{"year": {"$lt": 2000}}` → year < 2000 |
| `$eq` | Equal to | `{"year": 2010}` → year = 2010 |

**Try this variation:**

```json
{"year": {"$gte": 2010, "$lte": 2020}}
```

This finds movies released between 2010 and 2020 (inclusive).

---

### Step 2.3: UPDATE — Modify a Document

**What we're doing:** Changing a reviewer's name in the `comments` collection.

**Instructions:**

1. Navigate to: `sample_mflix` → `comments`

2. Find a document to update. Enter a filter in the query bar, for example:

```json
{"_id": ObjectId("5a9427648b0beebeb69579e7")}
```

Then click **Find**

3. Click the **pencil** (edit) icon on the document, **or** use the **Update** action to open the Update modal

4. In the Update modal:

<img src="../Lab%20Screenshots/Lab01_Step_2.3_Update_Document_Modal.png" alt="Update modal with filter and set operator" width="720"/>

- The **Filter** section shows which document(s) to update: `{ _id: ObjectId('...') }`
- The **Update** section is where you specify the changes

5. In the Update section, enter:

```json
{ "$set": { "name": "Updated Corporate User" } }
```

6. Click **Update** to save the changes

**Expected outcome:**

<img src="../Lab%20Screenshots/Lab01_Step_2.3_Update_Success_Toast.png" alt="Update success toast notification" width="480"/>

- The Preview shows **"Updated Corporate User"** as the new name value
- A success message: **"1 document has been updated"**

**Understanding `$set`:**
- `$set` modifies specific fields only; other fields remain unchanged
- Syntax: `{ "$set": { "fieldName": "new value" } }`

---

### Step 2.4: DELETE — Remove a Document

**What we're doing:** Removing a test document from the `comments` collection.

**Instructions:**

1. Stay in the `comments` collection

2. Find the document to delete:

```json
{"_id": ObjectId("5a9427648b0beebeb69579e7")}
```

Click **Find**

3. Hover over the document and click the **trash** icon

**What you should see:**

<img src="../Lab%20Screenshots/Lab01_Step_2.4_Delete_Flag_Document.png" alt="Document flagged for deletion" width="720"/>

- The document shows a **"Document flagged for deletion"** indicator

4. Confirm the deletion when prompted

**Expected outcome:**

<img src="../Lab%20Screenshots/Lab01_Step_2.4_Delete_Verify_Removed.png" alt="Document removed from collection" width="720"/>

- The document is no longer visible in the collection
- Searching for that `_id` again returns no results

> **Warning:** Deleted documents cannot be recovered. In production, consider **soft delete** (adding `isDeleted: true`) instead of permanent deletion.

---

## Part 3: Indexing — Improving Query Performance (5 minutes)

### What is an Index?

An **index** is a data structure that stores a portion of the collection in an easy-to-traverse form — like a book index that lets you jump directly to the right page.

| Without Index | With Index |
|---------------|------------|
| MongoDB scans EVERY document (**COLLSCAN**) | MongoDB scans ONLY matching index entries (**IXSCAN**) |
| Slower as data grows | Stays fast even with millions of documents |
| ~21,000 documents examined | ~515 documents examined (for 1999 query) |

---

### Step 3.1: Create an Index on the Year Field

**Instructions:**

1. Navigate to: `sample_mflix` → `movies`

2. Click the **Indexes** tab (next to Documents, Aggregations, Schema)

3. Click **Create Index**

4. In the index creation form:

<img src="../Lab%20Screenshots/Lab01_Step_3.1_Create_Index_Select_Year.png" alt="Create index on year field ascending" width="720"/>

- **Field name:** `year`
- **Order:** `1` (Ascending)

5. Click **Create Index**

**Expected outcome:**

<img src="../Lab%20Screenshots/Lab01_Step_3.1_Index_year_1_Created.png" alt="year_1 index created and ready" width="720"/>

- The Indexes tab shows `year_1` in the list
- Status shows **READY**

---

### Step 3.2: Verify the Index is Being Used (Explain Plan)

**What we're doing:** Using MongoDB's explain plan to see how a query executes.

**Method A — Documents tab (recommended):**

1. Return to the **Documents** tab on `sample_mflix.movies`

2. In the **query bar**, enter:

```json
{"year": 1999}
```

3. Click **Explain** (next to **Find** — do not click Find first)

4. Review the Explain Plan modal

**Method B — Aggregations tab (explain a `$match` stage):**

> The Aggregations tab has **no query filter bar**. Put your filter inside the pipeline.

1. Click the **Aggregations** tab
2. Switch to **TEXT** mode
3. Paste: `[ { "$match": { "year": 1999 } } ]`
4. Click **Explain** (top-right of pipeline builder)

**Expected outcome:**

<img src="../Lab%20Screenshots/Lab01_Step_3.2_Explain_Plan_IXSCAN.png" alt="Explain plan showing index scan and performance metrics" width="720"/>

| Metric | Value | Meaning |
|--------|-------|---------|
| **Documents returned** | ~515 | Movies from 1999 |
| **Documents examined** | ~515 | Only matching documents scanned |
| **Index keys examined** | ~515 | Index used efficiently |
| **Execution time** | ~12 ms | Very fast query |

**Look for IXSCAN** (index scan) rather than **COLLSCAN** (collection scan). The index made this query roughly **16x faster** than scanning all ~21,000 documents.

---

## Part 4: Aggregation Pipeline — Analyzing Data (5 minutes)

### What is an Aggregation Pipeline?

An **aggregation pipeline** passes documents through a sequence of stages. Each stage transforms the data.

```
Documents ──► [$match] ──► [$group] ──► [$sort] ──► [$limit] ──► Results
              (filter)     (group by)   (order)    (limit)
```

| Stage | Purpose | Example |
|-------|---------|---------|
| `$match` | Filter documents | Only movies from 2010–2020 |
| `$group` | Group by a field | Group by year, count movies |
| `$sort` | Order results | Highest counts first |
| `$limit` | Limit output | Only top 5 results |

---

### Step 4.1: Build the Aggregation Pipeline

**Instructions:**

1. Navigate to: `sample_mflix` → `movies`

2. Click the **Aggregations** tab

3. Build the pipeline using **STAGES** mode or **TEXT** mode:

**Option A: STAGES mode (shown in screenshots)**

Add four stages:

| Stage | Operator | Expression |
|-------|----------|------------|
| Stage 1 | `$match` | `{"year": {"$gte": 2010, "$lte": 2020}}` |
| Stage 2 | `$group` | `{"_id": "$year", "movieCount": {"$sum": 1}}` |
| Stage 3 | `$sort` | `{"movieCount": -1}` |
| Stage 4 | `$limit` | `5` |

<img src="../Lab%20Screenshots/Lab01_Step_4.1_Match_Stage_2010_2020.png" alt="$match stage filtering years 2010-2020" width="720"/>

<img src="../Lab%20Screenshots/Lab01_Step_4.1_Group_Stage_MovieCount.png" alt="$group stage counting movies per year" width="720"/>

<img src="../Lab%20Screenshots/Lab01_Step_4.1_Sort_Stage_MovieCount_Desc.png" alt="$sort stage ordering by movieCount descending" width="720"/>

<img src="../Lab%20Screenshots/Lab01_Step_4.1_Limit_Stage_Top_5.png" alt="$limit stage restricting to top 5 results" width="720"/>

**Option B: TEXT mode (paste entire pipeline)**

```json
[
  { "$match": { "year": { "$gte": 2010, "$lte": 2020 } } },
  { "$group": { "_id": "$year", "movieCount": { "$sum": 1 } } },
  { "$sort": { "movieCount": -1 } },
  { "$limit": 5 }
]
```

4. Click **Run** to execute the pipeline

---

### Step 4.2: Understanding the Pipeline

| Stage | What it does to the data |
|-------|--------------------------|
| `$match` | Keeps only movies from 2010–2020 |
| `$group` | Groups by year and counts movies per year |
| `$sort` | Orders years by count, highest first (`-1` = descending) |
| `$limit` | Shows only the top 5 years |

---

### Step 4.3: Review the Results

**Expected output:**

<img src="../Lab%20Screenshots/Lab01_Step_4.3_Aggregation_Results_Top_Years.png" alt="Aggregation results showing top years by movie count" width="720"/>

| _id (year) | movieCount |
|------------|------------|
| 2013 | ~1105 |
| 2012 | ~847 |
| 2011 | ~765 |
| 2014 | ~743 |
| 2010 | ~789 |

> Your numbers may vary slightly by sample dataset version, but early-2010s years should rank highest.

---

### Step 4.4: Challenge — Modify the Pipeline

**Challenge 1:** Find the top 3 years — change `$limit` from `5` to `3` and re-run.

**Challenge 2:** Find movies with IMDB rating above 8.5

```json
[
  { "$match": { "imdb.rating": { "$gte": 8.5 } } },
  { "$sort": { "imdb.rating": -1 } },
  { "$limit": 5 },
  { "$project": { "title": 1, "year": 1, "imdb.rating": 1 } }
]
```

**Challenge 3:** Count movies by genre

```json
[
  { "$unwind": "$genres" },
  { "$group": { "_id": "$genres", "movieCount": { "$sum": 1 } } },
  { "$sort": { "movieCount": -1 } },
  { "$limit": 5 }
]
```

---

## Part 5: Lab Completion Checklist

| Task | Completed |
|------|-----------|
| ✅ Atlas account created (no credit card) | ☐ |
| ✅ M0 free cluster created and active | ☐ |
| ✅ Sample dataset loaded (`sample_mflix`) | ☐ |
| ✅ INSERT: Added new movie document | ☐ |
| ✅ READ: Filtered movies with `$gt` operator | ☐ |
| ✅ UPDATE: Modified a comment's name | ☐ |
| ✅ DELETE: Removed a test comment | ☐ |
| ✅ INDEX: Created index on `year` field | ☐ |
| ✅ EXPLAIN: Verified index usage (~515 docs examined, ~12 ms) | ☐ |
| ✅ AGGREGATION: Ran pipeline with 4 stages | ☐ |

---

## Troubleshooting Guide

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Cluster stuck on **Creating** | Normal delay | Wait up to 7 minutes, refresh page |
| **Load sample data** not visible | UI layout changed | Look under **Add data** on cluster overview, or cluster **⋯** menu |
| Filter returns no results | Misspelled field name | Check spelling: `year` not `yea` or `Year` |
| Filter not applying | Query not executed | Click **Find** or press **Ctrl+Enter** |
| Can't find Insert Document | UI changed | Use **Add Data** → **Insert Document** |
| Update not saving | Syntax error | Use `$set`: `{"$set": {"field": "value"}}` |
| Index not showing IXSCAN | Wrong field in query | Verify query uses indexed field (`year`) |
| Aggregation timeout | M0 memory limit | Add `$match` early to reduce data |
| Explain button not visible on Aggregations | No filter bar on that tab | Use **Documents** tab → query bar → **Explain**, or add `$match` stage first |
| Can't find Data Explorer | New sidebar | **Database** → **Data Explorer**, or **Browse Collections** from Clusters |

---

## Key Takeaways

| Concept | What It Does | When to Use |
|---------|--------------|-------------|
| **CRUD Operations** | Create, Read, Update, Delete documents | Every application |
| **Indexes** | Speed up queries dramatically | Fields you search frequently |
| **Explain Plan** | Shows how MongoDB executes queries | Debugging slow queries |
| **Aggregation Pipeline** | Process and analyze data in stages | Reporting and analytics |

### Performance Comparison

| Query Type | Without Index | With Index |
|------------|---------------|------------|
| `{year: 1999}` | ~21,000 documents examined | ~515 documents examined |
| Execution time | ~200 ms | ~12 ms |

---

## Screenshot Reference Summary

All screenshots are in [`Lab Screenshots/`](../Lab%20Screenshots/).

| Screenshot | Lab Step |
|------------|----------|
| Lab01_Step_1.1_Sign_Up_Atlas.pdf | 1.1 — Atlas sign-up page |
| Lab01_Step_1.2_Cluster_Lab1_Overview.png | 1.2 — Cluster created |
| Lab01_Step_1.3_Select_Sample_Dataset_mflix.png | 1.3 — Select sample dataset |
| Lab01_Step_1.3_Sample_Dataset_Loaded_Success.png | 1.3 — Load confirmation |
| Lab01_Step_1.3_Verify_Collections_sample_mflix.png | 1.3 — Collections verified |
| Lab01_Step_2.1_Insert_Document_Modal.png | 2.1 — Insert document modal |
| Lab01_Step_2.2_Read_Filter_Year_GT_2010.png | 2.2 — Filter year > 2010 |
| Lab01_Step_2.3_Update_Document_Modal.png | 2.3 — Update document modal |
| Lab01_Step_2.3_Update_Success_Toast.png | 2.3 — Update success |
| Lab01_Step_2.4_Delete_Flag_Document.png | 2.4 — Flagged for deletion |
| Lab01_Step_2.4_Delete_Verify_Removed.png | 2.4 — Deletion verified |
| Lab01_Step_3.1_Create_Index_Select_Year.png | 3.1 — Create index on year |
| Lab01_Step_3.1_Index_year_1_Created.png | 3.1 — Index created |
| Lab01_Step_3.2_Explain_Plan_IXSCAN.png | 3.2 — Explain plan (IXSCAN) |
| Lab01_Step_4.1_Match_Stage_2010_2020.png | 4.1 — `$match` stage |
| Lab01_Step_4.1_Group_Stage_MovieCount.png | 4.1 — `$group` stage |
| Lab01_Step_4.1_Sort_Stage_MovieCount_Desc.png | 4.1 — `$sort` stage |
| Lab01_Step_4.1_Limit_Stage_Top_5.png | 4.1 — `$limit` stage |
| Lab01_Step_4.3_Aggregation_Results_Top_Years.png | 4.3 — Aggregation results |

---

## Lab 1 Complete! ✅
