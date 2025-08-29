# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Add click network groups to the cli command"""

import click

import tao_cli.common

from tao_cli.cli_actions.network_click_wrapper import create_click_group


@click.group()
@click.version_option(package_name="nvidia-tao-client")
@click.pass_context
def cli(ctx):
    """Create base tao click group"""
    pass


cli.add_command(tao_cli.common.login)
cli.add_command(tao_cli.common.get_gpu_types)

# TF2 CV networks
for tf2_network_name in set(["efficientdet_tf2", "classification_tf2"]):
    click_group = create_click_group(
        tf2_network_name, f"Create {tf2_network_name} click group"
    )
    cli.add_command(click_group)

# PYTORCH CV networks
for pyt_network_name in set(
    [
        "action_recognition",
        "bevfusion",
        "classification_pyt",
        "grounding_dino",
        "mal",
        "ml_recog",
        "mask2former",
        "mask_grounding_dino",
        "ocdnet",
        "ocrnet",
        "optical_inspection",
        "pointpillars",
        "pose_classification",
        "re_identification",
        "segformer",
        "deformable_detr",
        "dino",
        "rtdetr",
        "visual_changenet",
        "centerpose",
        "stylegan_xl",
        "nvdinov2"
    ]
):
    click_group = create_click_group(
        pyt_network_name, f"Create {pyt_network_name} click group"
    )
    cli.add_command(click_group)

# Data Services
for ds_network_name in set(
    ["annotations", "analytics", "auto_label", "augmentation", "image"]
):
    click_group = create_click_group(
        ds_network_name, f"Create {ds_network_name} click group"
    )
    cli.add_command(click_group)

# Maxine CV network
for ds_network_name in set(["maxine_eye_contact"]):
    click_group = create_click_group(
        ds_network_name, f"Create {ds_network_name} click group"
    )
    cli.add_command(click_group)

if __name__ == "__main__":
    cli()
