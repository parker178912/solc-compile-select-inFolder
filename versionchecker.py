import re
from solc_select.solc_select import get_available_versions

pragma = r"pragma solidity(?P<first>\s*(?P<first_comp>[>^=<]*)[\s\"\']*(?P<first_1>\d+)\s*\.\s*(?P<first_2>\d+)\s*\.*\s*(?P<first_3>\d+)*[\s\"\']*)(?P<second>(?P<second_comp>[>^=<]*)[\s\"\']*(?P<second_1>\d+)\s*\.\s*(?P<second_2>\d+)\s*\.*\s*(?P<second_3>\d+)*[\s\"]*)*;"


class VersionChecker:
    def __init__(self, solc_file: str) -> None:
        self.sol_file: str = solc_file  # .sol file.
        self.available_versions = []  # All available versions.
        self.lowest_version = []  # Lowest version.
        self.latest_version = []  # Latest version.
        self.pragma: str = None  # Solidity programa in file.
        self.version_list = list(get_available_versions().keys())[::-1]  # Get all version lists

    def resolve_pragma(self) -> None:
        """
        Get pragma from solidity code and put into self.pragme
        """
        with open(self.sol_file, "r") as f:
            context = f.readlines()
        for line in context:
            if re.match(pragma, line) != None:
                user_version = line
                break
        self.pragma = re.match(pragma, user_version).group()
        res = re.match(pragma, user_version).groups()
        if res[1] == None or res[2] == None or res[3] == None or res[4] == None:
            print(f"{user_version} is not a valid version number.")
            return
        self.version1 = ".".join([res[2], res[3], res[4]])
        self.operator1 = res[1]
        if res[6] != None and res[7] != None and res[8] != None and res[9] != None:
            self.version2 = ".".join([res[7], res[8], res[9]])
            self.operator2 = res[6]
            self.pragma = self.operator1 + self.version1 + " " + self.operator2 + self.version2
        else:
            self.pragma = self.operator1 + self.version1

    def get_all_version_data(self) -> None:
        """
        Get self.available_list, self.lowest_version and self.latest_version
        """
        if len(self.pragma) > 10:
            major1, minor1, patch1 = [int(part) for part in self.version1.split(".")]
            major2, minor2, patch2 = [int(part) for part in self.version2.split(".")]
            if major1 != major2 or (major1 == major2 and minor1 != minor2):
                if self.operator1 == ">" or self.operator1 == ">=":
                    available_list = self.available_list(self.version1, self.operator1)
                elif self.operator2 == ">" or self.operator2 == ">=":
                    available_list = self.available_list(self.version2, self.operator2)
            else:
                available_list1 = self.available_list(self.version1, self.operator1)
                available_list2 = self.available_list(self.version2, self.operator2)
                available_list = list(set(available_list1) & set(available_list2))
        else:
            available_list = self.available_list(self.version1, self.operator1)
        if len(available_list) != 0:
            patches = []
            for versions in available_list:
                major, minor, patch = [int(part) for part in versions.split(".")]
                patches.append(patch)
                patches = sorted(patches)
            self.available_versions = [
                str(major) + "." + str(minor) + "." + str(i) for i in patches
            ]
            self.lowest_version = self.available_versions[0]
            self.latest_version = self.available_versions[-1]

    def available_list(self, version: str, operator: str) -> list[str]:
        """
        Find available list by compare version function.

        ### Args :
            version : the version you want to compare.
            operator : the operator when compare.

        ### Returns :
            available_list : the list that satisfied operator and version.
        """
        available_list = []
        for list_version in self.version_list:
            if operator == ">":
                if self.compare_version(version, list_version) == "bigger":
                    available_list.append(list_version)
            elif operator == "<":
                if self.compare_version(version, list_version) == "smaller":
                    available_list.append(list_version)
            elif operator == ">=":
                if (
                    self.compare_version(version, list_version) == "bigger"
                    or self.compare_version(version, list_version) == "equal"
                ):
                    available_list.append(list_version)
            elif operator == "<=":
                if (
                    self.compare_version(version, list_version) == "smaller"
                    or self.compare_version(version, list_version) == "equal"
                ):
                    available_list.append(list_version)
            elif operator == "^":
                if self.compare_version(version, list_version) == "equal":
                    available_list.append(list_version)
        return available_list

    def compare_version(self, user_version: str, list_version: str) -> str:
        """
        Compare version in same major and minor.

        ### Args :
            user_version : the version user used.
            list_version : the version you want to compare with.

        ### Returns :
            compare : the compare result (bigger, smaller or equal).
        """
        user_major, user_minor, user_patch = [int(part) for part in user_version.split(".")]
        list_major, list_minor, list_patch = [int(part) for part in list_version.split(".")]
        if user_major == list_major and user_minor == list_minor:
            if list_patch > user_patch:
                compare = "bigger"
            elif list_patch < user_patch:
                compare = "smaller"
            else:
                compare = "equal"
        else:
            compare = ""
        return compare
