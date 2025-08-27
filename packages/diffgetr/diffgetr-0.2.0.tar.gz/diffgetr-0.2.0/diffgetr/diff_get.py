import deepdiff
import sys
import json
import io
import re
import argparse
from pprint import pprint


class Diffr:

    def __init__(
        self, s0, s1, loc=None, path=None, deep_diff_kw=None, ignore_added=False
    ):

        #TODO: fail here for type differences
        st0 = type(s0)
        st1 = type(s1)
        if st0 != st1:
            preview_0 = str(s0)[:100]
            preview_1 = str(s1)[:100]            
            raise Exception(f'{loc}.{path}| types different: {st0} vs {st1} |0: {preview_0} | 1:{preview_1}')
        elif st0 in (str,int,float):
            preview_0 = str(s0)[:100]
            preview_1 = str(s1)[:100]            
            if s0 != s1:
                raise Exception(f'{loc}.{path}| values different: {preview_0} vs {preview_1}')
        elif isinstance(s0, (tuple, list)) and isinstance(s1, (tuple, list)):
            print(f"converting lists -> dict")
            s0 = {i: v for i, v in enumerate(s0)}
            s1 = {i: v for i, v in enumerate(s1)}
        self.s0 = s0
        self.s1 = s1
        self.ignore_added = ignore_added
        if deep_diff_kw is None:
            self.deep_diff_kw = dict(
                ignore_numeric_type_changes=True, significant_digits=3
            )
        else:
            self.deep_diff_kw = deep_diff_kw

        if loc is None:
            self.loc = []
        else:
            self.loc = loc
        if path is not None:
            self.loc.append(path)
        else:
            self.loc = ["root"]

    def __getitem__(self, key):
        if key in self.s0 and key in self.s1:
            return Diffr(
                self.s0[key],
                self.s1[key],
                path=key,
                loc=self.loc.copy(),
                ignore_added=self.ignore_added,
                deep_diff_kw=self.deep_diff_kw,
            )
        else:
            # self.diff_data(sys.stdout,bytes=False)
            self.diff_summary()
            raise KeyError(f"{self.location} | key missing: {key}")

    @property
    def path(self):
        return '.'.join(self.loc)

    def keys(self):
        s0k = set(self.s0)
        s1k = set(self.s1)
        sa = set.intersection(s0k, s1k)
        return sa
    
    def dict_keys(self)->set:
        return set(( k for k in self.keys() \
                if isinstance(self.s0[k],dict) \
                and isinstance(self.s1[k],dict)
                ))

    def path_diffs(self,syskey:str) -> "Diffr":
        """take sys key like  root.p1.p2.pk[0].*.po[*].val and generate diffs through each matching key. If there is a key prefix'd with path, such as root.p1.p2 be sure to strip that so you can navigate the data.
        """
        if '.' not in syskey and '[' not in syskey:
            #you're here
            #print(f'returning {self.loc}')
            if syskey in self.dict_keys():
                yield self[syskey]
            else:
                yield self
        else:
            #recursive
            pre_path = '.'.join(self.loc)
            
            find = syskey
            if pre_path in syskey:
                #print(f'replacing: {pre_path} in {syskey}')
                find = syskey.replace(pre_path,"")
            
            pths = find.split('.')
            for i,key_seg in enumerate(pths):
                nx = pths[i+1:]
                nxt = '.'.join(nx)
                if not key_seg or key_seg == '.':
                    continue
                elif nx:
                    #print(f'getting {key_seg} -> {nxt}')

                    if '*' == key_seg:
                        for ky in self.dict_keys():
                            for val in self[ky].path_diffs(nxt):
                                yield val

                    elif '[*]' in key_seg:
                        array1 = self.s0[key_seg]
                        array2 = self.s1[key_seg]
                        for j in range(min(len(array1),len(array2))):
                            v1 = array1[j]
                            v2 = array2[j]
                            for val in Diffrr(v1,v2).path_diffs(nxt):
                                yield val

                    elif key_seg in self.dict_keys():
                        for val in self[key_seg].path_diffs(nxt):
                            yield val
                        


    def __iter__(self):
        return self.keys()

    def _ipython_key_completions_(self):
        """
        Returns the keys that IPython should suggest for tab completion
        when accessing items using obj[key].
        """
        return list(self.keys())

    # def __dir__(self):
    #     ol = super().__dir__()
    #     out = list(self.keys())
    #     out.extend(ol)
    #     return out

    @property
    def location(self):
        return ".".join(self.loc)

    def __repr__(self):
        return f"diff[{self.location}]"

    def __str__(self):
        fil = io.BytesIO()
        out = self.diff_summary(fil, top=10)
        fil.seek(0)
        buff = fil.getvalue().decode("utf-8")
        return buff

    def print_here(self):
        d0 = {
            k: (
                "{...}"
                if isinstance(v, dict)
                else v if not isinstance(v, (list, tuple)) else "[...]"
            )
            for k, v in self.s0.items()
        }
        d1 = {
            k: (
                "{...}"
                if isinstance(v, dict)
                else v if not isinstance(v, (list, tuple)) else "[...]"
            )
            for k, v in self.s1.items()
        }

        pprint(d0, indent=2)
        pprint(d1, indent=2)

    def print_below(self):
        print(f'## BASE')
        pprint(self.s0, indent=2)
        print(f'\n## TEST')
        pprint(self.s1, indent=2)        

    @property
    def diff_obj(self) -> deepdiff.DeepDiff:
        df = deepdiff.DeepDiff(self.s0, self.s1, **self.deep_diff_kw)
        if self.ignore_added:
            for k in list(df):
                if "added" in k:
                    df.pop(k)
        return df

    def diff_all(self, indent=2, file=None):
        df = self.diff_obj

        if file is None:
            file = sys.stdout
            bytes = False
        else:
            # Determine if file expects bytes or text
            bytes = hasattr(file, 'mode') and 'b' in file.mode

        title = f"{self.location} diffing data\n\n"
        file.write(title.encode("utf-8") if bytes else title)
        for k, dc in df.items():
            if dc:
                tit = f"\nDIFF CATEGORY: {k.upper()}\n"
                file.write(tit.encode("utf-8") if bytes else tit)
                pprint(dc, stream=file, indent=indent)

    def diff_sidebyside(self):
        # 1. Convert each dictionary to global key format (key1.key2[i].key3 = value)
        def flatten(d, parent_key="root", sep=".", out=None):
            if out is None:
                out = {}
            if isinstance(d, dict):
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}"
                    flatten(v, new_key, sep, out)
            elif isinstance(d, list):
                for i, v in enumerate(d):
                    new_key = f"{parent_key}[{i}]"
                    flatten(v, new_key, sep, out)
            else:
                out[parent_key] = d
            return out

        flat0 = flatten(self.s0)
        flat1 = flatten(self.s1)

        # 2. Record the missing global keys in each set
        keys0 = set(flat0.keys())
        keys1 = set(flat1.keys())
        only0 = keys0 - keys1
        only1 = keys1 - keys0
        both = keys0 & keys1

        # 3. Sort the differences by common parent key by amount and number of differences
        def parent_key(key):
            # Remove last .segment or [i]
            if "[" in key and key.endswith("]"):
                return key[: key.rfind("[")]
            if "." in key:
                return key[: key.rfind(".")]
            return key

        diff_keys = list({k for k in both if flat0[k] != flat1[k]})
        parent_counts = {}
        for k in diff_keys:
            p = parent_key(k)
            parent_counts[p] = parent_counts.get(p, 0) + 1

        sorted_parents = sorted(parent_counts.items(), key=lambda x: -x[1])

        # Group missing keys by parent
        if only0:
            missing_by_parent = {}
            for key in only0:
                p = parent_key(key)
                if p not in missing_by_parent:
                    missing_by_parent[p] = []
                missing_by_parent[p].append(key)

            print("MISSING KEYS:")
            for p, keys in sorted(missing_by_parent.items(), key=lambda x: -len(x[1])):
                key_suffixes = [k.replace(p, "").lstrip(".") for k in keys]
                print(f'-{p:<100}:\n\t[{", ".join(key_suffixes)}]')

        # Group added keys by parent
        if not self.ignore_added and only1:
            added_by_parent = {}
            for key in only1:
                p = parent_key(key)
                if p not in added_by_parent:
                    added_by_parent[p] = []
                added_by_parent[p].append(key)

            print("ADDED KEYS:")
            for p, keys in sorted(added_by_parent.items(), key=lambda x: -len(x[1])):
                key_suffixes = [k.replace(p, "").lstrip(".") for k in keys]
                print(f'-{p:<100}:\n\t[{", ".join(key_suffixes)}]')

        # 4. Loop through the groups of parent keys and print the differences side by side
        print(f"{'KEY':<50} | {'s0':^30} | {'s1':^30} | {'DIFF':>10} | {'% DIFF':>10}")
        print("-" * 145)
        threshold = 1.0 / (10 ** self.deep_diff_kw.get("significant_digits", 3))
        for p, _ in sorted_parents:
            group = [k for k in diff_keys if parent_key(k) == p]
            if not group:
                continue
            group_print = False
            for k in sorted(group):
                if not self.ignore_added and k not in flat0:
                    continue
                v0 = flat0.get(k, "<MISSING>")
                v1 = flat1.get(k, "<MISSING>")
                key = k.replace(p, "")
                if key.startswith("."):
                    key = key[1:]
                pct = None
                v0_num = None
                v1_num = None
                # Try to convert to float if possible
                try:
                    v0_num = float(v0)
                except (ValueError, TypeError):
                    pass
                try:
                    v1_num = float(v1)
                except (ValueError, TypeError):
                    pass
                diff = "-"
                if v0_num is not None and v1_num is not None:
                    try:
                        if v0_num == 0 and v1_num == 0:
                            pct = 0.0
                        elif v0_num == 0:
                            pct = float("inf")
                            diff = pct
                        else:
                            diff = v1_num - v0_num
                            pct = abs(diff / v0_num)
                        pct_diff = f"{pct:10.3%}"
                    except Exception:
                        pass
                v0s = (
                    json.dumps(v0, ensure_ascii=False)
                    if not isinstance(v0, str)
                    else v0
                )
                v1s = (
                    json.dumps(v1, ensure_ascii=False)
                    if not isinstance(v1, str)
                    else v1
                )
                if pct is not None and abs(pct) > threshold:
                    if group_print is False:
                        print(f"\nGROUP: {self.path}.{p}")
                        group_print = True
                    print(
                        f" >{key:<50} | {v0s:^30} | {v1s:^30} | {diff:>14.4f} |{pct_diff:>10}"
                    )
                elif pct is None and v0 != v1:
                    if group_print is False:
                        print(f"\nGROUP: {self.path}.{p}")
                        group_print = True
                    print(
                        f" >{key:<50} | {v0s:^30} | {v1s:^30} | {'-':^14} | {'-':^10}"
                    )

    def diff_summary(self, file=None, top=50, bytes=None):

        if file is None:
            file = sys.stdout
            bytes = False
        elif bytes is None:
            if hasattr(file, "mode"):
                bytes = "b" in file.mode
            else:
                # Fallback: check if file expects bytes by writing a test string
                try:
                    file.write(b"")  # Try writing empty bytes
                    bytes = True
                except TypeError:
                    bytes = False

        df = self.diff_obj

        title = f"{self.location} diffing summary\n\n"
        file.write(title.encode("utf-8") if bytes else title)
        uuid_word = re.compile(
            "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        )
        comp = "[0-9\.]*(,[0-9\.]+)+"
        csv_word = re.compile(comp)
        key_counts = {}
        all_sys_keys = set()
        sys_keys = {}
        for gk, cats in df.items():
            if isinstance(cats, dict):
                cats = list(cats.keys())
            sys_kf = [
                re.sub(csv_word, "<CSV>", re.sub(uuid_word, "<UUID>", v)) for v in cats
            ]
            sys_refs = [
                tuple(c.replace("']", "").replace("root.", "").split("['"))
                for c in sys_kf
            ]
            kc = key_counts.get(gk, {})
            for grps in sys_refs:
                L = len(grps)
                for i in range(L - 1):
                    wrds = tuple(grps[: L + 1 - i])
                    all_sys_keys.add(wrds)
                    seg_key = ".".join(wrds)
                    kc[seg_key] = kc.get(seg_key, 0) + 1

            key_counts[gk] = kc

        for k, v in key_counts.items():
            v = sorted(v.items(), key=lambda kv: kv[-1])
            tc = sum([vi[-1] for vi in v])
            t = f"{k.upper():<100}|{tc}\n"
            file.write(t.encode("utf-8") if bytes else t)
            for key, num in v[-top:]:
                f = f"{key:<100}|{num}\n"
                file.write(f.encode("utf-8") if bytes else f)
            file.write(("\n" * 2).encode("utf-8") if bytes else "\n" * 2)


def main():
    parser = argparse.ArgumentParser(
        description="Diff two JSON files and navigate to a specific path."
    )
    parser.add_argument("file1", help="First JSON file")
    parser.add_argument("file2", help="Second JSON file")
    parser.add_argument(
        "path", help="Dot-separated path to navigate in the JSON structure"
    )

    args = parser.parse_args()

    with open(args.file1, "r", encoding="utf-8") as f:
        s0 = json.load(f)
    with open(args.file2, "r", encoding="utf-8") as f:
        s1 = json.load(f)

    DIFF = Diffr(s0, s1)
    keys = args.path.split(".")
    try:
        for key in keys:
            if key.endswith("]") and "[" in key:
                base, idx = key.rsplit("[", 1)
                idx = int(idx[:-1])
                DIFF = DIFF[base]
                loc = DIFF.loc.copy()
                loc.append(f"[{idx}]")
                DIFF = Diffr(DIFF.s0[idx], DIFF.s1[idx], loc=loc)
                continue
            else:
                DIFF = DIFF[key]

        print(DIFF)

    except KeyError:
        # diff_data already prints to stdout in __getitem__ on KeyError
        pass

if __name__ == "__main__":
    main()
