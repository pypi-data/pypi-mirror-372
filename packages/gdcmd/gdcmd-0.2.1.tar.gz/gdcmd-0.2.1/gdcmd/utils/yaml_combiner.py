# Taken from: https://github.com/randomnoun/yaml-combine-py
import yaml
import os
import logging
import sys
from urllib.parse import unquote
import copy


class YamlCombiner:
    """Yaml combiner class"""

    def __init__(self):
        self._files = []
        """
        list(str): list of filenames to combine
        """

        self._yaml_files = {}
        """
        dict: YAML file cache ( filename -> contents )
        """

        self._verbose = False

        self._relative_dir = "."

        self._xref_stack = []

    def set_relative_dir(self, relative_dir):
        self._relative_dir = relative_dir

    def set_files(self, files):
        self._files = files

    def set_verbose(self, verbose):
        self._verbose = verbose

    def combine(self, output_stream):
        self._files.sort()
        merged_obj = None
        for f in self._files:
            relative_f = os.path.join(self._relative_dir, f)
            with open(relative_f, "r") as stream:
                try:
                    obj = yaml.safe_load(stream)
                    if merged_obj is None:
                        merged_obj = obj
                    else:
                        self._merge(merged_obj, obj, f, "")
                except yaml.YAMLError as exc:
                    print(exc)

        merged_obj = self._replace_refs(merged_obj, self._relative_dir, "")

        # formatting improvements as per
        # https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
        def str_representer(dumper, data):
            if len(data.splitlines()) > 1:  # check for multiline string
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        yaml.add_representer(str, str_representer)

        # yaml.dump() doesn't include the directives separator
        # include it for compatibility with the java yaml-combine output
        output_stream.write("---\n")

        # For Python 3.7+, dicts preserve insertion order.
        # so let's sort in py 3.6, and not sort in py 3.7
        is_py37 = sys.version_info >= (3, 7, 0)
        yaml.dump(
            merged_obj, output_stream, default_flow_style=False, allow_unicode=True, sort_keys=not is_py37
        )

    def _merge(self, merged_obj, obj, f, prefix):
        clone_list = list(obj.keys())
        for k in clone_list:
            v = obj[k]
            mv = merged_obj.get(k)
            if mv is None:
                # simple merge
                merged_obj[k] = v
            elif v is None:
                # nothing to merge
                pass
            elif isinstance(mv, dict) and isinstance(v, dict):
                # the only thing we can merge are dictionaries
                self._merge(mv, v, f, prefix + str(k) + "/")
            elif type(mv) is type(v):
                # replace if the types are the same
                merged_obj[k] = v
            else:
                raise ValueError("Could not merge " + f + "#" + prefix + str(k) +
                                 " (" + str(type(v)) + ") into merged object " + str(type(mv)))

    def _replace_refs(self, obj, relative_dir, space_prefix):
        """
        Returns a copy of ``obj``, with every $xref "resolved" at every level of the object tree.

        Assuming #Ref points to some structure called "result" then $xrefs are resolved as follows:

            The single item object {$xref: #Ref} always resolves to result.
            E.g., if #Ref points to the array [1, 2, 3] the {$xref: #Ref} resolves to [1, 2, 3].

            When result is an object (dictionary), the multiple item object
            {
                **previous_key_value_pairs
                $xref: #Ref
                **subsequent_keys_value_pairs
            }
            resolves to previous_key_value_pairs | result | subsequent_keys_value_pairs where the | operator is the
            Python dictionary update operator. I.e., the key/value pairs in result override the previous key/value
            pairs, and are overridden by subsequent key/value pairs.
            E.g., if #Ref points to the object {b: 7, c: 8, d: 9} then
            {
                a: 1
                b: 2
                $xref: #Ref
                d: 4
            }
            resolves to
            {
                a: 1  # a is retained from the previous key/value pairs
                b: 7  # b is overridden by the resolved $xref
                c: 8  # c is added from the resolved $xref
                d: 4  # d was added by the resolved $xref, but overridden in the subsequent key/value pairs
            }

            When result is not an object, the multiple item object
            {
                **previous_key_value_pairs
                $xref: #Ref
                **subsequent_keys_value_pairs
            }
            cannot resolve, so a ValueError is raised.
            E.g., if #Ref points to the array [1, 2, 3] then
            {
                a: 1
                b: 2
                $xref: #Ref
                d: 4
            }
            cannot resolve (you can't update an object with an array), so a ValueError is raised.

            In all cases, any $xrefs found in result are resolved recursively.

        Note: This method does not modify ``obj``.
        """

        if isinstance(obj, dict):
            # Case 1: Object; we will replace, merge, or add any resolved xrefs.
            new_obj = dict()

            for k, v in obj.items():
                if k == "$xref":

                    if v in self._xref_stack:
                        raise ValueError(f"$xref cycle detected: {' -> '.join(self._xref_stack + [v])}")
                    self._xref_stack.append(v)
                    result = self._replace_refs(self._get_xref(relative_dir, v), relative_dir, space_prefix)
                    self._xref_stack.pop()

                    if len(obj) == 1:
                        # result replaces the entire one-item object.
                        new_obj = result
                    elif isinstance(result, dict):
                        # result merges into the object.
                        new_obj.update(result)
                    else:
                        raise ValueError(f"Inconsistent $xref types within object:\n\n {obj}")

                else:
                    result = self._replace_refs(v, relative_dir, space_prefix)
                    # result is added to the object.
                    new_obj[k] = result

        elif isinstance(obj, list):
            # Case 2: Array; loop through and resolve each element.
            new_obj = [self._replace_refs(e, relative_dir, space_prefix) for e in obj]

        else:
            # Case 3: Constant; return a copy.
            new_obj = copy.copy(obj)

        return new_obj

    def _get_xref(self, relative_dir, ref):
        # myproject-v1-object.yaml#/definitions/InvalidResponse       existing
        # myproject-v1-swagger-api.yaml#/paths/~1authenticate         the JSON-Pointer way
        # myproject-v1-swagger-api.yaml#/paths/%2Fauthenticate        the url escape way
        # myproject-v1-swagger-api.yaml#/paths/#/authenticate         the randomnoun way.

        # can't have '#' as the start of a key as that's a comment. but you probably can. somehow.
        pos = ref.find("#")
        if pos == -1:
            # local refs still start with a '#'
            # $ref: '#/paths/~1blogs~1{blog_id}~1new~0posts'
            raise ValueError("Unparseable $xref '" + str(ref) + "'")
        else:
            f = ref[0:pos]
            p = ref[pos + 1:]
            result = ""
            as_json_path = True
            for ch in p:
                if ch == "#":
                    as_json_path = not as_json_path
                elif as_json_path:
                    result = result + ch
                else:
                    # escape this jsonpath-ly
                    if ch == "/":
                        result = result + "~1"
                    elif ch == "~":
                        result = result + "~0"
                    else:
                        result = result + ch
            ref = f + "#" + result

            # as per ResolverCache
            # although ResolverCache parses an entire json doc every time there's a ref,
            # even if we've already parsed it.

            ref_parts = ref.split("#/")
            file = ref_parts[0]
            definition_path = ref_parts[1] if len(ref_parts) == 2 else None

            contents = self._yaml_files.get(file)
            if contents is None:
                relative_f = os.path.join(relative_dir, file)
                with open(relative_f, "r") as stream:
                    try:
                        contents = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        raise ValueError("Invalid YAML file '" + relative_f + "'") from exc
                self._yaml_files[file] = contents

            if self._verbose:
                logging.info("definitionPath '" + definition_path + "' in '" + file + "'")

            if definition_path is None:
                return contents
            else:
                json_path_elements = definition_path.split("/")
                node = contents
                for json_path_element in json_path_elements:
                    try:
                        node = node[self._unescape_pointer(json_path_element)]
                    except BaseException:
                        raise ValueError("Could not descend into " + json_path_element +
                                         " of " + definition_path + " in contents of " + file)
                    if node is None:
                        raise ValueError("Could not find '" + definition_path + "' in contents of " + file)
                return node

    def _unescape_pointer(self, json_path_element):
        # URL decode the fragment
        # hopefully this is the python equivalent of URLDecoder.decode()
        json_path_element = unquote(json_path_element)
        # Unescape the JSON Pointer segment using the algorithm described in RFC 6901,
        # section 4: https://tools.ietf.org/html/rfc6901#section-4
        # First transform any occurrence of the sequence '~1' to '/'
        json_path_element = json_path_element.replace("~1", "/")
        # Then transforming any occurrence of the sequence '~0' to '~'.
        json_path_element = json_path_element.replace("~0", "~")
        return json_path_element
