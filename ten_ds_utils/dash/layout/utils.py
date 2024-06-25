def check_all_pages_exist(directory_manager, user_defined_pages):
    all_paths = []
    for primary_path, children in user_defined_pages.items():
        if isinstance(children, str):
            all_paths.append(primary_path)
        else:
            for secondary_path in children['section-pages']:
                all_paths.append(f"{primary_path}/{secondary_path}")

    for path in all_paths:
        if path not in directory_manager._url_objects:
            raise Exception(f'No path "{path}" in the directory manager')