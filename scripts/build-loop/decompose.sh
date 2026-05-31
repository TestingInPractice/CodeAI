#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --project <path>"
  exit 1
}

PROJECT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project|-p) PROJECT="$2"; shift 2 ;;
    *) usage ;;
  esac
done

if [ -z "$PROJECT" ]; then
  echo "Error: --project is required"
  usage
fi

SPECS_DIR="$PROJECT/docs/specs"
STATE_DIR="$PROJECT/.build-loop"

if [ ! -d "$SPECS_DIR" ]; then
  echo "Error: $SPECS_DIR does not exist. Run init.sh first."
  exit 1
fi

echo "=== Build Loop: Decompose $PROJECT ==="

# Find spec file (single .md or directory)
SPEC_FILE=""
for f in "$SPECS_DIR"/*.md "$SPECS_DIR"/*.MD; do
  if [ -f "$f" ]; then
    SPEC_FILE="$f"
    break
  fi
done

if [ -z "$SPEC_FILE" ]; then
  echo "Error: no .md files found in $SPECS_DIR"
  exit 1
fi

echo "Spec file: $SPEC_FILE"
echo "Output:    $STATE_DIR/phases.json"

# Run GSD decomposition
echo "Running GSD on $SPEC_FILE..."
npx @opengsd/get-shit-done-redux decompose "$SPEC_FILE" \
  --output "$STATE_DIR/phases.json" 2>&1

# If GSD fails, create a fallback decomposition
if [ ! -f "$STATE_DIR/phases.json" ] || [ ! -s "$STATE_DIR/phases.json" ] || grep -q '"phases":\s*\[\]' "$STATE_DIR/phases.json"; then
  echo ""
  echo "Note: GSD produced empty phases.json. Creating fallback decomposition from spec sections..."
  python3 -c "
import json, sys

with open('$SPEC_FILE') as f:
    content = f.read().lower()

# Define phases in logical execution order (dependencies first)
phase_defs = [
    ('Data Models',   'PostgreSQL схемы данных, типы, связи между сущностями'),
    ('Educational',   'Образовательный контент по этапам: звуки, слоги, слова, скороговорки'),
    ('PWA',           'Service Worker, манифест, иконки, offline-кеширование'),
    ('Auth',          'Telegram Login Widget, JWT, сессии'),
    ('API',           'Backend REST API: middleware, валидация, эндпоинты'),
    ('Levels',        'Уровни, EXP, прогрессия, этапы обучения 1–5'),
    ('Voice',         'Озвучка: ElevenLabs TTS, аудиофайлы, manifest.json'),
    ('Children',      'API и UI для профилей детей, переключение между детьми'),
    ('Feed',          'Лента достижений, ежедневный бонус'),
    ('Games',         'Игровой движок: PhonemicFind, MemoryMatch и др.'),
    ('Diagnostics',   'Диагностика речи через Web Speech API'),
    ('Shop',          'Магазин косметики, валюты, экипировка котика'),
    ('Subscriptions', 'Подписка, YooKassa/Robokassa, premium-гейтинг'),
    ('Referrals',     'Реферальные ссылки, начисление золота'),
    ('Admin',         'Админка: пользователи, feature flags, логи, настройки'),
]

# Only include phases that are referenced in the spec
phases = []
for i, (name, desc) in enumerate(phase_defs, 1):
    if name.lower() in content:
        phases.append({
            'id': i,
            'name': name,
            'description': desc,
            'status': 'pending',
            'depends_on': []
        })

# Set dependencies: each phase depends on all earlier phases
for i, p in enumerate(phases):
    p['depends_on'] = [phases[j]['id'] for j in range(i) if phases[j]['name'] in [
        'Data Models',
        'Auth',
        'API',
        'Educational',
        'Levels',
    ] and p['name'] not in ('Data Models', 'PWA')]

# Override with specific dependency rules
dep_rules = {
    'Auth':          ['Data Models'],
    'API':           ['Data Models', 'Auth'],
    'Levels':        ['Data Models'],
    'Voice':         ['Data Models'],
    'Educational':   ['Data Models'],
    'Children':      ['API', 'Auth'],
    'Feed':          ['API', 'Auth', 'Children'],
    'Games':         ['API', 'Educational', 'Levels'],
    'Diagnostics':   ['API', 'Games'],
    'Shop':          ['API', 'Levels'],
    'Subscriptions': ['API', 'Auth'],
    'Referrals':     ['API', 'Auth'],
    'Admin':         ['API', 'Auth'],
}
name_to_id = {p['name']: p['id'] for p in phases}
for p in phases:
    if p['name'] in dep_rules:
        p['depends_on'] = [name_to_id[d] for d in dep_rules[p['name']] if d in name_to_id]
    elif p['name'] == 'PWA':
        p['depends_on'] = []
    else:
        p['depends_on'] = []

with open('$STATE_DIR/phases.json', 'w') as f:
    json.dump({'phases': phases}, f, indent=2, ensure_ascii=False)
print(f'  Created {len(phases)} phases with dependencies')
"
fi

echo "=== Decompose complete ==="
echo "Phases written to $STATE_DIR/phases.json"
