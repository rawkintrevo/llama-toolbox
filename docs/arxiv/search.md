# docs/arxiv/search.md
# Search
The `Search` API searches for articles on arXiv.

## Parameters
* `query`: The search query
* `start`: The start index of the search results
* `max_results`: The maximum number of search results to return
* `submittedDateFrom`: The start submission date in the format YYYYMMDD
* `submittedDateTo`: The end submission date in the format YYYYMMDD
* `ti`: Search in title
* `au`: Search in author
* `abs`: Search in abstract
* `co`: Search in comment
* `jr`: Search in journal reference
* `cat`: Search in subject category

## Example Usage
```python  
search = Search()  
results = search.fn("machine learning", submittedDateFrom="20220101", submittedDateTo="20220131", ti="deep learning")  
print(results)  
```