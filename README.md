# FAST_LIO_RoboSense

[中文文档](README.zh-CN.md)

ROS2 Humble version of FAST_LIO with support for RoboSense Airy LiDAR.

## Features

- ✅ Based on FAST_LIO ROS2 Humble version
- ✅ Support for RoboSense Airy LiDAR (lidar_type: 5)

## Installation

1. Initialize git submodule:

```bash
git clone https://github.com/MichaelSun1001/FAST_LIO_Airy_ROS2 --recursive
```

2. Build:

```bash
colcon build --parallel-workers 20 --symlink-install
```

## Usage

### Launch RoboSense Airy LiDAR Mapping

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

Defaults: RViz starts by default, and the map save path defaults to `~/fast_lio_maps/robosense_airy_map.pcd`.

### Play GmbH scan6 Bag

Start mapping:

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

Play the bag in another terminal:

```bash
source /opt/ros/humble/setup.bash

ros2 bag play /home/sax/rosbags/GmbH/scan6 \
  --topics /rslidar_points /rslidar_imu_data
```

### Launch GigaAI Rear Airy Bag

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

This uses `/rslidar_rear/points`, `/rslidar_rear/imu_data`, and the rear LiDAR-IMU extrinsic in `config/gigaai_airy_rear.yaml`.

### Save Map

```bash
cd /home/sax/FAST_LIO_Airy_ROS2
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 service call /map_save std_srvs/srv/Trigger "{}"
```

The terminal response includes the saved PCD path, for example:

```text
message: Map saved successfully to /home/sax/fast_lio_maps/scan6_map.pcd
```

### Launch Arguments

- `use_sim_time`: default `false`
- `config_path`: default package config directory
- `config_file`: default `robosenseAiry.yaml` or `gigaai_airy_rear.yaml`
- `rviz`: default `true`
- `rviz_cfg`: default package RViz config
- `map_file_path`: default `~/fast_lio_maps/robosense_airy_map.pcd` or `~/fast_lio_maps/gigaai_airy_rear_map.pcd`
- `play_bag`: default `false`, only in `mapping_gigaai_airy_rear.launch.py`
- `bag_path`: bag directory, only used when `play_bag:=true`

### Parameter Configuration

Configuration file is located at `config/robosenseAiry.yaml`. Main parameters:

- `preprocess.lidar_type: 5` - RoboSense Airy LiDAR type
- `preprocess.scan_line: 96` - Number of scan lines
- `common.lid_topic: "/rslidar_points"` - Point cloud topic
- `common.imu_topic: "/rslidar_imu_data"` - IMU topic

## Troubleshooting

### Mapping "flies away" at startup with some bags

If one bag works but another "flies away" immediately, first compare `/rslidar_points` fields.

- Expected (this repo): `x, y, z, intensity, ring, timestamp` (`point_step = 26`)
- Some bags use: `x, y, z, intensity, tag, ring, timestamp` (`point_step = 27`)

The extra `tag` changes field offsets and may break `ring/timestamp` parsing, causing undistortion errors and early divergence.

Also check that per-point `timestamp` units/semantics are the same across bags. If startup motion is large, try `ros2 bag play <bag> --start-offset 2.0`.
