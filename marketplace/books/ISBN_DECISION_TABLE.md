# ISBN Testing - Decision Table / Cause-Effect Graph Approach

## Test Strategy Overview
This document describes the comprehensive test strategy for ISBN validation functionality using the **Decision Table / Cause-Effect Graph** technique as required for Avaliação A5.

## Causes (Conditions)

| ID | Cause | Description |
|----|-------|-------------|
| C1 | Empty/Null ISBN | ISBN value is empty string, None, or whitespace only |
| C2 | Length == 10 (normalized) | After normalization (removing hyphens/spaces), length is exactly 10 |
| C3 | Length == 13 (normalized) | After normalization (removing hyphens/spaces), length is exactly 13 |
| C4 | Valid Characters | Contains only digits (and 'X' as last char for ISBN-10) |
| C5 | Valid Checksum | Checksum calculation validates correctly |
| C6 | Duplicate in DB | ISBN already exists in database (unique constraint) |

## Effects (Actions/Results)

| ID | Effect | Description |
|----|--------|-------------|
| E1 | ACCEPT | ISBN is valid and can be stored |
| E2 | REJECT_FORMAT | Invalid format (wrong length, invalid chars) |
| E3 | REJECT_CHECKSUM | Valid format but checksum fails |
| E4 | REJECT_DUPLICATE | Valid ISBN but already exists in DB |
| E5 | ACCEPT_EMPTY | Empty ISBN is accepted (field is optional) |

## Decision Table

| Rule | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 |
|------|----|----|----|----|----|----|----|----|----|----|---- |-----|-----|-----|-----|
| **C1** Empty/Null | Y | N | N | N | N | N | N | N | N | N | N | N | N | N | N |
| **C2** Length=10 | - | Y | Y | Y | Y | N | N | N | N | N | N | N | N | N | N |
| **C3** Length=13 | - | N | N | N | N | Y | Y | Y | Y | N | N | N | N | N | N |
| **C4** Valid Chars | - | Y | Y | N | - | Y | Y | N | - | Y | Y | Y | Y | N | - |
| **C5** Valid Checksum | - | Y | N | - | - | Y | N | - | - | Y | Y | Y | Y | - | - |
| **C6** Duplicate | - | N | - | - | - | N | - | - | - | Y | N | N | N | - | - |
| **Effect** | E5 | E1 | E3 | E2 | E2 | E1 | E3 | E2 | E2 | E4 | E1 | E1 | E1 | E2 | E2 |
| **Description** | Empty OK | Valid ISBN-10 | Bad checksum-10 | Invalid chars-10 | Wrong length-10 | Valid ISBN-13 | Bad checksum-13 | Invalid chars-13 | Wrong length-13 | Duplicate | Valid with hyphens | Valid with spaces | Mixed format | Invalid chars general | Too short/long |

## Test Data for Each Rule

### R1: Empty/Null ISBN
- Input: `""`, `None`, `"   "`
- Expected: Accepted (optional field)

### R2: Valid ISBN-10
- Input: `"0596520689"`, `"043942089X"`
- Expected: ACCEPT

### R3: Bad Checksum ISBN-10
- Input: `"0596520680"` (last digit wrong)
- Expected: REJECT_CHECKSUM

### R4: Invalid Characters ISBN-10
- Input: `"059652068A"`, `"05965-2068"`
- Expected: REJECT_FORMAT

### R5: Wrong Length (near 10)
- Input: `"123456789"`, `"12345678901"`
- Expected: REJECT_FORMAT

### R6: Valid ISBN-13
- Input: `"9780596520687"`, `"9781234567897"`
- Expected: ACCEPT

### R7: Bad Checksum ISBN-13
- Input: `"9780596520680"` (last digit wrong)
- Expected: REJECT_CHECKSUM

### R8: Invalid Characters ISBN-13
- Input: `"978059652068X"`, `"978-0596-52068"`
- Expected: REJECT_FORMAT

### R9: Wrong Length (near 13)
- Input: `"97805965206"`, `"97805965206870"`
- Expected: REJECT_FORMAT

### R10: Duplicate ISBN
- Input: `"9780596520687"` (already in DB)
- Expected: REJECT_DUPLICATE

### R11: Valid ISBN-13 with Hyphens
- Input: `"978-0-596-52068-7"`
- Expected: ACCEPT (normalized to `9780596520687`)

### R12: Valid ISBN-10 with Spaces
- Input: `"0 596 52068 9"`
- Expected: ACCEPT (normalized to `0596520689`)

### R13: Mixed Separators
- Input: `"978 0-596-52068 7"`
- Expected: ACCEPT (normalized to `9780596520687`)

### R14: Invalid Special Characters
- Input: `"978@0596#52068$7"`, `"ISBN:9780596520687"`
- Expected: REJECT_FORMAT

### R15: Extremely Short/Long
- Input: `"123"`, `"12345678901234567890"`
- Expected: REJECT_FORMAT

## Test Coverage by Unit

### Unit 1: Utils (validate_isbn, normalize_isbn)
- Tests R1-R15 for validation logic
- Focus on pure function behavior
- No database interaction

### Unit 2: Model (Book model with ISBN field)
- Tests R1, R2, R6, R10, R11 (persistence layer)
- Test clean() and save() methods
- Test unique constraint (R10)
- Test normalization in model

### Unit 3: API (register_book_api endpoint)
- Tests R1, R2, R3, R6, R7, R10, R11 (integration)
- Test HTTP responses (200, 400, 201)
- Test JSON payloads
- Test error messages

## Expected Test Counts

- **Unit 1 (Utils)**: 15+ tests (one per rule + variations)
- **Unit 2 (Model)**: 8+ tests (persistence + constraints)
- **Unit 3 (API)**: 10+ tests (HTTP integration)

**Total**: 33+ comprehensive tests covering all decision table rules
