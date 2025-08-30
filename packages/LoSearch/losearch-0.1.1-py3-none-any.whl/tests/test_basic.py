import losearch as ls

# Initialize search engine
search = ls.LoSearch(enable_optimization=True)

# Add documents
documents = [
    {"id": "1", "title": "MacBook Pro", "content": "High-performance laptop with M2 chip"},
    {"id": "2", "title": "iPhone 15", "content": "Latest smartphone with advanced camera"}
]

search.add_documents(documents)

# Search with automatic optimization
results = search.contextual_search_with_scores("laptop with camera and M2 chip cpu")
for result in results:
    print(f"{result['title']} - Score: {result['score']}")