cluster-up:
	./cluster/up.sh

cluster-down:
	./cluster/down.sh

cluster-sync:
	./cluster/sync.sh

.PHONY: cluster-up cluster-down cluster-sync
