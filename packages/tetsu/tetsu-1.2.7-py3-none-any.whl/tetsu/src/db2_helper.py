# DB2 Helper class

"""
This class will dynamically differentiate between ODBC and JDBC connections.
Please keep in mind that JDBC requires certain certificates for connection.
Please ensure that all your connection specifications are in-place before usage.

*** ---------------------- IMPORTANT ---------------------- ***
pip install ibm_db ibm_db_sa sqlalchemy
make sure you have the caroot.pem certificate and store in a local directory and listed in your config.yaml
download here: https://github.ibm.com/cognitive-data-platform/cognitive-data-platform/blob/master/cedp/access/certificates/carootcert.pem

THIS CLASS REQUIRES THE CLOUDANT HELPER SCRIPT TO ALSO BE PRESENT IN YOUR PROJECT WRKDIR.
CHANGE THE IMPORT STATEMENT AS NEEDED TO CORRECTLY IMPORT CLOUDANT_HELPER
"""
import ast
import jaydebeapi
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from tetsu.src import cloudant_helper
from tetsu.src.log_helper import logger

logger = logger(name=__name__, handler="console")


class DB2Helper:
    def __init__(
            self,
            environment: str,
            driver: str = "ODBC",
            creds: dict = None,
            cloudant_doc=None,
    ):
        """
        Initialization of the DB2Helper class

        :param cloudant_doc (optional): Name of the cloudant document to be retrieved
        :param creds (optional): A credentials dictionary can be optionally used to retrieve the desired DB2 credentials from the
                                 cloudant document and override the default values
                                 Example:
                                 {"username": ['staging', 'databases', 'db2', 'username'],
                                  "password": ['staging', 'databases', 'db2', 'password'],
                                  "hostname": ['staging', 'databases', 'db2', 'hostname'],
                                  "port": ['staging', 'databases', 'db2', 'port'],
                                  "database": ['staging', 'databases', 'db2', 'database']}
        :param driver: Type of connection. Can be 'ODBC' or 'JDBC'
        """

        self.type = driver
        if cloudant_doc is None:
            self.cloudant_doc = ast.literal_eval(os.getenv("cloudant_document"))
        else:
            self.cloudant_doc = cloudant_doc

        if creds is None:
            self.creds = {
                "username": [environment, "db2", "username"],
                "password": [environment, "db2", "password"],
                "hostname": [environment, "db2", "hostname"],
                "port": [environment, "db2", "port"],
                "database": [environment, "db2", "database"],
                "ssl": [environment, "db2", "ssl"],
                "trustpass": [environment, "db2", "trustpass"],
                "truststore": [environment, "db2", "truststore"],
            }
        else:
            self.creds = creds
        self.creds = cloudant_helper.get_credentials(
            doc=self.cloudant_doc, creds=self.creds
        )

        if driver not in ["ODBC", "JDBC"]:
            raise RuntimeError(
                "The type parameter only accepts 'ODBC' or 'JDBC' as values"
            )

    def __get_conn_odbc(self):
        """
        Connects to DB2 then creates an engine and ODBC connection to that space

        :return: sqlalchemy engine and that engine's connection
        """
        sqla_url_f = (
            f"db2+ibm_db://{self.creds['username']}:{self.creds['password']}@{self.creds['hostname']}:{self.creds['port']}"
            f"/{self.creds['database']};{self.creds['ssl']};{self.creds['trustpass']};{self.creds['truststore']};"
        )
        try:
            engine = create_engine(sqla_url_f, pool_size=10, max_overflow=20)
            conn = engine.connect()
        except SQLAlchemyError as se:
            logger.exception(f"Could not connect to DB2 due to {se}")
        else:
            return conn, engine

    def __get_conn_jdbc(self):
        """
        Connects to DB2 then creates an engine and ODBC connection to that space

        :return: See return statements from getConnODBC or getConnJDBC depending on init param

        As the connection is JDBC, it means it's Java based. If the code sends a Java Home error, make sure that the
        machine or container have Java installed and the JAVA_HOME environment variable set. You can use these instructions
        as reference.
        Instructions: PASTE THIS SEGMENT INTO DOCKERFILE
            RUN apt update -y && apt-get install -y software-properties-common && \
            apt-add-repository 'deb http://security.debian.org/debian-security stretch/updates main' && apt update -y && \
            apt-get install -y openjdk-11-jdk-headless && \
            export JAVA_HOME && \
            apt-get clean
        You also need to make sure that the machine and container have the jars in the correct folder, if those are missing,
        you can download them here: https://ibm.ent.box.com/folder/151153955031. Make sure you have the correct jar file,
        the 2 possible types are: type 2 -> dbn2jc.jar and type 4-> db2jcc4.jar

        - Also make sure you have the correct libraries installed such as: JayDeBeApi, ibm-db and ibm-db-sa
        - For security related issues while testing locally, check that you are connected to this VPN:
          sasvpn.pok.ibm.com/TUNNELALL
        """
        # Tweak this URL to mimic your actual JDBC URL. Not all DB2 connections require SSL
        try:
            conn = jaydebeapi.connect(
                jclassname="com.ibm.db2.jcc.DB2Driver",
                url=f"jdbc:db2://{self.creds['hostname']}:{self.creds['port']}/{self.creds['database']}:sslConnection=True;",
                driver_args={
                    "user": self.creds["username"],
                    "password": self.creds["password"],
                },
                jars=r"config/db2jcc.jar",
            )
        except SQLAlchemyError as se:
            logger.exception(f"Failed to initiate DB2 connection due to {se}")
        else:
            return conn

    def get_conn(self):
        if self.type == "ODBC":
            return self.__get_conn_odbc()
        else:
            return self.__get_conn_jdbc()

    def __update_credentials(self, creds: dict = None):
        self.creds = creds
        self.creds = cloudant_helper.get_credentials(
            doc=self.cloudant_doc, creds=self.creds
        )

    def update_conn(self, creds: dict = None):
        self.__update_credentials(creds=creds)
        self.get_conn()

    def db2_push(
            self,
            table_name: str = None,
            schema_name: str = None,
            df: pd.DataFrame = None,
            query: str = None,
    ):
        """
        Push data into a DB2 table

        :param table_name: Name of the DB2 table
        :param schema_name: Name of the schema the DB2 table exists in
        :param df: The pandas dataframe holding the data
        :param query: Query used to push the data into the table *** ONLY NEEDED WITH JDBC CONNECTIONS ***
        :return:
        """

        if self.type == "ODBC":
            if not table_name:
                raise RuntimeError(
                    "If the connection type is ODBC, you must populate the table_name parameter"
                )
            if not schema_name:
                raise RuntimeError(
                    "If the connection type is ODBC, you must populate the schema_name parameter"
                )
            if not df:
                raise RuntimeError(
                    "If the connection type is ODBC, you must populate the df parameter"
                )

            conn, engine = self.get_conn()

            df.to_sql(
                name=table_name,
                schema=schema_name,
                con=engine,
                if_exists="append",
                index=False,
            )

            conn.close()
        else:
            if not query:
                raise RuntimeError(
                    "If the connection type is JDBC, you must populate the query parameter"
                )
            self.run_query(query=query)

    def db2_pull(self, query: str):
        """
        Pull data from a DB2 table

        :param query: Query used to pull the data
        :return: A pandas dataframe holding the pulled data
        """
        data = self.run_query(query=query)
        return data

    def check_db2_push(self, query: str, data: pd.DataFrame) -> bool:
        """
        Checks if pushed data has been pushed correctly

        :param query: The query to pull the data from the DB2 table
        :param data: Pandas dataframe holding the current data that should be in the table

        :return: True or False
        """
        stored_db = self.db2_pull(query=query)
        return (data.merge(stored_db).drop_duplicates().shape == data.drop_duplicates().shape)

    def run_query(self, query: str):
        if self.type == "ODBC":
            conn, engine = self.get_conn()
        else:
            conn = self.get_conn()
        obj = pd.read_sql_query(sql=query, con=conn)
        conn.close()
        return obj
