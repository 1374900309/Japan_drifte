#!/usr/bin/env python3
from datetime import timedelta
import numpy as np
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
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

# 设置自定义粒子状态颜色
custom_status_colors = {
    'initial': '#99FFFF',   # 初始
    'active': '#CCBBFF',    # 活跃
    'stranded': '#770077'   # 搁浅
}
o.status_colors = custom_status_colors

# 用于动画的 colormap
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

# 创建输出文件夹
output_dir = r"F:\open_drifter\result\figure4"
os.makedirs(output_dir, exist_ok=True)

# 🎞 MP4动图输出
animation_path = os.path.join(output_dir, "Japan_trajectory_1day.mp4")
plt.rcParams['figure.dpi'] = 650  # 设置全局DPI
plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg'  # 确保ffmpeg路径正确

o.animation(
    color='status',
    cmap=cmap_custom,
    fast=False,
    show_time=True,
    show_landmask=True,
    land_color='#b3b3b3',
    landmask_resolution='50m',
    filename=animation_path,
    corners=[137, 160.5, 33, 44],
    auto_range=False,
    writer='ffmpeg',  # 指定视频编码器
    fps=15,           # 帧率
    bitrate=5000,     # 比特率（更高画质）
    dpi=650           # 直接设置DPI
)

# 📌 静态轨迹图（高DPI）
trajectory_png = os.path.join(output_dir, "Japan_trajectory_1day.png")
try:
    o.plot(
        linecolor='status',
        cmap=cmap_custom,
        fast=True,
        filename=trajectory_png,
        show_landmask=True,
        land_color='#b3b3b3',
        landmask_resolution="50m",
        corners=[137, 160.5, 33, 44],
        auto_range=False,
        savefig_kwargs={'dpi': 650, 'quality': 100}
    )
except:
    # 备用方案
    fig = plt.figure(figsize=(12, 8), dpi=650)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    o.plot(ax=ax, fast=True, show_landmask=True)
    fig.savefig(trajectory_png, dpi=650, bbox_inches='tight', quality=100)
    plt.close(fig)

# ✅ 输出路径提示
print(f"✅ MP4动画保存路径: {animation_path}")
print(f"✅ 静态图保存路径: {trajectory_png}")
print(f"✅ 分辨率确认: 650 DPI（右键属性查看详细信息）")