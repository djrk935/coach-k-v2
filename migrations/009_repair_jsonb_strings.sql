-- Repair JSONB columns that were stored as JSON *string* scalars
-- (asyncpg double-encoded Python str / json.dumps without ::jsonb cast).
-- That broke "active program" detection: plan -> 'weekly_split' was NULL.

UPDATE programs
SET plan = (plan #>> '{}')::jsonb
WHERE jsonb_typeof(plan) = 'string';

UPDATE programs
SET citations = (citations #>> '{}')::jsonb
WHERE citations IS NOT NULL AND jsonb_typeof(citations) = 'string';

UPDATE user_profiles
SET profile = (profile #>> '{}')::jsonb
WHERE jsonb_typeof(profile) = 'string';

UPDATE athlete_readiness
SET readiness = (readiness #>> '{}')::jsonb
WHERE jsonb_typeof(readiness) = 'string';

UPDATE physique_photos
SET assessment = (assessment #>> '{}')::jsonb
WHERE assessment IS NOT NULL AND jsonb_typeof(assessment) = 'string';
