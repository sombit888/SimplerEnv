import numpy as np
import os
import tensorflow as tf

import mani_skill2.envs, gymnasium as gym
from transforms3d.euler import euler2axangle, euler2quat
from sapien.core import Pose

from real2sim.rt1.rt1_model import RT1Inference
from real2sim.utils.visualization import write_video

def main(env_name, scene_name, ckpt_path='rt_1_x_tf_trained_for_002272480_step',
         robot_init_x=None, robot_init_y=None, robot_init_quat=[0, 0, 0, 1], 
         obj_init_x_range=None, obj_init_y_range=None,
         rgb_overlay_path=None, tmp_exp=False,
         control_freq=3, sim_freq=510, action_repeat=5,
         instruction_override=None,
         action_scale=1.0):
    robot_init_x = robot_init_x if robot_init_x is not None else 0.31 # hardcoded
    robot_init_y = robot_init_y if robot_init_y is not None else 0.188 # hardcoded
    obj_init_x_range = obj_init_x_range if obj_init_x_range is not None else np.linspace(-0.35, -0.1, 10)
    obj_init_y_range = obj_init_y_range if obj_init_y_range is not None else np.linspace(0.0, 0.4, 10)
    
    if 'YCB' in env_name:
        asset_root='/home/xuanlin/Real2Sim/ManiSkill2_real2sim/data/mani_skill2_ycb/'
    else:
        asset_root='/home/xuanlin/Real2Sim/ManiSkill2_real2sim/data/custom/'
    
    # Build RT-1 Model
    rt1_model = RT1Inference(saved_model_path=ckpt_path, action_scale=action_scale)
    
    for obj_init_x in obj_init_x_range:
        for obj_init_y in obj_init_y_range:
            # Create environment
            env = gym.make(env_name,
                        # control_mode='arm_pd_ee_delta_pose_align_interpolate_gripper_pd_joint_pos',
                        control_mode='arm_pd_ee_delta_pose_align_interpolate_gripper_pd_joint_target_pos',
                        obs_mode='rgbd',
                        robot='google_robot_static',
                        sim_freq=sim_freq,
                        control_freq=control_freq * action_repeat,
                        max_episode_steps=60 * action_repeat,
                        asset_root=asset_root,
                        scene_root='/home/xuanlin/Real2Sim/ManiSkill2_real2sim/data/hab2_bench_assets/',
                        scene_name=scene_name,
                        obj_init_rand_rot_z_enabled=False,
                        obj_init_rand_rot_range=0,
                        obj_init_fixed_xy_pos=np.array([obj_init_x, obj_init_y]),
                        obj_init_fixed_z_rot=None,
                        robot_init_fixed_xy_pos=np.array([robot_init_x, robot_init_y]),
                        robot_init_fixed_rot_quat=robot_init_quat,
                        camera_cfgs={"add_segmentation": True},
                        rgb_overlay_path=rgb_overlay_path,
                        rgb_overlay_cameras=['overhead_camera'],
                        # Enable Ray Tracing
                        # shader_dir="rt",
                        # render_config={"rt_samples_per_pixel": 8, "rt_use_denoiser": True},
            )
            
            # Reset and initialize environment
            predicted_actions = []
            images = []
            
            obs, _ = env.reset()
            image = obs['image']['overhead_camera']['rgb']
            images.append(image)
            predicted_terminated, terminated, truncated = False, False, False
        
            obj_name = ' '.join(env.obj.name.split('_')[1:])
            if env_name == 'PickSingleYCBIntoBowl-v0':
                task_description = f"place {obj_name} into red bowl"
            elif env_name in ['GraspSingleYCBInScene-v0', 'GraspSingleYCBSomeInScene-v0']:
                task_description = f"pick {obj_name}"
            elif env_name in ['GraspSingleYCBFruitInScene-v0']:
                task_description = "pick fruit"
            elif env_name in ['GraspSingleYCBCanInScene-v0', 'GraspSingleYCBTomatoCanInScene-v0']:
                task_description = "pick can"
            elif 'CokeCan' in env_name:
                task_description = "pick coke can"
            elif env_name in ['GraspSinglePepsiCanInScene-v0', 'GraspSingleUpRightPepsiCanInScene-v0']:
                task_description = "pick pepsi can"
            elif env_name == 'GraspSingleYCBBoxInScene-v0':
                task_description = "pick box"
            elif env_name == 'KnockSingleYCBBoxOverInScene-v0':
                task_description = "knock box over"
            else:
                raise NotImplementedError()
            if instruction_override is not None:
                task_description = instruction_override
            print(task_description)
        
            # Reset RT-1 model
            rt1_model.reset(task_description)
        
            timestep = 0
            success = "failure"
            # Step the environment
            while not (predicted_terminated or truncated):
                cur_gripper_pose_at_robot_base = env.agent.robot.pose.inv() * env.tcp.pose
                cur_gripper_closedness = env.agent.get_gripper_closedness()
                
                if timestep % action_repeat == 0:
                    raw_action, action = rt1_model.step(image, cur_gripper_pose_at_robot_base, cur_gripper_closedness)
                    predicted_actions.append(raw_action)
                    print(timestep, raw_action)
                    predicted_terminated = bool(action['terminate_episode'][0] > 0)
                else:
                    action = rt1_model.step_repeat_last_goal(cur_gripper_pose_at_robot_base, cur_gripper_closedness)
                
                obs, reward, terminated, truncated, info = env.step(
                    np.concatenate(
                        [action['world_vector'], 
                        action['rot_axangle'],
                        action['gripper_closedness_action']
                        ]
                    )
                )
                if terminated:
                    # For now, if at any step the episode is successful, we consider it a success
                    success = "success"
                image = obs['image']['overhead_camera']['rgb']
                images.append(image)
                timestep += 1

            ckpt_path_basename = ckpt_path if ckpt_path[-1] != '/' else ckpt_path[:-1]
            ckpt_path_basename = ckpt_path_basename.split('/')[-1]
            video_path = f'debug/{success}_obj_{obj_init_x}_{obj_init_y}.mp4'
            if not tmp_exp:
                video_path = 'results/' + video_path
            else:
                video_path = 'results_tmp/' + video_path 
            write_video(video_path, images, fps=5)


