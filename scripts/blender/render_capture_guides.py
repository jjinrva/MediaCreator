from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


BODY_VIEWS = (
    ("body_front", Vector((0.0, -6.0, 1.7)), "Full body front framing with arms slightly away from the torso."),
    ("body_left", Vector((6.0, 0.0, 1.7)), "Left-side silhouette for overlap planning."),
    ("body_right", Vector((-6.0, 0.0, 1.7)), "Right-side silhouette for overlap planning."),
    ("body_back", Vector((0.0, 6.0, 1.7)), "Back-body framing for reconstruction coverage."),
    (
        "body_three_quarter",
        Vector((4.8, -4.8, 1.7)),
        "Three-quarter body framing to bridge front and side capture."
    ),
)

HEAD_VIEWS = (
    ("head_front", Vector((0.0, -2.1, 1.78)), "Face front with a visible hairline and neutral expression."),
    ("head_left", Vector((2.1, 0.0, 1.78)), "Face left close-up with the forehead and jawline visible."),
    ("head_right", Vector((-2.1, 0.0, 1.78)), "Face right close-up with the forehead and jawline visible."),
)


def parse_output_dir() -> Path:
    if "--" in sys.argv:
        index = sys.argv.index("--")
        args = sys.argv[index + 1 :]
        if args:
            return Path(args[0]).resolve()

    return Path(__file__).resolve().parents[2] / "docs" / "capture_guides" / "assets"


def reset_scene() -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 12
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new("GuideWorld")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
    background.inputs[1].default_value = 0.8
    return scene


def add_camera(scene: bpy.types.Scene) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new("GuideCamera")
    camera_data.type = "ORTHO"
    camera = bpy.data.objects.new("GuideCamera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    return camera


def aim_camera(
    camera: bpy.types.Object,
    location: Vector,
    target: Vector,
    ortho_scale: float,
) -> None:
    camera.location = location
    camera.data.ortho_scale = ortho_scale
    direction = target - location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_lights(scene: bpy.types.Scene) -> None:
    sun_data = bpy.data.lights.new("GuideSun", "SUN")
    sun_data.energy = 2.1
    sun = bpy.data.objects.new("GuideSun", sun_data)
    sun.rotation_euler = (math.radians(44), 0.0, math.radians(-28))
    scene.collection.objects.link(sun)

    fill_data = bpy.data.lights.new("GuideFill", "AREA")
    fill_data.energy = 700
    fill_data.shape = "RECTANGLE"
    fill_data.size = 3.0
    fill_data.size_y = 3.0
    fill = bpy.data.objects.new("GuideFill", fill_data)
    fill.location = (0.0, -2.5, 3.0)
    fill.rotation_euler = (math.radians(72), 0.0, 0.0)
    scene.collection.objects.link(fill)


def make_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    principled = material.node_tree.nodes["Principled BSDF"]
    principled.inputs["Base Color"].default_value = rgba
    principled.inputs["Roughness"].default_value = 0.88
    principled.inputs["Specular IOR Level"].default_value = 0.2
    return material


def add_mesh_object(
    primitive: str,
    *,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    material: bpy.types.Material,
    parent: bpy.types.Object,
) -> bpy.types.Object:
    if primitive == "cube":
        bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    elif primitive == "uv_sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=location, rotation=rotation)
    elif primitive == "cylinder":
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, location=location, rotation=rotation)
    elif primitive == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=20, location=location, rotation=rotation)
    else:
        raise ValueError(f"Unsupported primitive: {primitive}")

    obj = bpy.context.active_object
    obj.scale = scale
    obj.parent = parent
    obj.data.materials.append(material)
    return obj


