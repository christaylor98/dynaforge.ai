ARTIFACT_DIR := artifacts/phase0
DEMO_DIR := $(ARTIFACT_DIR)/demo
PHASE1_ARTIFACT_DIR := artifacts/phase1
PHASE1_ORCHESTRATION_DIR := $(PHASE1_ARTIFACT_DIR)/orchestration

.PHONY: demo phase1-demo audit clean

demo:
	@mkdir -p $(DEMO_DIR)
	@python3 agents/project_manager.py > $(DEMO_DIR)/project_manager.log
	@python3 pipelines/interaction_stub.py /status > $(DEMO_DIR)/status.json
	@python3 pipelines/interaction_stub.py /clarify "Phase 0 readiness check" > $(DEMO_DIR)/clarify.json
	@python3 pipelines/policy_parser.py > $(DEMO_DIR)/policy_summary.txt
	@tail -n 1 audit/handoff.jsonl > $(DEMO_DIR)/handoff_latest.jsonl
	@echo "Demo artifacts written to $(DEMO_DIR)"

phase1-demo:
	@mkdir -p $(PHASE1_ORCHESTRATION_DIR)
	@python3 pipelines/phase1_orchestrator.py --log $(PHASE1_ORCHESTRATION_DIR)/run.log > $(PHASE1_ORCHESTRATION_DIR)/run.json
	@echo "Phase 1 orchestration artifacts written to $(PHASE1_ORCHESTRATION_DIR)"

audit:
	@python3 pipelines/audit_summary.py

clean:
	@rm -rf $(DEMO_DIR) $(PHASE1_ORCHESTRATION_DIR)
	@echo "Demo artifacts removed."
