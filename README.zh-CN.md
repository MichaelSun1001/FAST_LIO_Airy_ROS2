# FAST_LIO_RoboSense

[English](README.md)

这是支持 RoboSense Airy LiDAR 的 FAST_LIO ROS2 Humble 版本。

## 功能

- ✅ 基于 FAST_LIO ROS2 Humble 版本
- ✅ 支持 RoboSense Airy LiDAR（`lidar_type: 5`）

## 安装

1. 克隆仓库并初始化 submodule：

```bash
git clone https://github.com/MichaelSun1001/FAST_LIO_Airy_ROS2 --recursive
```

2. 编译：

```bash
colcon build --parallel-workers 20 --symlink-install
```

## 使用

### 启动 RoboSense Airy 建图

```bash
cd /home/sax/FAST_LIO_Airy_ROS2
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch fast_lio_robosense mapping_robosense_airy.launch.py \
  use_sim_time:=false \
  config_file:=robosenseAiry.yaml \
  rviz:=true \
  map_file_path:=~/fast_lio_maps/robosense_airy_map.pcd
```

默认会启动 RViz，默认 PCD 保存路径是 `~/fast_lio_maps/robosense_airy_map.pcd`。

### 播放 GmbH scan6 数据包

启动建图：

```bash
cd /home/sax/FAST_LIO_Airy_ROS2
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch fast_lio_robosense mapping_robosense_airy.launch.py \
  use_sim_time:=false \
  config_file:=robosenseAiry.yaml \
  rviz:=true \
  map_file_path:=~/fast_lio_maps/scan6_map.pcd
```

另开终端播放 rosbag：

```bash
source /opt/ros/humble/setup.bash

ros2 bag play /home/sax/rosbags/GmbH/scan6 \
  --topics /rslidar_points /rslidar_imu_data
```

### 启动 GigaAI 后向 Airy 数据包

```bash
cd /home/sax/FAST_LIO_Airy_ROS2
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch fast_lio_robosense mapping_gigaai_airy_rear.launch.py \
  use_sim_time:=false \
  config_file:=gigaai_airy_rear.yaml \
  rviz:=true \
  map_file_path:=~/fast_lio_maps/gigaai_airy_rear_map.pcd \
  play_bag:=true \
  bag_path:=/home/sax/rosbags/GigaAI/airy_points_imu_20260512_175121
```

该 launch 使用 `/rslidar_rear/points`、`/rslidar_rear/imu_data`，以及 `config/gigaai_airy_rear.yaml` 中的后向雷达与 IMU 外参。

### 保存地图

```bash
cd /home/sax/FAST_LIO_Airy_ROS2
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 service call /map_save std_srvs/srv/Trigger "{}"
```

终端返回会包含保存后的 PCD 路径，例如：

```text
message: Map saved successfully to /home/sax/fast_lio_maps/scan6_map.pcd
```

### Launch 参数

- `use_sim_time`：默认 `false`
- `config_path`：默认使用包内 config 目录
- `config_file`：默认 `robosenseAiry.yaml` 或 `gigaai_airy_rear.yaml`
- `rviz`：默认 `true`
- `rviz_cfg`：默认使用包内 RViz 配置
- `map_file_path`：默认 `~/fast_lio_maps/robosense_airy_map.pcd` 或 `~/fast_lio_maps/gigaai_airy_rear_map.pcd`
- `play_bag`：默认 `false`，仅 `mapping_gigaai_airy_rear.launch.py` 支持
- `bag_path`：rosbag 目录，仅在 `play_bag:=true` 时使用

### 参数配置

配置文件位于 `config/robosenseAiry.yaml`。主要参数：

- `preprocess.lidar_type: 5`：RoboSense Airy LiDAR 类型
- `preprocess.scan_line: 96`：扫描线数
- `common.lid_topic: "/rslidar_points"`：点云话题
- `common.imu_topic: "/rslidar_imu_data"`：IMU 话题

## 故障排查

### 某些数据包启动后建图“飞走”

如果一个数据包正常，另一个数据包一启动就明显发散，先对比 `/rslidar_points` 字段。

- 本仓库期望：`x, y, z, intensity, ring, timestamp`（`point_step = 26`）
- 部分数据包可能是：`x, y, z, intensity, tag, ring, timestamp`（`point_step = 27`）

额外的 `tag` 字段会改变字段偏移，可能导致 `ring/timestamp` 解析错误，从而造成去畸变异常和早期发散。

同时检查每个点的 `timestamp` 单位和语义是否一致。如果启动阶段运动较大，可以尝试：

```bash
ros2 bag play <bag> --start-offset 2.0
```
