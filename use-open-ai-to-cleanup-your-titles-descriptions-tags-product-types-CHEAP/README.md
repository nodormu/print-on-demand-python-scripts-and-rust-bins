This was done on Ubuntu 24.04 LTS using python 3.12.x, but these scripts should run fine on windows and mac using python as long as your pip deps are setup  
Here are the commands for ubuntu 24.04 LTS  
sudo apt update  
sudo apt install python3-dev python3-pip

Then source to your python sandbox and pip install  
pip install openai==1.99.4

You might be able to use newer versions, but I had ZERO luck with 2.x and newer. 1.99.9 might work, but I haven't tested it yet.

These scripts will help you get your titles, descriptions, product_type and tags cleaned up with AI MUCH cheaper than using some 3rd party's service limited subset for processing such data.

If you don't need the JSON parts of it, then just use the following scripts to keep your processing ultra cheap for OpenAI calls

02-clean_name_output_to_new_csv-V4.py == This script uses your OpenAI key and organization strings to clean up the names and export to a new CSV for import

05-clean_descriptions_output_to_new_csv-V6.py == This script uses your OpenAI key and organization strings to clean up the names and export to a new CSV for import

08-add-tags-and-type-output-to-new-CSV == This script will use your Open AI key and organization strings to add respective tags and product type to your products

I recommend you test with the provide 01_RAW_JSON_DUMPS file so you can see how the CSV file headers look

Run the scripts in the numerical order presented if you plan on using the JSON parts, with your data as specified for each CSV input file to keep this processing SUPER CHEAP on token usage, and as with the short version above, test with the JSON dumps I provided so you can see how this works in case you need to modify parts of this for your own purposes.

I'm talking processing 10,000 titles, descriptions, tags and product_types for less than 25 bucks purchasing data processing tokens from OpenAI, WAY cheaper and cleaner than any 3rd party provided monthly service, especially when you see all the scammy, oh, you want that data transformation, that will be another 29.99 a month for your shopify store if you want the capability. Using these scripts will save a TON of money. Tryna to help bootstrappers and single moms on a budget here, and still get the best results possible, on the cheap if you use 3.5 turbo.

These scripts require you have JSON files for each of your entries exporting data for each part of the cleanup, but they are easily modifiable for your specific JSON file contents.

IMPORTANT NOTE #1
-----------------
the tag prep output script,

07-export-filename-name-description-for-tags-type-prep-to-CSV

REQUIRES that you manually add the following header:  custom_tags,

to the exported CSV file, so the header line is filename,name,description,custom_tags

This allows you to manually (or thru your own script) add a custom tag and give you a chance to spot check the names and descriptions as a sanity check for you products.

The custom tag (or multiple tags, which would need to be separated by |, i.e. printify|kitchen|living room) will be placed at the end of the list of those generated with the OpenAI API call.

The cool part about this script, is that you don't have to put a custom tag, but be sure the header is there or the script will fail, and if you do happen to add custom_tags and miss an entry, the script fails and the screen output shows you where it failed, then you can go into the CSV file, add the one you missed, then restart the script and it will pick up where it left off because of the PICKUP_TEXT_FILE.


IMPORTANT NOTE #2
-----------------
For the clean name using openai script, be sure you alter/change the strings in lines 38 and 43 to fit your specific product requirements.

Line 38 is so certain words are NOT used/reused

Line 43 is to avoid duplicate words that are more so synonyms so you don't have something like "comforter bedspread" in the name output as an example

IMPORTANT NOTE #3
-----------------
I do NOT recommend opening CSV files in spreadsheet programs due to how they can completely screw up certain long strings and numbers.

I used this code editor because I like the color coding:  https://kate-editor.org/get-it/

I have posted a short list of JSON files you can use for testing the script, as you may need to modify it some for your specific purposes.

Script Explanations
-------------------
01-export-filename-and-names-title-to-CSV.py == This script exports the names from your JSON files. Pay VERY close attention to lines 38 and 43, as you will need to modify/change those strings for your specific product. See important note number 2 for the requirement needs.

02-clean_name_output_to_new_csv-V4.py == This script uses your OpenAI key and organization strings to clean up the names and export to a new CSV for import

03-import-clean_name-to-JSON-files.py == This script imports those names you just got cleaned up with OpenAI

04-export-filename-name-description-to-CSV.py == This script exports the filename, name and ugly description from your JSON files with the cleaned titles

05-clean_descriptions_output_to_new_csv-V6.py == This script uses your OpenAI key and organization strings to clean up the names and export to a new CSV for import.

06-import-clean_description-to-JSON-files-V6.py == This script imports your cleaned descriptions into JSON files

07-export-filename-name-description-for-tags-type-prep-to-CSV.py == This script exports filename,name,description for tag and product_type prep, DON'T FORGET TO ADD ,custom_tags to the header file from the previous script and any custom tags separted by |, i.e. ,kitchen|living room

08-add-tags-and-type-output-to-new-CSV == This script will use your Open AI key and organization strings to add respective tags and product type to your products

09-write-tags-type-to-json-folder-output == This script will take the output CSV from the previous script and your JSON file to the final folder:  04_JSON_DUMPS_CLEANED_TAGS_PRODUCT_TYPES






