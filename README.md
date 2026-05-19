This is a working copy of the 05-rag-1 project created for separate work.

Files copied:
- chat.py
- indexing.py
- docker-compose.yml
- .env

Development
-----------

To run the project locally:

1. Create a virtual environment and install dependencies: `pip install -r requirements.txt`
2. Provide a `GOOGLE_API_KEY` in a `.env` file or via prompt.
3. To build the vector index (dry run): `python indexing.py`
4. To run the chat tool: `python chat.py`

See individual scripts for more details.

Testing
-------

Run the minimal smoke test suite with:

```
pytest -q
```

