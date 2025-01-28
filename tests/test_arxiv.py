import pytest
from llama_toolbox.arxiv import GetArticle, Search

def test_get_article():
    get_article = GetArticle()
    article = get_article.fn("1904.11655")
    assert article is not None

def test_search():
    search = Search()
    results = search.fn("machine learning")
    assert results is not None