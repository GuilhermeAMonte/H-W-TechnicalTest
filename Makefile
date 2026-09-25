# Makefile — Lab Red+Blue (H&W)
# Objetivo do case: "um comando documentado que sobe o laboratório inteiro".
# Cascas vazias por ora — preenchidas conforme as stages avançam.

SHELL := /bin/bash
COMPOSE := docker compose

.DEFAULT_GOAL := help

.PHONY: help up down restart ps logs nuke evidence

help: ## Lista os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Sobe o lab inteiro (gateway, waf, dvwa, app-api, postgres)
	$(COMPOSE) up -d --build
	@echo ">> lab no ar. 'make ps' pra ver o estado."

down: ## Derruba o lab (mantém volumes)
	$(COMPOSE) down

restart: down up ## Recria o lab

ps: ## Estado dos containers
	$(COMPOSE) ps

logs: ## Segue os logs de todos os serviços
	$(COMPOSE) logs -f

nuke: ## Derruba TUDO incluindo volumes (destrói dados do postgres)
	@echo "!! isso apaga volumes/dados. ctrl-C em 5s pra abortar."; sleep 5
	$(COMPOSE) down -v

evidence: ## Cria a árvore de evidência caso falte
	@for n in 01 02 03 04 05 06 07 08 09 10; do mkdir -p evidence/stage$$n; done
	@echo ">> evidence/ ok"
