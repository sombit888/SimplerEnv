gpu_id=0
declare -a policy_models=("openvla")
declare -a ckpt_path=("openvla/openvla-7b") ### ckpt_path on hf
declare -a logging_dir=("/scratch/sombit_dey/results_openvla")

declare -a coke_can_options_arr=("lr_switch=True") ## no need to test for different orientations

# URDF variations
# declare -a urdf_version_arr=(None "recolor_tabletop_visual_matching_1" "recolor_tabletop_visual_matching_2" "recolor_cabinet_visual_matching_1")
declare -a urdf_version_arr=(None "recolor_tabletop_visual_matching_1" )

scene_name=google_pick_coke_can_1_v4

declare -a env_arr=("GraspSingleOpenedCokeCanAltGoogleCameraInScene-v0" \
                   "GraspSingleOpenedCokeCanAltGoogleCamera2InScene-v0")



do for env_name in "${env_arr[@]}";

do for ckpt_path in "${arr[@]}";

do CUDA_VISIBLE_DEVICES=${gpu_id} python simpler_env/main_inference.py --policy-model openvla --ckpt-path ${ckpt_path} \
  --robot google_robot_static \
  --control-freq 3 --sim-freq 513 --max-episode-steps 80 \
  --env-name ${env_name} --scene-name ${scene_name} \
  --robot-init-x 0.35 0.35 1 --robot-init-y 0.20 0.20 1 --obj-init-x -0.35 -0.12 5 --obj-init-y -0.02 0.42 5 \
  --robot-init-rot-quat-center 0 0 0 1 --robot-init-rot-rpy-range 0 0 1 0 0 1 0 0 1 \
  --additional-env-build-kwargs ${coke_can_option};

done

done

done
