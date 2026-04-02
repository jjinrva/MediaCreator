from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import cast

import bpy

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "scripts" / "blender"))

from rigify_proxy_export import (  # noqa: E402
    add_body_shape_keys,
    apply_base_color_texture,
    apply_body_values,
    apply_pose_values,
    bind_mesh_to_rig,
    build_proxy_mesh,
    enable_rigify,
    generate_rigify_rig,
    reset_scene,
)

CONTROL_BONES = (
    "spine_fk",
    "spine_fk.001",
    "spine_fk.002",
    "spine_fk.003",
    "upper_arm_fk.L",
    "upper_arm_fk.R",
    "forearm_fk.L",
    "forearm_fk.R",
    "thigh_fk.L",
    "thigh_fk.R",
    "shin_fk.L",
    "shin_fk.R",
    "foot_fk.L",
    "foot_fk.R",
    "head",
)

KEY_POSES: dict[str, dict[str, object]] = {
    "neutral-stance": {
        "bones": {},
        "rig_location": (0.0, 0.0, 0.0),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "breath-shift": {
        "bones": {
            "spine_fk.002": (2.0, 0.0, 0.0),
            "upper_arm_fk.L": (6.0, 0.0, -4.0),
            "upper_arm_fk.R": (6.0, 0.0, 4.0),
        },
        "rig_location": (0.0, 0.0, 0.03),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "left-contact": {
        "bones": {
            "thigh_fk.L": (26.0, 0.0, 0.0),
            "thigh_fk.R": (-18.0, 0.0, 0.0),
            "shin_fk.R": (22.0, 0.0, 0.0),
            "upper_arm_fk.L": (-18.0, 0.0, -6.0),
            "upper_arm_fk.R": (18.0, 0.0, 6.0),
        },
        "rig_location": (-0.08, 0.0, 0.0),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "passing": {
        "bones": {
            "thigh_fk.L": (8.0, 0.0, 0.0),
            "thigh_fk.R": (8.0, 0.0, 0.0),
            "shin_fk.L": (8.0, 0.0, 0.0),
            "shin_fk.R": (8.0, 0.0, 0.0),
            "upper_arm_fk.L": (4.0, 0.0, -3.0),
            "upper_arm_fk.R": (4.0, 0.0, 3.0),
        },
        "rig_location": (0.0, 0.0, 0.01),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "right-contact": {
        "bones": {
            "thigh_fk.L": (-18.0, 0.0, 0.0),
            "thigh_fk.R": (26.0, 0.0, 0.0),
            "shin_fk.L": (22.0, 0.0, 0.0),
            "upper_arm_fk.L": (18.0, 0.0, -6.0),
            "upper_arm_fk.R": (-18.0, 0.0, 6.0),
        },
        "rig_location": (0.08, 0.0, 0.0),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "crouch": {
        "bones": {
            "spine_fk.001": (-8.0, 0.0, 0.0),
            "thigh_fk.L": (-34.0, 0.0, 0.0),
            "thigh_fk.R": (-34.0, 0.0, 0.0),
            "shin_fk.L": (42.0, 0.0, 0.0),
            "shin_fk.R": (42.0, 0.0, 0.0),
            "upper_arm_fk.L": (-16.0, 0.0, -8.0),
            "upper_arm_fk.R": (-16.0, 0.0, 8.0),
        },
        "rig_location": (0.0, 0.0, -0.12),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "launch": {
        "bones": {
            "spine_fk.002": (10.0, 0.0, 0.0),
            "thigh_fk.L": (18.0, 0.0, 0.0),
            "thigh_fk.R": (18.0, 0.0, 0.0),
            "shin_fk.L": (8.0, 0.0, 0.0),
            "shin_fk.R": (8.0, 0.0, 0.0),
            "upper_arm_fk.L": (45.0, 0.0, -12.0),
            "upper_arm_fk.R": (45.0, 0.0, 12.0),
        },
        "rig_location": (0.0, 0.0, 0.14),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "airborne": {
        "bones": {
            "spine_fk.002": (6.0, 0.0, 0.0),
            "thigh_fk.L": (24.0, 0.0, 0.0),
            "thigh_fk.R": (24.0, 0.0, 0.0),
            "shin_fk.L": (24.0, 0.0, 0.0),
            "shin_fk.R": (24.0, 0.0, 0.0),
            "upper_arm_fk.L": (58.0, 0.0, -10.0),
            "upper_arm_fk.R": (58.0, 0.0, 10.0),
        },
        "rig_location": (0.0, 0.0, 0.34),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "landing": {
        "bones": {
            "spine_fk.001": (-6.0, 0.0, 0.0),
            "thigh_fk.L": (-20.0, 0.0, 0.0),
            "thigh_fk.R": (-20.0, 0.0, 0.0),
            "shin_fk.L": (34.0, 0.0, 0.0),
            "shin_fk.R": (34.0, 0.0, 0.0),
            "upper_arm_fk.L": (8.0, 0.0, -8.0),
            "upper_arm_fk.R": (8.0, 0.0, 8.0),
        },
        "rig_location": (0.0, 0.0, -0.04),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "stand": {
        "bones": {},
        "rig_location": (0.0, 0.0, 0.0),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "knees-bend": {
        "bones": {
            "thigh_fk.L": (-22.0, 0.0, 0.0),
            "thigh_fk.R": (-22.0, 0.0, 0.0),
            "shin_fk.L": (24.0, 0.0, 0.0),
            "shin_fk.R": (24.0, 0.0, 0.0),
        },
        "rig_location": (0.0, 0.0, -0.1),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "seat-contact": {
        "bones": {
            "thigh_fk.L": (-66.0, 0.0, 0.0),
            "thigh_fk.R": (-66.0, 0.0, 0.0),
            "shin_fk.L": (84.0, 0.0, 0.0),
            "shin_fk.R": (84.0, 0.0, 0.0),
            "spine_fk.001": (-10.0, 0.0, 0.0),
        },
        "rig_location": (0.0, 0.0, -0.22),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "seated-idle": {
        "bones": {
            "thigh_fk.L": (-72.0, 0.0, 0.0),
            "thigh_fk.R": (-72.0, 0.0, 0.0),
            "shin_fk.L": (88.0, 0.0, 0.0),
            "shin_fk.R": (88.0, 0.0, 0.0),
        },
        "rig_location": (0.0, 0.0, -0.24),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "forward-stance": {
        "bones": {},
        "rig_location": (0.0, 0.0, 0.0),
        "rig_rotation_deg": (0.0, 0.0, 0.0),
    },
    "hips-rotate": {
        "bones": {
            "spine_fk.001": (0.0, 0.0, 12.0),
            "upper_arm_fk.L": (10.0, 0.0, -8.0),
            "upper_arm_fk.R": (10.0, 0.0, 8.0),
        },
        "rig_location": (0.0, 0.0, 0.0),
        "rig_rotation_deg": (0.0, 0.0, 28.0),
    },
    "full-turn": {
        "bones": {
            "spine_fk.001": (0.0, 0.0, 18.0),
            "upper_arm_fk.L": (12.0, 0.0, -8.0),
            "upper_arm_fk.R": (12.0, 0.0, 8.0),
        },
        "rig_location": (0.0, 0.0, 0.0),
        "rig_rotation_deg": (0.0, 0.0, 90.0),
    },
}


def parse_payload() -> dict[str, object]:
    if "--" not in sys.argv:
        raise SystemExit("Missing Blender payload path.")

    payload_path = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    return json.loads(payload_path.read_text(encoding="utf-8"))


def _set_material_color(obj: bpy.types.Object, rgba: tuple[float, float, float, float]) -> None:
    material = bpy.data.materials.new(name=obj.name)
    material.use_nodes = True
    principled = material.node_tree.nodes["Principled BSDF"]
    principled.inputs["Base Color"].default_value = rgba
    principled.inputs["Roughness"].default_value = 0.85
    obj.data.materials.clear()
    obj.data.materials.append(material)


def add_stage() -> None:
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    _set_material_color(ground, (0.84, 0.82, 0.78, 1.0))

    bpy.ops.object.light_add(type="SUN", location=(3.0, -4.0, 6.0))
    sun = bpy.context.active_object
    sun.data.energy = 2.3
    sun.rotation_euler = (math.radians(52.0), 0.0, math.radians(36.0))

    bpy.ops.object.light_add(type="AREA", location=(0.0, -2.4, 2.8))
    fill = bpy.context.active_object
    fill.data.energy = 1800.0
    fill.data.shape = "RECTANGLE"
    fill.data.size = 3.0
    fill.data.size_y = 1.8
    fill.rotation_euler = (math.radians(72.0), 0.0, 0.0)


def add_camera() -> None:
    bpy.ops.object.camera_add(location=(0.0, -4.8, 1.65))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(79.0), 0.0, 0.0)
    camera.data.lens = 42
    bpy.context.scene.camera = camera


def configure_render(
    scene: bpy.types.Scene,
    *,
    fps: int,
    frame_end: int,
    height: int,
    output_path: Path,
    width: int,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = 8
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = frame_end
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.audio_codec = "NONE"
    scene.render.filepath = str(output_path)
    if scene.world is None:
        scene.world = bpy.data.worlds.new("MediaCreatorWorld")
    scene.world.color = (0.98, 0.97, 0.95)


def _apply_pose_state(
    rig_obj: bpy.types.Object,
    *,
    bone_rotations_deg: dict[str, tuple[float, float, float]],
) -> None:
    for bone_name in CONTROL_BONES:
        pose_bone = rig_obj.pose.bones.get(bone_name)
        if pose_bone is None:
            continue
        pose_bone.rotation_mode = "XYZ"
        rotation_deg = bone_rotations_deg.get(bone_name, (0.0, 0.0, 0.0))
        pose_bone.rotation_euler = tuple(math.radians(value) for value in rotation_deg)


def _insert_pose_keyframes(rig_obj: bpy.types.Object, frame: int) -> None:
    rig_obj.keyframe_insert(data_path="location", frame=frame)
    rig_obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    for bone_name in CONTROL_BONES:
        pose_bone = rig_obj.pose.bones.get(bone_name)
        if pose_bone is None:
            continue
        pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame)


def _sequence_frames(frame_end: int, pose_count: int) -> list[int]:
    if pose_count <= 1:
        return [1]
    return [
        int(round(1 + ((frame_end - 1) * index / (pose_count - 1))))
        for index in range(pose_count)
    ]


def _set_linear_interpolation(rig_obj: bpy.types.Object) -> None:
    animation_data = rig_obj.animation_data
    if animation_data is None or animation_data.action is None:
        return

    for fcurve in animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = "LINEAR"


def animate_motion(
    scene: bpy.types.Scene,
    rig_obj: bpy.types.Object,
    *,
    duration_seconds: float,
    fps: int,
    motion_payload_path: Path,
) -> None:
    payload = json.loads(motion_payload_path.read_text(encoding="utf-8"))
    action_payload = payload.get("action_payload", {})
    key_pose_sequence = action_payload.get("key_pose_sequence", ["neutral-stance"])
    if not isinstance(key_pose_sequence, list) or not key_pose_sequence:
        key_pose_sequence = ["neutral-stance"]

    frame_end = max(12, int(round(duration_seconds * fps)))
    scene.frame_start = 1
    scene.frame_end = frame_end
    rig_obj.animation_data_clear()
    rig_obj.location = (0.0, 0.0, 0.0)
    rig_obj.rotation_mode = "XYZ"
    rig_obj.rotation_euler = (0.0, 0.0, 0.0)

    for pose_name, frame in zip(key_pose_sequence, _sequence_frames(frame_end, len(key_pose_sequence))):
        pose = KEY_POSES.get(str(pose_name), KEY_POSES["neutral-stance"])
        rig_obj.location = tuple(float(value) for value in pose["rig_location"])
        rig_obj.rotation_euler = tuple(
            math.radians(float(value))
            for value in pose["rig_rotation_deg"]
        )
        pose_bones = cast(dict[str, tuple[float, float, float]], pose["bones"])
        _apply_pose_state(
            rig_obj,
            bone_rotations_deg={
                bone_name: tuple(float(value) for value in rotation)
                for bone_name, rotation in pose_bones.items()
            },
        )
        _insert_pose_keyframes(rig_obj, frame)

    _set_linear_interpolation(rig_obj)
    scene.frame_set(1)


def main() -> None:
    payload = parse_payload()
    scene = reset_scene()
    enable_rigify()

    mesh_obj = build_proxy_mesh()
    add_body_shape_keys(mesh_obj)
    apply_body_values(mesh_obj, dict(cast(dict[str, float], payload["body_values"])))
    apply_base_color_texture(mesh_obj, str(payload.get("base_color_texture_path") or ""))
    rig_obj = generate_rigify_rig()
    bind_mesh_to_rig(mesh_obj, rig_obj)
    apply_pose_values(rig_obj, dict(cast(dict[str, float], payload["pose_values"])))
    add_stage()
    add_camera()
    animate_motion(
        scene,
        rig_obj,
        duration_seconds=float(payload["duration_seconds"]),
        fps=int(payload["fps"]),
        motion_payload_path=Path(str(payload["motion_payload_path"])).resolve(),
    )
    configure_render(
        scene,
        fps=int(payload["fps"]),
        frame_end=scene.frame_end,
        height=int(payload["resolution_height"]),
        output_path=Path(str(payload["output_video_path"])).resolve(),
        width=int(payload["resolution_width"]),
    )
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
