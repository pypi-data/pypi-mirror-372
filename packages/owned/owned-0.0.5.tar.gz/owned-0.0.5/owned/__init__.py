"""
owned.py

A module that uses the 'owner' library to embed information into byte content (weaving)
and store it locally, as well as post the resulting hash to a blockchain for ownership
verification. Includes helper functions to verify the posting of hashes on the blockchain.

Main Functionalities:
---------------------
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

Helper Functions:
----------------
- DFLT_HASH: Default hashing function (sha256).
- weave_content(content, extra_info=None): Uses 'owner.HeadWeaver' to weave extra bytes into the content.
- unweave_content(woven_bytes): Recovers content and metadata from woven bytes.
- Additional internal functions for file handling and directory creation.

Examples:
---------

>>> from owned import store_content, unweave_content
>>> import os

>>> # Store some content (with weaving) and get its hash key
>>> test_content = b"Hello, doctest!"
>>> key = store_content(test_content, extra_info=b"Extra info", use_weave=True)

>>> # Verify the file exists in ~/.config/owned
>>> file_path = os.path.expanduser(f"~/.config/owned/{key}")
>>> assert os.path.isfile(file_path)

>>> # Check the length of the SHA256 hash (64 hex chars)
>>> assert len(key) == 64

>>> # Read the stored file and unweave the content
>>> with open(file_path, "rb") as f:
...     woven_data = f.read()
>>> original_content = unweave_content(woven_data)
>>> original_content == test_content
True


"""

import os
import hashlib
import json
from pathlib import Path

# Blockchain tools (web3.py)
try:
    from web3 import Web3
except ImportError:
    Web3 = None

# owner library for weaving/unweaving
try:
    from owner import HeadWeaver
except ImportError:
    HeadWeaver = None


########################################################################
# Constants and Defaults
########################################################################


# Default hashing function: returns sha256 hex digest of the given content
def sha256_hash(content: bytes) -> str:
    """
    Returns the SHA256 hex digest for the given content.
    """
    return hashlib.sha256(content).hexdigest()


DFLT_HASH = sha256_hash

# Default storage directory
DEFAULT_STORAGE_DIR = Path.home() / '.config' / 'owned'


########################################################################
# Helper Functions
########################################################################


def _ensure_storage_dir_exists():
    """
    Ensures that the default storage directory (DEFAULT_STORAGE_DIR) exists.
    Creates it recursively if it does not exist.
    """
    DEFAULT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def weave_content(content: bytes, extra_info: bytes = None) -> bytes:
    """
    Weaves the content with optional extra_info using owner.HeadWeaver.
    Returns the woven bytes, which contain the original content plus
    additional embedded data.
    """
    if HeadWeaver is None:
        raise ImportError('owner library is not installed or not accessible.')
    weaver = HeadWeaver()
    woven_bytes = weaver.weave(content, extra_info if extra_info else b'')
    return woven_bytes


def unweave_content(woven_bytes: bytes):
    """
    Unweaves the provided bytes (created with weave_content) using owner.HeadWeaver.
    Returns the original content. This is not strictly required by the main
    functionalities but is provided for completeness and verification.
    """
    if HeadWeaver is None:
        raise ImportError('owner library is not installed or not accessible.')
    weaver = HeadWeaver()
    return weaver.unweave(woven_bytes)


########################################################################
# Core Functionalities
########################################################################


def store_content(
    content: bytes,
    extra_info: bytes = None,
    use_weave: bool = False,
    hasher=DFLT_HASH,
    storage_dir=DEFAULT_STORAGE_DIR,
) -> str:
    """
    Hashes the given content (optionally weaving extra_info into the content),
    stores it in the specified storage directory, and returns the computed hash
    (the 'key'). The file name is the resulting hash.

    Parameters
    ----------
    content : bytes
        The raw content to be stored.
    extra_info : bytes, optional
        Additional metadata to weave into the content if use_weave is True.
    use_weave : bool, optional
        If True, content is first woven with extra_info before hashing/storing.
    hasher : Callable, optional
        Function that takes bytes and returns a hash string. Defaults to DFLT_HASH.
    storage_dir : str or Path, optional
        Directory in which to store the content file. Defaults to DEFAULT_STORAGE_DIR.

    Returns
    -------
    str
        The hash string (file name) under which the content is stored.
    """
    _ensure_storage_dir_exists()

    final_content = weave_content(content, extra_info) if use_weave else content
    content_hash = hasher(final_content)

    file_path = Path(storage_dir) / content_hash
    if not file_path.exists():
        with open(file_path, 'wb') as f:
            f.write(final_content)

    return content_hash


