import tracemalloc
from time import time


tracemalloc.start()  # 启动内存跟踪

print("导入开始...")

start_time = time()  # 记录开始时间

# 记录导入前内存快照
before_snapshot = tracemalloc.take_snapshot()

end_time = time()  # 记录结束时间

print(f"\n【导入耗时】{end_time-start_time:.2f} s\n")  # 打印导入耗时

# 记录导入后内存快照
after_snapshot = tracemalloc.take_snapshot()

# 计算总内存增量
total_increase = sum(
    stat.size_diff for stat in after_snapshot.compare_to(before_snapshot, "traceback")
)
print(f"\n【总内存增量】{total_increase/1024**2:.2f} MB\n")  # 转换为MB单位

# 计算内存差异（按文件排序）
top_stats = after_snapshot.compare_to(before_snapshot, "lineno")

# 打印前10个内存分配点
print("[ 内存分配TOP10 ]")
for stat in top_stats[:10]:
    print(f"▲ {stat.size_diff/1024:.1f} KB | {stat.traceback.format()[-1]}")
