# 地铁换乘方案规划系统

这是一个基于Python实现的地铁换乘方案规划系统。该系统能够帮助用户找到从起点站到终点站的最优换乘路线。

## 功能特点

- 支持多条地铁线路的换乘规划
- 智能计算最短路径，避免不必要的换乘
- 优先考虑直达路线，减少换乘次数
- 清晰展示完整的换乘方案，包括具体换乘站点

## 使用说明

1. 确保系统中已安装Python环境
2. 运行`project.py`文件
3. 按照提示输入起点站和终点站
4. 系统将自动计算并显示最优换乘方案

## 实现原理

系统使用改进的Dijkstra算法实现路径规划，通过以下策略优化换乘方案：

- 优先考虑直达路线
- 避免不必要的换乘
- 计算最短路径时考虑换乘代价

## 注意事项

- 输入站点名称时请确保与系统中的站点名称完全匹配
- 系统会自动处理无效输入并提供相应提示 