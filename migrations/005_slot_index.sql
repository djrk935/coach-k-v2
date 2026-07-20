-- Disambiguates same-named exercises appearing twice in one day (e.g. a
-- warmup "Back Squat" row and a working-set "Back Squat" row) so logging
-- one doesn't mark both complete. NULL for pre-existing chat-logged sets
-- (they have no day/slot concept) — only Today-view logging sets this.
ALTER TABLE workout_sets ADD COLUMN slot_index INT;
