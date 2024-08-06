from typing import Optional, Sequence
import os
import matplotlib.pyplot as plt
import numpy as np
from transforms3d.euler import euler2axangle
from transformers import AutoModelForVision2Seq, AutoProcessor
from PIL import Image
import torch
import cv2 as cv


class FastWrongInference:
    def __init__(
        self,
        saved_model_path: str = "openvla/openvla-7b",
        unnorm_key: Optional[str] = None,
        policy_setup: str = "widowx_bridge",
        horizon: int = 1,
        pred_action_horizon: int = 1,
        exec_horizon: int = 1,
        image_size: list[int] = [224, 224],
        action_scale: float = 1.0,
    ) -> None:
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.image_size = image_size



    def reset(self, task_description: str) -> None:
        action = {}
        return 

    def step(
        self, image: np.ndarray, task_description: Optional[str] = None, *args, **kwargs
    ) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
        """
        # Input:
        #     image: np.ndarray of shape (H, W, 3), uint8
        #     task_description: Optional[str], task description; if different from previous task description, policy state is reset
        # Output:
        #     raw_action: dict; raw policy action output
        #     action: dict; processed action to be sent to the maniskill2 environment, with the following keys:
        #         - 'world_vector': np.ndarray of shape (3,), xyz translation of robot end-effector
        #         - 'rot_axangle': np.ndarray of shape (3,), axis-angle representation of end-effector rotation
        #         - 'gripper': np.ndarray of shape (1,), gripper action
        #         - 'terminate_episode': np.ndarray of shape (1,), 1 if episode should be terminated, 0 otherwise
        # """
        # if task_description is not None:
        #     if task_description != self.task_description:
        #         self.reset(task_description)

        assert image.dtype == np.uint8
        image = self._resize_image(image)
        action_wrong = {}
        action_wrong['gripper'] = np.array([0.0])
        action_wrong['terminate_episode'] = np.array([0.0]) 
        action_wrong['world_vector'] = np.array([0.0, 0.0, 0.0])
        action_wrong['rot_axangle'] = np.array([0.0, 0.0, 0.0,])

        return action_wrong, action_wrong

    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        image = cv.resize(image, tuple(self.image_size), interpolation=cv.INTER_AREA)
        return image

    def visualize_epoch(
        self, predicted_raw_actions: Sequence[np.ndarray], images: Sequence[np.ndarray], save_path: str
    ) -> None:
        return 