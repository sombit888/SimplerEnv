#!/bin/bash

# Navigate to directory 

cd ManiSkill2_real2sim

pip install -e . 

cd .. 

pip install -e .

pip install tensorflow==2.15.0
pip install -r requirements_full_install.txt
pip install -r https://raw.githubusercontent.com/openvla/openvla/main/requirements-min.txt
pip install accelerate flash-attn mediapy