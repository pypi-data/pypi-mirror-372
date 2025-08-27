from modules import forms
from ptlibs import ptprinthelper

def print_result(list_of_results: list, args):

    if not len(list_of_results) > 1:
        for r in list_of_results:
            ptprinthelper.ptprint(" ", "TEXT", condition=not args.json)
            for log, msg_type in r.logs:
                ptprinthelper.ptprint(log, msg_type, condition=not args.json)
                if msg_type.upper() == "ERROR":
                    pass#return
    else:
        if args.grouping_complete:
            ptprinthelper.ptprint("Summary (unique values)", "TITLE", condition=not args.json, newline_above=True)

    list_of_results = [l.data for l in list_of_results]
    titles = [i for i in {k: v for k, v in list_of_results[0].items() if v is not None}.keys()]
    args.file_handle = None
    if args.output and not args.output_parts:
        args.file_handle = open(args.output, "w")

    for index, title in enumerate(titles):
        if title in ["url", "abs_urls"]:
            continue

        if args.output_parts:
            args.file_handle = _get_handle(title, args)

        if args.grouping_complete:
            merged_result = _get_data_type(title)


        _print_title(title, args, index)
        for index, result_dictionary in enumerate(list_of_results):

            if args.grouping:
                _print_current_url(list_of_results, index, args)

            if args.grouping_complete:
                merged_result = _fill_merged_result(merged_result, list_of_results, index, title)

            else:
                if title == "internal_urls_with_parameters":
                    _print_parsed_urls(list_of_results, index, args)
                elif title == "metadata":
                    _print_metadata(list_of_results, index, args)
                elif title == "forms":
                    _print_forms(list_of_results, index, args)
                elif title == "comments":
                    _print_comments(list_of_results, index, args)
                elif title == "google_keys":
                    _print_google_keys(list_of_results, index, args)
                elif result_dictionary.get(title):
                    ptprinthelper.ptprint("\n".join(result_dictionary[title]), filehandle=args.file_handle, condition=not args.json)
                else:
                    ptprinthelper.ptprint("Not found", "", filehandle=args.file_handle, condition=not args.json)
                _get_endl(list_of_results, index, args)

        if args.grouping_complete:
            if title == "internal_urls_with_parameters":
                merged_result["internal_urls_with_parameters"] = sorted(merged_result["internal_urls_with_parameters"], key=lambda k: k['url'])
                _print_parsed_urls([merged_result], index=0, args=args)
            elif title == "metadata":
                _print_metadata([merged_result], index=0, args=args)
            elif title == "forms":
                _print_forms([merged_result], index=0, args=args)
            elif title == "comments":
                _print_comments([merged_result], index=0, args=args)
            elif title == "google_keys":
                _print_google_keys([merged_result], index=0, args=args)
            elif merged_result:
                ptprinthelper.ptprint("\n".join(sorted(merged_result)), "", end=_check_if_next(list_of_results, index)+"\n", filehandle=args.file_handle, condition=not args.json)
            else:
                ptprinthelper.ptprint("Not found", "", filehandle=args.file_handle, condition=not args.json)

        if args.output_parts:
            args.file_handle.close()

    if args.file_handle:
        args.file_handle.close()

def _get_handle(title, args):
    parsed_file_name = args.output.rsplit(".", 1)
    file_extension = "." + parsed_file_name[-1] if len(parsed_file_name) > 1 else ""
    handle = open(f"{parsed_file_name[0]}_{title.upper()}{file_extension}", "w")
    return handle



def _print_google_keys(list_of_results, index, args):
    result_dict = list_of_results[index].get("google_keys")
    if result_dict:
        for key, value in result_dict.items():
            ptprinthelper.ptprint(f"{key}:", "TEXT", condition=not args.json, indent=0)
            ptprinthelper.ptprint("\n    ".join(value), "TEXT", condition=not args.json, indent=4)
            ptprinthelper.ptprint(f" ", "TEXT", condition=not args.json)#
    else:
        ptprinthelper.ptprint("Not found", "TEXT", not args.json, filehandle=args.file_handle)

