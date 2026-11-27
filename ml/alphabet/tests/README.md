# ml/alphabet/tests

Owner: **Osama**.

The browser demo has software checks for hand cropping, stability filtering,
no-hand handling, and clearing old votes after a pause. Run them from the
repository root with the alphabet and MediaPipe dependencies installed:

```bash
python -m unittest ml.alphabet.tests.test_browser_demo -v
```

The classifier and hand detector are stubbed in these tests; they do not measure
recognition accuracy. Automated acceptance evidence for the trained baseline
remains to be implemented. Keep software checks separate from held-out
recognition evaluation.

## Planned acceptance evidence

- Check checkpoint/class-map count and contiguous indices.
- Check RGB conversion, deterministic 224×224 preprocessing, output shape and finite logits.
- Check a permitted golden fixture and CPU/GPU parity tolerances.
- For any rejection policy, measure coverage, accepted precision and false accepts on separate approved data.
- For live use, evaluate hand detection/cropping, no-hand/no-result behavior, static versus temporal classes, held/repeated letters, and runtime latency on named hardware.

The reported test metrics are notebook measurements on the held-out image split; they are not software test results and do not validate the webcam crop experiment.
