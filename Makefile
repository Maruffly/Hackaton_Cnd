DOCKER_COMPOSE = docker-compose
PYTHON = python3
PIP = pip3
VENV = venv
BIN = $(VENV)/bin
SRC_DIR = src
DATA_DIR = data


GREEN = \033[0;32m
BLUE  = \033[0;34m
NC    = \033[0m # No Color

.PHONY: all help run setup clean fclean re test

all: help

help:
	@echo "$(BLUE)Commandes disponibles :$(NC)"
	@echo "  make setup   : Crée le venv et installe les dépendances"
	@echo "  make run     : Lance la simulation (nettoyage + détection)"
	@echo "  make test    : Exécute les tests unitaires avec pytest"
	@echo "  make clean   : Supprime les fichiers temporaires et logs"
	@echo "  make fclean  : Supprime TOUT (venv, données processed, archives)"
	@echo "  make re      : Réinstalle tout et relance la simulation"

# 1 Install env
setup: setup-venv build-docker
		@echo "$(GREEN)Env ready (Local + Docker)$(NC)"

setup-venv:
	@echo "$(GREEN)Création du venv et installation des dépendances...$(NC)"
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

# Build infra
build-docker:
	@echo "$(BLUE)Construction des images Docker...$(NC)"
	$(DOCKER_COMPOSE) build

# Launch infra
up:
	@echo "$(GREEN)Démarrage des services (DB + Pipeline)...$(NC)"
	$(DOCKER_COMPOSE) up -d

# 
down:
	@echo "$(BLUE)Arrêt des services...$(NC)"
	$(DOCKER_COMPOSE) down

# Aide visuelle
help:
	@echo "$(BLUE)Commandes disponibles :$(NC)"
	@echo "  make setup   : Crée le venv + build les images Docker"
	@echo "  make up      : Lance la DB et le pipeline en arrière-plan"
	@echo "  make down    : Arrête et supprime les conteneurs"
	@echo "  make re      : Relance le build et le setup"

# 2 Launch pipeline
run:
	@if [ ! -d "$(VENV)" ]; then echo "Error: Do 'make setup' first"; exit 1; fi
	@echo "$(GREEN)Lancement du pipeline de logs...$(NC)"
	$(BIN)/python $(SRC_DIR)/main.py

# 3 Unit test
test:
	@echo "$(GREEN)Lauching tests with pytest...$(NC)"
	$(BIN)/python -m pytest tests/

# 4 Clean tmp
clean:
	@echo "$(BLUE)Cleaning tmp files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f pipeline.log

# 5 Full clean(Archive, Processed, Venv)
fclean: clean
	@echo "$(BLUE)Datas and venv cleaning...$(NC)"
	rm -rf $(VENV)
	rm -rf $(DATA_DIR)/processed/*
	rm -rf $(DATA_DIR)/archive/*
	touch $(DATA_DIR)/processed/.gitkeep
	touch $(DATA_DIR)/archive/.gitkeep
	$(DOCKER_COMPOSE) down -v --rmi all

re: fclean setup
	@echo "$(GREEN)Rebooting...$(NC)"
	$(MAKE) up