def _print_title(title, args, index=0):
    if args.file_handle and index > 0:
        args.file_handle.write("\n")
    #ptprinthelper.ptprint(f'\n{ptprinthelper.get_colored_text(title.upper().replace("_", " "), color="TITLE")}{"" * len(title)}', "", filehandle=args.file_handle, condition=not args.json)
    ptprinthelper.ptprint(f'\n{ptprinthelper.get_colored_text(title.upper().replace("_", " "), color="TITLE")}\n{"-" * len(title)}', "", filehandle=args.file_handle, condition=not args.json)


def _get_endl(list_of_results, index, args):
    """Add space if not last record"""
    if args.grouping and list_of_results[index] != list_of_results[-1]:
        ptprinthelper.ptprint(f" ", "", filehandle=args.file_handle, condition=not args.json)


def _check_if_next(list_of_results, index):
    try:
        endl = "\n" if list_of_results[index+1] else ""
    except Exception:
        endl = ""
    return endl


def _print_parsed_urls(list_of_results, index, args):
    if not list_of_results[index]["internal_urls_with_parameters"]:
        ptprinthelper.ptprint("Not found", "", not args.json, filehandle=args.file_handle)
    elif type(list_of_results[index]["internal_urls_with_parameters"]) == str: # If error msg (eg. cannot search file)
        ptprinthelper.ptprint(list_of_results[index]["internal_urls_with_parameters"], "", filehandle=args.file_handle, condition=not args.json)
    else:
        for url in list_of_results[index]["internal_urls_with_parameters"]:
            ptprinthelper.ptprint(f"URL: {url['url']}", "", filehandle=args.file_handle, condition=not args.json,)
            ptprinthelper.ptprint(f"Parameters:", "", filehandle=args.file_handle, condition=not args.json)
            for parameter in url['parameters']:
                ptprinthelper.ptprint(f'          {parameter}', "", condition=not args.json, filehandle=args.file_handle, end="\n")
            if url != list_of_results[index]["internal_urls_with_parameters"][-1]: # Add space if not last
                ptprinthelper.ptprint(f" ", "", filehandle=args.file_handle, condition=not args.json)


def _print_comments(list_of_results, index, args):
    if not any(list_of_results[index]["comments"].values()):
        ptprinthelper.ptprint(f"Not found", "", filehandle=args.file_handle, condition=not args.json)
    else:
        for key in list_of_results[index]["comments"].keys():
            if list_of_results[index]["comments"][key]:
                #ptprinthelper.ptprint(ptprinthelper.get_colored_text(key.upper(), "TITLE"), filehandle=args.file_handle, condition=not args.json)
                ptprinthelper.ptprint('\n'.join(list_of_results[index]["comments"][key]), "", filehandle=args.file_handle, condition=not args.json)


def _print_metadata(list_of_results, index, args):
    longest_key, _ = max(list_of_results[index]["metadata"].items(), key=lambda x: len(x[0]))
    for key, value in list_of_results[index]["metadata"].items():
        if type(value) is list:
            value = ', '.join(map(str, value))
        else:
            value = str(value).replace("\n", "\\n")
        ptprinthelper.ptprint(f"{key}{' '*(len(longest_key)-len(key))}: {', '.join(value) if type(value) is list else value}", "", filehandle=args.file_handle, condition=not args.json)


def _print_forms(list_of_results, index, args):
    if args.grouping_complete:
        if not list_of_results[0]["forms"]:
            ptprinthelper.ptprint("Not found", "", filehandle=args.file_handle, condition=not args.json)
        else:
            _pretty_print_forms(list_of_results, index, args)
    else:
        if not list_of_results[index]["forms"]:
            ptprinthelper.ptprint("Not found", "", filehandle=args.file_handle, condition=not args.json)
        elif type(list_of_results[index]["forms"]) == str:
            ptprinthelper.ptprint(list_of_results[index]["forms"], "", filehandle=args.file_handle, condition=not args.json)
        else:
            _pretty_print_forms(list_of_results, index, args)


def _print_current_url(list_of_results, index, args):
    ptprinthelper.ptprint(ptprinthelper.get_colored_text(f"{list_of_results[index]['url']}", 'INFO'), "", not args.json, filehandle=args.file_handle)


