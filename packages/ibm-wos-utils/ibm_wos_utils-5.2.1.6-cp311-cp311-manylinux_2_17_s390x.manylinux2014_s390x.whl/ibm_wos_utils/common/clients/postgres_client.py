# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

"""
Contains the client class to have any/all the communications with Postgres.
"""

import psycopg2
import psycopg2.pool
import psycopg2.extras
import random
import time
import pandas as pd
from psycopg2 import sql

from ibm_wos_utils.common.utils.common_logger import CommonLogger
from ibm_wos_utils.common.utils.date_util import DateUtil

COUNT_TABLE_ROWS = u'SELECT COUNT(*) FROM {}.{}'
GET_TABLE_ROWS_WITH_ALL_COLUMNS = u'SELECT * FROM "{}"."{}" LIMIT {}'
GET_TABLE_ROWS_WITH_SELECTED_COLUMNS = u'SELECT {} FROM "{}"."{}" LIMIT {}'

class PostgresClient:

    def __init__(
            self,
            hostname: str,
            port: str,
            dbname: str,
            username: str,
            password: str,
            sslmode: str="prefer",
            ssl_cert_path: str=None,
            min_connections: int=1,
            max_connections: int=10,
            postgres_connection_max_retry_count: int=10,
            logger=None,
            **kwargs
        ):
        """
        Initializes the object with credentials.
        :hostname: The Postgres host URL.
        :port: The port at which Postgres DB is hosted.
        :dbname: The DB to be accessed in the Postgres instance.
        :username: The user name for authentication.
        :password: The password for authentication.
        :sslmode: The ssl mode used by Postgres for verification.
        :sslrootcert: The path to the decoded ssl certificate
        :max_connections: Defines the minnimum connections to be created in the pool.
        :max_connections: Defines the maximum connections to be created in the pool.
        :postgres_connection_max_retry_count: The maximum number of retries to be done for a connection in case getting one fails.
        :logger: The logger object to be used to log messages. [If not given, common logger would be used.]
        """
        self.__hostname = hostname
        self.__port = port
        self.__dbname = dbname
        self.__username = username
        self.__password= password
        self.__sslmode = sslmode
        self.__ssl_cert_path = ssl_cert_path
        self.__min_connections = min_connections
        self.__max_connections = max_connections
        # Initializing logger
        self.logger = logger if logger is not None else CommonLogger(__name__)
        self.postgres_connection_max_retry_count = postgres_connection_max_retry_count

        # Creating a connection pool

        self.conn_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=min_connections, 
            maxconn=max_connections, 
            user=self.__username,
            password=self.__password,
            host=self.__hostname,
            port=self.__port,
            database=self.__dbname,
            sslmode=self.__sslmode,
            sslrootcert=self.__ssl_cert_path
        )

    def count_rows(self, schema_name: str, table_name:str) -> int:
        """
        Returns the number of records found in the table.
        :schema_name: The name of the schema in which the table resides.
        :table_name: The table from which the record count is to be fetched.

        :returns: The number of rows present in the table.
        """
        count = 0
        try:
            start_time = DateUtil.current_milli_time()

            self.logger.log_info('Counting rows in the table {} from schema {}'.format(table_name, schema_name))
            # Running query to fetch number of records in the table
            count = self._execute(COUNT_TABLE_ROWS, schema_name, table_name, return_rows=True)
            self.logger.log_info("Successfully fetched the count of rows in table {} from schema {}".format(table_name, schema_name), start_time=start_time)

            if len(count)>0:
                if len(count[0])>0:
                    count = int(count[0][0])
            
        except Exception as ex:
            self.logger.log_error("Failed to fetch the count of rows in the table {} from schema {}. ERROR: {}".format(table_name, schema_name, ex))
            raise

        return count


    def insert_data(self, schema_name: str, table_name: str, data: pd.DataFrame, page_size: int=100, retry_count: int=0) -> bool:
        """
        Adds data to the given table in the given schema.
        :schema_name: The name of the schema in which the table resides.
        :table_name: The table in which the data needs to be added.
        :data: The dataframe which contains the records to be added.
        :page_size: Maximum number of arglist items to include in every statement.
        :retry_count: The number of times retrying the connection has been done.

        :returns: True, if data was added successfully, False otherwise.
        """
        data_added = False
        self.logger.log_info("Adding data to the table {} in schema {}. Attempt: {}".format(table_name, schema_name, retry_count+1))
        try:
            start_time = DateUtil.current_milli_time()
            cursor = None
            connection = None
            # Fetching a connection from the connection pool
            connection = self._get_connection()

            # Fetching column names and converting the dataframe rows into tuples
            df_columns = list(data)
            df_rows = list(data.itertuples(index=False, name=None))
            columns = ",".join(df_columns)
            insert_stmt = 'INSERT INTO "{}"."{}" ({}) VALUES %s'.format(schema_name, table_name, columns)

            # Creating a cursor
            cursor = connection.cursor()
            psycopg2.extras.execute_values(cursor, insert_stmt, df_rows, page_size=page_size)
            # Commiting the query
            connection.commit()

            self.logger.log_info("Data stored successfully in table {} present in schem {}.".format(table_name, schema_name), start_time=start_time)
            data_added=True

        except Exception as ex:
            # Check if the connection is closed or severed from server side
            if not self._is_connection_alive(connection=connection):
                if retry_count==self.postgres_connection_max_retry_count:
                    self.logger.log_error('Failed to get a postgres connection from the connection pool after {} retries. ERROR: {}'.format(self.postgres_connection_max_retry_count+1, e))
                    raise
                
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (retry_count + 1) + random.randint(0, 10)
                time.sleep(time_to_sleep)

                self.logger.log_warning('Postgress connection error while fetching new connection from connection pool and executing query (attempt: {}). Will retry {} time after sleeping for {} seconds.'.format(attempt, attempt + 1, time_to_sleep))
                # If yes, create a new connection and add to connection pool
                self._create_new_connection()

                # Recursion with retry_count + 1 to retry the operation
                self.insert_data(schema_name=schema_name, table_name=table_name, data=data, page_size=page_size, retry_count=retry_count+1)
            else:
                # If connection is alive, throw error
                self.logger.log_error("Failed to upload data into the the table {} in schema {}. ERROR: {}".format(table_name, schema_name, ex))

                raise

        finally:
            self.logger.log_info("Closing the cursor and putting connection back into the pool")
            if cursor:
                # Closing the cursor
                cursor.close()
            if connection:
                # Putting the connection used back into the connection pool
                self.conn_pool._putconn(connection)

        return data_added


    def read_data(self, schema_name: str, table_name: str, limit: int=1000, columns: list=None) -> pd.DataFrame:
        """
        Reads data from the given table in the given schema.
        :schema_name: The name of the schema in which the table resides.
        :table_name: The table from which the data needs to be read.
        :limit: The number of rows to be read from the table.
        :columns: The list of columns to be read from the table, if None, all are returned.

        :returns: The data in a pandas data-frame.
        """
        self.logger.log_info("Fetching the first {} records from table {} in schema {}.".format(limit, table_name, schema_name))
        data_df = None
        try:
            if not columns:
                start_time = DateUtil.current_milli_time()

                # Running query to fetch all the columns from the table
                data = self._execute(GET_TABLE_ROWS_WITH_ALL_COLUMNS, schema_name, table_name, limit, return_rows=True, return_description=True, params_as_identifiers=False)
                self.logger.log_info("Successfully fetched data tuples from table {} in schema {}.".format(table_name, schema_name))

                # Extracting column names from cursor description
                description_columns = data.pop(0)
                columns = [col[0] for col in description_columns]

                # Creating the dataframe to be returned with the columns and data fetched by query
                data_df = pd.DataFrame(data, columns=columns)

                row_count_fetched = len(data_df)
                self.logger.log_info("Successfully fetched first {} records from table {} in schema {} and converted to pandas datafram.".format(row_count_fetched, table_name, schema_name), start_time=start_time)

            else:
                start_time = DateUtil.current_milli_time()
                self.logger.log_debug("List of column names found. Fetching data for the given columns.")

                column_names = ", ".join(columns)

                # Running query to fetch only the specified columns from the table
                data = self._execute(GET_TABLE_ROWS_WITH_SELECTED_COLUMNS, column_names, schema_name, table_name, limit, return_rows=True, params_as_identifiers=False)
                self.logger.log_info("Successfully fetched data tuples from table {} in schema {}.".format(table_name, schema_name))

                # Creating the dataframe to be returned with the columns provided and data fetched by query
                data_df = pd.DataFrame(data, columns=columns)
                self.logger.log_info("Successfully fetched first {} records from table {} in schema {} and converted to pandas datafram.".format(limit, table_name, schema_name), start_time=start_time)

        except Exception as ex:
            self.logger.log_error("Failed to fetch the first {} records from table {} in schema {}. ERROR: {}".format(limit, table_name, schema_name, ex))
            raise

        return data_df

    def run_sql(self, sql_query: str, return_rows: bool=True) -> pd.DataFrame:
        """
        Runs the given SQL query.
        :sql_query: The SQL query to be executed.
        :return_rows: Boolean flag to request for output if needed.

        :returns: The result set returned via the query in a pandas data-frame.
        """
        self.logger.log_info("Starting run for custom query.")
        try:
            start_time = DateUtil.current_milli_time()
            data_df = None

            # Executing the custom query provided
            data = self._execute(sql_query, return_rows=return_rows, params_as_identifiers=False)

            # Creating the dataframe to be returned with the data fetched by the query
            data_df = pd.DataFrame(data)
            self.logger.log_info("Successfully completed execution of custom query.", start_time=start_time)
            
        except Exception as ex:
            self.logger.log_error("Execution of custom query failed. ERROR: {}".format(ex))
            raise

        return data_df
    
    def close_connection_pool(self) -> bool:
        """
        Function to close all connections in connection pool.

        :returns: True if closed successfully, else False.
        """
        is_conn_pool_closed = False
        try:
            start_time = DateUtil.current_milli_time()
            self.logger.log_info("Attempting to close connection pool")
            
            while len(self.conn_pool._pool) > 0:
                connection = self._get_connection()

                self.logger.log_info("Closing fetched connection")
                self.conn_pool._putconn(connection, close=True)

            self.conn_pool._closeall()
            
            is_conn_pool_closed = True
            self.logger.log_info("Connection pool closed successfully" ,start_time=start_time)
        except Exception as ex:
            self.logger.log_error("Failed to close the connection pool. ERROR: {}".format(ex))
            raise

        return is_conn_pool_closed

    def _is_connection_alive(self, connection: psycopg2.extensions.connection) -> bool:
        """
        Function to check if a connection is alive. Returns True if the connection works else closes the connection, removes it from the connection pool and returns False.
        :connection: Postgres connection fetched from pool.

        :returns: True if connection is alive, else False.
        """
        is_conn_alive = False

        self.logger.log_info("Verifying if connection is alive")
        try:
            # Checking if the connection is alive
            connection.isolation_level
            self.logger.log_info("Connection is alive")
            is_conn_alive = True
        except psycopg2.OperationalError as e:
            self.logger.log_error("The connection is either closed or severed from server side. Closing and removing from pool")
            # Closing the server side closed connection and removing from pool
            self.conn_pool._putconn(connection, close=True)
        
        return is_conn_alive
    
    def _create_new_connection(self) -> None:
        """
        Function to create and add a new connection to the connection pool.

        :returns: None.
        """
        self.logger.log_info("Creating a new connection and adding to the connection pool")
        if len(self.conn_pool._pool) < self.__max_connections:
            # Creating a new connection and storing back in the connection pool
            self.conn_pool._connect()
        
        return None

    def _get_connection(self) -> psycopg2.extensions.connection:
        """
        Function to fetch a return a connection from the connection pool.

        :returns: The fetched connection.
        """
        connection = None
        for attempt in range(0, self.postgres_connection_max_retry_count):
            try:
                self.logger.log_info("Fetching a connection from the connection pool, attempt: {}".format(attempt+1))
                connection = self.conn_pool._getconn()
                self.logger.log_info("Successfully fetched a connection from connection pool")
                break

            except psycopg2.pool.PoolError as e:
                if attempt==self.postgres_connection_max_retry_count:
                    self.logger.log_error('Failed to get a postgres connection from the connection pool after {} retries. ERROR: {}'.format(self.postgres_connection_max_retry_count+1, e))
                    raise
                
                # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                time_to_sleep = 2 ** (attempt + 1) + random.randint(0, 10)
                time.sleep(time_to_sleep)
                self.logger.log_warning('Postgress connection error while fetching new connection from connection pool and executing query (attempt: {}). Will retry {} time after sleeping for {} seconds.'.format(attempt, attempt + 1, time_to_sleep))

            except Exception as ex:
                self.logger.log_error("Failed to get a postgres connection from the connection pool. ERROR: {}".format(ex))
                raise
        
        return connection

    def _cursor_execute(self, connection: psycopg2.extensions.connection, query: str, *params, return_rows: bool=False, return_description: bool=False, params_as_identifiers: bool=True):
        """
        Function to create a cursor and execute a query with parameters and return output fetched by cursor.
        :connection: Postgres connection fetched from pool.
        :query: The query statement to be executed.
        :*params: The parameters needed to complete query.
        :return_rows: Boolean flag to request for output if needed.
        :return_description: Boolean flag to request for the description of the output fetched by cursor.
        :params_as_identifiers: Boolean flag to use the params as SQL identifiers if passed as true else, it uses the parameters as they are passed.

        :returns: Output fetched by the cursor if 'return_rows' is True.
        """
        with connection:
            # Creating a cursor for the connection
            with connection.cursor() as cursor:
                param_list = []
                if params:
                    # If params are non-string values, set final query with the values directly
                    if not params_as_identifiers:
                        final_query = query.format(*params)
                    # If params are string values, convert to sql identifiers
                    else:
                        for param in params:
                            param_list.append(sql.Identifier(param))
                        final_query = sql.SQL(query).format(*param_list)
                else:
                    final_query = query
                
                # Executing the final query
                cursor.execute(final_query)
                resp = []

                # Returning description of cursor if return_description is True
                if return_description:
                    try:
                        resp.append(cursor.description)
                        if not return_rows:
                            return resp
                    except Exception as ex:
                        error_msg = "Failed to fetch cursor description for the executed query. ERROR: {}".format(ex)
                        self.logger.log_error(error_msg)
                        raise
                
                # Returning the output of the query, if return_rows is True
                if return_rows:
                    try:
                        rows = cursor.fetchall()
                        resp+=rows
                        return resp
                    except Exception as ex:
                        error_msg = "Failed to fetch results for the executed query. ERROR: {}".format(ex)
                        self.logger.log_error(error_msg)
                        raise
                
        return

    def _execute(self, query: str, *params, return_rows: bool=False, return_description: bool=False, params_as_identifiers: bool=True):
        """
        Function to execute query with retries.
        :query: The query statement to be executed.
        :*params: The parameters needed to complete query.
        :return_rows: Boolean flag to request for output if needed.
        :return_description: Boolean flag to request for the description of the output fetched by cursor.
        :params_as_identifiers: Boolean flag to use the params as SQL identifiers if passed as true else, it uses the parameters as they are passed.

        :returns: Output of the `_cursor_execute` function when successful.
        """
        for attempt in range(0, self.postgres_connection_max_retry_count):
            try:
                connection = None
                # Fetching a connection from the connection pool
                connection = self._get_connection()

                # Executing the query with the connection fetched from the pool
                response = self._cursor_execute(connection, query, *params, return_rows=return_rows, return_description=return_description, params_as_identifiers=params_as_identifiers)

                return response

            except Exception as ex:
                # Check if the connection is closed or severed from server side
                if not self._is_connection_alive(connection=connection):
                    if attempt==self.postgres_connection_max_retry_count:
                        self.logger.log_error('Failed to get a postgres connection from the connection pool after {} retries. ERROR: {}'.format(self.postgres_connection_max_retry_count+1, e))
                        raise
                    
                    # Doing binary exponential backoff for retrying with a random buffer time so that not all threads retry at the same time
                    time_to_sleep = 2 ** (attempt + 1) + random.randint(0, 10)
                    time.sleep(time_to_sleep)

                    self.logger.log_warning('Postgress connection error while fetching new connection from connection pool and executing query (attempt: {}). Will retry {} time after sleeping for {} seconds.'.format(attempt, attempt + 1, time_to_sleep))
                    # If yes, create a new connection and add to connection pool
                    self._create_new_connection()
                else:
                    # If connection is alive, throw error
                    self.logger.log_error('Failed to perform operation on the PostgresDB. ERROR: {}'.format(ex))
                    raise

            finally:
                if connection:
                    # Putting the connection used back into the connection pool
                    self.conn_pool._putconn(connection)

        return
