# Test fixture: a one-task benchmark in the format bench-model expects.
TASKS_ALL=(sh_feat)
tools_for() { echo bash; }
setup_sh_feat() {
  printf '#!/usr/bin/env bash\nname=${1:-world}\necho "hello $name"\n' > "$1/greet.sh"
}
P_sh_feat='Add a -h flag to greet.sh that prints usage. When done, reply with exactly: DONE'
check_sh_feat() {
  local d=$1 ok=1
  [ "$(cd "$d" && bash greet.sh -h)" = "usage: greet.sh [NAME]" ] || ok=0
  [ "$(cd "$d" && bash greet.sh Ana)" = "hello Ana" ] || ok=0
  echo $ok
}