def _get_data_type(title: str):
    """Return appropriate data type for supplied title"""
    if title == "metadata":
        merged_result = {"metadata": {}}
    elif title == "internal_urls_with_parameters":
        merged_result = {"internal_urls_with_parameters": []}
    elif title == "forms":
        merged_result = {"forms": list()}
    elif title == "comments":
        merged_result = {"comments": {"html": [], "js": [], "css": []}}
    elif title == "google_keys":
        merged_result = {"google_keys": {}}
    else:
        merged_result = set()
    return merged_result


def _pretty_print_forms(list_of_results, index, args):
    for idx, form in enumerate(list_of_results[index]["forms"]):
        for key, value in form.items():
            space = 0 if key == "form_name" else 9
            if value == '':
                value = "''"
            if key in ["inputs", "selects"]:
                if form[key]:
                    ptprinthelper.ptprint(" ", "", filehandle=args.file_handle, condition=not args.json)
                if not form[key]:
                    continue
                ptprinthelper.ptprint(f"{' '*space}{key.title()}:", "", filehandle=args.file_handle, condition=not args.json)
                space += len(key)
                for idx2, dictionary in enumerate(form[key]):
                    for key2, value2 in dictionary.items():
                        if not value2 and value2 is not None:
                            value2 = "''"
                        if key2 == "options":
                            ptprinthelper.ptprint(f"{' '*space}{key2.title()}:", "", filehandle=args.file_handle, condition=not args.json)

                            space += len(key)
                            for option in dictionary[key2]:
                                if not option and option is not None:
                                    option = "''"
                                ptprinthelper.ptprint(f"{' '*space}{option}", "", filehandle=args.file_handle, condition=not args.json)
                            if args.grouping_complete and form != list_of_results[index]["forms"][-1]:
                                ptprinthelper.ptprint(" ", "", filehandle=args.file_handle, condition=not args.json)
                        else:
                            ptprinthelper.ptprint(f"{' '*space}{key2.title()}: {value2}", "", filehandle=args.file_handle, condition=not args.json)
                    if idx2+1 != len(form[key]):
                        ptprinthelper.ptprint(" ", "", filehandle=args.file_handle, condition=not args.json)
            else:
                ptprinthelper.ptprint(f"{' '*space}{key.title().replace('_',' ')}: {value}", "", filehandle=args.file_handle, condition=not args.json)
        if idx+1 != len(list_of_results[index]["forms"]):
            ptprinthelper.ptprint(" ", "", filehandle=args.file_handle, condition=not args.json)


def _fill_merged_result(merged_result, list_of_results, index, title):
    if title == "internal_urls_with_parameters":
        for result_dict in list_of_results[index]["internal_urls_with_parameters"] or []:
            if result_dict not in merged_result["internal_urls_with_parameters"]:
                merged_result["internal_urls_with_parameters"].append(result_dict)

    elif title == "metadata":
        if list_of_results[index].get("metadata"):
            for key, value in list_of_results[index]["metadata"].items():
                if key not in merged_result["metadata"]:
                    merged_result["metadata"][key] = value

                elif isinstance(merged_result["metadata"][key], list):
                    if isinstance(value, list):
                        merged_result["metadata"][key].extend([val for val in value if val not in merged_result["metadata"][key]])
                    else:
                        if value not in merged_result["metadata"][key]: merged_result["metadata"][key].append(value)
                else:
                    if isinstance(value, list):
                        merged_result["metadata"][key] = [merged_result["metadata"][key]]
                        merged_result["metadata"][key].extend([val for val in value if val not in merged_result["metadata"][key]])
                    else:
                        merged_result["metadata"][key] = [merged_result["metadata"][key]]
                        if value not in merged_result["metadata"][key]: merged_result["metadata"][key].append(value)

    elif title == "forms":
        for form in list_of_results[index]["forms"]:
            form_without_value_keys = forms.pop_value_key_from_form(form)
            if form_without_value_keys not in merged_result["forms"]:
                merged_result["forms"].append(form_without_value_keys)

    elif title == "comments":
        for key, value_list in (list_of_results[index].get("comments") or {}).items():
            merged_result["comments"][key].extend(value_list)

    elif title == "google_keys":
        merged_result.setdefault("google_keys", {})
        for key, value_list in (list_of_results[index].get("google_keys") or {}).items():
            merged_result["google_keys"].setdefault(key, []).extend(value_list)

    else:
        if list_of_results[index].get(title):
            for i in list_of_results[index][title]:
                merged_result.add(i)

    return merged_result
