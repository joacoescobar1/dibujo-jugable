# patch — minimal fix to make the level winnable
Input: current spec.json + playtest_report JSON.
Output ONLY the full corrected spec.json (schema-valid).
Constraints:
- Smallest diff that fixes the reported root cause. Do not move the player or goal unless the report says they are the cause.
- Preserve the kid's rules (if "no puede tocar el agua", keep the water — add a bridge/gap instead of deleting it).
- Add `"_patch_note"`: one sentence on what changed and why (shown in the demo timeline).
