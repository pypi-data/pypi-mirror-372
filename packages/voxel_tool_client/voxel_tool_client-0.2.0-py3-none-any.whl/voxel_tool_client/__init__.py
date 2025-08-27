import requests
import dataclasses
from typing import *

@dataclasses.dataclass()
class ClientConfig:
    base_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    stream: Optional[str] = None

@dataclasses.dataclass()
class Vector3:
    x: float
    y: float
    z: float

@dataclasses.dataclass()
class BaseResult():
    success: bool = False
    message: Optional[str] = None

@dataclasses.dataclass()
class ResultData:
    data: Optional[Any] = None
    error: Optional[str] = None

@dataclasses.dataclass()
class NpcFindingRequest():
    world_id: int

@dataclasses.dataclass()
class NpcFindingNpcInfo():
    npc_id: int
    npc_position: Vector3

@dataclasses.dataclass()
class NpcFindingResult(BaseResult):
    npc_data: Optional[List[NpcFindingNpcInfo]] = None

@dataclasses.dataclass()
class PathFindingRequest():
    world_id: int
    start: Vector3
    end: Vector3
    not_move: Optional[List[Vector3]] = None

@dataclasses.dataclass()
class PathFindingResult(BaseResult):
    path: Optional[List[Vector3]] = None


class VoxelClient:
    """
    用于访问体素化服务器的客户端, 创建时需要初始化ClientConfig。
    base_url为体素化服务器的地址, username和password为体素化服务器的用户名和密码。
    
    使用示例:
    ```python
    base_url = "http://127.0.0.1:8000" # 体素化服务器的地址
    username = "123456" # 体素化服务器的用户名
    password = "123456" # 体素化服务器的密码
    stream = "test" # 流
    world_id = 1 # 世界ID
    start = Vector3(x=0, y=0, z=0) # 起点坐标

    voxel_client = voxel_tool_client.VoxelClient(voxel_tool_client.ClientConfig(base_url=base_url, username=username, password=password, stream=stream))
    voxel_client.get_voxel_version()
    npc_data_result = voxel_client.find_npc(voxel_tool_client.NpcFindingRequest(world_id=world_id))
    if npc_data_result.success is True:
        for npc_info in npc_data_result.npc_data:
            print(f"NPC {npc_info.npc_id} 的坐标: {npc_info.npc_position}")
            path_result = voxel_client.find_path(voxel_tool_client.PathFindingRequest(world_id=world_id, start=start, end=npc_info.npc_position, not_move=[]))
            if path_result.success is True:
                print(f"NPC {npc_info.npc_id} 的路径规划成功: {npc_info.npc_position}")
            else:
                print(f"NPC {npc_info.npc_id} 的路径规划失败: {path_result.message}")
    ```
    """
    def __init__(self, config: ClientConfig):
        self.config = config

    def _get_default_config(self)-> Dict[str, Any]:
        return {
            "username": self.config.username,
            "password": self.config.password,
            "stream": self.config.stream,
        }

    def _do_request(self, sub_url: str, params: Dict[str, Any]) -> ResultData:
        try:
            data = {
                "config": self._get_default_config(),
                "data": params
            }
            url = f"{self.config.base_url}{sub_url}"
            response = requests.post(url, json=data)
            response.raise_for_status()
            return ResultData(
                data=response.json(),
                error=None
            )
        except requests.exceptions.RequestException as e:
            return ResultData(
                data=None,
                error=f"请求失败: {str(e)}"
            )
        
    def get_voxel_version(self) -> Optional[str]:
        """
        获取体素化服务器的版本号，版本号中带有日期，可看到是什么时候生成的数据。
        """
        sub_url = "/get_voxel_version/"
        result = self._do_request(sub_url, {})
        if result.error is not None:
            return None
        data_version = result.data
        if isinstance(data_version, str) is False or data_version == "":
            return None
        return data_version

    """
    路径规划, 从起点到终点, 返回路径。

    输入参数:
    world_id: 世界ID
    start: 起点坐标
    end: 终点坐标
    not_move: 不可移动的点(可选)

    输出参数:
    success: 是否成功
    message: 消息

    path: 从起点到终点的路径
    """
    def find_path(self, params: PathFindingRequest) -> PathFindingResult:
        data = dataclasses.asdict(params)
        sub_url = "/path_finding/"
        result = self._do_request(sub_url, data)
        if result.error is not None:
            return PathFindingResult(   
                success=False,
                message=result.error,
                path=None,
            )

        path = None
        data_success = result.data.get("success")
        data_path = result.data.get("path")
        data_message = result.data.get("message")
        if data_path is not None:
            path = []
            for data_position in data_path:
                path_position = Vector3(x=data_position["x"], y=data_position["y"], z=data_position["z"])
                path.append(path_position)
        
        return PathFindingResult(
            success=data_success,
            message=data_message,
            path=path,
        )

    def find_npc(self, params: NpcFindingRequest) -> NpcFindingResult:
        """
        获取NPC的坐标

        输入参数:
        world_id: 世界ID 
        
        输出参数:
        success: 是否成功
        message: 消息

        npc_data: NPC的信息
        """
        sub_url = "/get_npc_data/"
        result = self._do_request(sub_url, dataclasses.asdict(params))
        if result.error is not None:
            return NpcFindingResult(
                success=False,
                message=result.error,
                npc_data=None,
            )
        data_npc_data = result.data.get("npc_data")
        data_message = result.data.get("message")
        npc_data = None
        if data_npc_data is not None:
            npc_data = []
            for data_npc_info in data_npc_data:
                npc_id = data_npc_info["npc_id"]
                npc_position_object = data_npc_info["npc_position"]
                npc_position = Vector3(x=npc_position_object["x"], y=npc_position_object["y"], z=npc_position_object["z"])
                npc_data.append(NpcFindingNpcInfo(npc_id=npc_id, npc_position=npc_position))
        return NpcFindingResult(
            success=True,
            message=data_message,
            npc_data=npc_data,
        )