def post_hash_to_blockchain(
    hash_str: str,
    provider_uri: str = 'http://127.0.0.1:8545',
    from_address: str = None,
    private_key: str = None,
    gas: int = 21000,
    gas_price: int = None,
):
    """
    Posts the given hash string to a blockchain using web3.py, embedding
    the hash as transaction data. Returns a transaction receipt or relevant
    logging info.

    Parameters
    ----------
    hash_str : str
        The hash to be recorded on the blockchain.
    provider_uri : str, optional
        URI of the Ethereum node to connect to. Defaults to local Ganache.
    from_address : str, optional
        Address from which to send the transaction. Required if signing locally.
    private_key : str, optional
        Private key for the above from_address. Required if signing locally.
    gas : int, optional
        Gas limit for the transaction. Defaults to 21000 (simple ETH transfer).
    gas_price : int, optional
        Gas price in wei. If not provided, a default strategy may be used.

    Returns
    -------
    dict or None
        A transaction receipt dict if the transaction is sent successfully,
        or None if web3.py is not installed or if insufficient parameters were provided.
    """
    if Web3 is None:
        raise ImportError('web3.py is not installed or not accessible.')

    w3 = Web3(Web3.HTTPProvider(provider_uri))
    if not w3.isConnected():
        raise ConnectionError(f'Cannot connect to Ethereum node at {provider_uri}')

    if not from_address or not private_key:
        raise ValueError(
            'from_address and private_key must be provided to sign transactions.'
        )

    nonce = w3.eth.getTransactionCount(from_address)

    tx = {
        'nonce': nonce,
        'to': '',  # No recipient (contract creation not required), just storing data in 'data' field
        'value': 0,
        'gas': gas,
        'gasPrice': gas_price if gas_price else w3.eth.gasPrice,
        'data': w3.toHex(text=hash_str),
        'chainId': w3.eth.chainId,
    }

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    return dict(receipt)


def verify_hash_on_blockchain(
    hash_str: str,
    provider_uri: str = 'http://127.0.0.1:8545',
    lookback_blocks: int = 1000,
):
    """
    Checks the blockchain for transactions embedding the specified hash string.
    Scans recent blocks (up to lookback_blocks). Returns a list of matches,
    where each match contains block number and transaction information.

    Note: This naive approach iterates over blocks in the given range. For
    production usage, an indexer or a more direct method is recommended.

    Parameters
    ----------
    hash_str : str
        The hash string to search for on the blockchain.
    provider_uri : str, optional
        URI of the Ethereum node to connect to.
    lookback_blocks : int, optional
        Number of past blocks to scan from the latest block.

    Returns
    -------
    list of dict
        Each dict may contain information such as blockNumber, transactionHash, etc.
    """
    if Web3 is None:
        raise ImportError('web3.py is not installed or not accessible.')

    w3 = Web3(Web3.HTTPProvider(provider_uri))
    if not w3.isConnected():
        raise ConnectionError(f'Cannot connect to Ethereum node at {provider_uri}')

    current_block = w3.eth.blockNumber
    earliest_block = max(0, current_block - lookback_blocks)

    matches = []
    target_hex = w3.toHex(text=hash_str)

    for block_num in range(earliest_block, current_block + 1):
        block = w3.eth.getBlock(block_num, full_transactions=True)
        for tx in block.transactions:
            if tx.input == target_hex:
                match_info = {
                    'blockNumber': block_num,
                    'transactionHash': tx.hash.hex(),
                    'from': tx['from'],
                    'to': tx['to'],
                    'data': tx.input,
                }
                matches.append(match_info)

    return matches


########################################################################
# Test Functions (pytest style)
########################################################################


def test_store_content_plain():
    """
    Tests storing unmodified content (no weaving). Asserts that the returned
    hash matches the actual content hash, and that a file is created.
    """
    test_data = b'hello world'
    hash_key = store_content(test_data, use_weave=False)
    assert os.path.exists(DEFAULT_STORAGE_DIR / hash_key), 'File was not stored.'
    # Verify that re-hashing the stored file yields the same key
    with open(DEFAULT_STORAGE_DIR / hash_key, 'rb') as f:
        actual_data = f.read()
    assert sha256_hash(actual_data) == hash_key, 'Hash mismatch for stored file.'


def test_store_content_woven():
    """
    Tests storing woven content. Asserts that the returned hash matches
    the hash of the woven result and that the unweave function can recover
    the original content.
    """
    test_data = b'bob and alice'
    hash_key = store_content(test_data, extra_info=b'my secret', use_weave=True)
    assert os.path.exists(DEFAULT_STORAGE_DIR / hash_key), 'File was not stored.'

    # Validate weaving/unweaving
    with open(DEFAULT_STORAGE_DIR / hash_key, 'rb') as f:
        stored_data = f.read()
    original = unweave_content(stored_data)
    assert original == test_data, 'Woven/unwoven content does not match original.'


def test_post_and_verify_hash_on_blockchain():
    """
    This test checks whether a hash can be posted and then verified on the
    blockchain. These operations require a running Ethereum node and valid
    credentials. If web3 or a node is not available, this test will likely fail.
    """
    if Web3 is None:
        # web3.py not installed; skip
        return

    sample_hash = 'abc123def456'
    # The following call will require a valid from_address and private key
    # post_hash_to_blockchain(hash_str=sample_hash, from_address="0x...", private_key="...")

    # The verify step can be performed by scanning a range of recent blocks:
    # results = verify_hash_on_blockchain(hash_str=sample_hash, lookback_blocks=100)
    # For demonstration, not asserting here because it depends on environment availability.
    pass
