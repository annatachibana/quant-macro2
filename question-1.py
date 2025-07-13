import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
import matplotlib.font_manager as fm

# 日本語フォント設定
plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
plt.rcParams['axes.unicode_minus'] = False

# パラメータ設定
gamma = 2.0  # 相対的リスク回避度
beta = 0.985**20  # 20年間の割引因子
r = 1.025**20 - 1  # 20年間の利子率（修正：1.025^20 - 1）

# 3つの生産性タイプ
productivity_types = [0.8027, 1.0, 1.2457]
productivity_names = ['Low Productivity', 'Medium Productivity', 'High Productivity']

# 遷移確率行列（P[i,j] = 若年期タイプi → 中年期タイプj）
P = np.array([[0.7451, 0.2528, 0.0021],
              [0.1360, 0.7281, 0.1360],
              [0.0021, 0.2528, 0.7451]])

# 資産グリッド設定
a_min = 0.0
a_max = 5.0
n_grid = 100
a_grid = np.linspace(a_min, a_max, n_grid)

# 数値計算の安定性のための小さな正の数
EPS = 1e-8

# 効用関数
def utility(c):
    """CRRA効用関数"""
    c = max(c, EPS)  # 正の消費を保証
    return (c**(1-gamma)) / (1-gamma)

# 老年期の価値関数（年金なし）
def V_old(a3):
    """老年期の価値関数：資産a3で老年期を迎える場合"""
    c3 = (1 + r) * a3  # 老年期の消費 = 資産×(1+利子率)
    return utility(c3)

# 中年期の価値関数を動的計画法で求める
def solve_middle_age():
    """中年期の価値関数と政策関数を求める"""
    V_middle = np.zeros((len(productivity_types), len(a_grid)))
    policy_middle = np.zeros((len(productivity_types), len(a_grid)))
    
    for i, w2 in enumerate(productivity_types):
        for j, a2 in enumerate(a_grid):
            # 中年期の総資源
            total_resources = (1 + r) * a2 + w2
            
            # 目的関数（負の価値関数を最小化）
            def objective(a3):
                c2 = total_resources - a3  # 中年期の消費
                if c2 <= EPS:
                    return 1e10  # 実行不可能な場合の大きなペナルティ
                
                # 期待継続価値（老年期の価値関数）
                expected_V = V_old(a3)
                
                # 負の価値関数を返す（最小化のため）
                return -(utility(c2) + beta * expected_V)
            
            # 最適化の制約：正の消費を保証
            bounds = (0, max(0, total_resources - EPS))
            
            if bounds[1] > bounds[0]:
                result = minimize_scalar(objective, bounds=bounds, method='bounded')
                best_a3 = result.x
                best_value = -result.fun
            else:
                best_a3 = 0
                best_value = utility(total_resources)
            
            V_middle[i, j] = best_value
            policy_middle[i, j] = best_a3
    
    return V_middle, policy_middle

# 若年期の価値関数を動的計画法で求める
def solve_young_age(V_middle):
    """若年期の価値関数と政策関数を求める"""
    V_young = np.zeros((len(productivity_types), len(a_grid)))
    policy_young = np.zeros((len(productivity_types), len(a_grid)))
    
    for i, w1 in enumerate(productivity_types):
        for j, a1 in enumerate(a_grid):
            # 若年期の総資源
            total_resources = (1 + r) * a1 + w1
            
            # 目的関数（負の価値関数を最小化）
            def objective(a2):
                c1 = total_resources - a2  # 若年期の消費
                if c1 <= EPS:
                    return 1e10  # 実行不可能な場合の大きなペナルティ
                
                # 期待継続価値（中年期の価値関数の期待値）
                expected_V = 0
                for k in range(len(productivity_types)):
                    V_middle_interp = np.interp(a2, a_grid, V_middle[k, :])
                    expected_V += P[i, k] * V_middle_interp
                
                # 負の価値関数を返す（最小化のため）
                return -(utility(c1) + beta * expected_V)
            
            # 最適化の制約：正の消費を保証
            bounds = (0, max(0, total_resources - EPS))
            
            if bounds[1] > bounds[0]:
                result = minimize_scalar(objective, bounds=bounds, method='bounded')
                best_a2 = result.x
                best_value = -result.fun
            else:
                best_a2 = 0
                best_value = utility(total_resources)
            
            V_young[i, j] = best_value
            policy_young[i, j] = best_a2
    
    return V_young, policy_young

