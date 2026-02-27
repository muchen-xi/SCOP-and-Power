# 空气源热泵供暖系统SCOP与能耗计算模型

本项目基于实测数据建立了空气源热泵的 COP 和制热量关于环境温度、出水温度的数学模型，并结合建筑热平衡原理，实现了供暖季季节能效比（SCOP）的计算。代码提供了两种确定建筑物总传热系数的方式（已知机组数量或已知建筑面积与耗热量指标），可灵活应用于不同场景。

## 功能特点
- 采用双二次多项式拟合制热量 \(P_{\text{hmax}}\)，R² 达 0.993 以上
- 采用二次线性多项式拟合 COP，R² 达 0.983
- 支持两种方式计算建筑物总传热系数 \(K\)（机组数法 / 面积法）
- 按月计算供热量、耗电量及 COP，自动累加供暖季总量
- 输出 SCOP 及各月详细数据，便于分析和验证

## 依赖环境
- Python 3.7+
- NumPy （推荐 1.20+）

## 安装
1. 确保已安装 Python 3.7 或更高版本。
2. 安装 NumPy：
   ```bash
   pip install numpy
将本项目代码保存为 scop_calculator.py（或任意命名）。

使用方法
基本调用
python
import numpy as np
from scop_calculator import calculate_scop

# 供暖季各月平均环境温度（11月~4月，单位℃）
env_temps = [-0.5, -1.2, -2.8, -1.5, 1.0, 5.5]
# 各月平均出水温度（℃）
out_temps = [42.0, 42.5, 43.0, 42.0, 41.0, 40.0]
# 各月天数（注意闰年2月可手动调整）
days_in_month = [30, 31, 31, 28, 31, 30]

# 方式1：已知机组数量（例如10台）
scop, details = calculate_scop(env_temps, out_temps, days_in_month,
                               n_units=10)

# 方式2：已知建筑面积与耗热量指标（例如1000 m²，25 W/m²）
scop, details = calculate_scop(env_temps, out_temps, days_in_month,
                               area=1000, q_H=25)

print(f"SCOP = {scop:.4f}")
参数说明
参数名	类型	必填	默认值	说明
env_temps_monthly	list[float]	是	-	供暖季各月平均环境温度（℃），顺序为11,12,1,2,3,4月
out_temps_monthly	list[float]	是	-	供暖季各月平均出水温度（℃），顺序同上
days_in_month	list[int]	是	-	供暖季各月天数，顺序同上
n_units	int	否*	None	热泵机组数量（与面积法二选一）
area	float	否*	None	建筑面积（m²），与 q_H 配合使用
q_H	float	否*	None	建筑耗热量指标（W/m²），与 area 配合使用
T_out_design	float	否	45	极寒设计工况下的出水温度（℃）
*注：必须提供 n_units 或同时提供 area 和 q_H，否则将引发异常。

返回值
函数返回一个元组 (SCOP, details)：

SCOP：浮点数，供暖季季节能效比

details：字典，包含以下字段：

K：建筑物总传热系数（kW/℃）

Q_total_kWh：供暖季总供热量（kWh）

P_total_kWh：供暖季总耗电量（kWh）

SCOP：同返回值

monthly：列表，每个元素为一个字典，包含各月详细数据：

month：月份名称（如"11月"）

T_menv：当月平均环境温度（℃）

T_mout：当月平均出水温度（℃）

days：当月天数

COP_m：当月平均 COP

Qm_kWh：当月总供热量（kWh）

Pm_kWh：当月总耗电量（kWh）

数学模型简述
COP 模型（来自论文拟合）
COP
=
0.00035510
 
T
env
2
+
0.0578
 
T
env
−
0.0637
 
T
out
+
6.0284
COP=0.00035510T 
env
2
​
 +0.0578T 
env
​
 −0.0637T 
out
​
 +6.0284
制热量模型（双二次多项式）
P
hmax
=
0.009111
 
T
env
2
+
5.736667
 
T
env
−
0.073627
 
T
out
2
+
4.822
 
T
out
+
214.022667
P 
hmax
​
 =0.009111T 
env
2
​
 +5.736667T 
env
​
 −0.073627T 
out
2
​
 +4.822T 
out
​
 +214.022667
建筑热平衡
极寒工况下，热泵满负荷输出满足：

n
⋅
P
hmax
=
K
⋅
(
20
−
(
−
7.2
)
)
⇒
K
=
n
⋅
P
hmax
27.2
n⋅P 
hmax
​
 =K⋅(20−(−7.2))⇒K= 
27.2
n⋅P 
hmax
​
 
​
 
或由面积法：

K
=
S
⋅
q
H
/
1000
27.2
K= 
27.2
S⋅q 
H
​
 /1000
​
 
月供热量：

Q
m
=
K
⋅
(
20
−
T
ˉ
env
,
m
)
⋅
t
m
Q 
m
​
 =K⋅(20− 
T
ˉ
  
env,m
​
 )⋅t 
m
​
 
月耗电量：

P
m
=
Q
m
/
COP
m
P 
m
​
 =Q 
m
​
 /COP 
m
​
 功耗作为中间量，可以直接从返回词典中收取
注意事项
环境温度低于 -7.2℃ 的情况在模型中不予考虑（依据供暖设计规范）。

若某月平均温度高于室内设计温度（20℃），该月供热量设为零。

各月天数应根据实际年份调整，2月可设定为28或29天。

许可证
本项目采用 MIT 许可证。详情请参阅 LICENSE 文件。

作者
晨曦

感谢山东方亚新能源集团提供数据支持。

贡献与反馈
欢迎通过 GitHub Issues 提交问题或建议。
