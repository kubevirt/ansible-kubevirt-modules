generate:
	./update-cluster-up.sh

cluster-up:
	./cluster-up/up.sh

cluster-down:
	./cluster-up/down.sh

cluster-sync:
	./jenkins/cluster-sync.sh

.PHONY: generate cluster-up cluster-down cluster-sync
