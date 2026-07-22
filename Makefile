.PHONY: up down reset demo logs

up:
	kind create cluster --config kind/cluster.yaml
	kubectl apply -f kubernetes/namespace.yaml
	docker-compose up -d

down:
	docker-compose down

reset:
	kind delete cluster --name self-healing-k8s
	$(MAKE) up

demo:
	bash scripts/generate-test-alert.sh

logs:
	docker-compose logs -f ai-engine
