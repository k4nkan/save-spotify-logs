create table if not exists public."spotify-tracks" (
  track_id text primary key,
  track_name text not null,
  artist_name text not null,
  track_url text,
  image_url text,
  created_at timestamp with time zone not null default now()
);

create table if not exists public."spotify-playback-history" (
  id bigint generated always as identity primary key,
  track_id text not null references public."spotify-tracks" (track_id) on delete cascade,
  played_at timestamp with time zone not null,
  unique (track_id, played_at)
);

create index if not exists spotify_playback_history_played_at_idx
  on public."spotify-playback-history" (played_at desc);

create index if not exists spotify_playback_history_track_id_idx
  on public."spotify-playback-history" (track_id);

create or replace function public.top_tracks_on_date_jst(
  target_date date,
  limit_count integer default 3
)
returns table (
  rank bigint,
  track_id text,
  track_name text,
  artist_name text,
  image_url text,
  play_count bigint
)
language sql
stable
as $$
  select
    row_number() over (order by count(*) desc, min(h.played_at) asc) as rank,
    t.track_id,
    t.track_name,
    t.artist_name,
    t.image_url,
    count(*) as play_count
  from public."spotify-playback-history" h
  join public."spotify-tracks" t on t.track_id = h.track_id
  where (h.played_at at time zone 'Asia/Tokyo')::date = target_date
  group by t.track_id, t.track_name, t.artist_name, t.image_url
  order by play_count desc, min(h.played_at) asc
  limit limit_count;
$$;

alter table public."spotify-tracks" enable row level security;
alter table public."spotify-playback-history" enable row level security;

revoke all on public."spotify-tracks" from anon, authenticated;
revoke all on public."spotify-playback-history" from anon, authenticated;
revoke execute on function public.top_tracks_on_date_jst(date, integer) from public;

grant all on public."spotify-tracks" to service_role;
grant all on public."spotify-playback-history" to service_role;
grant usage, select on all sequences in schema public to service_role;
grant execute on function public.top_tracks_on_date_jst(date, integer) to service_role;
