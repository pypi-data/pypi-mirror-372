# doc_utils/topic_map_parser.py

import os
import yaml
import glob

def detect_repo_type(base_path='.'):
    """
    Detect whether the repository uses topic maps (OpenShift-docs style) 
    or master.adoc files (traditional style).
    
    Returns:
        'topic_map' - if _topic_maps directory with .yml files exists
        'master_adoc' - if master.adoc files are found
        'unknown' - if neither pattern is detected
    """
    topic_maps_dir = os.path.join(base_path, '_topic_maps')
    
    # Check for topic maps
    if os.path.isdir(topic_maps_dir):
        yml_files = glob.glob(os.path.join(topic_maps_dir, '*.yml'))
        if yml_files:
            return 'topic_map'
    
    # Check for master.adoc files using os.walk to avoid symlink issues
    master_files = []
    for root, dirs, files in os.walk(base_path):
        # Skip symbolic link directories to prevent infinite recursion
        dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
        
        # Check for master.adoc in this directory
        if 'master.adoc' in files:
            master_files.append(os.path.join(root, 'master.adoc'))
            
    if master_files:
        return 'master_adoc'
    
    return 'unknown'


def extract_files_from_topic_map(topic_map_path):
    """
    Extract all referenced .adoc files from a topic map YAML file.
    
    Returns a set of file paths referenced in the topic map.
    """
    referenced_files = set()
    
    try:
        with open(topic_map_path, 'r', encoding='utf-8') as f:
            # Use safe_load_all to handle multiple YAML documents
            documents = yaml.safe_load_all(f)
            
            for doc in documents:
                if doc is None:
                    continue
                    
                # Process each topic group
                process_topic_group(doc, referenced_files)
                
    except Exception as e:
        print(f"Warning: Could not parse topic map {topic_map_path}: {e}")
    
    return referenced_files


def process_topic_group(group, referenced_files, parent_dir=''):
    """
    Recursively process a topic group to extract all file references.
    """
    if not isinstance(group, dict):
        return
        
    # Get the directory for this group
    current_dir = group.get('Dir', '')
    if parent_dir and current_dir:
        current_dir = os.path.join(parent_dir, current_dir)
    elif parent_dir:
        current_dir = parent_dir
        
    # Process topics in this group
    topics = group.get('Topics', [])
    if isinstance(topics, list):
        for topic in topics:
            if isinstance(topic, dict):
                # If topic has a File, add it
                if 'File' in topic:
                    file_path = topic['File']
                    if current_dir:
                        file_path = os.path.join(current_dir, file_path)
                    # Add .adoc extension if not present
                    if not file_path.endswith('.adoc'):
                        file_path += '.adoc'
                    referenced_files.add(file_path)
                
                # If topic has nested topics (sub-group), process recursively
                if 'Topics' in topic:
                    # For nested topics, use the Dir from the topic if present
                    sub_dir = topic.get('Dir', '')
                    if sub_dir:
                        # If topic has its own Dir, append it to current_dir
                        if current_dir:
                            next_dir = os.path.join(current_dir, sub_dir)
                        else:
                            next_dir = sub_dir
                    else:
                        # If no Dir specified, keep current_dir
                        next_dir = current_dir
                    # Process only the Topics, not the whole topic dict
                    process_topic_group({'Topics': topic['Topics']}, referenced_files, next_dir)


def get_all_topic_map_references(base_path='.'):
    """
    Get all .adoc files referenced in all topic maps.
    
    Returns a set of all referenced file paths.
    """
    topic_maps_dir = os.path.join(base_path, '_topic_maps')
    all_references = set()
    
    if not os.path.isdir(topic_maps_dir):
        return all_references
        
    # Process all .yml files in _topic_maps
    for yml_file in glob.glob(os.path.join(topic_maps_dir, '*.yml')):
        references = extract_files_from_topic_map(yml_file)
        all_references.update(references)
    
    return all_references