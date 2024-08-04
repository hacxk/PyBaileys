import os
import uuid
from typing import Dict, List, Any, Callable, Awaitable, TypeVar, Optional
from cachetools import TTLCache
from loguru import logger
from defaults.defaults import DEFAULT_CACHE_TTLS
from models.sock_models import AuthenticationCreds, CacheStore, SignalDataSet, SignalDataTypeMap, SignalKeyStore, SignalKeyStoreWithTransaction, TransactionCapabilityOptions
from .crypto_utils import Curve, signed_key_pair
from .generics_utils import delay, generate_registration_id

T = TypeVar('T')

def make_cacheable_signal_key_store(
    store: SignalKeyStore,
    logger: Any,
    _cache: Optional[CacheStore] = None
) -> SignalKeyStore:
    cache = _cache or TTLCache(maxsize=1000, ttl=DEFAULT_CACHE_TTLS['SIGNAL_STORE'])

    def get_unique_id(type: str, id: str) -> str:
        return f"{type}.{id}"

    async def get(type: str, ids: List[str]) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        ids_to_fetch: List[str] = []
        for id in ids:
            item = cache.get(get_unique_id(type, id))
            if item is not None:
                data[id] = item
            else:
                ids_to_fetch.append(id)

        if ids_to_fetch:
            logger.trace(f"loading {len(ids_to_fetch)} items from store")
            fetched = await store.get(type, ids_to_fetch)
            for id in ids_to_fetch:
                item = fetched.get(id)
                if item:
                    data[id] = item
                    cache[get_unique_id(type, id)] = item

        return data

    async def set(data: SignalDataSet):
        keys = 0
        for type in data:
            for id in data[type]:
                cache[get_unique_id(type, id)] = data[type][id]
                keys += 1

        logger.trace(f"updated {keys} keys in cache")
        await store.set(data)

    async def clear():
        cache.clear()
        if hasattr(store, 'clear'):
            await store.clear()

    return SignalKeyStore(get=get, set=set, clear=clear)

def add_transaction_capability(
    state: SignalKeyStore,
    logger: Any,
    options: TransactionCapabilityOptions
) -> SignalKeyStoreWithTransaction:
    max_commit_retries = options.get('maxCommitRetries', 5)
    delay_between_tries_ms = options.get('delayBetweenTriesMs', 1000)

    db_queries_in_transaction = 0
    transaction_cache: SignalDataSet = {}
    mutations: SignalDataSet = {}
    transactions_in_progress = 0

    def is_in_transaction() -> bool:
        return transactions_in_progress > 0

    async def get(type: str, ids: List[str]) -> Dict[str, Any]:
        if is_in_transaction():
            dict_ = transaction_cache.get(type, {})
            ids_requiring_fetch = [id for id in ids if id not in dict_]
            if ids_requiring_fetch:
                nonlocal db_queries_in_transaction
                db_queries_in_transaction += 1
                result = await state.get(type, ids_requiring_fetch)
                transaction_cache.setdefault(type, {}).update(result)

            return {id: transaction_cache[type][id] for id in ids if id in transaction_cache.get(type, {})}
        else:
            return await state.get(type, ids)

    async def set(data: SignalDataSet):
        if is_in_transaction():
            logger.trace(f"caching {list(data.keys())} types in transaction")
            for key in data:
                transaction_cache.setdefault(key, {}).update(data[key])
                mutations.setdefault(key, {}).update(data[key])
        else:
            await state.set(data)

    async def transaction(work: Callable[[], Awaitable[T]]) -> T:
        nonlocal transactions_in_progress, db_queries_in_transaction
        transactions_in_progress += 1
        if transactions_in_progress == 1:
            logger.trace("entering transaction")

        try:
            result = await work()
            if transactions_in_progress == 1:
                if mutations:
                    logger.trace("committing transaction")
                    tries = max_commit_retries
                    while tries:
                        tries -= 1
                        try:
                            await state.set(mutations)
                            logger.trace(f"committed transaction with {db_queries_in_transaction} db queries")
                            break
                        except Exception as error:
                            logger.warning(f"failed to commit {len(mutations)} mutations, tries left={tries}")
                            await delay(delay_between_tries_ms)
                else:
                    logger.trace("no mutations in transaction")
            return result
        finally:
            transactions_in_progress -= 1
            if transactions_in_progress == 0:
                nonlocal transaction_cache, mutations
                transaction_cache = {}
                mutations = {}
                db_queries_in_transaction = 0

    return SignalKeyStoreWithTransaction(
        get=get,
        set=set,
        isInTransaction=is_in_transaction,
        transaction=transaction
    )

def init_auth_creds() -> AuthenticationCreds:
    identity_key = Curve.generate_key_pair()
    return AuthenticationCreds(
        noise_key=Curve.generate_key_pair(),
        pairing_ephemeral_key_pair=Curve.generate_key_pair(),
        signed_identity_key=identity_key,
        signed_pre_key=signed_key_pair(identity_key, 1),
        registration_id=generate_registration_id(),
        adv_secret_key=os.urandom(32).hex(),
        processed_history_messages=[],
        next_pre_key_id=1,
        first_unuploaded_pre_key_id=1,
        account_sync_counter=0,
        account_settings={
            'unarchive_chats': False
        },
        device_id=uuid.uuid4().hex.encode().decode('utf-8'),
        phone_id=str(uuid.uuid4()),
        identity_id=os.urandom(20),
        registered=False,
        backup_token=os.urandom(20),
        registration={},
        pairing_code=None,
        last_prop_hash=None,
        routing_info=None,
    )