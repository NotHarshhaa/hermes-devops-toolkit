# Example: Jenkins — test stage failure (flaky test)

Sanitized example input for the pipeline-failure-translator skill. Fictional
project and job names, no real credentials or hostnames.

## Input

User message:
"Our Jenkins master pipeline went red for the third time this week and nothing
changed in the code. The test stage fails but it passes locally every time. Here's
the console output of the run:"

```text
Started by upstream pipeline "bill-payment-service" build number 142
originally caused by:
    gitlab MR !37 "Add card-free payment path"
Obtained Jenkinsfile from git at.branch/main
Running on built-in node in /var/jenkins_home/workspace/bill-payment-service
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Checkout) }
[Pipeline] checkout
Checked out revision 8f3a21c (origin/main, main)
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Setup) }
[Pipeline] echo
Installing toolchain (this may take a few minutes)
[Pipeline] sh
+ ./scripts/install-toolchain.sh --ci
toolchain v2.14.0 installed successfully
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Build) }
[Pipeline] sh
+ ./scripts/build.sh --target=release
build completed in 41s, no warnings
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Unit tests) }
[Pipeline] sh
+ ./scripts/test.sh --scope unit
running 1,204 tests ...
ok        payments/core            3.2s
ok        payments/ledger          5.1s
FAIL      payments/webhooks        webhook_retry_test.go:88 webhook retried 3 times, expected 2
--- FAIL: TestWebhookRetryBackoff (12.04s)
FAIL	payments/webhooks	12.161s
FAIL
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Integration tests) }
Stage "Integration tests" skipped due to earlier failure(s)
[Pipeline] }
[Pipeline] stage
[Pipeline] { (Package) }
Stage "Package" skipped due to earlier failure(s)
[Pipeline] }
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
ERROR: script returned exit code 1
Finished: FAILURE
```

## Notes for the analyst

- The single visible test failure looks like a timing assertion. The user says the
  code has not changed and it fails only in CI — that asymmetry is evidence for an
  environment/timing issue rather than a logic regression.
- MR !37 introduced a change but the user says it "passes ..." — evaluate whether
  that claim is actually supported by the evidence provided (it is not directly
  verifiable from the log alone).

## What a correct analysis should do

See `tests/test-cases.md` → TC-2.
