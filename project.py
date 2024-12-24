import csv
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Station:
    """
    表示地铁系统中的一个站点
    
    属性:
        id: 站点的唯一标识符
        line: 站点所属的线路名称
        name: 站点名称
        transfer_ids: 可换乘的其他站点ID列表
        prev: 同一线路上的前一个站点(可选)
        next: 同一线路上的后一个站点(可选)
    """
    id: int
    line: str 
    name: str
    transfer_ids: List[int] # 换乘站点的ID
    prev: Optional['Station'] = None  # 前一站点,默认为None
    next: Optional['Station'] = None  # 后一站点,默认为None

class SubwaySystem:
    """
    一个地铁换乘系统，它可以从一个 CSV 文件中加载站点信息，并提供一个方法来查找从一个站点到另一个站点的所有换乘路径。
    
    属性:
        stations: 存储所有站点的字典,key为站点ID,value为Station对象
        lines: 存储所有线路的字典,key为线路名称,value为该线路上所有站点的列表
    """
    
    def __init__(self):
        """
        初始化地铁换乘系统。
        创建两个空字典用于存储站点和线路信息。
        """
        self.stations: Dict[int, Station] = {}  # 存储所有站点
        self.lines: Dict[str, List[Station]] = {}  # 存储所有线路
        
    def load_from_csv(self, filename: str):
        """
        从一个 CSV 文件中加载站点信息，并将其加入到换乘系统中。
        
        处理步骤:
        1. 打开并读取CSV文件
        2. 跳过表头行
        3. 解析每一行数据:
           - 转换站点ID为整数
           - 获取线路名称
           - 获取站点名称
           - 处理换乘站点ID(如果存在)
        4. 创建Station对象并存储
        5. 建立同一线路站点之间的前后关系
        
        :param filename: CSV 文件的路径
        """
        with open(filename, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader) # 跳过表头
            
            # 逐行处理CSV数据
            for row in reader:
                station_id = int(row[0])
                line = row[1]
                name = row[2]
                # 处理换乘站点ID,如果存在则分割并转换为整数列表
                transfer_ids = [int(id) for id in row[3].split('/')] if row[3] else []
                
                # 创建新的Station对象
                station = Station(station_id, line, name, transfer_ids)
                self.stations[station_id] = station
                
                # 将站点添加到对应的线路列表中
                if line not in self.lines:
                    self.lines[line] = []
                self.lines[line].append(station)
        
        # 设置站点的前后关系
        for line_stations in self.lines.values():
            for i in range(len(line_stations)):
                # 设置前一站点(除第一个站点外)
                if i > 0:
                    line_stations[i].prev = line_stations[i-1]
                # 设置后一站点(除最后一个站点外)
                if i < len(line_stations) - 1:
                    line_stations[i].next = line_stations[i+1]
    
    def find_route(self, start_line: str, start_station: str, end_line: str, end_station: str) -> List[List[Tuple[Station, bool]]]:
        """
        查找从一个站点到另一个站点的所有换乘路径。
        
        :param start_line: 起点站的线路
        :param start_station: 起点站的名称
        :param end_line: 终点站的线路
        :param end_station: 终点站的名称
        :return: 一个列表，其中每个元素是一个换乘路径，换乘路径是一个列表，其中每个元素是一个元组，包含当前站点和是否需要换乘
        """
        # 找到起点和终点站
        start = next((s for s in self.lines[start_line] if s.name == start_station), None)
        end = next((s for s in self.lines[end_line] if s.name == end_station), None)
        
        if not start or not end:
            return []
            
        # 用于存储已访问的站点，避免重复访问形成环路
        visited: Set[int] = set()
        # 用于存储当前正在探索的路径
        current_path: List[Tuple[Station, bool]] = []
        # 用于存储所有找到的有效路径
        all_paths: List[List[Tuple[Station, bool]]] = []
        # 用于存储路径的唯一标识，防止重复路径
        path_signatures: Set[str] = set()
        
        def get_path_signature(path: List[Tuple[Station, bool]]) -> str:
            """
            获取当前路径的字符串表示，用于路径去重。
            连续出现两次相同站点ID是允许的（表示换乘），
            但连续出现三次或更多次相同站点ID时只保留两次。
            
            :param path: 当前路径
            :return: 路径的字符串表示，由站点ID组成
            """
            processed_ids: List[int] = []
            for station, _ in path:
                # 如果processed_ids长度小于2，或者当前站点与前两个站点不同，
                # 或者只与前一个站点相同，则添加
                if (len(processed_ids) < 2 or 
                    station.id != processed_ids[-1] or 
                    station.id != processed_ids[-2]):
                    processed_ids.append(station.id)
            return ','.join(str(id) for id in processed_ids)
        
        def dfs(current: Station, target: Station, is_transfer: bool = False):
            """
            使用深度优先搜索来查找换乘路径。
            
            :param current: 当前站点
            :param target: 目标站点
            :param is_transfer: 是否是换乘到当前站点
            """
            if current.id in visited:
                return
                
            visited.add(current.id)
            current_path.append((current, is_transfer))
            
            if current.id == target.id:
                path_sig = get_path_signature(current_path)
                if path_sig not in path_signatures:
                    path_signatures.add(path_sig)
                    all_paths.append(current_path[:])
            else:
                # 如果当前已经在目标线路上，只考虑同线路移动
                if current.line == target.line:
                    for next_station in [current.prev, current.next]:
                        if next_station and next_station.id not in visited:
                            dfs(next_station, target, False)
                else:
                    # 不在目标线路上时，优先考虑换乘到目标线路
                    target_line_transfers = []
                    other_transfers = []
                    
                    for transfer_id in current.transfer_ids:
                        transfer_station = self.stations[transfer_id]
                        if transfer_station.id not in visited:
                            if transfer_station.line == target.line:
                                target_line_transfers.append(transfer_station)
                            else:
                                other_transfers.append(transfer_station)
                    
                    # 优先探索通向目标线路的换乘站
                    if target_line_transfers:
                        for transfer_station in target_line_transfers:
                            dfs(transfer_station, target, True)
                    else:
                        # 如果没有通向目标线路的换乘站，则考虑其他选项
                        for transfer_station in other_transfers:
                            dfs(transfer_station, target, True)
                        
                        # 同一线路移动
                        for next_station in [current.prev, current.next]:
                            if next_station and next_station.id not in visited:
                                dfs(next_station, target, False)
            
            current_path.pop()
            visited.remove(current.id)
        
        # 开始搜索路径
        dfs(start, end)
        return all_paths

