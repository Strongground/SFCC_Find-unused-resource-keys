# Find Unused Resource Keys
Find unused resource keys in properties files in a Salesforce Commerce Cloud project and get rid of them.

It looks through all \*.properties files in a specified directory and sub-directories and then proceeds to look through all specified file types in the project looking for each resource key in each line, taking note of each one that is not found. Only found keys are included in the final output, so as a result you have the  properties files minus the unused keys.

## Preamble
This tool is meant as a one-time check to weed out unused keys before transitioning to the excellent https://github.com/SalesforceCommerceCloud/resource-manager, so that there isn't too much overhead and bloat in terms of unused keys. You might adopt it for use in automatic processes, but I didn't write it with that intention - so do your own tests accordingly before using it.

Since this might touch thousands of keys in hundreds of files, you are advised to sanity check results and always keep backups. I don't want to be responsible for you losing translations over this. :) Though in my tests, no errors of any kind came to my attention.

## How to
1. Install jprops Python package. `pip3 install jprops`
2. Clone repository or direct-download the delete-unused-resource-keys.py file from Github.
3. Put it into a directory **above or within** the directory containing your properties files. It can only go down on the folder hierarchy, never up.
4. Open the help page of the tool by executing, on a CLI: `delete-unused-resource-keys.py -h`. All arguments are explained so you can see what you need.
5. Example command: `python3 delete-unused-resource-keys.py -sd cartridges -td cleaned_properties -l -v`, looking through all resource files in the 'cartridges' folder, putting cleaned versions of those into 'cleaned_properties' folder. It also writes a logfile (put in the target directory if given, else next to script file) called 'cleaning_report.txt'. It is also set to verbose, so outputting additional information during runtime.

### Notes:
Currently, the tool does not handle duplicate files very well. If you have overloaded properties files in cartridge, i.e. with exact same name but differing contents, the last processed one will win. In this case I recommend using the tool in each cartridge separately. This should also be possible with multiple instances of the script simultaneously, with no issues - just use a different output directory for each instance.

Having _-v/--verbose_ flag lengthens the runtime considerably. If you want to just see what happens, before the actual final run, this is fine. During final run, it makes sense to either not set verbose flag or reroute the output to another file via `python3 delete-unused-resource-keys.py -sd some_dir -td another_dir -v > console_output.txt`.

Some files are ignored during lookup. Those are defined in the `is_ignored_folder` function. There is a simple array inside that function containing file endings. Feel free to change them to suit your needs.

The file types where the script is looking for resource keys is also described in an array called 'lookup_files', defined at the top of the script for convenience. You can just edit the array.

Running this on a multi-language/multi-brand project with hundreds of properties-files (averaging 300-500 lines each) may take 1-2 hrs.

## Contribution
If you have a feasible idea for improvement, find my code horrible and want to improve it or just find an error or edge-case that isn't handled yet, feel free to either create a bug ticket here in Github or a pull request fixing the problem. Your contribution will be listed (except you don't want that).
