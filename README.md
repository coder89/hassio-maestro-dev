# How to Run and Test

1. Start the setup:

   ```
   docker compose up -d --build
   ```

   This builds the maestro image (once), starts both containers.

2. Interact/Test inside containers (no host tools needed):

   Exec into maestro: `docker compose exec maestro bash`

   Check ADB: `adb devices` (should show `redroid:5555 device` if connected).

   If not connected: `adb connect redroid:5555`

   Run a Maestro flow: Place a sample `flow.yaml` in `./flows` on host, then `maestro test /flows/flow.yaml --device redroid:5555`

   Start Maestro Studio: `maestro studio --host 0.0.0.0 --port 9999 --device redroid:5555` (access http://localhost:9999 from host browser to record flows).

3. Install apps in redroid (from maestro container, since it has ADB):

   Download APK inside container: wget https://example.com/your-app.apk (or mount APKs via volumes).

   Install: `adb install your-app.apk`

4. Stop/Cleanup:

   ```
   docker compose down
   ```