import numpy as np

# パラメータ設定
gamma = 2.0  # 相対的リスク回避度
beta = 0.985**20  # 20年間の割引因子
r = 1.025**20 - 1  # 20年間の利子率
tax_rate = 0.30  # 中年期の所得税率（30%）

# 3つの生産性タイプ
productivity_types = [0.8027, 1.0, 1.2457]
productivity_names = ['Low Productivity', 'Medium Productivity', 'High Productivity']

# 遷移確率行列（P[i,j] = 若年期タイプi → 中年期タイプj）
P = np.array([[0.7451, 0.2528, 0.0021],
              [0.1360, 0.7281, 0.1360],
              [0.0021, 0.2528, 0.7451]])

# 各タイプの人口比率（若年期）
initial_population = np.array([1/3, 1/3, 1/3])

print("=== 年金制度の税収と年金額計算 ===")
print(f"所得税率: {tax_rate*100:.1f}%")
print(f"利子率 (20年): {r:.4f}")

# 中年期の人口分布を計算
middle_age_population = np.zeros(len(productivity_types))
for i in range(len(productivity_types)):
    for j in range(len(productivity_types)):
        middle_age_population[j] += initial_population[i] * P[i, j]

print(f"\n=== 人口分布 ===")
print(f"若年期の人口比率: {initial_population}")
print(f"中年期の人口比率: {middle_age_population}")

# 中年期の総税収を計算
total_tax_revenue = 0
print(f"\n=== 税収計算の詳細 ===")
for j in range(len(productivity_types)):
    # 中年期の各タイプの労働所得
    labor_income = productivity_types[j]
    # 各タイプの税収
    tax_per_person = tax_rate * labor_income
    # 人口比率を考慮した総税収への貢献
    contribution = middle_age_population[j] * tax_per_person
    total_tax_revenue += contribution
    
    print(f"{productivity_names[j]}:")
    print(f"  労働所得: {labor_income:.4f}")
    print(f"  一人当たり税額: {tax_per_person:.4f}")
    print(f"  人口比率: {middle_age_population[j]:.4f}")
    print(f"  総税収への貢献: {contribution:.6f}")

print(f"\n=== 最終結果 ===")
print(f"中年期の総税収: {total_tax_revenue:.6f}")

# 老年期の年金額を計算
# 政府は税収を利子率rで運用し、老年期に均等に分配
pension_fund = total_tax_revenue * (1 + r)
pension_per_person = pension_fund / 1.0  # 総人口は1

print(f"\n=== 年金計算 ===")
print(f"税収の運用後価値: {total_tax_revenue:.6f} × (1 + {r:.4f}) = {pension_fund:.6f}")
print(f"一人当たり年金額: {pension_per_person:.6f}")

# 計算の検証
print(f"\n=== 計算の検証 ===")
print(f"税収計算の確認:")
manual_calculation = (
    (1/3) * 0.7451 * 0.30 * 0.8027 +  # 低→低
    (1/3) * 0.1360 * 0.30 * 0.8027 +  # 中→低
    (1/3) * 0.0021 * 0.30 * 0.8027 +  # 高→低
    (1/3) * 0.2528 * 0.30 * 1.0 +     # 低→中
    (1/3) * 0.7281 * 0.30 * 1.0 +     # 中→中
    (1/3) * 0.2528 * 0.30 * 1.0 +     # 高→中
    (1/3) * 0.0021 * 0.30 * 1.2457 +  # 低→高
    (1/3) * 0.1360 * 0.30 * 1.2457 +  # 中→高
    (1/3) * 0.7451 * 0.30 * 1.2457    # 高→高
)
print(f"手計算による総税収: {manual_calculation:.6f}")
print(f"プログラム計算による総税収: {total_tax_revenue:.6f}")
print(f"差: {abs(manual_calculation - total_tax_revenue):.10f}")

# 簡潔な答え
print(f"\n" + "="*50)
print(f"【答え】")
print(f"中年期における政府の総税収: {total_tax_revenue:.6f}")
print(f"一人当たりの年金額: {pension_per_person:.6f}")
print(f"="*50)