# モデルを解く
print("=== Solving 3-period lifecycle model ===")
print("Calculating middle-age value function...")
V_middle, policy_middle = solve_middle_age()

print("Calculating young-age value function...")
V_young, policy_young = solve_young_age(V_middle)

print("=== Calculation completed ===")

# グラフを作成
fig, ax = plt.subplots(figsize=(12, 8))

colors = ['blue', 'green', 'red']
linestyles = ['-', '--', '-.']

# 貯蓄政策関数をプロット
for i, (prod, name) in enumerate(zip(productivity_types, productivity_names)):
    policy_values = policy_young[i, :]
    
    # 診断情報を表示
    print(f"\n{name}:")
    print(f"  Productivity: {prod:.4f}")
    print(f"  Policy function range: [{np.min(policy_values):.4f}, {np.max(policy_values):.4f}]")
    print(f"  Average savings: {np.mean(policy_values):.4f}")
    
    # 政策関数をプロット
    ax.plot(a_grid, policy_values, 
            color=colors[i], 
            linestyle=linestyles[i],
            linewidth=2.5,
            label=f'{name} (w={prod:.4f})',
            alpha=0.9)

# 45度線を参考として追加
ax.plot(a_grid, a_grid, 'k--', alpha=0.4, label='45-degree line', linewidth=1)

# グラフの設定（軸の範囲を2.0に変更）
ax.set_xlabel('Young Period Initial Assets (excluding interest)', fontsize=12)
ax.set_ylabel('Next Period Assets (Savings)', fontsize=12)
ax.set_title('Savings Policy Function (No Pension)', fontsize=14, pad=20)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.set_xlim(0, 2.0)
ax.set_ylim(0, 2.0)

plt.tight_layout()

# 経済学的直感の説明
explanation = """
経済学的直感：

1. 右上がりの政策関数：
   • 初期資産が多いほど、より多くの貯蓄が可能
   • 資産は正常財であり、富の効果により貯蓄が増加

2. 生産性による違い：
   • 高生産性の個人：将来の高い所得を期待し、より多くの貯蓄を行う
   • 低生産性の個人：現在の消費を重視し、貯蓄は相対的に少ない
   • 中生産性の個人：両者の中間的な行動

3. 消費平滑化動機：
   • 全ての個人が期間を通じて消費を平滑化しようとする
   • 生産性の違いにより、最適な平滑化パターンが異なる

4. 予防的貯蓄動機：
   • 将来の所得の不確実性に対する保険としての貯蓄
   • リスク回避的な個人ほど、この動機が強い

5. 長期的な格差：
   • 生産性の違いが貯蓄行動の差を生み、長期的な資産格差につながる
"""

print(explanation)

plt.show()

# 具体的な数値例
print("\n=== Specific Policy Function Values ===")
sample_assets = [0.5, 1.0, 1.5, 2.0, 3.0]
for assets in sample_assets:
    idx = np.argmin(np.abs(a_grid - assets))
    print(f"\nInitial assets = {assets:.1f}:")
    for i, name in enumerate(productivity_names):
        savings = policy_young[i, idx]
        consumption = (1 + r) * assets + productivity_types[i] - savings
        print(f"  {name}: savings {savings:.4f}, consumption {consumption:.4f}")

# パラメータ情報
print(f"\n=== Parameter Information ===")
print(f"Interest rate (20 years): {r:.4f}")
print(f"Discount factor (20 years): {beta:.4f}")
print(f"Relative risk aversion: {gamma}")
print(f"Productivity types: {productivity_types}")
