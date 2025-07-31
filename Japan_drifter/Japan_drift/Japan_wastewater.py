from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.radionuclides import RadionuclideDrift
from datetime import datetime, timedelta
import numpy as np
import os
import xarray as xr
# 模拟保存目录
save_dir = r'F:\open_drifter\result\figure'
os.makedirs(save_dir, exist_ok=True)

# 初始化模型
o = RadionuclideDrift(loglevel=20, seed=0)

# 读取海流数据
ocean_data_path = r'F:\open_drifter\opendrift\tests\test_data\21Japan\Japan_21-22_renamed.nc'
ds = xr.open_dataset(ocean_data_path)
conc_lat = ds.latitude.values
conc_lon = ds.longitude.values
reader_current = reader_netCDF_CF_generic.Reader(
    ocean_data_path,
    name='main_reader',
    standard_name_mapping={
        'sea_floor_depth_below_sea_level': 'sea_floor_depth_below_sea_level',
        'latitude': 'latitude',
        'longitude': 'longitude'
    }
)
o.add_reader(reader_current)

# 模型配置
o.set_config('drift:vertical_mixing', True)
o.set_config('vertical_mixing:diffusivitymodel', 'environment')
o.set_config('vertical_mixing:timestep', 600.)
o.set_config('drift:horizontal_diffusivity', 10)
o.set_config('radionuclide:particle_diameter', 5e-6)
o.set_config('radionuclide:sediment:resuspension_depth', 2.0)
o.set_config('radionuclide:sediment:resuspension_depth_uncert', 0.1)
o.set_config('radionuclide:sediment:resuspension_critvel', 0.15)
o.set_config('radionuclide:isotope', '137Cs')
o.set_config('radionuclide:specie_setup', 'LMM + Rev')
o.set_config('general:coastline_action', 'previous')
o.set_config('general:seafloor_action', 'lift_to_seafloor')
o.set_config('seed:LMM_fraction', 0.45)
o.set_config('seed:particle_fraction', 0.55)

# 投放粒子
start_time = reader_current.start_time
latseed, lonseed = 37.5, 138.5
ntraj = 5000
depth_init = np.random.uniform(-10, 0, ntraj)

o.seed_elements(
    lon=lonseed,
    lat=latseed,
    z=depth_init,
    radius=2000,
    number=ntraj,
    time=start_time
)

# 运行模拟（1 周）
o.run(
    steps=24 * 7,  # 一周，每小时1步
    time_step=timedelta(hours=1),
    time_step_output=timedelta(hours=3)
)

# 打印信息
print(o)
print('Final speciation:')
for isp, sp in enumerate(o.name_species):
    print('{:32}: {:>6}'.format(sp, sum(o.elements.specie == isp)))

print('Number of transformations:')
for isp in range(o.nspecies):
    print('{}'.format(['{:>9}'.format(np.int32(item)) for item in o.ntransformations[isp, :]]))

# 输出静态轨迹图
o.plot(
    linecolor='specie',
    vmin=0,
    vmax=o.nspecies - 1,
    fast=True,
    filename=os.path.join(save_dir, 'trajectory_static.png')
)

o.write_netcdf_radionuclide_density_map(
    filename=os.path.join(save_dir, 'radio_conc.nc'),
    pixelsize_m=500.,
    zlevels=[-2.],
    activity_unit='Bq',
    horizontal_smoothing=True,
    smoothing_cells=1,
    time_avg_conc=True,
    deltat=2.  # 小时
)

# 导出轨迹动态图
o.animation(
    filename=os.path.join(save_dir, 'trajectory_animation.gif'),
    color='specie',
    vmin=0,
    vmax=o.nspecies - 1,
    legend=[o.specie_num2name(i) for i in range(o.nspecies)],
    legend_loc=4,
    fast=True,
    dpi=100
)

# 导出垂向剖面动态图
o.animation_profile(
    filename=os.path.join(save_dir, 'vertical_profile.gif'),
    color='specie',
    vmin=0,
    vmax=o.nspecies - 1,
    legend=[o.specie_num2name(i) for i in range(o.nspecies)],
    legend_loc=3,
    dpi=100
)

# 输出垂向静态分布图
o.plot_vertical_distribution(
    filename=os.path.join(save_dir, 'vertical_distribution.png')
)
