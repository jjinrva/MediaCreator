# Character Registry Contract

Phase 11 introduces the first durable character-registry contract.

## API routes

- `POST /api/v1/characters`
  - accepts a persisted `photoset_public_id`
  - creates exactly one `character` asset per source photoset
  - returns `201` on the first creation and `200` on idempotent repeats
- `GET /api/v1/characters/{character_public_id}`
  - returns the stored base character record
  - includes the source photoset public ID
  - includes the accepted prepared references captured at creation time
  - includes the character history trail

## Registry rules

- `assets` remains the canonical registry table.
- A Phase 11 character record is an `assets` row with:
  - `asset_type = "character"`
  - `status = "base-created"`
  - `source_asset_id` pointing at the originating photoset asset
- The create route is idempotent by source photoset. Repeating the same request returns the same character public ID instead of creating a duplicate row.

## History events

Phase 11 writes two character-level history events:

- `character.created`
- `character.photoset_linked`

Those events store the source photoset public ID plus the accepted entry public IDs that were locked in at creation time. Later phases extend the same character history stream instead of creating a parallel audit path.
