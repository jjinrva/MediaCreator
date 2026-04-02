from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


BODY_DEFAULTS = {
    "height_scale": 1.0,
    "shoulder_width": 1.0,
    "chest_volume": 1.0,
    "waist_width": 1.0,
    "hip_width": 1.0,
    "upper_arm_volume": 1.0,
    "thigh_volume": 1.0,
    "calf_volume": 1.0,
}

POSE_BONE_MAP = {
    "upper_arm_l_pitch_deg": "upper_arm_fk.L",
    "upper_arm_r_pitch_deg": "upper_arm_fk.R",
    "thigh_l_pitch_deg": "thigh_fk.L",
    "thigh_r_pitch_deg": "thigh_fk.R",
}


def parse_payload() -> dict[str, object]:
    if "--" not in sys.argv:
        raise SystemExit("Missing Blender payload path.")

    payload_path = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    return json.loads(payload_path.read_text(encoding="utf-8"))


def reset_scene() -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    return scene


def enable_rigify() -> None:
    bpy.ops.preferences.addon_enable(module="rigify")


def make_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    principled = material.node_tree.nodes["Principled BSDF"]
    principled.inputs["Base Color"].default_value = rgba
    principled.inputs["Roughness"].default_value = 0.82
    principled.inputs["Specular IOR Level"].default_value = 0.2
    return material


def add_mesh_object(
    primitive: str,
    *,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    material: bpy.types.Material,
) -> bpy.types.Object:
    if primitive == "cube":
        bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    elif primitive == "uv_sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=24,
            ring_count=12,
            location=location,
            rotation=rotation,
        )
    elif primitive == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=20,
            location=location,
            rotation=rotation,
        )
    else:
        raise ValueError(f"Unsupported primitive: {primitive}")

    obj = bpy.context.active_object
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def build_proxy_mesh() -> bpy.types.Object:
    body_material = make_material("ProxyBody", (0.73, 0.64, 0.58, 1.0))
    accent_material = make_material("ProxyAccent", (0.21, 0.24, 0.31, 1.0))

    mesh_parts: list[bpy.types.Object] = []
    mesh_parts.append(
        add_mesh_object(
            "cube",
            location=(0.0, 0.0, 1.28),
            scale=(0.18, 0.12, 0.34),
            material=body_material,
        )
    )
    mesh_parts.append(
        add_mesh_object(
            "cube",
            location=(0.0, 0.0, 0.92),
            scale=(0.16, 0.11, 0.24),
            material=body_material,
        )
    )
    mesh_parts.append(
        add_mesh_object(
            "uv_sphere",
            location=(0.0, 0.0, 1.72),
            scale=(0.16, 0.16, 0.19),
            material=body_material,
        )
    )
    mesh_parts.append(
        add_mesh_object(
            "cube",
            location=(0.0, -0.02, 1.88),
            scale=(0.1, 0.05, 0.03),
            material=accent_material,
        )
    )

    for side in (-1, 1):
        mesh_parts.append(
            add_mesh_object(
                "cylinder",
                location=(0.28 * side, 0.0, 1.28),
                rotation=(0.0, 0.0, math.radians(12 * side)),
                scale=(0.045, 0.045, 0.23),
                material=body_material,
            )
        )
        mesh_parts.append(
            add_mesh_object(
                "cylinder",
                location=(0.43 * side, 0.0, 0.98),
                rotation=(0.0, 0.0, math.radians(8 * side)),
                scale=(0.04, 0.04, 0.21),
                material=body_material,
            )
        )
        mesh_parts.append(
            add_mesh_object(
                "cylinder",
                location=(0.12 * side, 0.0, 0.62),
                scale=(0.06, 0.06, 0.27),
                material=body_material,
            )
        )
        mesh_parts.append(
            add_mesh_object(
                "cylinder",
                location=(0.12 * side, 0.0, 0.16),
                scale=(0.05, 0.05, 0.24),
                material=body_material,
            )
        )

    bpy.ops.object.select_all(action="DESELECT")
    for obj in mesh_parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()

    mesh_obj = bpy.context.active_object
    mesh_obj.name = "CharacterProxyMesh"
    bpy.ops.object.shade_smooth()
    return mesh_obj


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _span_weight(value: float, start: float, end: float) -> float:
    if value <= start:
        return 0.0
    if value >= end:
        return 1.0
    return (value - start) / (end - start)


def _band_weight(value: float, lower: float, center: float, upper: float) -> float:
    if value <= lower or value >= upper:
        return 0.0
    if value == center:
        return 1.0
    if value < center:
        return (value - lower) / (center - lower)
    return (upper - value) / (upper - center)


