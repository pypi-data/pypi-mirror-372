# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

"""
Contains the client class to have any/all the communications with Redis as async.
"""

import asyncio
import random
import redis.asyncio as redis
from ibm_wos_utils.common.utils.common_logger import CommonLogger
from ibm_wos_utils.common.utils.date_util import DateUtil


class RedisAsyncClient:

    """
    The class contains the methods to have async communications with Redis.
    """

    def __init__(
            self,
            url: str,
            port: int,
            username: str,
            password: str,
            ssl_ca_cert_path: str,
            max_connections: int=10,
            timeout: int=10,
            redis_connection_max_retry_count:int=5,
            health_check_interval: int=10,
            enable_locking_keys: bool=False,
            logger=None
        ):
        """
        Initializes the object with credentials.
        :url: The Redis host URL.
        :port: The Redis port.
        :username: The user name for authentication.
        :password: The password for authentication.
        :max_connections: Defines the pool size.
        :timeout: The number of seconds to wait for a connection to be available, if None, it will wait/block forever.
        :redis_connection_max_retry_count: The maximum number of retries to be done for a connection in case getting one fails.
        :health_check_interval: The health check interval for connections in the pool so that they don't die.
        :enable_locking_keys: Enables methods to allow locking keys in Redis.
        :logger: The logger object to be used to log messages. [If not given, common logger would be used.]
        """
        # Initializing the logger
        self.logger = logger if logger is not None else CommonLogger(__name__)
        self.redis_connection_max_retry_count = redis_connection_max_retry_count
        self.health_check_interval = health_check_interval
        self.enable_locking_keys = enable_locking_keys

        # Creating a connection pool
        self.conn_pool = redis.BlockingConnectionPool(
            connection_class=redis.SSLConnection,
            max_connections=max_connections,
            timeout=timeout,
            host=url,
            port=port,
            username=username,
            password=password,
            ssl_ca_certs=ssl_ca_cert_path,
            decode_responses=True
        )
        return
    
    async def set(self, key: str, value: str, ex: int=None, px:int=None, nx:bool=False, xx:bool=False, keepttl:bool=False, retry_count: int=0) -> bool:
        """
        Sets the given key-value (bytes, string, int or float) in Redis.
        :key: The key to be stored.
        :value: The string value to be stored.
        :ex: Sets an expire flag on key for ``ex`` seconds.
        :px: Sets an expire flag on key for ``px`` milliseconds.
        :nx: If set to True, set the value at key to ``value`` only if it does not exist.
        :xx: If set to True, set the value at key to ``value`` only if it already exists.
        :keepttl: If True, retain the time to live associated with the key. (Available since Redis 6.0)
        :retry_count: The number of times retrying the connection has been done.

        :returns: True is value was set successfully, False otherwise.
        """

        key_stored = False
        try:
            if self.enable_locking_keys:
                # Checking if a lock is present on the key
                lock_key = f"lock_{key}"
                if await self.get(key=lock_key) is not None:
                    # Lock is present on the key, it cannot be modified
                    self.logger.log_info(f"Lock is present on the key '{key}', hence it cannot be modified.")
                    return key_stored

            # Getting a connection to Redis
            rconn = await self._get_connection(key=key, operation="SET")

            # Setting the value in Redis
            self.logger.log_info(f"Setting key '{key}' to Redis.")
            start_time = DateUtil.current_milli_time()
            key_stored = await rconn.set(key, value, ex=ex, px=px, nx=nx, xx=xx, keepttl=keepttl)
            if key_stored is None and nx:
                key_stored = False
                self.logger.log_info(f"Could not store key '{key}' as it was already there as 'nx' was set to true.")
            self.logger.log_info(f"Successfully set key '{key}' to Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'SET' on key '{key}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'SET' on key '{key}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                key_stored = await self.set(key, value, ex, px, nx, xx, keepttl, retry_count+1)
        except Exception as ex:
            self.logger.log_error(f"Failed to set key '{key}' in Redis. Error: '{str(ex)}'.")
            raise

        return key_stored
    
    async def get(self, key: str, retry_count: int=0) -> bytes:
        """
        Gets the value for the given key from Redis.
        :key: The key to be retrieved.
        :retry_count: The number of times retrying the connection has been done.

        :returns: The value (bytes) for the given key, None if key does not exist.
        """
        val = None

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(key=key, operation="GET")

            # Getting the value from Redis
            self.logger.log_info(f"Getting key '{key}' from Redis.")
            start_time = DateUtil.current_milli_time()
            val = await rconn.get(key)
            self.logger.log_info(f"Successfully retrieved key '{key}' from Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'GET' on key '{key}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'GET' on key '{key}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                val = await self.get(key, retry_count+1)
        except Exception as ex:
            self.logger.log_error(f"Failed to get key '{key}' from Redis. Error: '{str(ex)}'.")
            raise

        return val
    
    async def hget(self, name: str, key: str, retry_count: int=0) -> str:
        """
        Gets the value for the given key from the sorted set with given name from Redis.
        :name: The name of the sorted set.
        :key: The key to be retrieved from the sorted set.
        :retry_count: The number of times retrying the connection has been done.

        :returns: The value for the given key, None if key does not exist.
        """
        val = None

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(key=key, operation="HGET")

            # Getting the value from Redis
            self.logger.log_info(f"Getting key '{key}' from sorted set '{name}' in Redis.")
            start_time = DateUtil.current_milli_time()
            val = await rconn.hget(name, key)
            self.logger.log_info(f"Successfully retrieved key '{key}' from sorted set '{name}' in Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'HGET' on key '{key}' from sorted set '{name}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'HGET' on key '{key}' from sorted set '{name}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                val = await rconn.hget(name, key)
        except Exception as ex:
            self.logger.log_error(f"Failed to get key '{key}' from sorted set '{name}' in Redis. Error: '{str(ex)}'.")
            raise

        return val
    
    async def zrange(
        self,
        name: str,
        start: int,
        end: int,
        desc: bool=None,
        withscores: bool=None,
        score_cast_func: callable=None,
        byscore: bool=None,
        bylex: bool=None,
        offset: int=None,
        num: int=None,
        retry_count: int=0
    ) -> list:
        """
        Returns the range of values from the sorted set `name` between `start` and `end` sorted in ascending order.
        :name: The name of the sorted set.
        :start: The start of the range.
        :end: The end of the range.
        :desc: Boolean to indicate to sort the result in descending order. DEFAULT: False.
        :withscores: Boolean to return scores along with values. DEFAULT: False.
        :score_cast_func: Callable used to cast the score values.
        :byscore: Boolean to return the values from the sorted set between between `start` and `end` inclusive. DEFAULT: False.
        :bylex: Boolean to return the range of elements from the sorted set between the start and end lexicographical closed range intervals. Valid `start` and `end` must start with ( or [, in order to specify whether the range interval is exclusive or inclusive, respectively.
        :offset: `offset` and `num` are specified, then return a slice of the range. Can't be provided when using bylex.
        :num:`offset` and `num` are specified, then return a slice of the range. Can't be provided when using bylex.
        :retry_count: The number of times retrying the connection has been done.

        :returns: The list of ranges from the sorted set.
        """
        values = None

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(key=name, operation="ZRANGE")

            # Getting the value from Redis
            self.logger.log_info(f"Getting range from sorted set '{name}' from Redis.")
            start_time = DateUtil.current_milli_time()
            values = await rconn.zrange(
                name=name,
                start=start,
                end=end,
                desc=desc,
                withscores=withscores,
                score_cast_func=score_cast_func,
                byscore=byscore,
                bylex=bylex,
                offset=offset,
                num=num
            )
            self.logger.log_info(f"Successfully retrieved range from sorted set '{name}' from Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'ZRANGE' on sorted set '{name}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'ZRANGE' on sorted set '{name}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                values = await self.zrange(
                    name=name,
                    start=start,
                    end=end,
                    desc=desc,
                    withscores=withscores,
                    score_cast_func=score_cast_func,
                    byscore=byscore,
                    bylex=bylex,
                    offset=offset,
                    num=num,
                    retry_count=retry_count+1
                )
        except Exception as ex:
            self.logger.log_error(f"Failed to get range from sorted set '{name}' from Redis. Error: '{str(ex)}'.")
            raise

        return values
    
    async def zscore(self, name: str, value: any, retry_count: int=0) -> any:
        """
        Gets the score of the value for the given sorted set from Redis.
        :name: The name of the sorted set.
        :value: The value for which the score is to be retrieved.
        :retry_count: The number of times retrying the connection has been done.

        :returns: The score for the given value, None if value does not exist in sorted set.
        """
        score = None

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(key=name, operation="ZSCORE")

            # Getting the value from Redis
            self.logger.log_info(f"Getting score for value '{value}' in sorted set '{name}' from Redis.")
            start_time = DateUtil.current_milli_time()
            score = await rconn.zscore(name, value)
            self.logger.log_info(f"Successfully retrieved score for value '{value}' from sorted set '{name}' from Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'ZSCORE' on sorted set '{name}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'ZSCORE' for value '{value}' in sorted set '{name}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                score = await self.zscore(name, value, retry_count+1)
        except Exception as ex:
            self.logger.log_error(f"Failed to get score for value {value} in sorted set '{name}' from Redis. Error: '{str(ex)}'.")
            raise

        return score
    
    async def delete(self, key: str, retry_count: int=0) -> bool:
        """
        Deletes the value (bytes, string, int or float) for the given key.
        :key: The key to be deleted.
        :retry_count: The number of times retrying the connection has been done.

        :returns: True is the key was deleted successfully, False otherwise.
        """
        key_deleted = False

        try:
            if self.enable_locking_keys:
                # Checking if a lock is present on the key
                lock_key = f"lock_{key}"
                if await self.get(key=lock_key) is not None:
                    # Lock is present on the key, it cannot be deleted
                    self.logger.log_info(f"Lock is present on the key '{key}', hence it cannot be deleted.")
                    return key_deleted
            
            # Getting a connection to Redis
            rconn = await self._get_connection(key=key, operation="DELETE")

            # Deleting the value from Redis
            self.logger.log_info(f"Deleting key '{key}' from Redis.")
            start_time = DateUtil.current_milli_time()
            await rconn.delete(key)
            key_deleted = True
            self.logger.log_info(f"Successfully deleted key '{key}' from Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'DELETE' on key '{key}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'DELETE' on key '{key}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                key_deleted = await self.delete(key, retry_count+1)
        except Exception as ex:
            self.logger.log_error(f"Failed to delete key '{key}' from Redis. Error: '{str(ex)}'.")
            raise

        return key_deleted
    
    async def zrem(self, name: str, *values, retry_count: int=0) -> int:
        """
        Deletes the given values from the sorted set with the given name.
        :name: The name of the sorted set.
        :values: The values to be deleted from the sorted set.
        :retry_count: The number of times retrying the connection has been done.

        :returns: Number of values deleted from the sorted set.
        """
        num_deleted = None

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(key=name, operation="ZREM")

            # Deleting the value from Redis
            self.logger.log_info(f"Deleting values '{values}' from sorted set '{name}' in Redis.")
            start_time = DateUtil.current_milli_time()
            num_deleted = await rconn.zrem(name, *values)
            self.logger.log_info(f"Successfully deleted values '{values}' with num_deleted '{num_deleted}' from sorted set '{name}' in Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'ZREM' on sorted set '{name}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'ZREM' on sorted set '{name}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                num_deleted = await self.zrem(name, *values, retry_count+1)
        except Exception as ex:
            self.logger.log_error(f"Failed to delete values '{values}' from sorted set '{name}' in Redis. Error: '{str(ex)}'.")
            raise

        return num_deleted
    
    async def ttl(self, key: str, retry_count: int=0) -> int:
        """
        Returns the number of seconds until the key will expire.
        :key: The key for which the TTL is to be retrieved.
        :retry_count: The number of times retrying the connection has been done.

        :returns: The TTL for the given key in seconds.
        """
        ttl = None

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(key=key, operation="TTL")
            
            # Getting the TTL for the give key
            self.logger.log_info(f"Getting TTL for key '{key}' from Redis.")
            start_time = DateUtil.current_milli_time()
            ttl = await rconn.ttl(key)
            self.logger.log_info(f"Successfully retrieved the TTL for key '{key}' from Redis.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation 'TTL' on key '{key}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation 'TTL' on key '{key}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                ttl = await self.ttl(key, retry_count+1)
        except Exception as ex:
            self.logger.log_error(f"Failed to get TTL for key '{key}' from Redis. Error: '{str(ex)}'.")
            raise

        return ttl
    
    async def keys(self, pattern: str) -> list:
        """
        Gets a list of keys matching the given pattern.
        :pattern: The pattern with which the keys are to be returned.

        :returns: The list of keys that match the pattern.
        """
        keys = list()

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(key=f"{pattern} (pattern, not key)", operation="KEYS")

            # Getting the list of keys with the given pattern
            start_time = DateUtil.current_milli_time()
            keys = await rconn.keys(pattern)
            self.logger.log_info(f"Successfully retrieved the keys with pattern '{pattern}' from Redis.", start_time=start_time)
        except Exception as ex:
            self.logger.log_error(f"Failed to get keys with pattern '{pattern}' from Redis. Error: '{str(ex)}'.")
            raise

        return keys
    
    async def register_script(self, script: str) -> callable:
        """
        Registers the given Lua script in Redis.
        :script: The Lua script.

        :returns: The `Script` object (callable).
        """
        script_method = None

        try:
            # Getting a connection to Redis
            rconn = await self._get_connection(operation="REGISTER_SCRIPT")
            
            # Getting the list of keys with the given pattern
            start_time = DateUtil.current_milli_time()
            script_method = rconn.register_script(script)
            self.logger.log_info("Successfully registered script in Redis.", start_time=start_time)
        except Exception as ex:
            self.logger.log_error(f"Failed to register script in Redis. Error: '{str(ex)}'.")
            raise

        return script_method
    
    async def lock_key(self, key: str, expire_time: int=None) -> bool:
        """
        Locks the given key to allow read-only operations.
        :key: The key to be locked.
        :expire_time: Number of seconds for the lock to expire automatically if not released.

        :returns: Boolean indicating whether lock was successfully acquired or not.
        """
        lock_ack = False

        try:
            if not self.enable_locking_keys:
                self.logger.log_warning(f"Not locking key '{key}' as locking is disabled via flag 'enable_locking_keys' being set to false.")
                return lock_ack
            
            # Generating the lock key
            lock_key = f"lock_{key}"
            
            # Getting a lock on the given key
            lock_ack = await self.set(
                key=lock_key,
                value="true",
                ex=expire_time,
                nx=True
            )

            if not lock_ack:
                # Lock already exists
                self.logger.log_info(f"Lock already exists for key '{key}, hence it cannot be acquired.'")
        except Exception as ex:
            self.logger.log_error(f"Failed to get lock on key '{key}' from Redis. Error: '{str(ex)}'.")
            raise

        return lock_ack
    
    async def unlock_key(self, key: str) -> bool:
        """
        Releases the lock on the given key.
        :key: The key on which the lock is to be released.

        :returns: True if lock was released successfully, False otherwise.
        """
        lock_released = False

        try:
            if not self.enable_locking_keys:
                self.logger.log_warning(f"Not unlocking key '{key}' as locking is disabled via flag 'enable_locking_keys' being set to false.")
                return
            
            # Generating the lock key
            lock_key = f"lock_{key}"

            # Deleting the lock key
            lock_released = await self.delete(key=lock_key)
        except Exception as ex:
            self.logger.log_error(f"Failed to release lock on key '{key}' from Redis. Error: '{str(ex)}'.")
            raise

        return lock_released
    
    async def block_lock(self, lock_name: str, lock_ttl: int=600, wait_interval: int=3) -> bool:
        """
        Blocks a lock with the given name for the given time, the method blocks the control till the time lock is present.
        :lock_name: The name of the lock to be acquired.
        :lock_ttl: The maximum time duration in seconds for which the lock would be acquired.
        :wait_interval: The number of seconds to wait between checks if lock is already acquired.

        :returns: True if lock was acquired successfully, False otherwise.
        """
        lock_ack = False

        try:
            # Getting the lock
            lock_ack = await self.set(
                key=lock_name,
                value="locked",
                ex=lock_ttl,
                nx=True
            )
            if lock_ack:
                # Lock acquired
                self.logger.log_info(f"Lock with name '{lock_name}' successfully acquired for at max '{lock_ttl}' seconds.")
            else:
                # Lock could not be acquired as it was already present
                lock_ack = False if lock_ack is None else lock_ack
                lock_ttl = await self.ttl(key=lock_name)
                self.logger.log_info(f"Lock with name '{lock_name}' already exists, hence cannot be acquired, waiting for the lock to be released till max '{lock_ttl}' seconds (TTL of the lock).")
                total_wait = 0
                while total_wait <= lock_ttl:
                    await asyncio.sleep(wait_interval)
                    total_wait += wait_interval
                    # Trying to get the lock
                    lock_ack = await self.set(
                        key=lock_name,
                        value="locked",
                        ex=lock_ttl,
                        nx=True
                    )
                    if lock_ack:
                        # Lock acquired
                        self.logger.log_info(f"Lock with name '{lock_name}' successfully acquired for at max '{lock_ttl}' seconds.")
                        break
                
                if not lock_ack:
                    # Lock could not be acquired
                    self.logger.log_error(f"Lock '{lock_name}' could not be acquired even after waiting for '{total_wait} seconds.'")
        except Exception as ex:
            self.logger.log_error(f"Failed to block lock with name '{lock_name}' in Redis. Error: '{str(ex)}'.")
            raise

        return lock_ack
    
    async def release_lock(self, lock_name: str) -> bool:
        """
        Releases the given lock.
        :lock_name: The lock to be released.

        :returns: True if lock was released successfully, False otherwise.
        """
        lock_released = False

        try:
            # Releasing the lock
            lock_released = await self.delete(lock_name)
        except Exception as ex:
            self.logger.log_error(f"Failed to release lock '{lock_name}'. Error: '{str(ex)}'.")
            raise

        return lock_released
    
    async def _get_connection(self, retry_count: int=0, key: str=None, operation: str=None) -> redis.Redis:
        """
        Creates and returns a connection to Redis.
        :retry_count: The number of times retrying the connection has been done.
        :key: The key for which the connection is being obtained. Used for logging purposes.
        :operation: The operation for which the connection is being obtained. Used for logging purposes.

        :returns: a connection object.
        """

        # Creating a connection to Redis
        self.logger.log_info(f"Getting a connection from the pool to Redis for operation '{operation}' on key '{key}'.")
        start_time = DateUtil.current_milli_time()
        try:
            rconn = redis.StrictRedis(connection_pool=self.conn_pool, socket_keepalive=True, health_check_interval=self.health_check_interval, retry_on_timeout=True)
            self.logger.log_info(f"Successfully got a connection from the pool to Redis for operation '{operation}' on key '{key}'.", start_time=start_time)
        except redis.ConnectionError as ce:
            if retry_count >= self.redis_connection_max_retry_count:
                self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation '{operation}' on key '{key}'. Error: '{str(ce)}'.")
                raise
            else:
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                self.logger.log_warning(f"Connection to redis failed due to error for operation '{operation}' on key '{key}': '{str(ce)}' will retry {retry_count + 1} time after sleeping for {time_to_sleep} seconds.")
                await asyncio.sleep(time_to_sleep)
                rconn = self._get_connection(retry_count=retry_count + 1, key=key, operation=operation)
        except Exception as ex:
            self.logger.log_error(f"Failed to get a connection from the pool to Redis for operation '{operation}' on key '{key}'. Error: '{str(ex)}'.")
            raise

        return rconn