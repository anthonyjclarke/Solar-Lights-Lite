# User-supplied working upload snapshot

Files copied unchanged from the Downloads attachment. Upload and startup were reported successful by the user. This is evidence, not the production configuration.

The 8 MHz build requests Serial.begin(19200), but the user reports readable output at 38400. This strongly indicates a 16 MHz runtime; see ../user-hardware-upload.md. No fuse write, upload, or production-source change was performed when recording these attachments.