def add_body_shape_keys(mesh_obj: bpy.types.Object) -> None:
    basis = mesh_obj.shape_key_add(name="Basis", from_mix=False)
    basis_coordinates = [point.co.copy() for point in basis.data]

    for parameter_key in BODY_DEFAULTS:
        key_block = mesh_obj.shape_key_add(name=parameter_key, from_mix=False)
        key_block.slider_min = -0.5
        key_block.slider_max = 0.5

        for index, base in enumerate(basis_coordinates):
            co = base.copy()

            if parameter_key == "height_scale" and co.z > 0.0:
                co.z *= 2.0
            elif parameter_key == "shoulder_width":
                shoulder_weight = _span_weight(co.z, 1.05, 1.55)
                co.x *= 1.0 + shoulder_weight
            elif parameter_key == "chest_volume":
                chest_weight = _band_weight(co.z, 1.0, 1.28, 1.55)
                co.y *= 1.0 + (0.85 * chest_weight)
            elif parameter_key == "waist_width":
                waist_weight = _band_weight(co.z, 0.75, 1.0, 1.2)
                co.x *= 1.0 + (0.8 * waist_weight)
            elif parameter_key == "hip_width":
                hip_weight = _band_weight(co.z, 0.55, 0.86, 1.08)
                co.x *= 1.0 + hip_weight
            elif parameter_key == "upper_arm_volume":
                arm_weight = _band_weight(abs(co.x), 0.2, 0.36, 0.52) * _band_weight(
                    co.z, 0.9, 1.16, 1.42
                )
                co.y *= 1.0 + (0.9 * arm_weight)
            elif parameter_key == "thigh_volume":
                thigh_weight = _band_weight(abs(co.x), 0.03, 0.13, 0.26) * _band_weight(
                    co.z, 0.3, 0.62, 0.94
                )
                co.y *= 1.0 + (0.9 * thigh_weight)
            elif parameter_key == "calf_volume":
                calf_weight = _band_weight(abs(co.x), 0.03, 0.12, 0.23) * _band_weight(
                    co.z, -0.02, 0.18, 0.42
                )
                co.y *= 1.0 + (0.8 * calf_weight)

            key_block.data[index].co = co


def apply_body_values(mesh_obj: bpy.types.Object, body_values: dict[str, float]) -> None:
    if mesh_obj.data.shape_keys is None:
        return

    key_blocks = mesh_obj.data.shape_keys.key_blocks
    for key, default_value in BODY_DEFAULTS.items():
        if key not in key_blocks:
            continue

        target_value = float(body_values.get(key, default_value))
        key_blocks[key].value = _clamp(target_value - default_value, -0.5, 0.5)


def generate_rigify_rig() -> bpy.types.Object:
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.location = (0.0, 0.0, 0.0)
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.rigify_generate()
    bpy.ops.object.mode_set(mode="OBJECT")

    rig = bpy.data.objects["rig"]
    metarig.hide_set(True)
    metarig.hide_render = True
    return rig


def bind_mesh_to_rig(mesh_obj: bpy.types.Object, rig_obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    rig_obj.select_set(True)
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def apply_pose_values(rig_obj: bpy.types.Object, pose_values: dict[str, float]) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    rig_obj.select_set(True)
    bpy.context.view_layer.objects.active = rig_obj
    bpy.ops.object.mode_set(mode="POSE")

    for parameter_key, bone_name in POSE_BONE_MAP.items():
        pose_bone = rig_obj.pose.bones.get(bone_name)
        if pose_bone is None:
            continue

        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler.x = math.radians(float(pose_values.get(parameter_key, 0.0)))

    bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.pose.armature_apply(selected=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def triangulate_mesh(mesh_obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode="OBJECT")


def export_glb(mesh_obj: bpy.types.Object, rig_obj: bpy.types.Object, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    rig_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    bpy.ops.export_scene.gltf(
        filepath=str(output_path),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_normals=True,
        export_tangents=True,
        export_skins=True,
        export_morph=True,
        export_morph_normal=True,
        export_morph_tangent=True,
        export_animations=True,
        export_current_frame=True,
        export_materials="EXPORT",
    )


def main() -> None:
    payload = parse_payload()
    reset_scene()
    enable_rigify()

    body_values = dict[str, float](payload["body_values"])
    pose_values = dict[str, float](payload["pose_values"])
    output_path = Path(str(payload["output_preview_glb_path"])).resolve()

    mesh_obj = build_proxy_mesh()
    add_body_shape_keys(mesh_obj)
    apply_body_values(mesh_obj, body_values)
    rig_obj = generate_rigify_rig()
    bind_mesh_to_rig(mesh_obj, rig_obj)
    apply_pose_values(rig_obj, pose_values)
    triangulate_mesh(mesh_obj)
    export_glb(mesh_obj, rig_obj, output_path)


if __name__ == "__main__":
    main()
