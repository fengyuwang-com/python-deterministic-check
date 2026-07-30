"""
确定性运算验证 —— 在任何平台、任何时间运行，结果都应完全一致
测试类别：整数运算、浮点运算、复数、矩阵、高精度、素数、斐波那契、数值积分
"""
import hashlib
import time
from decimal import Decimal, getcontext
from fractions import Fraction
import math

print("=" * 60)
print("确定性运算验证 —— 跨平台结果一致性测试")
print("=" * 60)

results = {}  # 收集所有结果用于最终校验

# ---------- 1. 大整数运算 ----------
a = 12345678901234567890
b = 98765432109876543210
big_mul = a * b
big_pow = pow(1234567, 89)
results['大整数乘法'] = big_mul
results['大整数幂']   = big_pow
print(f"\n[1] 大整数运算")
print(f"    {a} × {b} = {big_mul}")
print(f"    1234567^89 末50位 = ...{str(big_pow)[-50:]}")

# ---------- 2. 浮点运算（IEEE 754 全球统一）----------
x = 1.23456789
y = 9.87654321
fp_sum  = x + y
fp_prod = x * y
fp_div  = x / y
fp_sqrt = math.sqrt(x)
results['浮点加法']   = fp_sum
results['浮点乘法']   = fp_prod
results['浮点除法']   = fp_div
results['浮点开方']   = fp_sqrt
print(f"\n[2] 浮点运算（IEEE 754）")
print(f"    1.23456789 + 9.87654321 = {fp_sum}")
print(f"    1.23456789 × 9.87654321 = {fp_prod}")
print(f"    1.23456789 / 9.87654321 = {fp_div}")
print(f"    √1.23456789              = {fp_sqrt}")

# ---------- 3. 高精度 Decimal（固定精度）----------
getcontext().prec = 50
d1 = Decimal("1") / Decimal("7")
d2 = Decimal("2").sqrt()
d3 = Decimal("123456789") * Decimal("987654321") / Decimal("999999999")
results['高精度1/7']    = str(d1)
results['高精度√2']     = str(d2)
results['高精度运算']   = str(d3)
print(f"\n[3] 高精度 Decimal（50位）")
print(f"    1/7   = {d1}")
print(f"    √2    = {d2}")
print(f"    123456789×987654321/999999999 = {d3}")

# ---------- 4. 复数运算 ----------
c1 = complex(3, 4)
c2 = complex(1, -2)
c_add  = c1 + c2
c_mul  = c1 * c2
c_exp  = complex(math.cos(1), math.sin(1))  # e^i
c_euler = c_exp  # 验证欧拉公式近似
results['复数加法'] = (c_add.real, c_add.imag)
results['复数乘法'] = (c_mul.real, c_mul.imag)
print(f"\n[4] 复数运算")
print(f"    (3+4i)+(1-2i) = {c_add}")
print(f"    (3+4i)×(1-2i) = {c_mul}")
print(f"    e^i ≈ {c_exp}  （模长应≈1: {abs(c_exp):.10f}）")

# ---------- 5. 矩阵运算（纯 Python 实现，不依赖 NumPy）----------
def mat_mul(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]

def mat_pow(M, n):
    size = len(M)
    result = [[1 if i==j else 0 for j in range(size)] for i in range(size)]
    base = [row[:] for row in M]
    while n:
        if n & 1:
            result = mat_mul(result, base)
        base = mat_mul(base, base)
        n >>= 1
    return result

M = [[1, 1], [1, 0]]  # 斐波那契矩阵
M_50 = mat_pow(M, 50)
results['矩阵M^50'] = M_50
print(f"\n[5] 矩阵运算")
print(f"    [[1,1],[1,0]]^50 =")
for row in M_50:
    print(f"      {row}")
print(f"    → 右上角 = F(50) = {M_50[0][1]}")

# ---------- 6. 斐波那契数列（快速加倍法，O(log n)）----------
def fib(n):
    if n == 0: return 0
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * ((b << 1) - a)
        d = a * a + b * b
        if bit == '1':
            a, b = d, c + d
        else:
            a, b = c, d
    return a

fib_100 = fib(100)
fib_10000 = fib(10000)
results['F(100)']    = fib_100
results['F(10000)末20位'] = str(fib_10000)[-20:]
print(f"\n[6] 斐波那契数列")
print(f"    F(100)  = {fib_100}")
print(f"    F(10000) 共 {len(str(fib_10000))} 位，末20位 = ...{str(fib_10000)[-20:]}")

# ---------- 7. 素数判定 & 筛法 ----------
def sieve(n):
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i, p in enumerate(is_prime) if p]

primes_1000 = sieve(1000)
is_997_prime = 997 in primes_1000
results['素数个数(<1000)'] = len(primes_1000)
results['997是否素数']     = is_997_prime
print(f"\n[7] 素数")
print(f"    <1000 的素数共 {len(primes_1000)} 个")
print(f"    997 是素数？{is_997_prime}")
print(f"    最大的5个：{primes_1000[-5:]}")

# ---------- 8. 数值积分（辛普森法，确定性步数）----------
def simpson(f, a, b, n=100000):
    """n 必须为偶数"""
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        x = a + i * h
        s += f(x) * (4 if i % 2 else 2)
    return s * h / 3

integral_pi = simpson(lambda x: math.sqrt(1 - x**2), 0, 1, 100000) * 4  # 应≈π
integral_e  = simpson(lambda x: math.exp(-x**2), 0, 1, 100000) * 2 / math.sqrt(math.pi)  # 应≈erf(1)
results['积分π'] = integral_pi
results['积分erf(1)'] = integral_e
print(f"\n[8] 数值积分（辛普森法，100000步）")
print(f"    4*int_0^1 sqrt(1-x^2)dx ~ {integral_pi}  (err {abs(integral_pi-math.pi):.2e})")
print(f"    2/sqrt(pi)*int_0^1 e^(-x^2)dx ~ {integral_e}  (err {abs(integral_e-math.erf(1)):.2e})")

# ---------- 9. 字符串哈希校验（SHA-256）----------
all_output = "\n".join(f"{k}: {v}" for k, v in sorted(results.items()))
sha = hashlib.sha256(all_output.encode()).hexdigest()
results['SHA-256'] = sha
print(f"\n[9] 结果汇总 SHA-256 校验")
print(f"    哈希值 = {sha}")

# ---------- 汇总表 ----------
print("\n" + "=" * 60)
print("全部结果汇总（此输出在任何平台应完全一致）")
print("=" * 60)
for k, v in sorted(results.items()):
    val_str = str(v)
    if len(val_str) > 80:
        val_str = val_str[:77] + "..."
    print(f"  {k:20s} = {val_str}")

print(f"\n[全局 SHA-256 校验和]")
print(f"   {sha}")
print("\n如果你的机器跑出同样的 SHA-256，说明所有运算结果完全一致！")
