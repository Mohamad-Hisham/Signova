# ml/alphabet/tests

Owner: **Osama**.

The [backend alphabet adapter tests](../../../backend/tests/unit/test_alphabet_adapter.py)
cover hand crop geometry, classifier decision logic, and startup and inference
with the local checkpoint when both model assets are available.

## Planned acceptance evidence

- Check checkpoint/class-map count and contiguous indices.
- Check RGB conversion, deterministic 224×224 preprocessing, output shape and finite logits.
- Check a permitted golden fixture and CPU/GPU parity tolerances.
- For any rejection policy, measure coverage, accepted precision and false accepts on separate approved data.
- For live use, evaluate hand detection/cropping, no-hand/no-result behavior, static versus temporal classes, held/repeated letters, and runtime latency on named hardware.

The reported test metrics are notebook measurements on the held-out image split; they are not software test results and do not validate the webcam crop experiment.
