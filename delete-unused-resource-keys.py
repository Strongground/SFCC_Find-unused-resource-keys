#!/usr/bin/python3

import argparse
from os import path, walk, sep, getcwd
import re
from pprint import *
import jprops as jprops

version = 0.83
lookup_files = ['.isml', '.ds', '.js', '.xml']

def delete_unused_keys(source_file, target_file, source_dir, target_dir, verbose, write_log):
    total_unused = 0
    if source_dir:
        print_verbose(verbose, 'Reading from specified directory "./'+source_dir+'"')
    else:
        source_dir = getcwd()
        print_verbose(verbose, 'No input directory specified, reading from "./'+source_dir+'"')
    
    if target_dir:
        print_verbose(verbose, 'Writing into specified directory "./'+target_dir+'"')
    else:
        print_verbose(verbose, 'No output directory specified, writing into "./'+target_dir+'"')
    
    if source_file:
        print_verbose(verbose, 'Explicit conversion of given file.')
    else: 
        print_verbose(verbose, 'Converting all properties files found in "resources" folders in all cartridges.')
    
    for current_dir, _, sub_files in walk(source_dir):
        for current_file in sub_files:
            if (not source_file and 'resources' in current_dir and path.splitext(current_file)[1] == '.properties') or (source_file and 'resources' in current_dir and current_file == source_file):
                print_verbose(verbose, 'Hit: '+path.join(current_dir, current_file))
                if not target_dir:
                    target_dir = current_dir
                try:
                    result = check_file(current_file, target_file, current_dir, target_dir, verbose)
                    print_verbose(verbose, 'file check completed for',current_file)
                except:
                    print('Error in file',current_file,'... skipping.')
                    break
                if write_log:
                    with open(path.join(target_dir, 'cleaning_report.txt'), mode='a+', encoding='utf-8') as log_file:
                        if result['empty']:
                            log_file.write('\n==== EMPTY: File '+current_file+' had no keys that where used anywhere in the project.\n')
                        if len(result['unused_keys']) > 0:
                            log_file.write('\n\n==== Found '+str(len(result['unused_keys']))+' resource keys in file '+current_file+' that where not used anywhere:\n')
                            total_unused += len(result['unused_keys'])
                            for key in result['unused_keys']:
                                log_file.write('\n'+key[0])
                        log_file.close()
    if write_log:
        with open(path.join(target_dir, 'cleaning_report.txt'), mode='a+', encoding='utf-8') as log_file:
            if total_unused > 0:
                log_file.write('\n\n==== Total unused keys found in this run: '+str(total_unused))
            log_file.close()    
    print('Done.')

def is_ignored_folder(folder_path, verbose):
    for folder in ['node_modules', 'dist', '.git']:
        if folder in folder_path:
            print_verbose(verbose, 'Ignored folder, skipping')
            return True

def check_file(source_file, target_file, source_dir, target_dir, verbose):
    unused_props = []
    file_empty = False
    found_props = []
    map_obj = {}
    if not target_file:
        target_file = source_file
    origin_file = open(path.join(source_dir, source_file))
    print_verbose(verbose, '############################')
    print_verbose(verbose, 'Cleansing file '+source_dir+sep+source_file+' with holy fire!')
    for prop in jprops.iter_properties(origin_file):
        key_found = False
        if prop[0] not in found_props:
            print_verbose(verbose, 'For prop:',prop[0])
            for cur_dir, _, sub_files in walk(getcwd()):
                if key_found or is_ignored_folder(cur_dir, verbose):
                    break
                else:
                    for cur_file in sub_files:
                        if path.splitext(cur_file)[1] in lookup_files and not key_found:
                            comparison_file = open(path.join(cur_dir,cur_file))
                            for line in comparison_file:
                                result = re.findall(prop[0], line)
                                if result:
                                    print_verbose(verbose, 'In',cur_file,'found key',prop[0])
                                    found_props.append(prop)
                                    map_obj[prop[0]] = prop[1]
                                    key_found = True
                                    break
        if not key_found:
            # In case key is not used anywhere in the project, it will be collected here for reporting
            unused_props.append(prop)
    if len(found_props) == len(unused_props):
        print_verbose(verbose, 'Something is fishy here... we found as many keys as we declared "unused". I call bullshit!')
    if len(map_obj) > 0:
        # Write out back the contents minus the unused keys
        with open(path.join(target_dir, target_file), mode='w', encoding='utf-8') as writefile:
            jprops.store_properties(writefile, map_obj, comment='######### This file has been cleaned of unused keys by delete-unusued-resource-keys.py (version '+str(version)+') #########\n######### If you find any errors where made, contact n.stroehmer-lohfink@internetstores.de #########')
            writefile.close()
        origin_file.close()
        print_verbose(verbose, 'Written all keys of file',target_file)
    else:
        # No used keys found at all
        print_verbose(verbose,'File',source_file,'didn\'t contain any used resources and was thus not converted at all. Consider deleting it.')
        file_empty = True
    return {'empty':file_empty, 'unused_keys':unused_props}

def print_verbose(verbose, *args):
    if verbose:
        print(*args)

def cli_parse():
    """Start the CLI interface."""
    ## Define CLI arguments
    parser = argparse.ArgumentParser(description='Iterate over all properties files in a given directory and look for usage of the keys in those files. If a key is not used, delete it from the file.')
    parser.add_argument('-sd', '--source-dir', action='store', dest='source_dir', help='Set the directory of the properties files that should be cleaned. Can contain sub directories. If ommitted, the current location of the script file will be used.')
    parser.add_argument('-td', '--target-dir', action='store', dest='target_dir', help='Set the directory where clean properties files are saved. If omitted, the source directory is used.')
    parser.add_argument('-sf', '--source-file', action='store', dest='source_file', help='Optionally set the properties file that should be cleaned. If omitted, all properties files in the source directory will be converted.')
    parser.add_argument('-tf', '--target-file', action='store', dest='target_file', help='Optionally set the desired name for target properties file. If the file already exists, it\'s contents will be overwritten. If omitted, the name of the source file will be used.')
    parser.add_argument('-l', '--log-results', action='store_true', dest='write_log', help='Optionally log all unused keys and empty files to illustrate how much stuff is not needed anymore.')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Set to verbose.')
    args = parser.parse_args()

    delete_unused_keys(args.source_file, args.target_file, args.source_dir, args.target_dir, args.verbose, args.write_log)

cli_parse()
