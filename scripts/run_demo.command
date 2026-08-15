#!/bin/zsh

set -u

project_dir="${0:A:h:h}"
python_bin="$project_dir/.venv/bin/python"

if [[ ! -x "$python_bin" ]]; then
  /usr/bin/osascript -e 'display alert "MonsterDeleterMac 尚未安装依赖" message "请先在终端运行：cd ~/Desktop/MonsterDeleterMac && uv sync --dev" as critical'
  exit 1
fi

cd "$project_dir"
exec "$python_bin" -m monster_deleter_mac.cli --demo

