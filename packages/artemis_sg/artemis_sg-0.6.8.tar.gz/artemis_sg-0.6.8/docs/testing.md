# Testing
[Pytest](https://docs.pytest.org/en/7.1.x/index.html) is used for testing.
All tests are in the `tests` directory.  The
full test suite can be run with the following command.

```shell
pytest
```

Some of the tests are full integration tests that assume connections to the
internet and a Google Cloud account.  The full integration tests need access to
a Google Sheet.  The sheet for these tests should be defined in `config.toml` using
the following fields.  The Google sheet should also have a small number of
records in it and the ISBN column should use the heading "ISBN-13".  These
tests will generate a slide deck on the authenticated account.  Such slide
decks will need to be manually deleted since the application does not have
permission to do so.

```
asg.test.sheet.id="GOOGLE_SHEET_ID_HERE"
```

The full integration tests are time consuming and can be skipped using the
following command.

```shell
pytest -m 'not integration'
```

## Coverage
The coverage module can produce coverage reports, including html reports that
can be navigated to visually see what code is and is not covered by tests.

The following commands will generate a code coverage report that can be
browsed.
```shell
python -m coverage run -m pytest -m 'not integration'
python -m coverage report
python -m coverage html -i
```
