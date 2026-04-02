export const DOCS_GUIDE_RELATIVE_PATH = "docs/capture_guides/capture_guide.md";
export const RENDER_SCRIPT_RELATIVE_PATH = "scripts/blender/render_capture_guides.sh";
export const BLENDER_SCRIPT_RELATIVE_PATH = "scripts/blender/render_capture_guides.py";
export const ASSET_DIRECTORY_RELATIVE_PATH = "docs/capture_guides/assets";

export const CAPTURE_REQUIREMENTS = [
  { label: "LoRA-ready set", value: "20-30 sharp photos with a neutral expression and repeatable lighting" },
  { label: "High-detail 3D set", value: "60-120+ sharp photos, because later reconstruction needs far more coverage than LoRA" },
  { label: "Full-body distance", value: "3-4 meters from the subject with the camera near chest height" },
  { label: "Head close-up distance", value: "0.8-1.2 meters so the hairline, ears, and jawline stay readable" },
  { label: "Frame overlap", value: "60-70% overlap between neighboring shots so later geometry can bridge views cleanly" }
] as const;

export const CAPTURE_STEPS = [
  "Start with a full-body sweep of 12-16 photos around the subject in roughly 30-degree steps.",
  "Add 6-8 head close-ups after the body sweep: front, both three-quarter angles, both profiles, and two extra shots if hair hides the ears or jawline.",
  "Keep the face neutral, the mouth closed, and the eyes open so later face and expression phases start from a stable baseline.",
  "Keep both arms 10-15 cm away from the torso with relaxed hands so the body silhouette reads clearly.",
  "Pull hair off the forehead and away from the ears for at least the head pass so the hairline stays visible."
] as const;

export const LIGHTING_AND_WARDROBE = [
  "Use bright diffuse daylight or two soft lights at about 45 degrees from the subject.",
  "Wear fitted matte clothing in solid colors so the torso, hips, elbows, and knees are easy to read.",
  "Avoid hats, sunglasses, glossy jackets, sequins, and loose outerwear that hides the body outline.",
  "Lock focus if possible and keep every frame sharp; motion blur and focus hunting weaken both LoRA and later 3D work."
] as const;

export const BACKGROUNDS_TO_AVOID = [
  "Mirrors, windows behind the subject, and bright backlighting",
  "Busy wallpaper, shelves, clutter, or other people moving through frame",
  "Deep shadows that hide the jaw, neck, armpits, or clothing silhouette",
  "Patterned floors or reflective surfaces that compete with the body edges"
] as const;

export const RISK_NOTES = [
  "LoRA training can start from the smaller set, but later high-detail 3D phases need the larger set up front if you want strong geometry and texture recovery.",
  "Long hair, loose garments, and reflective materials usually need more than the minimum photo count because they hide or distort the silhouette."
] as const;

export type CaptureAsset = {
  alt: string;
  caption: string;
  fileName: string;
};

export type CaptureAssetGroup = {
  description: string;
  title: string;
  assets: CaptureAsset[];
};

export const CAPTURE_ASSET_GROUPS: CaptureAssetGroup[] = [
  {
    title: "Male mannequin board",
    description: "Neutral silhouette reference for the body sweep and head pass.",
    assets: [
      {
        fileName: "male_body_front.png",
        alt: "Male mannequin full-body front reference",
        caption: "Front body framing with both arms slightly away from the torso."
      },
      {
        fileName: "male_body_left.png",
        alt: "Male mannequin full-body left reference",
        caption: "Left-side silhouette for overlap planning."
      },
      {
        fileName: "male_body_right.png",
        alt: "Male mannequin full-body right reference",
        caption: "Right-side silhouette for overlap planning."
      },
      {
        fileName: "male_body_back.png",
        alt: "Male mannequin full-body back reference",
        caption: "Back-body framing so later reconstruction can close the loop."
      },
      {
        fileName: "male_body_three_quarter.png",
        alt: "Male mannequin three-quarter body reference",
        caption: "Three-quarter bridge shot between the front and side passes."
      },
      {
        fileName: "male_head_front.png",
        alt: "Male mannequin front head reference",
        caption: "Front face close-up with a neutral expression and visible hairline."
      },
      {
        fileName: "male_head_left.png",
        alt: "Male mannequin left head reference",
        caption: "Left head close-up with the forehead, ear, and jawline visible."
      },
      {
        fileName: "male_head_right.png",
        alt: "Male mannequin right head reference",
        caption: "Right head close-up with the forehead, ear, and jawline visible."
      }
    ]
  },
  {
    title: "Female mannequin board",
    description: "A second neutral board so users can compare silhouette and head framing.",
    assets: [
      {
        fileName: "female_body_front.png",
        alt: "Female mannequin full-body front reference",
        caption: "Front body framing with the shoulders open and the arms off the torso."
      },
      {
        fileName: "female_body_left.png",
        alt: "Female mannequin full-body left reference",
        caption: "Left-side body view for the rotation sweep."
      },
      {
        fileName: "female_body_right.png",
        alt: "Female mannequin full-body right reference",
        caption: "Right-side body view for the rotation sweep."
      },
      {
        fileName: "female_body_back.png",
        alt: "Female mannequin full-body back reference",
        caption: "Back-body framing to preserve shoulder and hip coverage."
      },
      {
        fileName: "female_body_three_quarter.png",
        alt: "Female mannequin three-quarter body reference",
        caption: "Three-quarter body view to connect the front and profile passes."
      },
      {
        fileName: "female_head_front.png",
        alt: "Female mannequin front head reference",
        caption: "Front head close-up with a neutral expression and exposed hairline."
      },
      {
        fileName: "female_head_left.png",
        alt: "Female mannequin left head reference",
        caption: "Left head close-up with the ear line and jaw contour visible."
      },
      {
        fileName: "female_head_right.png",
        alt: "Female mannequin right head reference",
        caption: "Right head close-up with the ear line and jaw contour visible."
      }
    ]
  }
];

export const EXPECTED_ASSET_NAMES = CAPTURE_ASSET_GROUPS.flatMap((group) =>
  group.assets.map((asset) => asset.fileName)
);