def main():
    subway = SubwaySystem()
    subway.load_from_csv("线路.csv")
    
    print("欢迎使用地铁换乘查询系统")
    print("请按照以下格式输入起点和终点：")
    print("线路名，站名-线路名，站名")
    print("例如：18号线，复旦大学-10号线，交通大学")
    
    while True:
        try:
            print("\n请输入线路信息：")
            route_info = input().strip()
            
            # 分割起点和终点信息
            if '-' not in route_info:
                print("错误：格式不正确，请使用'-'分隔起点和终点")
                continue
                
            start_info, end_info = [x.strip() for x in route_info.split('-')]
            
            # 处理起点信息
            start_info = start_info.replace('，', ',')
            if ',' not in start_info:
                print("错误：起点格式不正确，请使用逗号分隔线路名和站名")
                continue
            start_line, start_station = [x.strip() for x in start_info.split(',')]
            
            # 处理终点信息
            end_info = end_info.replace('，', ',')
            if ',' not in end_info:
                print("错误：终点格式不正确，请使用逗号分隔线路名和站名")
                continue
            end_line, end_station = [x.strip() for x in end_info.split(',')]
            
            # 验证线路是否存在
            if start_line not in subway.lines:
                print(f"错误：未找到线路 '{start_line}'")
                continue
            if end_line not in subway.lines:
                print(f"错误：未找到线路 '{end_line}'")
                continue
            
            # 验证站点是否存在
            if not any(s.name == start_station for s in subway.lines[start_line]):
                print(f"错误：在 {start_line} 上未找到站点 '{start_station}'")
                continue
            if not any(s.name == end_station for s in subway.lines[end_line]):
                print(f"错误：在 {end_line} 上未找到站点 '{end_station}'")
                continue
            
            routes = subway.find_route(start_line, start_station, end_line, end_station)
            
            if routes:
                print("\n路线规划：")
                for i, route in enumerate(routes):
                    print(f"\n 路线 {i+1}：")
                    for station, is_transfer in route:
                        if is_transfer:
                            print("换乘")
                        print(f"{station.line}，{station.name}")
            else:
                print("未找到可行路线")
                
            # 询问是否继续
            if input("\n是否继续查询？(y/n): ").lower() != 'y':
                break
                
        except Exception as e:
            print(f"发生错误：{str(e)}")
            print("请重新输入\n")

if __name__ == "__main__":
    main()
