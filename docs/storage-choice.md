# Choosing storage for our bar example

[Repository overview](../README.md#current-class-persistence-and-databases-exercise-4) | [Exercise 4, Part B](../exercises/04-persistence.md#part-b---explain-json-storage) | [Project choice](../exercises/04-persistence.md#apply-the-comparison-to-your-project)

Start with one operation: **save an order and its lines**. This is the diagram from the classroom slides. It helps shortlist options; the questions are not an exhaustive database-selection algorithm.

![Decision guide for JSON files, relational storage and database deployment. The same decisions are explained in the table below.](images/storage-choice.svg)

## Read the decisions

| Question | What the branch means for our example |
| --- | --- |
| Are simple whole-file reads and writes sufficient? | A JSON file can suit a small, controlled prototype. Our `solution/` loads the file, checks and changes the data, then saves it. The application remains responsible for consistency and coordinating writes. |
| Are related records and all-or-nothing writes central? | A relational database is a useful candidate for orders, order lines and menu items. Relationships and transactions are also available in other database models; this branch is a shortlist, not an exclusive capability claim. |
| Is access local, with limited simultaneous writes? | File-backed SQLite suits our classroom comparison. It permits multiple readers but serialises writes. Evaluate a database server, such as PostgreSQL, when shared service access or greater simultaneous write demand is important. User count alone is not the deciding factor. |
| Does another access pattern dominate? | Explore document, key-value, graph or specialised stores. One application may use more than one store. These are further reading, with no additional setup task in this class. |

The initial JSON prototype and the SQLite comparison illustrate different requirements for the same bar scenario. A JSON file remains a valid project choice when it meets your needs. JSON sent over HTTP is a separate issue: an API can return JSON regardless of how it stores its data.

## Where the ORM fits

**Python objects ? SQLModel / SQLAlchemy ? relational database.** The ORM maps objects to rows and translates operations into SQL. It is a programming approach, not another database family. Our small comparison uses SQLite in a file; declaring a Python class alone does not create an ORM mapping or a database.

In class, first follow the JSON explanation in [Part B](../exercises/04-persistence.md#part-b---explain-json-storage), then sketch related records in [Part C](../exercises/04-persistence.md#part-c---sketch-related-records). We introduce the session and read mapped code before starting the [ORM comparison in Part D](../extensions/orm/README.md#classroom-stages).

## Use it for your project

Choose one operation, state what must be stored and what must succeed or fail together, then justify a storage candidate. Explain one limitation and show evidence that the chosen approach works. Use the [project comparison activity](../exercises/04-persistence.md#apply-the-comparison-to-your-project) after the query experiment. Adopting an ORM is optional; no new project requirement is introduced here.

## Sources and further reading

The decision questions are a teaching synthesis for this repository. The question-and-branch layout is inspired by [Microsoft's vector-search flowchart](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/images/vector-search-flowchart.svg); its product-selection rules are not used here.

- [Microsoft: understand data-store models](https://learn.microsoft.com/en-us/azure/architecture/data-guide/technology-choices/understand-data-store-models) explains relational, document, key-value, graph and other models for different access patterns.
- [SQLite: appropriate uses](https://www.sqlite.org/whentouse.html) discusses local storage, deployment and write-concurrency considerations.
- [FastAPI: SQL databases](https://fastapi.tiangolo.com/tutorial/sql-databases/) supplies the official SQLModel/SQLite teaching example behind our ORM walkthrough.

[Return to Exercise 4](../exercises/04-persistence.md) | [Return to the repository overview](../README.md)
