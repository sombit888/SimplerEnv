## Installation Instruction to evaluate OpenVLA on Simpler-Env 
- git clone the repo with ` git clone https://github.com/sombit888/SimplerEnv.git --recursive`
- create a micromamba env with python=3.10 eg.
 `micromamba  create  -n  simpler_slurm  -f  env.yml  --yes`   
- activate the environment 	` micromamba activate simpler_slurm`
- `bash install_script.sh` , install maniskill, and simpler_env. Also install libraries to evaluate rt1. Can avoid installing other libraries only to evaluate Openvla
- Currently works without denoising on both L4 and A100-40G
## Evaluation
- `bash scripts/openvla/{x}` based on what you want to evaluate. 
	- Visual Matching : To evaluate the overall performance with greenscreen matching to minimize real-sim gap
	- Variant_agg : To evaluate various changes to lighting, scene, camera angles 
## Adding New policy 
- `cd simpler_env/policies/` 
- create folder and a 'model.py' inside it. eg `openvla, openvla_model.py` 
- 'model.py' should have `reset, step, and visualize_epoch` attributes. 
- import the file in `simpler_env/main_inference.py` and modify accordingly
##  Run specific envaluations
- ` bash scripts/openvla/openvla_ood_objects.sh`
- 
TODOS to add additional scripts after rechecking

## Obtain Simpler-Env eval metrics
- `python tools/calc_metrics_evaluation_videos.py`, pass the results dir in args/change the default.

## Obtain Specific Evaluations
	TODO 