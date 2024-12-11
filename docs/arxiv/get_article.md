# Get Article
The `GetArticle` API retrieves a specific article from arXiv.

## Parameters
* `id`: The ID of the article

## Example Usage
```python  
get_article = GetArticle()  
article = get_article.fn("1904.11655")  
print(article)  
```
