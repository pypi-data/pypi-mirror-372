import warnings

from IPython.display import display, HTML
from IPython.core.magic import (
    Magics,
    magics_class,
    line_cell_magic,
)
from IPython import get_ipython

import json
import base64
import pickle
import time
from requests import HTTPError
import pandas

from ..agent_client.agent_client import AGClient
from ..utils.error_print import eprint
from .errors import AGRuntimeError
from ..config.config import config

@magics_class
class AGMagic(Magics):
    """
    Provides %%ag cell magic and private python code execution on Antigranular server
    """

    session_id: str
    # user_name: str
    ag_server: AGClient = None
    sql_server = None


    @classmethod
    def load_oblv_client(cls, ag_server=None, session_id=None, sql_server=None):
        if ag_server:
            cls.ag_server = ag_server
        if session_id:
            cls.session_id = session_id
        if sql_server:
            cls.sql_server = sql_server
        # cls.user_name = user_name

    @line_cell_magic
    def ag(self, line, cell=None):
        """
        Executes the provided code on the Antigranular server.

        Parameters:
            line (str): The code in a single line.
            cell (str): The code in a cell format.

        Returns:
            None
        """
        if cell is None:
            print("Please call ag as a cell magic using '%%ag'")
            return
        else:
            if not self.ag_server:
                eprint("You are not logged in to Antigranular server, please login using login method")
                return
            try:
                self.execute(cell, 'ag')
            # except any exception
            except KeyboardInterrupt:
                res = self.interrupt_kernel()
                if res["status"] == "ok":
                    # return interrupt message
                    eprint("Kernel interrupted successfully")
                else:
                    eprint("Error while interrupting kernel")
                    eprint(res)
    @staticmethod
    def safe_to_numeric(series):
        try:
            return pandas.to_numeric(series)
        except (ValueError, TypeError):
            return series

    @line_cell_magic
    def sql(self, line, cell=None):
        """
        Executes the sql code on the Antigranular server.

        Parameters:
            line (str): The code in a single line.
            cell (str): The code in a cell format.

        Returns:
            None
        """
        if cell is None:
            print("Please call sql as a cell magic using '%%sql'")
            return
        else:
            if not self.sql_server:
                eprint("You are not logged in to SQL server, please login using login_sql method")
                return
            try:
                var_name = "sql_results_df"
                if line:
                    # Check if line is a valid variable name
                    if line.isidentifier():
                        var_name = line
                    else:
                        warnings.warn("The given variable name is not valid, using default name 'sql_results_df' instead")
                else:
                    warnings.warn("No variable name provided, using default name 'sql_results_df' instead")
                result_set = self.sql_server.execute(cell)
                num_rows = len(result_set)-1
                print(f"Execution successful, {num_rows} rows returned")
                print("Preview:")
                df = pandas.DataFrame(result_set[1:], columns=result_set[0])

                df = df.apply(AGMagic.safe_to_numeric).convert_dtypes()
                    
                print(df.head(5))
                user_ns = get_ipython().user_ns
                user_ns[var_name] = df
                print(f"Exported results dataframe into local variable '{var_name}'")


            # except any exception
            except KeyboardInterrupt:
                res = self.interrupt_kernel()
                if res["status"] == "ok":
                    # return interrupt message
                    eprint("Kernel interrupted successfully")
                else:
                    eprint("Error while interrupting kernel")
                    eprint(res)
            except Exception as e:
                eprint(f"Error while executing sql: {str(e)}")


    def execute(self, code: str, code_type: str):
        """
        Executes the code on the Antigranular server.

        Parameters:
            code (str): The code to be executed.

        Returns:
            None
        """
        path = "/sessions/execute" if code_type == 'ag' else "/execute_sql"
        url = f"{self.ag_server.url}:{self.ag_server.port}" if code_type == 'ag' else config.AGENT_SQL_SERVER_URL
        try:
            res = self.ag_server.post(
                f"{url}{path}",
                json={"session_id": self.session_id, "code": code},
            )
        except Exception as err:
            raise ConnectionError(f"Error calling /execute: {str(err)}")
        else:
            if res.status_code != 200:
                raise HTTPError(
                    f"Error while requesting AG server to execute the code, HTTP status code: {res.status_code}, message: {res.text}"
                )
            res_body_dict = json.loads(res.text)
            if code_type == 'sql':
                print(res_body_dict)
            else:
                self.get_output(res_body_dict.get('message_id'))

    def interrupt_kernel(self) -> dict:
        try:
            res = self.ag_server.post(
                f"{self.ag_server.url}:{self.ag_server.port}/sessions/interrupt-kernel",
                json={"session_id": self.session_id},
            )
        except Exception as err:
            raise ConnectionError(
                f"Error calling /sessions/interrupt-kernel: {str(err)}"
            )
        else:
            if res.status_code != 200:
                raise HTTPError(
                    f"Error while requesting AG server to interrupt the kernel, HTTP status code: {res.status_code}, message: {res.text}"
                )
            return json.loads(res.text)

    def get_output(self, message_id):
        """
        Retrieves the code execution output from the Antigranular server.
        """
        count = 1

        while True:
            if count > int(config.AG_EXEC_TIMEOUT):
                eprint("Error : AG execution timeout.")
                break
            try:
                res = self.ag_server.get(
                    f"{self.ag_server.url}:{self.ag_server.port}/sessions/output",
                    params={"session_id": self.session_id},
                )
            except Exception as err:
                raise ConnectionError(
                    f"Error during code execution on AG Server: {str(err)}"
                )
            if res.status_code != 200:
                raise HTTPError(
                    f"Error while requesting AG server for output, HTTP status code: {res.status_code}, message: {res.text}"
                )
            kernel_messages = json.loads(res.text)["output_list"]
            for message in kernel_messages:
                if message.get("parent_header", {}).get("msg_id") == message_id:
                    if message["msg_type"] == "status":
                        if message["content"]["execution_state"] == "idle":
                            return
                    elif message["msg_type"] == "stream":
                        if message["content"]["name"] == "stdout":
                            print(message["content"]["text"])
                        elif message["content"]["name"] == "stderr":
                            eprint(message["content"]["text"])

                    elif message["msg_type"] == "error":
                        tb_str = ""
                        for tb in message["content"]["traceback"]:
                            tb_str += tb

                        print(tb_str)
                        raise AGRuntimeError(
                            etype=str(message["content"]["evalue"]),
                            evalue="RuntimeError",
                            msg=tb_str,
                        )

                    elif message["msg_type"] == "ag_export_value":
                        try:
                            user_ns = get_ipython().user_ns
                            data = message["content"]
                            for name, value in data.items():
                                user_ns[name] = pickle.loads(base64.b64decode(value))
                                print(
                                    "Setting up exported variable in local environment:",
                                    name,
                                )

                        except Exception as err:
                            raise ValueError(
                                f"Error while parsing export values message: {str(err)}"
                            )
            time.sleep(1)
            count += 1

    @staticmethod
    def load_ag_magic():
        """
        Loads the AGMagic class as a magic in the IPython session.
        """
        ipython = get_ipython()
        if ipython is None:
            raise RuntimeError(
                "This function can only be called from an IPython session"
            )
        ipython.register_magics(AGMagic)

