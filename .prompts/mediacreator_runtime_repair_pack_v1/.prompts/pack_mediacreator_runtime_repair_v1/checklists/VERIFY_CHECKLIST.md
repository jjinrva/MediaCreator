# Manual verification checklist

## Network / host
- [ ] API script binds to `0.0.0.0`
- [ ] web script binds to `0.0.0.0`
- [ ] browser can open the app through a LAN hostname/IP that is not `10.0.0.102`
- [ ] browser requests to the API do not fail with CORS errors

## Upload / QC
- [ ] drag-and-drop upload works
- [ ] thumbnails appear before upload
- [ ] persisted QC results appear after upload
- [ ] accepted count is visible
- [ ] rejected count is visible
- [ ] failed images stay visible with reasons

## Character creation
- [ ] zero accepted images blocks character creation
- [ ] valid accepted images can create a base character
- [ ] detail route loads by public ID
- [ ] body, pose, face, history, and outputs sections all load

## Progress
- [ ] after base creation, preview generation is queued
- [ ] a progress card shows queued/running state
- [ ] worker offline/stale state is visible if applicable
- [ ] the page refreshes into final preview state on completion
- [ ] failures are shown clearly

## Persistence
- [ ] body changes still persist
- [ ] pose changes still persist
- [ ] history records changes
- [ ] preview/final state survives reload
