# Implementation Notes

- **Design choices:** Used in-memory storage with isolated state for each FastAPI application instance. 
  - Implemented text chunking with overlap, embedding-based retrieval, and document replacement.
- **Future improvements:** With more time, I would add persistent storage, improve error handling, and expand integration and edge-case tests.
- **AI tools used:** ChatGPT was used for implementation guidance, debugging assistance, code review, and test-case suggestions.
- **Testing:** Implemented automated tests covering API endpoints, input validation, document management, and chunking behavior.