## Usage
For each work session, you will need to activate the python virtual environment
prior to executing any commands.  Once the environment is activated, you can
execute the [Slide Generator Workflow](#slide-generator-workflow), the
[Spreadsheet Images Workflow](#spreadsheet-images-workflow),
[Spreadsheet Waves Workflow](#spreadsheet-waves-workflow) as outlined
below or run any of the commands independently as needed.

### Session Setup
Session setup comprises the following steps:

* Activate the previously created python virtual environment.

```{tab} Windows PowerShell
    "$HOME\python_venvs\venv_artemis\Scripts\Activate.ps1"
```

```{tab} Windows CMD
    "$HOME\python_venvs\venv_artemis\Scripts\activate.bat"
```

```{tab} Linux
    source "$HOME/python_venvs/venv_artemis/bin/activate"
```

### Slide Generator Workflow
In order to produce a slide deck, the following workflow is prescribed.
These elements are broken into separate components so that they might be
executed without a defined pipeline if needed.

The package includes a set of subcommands under the unified CLI command
`artemis_sg` once it is installed to facilitate this workflow.  See
the complete [CLI Command Reference](#cli-command-reference) for more
detail on each of these commands.

Steps in the workflow that are a manual task not handled by the software
are highlighted with the *Manual* tag.

* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Scrape Data](#scrape-data)
* [Download Images](#download-images)
* [Upload Images to Google Cloud](#upload-images-to-google-cloud)
* [Generate Slide Deck](#generate-slide-deck)

Workflow
```{mermaid}
flowchart LR
  W[/Add/Update Vendor\]
  X[/Create Spreadsheet\] --> A
  X --> B
  A[/Google Sheet ID/] --> C
  B[/XLSX File/] --> C
  C(scrape) --> D(download)
  C <--> Z((Internet))
  C --> Y[(local db)]
  Y --> D
  D --> E[local storage]
  D --> F(upload)
  E --> F
  F --> G[Google Cloud Storage]
  F --> H(generate)
  G --> H
  Y --> H
  H --> I[/Google Slides/]
```

#### Create Spreadsheet
*Manual*

Create spreadsheet that includes the field titles in row 1 and the desired
slide records in subsequent rows.  The spreadsheet must include a column for
ISBN numbers.  The ISBN numbers are assumed to be in the
[ISBN-13 format](https://www.isbn.org/about_ISBN_standard).  Make a
note of the location of this spreadsheet in your file system.
You may want to re-use this location in the
[spreadsheet images workflow](#spreadsheet-images-workflow).

#### Add/Update Vendor
*Manual*

The vendors are defined in the `[asg.vendors]` field of the `config.toml` file.
They contain three keys:

* `code`: This is the VENDOR code used to reference the VENDOR when using the
  `artemis_sg` command set.
* `name`: This is the full name of the vendor as it will appear on the Google
  Slide Decks created by the `artemis_sg generate` command.
* `isbn_key`:  This is the value used to identify ISBN data columns in
  spreadsheets.

Open `config.toml` in your favorite text editor.  If there is not an existing
record for the vendor, add one with the following pattern, including the field
key used for ISBN numbers.

If there is an existing record, update the appropriate values.

The format is as follows:
```
[asg]
vendors = [
    { code = "sample", name = "Sample Vendor", isbn_key = "ISBN-13" },
]
```

#### Scrape Data
Run the `artemis_sg scrape` command to save the item descriptions and image
URLs gathered for each item record in the spreadsheet to the file defined by the
configuration field `[asg.data.file.scraped]`.  The base command needs a valid
vendor code argument to map to the applicable vendor record updated in the
`[asg.vendors]` configuration field in the
[workflow step above](#add/update-vendor).  The base command also needs a valid
WORKBOOK identifier.  The WORKBOOK identifier can be a Google Sheet ID or an
Excel file location in which the item data
resides.

Example:
```shell
artemis_sg --verbose --vendor sample_vendor --workbook MY_GOOGLE_SHEET_ID scrape
```
##### Add images to existing data
Add the `--update-images` flag to the scrape sub-command to update existing data entries with image URLS from a spreadsheet. The spreadsheet must contain an image column with the name defined in `[asg.spreadshet.update_images_from]`

##### Re-scrape Amazon rankings
Add the `--update-ranks` flag to the scrape sub-command to update existing data entries with the Amazon ranking ('\# in Books' from the product page). If the vendor specified has it's backup scraper set to `AmznUkScraper` in config, then it will also update the Amazon UK ranking.

#### Download Images
Download images from the scraped data using the `artemis_sg download` command.

Example:
```shell
artemis_sg --verbose download
```
The command can optionally be run with a valid vendor code and WORKBOOK (Google Sheet ID or Excel file path), so that it only downloads images for titles included in the workbook. This is useful when you have a large scraped data file, and want to increase the download speed by only downloading images for titles that you need.

Example:
```shell
artemis_sg --verbose --vendor  sample_vendor --workbook MY_GOOGLE_SHEET_ID download
```
#### Upload Images to Google Cloud
Run the `artemis_sg upload` command to upload previously download images to
Google Cloud.

Example:
```shell
artemis_sg --verbose upload
```

#### Generate Slide Deck
Run the `artemis_sg generate` command to create a Google Slide deck of the
items in the spreadsheet including the description and images gathered by the
[scrape workflow step](#scrape-data).  You should set a desired slide title
using the `--title` option.  The base command needs a valid vendor code, and a
valid WORKBOOK (Google Sheet ID or Excel file path) in which the item data
resides.

Example:
```{tab} Windows
    artemis_sg --verbose --vendor sample_vendor --workbook MY_GOOGLE_SHEET_ID ^
               generate --title "Badass presentation"
```

```{tab} Linux
    artemis_sg --verbose --vendor sample_vendor --workbook MY_GOOGLE_SHEET_ID \
               generate --title "Badass presentation"
```

#### Command Chaining
The above `artemis_sg` sub-commands can be "chained" together to perform the
automated steps of the workflow using a single "chained" command.  The command
chain will run in the order specified. The base command needs a valid vendor
code, and a valid WORKBOOK (Google Sheet ID or Excel file path) in which the
item data resides.  The `generate` command can take an optional `--title`.

Example:
```{tab} Windows
    artemis_sg --vendor sample_vendor ^
               --workbook MY_GOOGLE_SHEET_ID ^
               scrape download upload generate --title "Badass presentation"
```

```{tab} Linux
    artemis_sg --vendor sample_vendor \
               --workbook MY_GOOGLE_SHEET_ID \
               scrape download upload generate --title "Badass presentation"
```

#### Html Feature Flag
The generate command can be run with the `--html` option to produce an html slide deck.
* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Generate Slide Deck](#generate-slide-deck)

Workflow
```{mermaid}
flowchart LR
  W[/Add/Update Vendor\]
  X[/Create Spreadsheet\] --> A
  X --> B
  A[/Google Sheet ID/] --> C
  B[/XLSX File/] --> C
  C(scrape) --> D[/Html Page/]
  C <--> Z((Internet))
  C --> Y[(local db)]
  Y --> D
```
### Spreadsheet Images Workflow
In order to produce a spreadsheet with thumbnail images added for items, the
following workflow is suggested.

The following steps are shared with the
[slide generator workflow](#slide-generator-workflow).  These steps are linked
to the appropriate step in that workflow rather then duplicating them here.

* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Scrape Data](#scrape-data)
* [Download Images](#download-images)

The unique steps for this workflow are:

* [Create Thumbnails](#create-thumbnails)
* [Add Thumbnails to Spreadsheet](#add-thumbnails-to-spreadsheet)

Workflow
```{mermaid}
flowchart LR
  W[/Add/Update Vendor\]
  X[/Create Spreadsheet\] --> A
  X --> B
  A[/Google Sheet ID/] --> C
  B[/XLSX File/] --> C
  C(scrape) --> D(download)
  C <--> Z((Internet))
  C --> Y[(local db)]
  Y --> D
  D --> E[local storage]
  D --> F(mkthumbs)
  F --> E
  F --> H(sheet-image)
  E --> H
  H --> I[/XLSX File/]
```

#### Create Thumbnails
Create thumbnail images from previously downloaded images using the `artemis_sg
mkthumbs` command.

Example:
```shell
artemis_sg --verbose mkthumbs
```

#### Add Thumbnails to Spreadsheet
Create a new Excel spreadsheet containing a thumbnail images column populated
with available thumbnails using the `artemis_sg sheet-image` command.
The base command needs a valid vendor code, and a valid WORKBOOK
(Excel file path) in which the item data resides.
This file path can be noted from
the [Create Spreadsheet](#create-spreadsheet) step.

**NOTE:** Currently, `artemis_sg sheet-image` does not support Google Sheet IDs
as a valid WORKBOOK type.

By default, the new Excel file is saved as "out.xlsx" in the directory from
which the command was run.  The
`--output` option can be used to specify a desired output file.  The
specification for the `--output` file can include either an absolute or
relative path location for the file as well.

Example:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-image
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-image
```

Example, specifying output file with an absolute file path:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-image ^
               --output "C:\Users\john\Documents\spreadsheets\my_new_spreadsheet.xlsx"
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-image \
               --output "/home/john/Documents/spreadsheets/my_new_spreadsheet.xlsx"
```

Example, specifying output file with a relative file path:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-image ^
               --output "..\..\my_new_spreadsheet.xlsx"
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-image \
               --output "../../my_new_spreadsheet.xlsx"
```

#### Cutoff Date Flag
If the sheet-image command is run with the `cutoff-date` flag, it only adds images for titles with a receive date after the cutoff date (DD/MM/YYYY). The column name it uses to find receive dates is vendor specific, and should be defined in config under 
```[asg.spreadsheet.sheet_image.vendor_date_col_names.<vendor>]```

Example:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-image --cutoff-date "01/02/2024"
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-image --cutoff-date "01/02/2024"
```

### Spreadsheet Waves Workflow
In order to produce a spreadsheet with additional columns added for items in
support of importing them into the waves platform, the following workflow is
suggested.

The following steps are shared with the
[spreadsheet images workflow](#spreadsheet-images-workflow).  These steps are
linked to the appropriate step in that workflow rather then duplicating them
here.

* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Scrape Data](#scrape-data)

Workflow
```{mermaid}
flowchart LR
  W[/Add/Update Vendor\]
  X[/Create Spreadsheet\] --> B
  B[/XLSX File/] --> C
  C(scrape)
  C <--> Z((Internet))
  C --> Y[(local db)]
  C --> H(sheet-waves)
  Y --> H
  H --> I[/XLSX File/]
```

#### Add Data Columns to Spreadsheet
Create a new Excel spreadsheet containing additional populated data columns
from scraped data using the `artemis_sg sheet-waves` command.
The base command needs a valid vendor code, and a valid WORKBOOK
(Excel file path) in which the item data resides.
This file path can be noted from
the [Create Spreadsheet](#create-spreadsheet) step.

**NOTE:** Currently, `artemis_sg sheet-waves` does not support Google Sheet IDs
as a valid WORKBOOK type.

By default, the new Excel file is saved as "out.xlsx" in the directory from
which the command was run.  The
`--output` option can be used to specify a desired output file.  The
specification for the `--output` file can include either an absolute or
relative path location for the file as well.

The `--gbp_to_usd` option can be used to specify the GBP to USD conversion rate. This 
conversion rate will then be applied to the discounted prices produced by sheet-waves.

Example:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-waves
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-waves
```

Example, specifying output file with an absolute file path:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-waves ^
               --output "C:\Users\john\Documents\spreadsheets\my_new_spreadsheet.xlsx"
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-waves \
               --output "/home/john/Documents/spreadsheets/my_new_spreadsheet.xlsx"
```

Example, specifying output file with a relative file path:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-waves ^
               --output "..\..\my_new_spreadsheet.xlsx"
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-waves \
               --output "../../my_new_spreadsheet.xlsx"
```

#### Inventory Flag

Sheet-waves can be run with the inventory flag to specify an inventory spreadsheet. If this flag is used, the output spreadsheet will have it's quantity column updated from the inventory. The column names for the input spreadsheet and the inventory spreadsheet must be specified under the `[asg.spreadsheet.sheet_waves.qty_col_names]` section of [config](#General).

Example:
```{tab} Windows
    artemis_sg --verbose ^
               --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               sheet-waves ^
               --inventory "C:\Users\john\Documents\spreadsheets\inventory_list.xlsx"
```

```{tab} Linux
    artemis_sg --verbose \
               --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               sheet-waves \
               --inventory "C:\Users\john\Documents\spreadsheets\inventory_list.xlsx"
```

### Command Chaining
The above `artemis_sg` sub-commands can be "chained" together to perform the
automated steps of the workflow using a single "chained" command.  The command
chain will run in the order specified. The base command needs a valid vendor
code, and a valid WORKBOOK (Excel file path) in which the
item data resides.  The `sheet-image` command can take an optional `--output`.

Example:
```{tab} Windows
    artemis_sg --vendor sample_vendor ^
               --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
               scrape download mkthumbs sheet-image ^
               --output "..\..\my_new_spreadsheet.xlsx"
```

```{tab} Linux
    artemis_sg --vendor sample_vendor \
               --workbook "/home/john/Documents/spreadsheets/my_spreadsheet.xlsx" \
               scrape download mkthumbs sheet-image \
               --output "../../my_new_spreadsheet.xlsx"
```

### Config.toml

You can edit the `config.toml` file to configure things for the various artemis_sg worlflows.

#### Vendor Configuration
*Manual*

Vendors can be added or updated under the `[asg.vendors]` section of config. Each vendor can have the following fields: 
- `code`: The vendor code associated with the vendor. 
- `isbn_key`: The name of the isbn column in spreadsheets used with this vendor.
- `name`: (optional) The name of the vendor.
- `failover_scraper`: (optional) The type of failover scraper. If a title's data cannot be found from [Amazon.com](https://www.amazon.com/), the failover scraper is used. The options are:
    - `AmznUkScraper`: Scraper for [Amazon UK](https://www.amazon.co.uk/)
    - `GJScraper`: Scraper for [Great Jones](https://www.greatjonesbooks.com/)
    - `TBScraper`: Scraper for [Texas Bookman](https://www.texasbookman.com/)
    - `SDScraper`: Scraper for [Strathearn Distribution](https://strathearndistribution.com/) 
    - `WaveScraper`: Scraper for [artemisbooksales.b2bwave.com](https://artemisbooksales.b2bwave.com/)

#### Slide Deck Configuration
*Manual*

The Html and Google Slides configurations are defined in the `[asg.slide_generator]` field of the `config.toml` file.

##### Text Mapping
* **`[asg.slide_generator.text_map]`:** This is where spreadsheet column headers are mapped to text in the slide decks.
```
[asg.slide_generator.text_map]
"AUTHOR": "by {t}",
"PUB DATE": "Pub Date: {t}",
"PUBLISHERDATE": "Pub Date: {t}",
```
* **`[asg.slide_generator.text_map.prices]`:** This is where spreadsheet column headers are mapped to text for prices.
```
[asg.slide_generator.text_map.price]
"YOUR COST": "Your Cost: ${t}",
"PUB LIST": "List Price: ${t}",
"LISTPRICE": "List Price: ${t}",
```

* **`[asg.slide_generator.text_map.<vendor_code>]`:** This is where vendor specific text maps can be specified by making the vendor code a key in `[asg.slide_generator.text_map]`.

In the following example, slide decks made with vendor code `example_vendor_code` add product links to the slides using the "ISBN" column.
```
[asg.slide_generator.text_map.example_vendor_code]
"ISBN": "www.example_vendor_product_link/{t}"
```
* **`[asg.slide_generator.blacklist_keys]`:** This is where column headers that should not be added to the slide decks are specified.
```
[asg.slide_generator]
blacklist_keys = [
    "ORDER",
    "ORDER QTY",
    "GJB SUGGESTED",
    "DATE RECEIVED",
    "SUBJECT",
    "AVAILABLE START DATE",
    "CATEGORY",
]
```
##### Formatting

* **`[asg.slide_generator]`:** This is where the Google Slides formatting can be specified.
```
[asg.slide_generator]
title_default = "New Arrivals"
line_spacing = 1
text_width = 80
max_fontsize = 18
...
```
* **`[asg.slide_generator.html]`:** This is where the HTML slide formatting can be specified. 
Values you might want to change including `font_size`, `page_background_color`, and `container_background_color` are found here.
```
[asg.slide_generator.html]
bold_text = ["TITLE"]
font_size = "18px"
page_background_color = "#ffe6b3"
container_background_color = "#b22424c1"
...
```

#### Spreadsheet Configuration
*Manual*

The sheet-waves configurations are defined in the `[asg.spreadsheet.sheet-waves]` field of the `config.toml` file.


##### General

* **`[asg.spreadsheet.sheet_waves.qty_col_names]`:**: This is where the quantity column names can be specified for the input spreadsheet and inventory spreadsheet. This is used by sheet-waves with the `--inventory flag`.

```
[asg.spreadsheet.sheet_waves.qty_col_names.<example vendor>]
"inventory" = "Available Stock"
"workbook" = "quantity"
```

* **`[asg.spreadsheet.sheet_waves.preset_fields]`:** This is where new columns added by sheet-waves that have a preset value can be specified:   

```
[asg.spreadsheet.sheet_waves.preset_fields]
product_active = 1
quantity_monitor = 1
Brand = "66 Books, Ltd."
dimension_measurement_unit = "inches"
```
* **`[asg.spreadsheet.sheet_waves.rename_fields]`:** This is where column headers can be renamed in the sheet produced by sheet-waves:   

```
[asg.spreadsheet.sheet_waves.rename_fields]
Barcode = "product_sku"
Title = "Name"
```

* **`[asg.spreadsheet.sheet_waves.data_columns]`:** This is where the new columns to be added by sheet-waves are specified 

```
[asg.spreadsheet.sheet_waves]
data_columns = [
    "Description",
    "Width",
    "Length",
    "Height",
    "category_path",
    "Pound Pricing",
    "is_private",
]
```
##### Prices
In this section you can change the mapping scheme used for pound price and choose the discounted prices.

* **`[asg.spreadsheet.sheet_waves.pound_pricing_map]`:** This is where the pound pricing calculation can be configured based on the format and RRP. 
You specify the mapping with:
```
[asg.spreadsheet.sheet_waves.pound_pricing_map.<format>.<pounds>]
<pence> = <pound price>
```
Example for mapping format of `af` with RRP of `£2.99` to a pound price of `£1.00`:
```
[asg.spreadsheet.sheet_waves.pound_pricing_map.af.2]
99 = 1.0
```
* **`[asg.spreadsheet.sheet_waves.pound_pricing_unmapped_multiplier]`:** This is where the default multiplier can be specified for pound price of titles that do not have a specific mapping based on their format and RRP. 
```
[asg.spreadsheet.sheet_waves]
pound_pricing_unmapped_multiplier = 0.4
```
* **`[asg.spreadsheet.sheet_waves.discount_prices]`:** This is where the discounted prices to be added to the spreadsheet are specified. 
```
[asg.spreadsheet.sheet_waves]
discounted_prices = [
    "50%",
    "60%",
]
```
* **`[asg.spreadsheet.sheet_waves.discount_text_map]`:** This is where the text map for the discounted prices is specified. 
```
[asg.spreadsheet.sheet_waves]
discount_text_map = "{t} off (usd)"
```

##### Custom fields
You can customize how fields are calculated in sheet-waves using the following fields in `config.toml`.

* **`[asg.spreadsheet.sheet_waves.calculate_fields]`:** This is where new column mappings can be specified using the following basic structure: 
```
[asg.spreadsheet.sheet_waves.calculate_fields.<new_column_name>]
map_from = "<existing column name>"
[asg.spreadsheet.sheet_waves.calculate_fields.<new_column_name>.map]
"value from existing column" = "value for new column"
```

Here is an example for mapping the `Rights` column (R1, R2, R3, etc) to a new `is_private` column (either 1 or 0).

```
[asg.spreadsheet.sheet_waves.calculate_fields.is_private]
map_from = "Rights"

[asg.spreadsheet.sheet_waves.calculate_fields.is_private.map]
"R1" = 1
"R2" = 1
"R3" = 1
"RA2" = 1
```

This structure can be extended to map from multiple existing columns:

```
[asg.spreadsheet.sheet_waves.calculate_fields.<new_column_name>]
map_from = [
"Existing column 1",
"Existing column 2",
]
[asg.spreadsheet.sheet_waves.calculate_fields.<new_column_name>.map.<Column 1 value>]
"Column 2 value" = "value for new column"
```

If you want the value to be ignored for a specific mapping, you can use `"any"` as a placeholder value.
Here is an example that maps books with any `Category 1` and a `Category 2` of `History` to a new column `category_path` of value `Non-Fiction/History & Politics/`.

```
[asg.spreadsheet.sheet_waves.calculate_fields.category_path]
map_from = [
"Category 1",
"Category 2",
]
[asg.spreadsheet.sheet_waves.calculate_fields.category_path.map."any"]
"History" = "Non-Fiction/History & Politics/"
```