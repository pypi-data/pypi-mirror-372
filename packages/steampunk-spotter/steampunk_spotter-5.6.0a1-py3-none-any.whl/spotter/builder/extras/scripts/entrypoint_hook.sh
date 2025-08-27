#!/bin/sh

set -eu

# TODO: add SPOTTER_DEBUG=true/false and print debug info if true NEEDS TESTING
#       also add --debug if debug is on
# TODO: accept "true" and "1" as boolean true NEEDS TESTING
#       "True" and "2" are false
is_true(){
  local value="$1"
  case "$value" in
    [Tt][Rr][Uu][Ee]|1)
        return 0  # true
        ;;
    *)
        return 1  # false
        ;;
  esac
}

# TODO: add trap for any exit and print message
# scan included/used collections ?
# which spotter project to use?
SPOTTER_OPTS="--timeout 30 --no-color"
SCAN_OPTS="--no-progress -f text"
SCAN_OPTS+=" -l warning"
SCAN_OPTS+=" --origin ci"
SCAN_LIST=""
SCAN_LIST+=" ${@: -1} "  # last argument is playbook
[ -e "playbooks" ] && SCAN_LIST+=" playbooks "
[ -e "roles" ] && SCAN_LIST+=" roles "

SPOTTER_DEBUG=${SPOTTER_DEBUG:-0}
if [ "$SPOTTER_DEBUG" = "1" ]
then
  SPOTTER_OPTS+=" --debug"
fi

SPOTTER_RUNTIME_ENABLED=${SPOTTER_RUNTIME_ENABLED:-0}
ANSIBLE_CALLBACKS_ENABLED=${ANSIBLE_CALLBACKS_ENABLED:- }
if [ "$SPOTTER_RUNTIME_ENABLED" = "1" ]
then
  export ANSIBLE_CALLBACKS_ENABLED=xlab_steampunk.spotter.spotter,$ANSIBLE_CALLBACKS_ENABLED
fi

SPOTTER_PREFLIGHT_ENABLED=${SPOTTER_PREFLIGHT_ENABLED:-0}
if [ "$SPOTTER_PREFLIGHT_ENABLED" = "0" ]
then
  echo "INFO: Steampunk Spotter preflight checks not enabled. Running ansible playbook."
  exec "$@"
else
  SPOTTER_PROJECT=${SPOTTER_PROJECT:-}
  if [ -z "${SPOTTER_PROJECT}" ]; then
    echo "Project id is not set (environment var SPOTTER_PROJECT). Steampunk Spotter will use the default project. "
  else
    SCAN_OPTS+=" --project-id ${SPOTTER_PROJECT}"
  fi
fi

SPOTTER_ON_ERROR_EXIT=${SPOTTER_ON_ERROR_EXIT:-1}
on_spotter_error() {
  if [ "$SPOTTER_ON_ERROR_EXIT" = "0" ]
  then
    echo "WARN: Steampunk Spotter scan reported issues. However, we proceed to run the playbook."
  else
    echo "ERROR: Steampunk Spotter reported issues. Playbook run aborted."
    exit 1
  fi
}

echo "$@"
echo spotter $SPOTTER_OPTS scan $SCAN_OPTS $SCAN_LIST
spotter $SPOTTER_OPTS scan $SCAN_OPTS $SCAN_LIST || on_spotter_error

exec "$@"
