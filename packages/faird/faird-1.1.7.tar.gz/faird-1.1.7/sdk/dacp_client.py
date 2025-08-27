from __future__ import annotations

from enum import Enum
from typing import Optional, List
from urllib.parse import urlparse
import pyarrow as pa
import pyarrow.flight
import json
import socket
from utils.logger_utils import get_logger
logger = get_logger(__name__)
import requests
from sdk.connection_pool import FlightConnectionPool, ConnectionManager


class DacpClient:
    def __init__(self, url: str, principal: Optional[Principal] = None):
        self.__url = url
        self.__principal = principal
        self.__token = None
        self.__connection_id = None

    @staticmethod
    def connect(url: str, principal: Optional[Principal] = None) -> DacpClient:
        client = DacpClient(url, principal)
        logger.info(f"Connecting to {url} with principal {principal}...")
        parsed = urlparse(url)
        host = f"grpc://{parsed.hostname}:{parsed.port}"
        ConnectionManager.set_connection_pool(FlightConnectionPool(host, max_connections=20))

        # 构建ticket
        try:
            client_ip = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            client_ip = "127.0.0.1"
        ticket = {
            'clientIp': client_ip
        }

        if principal:
            if principal.auth_type == AuthType.OAUTH:
                ticket.update({
                    'auth_type': principal.auth_type.value,
                    'type': principal.params.get('type'),
                    'username': principal.params.get('username'),
                    'password': principal.params.get('password')
                })
            elif principal.auth_type == AuthType.CONTROLD:
                ticket.update({
                    'auth_type': principal.auth_type.value,
                    'controld_domain_name': principal.params.get('controld_domain_name'),
                    'signature': principal.params.get('signature')
                })
            elif principal.auth_type == AuthType.ANONYMOUS:
                ticket.update({
                    'auth_type': principal.auth_type.value
                })

        # 发送连接请求
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("connect_server", json.dumps(ticket).encode('utf-8')))
            for res in results:
                res_json = json.loads(res.body.to_pybytes().decode('utf-8'))
                if res_json.get('errorMsg') != None:
                    logger.error(res_json.get('errorMsg'))
                    return None
                client.__token = res_json.get("token")
                client.__connection_id = res_json.get("connectionID")
            return client

    def list_datasets(self) -> List[str]:
        ticket = {
            'token': self.__token,
            'page': 1,
            'limit': 999999
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("list_datasets", json.dumps(ticket).encode('utf-8')))
            for res in results:
                res_json = json.loads(res.body.to_pybytes().decode('utf-8'))
                return res_json

    def get_dataset(self, dataset_name: str):
        ticket = {
            'token': self.__token,
            'dataset_name': dataset_name
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("get_dataset", json.dumps(ticket).encode('utf-8')))
            for res in results:
                res_json = json.loads(res.body.to_pybytes().decode('utf-8'))
                return res_json

    def list_dataframes(self, dataset_name: str) -> List[str]:
        ticket = {
            'token': self.__token,
            'username': self.__principal.params.get('username') if self.__principal and self.__principal.params else None,
            'dataset_name': dataset_name,
            'max_chunksize': 50000
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("list_dataframes", json.dumps(ticket).encode('utf-8')))
            dataframes = []
            for res in results:
                res_json = json.loads(res.body.to_pybytes().decode('utf-8'))
                dataframes.extend(res_json)
                print(f"Successfully fetch {len(dataframes)} dataframes")
            return dataframes

    def list_dataframes_stream(self, dataset_name: str, max_chunksize: Optional[int] = 50000):
        ticket = {
            'token': self.__token,
            'username': self.__principal.params.get('username') if self.__principal and self.__principal.params else None,
            'dataset_name': dataset_name,
            'max_chunksize': max_chunksize
        }
        with ConnectionManager.get_connection() as conn:
            reader = conn.do_action(pa.flight.Action("list_dataframes", json.dumps(ticket).encode('utf-8')))
            for chunk in reader:
                chunk_json = json.loads(chunk.body.to_pybytes().decode('utf-8'))
                print(f"Successfully fetch {len(chunk_json)} dataframes")
                yield chunk_json

    def list_user_auth_dataframes(self, username: str) -> List[str]:
        if username is None or username == "":
            logger.error("No username provided")
            return None
        ticket = {
            'username': username
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("list_user_auth_dataframes", json.dumps(ticket).encode('utf-8')))
            for res in results:
                res_json = json.loads(res.body.to_pybytes().decode('utf-8'))
                return res_json

    def check_permission(self, dataset_name: str, username: str) -> bool:
        ticket = {
            'dataset_name': dataset_name,
            'username': username
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("check_permission", json.dumps(ticket).encode('utf-8')))
            for res in results:
                res_str = res.body.to_pybytes().decode('utf-8')
                return res_str.lower() == 'true'

    def sample(self, dataframe_name: str):
        ticket = {
            'dataframe_name': dataframe_name,
            'connection_id': self.__connection_id
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("sample", json.dumps(ticket).encode('utf-8')))
            for res in results:
                return res.body.to_pybytes().decode('utf-8')

    def count(self, dataframe_name: str):
        ticket = {
            'dataframe_name': dataframe_name,
            'connection_id': self.__connection_id
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("count", json.dumps(ticket).encode('utf-8')))
            for res in results:
                return res.body.to_pybytes().decode('utf-8')

    def open(self, dataframe_name: str):
        from sdk.dataframe import DataFrame
        ticket = {
            'dataframe_name': dataframe_name,
            'connection_id': self.__connection_id
        }
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(pa.flight.Action("open", json.dumps(ticket).encode('utf-8')))
            return DataFrame(id=dataframe_name, connection_id=self.__connection_id)


    def get_ips(self) -> dict:
        public_ip = "0.0.0.0"
        private_ip = "127.0.0.1"

        # 获取公网IP
        try:
            response = requests.get('https://ifconfig.me/ip', timeout=5)
            response.raise_for_status()
            public_ip = response.text.strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取公网IP失败：{e}")

        # 获取内网IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            private_ip = s.getsockname()[0]
            s.close()
        except Exception as e:
            logger.error(f"获取内网IP失败：{e}")

        return {
            "public_ip": public_ip,
            "private_ip": private_ip
        }

    # mount 挂载时候 ，验证并获取 token 有效期
    def token_verification(self, dataframe_name: str, token: str, username: Optional[str] = None):
        if not username:
            username = self.__principal.params.get('username')
        ticket = {
            'dataframe_name': dataframe_name,
            'token': token,
            'username': username,
            'connection_id': self.__connection_id
        }
        # 验证令牌是否有效
        with ConnectionManager.get_connection() as conn:
            results = conn.do_action(
                pa.flight.Action("token_verification", json.dumps(ticket).encode('utf-8')))
            for res in results:
                result_json = json.loads(res.body.to_pybytes().decode('utf-8'))
                if (result_json.get('exists')):
                    deadline_str = result_json.get('deadline')
                    token_info = {
                        "exists": True,
                        'deadline': deadline_str
                    }
                    return token_info
                else:
                    error_msg = "Token验证失败：不存在或已过期"
                    error_info = {
                        "exists": False,
                        "msg": error_msg
                    }
                    return error_info
            return None

    def get_dataframe_stream(self, dataframe_name: str, token: str, max_chunksize: Optional[int] = 1024 * 1024 * 5
                             , username: Optional[str] = None , mount_timestamp: Optional[str] = None):
        if not token:
            raise ValueError("token is none")
        if not username :
            username = self.__principal.params.get('username')
        ips = self.get_ips()
        public_ip = ips['public_ip']
        private_ip = ips['private_ip']

        ticket = {
            'dataframe_name': dataframe_name,
            'token': token,
            'username': username,
            "public_ip": public_ip,
            "private_ip": private_ip,
            'max_chunksize': max_chunksize,
            'mount_timestamp': mount_timestamp,
            'connection_id': self.__connection_id
        }
        # 获取数据流
        with ConnectionManager.get_connection() as conn:
            stream_generator = conn.do_action(
                pa.flight.Action("get_dataframe_stream", json.dumps(ticket).encode('utf-8')))
            # 1. 尝试获取第一个数据块并检查其内容
            try:
                first_chunk = next(stream_generator)
                chunk_bytes = first_chunk.body.to_pybytes()
            except StopIteration:
                logger.error(f"数据获取失败: 没有数据可供获取")
                raise ValueError("数据获取失败: 没有数据可供获取")

            try:
                error_info = json.loads(chunk_bytes.decode('utf-8'))
                if 'status' in error_info and error_info['status'] == 'error' and error_info['code'] == 401:
                    logger.error(f"数据获取失败: {error_info['msg']}")
                    raise ValueError(error_info)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

            yield chunk_bytes
            for chunk in stream_generator:
                yield chunk.body.to_pybytes()

class AuthType(Enum):
    OAUTH = "oauth"
    CONTROLD = "controld"
    ANONYMOUS = "anonymous"

class Principal:
    ANONYMOUS = None

    def __init__(self, auth_type: AuthType, **kwargs):
        self.auth_type = auth_type
        self.params = kwargs

    @staticmethod
    def oauth(type: str,  **kwargs) -> Principal:
        return Principal(AuthType.OAUTH, type=type, **kwargs)

    @staticmethod
    def controld(domain_name: str, signature: str, **kwargs) -> Principal:
        return Principal(AuthType.CONTROLD, controld_domain_name=domain_name, signature=signature, **kwargs)

    @staticmethod
    def anonymous() -> Principal:
        return Principal(AuthType.ANONYMOUS)

    def __repr__(self):
        return f"Principal(auth_type={self.auth_type}, params={self.params})"

Principal.ANONYMOUS = Principal.anonymous()


