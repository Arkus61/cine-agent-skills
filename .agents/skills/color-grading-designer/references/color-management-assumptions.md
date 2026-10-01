# Color management and assumptions

Color management keeps source interpretation, creative work, and display rendering distinct. Record them separately:

- **Input encoding** describes how a supplied source version's values should be interpreted. Declare it only from metadata applicable to the exact segment and source version; otherwise leave it unknown or proposed.
- **Working space** is an unknown or proposed environment for balancing and look development. This standalone contract does not certify it from metadata. It is not proof of the input encoding and does not by itself identify a display result.
- **Output/display intent** describes the destination display and viewing conditions. A display transform is chosen for that destination; do not infer one from the working space.

Normalize sources only after their encodings are established. Camera originals and VFX renders may need different input interpretations even when they meet in one working space. Record range handling, baked looks, render space, and transform/configuration versions when supplied, without inventing software settings.

Metadata records use `<PROJECT>-CM###` and bind one exact segment, media version, field, value, and source reference. A filename or folder path is a hint, not metadata. Evidence records use `<PROJECT>-CE###` and bind an exact item, complete segment set, graded output version, claim, and claimed value. Provenance paths help locate records but do not independently authenticate them.

For uncertain sources, plan identification, normalization tests, and display review while leaving numeric corrections conditional.
