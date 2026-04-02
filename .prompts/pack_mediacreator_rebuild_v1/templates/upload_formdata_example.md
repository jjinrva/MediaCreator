
# FormData upload example

Use `FormData` on the client and `UploadFile` on the API side.

```ts
export async function uploadCharacterPhotos(files: File[]): Promise<Response> {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file, file.name));

  return fetch('/api/v1/characters/import-photos', {
    method: 'POST',
    body: formData,
  });
}
```

```py
from typing import Annotated
from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/api/v1/characters", tags=["characters"])

@router.post("/import-photos")
async def import_character_photos(
    files: Annotated[list[UploadFile], File(description="Character reference images")],
):
    ...
```
