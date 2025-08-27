# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project attempts to adhere to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
### Fixed
### Changed
### Removed

## [0.6.8] - 2025-08-26
### Added
- Docs: add sheet-waves inventory flag docs. (#320)
- Docs: add vendor configuration documentation. (#314)
- Cli.py: add --mailchimp flag to generate sub-command. (#316)
- Spreadsheet: sheet-image: add rank columns. (#125)
- Scraper: update-ranks option. (#125)
- Scraper: scrape amazon rankings. (#125)
- Spreadsheet: sheet-image: cutoff-date flag. (#308)
- Scraper: update-images flag updates datafile with images from sheet. (#291)
- Spreadsheet: sheet-waves: product_active calculated from inventory. (#306)
- Spreadsheet: sheet-waves: fields added for unscraped titles. (#309)
- Sheet-waves: Optional --inventory flag to update quantities (#305)
- Spreadsheet: Format headers based on first cell format. (#292)
- Docs: Info on using config.toml fields. (#303)
- HtmlSlideGenerator: Add page number (#290)
- HtmlSlideGenerator: Add vendor specific text map (#299)
- ImgDownloader: Option to download less title images. (#301)
- ImgDownloader: Auto install TB certificate pem file. (#129)
- Scraper: Add `scrape_description` tests. (#286)
- Spreadsheet: Docstrings added to `spreadsheet.py`. (#89,#112)
- Scraper: Add WaveScraper. (#283)
- Items: Docstrings added to `items.py`. (#89,#109)
- Item: Docstrings added to `item.py`. (#89,#108)
- Test: Spreadsheet sheet_image doesn't duplicate Order column. (#213)
### Fixed
- Fix: Spreadsheet: sheet_image uses item.isbn instead of row value. (#310)
- Fix: img_downloader: Download images using item.isbn instead of row value. (#311)
- Fix: sheet-waves: Fixed waves not adding sheet data (#307)
- Fix: Order: Titles with no qty skipped (#293)
- Fix: Spreadsheet: Waves calculate prices for unscraped titles (#302)
- Fix: Isbn_key case regression. Key not upper cased. (#288)
- Fix: Lint fix.
- Test: Fix tests broken on Windows. (#249)
### Changed
- SlideGenerator: get_slide_text_key_map supports nested item data. (#317)
- Scraper: failover_scraper uses isbn10. (#321)
- Items: set_scraped_data iters through items instead of data. (#322)
- Spreadsheet: get_order_items gets isbn from item.isbn. (#312)
- ISBN: Isbn's with pattern 'FI-####' can be valid isbn. (#294)
- ISBN: Any 12-13 digit string can be valid isbn. (#294)
- Requirements: Python version bumped from 3.7 to 3.9.
- Scraper: Non-critical log errors changed to warnings. (#99)
- ImgDownloader: Catch exception for failed downloads.  (#231)
- Item, Spreadsheet: mv validate_isbn into a separate module. (#266)
- amazoncaptcha: Use forked version 2024.12.08.1. (#284)
- Vendor: Converted from class to function. (#285)
- Vendor: Add optional all_data param.  (#285)
- Vendor: Attribute names shortened (vendor_code -> code, vendor_name -> name). (#285)
- CONFIG: [asg][spreadsheet][sheet_waves][[calculate_fields] improve ease of use. (#278)
### Removed

## [0.6.7] - 2024-09-24
### Added
- CONFIG: [asg.slide_generator.html.bold_text] field to bold html text. (#276)
- CONFIG: [asg.slide_generator.html] fields to enable user adjustment. (#274)
- HtmlSlideGenerator: tag, and add_images methods to add images to slide decks. (#262)
- HtmlSlideGenerator: upload method to upload html slide decks to google cloud. (#259)
- HtmlSlideGenerator: generate function to create html slide decks. (#262)
- data/template.html: html template used to generate html slide decks. (#262)
### Fixed
### Changed
- HtmlSlideGenerator: add logo image to html slide decks. (#275)
- Docs: Information on using the html feature flag. (#271)
- SlideGenerator: Subclass for HTML and Google Slides (#269)
### Removed

## [0.6.6] - 2024-08-28
### Added
### Fixed
### Changed
- Item: validate ISBN using isbnlib. (#242)
- CLI: Add html feature flag. (#239)
- `hatch run test(-cov)`: Add doctest-modules to pytest run.
- Spreadsheet: validate ISBN using isbnlib. (#242)
- Spreadsheet: sheet-waves add gbp_to_usd. (#254)
- Spreadsheet: sheet-waves add category path. (#254)
- Spreadsheet: sheet-waves add preset fields. (#254)
- ruff.lint: Add `ruff format` to lint check. (#256)
- Spreadsheet: sheet-waves add price discount columns. (#254)
- SlideGenerator: Generate Slide formatting for prices. (#251)
- SlideGenerator: Generate Slide formatting for ISBN and ITEM#. (#251)
- SlideGenerator: Delete GCloud text images. (#253)
- Spreadsheet: sheet-waves dimensions split into Width, Length, Height. (#225)
### Removed

## [0.6.5] - 2024-07-05
### Added
- Docs: Development environment setup guide. (#250)
### Fixed
- Fix definitions in `pyproject.toml` for `hatch` and `ruff` on Windows. (#248)
- SDScraper: Login button finder to XPATH. (#236)
- Fix: Lint UP031 issues with string format
### Changed
### Removed

## [0.6.4] - 2024-04-05
### Added
### Fixed
- SlideGenerator: Create cloud image URLs at time of slide content to ensure they do not expire. (#215)
### Changed
### Removed

## [0.6.3] - 2024-03-17
### Added
- AmznScraper: Image widget failover. (#228)
- Docstrings to `img_downloader.py`. (#89,#107)
### Fixed
- Scraper: Prevent AmznUkScraper hanging on 503 page. (#227)
- Scraper: Prevent AmznUkScraper from throwing exceptions. (#227)
- Spreadsheet: freeze first row behavior. (#224)
### Changed
- Image size limit check moved from `ImgDownloader.download` to `gcloud.upload`. (#228)
### Removed

## [0.6.2] - 2024-03-07
### Added
- Docstrings to `gcloud.py`. (#89,#106)
### Fixed
- CLI: --logfile logname compatible with Windows. (#130)
- SlideGenerator - fix spelling of CFG["asg"]["slide_generator"]["text_box_resize_img_threshold"]. (#186)
### Changed
- Spreadsheet: Freeze first row of sheet_image and sheet_waves spreadsheets. (#96)
- Items - Use fault tolerant save for items file.  (#209)
- Scraper - save scraped data after every scraped item.  (#209)
- GJScraper - move sentinel publisher to CFG["asg"]["scraper"]["gjscraper"]. (#185)
- Scraper - move login timeout to CFG["asg"]["scraper"].  (#185)
- Scraper - move failover scraper CFG["asg"]["vendors"]. (#185)
- Scraper.get_failover_scraper_item_id - changed vendor arg from string to object. (#185)
- Vendor- added `failover_scraper` attribute to object. (#185)
- Item - move sort order of data CFG["asg"]["item"].  (#184)
- GCloud - move new file time threshold to CFG["google"]["cloud"].  (#183)
- CLI - move default slide deck title to CFG["asg"]["slide_generator"]. (#182)
- Spreadsheet: move `sheet_image` column order to CFG[asg.spreadsheet.sheet_image]. (#187)
### Removed

## [0.6.1] - 2024-03-05
### Added
### Fixed
- Items - filter out Item objects that have no valid data. (#215)
### Changed
### Removed

## [0.6.0] - 2024-02-29
### Added
- **BREAKING**: CLI: `artemis_sg sheet-waves [OPTIONS] VENDOR WORKBOOK WORKSHEET` command to create waves import spreadsheet. (#201)
- `AmznUkScraper` class and set vendor pw to use it as failover. (#131)
- CONFIG: [asg.spreadsheet.slide_generator] fields to enable user adjustment. (#186)
- CLI: --logfile option to save output to logfile. (#130)
### Fixed
- AmznScraper: Fixed manual entry trigger on failed captcha. (#211)
### Changed
### Removed

## [0.5.9] - 2024-02-05
### Added
- SlideGenerator: Add Bestsellers slide label mapping. (#203)
### Fixed
- ImgDownloader: Remove file if over 1MB in size. (#195)
### Changed
- Scraper: Filter out `None` keys when gethering sheet data. (#198)
- TBScraper: Filter out UK items when searching py ISBN. (#200)
- SlideGenerator: Reduce API slide batch size to 25. (#195)
### Removed

## [0.5.8] - 2024-01-03
### Fixed
- AmznScraper: Add failed captcha delay for manual entry. (#192)

## [0.5.7] - 2023-12-13
### Fixed
- SDScraper: Update main image locator. (#190)

## [0.5.6] - 2023-11-06
### Added
- Tests: Added coverage to Scraper.
- Add cov-html to pyproject.toml.
- Docs: Add point release checklist.
- Annotate data that should be in CFG. (#163)
### Fixed
- ImgDownloader: Remove existing PNG when moving file. (#188)
- Item: Add validate_isbn method.
- Scraper: Always handle TimeoutException when using WebDriverWait.
- Item: Handle None and non-string keys.
### Changed
### Removed

## [0.5.5] - 2023-10-12
### Fixed
- AmznScraper: Use amazoncaptcha on first use. (#180)

## [0.5.4] - 2023-10-10
### Fixed
- Catch empty files in ImgDownloader.is_image. (#177)

## [0.5.3] - 2023-10-08
### Added
- order --timeout option. (#174)
### Fixed
- SD Login button finder. (#176)
### Changed
- Use ruff for lint testing. (#173)
### Removed

## [0.5.2] - 2023-09-30
### Added
### Fixed
### Changed
### Removed
- "Confirmed" column from `sheet-image` XLSX files. (#169)

## [0.5.1] - 2023-09-29
### Added
### Fixed
### Changed
- Migrated documentation from README to docs. (#167)
### Removed

## [0.5.0] - 2023-09-27
### Added
### Fixed
### Changed
- **BREAKING**: Change CLI to support command chaining. (#140)
### Removed

## [0.4.1] - 2023-09-26
### Added
- CONFIG: [asg.spreadsheet.mkthumbs] fields to enable user adjustment. (#95)
- CONFIG: [asg.spreadsheet.sheet_image] fields to enable user adjustment. (#95)
- CONFIG: [asg.scraper.headless] field to enable headless scraper. (#159)
- CI: Deploy stage to create gitlab pages. (#158)
### Fixed
- SlideGenerator: Fix bucket_prefix for generated image files on Windows. (#164)
- SlideGenerator: Fix creating `test_bucket_prefix` directory in path of execution. (#164)
- CONFIG: Deep merge of CFG when loading configuration file from disk.
- README: Updated for v0.4.0. (#158)
- Mkthumbs: enabled `artemis_logo.png` to be included in package builds. (#160)
### Changed
### Removed

## [0.4.0] - 2023-09-23
### Added
- Support for Excel WORKBOOK/WORKSHEET to `artemis_sg scrape`. (#137)
- Support for Excel WORKBOOK/WORKSHEET to `artemis_sg generate`. (#137)
### Fixed
- Refactored pytest fixtures into conftest.py.
- Refactored mock.side_effect instances into mock.return_values.
### Changed
- **BREAKING**: Move vendor data storage from `vendors.json` to `config.toml`. (#152)
- **BREAKING**: Make `--worksheet` an optional argument for `artemis_sg scrape`. (#139)
- **BREAKING**: Make `--worksheet` an optional argument for `artemis_sg generate`. (#139)
- Replace usage of `imghdr` library with `puremagic`. (#103)
- **BREAKING**: Make `--worksheet` an optional argument for `artemis_sg sheet-image`. (#138)
- **BREAKING**: Make `--worksheet` an optional argument for `artemis_sg order`. (#138)
### Removed
- Support for `vendors.json`. (#152)

## [0.3.0] - 2023-09-19
### Added
### Fixed
### Changed
- **BREAKING**: Move configuration to `$user_config_dir/config.toml`. (#151)
- Set configuration files to be in `user_config_dir`. (#142)
- Set data files to be in `user_data_dir`. (#142)
- Changed module name from `artemis_slide_generator` to `artemis_sg`. (#147)
### Removed

## [0.2.5] - 2023-09-14

### Added
- Support in `pyproject.toml` for package build and publish via `hatch`. (#143)
- `Spreadsheet.sheet_image()`: Dynamically set column width with a max of about 500px. (#95)
- Docstrings to `app_creds.py`. (#89,#104)
- Documentation for installing via PowerShell. (#136)

### Fixed
- `ImgDownloader.download()`: No longer hard-coded to '.jpg'.  Handle all file
  types. The Windows `PermissionError: [WinError 32]` has been addressed. (#14)
- Test `cli.mkthumbs`:  Correct image-directory assumption.
- Test `cli.sheet_image`: Fix path for Windows.
- Test: Close test db fixture file to prevent `PermissionError: [WinError 32]`
  on Windows.

### Changed
- Project name for builds to `artemis_sg`. (#143)
- Appended `namespace` variables to logging messages. (#88)

### Removed


## [0.2.4] - 2023-08-24

### Fixed
- `sheet_image`: `isbn` values are coerced to integers if they come in as
  floating point numbers (#101).

## [0.2.3] - 2023-08-23

### Fixed
- `sheet-image`: `isbn_key` and `row01` values are upper-cased before compare
  (#90).

## [0.2.2] - 2023-08-23

### Removed
- Reverted: `ImgDownloader.download()`: No longer hard-coded to '.jpg'.  Handle
  all file types. (#14)
  - This triggered `PermissionError: [WinError 32]` on Windows.

## [0.2.1] - 2023-08-21

### Added
- CLI: `--email` option to the `order` sub-command.  This is used to
  impersonate customers for the 'tb' vendor (#70).
- Use "TBCODE" for item if no "ISBN" (#5).

### Fixed
- Docs: `sheet-image` examples using the `--output` option have been amended
  for clarity (#37).
- Tests: Fixed slow scraper tests (#83).
- Tests: Enable app_creds tests (#84).
- Linting errors.
- `mkthumbs`: Support any filename (#64).
- `ImgDownloader.download()`: No longer hard-coded to '.jpg'.  Handle all file
  types. (#14)

### Changed
- `sheet_image`: Create "Confirmed" column to the right of the "Order" column
  of generated spreadsheet (#34).
- `sheet_image`: Copy cell format from "ISBN_KEY" header cell to the header
  cells of created columns (#75).
- Refactor `gcloud.upload()` out of `gcloud.main()` (#47).
- Spreadsheet: Use variable for namespace in log messages.

### Removed
- `GCLoud`: replace `PIL` with `imghdr` for image file validation.

## [0.2.0] - 2023-08-16

### Added
- CHANGELOG
- Unit test for `Spreadsheet.sheet-image()` (#28).
- Unit test for `BLACKLIST_KEYS` in `SlideGenerator` (#25).
- For `GJScraper.load_login_page`, load search page first in an attempt to cache Publishers.
- CLI: `artemis_sg order [OPTIONS] VENDOR WORKBOOK WORKSHEET` command to construct web orders.
  - Valid vendor codes are: "tb", "gj", and "sd".
  - Scraper: for the above vendor scrapers, the following methods were added:
    - `load_login_page()`
    - `login()`
    - `add_to_cart()`
    - `load_cart_page()`

### Fixed
- Linting errors.

### Changed
- Internally, use search page for `GJScraper.load_item_page()` when logged in (#58).
- Scraper: `load_item_page()` methods now return a boolean.
- Update formatting of GitLab issue template.

### Removed

## [0.1.5] - 2023-08-11

### Added
- Output examples to `sheet-image` documentation in README (#37).
- GitLab issue templates (#62).

### Fixed
- `mkthumbs`: Ignore image files without basename (e.g. ".jpg") (#59).

### Changed
- Move ISBN validation into `ImageDownloader` class (#53).
- Allow non-ISBN values in `ImageDownloader` (#53), `mkthumbs` (#54), `sheet-image` (#60).

### Removed
- Use of webdriver-manager (#50).

## [0.1.4] - 2023-07-28

### Fixed
- Catch `TimeoutException` in `SDScraper.load_item_page()` (#38).

### Removed
- `TODO.md` in favor of tracking work via
   [GitLab issues](https://gitlab.com/johnduarte/artemis_slide_generator/-/issues)

## [0.1.3] - 2023-07-23

### Added
- `GJScraper` class with custom implementations of `BaseScraper` methods (#4).
- Failover to `GJScraper` in `scraper.main()` when vendor is "gj".

### Fixed
- Catch `UnidentifiedImageError` in `Spreadsheet.mkthumbs()` (#43).

## [0.1.2] - 2023-07-23

### Added
- `SDScraper` class with custom implementations of `BaseScraper` methods (#38).
- Failover to `SDScraper` in `scraper.main()` when vendor is "sd".

### Fixed
- Missing `ASG_VENDOR_DATAFILE` definition within `.env` in README (#36).
- Uppercase `isbn_key` when read from `ASG_VENDOR_DATAFILE` to ensure it is in
  the same state as the keys defined in `Item` (#39).

## [0.1.1] - 2023-07-21

### Added
- ISBN as plain text to generated slides (#9).

## [0.1.0] - 2023-07-11

### Changed
- **BREAKING**: CLI commands `scrape`, `generate` now take requiered SHEET_ID and SHEET_TAB arguments.
- **BREAKING**: Convert `database.json` to `vendors.json` and change the data structure.
- **BREAKING**: Use `.env` to define `ASG_VENDOR_DATAFILE`.
- Update documentation for changes above.

## [0.0.2] - 2023-07-18

### Added
- Mandatory VENDOR CLI argument for `sheet-image` command.
- Make `ImgDownloader.download()` idempotent in order to not re-download images.
- Have `Slidegenerator` clean up the text images created during run.
- `BaseScraper.delay()` to allow tuning sleep calls for scraper operations.

### Fixed
- `vendor` import in `spreadsheet.py`.
- Catch invalid ISBN values in `spreadsheet.sheet_image()`.
- Catch exception if TB item data does not contain "LINK" data.
- `TBScraper` indentation error that prevented image URLs from being appended as expected.

### Changed
- Create only one Google API token for project rather than one per vendor.
- Default slide title is now set to "New Arrivals".
- Default `sheet-image` output file set to "out.xlsx".
- Refactoring of `slide_generator.py`.

### Removed
- CLI options for `scrape` and `generate`: `--vendor-database`, `--scraped-items-database`.
- CLI options for `sheet-image`: `--image-directory`.


## [0.0.1] - 2023-07-10

### Added
- CLI interface with the following commands:
  - `artemis_sg scrape`
  - `artemis_sg download`
  - `artemis_sg upload`
  - `artemis_sg generate`
  - `artemis_sg sheet_image`
  - `artemis_sg mkthumbs`
- Documentation via README.
- Object oriented structure to code-base.
- LICENSE for GPL-3.0 or later.

### Removed
- Script interface for slide generation.

[unreleased]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.8...main
[0.6.8]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.7...v0.6.8
[0.6.7]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.6...v0.6.7
[0.6.6]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.5...v0.6.6
[0.6.5]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.4...v0.6.5
[0.6.4]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.3...v0.6.4
[0.6.3]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.2...v0.6.3
[0.6.2]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.1...v0.6.2
[0.6.1]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.6.0...v0.6.1
[0.6.0]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.9...v0.6.0
[0.5.9]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.8...v0.5.9
[0.5.8]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.7...v0.5.8
[0.5.7]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.6...v0.5.7
[0.5.6]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.5...v0.5.6
[0.5.5]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.4...v0.5.5
[0.5.4]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.3...v0.5.4
[0.5.3]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.2...v0.5.3
[0.5.2]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.1...v0.5.2
[0.5.1]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.5.0...v0.5.1
[0.5.0]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.4.1...v0.5.0
[0.4.1]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.4.0...v0.4.1
[0.4.0]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.3.0...v0.4.0
[0.3.0]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.2.5...v0.3.0
[0.2.5]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.2.4...v0.2.5
[0.2.4]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.2.3...v0.2.4
[0.2.3]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.2.2...v0.2.3
[0.2.2]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.2.1...v0.2.2
[0.2.1]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.2.0...v0.2.1
[0.2.0]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.1.5...v0.2.0
[0.1.5]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.1.4...v0.1.5
[0.1.4]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.1.3...v0.1.4
[0.1.3]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.1.2...v0.1.3
[0.1.2]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.1.1...v0.1.2
[0.1.1]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.1.0...v0.1.1
[0.1.0]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.0.2...v0.1.0
[0.0.2]: https://gitlab.com/johnduarte/artemis_slide_generator/compare/v0.0.1...v0.0.2
[0.0.1]: https://gitlab.com/johnduarte/artemis_slide_generator/-/tags/v0.0.1
