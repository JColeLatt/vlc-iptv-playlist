#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
epg_dir="$repo_dir/epg"
cache_dir="/home/ripper/.cache/vlc-iptv-epg/iptv-org-epg"
runtime_dir="/home/ripper/.cache/vlc-iptv-epg/node-v22"
staged="$epg_dir/guide.xml.new"

mkdir -p "$(dirname -- "$cache_dir")"
if [[ ! -x "$runtime_dir/bin/node" ]]; then
    runtime_stage="${runtime_dir}.new"
    sums_file="$(mktemp)"
    archive_file="$(mktemp --suffix=.tar.xz)"
    trap 'rm -f -- "$sums_file" "$archive_file"; rm -rf -- "$runtime_stage"' EXIT
    curl -fsSL https://nodejs.org/dist/latest-v22.x/SHASUMS256.txt -o "$sums_file"
    archive_name="$(sed -n 's/^[0-9a-f]\{64\} \(node-v22[^ ]*-linux-x64\.tar\.xz\)$/\1/p' "$sums_file")"
    [[ -n "$archive_name" ]]
    curl -fsSL "https://nodejs.org/dist/latest-v22.x/$archive_name" -o "$archive_file"
    expected_hash="$(sed -n "s/^\([0-9a-f]\{64\}\) $archive_name$/\1/p" "$sums_file")"
    printf '%s %s\n' "$expected_hash" "$archive_file" | sha256sum --check --status
    rm -rf -- "$runtime_stage"
    mkdir -p "$runtime_stage"
    tar -xJf "$archive_file" --strip-components=1 -C "$runtime_stage"
    mv -f -- "$runtime_stage" "$runtime_dir"
    rm -f -- "$sums_file" "$archive_file"
    trap - EXIT
fi
npm_cmd="$runtime_dir/bin/npm"
export PATH="$runtime_dir/bin:$PATH"
if [[ ! -d "$cache_dir/.git" ]]; then
    git clone --depth 1 --branch master https://github.com/iptv-org/epg.git "$cache_dir"
else
    git -C "$cache_dir" pull --ff-only
fi

lock_hash="$(sha256sum "$cache_dir/package-lock.json" | cut -d' ' -f1)"
if [[ ! -d "$cache_dir/node_modules" || ! -f "$cache_dir/.installed-lock-sha256" || "$(<"$cache_dir/.installed-lock-sha256")" != "$lock_hash" ]]; then
    "$npm_cmd" --prefix "$cache_dir" ci
    printf '%s\n' "$lock_hash" > "$cache_dir/.installed-lock-sha256"
fi

rm -f -- "$staged"
"$npm_cmd" --prefix "$cache_dir" run grab -- \
    --channels="$epg_dir/epg.channels.xml" \
    --output="$staged" \
    --days=3 \
    --maxConnections=4

python3 "$epg_dir/validate_guide.py" "$staged" --minimum-channels=35
mv -f -- "$staged" "$epg_dir/guide.xml"
chmod 0644 "$epg_dir/guide.xml"
