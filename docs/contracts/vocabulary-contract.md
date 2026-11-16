# Vocabulary and bilingual output contract

Owner: Basil for the reviewed semantic catalogue; Osama/Bavly for their model-specific class maps; Ali for public vocabulary; Adham for rendering; Hisham for variety/scope and final approval.

A stable `label_id` denotes meaning. A human-reviewed Arabic display string is not a model output index. Each model release supplies its own ordered class map tied to its version/checksum. Changing folder sort order must never change a deployed class's meaning. Do not assume 28 alphabet classes or a particular number of words.

Basil's label metadata uses `label_id`, `text_ar`, task, sign variety and approval status. Each model's mapping links `class_index` to stable ID/Arabic text; filenames differ by model release. Ali's **current v1 public schema** remains `{mode,model_version,labels:[{label_id,text,kind}]}` at GET `/api/v1/vocabulary?mode=word` or `mode=alphabet`. Candidate/item Arabic strings also use `text`. Public modes are `word`/`alphabet`, kinds are `word`/`letter`; exclude neutral/unknown internals. Return 503 when no approved mapping exists and 422 when mode is missing/invalid. Sort the public list stably without reordering the model's logit-index map.

## English output is an explicit unresolved integration decision

The current product requires Arabic and approved English equivalents, and the board describes a dictionary. The detailed backend/frontend v1 catalogues expose only Arabic `text`; they specify no English field, dictionary asset format or route. Data/model handbooks primarily define Arabic labels. Do not silently add an API field/route, ship a hardcoded duplicate vocabulary, or claim the current wire contract already satisfies bilingual delivery.

Recommendation for Hisham: approve a versioned bilingual semantic catalogue keyed by existing stable label IDs, then let Ali and Adham jointly select its distribution and version it in the public contract before implementing English display. Any future metadata must define reviewed equivalent, mapping version, variety, approval status, allowed use and missing-entry behavior. These are design requirements, not newly agreed wire keys. The exact mechanism is Q02/Q10 in [open questions](../architecture/decisions/open-questions.md).

English means an approved equivalent of a supported word/gloss. It requires no ASL training or second language recognizer. Arabic letters may have approved names/transliterations, but spelling does not automatically translate assembled Arabic words into English. Manual user text is not guaranteed to have an approved equivalent. Missing mappings must be shown honestly, without guessing, grammar generation or external automatic translation.

## Change and display rules

Review supported sign variety, vocabulary, multiword meanings, orthographic aliases and known confusions with qualified sign-language reviewers and Hisham. Disputed items stay out of the approved supported list. New/removed/merged meanings require coordinated data, model map, public catalogue, fixtures and UI compatibility review; never reuse an old ID for a new meaning.

Use NFC UTF-8 and logical Unicode order. Preserve meaningful letters, hamza, diacritics and punctuation; aliases do not merge semantics. Arabic display uses RTL and English display LTR while stored values remain in logical order. A multiword sign label is one transcript item. Edited/new manual text loses model provenance and is not a training label.

Sign Library/Help use the same model-compatible supported catalogue. A word label is not a validated gesture tutorial; media needs separate rights, attribution and model-owner semantic review. No mockup gesture, sample word or confidence percentage proves recognition capability.

Acceptance: unique IDs, exact ordered class-map correspondence, supported/public-only subset, model/mapping version alignment, no unsupported substitutions, mixed-direction rendering, approved English mapping coverage and honest missing/manual/alphabet behavior. English delivery remains pending until the shared contract is approved.
