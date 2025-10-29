ARTIFACT_DIR := artifacts/phase0
DEMO_DIR := $(ARTIFACT_DIR)/demo

.PHONY: demo audit clean

demo:
	@mkdir -p $(DEMO_DIR)
	@python3 agents/project_manager.py > $(DEMO_DIR)/project_manager.log
	@python3 pipelines/interaction_stub.py /status > $(DEMO_DIR)/status.json
	@python3 pipelines/interaction_stub.py /clarify "Phase 0 readiness check" > $(DEMO_DIR)/clarify.json
	@python3 pipelines/policy_parser.py > $(DEMO_DIR)/policy_summary.txt
	@tail -n 1 audit/handoff.jsonl > $(DEMO_DIR)/handoff_latest.jsonl
	@echo "Demo artifacts written to $(DEMO_DIR)"

audit:
	@python3 pipelines/audit_summary.py

clean:
	@rm -rf $(DEMO_DIR)
	@echo "Demo artifacts removed."
