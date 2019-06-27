
run_test() {
  # Clean up and wait a bit
  pip uninstall -y ansible || :
  sleep 60

  # First make sure everything has been cleaned up
  objcount=$( for kind in vmi pvc vm vmirs vmipreset template; do cluster-up/oc.sh get $kind -o name || :; done | wc -l )
  if [ $objcount != 0 ]; then
    echo "Playbooks did not clean up after themselves; aborting"
    false
  fi

  # Test
  ci-common/install-ansible.sh $1

  ansible-playbook --version
  ansible-playbook -vvv tests/playbooks/all.yml
}

@test "pip" {
  run_test pip
}

@test "branch/stable-2.8" {
  run_test branch/stable-2.8
}

@test "branch/devel" {
  run_test branch/devel
}

