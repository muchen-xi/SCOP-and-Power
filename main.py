import numpy as np

def calculate_scop(env_temps_monthly, out_temps_monthly, days_in_month,
                   n_units=None, area=None, q_H=None, T_out_design=45):
    """
    计算空气源热泵供暖季的季节能效比 SCOP

    参数：
        env_temps_monthly : list, 供暖季各月平均环境温度 (℃)，顺序为11,12,1,2,3,4月
        out_temps_monthly : list, 供暖季各月平均出水温度 (℃)，顺序同上
        days_in_month     : list, 供暖季各月天数，顺序同上
        n_units           : int, 热泵机组数量 (可选，与面积法二选一)
        area              : float, 建筑面积 (m²) (可选，与n_units二选一)
        q_H               : float, 建筑耗热量指标 (W/m²) (与面积配合使用)
        T_out_design      : float, 极寒设计工况下的出水温度 (℃)，默认45℃

    返回：
        SCOP : float, 季节能效比
        details : dict, 包含各月耗热量、耗电量、总供热量、总耗电量的详细信息
    """
    # 设计参数
    T_design = -7.2          # 青岛供暖室外计算温度 ℃
    T_room = 20.0            # 室内设计温度 ℃
    delta_T_max = T_room - T_design  # 27.2 ℃

    # 1. 计算极寒设计工况下机组的最大制热功率 P_hmax_design (kW)
    a1, b1, c1, d1, e1 = 0.009111, 5.736667, -0.073627, 4.822, 214.022667
    P_hmax_design = (a1 * T_design**2 + b1 * T_design +
                     c1 * T_out_design**2 + d1 * T_out_design + e1)

    # 2. 确定建筑物的总传热系数 K (kW/℃)
    if n_units is not None:
        K = n_units * P_hmax_design / delta_T_max
        method = "机组数法"
    elif area is not None and q_H is not None:
        # 极寒工况下最大热负荷 Qmax (kW) = 面积 * 耗热量指标 / 1000
        Qmax_kW = area * q_H / 1000.0
        K = Qmax_kW / delta_T_max
        method = "面积法"
    else:
        raise ValueError("必须提供 n_units（机组数）或 (area 和 q_H) 中的一组参数。")

    print(f"使用 {method} 计算 K = {K:.6f} kW/℃")

    # 3. 初始化累计值
    Q_total = 0.0   # 总供热量 (kWh)
    P_total = 0.0   # 总耗电量 (kWh)
    monthly_data = []  # 存储各月详细数据

    # 4. 对供暖季各月循环
    for i, (T_menv, T_mout, days) in enumerate(zip(env_temps_monthly, out_temps_monthly, days_in_month)):
        month_name = ["11月", "12月", "1月", "2月", "3月", "4月"][i]
        t_m = days * 24.0  # 当月运行小时数

        # 当月平均 COP
        a, b, c, d = 0.00035510, 0.0578, -0.0637, 6.0284
        COP_m = a * T_menv**2 + b * T_menv + c * T_mout + d

        # 当月温差 (室内 - 室外)
        delta_T = T_room - T_menv
        if delta_T <= 0:
            # 当月平均温度高于室内，理论上无需供热，供热量为0
            Qm = 0.0
            Pm = 0.0
            print(f"{month_name}: 平均室外温度 {T_menv:.1f}℃ 高于室内，Qm=0, Pm=0")
        else:
            Qm = K * delta_T * t_m          # 当月总供热量 (kWh)
            Pm = Qm / COP_m                  # 当月总耗电量 (kWh)

        Q_total += Qm
        P_total += Pm

        monthly_data.append({
            'month': month_name,
            'T_menv': T_menv,
            'T_mout': T_mout,
            'days': days,
            'COP_m': COP_m,
            'Qm_kWh': Qm,
            'Pm_kWh': Pm
        })

    # 5. 计算 SCOP
    if P_total > 0:
        SCOP = Q_total / P_total
    else:
        SCOP = float('nan')
        print("警告：总耗电量为0，无法计算SCOP")

    # 返回结果
    details = {
        'K': K,
        'Q_total_kWh': Q_total,
        'P_total_kWh': P_total,
        'SCOP': SCOP,
        'monthly': monthly_data
    }
    return SCOP, details


# 示例调用
if __name__ == "__main__":
    # 假设的月平均温度数据（青岛供暖季典型数据，仅供参考）
    env_temps = [-0.5, -1.2, -2.8, -1.5, 1.0, 5.5]   # 11,12,1,2,3,4月
    out_temps = [40.0, 40.0, 40.0, 40.0, 40.0, 40.0] # 对应的月平均出水温度
    days_in_month = [15, 31, 31, 28, 31, 5]         # 各月天数

    # 方式1：已知机组数量（假设10台）
    scop1, det1 = calculate_scop(env_temps, out_temps, days_in_month, n_units=21)

    # 方式2：已知建筑面积和耗热量指标（假设1000 m², q_H=25 W/m²）
    scop2, det2 = calculate_scop(env_temps, out_temps, days_in_month,
                                 area=67000, q_H=25)

    print("\n===== 结果 =====")
    print(f"方式1 (n=10台) : SCOP = {scop1:.4f}")
    print(f"方式2 (S=1000m², q=25W/m²) : SCOP = {scop2:.4f}")

    # 可选：打印各月详情
    # import pandas as pd
    # df = pd.DataFrame(det1['monthly'])
    # print(df)