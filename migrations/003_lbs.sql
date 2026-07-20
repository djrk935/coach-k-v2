-- Switch canonical units to pounds. Converts existing kg data in place.
-- Existing deployments: psql coachk -f migrations/003_lbs.sql

ALTER TABLE workout_sets RENAME COLUMN weight_kg TO weight_lbs;
UPDATE workout_sets SET weight_lbs = round(weight_lbs * 2.20462, 1)
    WHERE weight_lbs IS NOT NULL;

-- Profiles: convert lifts_1rm values, bodyweight_kg -> bodyweight_lbs, tag units.
UPDATE user_profiles SET profile = profile
    || jsonb_build_object('units', 'lbs')
    || CASE WHEN profile ? 'lifts_1rm' THEN jsonb_build_object(
            'lifts_1rm',
            (SELECT jsonb_object_agg(k, round(v::numeric * 2.20462))
             FROM jsonb_each_text(profile -> 'lifts_1rm') AS t(k, v)))
       ELSE '{}'::jsonb END
    || CASE WHEN profile ? 'bodyweight_kg' THEN jsonb_build_object(
            'bodyweight_lbs', round((profile ->> 'bodyweight_kg')::numeric * 2.20462))
       ELSE '{}'::jsonb END;
UPDATE user_profiles SET profile = profile - 'bodyweight_kg';
