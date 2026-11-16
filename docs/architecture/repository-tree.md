# Complete repository tree

Owner: Hisham. Current project tree including implemented repository CI, the application scaffold, and preserved original references. Git metadata and workspace tool mounts are excluded. The original README, license, five handbooks and Excalidraw remain unchanged; the CI task updates related guides. The current workspace is the repository root.

```text
Signova/
├── .github/
│   ├── workflows/
│   │   ├── README.md
│   │   └── ci.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── README.md
├── artifacts/
│   ├── alphabet/
│   │   ├── README.md
│   │   └── RELEASE-TEMPLATE.md
│   ├── words/
│   │   ├── README.md
│   │   └── RELEASE-TEMPLATE.md
│   └── README.md
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── README.md
│   │   │   ├── catalog.py
│   │   │   ├── health.py
│   │   │   ├── sessions.py
│   │   │   └── transcript.py
│   │   ├── models/
│   │   │   ├── README.md
│   │   │   ├── alphabet.py
│   │   │   ├── base.py
│   │   │   ├── fake.py
│   │   │   └── word.py
│   │   ├── schemas/
│   │   │   ├── README.md
│   │   │   ├── common.py
│   │   │   ├── events.py
│   │   │   └── rest.py
│   │   ├── services/
│   │   │   ├── README.md
│   │   │   ├── commands.py
│   │   │   ├── recognition.py
│   │   │   ├── sessions.py
│   │   │   ├── transcript.py
│   │   │   └── word_gate.py
│   │   ├── utilities/
│   │   │   ├── README.md
│   │   │   ├── errors.py
│   │   │   ├── ids.py
│   │   │   └── time.py
│   │   ├── ws/
│   │   │   ├── README.md
│   │   │   └── live.py
│   │   ├── README.md
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   ├── fixtures/
│   │   │   └── README.md
│   │   ├── integration/
│   │   │   └── README.md
│   │   ├── unit/
│   │   │   └── README.md
│   │   └── README.md
│   ├── .env.example
│   ├── README.md
│   ├── requirements.in
│   └── requirements.lock.txt
├── data/
│   ├── configs/
│   │   └── README.md
│   ├── features/
│   │   ├── .gitkeep
│   │   └── README.md
│   ├── interim/
│   │   ├── .gitkeep
│   │   └── README.md
│   ├── labels/
│   │   └── README.md
│   ├── manifests/
│   │   └── README.md
│   ├── processed/
│   │   ├── .gitkeep
│   │   └── README.md
│   ├── raw/
│   │   ├── .gitkeep
│   │   └── README.md
│   ├── reports/
│   │   ├── DATA_CARD.md
│   │   └── README.md
│   ├── scripts/
│   │   ├── README.md
│   │   ├── build_manifests.py
│   │   ├── clean.py
│   │   ├── inventory.py
│   │   ├── package_release.py
│   │   ├── split.py
│   │   └── validate_release.py
│   ├── source_register/
│   │   └── README.md
│   ├── tests/
│   │   └── README.md
│   ├── README.md
│   ├── requirements.in
│   └── requirements.lock.txt
├── docs/
│   ├── architecture/
│   │   ├── README.md
│   │   ├── file-catalog.md
│   │   ├── monorepo-structure.md
│   │   ├── repository-tree.md
│   │   ├── runtime-data-flow.md
│   │   └── system-overview.md
│   ├── contracts/
│   │   ├── README.md
│   │   ├── dataset-contract.md
│   │   ├── frontend-backend-contract.md
│   │   ├── model-interface.md
│   │   ├── rest-api.md
│   │   ├── starting-limits.md
│   │   ├── vocabulary-contract.md
│   │   └── websocket-protocol.md
│   ├── datasets/
│   │   ├── README.md
│   │   ├── data-governance.md
│   │   └── source-register.md
│   ├── runbooks/
│   │   ├── README.md
│   │   ├── continuous-integration.md
│   │   └── integration-checklist.md
│   ├── team/
│   │   ├── README.md
│   │   ├── git-workflow.md
│   │   ├── handoffs.md
│   │   ├── meeting-rhythm.md
│   │   └── ownership.md
│   └── README.md
├── frontend/
│   ├── e2e/
│   │   └── README.md
│   ├── src/
│   │   ├── api/
│   │   │   ├── README.md
│   │   │   ├── client.ts
│   │   │   ├── contracts.ts
│   │   │   └── liveSocket.ts
│   │   ├── app/
│   │   │   ├── App.tsx
│   │   │   ├── README.md
│   │   │   ├── sessionController.ts
│   │   │   └── sessionReducer.ts
│   │   ├── camera/
│   │   │   ├── README.md
│   │   │   ├── frameSampler.ts
│   │   │   └── useCamera.ts
│   │   ├── components/
│   │   │   ├── ConfirmDialog.tsx
│   │   │   ├── README.md
│   │   │   └── StatusMessage.tsx
│   │   ├── features/
│   │   │   ├── about-help/
│   │   │   │   ├── AboutHelp.tsx
│   │   │   │   └── README.md
│   │   │   ├── home/
│   │   │   │   ├── HomePage.tsx
│   │   │   │   └── README.md
│   │   │   ├── recognition/
│   │   │   │   ├── README.md
│   │   │   │   ├── RecognitionPreview.tsx
│   │   │   │   └── RecognitionWorkspace.tsx
│   │   │   ├── recovery/
│   │   │   │   ├── README.md
│   │   │   │   ├── RecoveryView.tsx
│   │   │   │   └── recoveryStore.ts
│   │   │   ├── sign-library/
│   │   │   │   ├── README.md
│   │   │   │   └── SignLibrary.tsx
│   │   │   ├── transcript/
│   │   │   │   ├── README.md
│   │   │   │   ├── TranscriptEditor.tsx
│   │   │   │   ├── TranscriptPanel.tsx
│   │   │   │   └── transcriptActions.ts
│   │   │   └── README.md
│   │   ├── mocks/
│   │   │   ├── README.md
│   │   │   └── SCENARIOS.md
│   │   ├── styles/
│   │   │   ├── README.md
│   │   │   ├── global.css
│   │   │   └── tokens.css
│   │   ├── README.md
│   │   └── main.tsx
│   ├── tests/
│   │   └── README.md
│   ├── .env.example
│   ├── README.md
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── ml/
│   ├── alphabet/
│   │   ├── configs/
│   │   │   └── README.md
│   │   ├── reports/
│   │   │   ├── MODEL_CARD.md
│   │   │   └── README.md
│   │   ├── src/
│   │   │   ├── README.md
│   │   │   ├── dataset.py
│   │   │   ├── decision.py
│   │   │   ├── evaluate.py
│   │   │   ├── export.py
│   │   │   ├── model.py
│   │   │   ├── predict.py
│   │   │   ├── preprocessing.py
│   │   │   └── train.py
│   │   ├── tests/
│   │   │   └── README.md
│   │   ├── README.md
│   │   ├── requirements.in
│   │   └── requirements.lock.txt
│   ├── common/
│   │   ├── contracts/
│   │   │   └── README.md
│   │   ├── evaluation/
│   │   │   └── README.md
│   │   ├── preprocessing/
│   │   │   └── README.md
│   │   └── README.md
│   ├── words/
│   │   ├── configs/
│   │   │   └── README.md
│   │   ├── reports/
│   │   │   ├── MODEL_CARD.md
│   │   │   └── README.md
│   │   ├── src/
│   │   │   ├── README.md
│   │   │   ├── dataset.py
│   │   │   ├── decision.py
│   │   │   ├── evaluate.py
│   │   │   ├── export.py
│   │   │   ├── model.py
│   │   │   ├── predict.py
│   │   │   ├── preprocessing.py
│   │   │   └── train.py
│   │   ├── tests/
│   │   │   └── README.md
│   │   ├── README.md
│   │   ├── requirements.in
│   │   └── requirements.lock.txt
│   └── README.md
├── scripts/
│   ├── README.md
│   └── check_repository.py
├── tests/
│   ├── ci/
│   │   ├── README.md
│   │   └── test_repository_checks.py
│   ├── contracts/
│   │   └── README.md
│   ├── fixtures/
│   │   └── README.md
│   ├── integration/
│   │   └── README.md
│   └── README.md
├── .editorconfig
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── START-HERE.md
├── Signova - Adham Frontend Engineering Handbook.docx
├── Signova - Ali Backend Engineering Handbook.docx
├── Signova - Basil Data Engineering Handbook.docx
├── Signova - Osama Alphabet Model Engineering Handbook.docx
├── Signova - Pavly Word Model Engineering Handbook.docx
└── Signova.excalidraw
```
