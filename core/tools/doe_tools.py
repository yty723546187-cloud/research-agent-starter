import math
import pandas as pd
from itertools import product
from typing import Dict, List, Optional

def l9_table_from_factors(factors: dict) -> pd.DataFrame:
    """
    生成 Taguchi L9(3^4) 的前三/四列映射到你的因子。
    factors: {"A":[L1,L2,L3], "B":[...], "C":[...] , 可选 "D":[...] }
    """
    base = [
        [1,1,1,1],
        [1,2,2,2],
        [1,3,3,3],
        [2,1,2,3],
        [2,2,3,1],
        [2,3,1,2],
        [3,1,3,2],
        [3,2,1,3],
        [3,3,2,1],
    ]
    keys = list(factors.keys())
    if len(keys) not in (3,4):
        raise ValueError("当前示例仅支持 3 或 4 个因子（每个 3 水平）。")
    df = pd.DataFrame([{k: factors[k][row[i]-1] for i,k in enumerate(keys)} for row in base])
    df.insert(0, "试验号", [f"Run{i:02d}" for i in range(1,10)])
    return df

def taguchi_snr(values, mode="larger"):
    """
    Taguchi SNR:
    - larger: -10*log10( mean(1/y^2) )
    - smaller: -10*log10( mean(y^2) )
    - nominal: 10*log10( mean^2 / var )
    """
    y = [float(v) for v in values if v is not None and str(v)!='']
    if not y:
        return float("nan")
    if mode == "larger":
        return -10.0 * math.log10(sum(1.0/(v**2) for v in y) / len(y))
    elif mode == "smaller":
        return -10.0 * math.log10(sum((v**2) for v in y) / len(y))
    elif mode == "nominal":
        mean = sum(y)/len(y)
        var = sum((v-mean)**2 for v in y) / (len(y)-1 if len(y)>1 else 1)
        if var <= 0: var = 1e-12
        return 10.0 * math.log10((mean*mean)/var)
    else:
        raise ValueError("mode 必须是 larger/smaller/nominal")

def full_factorial_table(factors: Dict[str, List[str]], replicates: int = 1,
                         randomize: bool = True, seed: Optional[int] = None,
                         add_replicate_columns: bool = True) -> pd.DataFrame:
    """
    生成“全因子”设计表（所有组合）。例如 3 因子 × 3 水平 = 27 次。
    - factors: {"A":[L1,L2,L3], "B":[...], "C":[...]}
    - replicates: 每个组合的重复次数（用于实际实施重复）。
    - randomize: 是否对实施顺序随机化。
    - seed: 随机种子（可复现）。
    - add_replicate_columns: 如果为 True，则预先添加“重复1..N”空列。
    返回：包含“试验号/实施顺序/因子列/(可选的重复列)”的 DataFrame
    """
    if not factors:
        raise ValueError("factors 不能为空")
    import pandas as _pd
    from itertools import product as _product
    keys = list(factors.keys())
    levels = [list(v) for v in factors.values()]
    combos = list(_product(*levels))
    df = _pd.DataFrame([dict(zip(keys, combo)) for combo in combos])
    df.insert(0, "试验号", [f"Run{i:03d}" for i in range(1, len(df)+1)])
    if randomize:
        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    df.insert(1, "实施顺序", range(1, len(df)+1))
    if replicates > 1 and not add_replicate_columns:
        df = _pd.concat([df.assign(重复编号=r+1) for r in range(replicates)], ignore_index=True)
        if randomize:
            df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
        df.insert(0, "试验号", [f"Run{i:03d}" for i in range(1, len(df)+1)])
        df["实施顺序"] = range(1, len(df)+1)
    elif replicates >= 1 and add_replicate_columns:
        for r in range(1, replicates+1):
            df[f"重复{r}"] = None
    return df
