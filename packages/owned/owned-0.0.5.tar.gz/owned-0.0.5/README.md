# owned

A little tool to manage secrets.

The package uses the 'owner' library to embed information into byte content (weaving)
and store it locally, as well as post the resulting hash to a blockchain for ownership
verification. Includes helper functions to verify the posting of hashes on the blockchain.

To install:	```pip install owned```

# Main Functionalities


1) store_content(content, ...) -> str
   - Optionally weaves metadata into the content (using 'owner') before storage.
   - Saves the content in the ~/.config/owned folder under a file name derived from its hash.
   - Returns the computed hash string (the 'key').

2) post_hash_to_blockchain(hash_str, provider_uri='http://127.0.0.1:8545', ...)
   - Posts the hash to a chosen blockchain via web3.py.
   - Returns transaction or logging information.

3) verify_hash_on_blockchain(hash_str, provider_uri='http://127.0.0.1:8545', ...)
   - Verifies that a particular hash has been posted on the blockchain.
   - Returns information such as block number, transaction details, or a boolean indicating presence.

## Helper Functions

- DFLT_HASH: Default hashing function (sha256).
- weave_content(content, extra_info=None): Uses 'owner.HeadWeaver' to weave extra bytes into the content.
- unweave_content(woven_bytes): Recovers content and metadata from woven bytes.
- Additional internal functions for file handling and directory creation.

## Examples

```python
>>> from owned import store_content, unweave_content
>>> import os
```

Store some content (with weaving) and get its hash key.

```python
>>> test_content = b"Hello, doctest!"
>>> key = store_content(test_content, extra_info=b"Extra info", use_weave=True)
```

Verify the file exists in ~/.config/owned

```python
>>> file_path = os.path.expanduser(f"~/.config/owned/{key}")
>>> assert os.path.isfile(file_path)
```

Check the length of the SHA256 hash (64 hex chars).

```python
>>> len(key)
64
```

Read the stored file and unweave the content.

```python
>>> with open(file_path, "rb") as f:
...     woven_data = f.read()
>>> original_content = unweave_content(woven_data)
>>> original_content == test_content
True
```
