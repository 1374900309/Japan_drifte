#!/usr/bin/env python3
from datetime import timedelta
import numpy as np
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.colors import ListedColormap
from scipy.ndimage import gaussian_filter
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
n_elements = 100000
wind_drift_factor = np.full(n_elements, 0.03)
o.seed_elements(
    lon=141, lat=37.5, radius=50000, number=n_elements,
    time=reader_current.start_time, wind_drift_factor=wind_drift_factor
)

# 运行模拟
o.run(
    time_step=timedelta(minutes=15),
    time_step_output=timedelta(hours=1),
    duration=timedelta(days=30)
)

# 输出文件夹
output_dir = r"F:\open_drifter\result\figure3"
os.makedirs(output_dir, exist_ok=True)

# ✅ Glow 热力图输出（叠加地形图背景）
glow_png = os.path.join(output_dir, "Japan_trajectory_glow730days(100000).png")

# 获取所有时间步粒子位置
lon_all = o.result['lon'].values.flatten()
lat_all = o.result['lat'].values.flatten()

# 生成密度图
lon_bins = np.linspace(137, 160.5, 1000)
lat_bins = np.linspace(33, 44, 1000)
density, _, _ = np.histogram2d(lat_all, lon_all, bins=[lat_bins, lon_bins])
glow = gaussian_filter(density, sigma=8)

# 自定义透明 colormap
colors = plt.cm.plasma(np.linspace(0, 1, 256))
colors[:50, -1] = 0  # 最低密度透明
transparent_cmap = ListedColormap(colors)

# 读取地形图
terrain_path = os.path.join(output_dir, "111.tif")
terrain_img = plt.imread(terrain_path)

# 绘图
fig = plt.figure(figsize=(12, 8), dpi=650)
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([137, 160.5, 33, 44])

# 叠加地形图作为背景
ax.imshow(
    terrain_img,
    origin='upper',  # 根据图片方向可改为 'lower'
    extent=[137, 160.5, 33, 44],
    transform=ccrs.PlateCarree(),
    zorder=0
)

# ❌ 移除地图黑色轮廓线（即不调用 coastlines）
# ax.coastlines(resolution='50m', color='black', linewidth=0.4, zorder=2)

# Glow 层叠加
im = ax.imshow(
    glow,
    origin='lower',
    extent=[137, 160.5, 33.23, 43.77],  # 注意使用更小的范围叠加效果更好
    cmap=transparent_cmap,
    alpha=1.0,
    transform=ccrs.PlateCarree(),
    zorder=1
)

# colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
cbar.set_label('Particle Density (Glow)', fontsize=12)

# ✅ 去除边框和刻度
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

# 保存
plt.savefig(glow_png, dpi=650, bbox_inches='tight')
plt.close()
print(f"✅ Glow 热力图保存路径: {glow_png}")
