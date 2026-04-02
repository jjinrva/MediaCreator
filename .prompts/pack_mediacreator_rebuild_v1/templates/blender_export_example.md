
# Blender glTF export example

```py
import bpy

def export_glb(filepath: str) -> None:
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_texcoords=True,
        export_normals=True,
        export_tangents=True,
        export_materials='EXPORT',
        export_colors=True,
        export_yup=True,
        export_animations=True,
        export_skins=True,
        export_morph=True,
        export_morph_normal=True,
        export_morph_tangent=True,
    )
```
