# Tests for djangoldp_becknld

This directory contains the unit test suite for the `djangoldp_becknld` package.

## Test Structure

- `tests_sample.py` - Sample tests and base test class
- `test_models.py` - Tests for models (Transaction, Item, etc.)
- `test_activities.py` - Tests for BecknLD activities
- `test_consts.py` - Tests for constants and configuration
- `test_views.py` - Tests for views and their methods
- `test_utils.py` - Tests for utilities and helper functions

## Test Coverage

### Models

- **Transaction**:
  - Basic creation and properties
  - `tidgen()` function for UUID generation
  - Properties `bap_inbox`, `bpp_inbox`, `bap_outbox`, `bpp_outbox`
  - `__str__` method

- **Item**:
  - Basic creation and properties
  - `__str__` method

### Activities

- **BecknLDActivity**:
  - Required attributes validation
  - Error handling validation

- **Specific Activity Types**:
  - BecknLDSelect, BecknLDInit, BecknLDConfirm
  - BecknLDOnSelect, BecknLDOnInit, BecknLDOnConfirm

### Constants and Configuration

- **BECKNLD_CONTEXT**:
  - Namespace structure and values

- **BAP/BPP Configuration**:
  - URI management
  - Required parameters validation
  - Configuration error handling

### Views

- **InboxViewset**:
  - GET method with BAP authentication
  - Non-existent transaction handling
  - Activity type handling
  - Response headers

### Utilities

- **tidgen() function**:
  - Correct format

## Running Tests

### Run all tests

```bash
python -m unittest djangoldp_becknld.tests.runner
```
