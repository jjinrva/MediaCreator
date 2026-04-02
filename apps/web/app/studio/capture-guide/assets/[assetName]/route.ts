import { readFile } from "fs/promises";
import path from "path";

import { NextResponse } from "next/server";

import { EXPECTED_ASSET_NAMES } from "../../content";

const ASSET_ROOT = path.resolve(process.cwd(), "..", "..", "docs", "capture_guides", "assets");

export const runtime = "nodejs";

export async function GET(
  _request: Request,
  { params }: { params: { assetName: string } }
) {
  const { assetName } = params;

  if (!EXPECTED_ASSET_NAMES.includes(assetName)) {
    return NextResponse.json({ detail: "Asset not found." }, { status: 404 });
  }

  try {
    const payload = await readFile(path.join(ASSET_ROOT, assetName));

    return new NextResponse(payload, {
      headers: {
        "cache-control": "public, max-age=0, must-revalidate",
        "content-type": "image/png"
      }
    });
  } catch {
    return NextResponse.json({ detail: "Asset not found." }, { status: 404 });
  }
}
