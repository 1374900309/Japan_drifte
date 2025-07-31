#!/usr/bin/env python3
from datetime import timedelta
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.oceandrift import OceanDrift

# 初始化模型
o = OceanDrift(loglevel=20)

# 数据路径
reader_current = reader_netCDF_CF_generic.Reader(
    r"F:\open_drifter\opendrift\tests\test_data\21Japan\Japan_21-22.nc"
)
reader_wind = reader_netCDF_CF_generic.Reader(
    r"F:/open_drifter/opendrift/tests/test_data/20Japan/era5_wind_ready.nc"
)
o.add_reader([reader_current, reader_wind])

# 模型配置
o.set_config("drift:vertical_mixing", False)

# 投放粒子
n_elements = 2000
wind_drift_factor = np.full(n_elements, 0.03)
o.seed_elements(
    lon=141, lat=37.5, radius=50000, number=n_elements,
    time=reader_current.start_time, wind_drift_factor=wind_drift_factor
)

# 自定义粒子颜色
custom_status_colors = {
    'initial': '#99FFFF',
    'active': '#CCBBFF',
    'stranded': '#770077'
}
o.status_colors = custom_status_colors
cmap_custom = ListedColormap([
    custom_status_colors['initial'],
    custom_status_colors['active'],
    custom_status_colors['stranded']
])

# 运行模拟
o.run(
    time_step=timedelta(minutes=15),
    time_step_output=timedelta(hours=1),
    duration=timedelta(days=1)
)

# 输出路径
output_dir = r"F:\open_drifter\result\figure3"
os.makedirs(output_dir, exist_ok=True)
trajectory_png = os.path.join(output_dir, "Japan_trajectory_1ays(nozuobiao)1.png")
plt.rcParams['figure.dpi'] = 650  # 设置全局DPI
plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg'  # 确保ffmpeg路径正确
# ❗ 正确使用 plot（去掉 fast=True）
o.plot(
    hide_landmask=True, #关闭地图绘制部分
    show_landmask=False,
    background=None,
    landmask_resolution="50m",
    linecolor='status',
    cmap=cmap_custom,
    legend=False,
    title=None,
    filename=trajectory_png,
    corners=[137, 160.5, 33, 44],
    auto_range=False,
    return_fig=True,  # ✅ 关键参数
    dpi=650,
    markersize=100
)



print(f"✅ 高分辨率静态图保存路径: {trajectory_png}")
