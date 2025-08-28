# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import argparse
import json
import os
from importlib import import_module
from pathlib import Path

# from .finders.files import Fnmatches, Extensions, Names
from typing import List, Set

import msgspec
from tabulate import tabulate

PACKAGE_DIR = Path(__file__).parent.absolute()

FINDER_PACKAGE_DIRS = [PACKAGE_DIR / "finders"]

FINDER_PACKAGES = {
    path.stem.replace("_", "."): import_module(f".{path.stem}", "taggie.finders")
    for finder_package_dir in FINDER_PACKAGE_DIRS
    for path in finder_package_dir.glob("*.py")
    if not path.stem.startswith("_")
}

FINDER_TYPES = [finder.Finder for finder in FINDER_PACKAGES.values()]


def get_tag_directory(tag_path: Path) -> Set[str]:
    tag_files = set()
    for root, _, files in os.walk(tag_path):
        root_path = Path(root)
        for file in files:
            tag_files.add(str(root_path / file))
    return tag_files


def get_tag_files(tag_files: List[str]) -> Set[str]:
    all_tag_files = set()
    for tag_file in tag_files:
        tag_path = Path(tag_file)
        if tag_path.is_dir():
            all_tag_files |= get_tag_directory(tag_path)
        else:
            all_tag_files.add(tag_file)
    return all_tag_files


def get_all_files(path: Path) -> Set[str]:
    all_files = set()
    for root, _, files in os.walk(path):
        root_path = Path(root)
        relative_path = root_path.relative_to(path)
        for file in files:
            all_files.add(str(relative_path / file))
    return all_files


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--tag-file", dest="tag_files", action="append")
    parser.add_argument("-f", "--filter", dest="filters", action="append")
    parser.add_argument(
        "-s", "--sort", dest="sort_by", choices=["most", "name"], default="most"
    )
    args = parser.parse_args()

    base_path = Path.cwd()

    # print(FINDER_PACKAGES)
    # print(FINDER_TYPES)

    all_tag_files = get_tag_files(args.tag_files)
    # print(all_tag_files)

    all_files = get_all_files(base_path)
    # print(all_files)

    # map_file_tags = {}
    # map_tag_files = {}

    for tag_file in all_tag_files:
        finders = msgspec.yaml.decode(open(tag_file).read(), type=List[*FINDER_TYPES])
        for finder in finders:
            if args.filters and not any(fi in finder.filters for fi in args.filters):
                continue

            finder_type = (
                Path(finder.__class__.__module__)
                .suffix.lower()
                .replace(".", "")
                .replace("_", ".")
            )
            FINDER_PACKAGES[finder_type].register(finder)

    all_found_tags = {}
    for finder_type, finder_package in FINDER_PACKAGES.items():
        found_tags = finder_package.find_tags(all_files)
        for tag, files in found_tags.items():
            all_found_tags.setdefault(tag, set())
            all_found_tags[tag] |= files

    # print(all_found_tags)

    table = []
    for tag, files in found_tags.items():
        table.append([len(files), tag, list(files)[0]])

    if args.sort_by == "most":
        table = sorted(table, key=lambda k: k[0], reverse=True)
    elif args.sort_by == "name":
        table = sorted(table, key=lambda k: k[1])

    if table:
        print(
            tabulate(
                table,
                tablefmt="plain",
                headers=["TOTAL", "NAME", "EXAMPLE"],
                colalign=["left", "left", "left"],
            )
        )

    # print(json.dumps(found_tags, indent=2, cls=SetEncoder))

    # from .finders.file_extension import _EXTENSIONS, _TAGS
    # import pprint
    # pprint.pprint(_EXTENSIONS)
    # pprint.pprint(_TAGS)

    # for pattern in finder.patterns:
    #     if isinstance(pattern, str):
    #         finder.files.extend(fnmatch.filter(all_files, pattern))
    #     elif isinstance(pattern, Extensions):
    #         for extension in pattern.extensions:
    #             finder.files.extend([file for file in all_files if Path(file).suffix == f".{extension}"])
    #     elif isinstance(pattern, Names):
    #         for name in pattern.names:
    #             finder.files.extend([file for file in all_files if Path(file).name == name])
    #     else:
    #         raise NotImplementedError
    # found = finder.get()
    # if found:
    #     found_finders.append(found)


#     found_finders = []
#
#     for tag_file in all_tag_files:
#         finders = msgspec.yaml.decode(open(tag_file).read(), type=List[Fnmatches | Extensions | Names])
#         for finder in finders:
#             if args.filters and not any(fi in finder.filters for fi in args.filters):
#                 continue
#
#             finder.find(all_files)
#             # for pattern in finder.patterns:
#             #     if isinstance(pattern, str):
#             #         finder.files.extend(fnmatch.filter(all_files, pattern))
#             #     elif isinstance(pattern, Extensions):
#             #         for extension in pattern.extensions:
#             #             finder.files.extend([file for file in all_files if Path(file).suffix == f".{extension}"])
#             #     elif isinstance(pattern, Names):
#             #         for name in pattern.names:
#             #             finder.files.extend([file for file in all_files if Path(file).name == name])
#             #     else:
#             #         raise NotImplementedError
#             found = finder.get()
#             if found:
#                 found_finders.append(found)
#
#     found_tags = {}
#     for finder in found_finders:
#         for tag in finder.tags:
#             found_tags.setdefault(tag, [])
#             found_tags[tag].append(finder)
#
#     # for finder in found_finders:
#         # print(finder.patterns, len(finder.files), finder.tags)
#
#     for tag, finders in found_tags.items():
#         print(sum(len(finder.files) for finder in finders), tag)