if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    os.environ['DISPLAY'] = ''
    # rgb_overlay_path = '/home/xuanlin/Real2Sim/ManiSkill2_real2sim/data/google_table_top_1.png'
    # env_name = 'GraspSingleUpRightCokeCanInScene-v0'
    # env_name = 'GraspSingleCokeCanInScene-v0'
    env_name = 'GraspSingleVerticalCokeCanInScene-v0'
    # env_name = 'GraspSingleUpRightOpenedCokeCanInScene-v0'
    # env_name = 'GraspSingleCokeCanWithDistractorInScene-v0'
    # env_name = 'GraspSingleOpenedCokeCanInScene-v0'
    # env_name = 'GraspSinglePepsiCanInScene-v0'
    # env_name = 'GraspSingleUpRightPepsiCanInScene-v0'
    # env_name = 'GraspSingleYCBSomeInScene-v0'
    rt1_main_ckpt_path = '/home/xuanlin/Real2Sim/robotics_transformer/trained_checkpoints/rt1main/'
    
    gpus = tf.config.list_physical_devices('GPU')
    tf.config.set_logical_device_configuration(
        gpus[0],
        [tf.config.LogicalDeviceConfiguration(memory_limit=4096)])

    # Baked_sc1_staging_table_616385
    # robot_init_x, robot_init_y = 0.32, 0.188
    # rob_init_quat = (Pose(q=[0, 0, 0, 1]) * Pose(q=euler2quat(0, 0, -0.01))).q
    # obj_init_x_range = np.linspace(-0.35, -0.1, 5)
    # obj_init_y_range = np.linspace(0.0, 0.4, 5)
    # rgb_overlay_path = '/home/xuanlin/Real2Sim/ManiSkill2_real2sim/data/google_table_top_1.png'
    # for env_name in ['GraspSingleVerticalCokeCanInScene-v0', 'GraspSingleCokeCanInScene-v0', 'GraspSingleUpRightOpenedCokeCanInScene-v0']:
    #     main(env_name, 'Baked_sc1_staging_table_616385', rgb_overlay_path=rgb_overlay_path,
    #          obj_init_x_range=obj_init_x_range, obj_init_y_range=obj_init_y_range,
    #          robot_init_x=robot_init_x, robot_init_y=robot_init_y, robot_init_quat=rob_init_quat)
        
    # # google robot pick coke can reproduce real
    robot_init_x, robot_init_y = 0.38, 0.20
    rob_init_quat = (Pose(q=[0, 0, 0, 1]) * Pose(q=euler2quat(0, 0, 0.003))).q
    obj_init_x_range = [10]
    obj_init_y_range = [10]
    rgb_overlay_path = '/home/xuanlin/Real2Sim/ManiSkill2_real2sim/data/real_impainting/google_vertical_coke_can_eval_1_cleanup.png'
    for env_name in ['GraspSingleVerticalOpenedCokeCanInScene-v0']:
        main(env_name, 'google_pick_coke_can_1', rgb_overlay_path=rgb_overlay_path,
             obj_init_x_range=obj_init_x_range, obj_init_y_range=obj_init_y_range,
             robot_init_x=robot_init_x, robot_init_y=robot_init_y, robot_init_quat=rob_init_quat)