def build_mannequin(
    scene: bpy.types.Scene,
    *,
    name: str,
    body_color: tuple[float, float, float, float],
    hairline_color: tuple[float, float, float, float],
    torso_scale: tuple[float, float, float],
    hip_scale: tuple[float, float, float],
    shoulder_width: float,
) -> list[bpy.types.Object]:
    root = bpy.data.objects.new(name, None)
    scene.collection.objects.link(root)

    body_material = make_material(f"{name}Body", body_color)
    accent_material = make_material(f"{name}Accent", hairline_color)
    eye_material = make_material(f"{name}Eye", (0.18, 0.18, 0.2, 1.0))

    objects: list[bpy.types.Object] = [root]

    objects.append(
        add_mesh_object(
            "cube",
            location=(0.0, 0.0, 1.26),
            scale=torso_scale,
            material=body_material,
            parent=root,
        )
    )
    objects.append(
        add_mesh_object(
            "cube",
            location=(0.0, 0.0, 0.92),
            scale=hip_scale,
            material=body_material,
            parent=root,
        )
    )
    objects.append(
        add_mesh_object(
            "uv_sphere",
            location=(0.0, 0.0, 1.78),
            scale=(0.18, 0.18, 0.2),
            material=body_material,
            parent=root,
        )
    )
    objects.append(
        add_mesh_object(
            "cylinder",
            location=(0.0, 0.0, 1.54),
            scale=(0.065, 0.065, 0.13),
            material=body_material,
            parent=root,
        )
    )
    objects.append(
        add_mesh_object(
            "cube",
            location=(0.0, -0.11, 1.93),
            scale=(0.12, 0.02, 0.03),
            material=accent_material,
            parent=root,
        )
    )
    objects.append(
        add_mesh_object(
            "uv_sphere",
            location=(0.06, -0.16, 1.8),
            scale=(0.025, 0.025, 0.025),
            material=eye_material,
            parent=root,
        )
    )
    objects.append(
        add_mesh_object(
            "uv_sphere",
            location=(-0.06, -0.16, 1.8),
            scale=(0.025, 0.025, 0.025),
            material=eye_material,
            parent=root,
        )
    )
    objects.append(
        add_mesh_object(
            "cone",
            location=(0.0, -0.18, 1.74),
            rotation=(math.radians(90), 0.0, 0.0),
            scale=(0.04, 0.04, 0.08),
            material=body_material,
            parent=root,
        )
    )

    for side in (-1, 1):
        arm_direction = math.radians(60 * side)
        forearm_direction = math.radians(75 * side)
        upper_leg_x = 0.14 * side
        arm_x = shoulder_width * side

        objects.append(
            add_mesh_object(
                "cylinder",
                location=(arm_x, 0.0, 1.32),
                rotation=(0.0, arm_direction, 0.0),
                scale=(0.058, 0.058, 0.28),
                material=body_material,
                parent=root,
            )
        )
        objects.append(
            add_mesh_object(
                "cylinder",
                location=(0.63 * side, 0.0, 1.02),
                rotation=(0.0, forearm_direction, 0.0),
                scale=(0.05, 0.05, 0.24),
                material=body_material,
                parent=root,
            )
        )
        objects.append(
            add_mesh_object(
                "uv_sphere",
                location=(0.78 * side, 0.0, 0.78),
                scale=(0.055, 0.055, 0.055),
                material=body_material,
                parent=root,
            )
        )
        objects.append(
            add_mesh_object(
                "cylinder",
                location=(upper_leg_x, 0.0, 0.54),
                scale=(0.075, 0.075, 0.38),
                material=body_material,
                parent=root,
            )
        )
        objects.append(
            add_mesh_object(
                "cylinder",
                location=(upper_leg_x, 0.0, 0.14),
                scale=(0.06, 0.06, 0.32),
                material=body_material,
                parent=root,
            )
        )
        objects.append(
            add_mesh_object(
                "cube",
                location=(upper_leg_x, -0.1, -0.14),
                scale=(0.11, 0.18, 0.05),
                material=body_material,
                parent=root,
            )
        )

    return objects


def set_visibility(objects: list[bpy.types.Object], visible: bool) -> None:
    for obj in objects:
        obj.hide_render = not visible
        obj.hide_viewport = not visible


def render_variant(
    scene: bpy.types.Scene,
    camera: bpy.types.Object,
    output_dir: Path,
    variant_name: str,
    objects: list[bpy.types.Object],
) -> None:
    set_visibility(objects, True)
    target_body = Vector((0.0, 0.0, 1.0))
    target_head = Vector((0.0, 0.0, 1.78))

    for view_name, location, _caption in BODY_VIEWS:
        aim_camera(camera, location, target_body, ortho_scale=3.8)
        scene.render.filepath = str(output_dir / f"{variant_name}_{view_name}.png")
        bpy.ops.render.render(write_still=True)

    for view_name, location, _caption in HEAD_VIEWS:
        aim_camera(camera, location, target_head, ortho_scale=1.45)
        scene.render.filepath = str(output_dir / f"{variant_name}_{view_name}.png")
        bpy.ops.render.render(write_still=True)

    set_visibility(objects, False)


def main() -> None:
    output_dir = parse_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    scene = reset_scene()
    camera = add_camera(scene)
    add_lights(scene)

    male_objects = build_mannequin(
        scene,
        name="MaleGuide",
        body_color=(0.77, 0.79, 0.83, 1.0),
        hairline_color=(0.42, 0.45, 0.52, 1.0),
        torso_scale=(0.36, 0.21, 0.42),
        hip_scale=(0.24, 0.18, 0.15),
        shoulder_width=0.38,
    )
    female_objects = build_mannequin(
        scene,
        name="FemaleGuide",
        body_color=(0.84, 0.76, 0.75, 1.0),
        hairline_color=(0.56, 0.38, 0.34, 1.0),
        torso_scale=(0.3, 0.18, 0.4),
        hip_scale=(0.28, 0.2, 0.16),
        shoulder_width=0.32,
    )

    set_visibility(male_objects, False)
    set_visibility(female_objects, False)

    render_variant(scene, camera, output_dir, "male", male_objects)
    render_variant(scene, camera, output_dir, "female", female_objects)

    print(f"Rendered capture guide assets to {output_dir}")


if __name__ == "__main__":
    main()
