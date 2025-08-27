from datetime import datetime, timedelta
from graphlib import TopologicalSorter
import os
from pathlib import Path
from functools import cmp_to_key
import shutil
import math
import tarfile
import re
import urllib.request
import zipfile
import json
import configparser
import tempfile
import uuid
import yaml
import requests
from packaging import version
import xmlschema
from OpenSSL import crypto
from lxml import etree
from .GeneralUtilities import GeneralUtilities
from .ScriptCollectionCore import ScriptCollectionCore
from .SCLog import SCLog, LogLevel
from .ProgramRunnerEpew import ProgramRunnerEpew
from .ImageUpdater import ImageUpdater, VersionEcholon


class CreateReleaseConfiguration():
    projectname: str
    remotename: str
    artifacts_folder: str
    push_artifacts_scripts_folder: str
    verbosity: int
    reference_repository_remote_name: str = None
    reference_repository_branch_name: str = "main"
    build_repository_branch: str = "main"
    public_repository_url: str
    additional_arguments_file: str = None
    repository_folder_name: str = None
    repository_folder: str = None
    __sc: ScriptCollectionCore = None

    def __init__(self, projectname: str, remotename: str, build_artifacts_target_folder: str, push_artifacts_scripts_folder: str, verbosity: int, repository_folder: str, additional_arguments_file: str, repository_folder_name: str):
        self.__sc = ScriptCollectionCore()
        self.projectname = projectname
        self.remotename = remotename
        self.artifacts_folder = build_artifacts_target_folder
        self.push_artifacts_scripts_folder = push_artifacts_scripts_folder
        self.verbosity = verbosity
        if self.remotename is None:
            self.public_repository_url = None
        else:
            self.public_repository_url = self.__sc.git_get_remote_url(repository_folder, remotename)
        self.reference_repository_remote_name = self.remotename
        self.additional_arguments_file = additional_arguments_file
        self.repository_folder = repository_folder
        self.repository_folder_name = repository_folder_name


class CreateReleaseInformationForProjectInCommonProjectFormat:
    projectname: str
    repository: str
    artifacts_folder: str
    verbosity: int = 1
    reference_repository: str = None
    public_repository_url: str = None
    target_branch_name: str = None
    push_artifacts_scripts_folder: str = None
    target_environmenttype_for_qualitycheck: str = "QualityCheck"
    target_environmenttype_for_productive: str = "Productive"
    additional_arguments_file: str = None
    export_target: str = None

    def __init__(self, repository: str, artifacts_folder: str, projectname: str, public_repository_url: str, target_branch_name: str, additional_arguments_file: str, export_target: str, push_artifacts_scripts_folder: str):
        self.repository = repository
        self.public_repository_url = public_repository_url
        self.target_branch_name = target_branch_name
        self.artifacts_folder = artifacts_folder
        self.additional_arguments_file = additional_arguments_file
        self.export_target = export_target
        self.push_artifacts_scripts_folder = push_artifacts_scripts_folder
        if projectname is None:
            projectname = os.path.basename(self.repository)
        else:
            self.projectname = projectname
        self.reference_repository = f"{repository}Reference"


class MergeToStableBranchInformationForProjectInCommonProjectFormat:
    repository: str
    sourcebranch: str = "main"
    targetbranch: str = "stable"
    sign_git_tags: bool = True
    target_environmenttype_for_qualitycheck: str = "QualityCheck"
    target_environmenttype_for_productive: str = "Productive"
    additional_arguments_file: str = None
    export_target: str = None

    push_source_branch: bool = False
    push_source_branch_remote_name: str = None
    push_target_branch: bool = False
    push_target_branch_remote_name: str = None

    verbosity: int = 1

    def __init__(self, repository: str, additional_arguments_file: str, export_target: str):
        self.repository = repository
        self.additional_arguments_file = additional_arguments_file
        self.export_target = export_target


class TasksForCommonProjectStructure:
    __sc: ScriptCollectionCore = None
    reference_latest_version_of_xsd_when_generating_xml: bool = True
    validate_developers_of_repository: bool = True
    dotnet_runsettings_file = "runsettings.xml"

    def __init__(self, sc: ScriptCollectionCore = None):
        if sc is None:
            log: SCLog = SCLog()
            log.loglevel = LogLevel.Information
            sc = ScriptCollectionCore()
            sc.log = log
        self.__sc = sc

    @GeneralUtilities.check_arguments
    def is_codeunit_folder(self, codeunit_folder: str) -> bool:
        repo_folder = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        if not self.__sc.is_git_repository(repo_folder):
            return False
        codeunit_name = os.path.basename(codeunit_folder)
        codeunit_file: str = os.path.join(codeunit_folder, f"{codeunit_name}.codeunit.xml")
        if not os.path.isfile(codeunit_file):
            return False
        return True

    @GeneralUtilities.check_arguments
    def assert_is_codeunit_folder(self, codeunit_folder: str) -> str:
        repo_folder = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        if not self.__sc.is_git_repository(repo_folder):
            raise ValueError(f"'{codeunit_folder}' can not be a valid codeunit-folder because '{repo_folder}' is not a git-repository.")
        codeunit_name = os.path.basename(codeunit_folder)
        codeunit_file: str = os.path.join(codeunit_folder, f"{codeunit_name}.codeunit.xml")
        if not os.path.isfile(codeunit_file):
            raise ValueError(f"'{codeunit_folder}' is no codeunit-folder because '{codeunit_file}' does not exist.")

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_development_environment_name() -> str:
        return "Development"

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_qualitycheck_environment_name() -> str:
        return "QualityCheck"

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_productive_environment_name() -> str:
        return "Productive"

    @GeneralUtilities.check_arguments
    def get_build_folder(self, repository_folder: str, codeunit_name: str) -> str:
        self.__sc.assert_is_git_repository(repository_folder)
        return os.path.join(repository_folder, codeunit_name, "Other", "Build")

    @GeneralUtilities.check_arguments
    def get_artifacts_folder(self, repository_folder: str, codeunit_name: str) -> str:
        self.__sc.assert_is_git_repository(repository_folder)
        return os.path.join(repository_folder, codeunit_name, "Other", "Artifacts")

    @GeneralUtilities.check_arguments
    def get_wheel_file(self, repository_folder: str, codeunit_name: str) -> str:
        self.__sc.assert_is_git_repository(repository_folder)
        return self.__sc.find_file_by_extension(os.path.join(self.get_artifacts_folder(repository_folder, codeunit_name), "BuildResult_Wheel"), "whl")

    @GeneralUtilities.check_arguments
    def get_testcoverage_threshold_from_codeunit_file(self, codeunit_file: str):
        root: etree._ElementTree = etree.parse(codeunit_file)
        return float(str(root.xpath('//cps:properties/cps:testsettings/@minimalcodecoverageinpercent', namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'})[0]))

    @GeneralUtilities.check_arguments
    def codeunit_has_testable_sourcecode(self, codeunit_file: str) -> bool:
        root: etree._ElementTree = etree.parse(codeunit_file)
        return GeneralUtilities.string_to_boolean(str(root.xpath('//cps:properties/@codeunithastestablesourcecode', namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'})[0]))

    @GeneralUtilities.check_arguments
    def codeunit_throws_exception_if_codeunitfile_is_not_validatable(self, codeunit_file: str) -> bool:
        root: etree._ElementTree = etree.parse(codeunit_file)
        return GeneralUtilities.string_to_boolean(str(root.xpath('//cps:properties/@throwexceptionifcodeunitfilecannotbevalidated', namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'})[0]))

    @GeneralUtilities.check_arguments
    def codeunit_has_updatable_dependencies(self, codeunit_file: str) -> bool:
        root: etree._ElementTree = etree.parse(codeunit_file)
        return GeneralUtilities.string_to_boolean(str(root.xpath('//cps:properties/@codeunithasupdatabledependencies', namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'})[0]))

    @GeneralUtilities.check_arguments
    def get_codeunit_description(self, codeunit_file: str) -> bool:
        root: etree._ElementTree = etree.parse(codeunit_file)
        return str(root.xpath('//cps:properties/@description', namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'})[0])

    @GeneralUtilities.check_arguments
    def check_testcoverage(self, testcoverage_file_in_cobertura_format: str, repository_folder: str, codeunitname: str) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        GeneralUtilities.write_message_to_stdout("Check testcoverage..")
        root: etree._ElementTree = etree.parse(testcoverage_file_in_cobertura_format)
        if len(root.xpath('//coverage/packages/package')) != 1:
            raise ValueError(f"'{testcoverage_file_in_cobertura_format}' must contain exactly 1 package.")
        if root.xpath('//coverage/packages/package[1]/@name')[0] != codeunitname:
            raise ValueError(f"The package name of the tested package in '{testcoverage_file_in_cobertura_format}' must be '{codeunitname}'.")
        coverage_in_percent = round(float(str(root.xpath('//coverage/packages/package[1]/@line-rate')[0]))*100, 2)
        technicalminimalrequiredtestcoverageinpercent = 0
        if not technicalminimalrequiredtestcoverageinpercent < coverage_in_percent:
            raise ValueError(f"The test-coverage of package '{codeunitname}' must be greater than {technicalminimalrequiredtestcoverageinpercent}%.")
        codeunit_file = os.path.join(repository_folder, codeunitname, f"{codeunitname}.codeunit.xml")
        minimalrequiredtestcoverageinpercent = self.get_testcoverage_threshold_from_codeunit_file(codeunit_file)
        if (coverage_in_percent < minimalrequiredtestcoverageinpercent):
            raise ValueError(f"The testcoverage for codeunit {codeunitname} must be {minimalrequiredtestcoverageinpercent}% or more but is {coverage_in_percent}%.")

    @GeneralUtilities.check_arguments
    def replace_version_in_python_file(self, file: str, new_version_value: str) -> None:
        GeneralUtilities.write_text_to_file(file, re.sub("version = \"\\d+\\.\\d+\\.\\d+\"", f"version = \"{new_version_value}\"", GeneralUtilities.read_text_from_file(file)))

    @GeneralUtilities.check_arguments
    def standardized_tasks_run_testcases_for_python_codeunit(self, run_testcases_file: str, generate_badges: bool, verbosity: int, targetenvironmenttype: str, commandline_arguments: list[str]) -> None:
        codeunitname: str = Path(os.path.dirname(run_testcases_file)).parent.parent.name
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        repository_folder: str = str(Path(os.path.dirname(run_testcases_file)).parent.parent.parent.absolute())
        codeunit_folder = os.path.join(repository_folder, codeunitname)
        self.__sc.run_program("coverage", f"run -m pytest -s ./{codeunitname}Tests", codeunit_folder,  verbosity=verbosity)
        self.__sc.run_program("coverage", "xml", codeunit_folder, verbosity=verbosity)
        coveragefolder = os.path.join(repository_folder, codeunitname, "Other/Artifacts/TestCoverage")
        GeneralUtilities.ensure_directory_exists(coveragefolder)
        coveragefile = os.path.join(coveragefolder, "TestCoverage.xml")
        GeneralUtilities.ensure_file_does_not_exist(coveragefile)
        os.rename(os.path.join(repository_folder, codeunitname, "coverage.xml"), coveragefile)
        self.run_testcases_common_post_task(repository_folder, codeunitname, verbosity, generate_badges, targetenvironmenttype, commandline_arguments)

    @GeneralUtilities.check_arguments
    def copy_source_files_to_output_directory(self, buildscript_file: str) -> None:
        GeneralUtilities.write_message_to_stdout("Copy sourcecode...")
        folder = os.path.dirname(os.path.realpath(buildscript_file))
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", folder)
        result = self.__sc.run_program_argsasarray("git", ["ls-tree", "-r", "HEAD", "--name-only"], codeunit_folder)
        files = [f for f in result[1].split('\n') if len(f) > 0]
        for file in files:
            full_source_file = os.path.join(codeunit_folder, file)
            if os.path.isfile(full_source_file):
                # Reson of isdir-check:
                # Prevent trying to copy files which are not exist.
                # Otherwise exceptions occurr because uncommitted deletions of files will result in an error here.
                target_file = os.path.join(codeunit_folder, "Other", "Artifacts", "SourceCode", file)
                target_folder = os.path.dirname(target_file)
                GeneralUtilities.ensure_directory_exists(target_folder)
                shutil.copyfile(full_source_file, target_file)

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_dart_project_in_common_project_structure(self, build_script_file: str, verbosity: int, targets: list[str], args: list[str], package_name: str):
        codeunit_folder = GeneralUtilities.resolve_relative_path("../../..", build_script_file)
        codeunit_name = os.path.basename(codeunit_folder)
        src_folder = GeneralUtilities.resolve_relative_path(package_name, codeunit_folder)  # TODO replace packagename
        artifacts_folder = os.path.join(codeunit_folder, "Other", "Artifacts")
        verbosity = self.get_verbosity_from_commandline_arguments(args, verbosity)
        target_names: dict[str, str] = {
            "web": "WebApplication",
            "windows": "Windows",
            "ios": "IOS",
            "appbundle": "Android",
        }
        for target in targets:
            GeneralUtilities.write_message_to_stdout(f"Build package {package_name} for target {target_names[target]}...")
            self.run_with_epew("flutter", f"build {target}", src_folder, verbosity)
            if target == "web":
                web_relase_folder = os.path.join(src_folder, "build/web")
                web_folder = os.path.join(artifacts_folder, "BuildResult_WebApplication")
                GeneralUtilities.ensure_directory_does_not_exist(web_folder)
                GeneralUtilities.ensure_directory_exists(web_folder)
                GeneralUtilities.copy_content_of_folder(web_relase_folder, web_folder)
            elif target == "windows":
                windows_release_folder = os.path.join(src_folder, "build/windows/x64/runner/Release")
                windows_folder = os.path.join(artifacts_folder, "BuildResult_Windows")
                GeneralUtilities.ensure_directory_does_not_exist(windows_folder)
                GeneralUtilities.ensure_directory_exists(windows_folder)
                GeneralUtilities.copy_content_of_folder(windows_release_folder, windows_folder)
            elif target == "ios":
                raise ValueError("building for ios is not implemented yet")
            elif target == "appbundle":
                aab_folder = os.path.join(artifacts_folder, "BuildResult_AAB")
                GeneralUtilities.ensure_directory_does_not_exist(aab_folder)
                GeneralUtilities.ensure_directory_exists(aab_folder)
                aab_relase_folder = os.path.join(src_folder, "build/app/outputs/bundle/release")
                aab_file_original = self.__sc.find_file_by_extension(aab_relase_folder, "aab")
                aab_file = os.path.join(aab_folder, f"{codeunit_name}.aab")
                shutil.copyfile(aab_file_original, aab_file)
                bundletool = os.path.join(codeunit_folder, "Other/Resources/AndroidAppBundleTool/bundletool.jar")
                apk_folder = os.path.join(artifacts_folder, "BuildResult_APK")
                GeneralUtilities.ensure_directory_does_not_exist(apk_folder)
                GeneralUtilities.ensure_directory_exists(apk_folder)
                apks_file = f"{apk_folder}/{codeunit_name}.apks"
                self.__sc.run_program("java", f"-jar {bundletool} build-apks --bundle={aab_file} --output={apks_file} --mode=universal", aab_relase_folder, verbosity)
                with zipfile.ZipFile(apks_file, "r") as zip_ref:
                    zip_ref.extract("universal.apk", apk_folder)
                GeneralUtilities.ensure_file_does_not_exist(apks_file)
                os.rename(f"{apk_folder}/universal.apk", f"{apk_folder}/{codeunit_name}.apk")
            else:
                raise ValueError(f"Not supported target: {target}")
        self.copy_source_files_to_output_directory(build_script_file)

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_python_codeunit(self, buildscript_file: str, verbosity: int, targetenvironmenttype: str, commandline_arguments: list[str]) -> None:
        codeunitname: str = Path(os.path.dirname(buildscript_file)).parent.parent.name
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        codeunit_folder = str(Path(os.path.dirname(buildscript_file)).parent.parent.absolute())
        repository_folder: str = str(Path(os.path.dirname(buildscript_file)).parent.parent.parent.absolute())
        target_directory = GeneralUtilities.resolve_relative_path("../Artifacts/BuildResult_Wheel", os.path.join(self.get_artifacts_folder(repository_folder, codeunitname)))
        GeneralUtilities.ensure_directory_exists(target_directory)
        self.__sc.run_program("python", f"-m build --wheel --outdir {target_directory}", codeunit_folder, verbosity=verbosity)
        self.generate_bom_for_python_project(verbosity, codeunit_folder, codeunitname, commandline_arguments)
        self.copy_source_files_to_output_directory(buildscript_file)

    @GeneralUtilities.check_arguments
    def generate_bom_for_python_project(self, verbosity: int, codeunit_folder: str, codeunitname: str, commandline_arguments: list[str]) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        repository_folder = os.path.dirname(codeunit_folder)
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        codeunitversion = self.get_version_of_codeunit_folder(codeunit_folder)
        bom_folder = "Other/Artifacts/BOM"
        bom_folder_full = os.path.join(codeunit_folder, bom_folder)
        GeneralUtilities.ensure_directory_exists(bom_folder_full)
        if not os.path.isfile(os.path.join(codeunit_folder, "requirements.txt")):
            raise ValueError(f"Codeunit {codeunitname} does not have a 'requirements.txt'-file.")
        # TODO check that all values from setup.cfg are contained in requirements.txt
        result = self.__sc.run_program("cyclonedx-py", "requirements", codeunit_folder, verbosity=verbosity)
        bom_file_relative_json = f"{bom_folder}/{codeunitname}.{codeunitversion}.bom.json"
        bom_file_relative_xml = f"{bom_folder}/{codeunitname}.{codeunitversion}.bom.xml"
        bom_file_json = os.path.join(codeunit_folder, bom_file_relative_json)
        bom_file_xml = os.path.join(codeunit_folder, bom_file_relative_xml)

        GeneralUtilities.ensure_file_exists(bom_file_json)
        GeneralUtilities.write_text_to_file(bom_file_json, result[1])
        self.ensure_cyclonedxcli_is_available(repository_folder)
        cyclonedx_exe = os.path.join(repository_folder, "Other/Resources/CycloneDXCLI/cyclonedx-cli")
        if GeneralUtilities.current_system_is_windows():
            cyclonedx_exe = cyclonedx_exe+".exe"
        self.__sc.run_program(cyclonedx_exe, f"convert --input-file ./{codeunitname}/{bom_file_relative_json} --input-format json --output-file ./{codeunitname}/{bom_file_relative_xml} --output-format xml", repository_folder)
        self.__sc.format_xml_file(bom_file_xml)
        GeneralUtilities.ensure_file_does_not_exist(bom_file_json)

    @GeneralUtilities.check_arguments
    def standardized_tasks_push_wheel_file_to_registry(self, wheel_file: str, api_key: str, repository: str, gpg_identity: str, verbosity: int) -> None:
        # repository-value when PyPi should be used: "pypi"
        # gpg_identity-value when wheel-file should not be signed: None
        folder = os.path.dirname(wheel_file)
        filename = os.path.basename(wheel_file)

        if gpg_identity is None:
            gpg_identity_argument = GeneralUtilities.empty_string
        else:
            gpg_identity_argument = GeneralUtilities.empty_string  # f" --sign --identity {gpg_identity}"
            # disabled due to https://blog.pypi.org/posts/2023-05-23-removing-pgp/

        if verbosity > 2:
            verbose_argument = " --verbose"
        else:
            verbose_argument = GeneralUtilities.empty_string

        twine_argument = f"upload{gpg_identity_argument} --repository {repository} --non-interactive {filename} --disable-progress-bar"
        twine_argument = f"{twine_argument} --username __token__ --password {api_key}{verbose_argument}"
        self.__sc.run_program("twine", twine_argument, folder, verbosity=verbosity, throw_exception_if_exitcode_is_not_zero=True)

    @GeneralUtilities.check_arguments
    def push_wheel_build_artifact(self, push_build_artifacts_file, product_name, codeunitname, repository: str, apikey: str, gpg_identity: str, verbosity: int, commandline_arguments: list[str], repository_folder_name: str) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        folder_of_this_file = os.path.dirname(push_build_artifacts_file)
        repository_folder = GeneralUtilities.resolve_relative_path(f"..{os.path.sep}../Submodules{os.path.sep}{repository_folder_name}", folder_of_this_file)
        wheel_file = self.get_wheel_file(repository_folder, codeunitname)
        self.standardized_tasks_push_wheel_file_to_registry(wheel_file, apikey, repository, gpg_identity, verbosity)

    @GeneralUtilities.check_arguments
    def get_version_of_codeunit_file_content(self, codeunit_file_content: str) -> str:
        root: etree._ElementTree = etree.fromstring(codeunit_file_content.encode("utf-8"))
        result = str(root.xpath('//cps:version/text()',  namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'})[0])
        return result

    @GeneralUtilities.check_arguments
    def get_version_of_codeunit(self, codeunit_file: str) -> None:
        return self.get_version_of_codeunit_file_content(GeneralUtilities.read_text_from_file(codeunit_file))

    @GeneralUtilities.check_arguments
    def get_version_of_codeunit_folder(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_file = os.path.join(codeunit_folder, f"{os.path.basename(codeunit_folder)}.codeunit.xml")
        return self.get_version_of_codeunit(codeunit_file)

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_string_value_from_commandline_arguments(commandline_arguments: list[str], property_name: str, default_value: str) -> str:
        result = TasksForCommonProjectStructure.get_property_from_commandline_arguments(commandline_arguments, property_name)
        if result is None:
            return default_value
        else:
            return result

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_is_pre_merge_value_from_commandline_arguments(commandline_arguments: list[str],  default_value: bool) -> bool:
        result = TasksForCommonProjectStructure.get_property_from_commandline_arguments(commandline_arguments, "is_pre_merge")
        if result is None:
            return default_value
        else:
            return GeneralUtilities.string_to_boolean(result)

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_assume_dependent_codeunits_are_already_built_from_commandline_arguments(commandline_arguments: list[str],  default_value: bool) -> bool:
        result = TasksForCommonProjectStructure.get_property_from_commandline_arguments(commandline_arguments, "assume_dependent_codeunits_are_already_built")
        if result is None:
            return default_value
        else:
            return GeneralUtilities.string_to_boolean(result)

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_verbosity_from_commandline_arguments(commandline_arguments: list[str],  default_value: int) -> int:
        result = TasksForCommonProjectStructure.get_property_from_commandline_arguments(commandline_arguments, "verbosity")
        if result is None:
            return default_value
        else:
            return int(result)

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_targetenvironmenttype_from_commandline_arguments(commandline_arguments: list[str],  default_value: str) -> str:
        result = TasksForCommonProjectStructure.get_property_from_commandline_arguments(commandline_arguments, "targetenvironmenttype")
        if result is None:
            return default_value
        else:
            return result

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_additionalargumentsfile_from_commandline_arguments(commandline_arguments: list[str],  default_value: str) -> str:
        result = TasksForCommonProjectStructure.get_property_from_commandline_arguments(commandline_arguments, "additionalargumentsfile")
        if result is None:
            return default_value
        else:
            return result

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_filestosign_from_commandline_arguments(commandline_arguments: list[str],  default_value: dict[str, str]) -> dict[str, str]:
        result_plain = TasksForCommonProjectStructure.get_property_from_commandline_arguments(commandline_arguments, "sign")
        if result_plain is None:
            return default_value
        else:
            result: dict[str, str] = dict[str, str]()
            files_tuples = GeneralUtilities.to_list(result_plain, ";")
            for files_tuple in files_tuples:
                splitted = files_tuple.split("=")
                result[splitted[0]] = splitted[1]
            return result

    @staticmethod
    @GeneralUtilities.check_arguments
    def get_property_from_commandline_arguments(commandline_arguments: list[str], property_name: str) -> str:
        result: str = None
        count = len(commandline_arguments)
        loop_index = -1
        for commandline_argument in commandline_arguments:
            loop_index = loop_index+1
            if loop_index < count-1:
                prefix = f"--overwrite_{property_name}"
                if commandline_argument == prefix:
                    result = commandline_arguments[loop_index+1]
                    return result
        return result

    @GeneralUtilities.check_arguments
    def update_version_of_codeunit(self, common_tasks_file: str, current_version: str) -> None:
        codeunit_name: str = os.path.basename(GeneralUtilities.resolve_relative_path("..", os.path.dirname(common_tasks_file)))
        codeunit_file: str = os.path.join(GeneralUtilities.resolve_relative_path("..", os.path.dirname(common_tasks_file)), f"{codeunit_name}.codeunit.xml")
        self.write_version_to_codeunit_file(codeunit_file, current_version)

    @GeneralUtilities.check_arguments
    def t4_transform(self, commontasks_script_file_of_current_file: str, verbosity: int, ignore_git_ignored_files: bool = True):
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", commontasks_script_file_of_current_file)
        self.__ensure_grylibrary_is_available(codeunit_folder)
        repository_folder: str = os.path.dirname(codeunit_folder)
        codeunitname: str = os.path.basename(codeunit_folder)
        codeunit_folder = os.path.join(repository_folder, codeunitname)
        for search_result in Path(codeunit_folder).glob('**/*.tt'):
            tt_file = str(search_result)
            relative_path_to_tt_file_from_repository = str(Path(tt_file).relative_to(repository_folder))
            if (not ignore_git_ignored_files) or (ignore_git_ignored_files and not self.__sc.file_is_git_ignored(relative_path_to_tt_file_from_repository, repository_folder)):
                relative_path_to_tt_file_from_codeunit_file = str(Path(tt_file).relative_to(codeunit_folder))
                argument = [f"--parameter=repositoryFolder={repository_folder}", f"--parameter=codeUnitName={codeunitname}", relative_path_to_tt_file_from_codeunit_file]
                self.__sc.run_program_argsasarray("t4", argument, codeunit_folder, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def get_resource_from_global_resource(self, codeunit_folder: str, resource_name: str):
        repository_folder: str = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        source_folder: str = os.path.join(repository_folder, "Other", "Resources", resource_name)
        target_folder: str = os.path.join(codeunit_folder, "Other", "Resources", resource_name)
        GeneralUtilities.ensure_folder_exists_and_is_empty(target_folder)
        GeneralUtilities.copy_content_of_folder(source_folder, target_folder)

    @GeneralUtilities.check_arguments
    def standardized_tasks_generate_reference_by_docfx(self, generate_reference_script_file: str, verbosity: int, targetenvironmenttype: str, commandline_arguments: list[str]) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        folder_of_current_file = os.path.dirname(generate_reference_script_file)
        generated_reference_folder = GeneralUtilities.resolve_relative_path("../Artifacts/Reference", folder_of_current_file)
        GeneralUtilities.ensure_directory_does_not_exist(generated_reference_folder)
        GeneralUtilities.ensure_directory_exists(generated_reference_folder)
        obj_folder = os.path.join(folder_of_current_file, "obj")
        GeneralUtilities.ensure_directory_does_not_exist(obj_folder)
        GeneralUtilities.ensure_directory_exists(obj_folder)
        self.__sc.run_program("docfx", "docfx.json", folder_of_current_file, verbosity=verbosity)
        # TODO generate also a darkmode-variant (darkFX for example, see https://dotnet.github.io/docfx/extensions/templates.html )
        GeneralUtilities.ensure_directory_does_not_exist(obj_folder)

    def standardized_task_verify_standard_format_csproj_files(self, codeunit_folder: str) -> bool:
        self.assert_is_codeunit_folder(codeunit_folder)
        repository_folder = os.path.dirname(codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        codeunit_folder = os.path.join(repository_folder, codeunit_name)
        codeunit_version = self.get_version_of_codeunit_folder(codeunit_folder)

        csproj_project_name = codeunit_name
        csproj_file = os.path.join(codeunit_folder, csproj_project_name, csproj_project_name+".csproj")
        result1: tuple[bool, str] = self.__standardized_task_verify_standard_format_for_project_csproj_file(csproj_file, codeunit_folder, codeunit_name, codeunit_version)
        if not result1[0]:
            raise ValueError(f"'{csproj_file}' with content '{GeneralUtilities.read_text_from_file(csproj_file)}' does not match the standardized .csproj-file-format which is defined by the regex '{result1[1]}'.")

        test_csproj_project_name = csproj_project_name+"Tests"
        test_csproj_file = os.path.join(codeunit_folder, test_csproj_project_name, test_csproj_project_name+".csproj")
        result2: tuple[bool, str] = self.__standardized_task_verify_standard_format_for_test_csproj_file(test_csproj_file, codeunit_name, codeunit_version)
        if not result2[0]:
            raise ValueError(f"'{test_csproj_file}' with content '{GeneralUtilities.read_text_from_file(test_csproj_file)}' does not match the standardized .csproj-file-format which is defined by the regex '{result2[1]}'.")

    def __standardized_task_verify_standard_format_for_project_csproj_file(self, csproj_file: str, codeunit_folder: str, codeunit_name: str, codeunit_version: str) -> tuple[bool, str]:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name_regex = re.escape(codeunit_name)
        codeunit_file = os.path.join(codeunit_folder, f"{codeunit_name}.codeunit.xml")
        codeunit_description = self.get_codeunit_description(codeunit_file)
        codeunit_version_regex = re.escape(codeunit_version)
        codeunit_description_regex = re.escape(codeunit_description)
        regex = f"""^<Project Sdk=\\"Microsoft\\.NET\\.Sdk\\">
    <PropertyGroup>
        <TargetFramework>([^<]+)<\\/TargetFramework>
        <Authors>([^<]+)<\\/Authors>
        <Version>{codeunit_version_regex}<\\/Version>
        <AssemblyVersion>{codeunit_version_regex}<\\/AssemblyVersion>
        <FileVersion>{codeunit_version_regex}<\\/FileVersion>
        <SelfContained>false<\\/SelfContained>
        <IsPackable>false<\\/IsPackable>
        <PreserveCompilationContext>false<\\/PreserveCompilationContext>
        <GenerateRuntimeConfigurationFiles>true<\\/GenerateRuntimeConfigurationFiles>
        <Copyright>([^<]+)<\\/Copyright>
        <Description>{codeunit_description_regex}<\\/Description>
        <PackageProjectUrl>https:\\/\\/([^<]+)<\\/PackageProjectUrl>
        <RepositoryUrl>https:\\/\\/([^<]+)\\.git<\\/RepositoryUrl>
        <RootNamespace>([^<]+)\\.Core<\\/RootNamespace>
        <ProduceReferenceAssembly>false<\\/ProduceReferenceAssembly>
        <Nullable>(disable|enable|warnings|annotations)<\\/Nullable>
        <Configurations>Development;QualityCheck;Productive<\\/Configurations>
        <IsTestProject>false<\\/IsTestProject>
        <LangVersion>([^<]+)<\\/LangVersion>
        <PackageRequireLicenseAcceptance>true<\\/PackageRequireLicenseAcceptance>
        <GenerateSerializationAssemblies>Off<\\/GenerateSerializationAssemblies>
        <AppendTargetFrameworkToOutputPath>false<\\/AppendTargetFrameworkToOutputPath>
        <OutputPath>\\.\\.\\\\Other\\\\Artifacts\\\\BuildResult_DotNet_win-x64<\\/OutputPath>
        <PlatformTarget>([^<]+)<\\/PlatformTarget>
        <WarningLevel>\\d<\\/WarningLevel>
        <Prefer32Bit>false<\\/Prefer32Bit>
        <SignAssembly>True<\\/SignAssembly>
        <AssemblyOriginatorKeyFile>\\.\\.\\\\\\.\\.\\\\Other\\\\Resources\\\\PublicKeys\\\\StronglyNamedKey\\\\([^<]+)PublicKey\\.snk<\\/AssemblyOriginatorKeyFile>
        <DelaySign>True<\\/DelaySign>
        <NoWarn>([^<]+)<\\/NoWarn>
        <WarningsAsErrors>([^<]+)<\\/WarningsAsErrors>
        <ErrorLog>\\.\\.\\\\Other\\\\Resources\\\\CodeAnalysisResult\\\\{codeunit_name_regex}\\.sarif<\\/ErrorLog>
        <OutputType>([^<]+)<\\/OutputType>
        <DocumentationFile>\\.\\.\\\\Other\\\\Artifacts\\\\MetaInformation\\\\{codeunit_name_regex}\\.xml<\\/DocumentationFile>(\\n|.)*
    <\\/PropertyGroup>
    <PropertyGroup Condition=\\\"'\\$\\(Configuration\\)'=='Development'\\\">
        <DebugType>full<\\/DebugType>
        <DebugSymbols>true<\\/DebugSymbols>
        <Optimize>false<\\/Optimize>
        <DefineConstants>TRACE;DEBUG;Development<\\/DefineConstants>
        <ErrorReport>prompt<\\/ErrorReport>
    <\\/PropertyGroup>
    <PropertyGroup Condition=\\\"'\\$\\(Configuration\\)'=='QualityCheck'\\\">
        <DebugType>portable<\\/DebugType>
        <DebugSymbols>true<\\/DebugSymbols>
        <Optimize>false<\\/Optimize>
        <DefineConstants>TRACE;QualityCheck<\\/DefineConstants>
        <ErrorReport>none<\\/ErrorReport>
    <\\/PropertyGroup>
    <PropertyGroup Condition=\\\"'\\$\\(Configuration\\)'=='Productive'\\\">
        <DebugType>none<\\/DebugType>
        <DebugSymbols>false<\\/DebugSymbols>
        <Optimize>true<\\/Optimize>
        <DefineConstants>Productive<\\/DefineConstants>
        <ErrorReport>none<\\/ErrorReport>
    <\\/PropertyGroup>(\\n|.)*
<\\/Project>$"""
        return (self.__standardized_task_verify_standard_format_for_csproj_files(regex, csproj_file), regex)

    def __standardized_task_verify_standard_format_for_test_csproj_file(self, csproj_file: str, codeunit_name: str, codeunit_version: str) -> tuple[bool, str]:
        codeunit_name_regex = re.escape(codeunit_name)
        codeunit_version_regex = re.escape(codeunit_version)
        regex = f"""^<Project Sdk=\\"Microsoft\\.NET\\.Sdk\\">
    <PropertyGroup>
        <TargetFramework>([^<]+)<\\/TargetFramework>
        <Authors>([^<]+)<\\/Authors>
        <Version>{codeunit_version_regex}<\\/Version>
        <AssemblyVersion>{codeunit_version_regex}<\\/AssemblyVersion>
        <FileVersion>{codeunit_version_regex}<\\/FileVersion>
        <SelfContained>false<\\/SelfContained>
        <IsPackable>false<\\/IsPackable>
        <PreserveCompilationContext>false<\\/PreserveCompilationContext>
        <GenerateRuntimeConfigurationFiles>true<\\/GenerateRuntimeConfigurationFiles>
        <Copyright>([^<]+)<\\/Copyright>
        <Description>{codeunit_name_regex}Tests is the test-project for {codeunit_name_regex}\\.<\\/Description>
        <PackageProjectUrl>https:\\/\\/([^<]+)<\\/PackageProjectUrl>
        <RepositoryUrl>https:\\/\\/([^<]+)\\.git</RepositoryUrl>
        <RootNamespace>([^<]+)\\.Tests<\\/RootNamespace>
        <ProduceReferenceAssembly>false<\\/ProduceReferenceAssembly>
        <Nullable>(disable|enable|warnings|annotations)<\\/Nullable>
        <Configurations>Development;QualityCheck;Productive<\\/Configurations>
        <IsTestProject>true<\\/IsTestProject>
        <LangVersion>([^<]+)<\\/LangVersion>
        <PackageRequireLicenseAcceptance>true<\\/PackageRequireLicenseAcceptance>
        <GenerateSerializationAssemblies>Off<\\/GenerateSerializationAssemblies>
        <AppendTargetFrameworkToOutputPath>false<\\/AppendTargetFrameworkToOutputPath>
        <OutputPath>\\.\\.\\\\Other\\\\Artifacts\\\\BuildResultTests_DotNet_win-x64<\\/OutputPath>
        <PlatformTarget>([^<]+)<\\/PlatformTarget>
        <WarningLevel>\\d<\\/WarningLevel>
        <Prefer32Bit>false<\\/Prefer32Bit>
        <SignAssembly>True<\\/SignAssembly>
        <AssemblyOriginatorKeyFile>\\.\\.\\\\\\.\\.\\\\Other\\\\Resources\\\\PublicKeys\\\\StronglyNamedKey\\\\([^<]+)PublicKey\\.snk<\\/AssemblyOriginatorKeyFile>
        <DelaySign>True<\\/DelaySign>
        <NoWarn>([^<]+)<\\/NoWarn>
        <WarningsAsErrors>([^<]+)<\\/WarningsAsErrors>
        <ErrorLog>\\.\\.\\\\Other\\\\Resources\\\\CodeAnalysisResult\\\\{codeunit_name_regex}Tests\\.sarif<\\/ErrorLog>
        <OutputType>Library<\\/OutputType>(\\n|.)*
    <\\/PropertyGroup>
    <PropertyGroup Condition=\\\"'\\$\\(Configuration\\)'=='Development'\\\">
        <DebugType>full<\\/DebugType>
        <DebugSymbols>true<\\/DebugSymbols>
        <Optimize>false<\\/Optimize>
        <DefineConstants>TRACE;DEBUG;Development<\\/DefineConstants>
        <ErrorReport>prompt<\\/ErrorReport>
    <\\/PropertyGroup>
    <PropertyGroup Condition=\\\"'\\$\\(Configuration\\)'=='QualityCheck'\\\">
        <DebugType>portable<\\/DebugType>
        <DebugSymbols>true<\\/DebugSymbols>
        <Optimize>false<\\/Optimize>
        <DefineConstants>TRACE;QualityCheck<\\/DefineConstants>
        <ErrorReport>none<\\/ErrorReport>
    <\\/PropertyGroup>
    <PropertyGroup Condition=\\\"'\\$\\(Configuration\\)'=='Productive'\\\">
        <DebugType>none<\\/DebugType>
        <DebugSymbols>false<\\/DebugSymbols>
        <Optimize>true<\\/Optimize>
        <DefineConstants>Productive<\\/DefineConstants>
        <ErrorReport>none<\\/ErrorReport>
    <\\/PropertyGroup>(\\n|.)*
<\\/Project>$"""
        return (self.__standardized_task_verify_standard_format_for_csproj_files(regex, csproj_file), regex)

    def __standardized_task_verify_standard_format_for_csproj_files(self, regex: str, csproj_file: str) -> bool:
        filename = os.path.basename(csproj_file)
        GeneralUtilities.write_message_to_stdout(f"Check {filename}...")
        file_content = GeneralUtilities.read_text_from_file(csproj_file)
        regex = regex.replace("\r", GeneralUtilities.empty_string).replace("\n", "\\n")
        file_content = file_content.replace("\r", GeneralUtilities.empty_string)
        match = re.match(regex, file_content)
        return match is not None

    @GeneralUtilities.check_arguments
    def __standardized_tasks_build_for_dotnet_build(self, csproj_file: str, originaloutputfolder: str, files_to_sign: dict[str, str], commitid: str, verbosity: int, runtimes: list[str], target_environmenttype: str, target_environmenttype_mapping:  dict[str, str], copy_license_file_to_target_folder: bool, repository_folder: str, codeunit_name: str, commandline_arguments: list[str]) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        csproj_filename = os.path.basename(csproj_file)
        GeneralUtilities.write_message_to_stdout(f"Build {csproj_filename}...")
        dotnet_build_configuration: str = target_environmenttype_mapping[target_environmenttype]
        verbosity = self.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        codeunit_folder = os.path.join(repository_folder, codeunit_name)
        csproj_file_folder = os.path.dirname(csproj_file)
        csproj_file_name = os.path.basename(csproj_file)
        csproj_file_name_without_extension = csproj_file_name.split(".")[0]
        sarif_folder = os.path.join(codeunit_folder, "Other", "Resources", "CodeAnalysisResult")
        GeneralUtilities.ensure_directory_exists(sarif_folder)
        gitkeep_file = os.path.join(sarif_folder, ".gitkeep")
        GeneralUtilities.ensure_file_exists(gitkeep_file)
        for runtime in runtimes:
            outputfolder = originaloutputfolder+runtime
            GeneralUtilities.ensure_directory_does_not_exist(os.path.join(csproj_file_folder, "obj"))
            GeneralUtilities.ensure_directory_does_not_exist(outputfolder)
            self.__sc.run_program("dotnet", "clean", csproj_file_folder, verbosity=verbosity)
            GeneralUtilities.ensure_directory_exists(outputfolder)
            self.__sc.run_program("dotnet", "restore", codeunit_folder, verbosity=verbosity)
            self.__sc.run_program_argsasarray("dotnet", ["build", csproj_file_name, "-c", dotnet_build_configuration, "-o", outputfolder, "--runtime", runtime], csproj_file_folder, verbosity=verbosity)
            if copy_license_file_to_target_folder:
                license_file = os.path.join(repository_folder, "License.txt")
                target = os.path.join(outputfolder, f"{codeunit_name}.License.txt")
                shutil.copyfile(license_file, target)
            if 0 < len(files_to_sign):
                for key, value in files_to_sign.items():
                    dll_file = key
                    snk_file = value
                    dll_file_full = os.path.join(outputfolder, dll_file)
                    if os.path.isfile(dll_file_full):
                        GeneralUtilities.assert_condition(self.__sc.run_program("sn", f"-vf {dll_file}", outputfolder, throw_exception_if_exitcode_is_not_zero=False)[0] == 1, f"Pre-verifying of {dll_file} failed.")
                        self.__sc.run_program_argsasarray("sn", ["-R", dll_file, snk_file], outputfolder)
                        GeneralUtilities.assert_condition(self.__sc.run_program("sn", f"-vf {dll_file}", outputfolder, throw_exception_if_exitcode_is_not_zero=False)[0] == 0, f"Verifying of {dll_file} failed.")
            sarif_filename = f"{csproj_file_name_without_extension}.sarif"
            sarif_source_file = os.path.join(sarif_folder, sarif_filename)
            if os.path.exists(sarif_source_file):
                sarif_folder_target = os.path.join(codeunit_folder, "Other", "Artifacts", "CodeAnalysisResult")
                GeneralUtilities.ensure_directory_exists(sarif_folder_target)
                sarif_target_file = os.path.join(sarif_folder_target, sarif_filename)
                GeneralUtilities.ensure_file_does_not_exist(sarif_target_file)
                shutil.copyfile(sarif_source_file, sarif_target_file)

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_dotnet_project(self, buildscript_file: str, default_target_environmenttype: str, target_environmenttype_mapping:  dict[str, str], runtimes: list[str], verbosity: int, commandline_arguments: list[str]) -> None:
        # hint: arguments can be overwritten by commandline_arguments
        # this function builds an exe
        target_environmenttype = self.get_targetenvironmenttype_from_commandline_arguments(commandline_arguments, default_target_environmenttype)
        self.__standardized_tasks_build_for_dotnet_project(
            buildscript_file, target_environmenttype_mapping, default_target_environmenttype, verbosity, target_environmenttype,  runtimes, True, commandline_arguments)

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_dotnet_library_project(self, buildscript_file: str, default_target_environmenttype: str, target_environmenttype_mapping:  dict[str, str], runtimes: list[str], verbosity: int, commandline_arguments: list[str]) -> None:
        # hint: arguments can be overwritten by commandline_arguments
        # this function builds a dll and converts it to a nupkg-file

        target_environmenttype = self.get_targetenvironmenttype_from_commandline_arguments(commandline_arguments, default_target_environmenttype)
        self.__standardized_tasks_build_for_dotnet_project(buildscript_file, target_environmenttype_mapping, default_target_environmenttype, verbosity, target_environmenttype, runtimes, True, commandline_arguments)
        self.__standardized_tasks_build_nupkg_for_dotnet_create_package(buildscript_file, verbosity, commandline_arguments)

    @GeneralUtilities.check_arguments
    def get_default_target_environmenttype_mapping(self) -> dict[str, str]:
        return {
            TasksForCommonProjectStructure.get_development_environment_name(): TasksForCommonProjectStructure.get_development_environment_name(),
            TasksForCommonProjectStructure.get_qualitycheck_environment_name(): TasksForCommonProjectStructure.get_qualitycheck_environment_name(),
            TasksForCommonProjectStructure.get_productive_environment_name(): TasksForCommonProjectStructure.get_productive_environment_name()
        }

    @GeneralUtilities.check_arguments
    def __standardized_tasks_build_for_dotnet_project(self, buildscript_file: str, target_environmenttype_mapping:  dict[str, str], default_target_environment_type: str,  verbosity: int, target_environment_type: str, runtimes: list[str], copy_license_file_to_target_folder: bool, commandline_arguments: list[str]) -> None:
        codeunitname: str = os.path.basename(str(Path(os.path.dirname(buildscript_file)).parent.parent.absolute()))
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        files_to_sign: dict[str, str] = TasksForCommonProjectStructure.get_filestosign_from_commandline_arguments(commandline_arguments,  dict())
        repository_folder: str = str(Path(os.path.dirname(buildscript_file)).parent.parent.parent.absolute())
        commitid = self.__sc.git_get_commit_id(repository_folder)
        outputfolder = GeneralUtilities.resolve_relative_path("../Artifacts", os.path.dirname(buildscript_file))
        codeunit_folder = os.path.join(repository_folder, codeunitname)
        csproj_file = os.path.join(codeunit_folder, codeunitname, codeunitname + ".csproj")
        csproj_test_file = os.path.join(codeunit_folder, codeunitname+"Tests", codeunitname+"Tests.csproj")
        self.__standardized_tasks_build_for_dotnet_build(csproj_file,  os.path.join(outputfolder, "BuildResult_DotNet_"), files_to_sign, commitid, verbosity, runtimes, target_environment_type, target_environmenttype_mapping, copy_license_file_to_target_folder, repository_folder, codeunitname, commandline_arguments)
        self.__standardized_tasks_build_for_dotnet_build(csproj_test_file,  os.path.join(outputfolder, "BuildResultTests_DotNet_"), files_to_sign, commitid, verbosity, runtimes, target_environment_type, target_environmenttype_mapping, copy_license_file_to_target_folder, repository_folder, codeunitname, commandline_arguments)
        self.generate_sbom_for_dotnet_project(codeunit_folder, verbosity, commandline_arguments)
        self.copy_source_files_to_output_directory(buildscript_file)

    @GeneralUtilities.check_arguments
    def __standardized_tasks_build_nupkg_for_dotnet_create_package(self, buildscript_file: str, verbosity: int, commandline_arguments: list[str]) -> None:
        codeunitname: str = os.path.basename(str(Path(os.path.dirname(buildscript_file)).parent.parent.absolute()))
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        repository_folder: str = str(Path(os.path.dirname(buildscript_file)).parent.parent.parent.absolute())
        build_folder = os.path.join(repository_folder, codeunitname, "Other", "Build")
        outputfolder = GeneralUtilities.resolve_relative_path("../Artifacts/BuildResult_NuGet", os.path.dirname(buildscript_file))
        root: etree._ElementTree = etree.parse(os.path.join(build_folder, f"{codeunitname}.nuspec"))
        current_version = root.xpath("//*[name() = 'package']/*[name() = 'metadata']/*[name() = 'version']/text()")[0]
        nupkg_filename = f"{codeunitname}.{current_version}.nupkg"
        nupkg_file = f"{build_folder}/{nupkg_filename}"
        GeneralUtilities.ensure_file_does_not_exist(nupkg_file)
        commit_id = self.__sc.git_get_commit_id(repository_folder)
        self.__sc.run_program("nuget", f"pack {codeunitname}.nuspec -Properties \"commitid={commit_id}\"", build_folder, verbosity=verbosity)
        GeneralUtilities.ensure_directory_does_not_exist(outputfolder)
        GeneralUtilities.ensure_directory_exists(outputfolder)
        os.rename(nupkg_file, f"{outputfolder}/{nupkg_filename}")

    @GeneralUtilities.check_arguments
    def generate_sbom_for_dotnet_project(self, codeunit_folder: str, verbosity: int, commandline_arguments: list[str]) -> None:
        GeneralUtilities.write_message_to_stdout("Generate SBOM...")
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        bomfile_folder = "Other\\Artifacts\\BOM"
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        self.__sc.run_program_argsasarray("dotnet", ["CycloneDX", f"{codeunit_name}\\{codeunit_name}.csproj", "-o", bomfile_folder, "--disable-github-licenses"], codeunit_folder, verbosity=verbosity)
        codeunitversion = self.get_version_of_codeunit(os.path.join(codeunit_folder, f"{codeunit_name}.codeunit.xml"))
        target = f"{codeunit_folder}\\{bomfile_folder}\\{codeunit_name}.{codeunitversion}.sbom.xml"
        GeneralUtilities.ensure_file_does_not_exist(target)
        os.rename(f"{codeunit_folder}\\{bomfile_folder}\\bom.xml", target)
        self.__sc.format_xml_file(target)

    @GeneralUtilities.check_arguments
    def standardized_tasks_run_linting_for_flutter_project_in_common_project_structure(self, script_file: str, default_verbosity: int, args: list[str]):
        pass  # TODO

    @GeneralUtilities.check_arguments
    def standardized_tasks_linting_for_python_codeunit(self, linting_script_file: str, verbosity: int, targetenvironmenttype: str, commandline_arguments: list[str]) -> None:
        codeunitname: str = Path(os.path.dirname(linting_script_file)).parent.parent.name
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        repository_folder: str = str(Path(os.path.dirname(linting_script_file)).parent.parent.parent.absolute())
        errors_found = False
        GeneralUtilities.write_message_to_stdout(f"Check for linting-issues in codeunit {codeunitname}.")
        src_folder = os.path.join(repository_folder, codeunitname, codeunitname)
        tests_folder = src_folder+"Tests"
        # TODO check if there are errors in sarif-file
        for file in GeneralUtilities.get_all_files_of_folder(src_folder)+GeneralUtilities.get_all_files_of_folder(tests_folder):
            relative_file_path_in_repository = os.path.relpath(file, repository_folder)
            if file.endswith(".py") and os.path.getsize(file) > 0 and not self.__sc.file_is_git_ignored(relative_file_path_in_repository, repository_folder):
                GeneralUtilities.write_message_to_stdout(f"Check for linting-issues in {os.path.relpath(file, os.path.join(repository_folder, codeunitname))}.")
                linting_result = self.__sc.python_file_has_errors(file, repository_folder)
                if (linting_result[0]):
                    errors_found = True
                    for error in linting_result[1]:
                        GeneralUtilities.write_message_to_stderr(error)
        if errors_found:
            raise ValueError("Linting-issues occurred.")
        else:
            GeneralUtilities.write_message_to_stdout("No linting-issues found.")

    @GeneralUtilities.check_arguments
    def standardized_tasks_generate_coverage_report(self, repository_folder: str, codeunitname: str, verbosity: int, generate_badges: bool, targetenvironmenttype: str, commandline_arguments: list[str], add_testcoverage_history_entry: bool = None) -> None:
        """This function expects that the file '<repositorybasefolder>/<codeunitname>/Other/Artifacts/TestCoverage/TestCoverage.xml'
        which contains a test-coverage-report in the cobertura-format exists.
        This script expectes that the testcoverage-reportfolder is '<repositorybasefolder>/<codeunitname>/Other/Artifacts/TestCoverageReport'.
        This script expectes that a test-coverage-badges should be added to '<repositorybasefolder>/<codeunitname>/Other/Resources/Badges'."""
        GeneralUtilities.write_message_to_stdout("Generate testcoverage report..")
        self.__sc.assert_is_git_repository(repository_folder)
        codeunit_version = self.get_version_of_codeunit(os.path.join(repository_folder, codeunitname, f"{codeunitname}.codeunit.xml"))
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        if verbosity == 0:
            verbose_argument_for_reportgenerator = "Off"
        elif verbosity == 1:
            verbose_argument_for_reportgenerator = "Error"
        elif verbosity == 2:
            verbose_argument_for_reportgenerator = "Info"
        elif verbosity == 3:
            verbose_argument_for_reportgenerator = "Verbose"
        else:
            raise ValueError(f"Unknown value for verbosity: {GeneralUtilities.str_none_safe(verbosity)}")

        # Generating report
        GeneralUtilities.ensure_directory_does_not_exist(os.path.join(repository_folder, codeunitname, f"{codeunitname}/Other/Artifacts/TestCoverageReport"))
        GeneralUtilities.ensure_directory_exists(os.path.join(repository_folder, codeunitname, "Other/Artifacts/TestCoverageReport"))

        if add_testcoverage_history_entry is None:
            add_testcoverage_history_entry = self.get_is_pre_merge_value_from_commandline_arguments(commandline_arguments, add_testcoverage_history_entry)

        history_folder = f"{codeunitname}/Other/Resources/TestCoverageHistory"
        history_folder_full = os.path.join(repository_folder, history_folder)
        GeneralUtilities.ensure_directory_exists(history_folder_full)
        history_argument = f" -historydir:{history_folder}"
        argument = f"-reports:{codeunitname}/Other/Artifacts/TestCoverage/TestCoverage.xml -targetdir:{codeunitname}/Other/Artifacts/TestCoverageReport --verbosity:{verbose_argument_for_reportgenerator}{history_argument} -title:{codeunitname} -tag:v{codeunit_version}"
        self.__sc.run_program("reportgenerator", argument, repository_folder, verbosity=verbosity)
        if not add_testcoverage_history_entry:
            os.remove(GeneralUtilities.get_direct_files_of_folder(history_folder_full)[-1])

        # Generating badges
        if generate_badges:
            testcoverageubfolger = "Other/Resources/TestCoverageBadges"
            fulltestcoverageubfolger = os.path.join(repository_folder, codeunitname, testcoverageubfolger)
            GeneralUtilities.ensure_directory_does_not_exist(fulltestcoverageubfolger)
            GeneralUtilities.ensure_directory_exists(fulltestcoverageubfolger)
            self.__sc.run_program("reportgenerator", f"-reports:Other/Artifacts/TestCoverage/TestCoverage.xml -targetdir:{testcoverageubfolger} -reporttypes:Badges --verbosity:{verbose_argument_for_reportgenerator}", os.path.join(repository_folder, codeunitname), verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def standardized_tasks_run_testcases_for_dotnet_project(self, runtestcases_file: str, targetenvironmenttype: str, verbosity: int, generate_badges: bool, target_environmenttype_mapping:  dict[str, str], commandline_arguments: list[str]) -> None:
        GeneralUtilities.write_message_to_stdout("Run testcases...")
        dotnet_build_configuration: str = target_environmenttype_mapping[targetenvironmenttype]
        codeunit_name: str = os.path.basename(str(Path(os.path.dirname(runtestcases_file)).parent.parent.absolute()))
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        repository_folder: str = str(Path(os.path.dirname(runtestcases_file)).parent.parent.parent.absolute()).replace("\\", "/")
        coverage_file_folder = os.path.join(repository_folder, codeunit_name, "Other/Artifacts/TestCoverage")
        temp_folder = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        GeneralUtilities.ensure_directory_exists(temp_folder)
        runsettings_file = self.dotnet_runsettings_file
        codeunit_folder = f"{repository_folder}/{codeunit_name}"
        arg = f"test . -c {dotnet_build_configuration} -o {temp_folder}"
        if os.path.isfile(os.path.join(codeunit_folder, runsettings_file)):
            arg = f"{arg} --settings {runsettings_file}"
        arg = f"{arg} /p:CollectCoverage=true /p:CoverletOutput=../Other/Artifacts/TestCoverage/Testcoverage /p:CoverletOutputFormat=cobertura"
        self.__sc.run_program("dotnet", arg, codeunit_folder, verbosity=verbosity, print_live_output=True)
        target_file = os.path.join(coverage_file_folder,  "TestCoverage.xml")
        GeneralUtilities.ensure_file_does_not_exist(target_file)
        os.rename(os.path.join(coverage_file_folder,  "Testcoverage.cobertura.xml"), target_file)
        self.__remove_unrelated_package_from_testcoverage_file(target_file, codeunit_name)
        root: etree._ElementTree = etree.parse(target_file)
        source_base_path_in_coverage_file: str = root.xpath("//coverage/sources/source/text()")[0].replace("\\", "/")
        content = GeneralUtilities.read_text_from_file(target_file)
        GeneralUtilities.assert_condition(source_base_path_in_coverage_file.startswith(repository_folder) or repository_folder.startswith(source_base_path_in_coverage_file), f"Unexpected path for coverage. Sourcepath: \"{source_base_path_in_coverage_file}\"; repository: \"{repository_folder}\"")
        content = re.sub('\\\\', '/', content)
        content = re.sub("filename=\"([^\"]+)\"", lambda match: self.__standardized_tasks_run_testcases_for_dotnet_project_helper(source_base_path_in_coverage_file, codeunit_folder, match), content)
        GeneralUtilities.write_text_to_file(target_file, content)
        self.run_testcases_common_post_task(repository_folder, codeunit_name, verbosity, generate_badges, targetenvironmenttype, commandline_arguments)
        artifacts_folder = os.path.join(repository_folder, codeunit_name, "Other", "Artifacts")
        for subfolder in GeneralUtilities.get_direct_folders_of_folder(artifacts_folder):
            if os.path.basename(subfolder).startswith("BuildResultTests_DotNet_"):
                GeneralUtilities.ensure_directory_does_not_exist(subfolder)

    @GeneralUtilities.check_arguments
    def run_testcases_common_post_task(self, repository_folder: str, codeunit_name: str, verbosity: int, generate_badges: bool, targetenvironmenttype: str, commandline_arguments: list[str]) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        coverage_file_folder = os.path.join(repository_folder, codeunit_name, "Other/Artifacts/TestCoverage")
        coveragefiletarget = os.path.join(coverage_file_folder,  "TestCoverage.xml")
        self.update_path_of_source_in_testcoverage_file(repository_folder, codeunit_name)
        self.standardized_tasks_generate_coverage_report(repository_folder, codeunit_name, verbosity, generate_badges, targetenvironmenttype, commandline_arguments)
        self.check_testcoverage(coveragefiletarget, repository_folder, codeunit_name)

    @GeneralUtilities.check_arguments
    def update_path_of_source_in_testcoverage_file(self, repository_folder: str, codeunitname: str) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        GeneralUtilities.write_message_to_stdout("Update paths of source files in testcoverage files..")
        folder = f"{repository_folder}/{codeunitname}/Other/Artifacts/TestCoverage"
        filename = "TestCoverage.xml"
        full_file = os.path.join(folder, filename)
        GeneralUtilities.write_text_to_file(full_file, re.sub("<source>.+<\\/source>", f"<source><!--[repository]/-->./{codeunitname}/</source>", GeneralUtilities.read_text_from_file(full_file)))
        self.__remove_not_existing_files_from_testcoverage_file(full_file, repository_folder, codeunitname)

    @GeneralUtilities.check_arguments
    def __standardized_tasks_run_testcases_for_dotnet_project_helper(self, source: str, codeunit_folder: str, match: re.Match) -> str:
        self.assert_is_codeunit_folder(codeunit_folder)
        filename = match.group(1)
        file = os.path.join(source, filename)
        # GeneralUtilities.assert_condition(os.path.isfile(file),f"File \"{file}\" does not exist.")
        GeneralUtilities.assert_condition(file.startswith(codeunit_folder), f"Unexpected path for coverage-file. File: \"{file}\"; codeunitfolder: \"{codeunit_folder}\"")
        filename_relative = f".{file[len(codeunit_folder):]}"
        return f'filename="{filename_relative}"'

    @GeneralUtilities.check_arguments
    def __remove_not_existing_files_from_testcoverage_file(self, testcoveragefile: str, repository_folder: str, codeunit_name: str) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        root: etree._ElementTree = etree.parse(testcoveragefile)
        codeunit_folder = os.path.join(repository_folder, codeunit_name)
        xpath = f"//coverage/packages/package[@name='{codeunit_name}']/classes/class"
        coverage_report_classes = root.xpath(xpath)
        found_existing_files = False
        for coverage_report_class in coverage_report_classes:
            filename = coverage_report_class.attrib['filename']
            file = os.path.join(codeunit_folder, filename)
            if os.path.isfile(file):
                found_existing_files = True
            else:
                coverage_report_class.getparent().remove(coverage_report_class)
        GeneralUtilities.assert_condition(found_existing_files, f"No existing files in testcoderage-report-file \"{testcoveragefile}\".")
        result = etree.tostring(root).decode("utf-8")
        GeneralUtilities.write_text_to_file(testcoveragefile, result)

    @GeneralUtilities.check_arguments
    def __remove_unrelated_package_from_testcoverage_file(self, file: str, codeunit_name: str) -> None:
        root: etree._ElementTree = etree.parse(file)
        packages = root.xpath('//coverage/packages/package')
        for package in packages:
            if package.attrib['name'] != codeunit_name:
                package.getparent().remove(package)
        result = etree.tostring(root).decode("utf-8")
        GeneralUtilities.write_text_to_file(file, result)

    @GeneralUtilities.check_arguments
    def write_version_to_codeunit_file(self, codeunit_file: str, current_version: str) -> None:
        versionregex = "\\d+\\.\\d+\\.\\d+"
        versiononlyregex = f"^{versionregex}$"
        pattern = re.compile(versiononlyregex)
        if pattern.match(current_version):
            GeneralUtilities.write_text_to_file(codeunit_file, re.sub(f"<cps:version>{versionregex}<\\/cps:version>", f"<cps:version>{current_version}</cps:version>", GeneralUtilities.read_text_from_file(codeunit_file)))
        else:
            raise ValueError(f"Version '{current_version}' does not match version-regex '{versiononlyregex}'.")

    @GeneralUtilities.check_arguments
    def standardized_tasks_linting_for_dotnet_project(self, linting_script_file: str, verbosity: int, targetenvironmenttype: str, commandline_arguments: list[str]) -> None:
        GeneralUtilities.write_message_to_stdout("Run linting...")
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        # TODO check if there are errors in sarif-file

    @GeneralUtilities.check_arguments
    def __export_codeunit_reference_content_to_reference_repository(self, project_version_identifier: str, replace_existing_content: bool, target_folder_for_reference_repository: str, repository: str, codeunitname: str, projectname: str, codeunit_version: str, public_repository_url: str, branch: str) -> None:
        codeunit_folder = os.path.join(repository, codeunitname)
        codeunit_file = os.path.join(codeunit_folder, f"{codeunitname}.codeunit.xml")
        codeunit_has_testcases = self.codeunit_has_testable_sourcecode(codeunit_file)
        target_folder = os.path.join(target_folder_for_reference_repository, project_version_identifier, codeunitname)
        if os.path.isdir(target_folder) and not replace_existing_content:
            raise ValueError(f"Folder '{target_folder}' already exists.")
        GeneralUtilities.ensure_directory_does_not_exist(target_folder)
        GeneralUtilities.ensure_directory_exists(target_folder)
        codeunit_version_identifier = "Latest" if project_version_identifier == "Latest" else "v"+codeunit_version
        page_title = f"{codeunitname} {codeunit_version_identifier} codeunit-reference"
        diff_report = f"{repository}/{codeunitname}/Other/Artifacts/DiffReport/DiffReport.html"
        diff_target_folder = os.path.join(target_folder, "DiffReport")
        GeneralUtilities.ensure_directory_exists(diff_target_folder)
        diff_target_file = os.path.join(diff_target_folder, "DiffReport.html")
        title = (f'Reference of codeunit {codeunitname} {codeunit_version_identifier} (contained in project <a href="{public_repository_url}">{projectname}</a> {project_version_identifier})')
        if public_repository_url is None:
            repo_url_html = GeneralUtilities.empty_string
        else:
            repo_url_html = f'<a href="{public_repository_url}/tree/{branch}/{codeunitname}">Source-code</a>'
        if codeunit_has_testcases:
            coverage_report_link = '<a href="./TestCoverageReport/index.html">Test-coverage-report</a><br>'
        else:
            coverage_report_link = GeneralUtilities.empty_string
        index_file_for_reference = os.path.join(target_folder, "index.html")

        design_file = None
        design = "ModestDark"
        if design == "ModestDark":
            design_file = GeneralUtilities.get_modest_dark_url()
        # TODO make designs from customizable sources be available by a customizable name and outsource this to a class-property because this is duplicated code.
        if design_file is None:
            design_html = GeneralUtilities.empty_string
        else:
            design_html = f'<link type="text/css" rel="stylesheet" href="{design_file}" />'

        index_file_content = f"""<!DOCTYPE html>
<html lang="en">

  <head>
    <meta charset="UTF-8">
    <title>{page_title}</title>
    {design_html}
  </head>

  <body>
    <h1>{title}</h1>
    <hr/>
    Available reference-content for {codeunitname}:<br>
    {repo_url_html}<br>
    <!--TODO add artefacts-link: <a href="./x">Artefacts</a><br>-->
    <a href="./Reference/index.html">Reference</a><br>
    <a href="./DiffReport/DiffReport.html">Diff-report</a><br>
    {coverage_report_link}
  </body>

</html>
"""

        GeneralUtilities.ensure_file_exists(index_file_for_reference)
        GeneralUtilities.write_text_to_file(index_file_for_reference, index_file_content)
        other_folder_in_repository = os.path.join(repository, codeunitname, "Other")
        source_generatedreference = os.path.join(other_folder_in_repository, "Artifacts", "Reference")
        target_generatedreference = os.path.join(target_folder, "Reference")
        shutil.copytree(source_generatedreference, target_generatedreference)

        shutil.copyfile(diff_report, diff_target_file)

        if codeunit_has_testcases:
            source_testcoveragereport = os.path.join(other_folder_in_repository, "Artifacts", "TestCoverageReport")
            if os.path.isdir(source_testcoveragereport):  # check, because it is not a mandatory artifact. if the artifact is not available, the user gets already a warning.
                target_testcoveragereport = os.path.join(target_folder, "TestCoverageReport")
                shutil.copytree(source_testcoveragereport, target_testcoveragereport)

    @GeneralUtilities.check_arguments
    def __standardized_tasks_release_artifact(self, information: CreateReleaseInformationForProjectInCommonProjectFormat) -> None:
        GeneralUtilities.write_message_to_stdout("Release artifacts...")
        project_version = self.__sc.get_semver_version_from_gitversion(information.repository)
        target_folder_base = os.path.join(information.artifacts_folder, information.projectname, project_version)
        GeneralUtilities.ensure_directory_exists(target_folder_base)

        self.build_codeunits(information.repository, information.verbosity, information.target_environmenttype_for_productive, information.additional_arguments_file, False, information.export_target, [], True, "Generate artifacts")  # Generate artifacts after merge (because now are constants like commit-id of the new version available)

        reference_folder = os.path.join(information.reference_repository, "ReferenceContent")

        for codeunitname in self.get_codeunits(information.repository):
            # Push artifacts to registry
            if information.verbosity > 2:
                GeneralUtilities.write_message_to_stdout(f"Push artifacts of {codeunitname}...")
            scriptfilename = f"PushArtifacts.{codeunitname}.py"
            push_artifact_to_registry_script = os.path.join(information.push_artifacts_scripts_folder, scriptfilename)
            if os.path.isfile(push_artifact_to_registry_script):
                GeneralUtilities.write_message_to_stdout(f"Push artifacts of codeunit {codeunitname}...")
                self.__sc.run_program("python", push_artifact_to_registry_script, information.push_artifacts_scripts_folder, verbosity=information.verbosity, throw_exception_if_exitcode_is_not_zero=True)

            # Copy reference of codeunit to reference-repository
            codeunit_version = self.get_version_of_codeunit_folder(os.path.join(information.repository, codeunitname))
            self.__export_codeunit_reference_content_to_reference_repository(f"v{project_version}", False, reference_folder, information.repository, codeunitname, information.projectname, codeunit_version, information.public_repository_url, f"v{project_version}")
            self.__export_codeunit_reference_content_to_reference_repository("Latest", True, reference_folder, information.repository, codeunitname, information.projectname, codeunit_version, information.public_repository_url, information.target_branch_name)

            # Generate reference
            self.__generate_entire_reference(information.projectname, project_version, reference_folder)

    @staticmethod
    @GeneralUtilities.check_arguments
    def _internal_sort_reference_folder(folder1: str, folder2: str) -> int:
        """Returns a value greater than 0 if and only if folder1 has a base-folder-name with a with a higher version than the base-folder-name of folder2.
        Returns a value lower than 0 if and only if folder1 has a base-folder-name with a with a lower version than the base-folder-name of folder2.
        Returns 0 if both values are equal."""
        if (folder1 == folder2):
            return 0

        version_identifier_1 = os.path.basename(folder1)
        if version_identifier_1 == "Latest":
            return -1
        version_identifier_1 = version_identifier_1[1:]

        version_identifier_2 = os.path.basename(folder2)
        if version_identifier_2 == "Latest":
            return 1
        version_identifier_2 = version_identifier_2[1:]

        if version.parse(version_identifier_1) < version.parse(version_identifier_2):
            return -1
        elif version.parse(version_identifier_1) > version.parse(version_identifier_2):
            return 1
        else:
            return 0

    @GeneralUtilities.check_arguments
    def __generate_entire_reference(self, projectname: str, project_version: str, reference_folder: str) -> None:
        all_available_version_identifier_folders_of_reference: list[str] = list(folder for folder in GeneralUtilities.get_direct_folders_of_folder(reference_folder))
        all_available_version_identifier_folders_of_reference = sorted(all_available_version_identifier_folders_of_reference, key=cmp_to_key(TasksForCommonProjectStructure._internal_sort_reference_folder))
        reference_versions_html_lines = []
        reference_versions_html_lines.append('    <hr/>')
        for all_available_version_identifier_folder_of_reference in all_available_version_identifier_folders_of_reference:
            version_identifier_of_project = os.path.basename(all_available_version_identifier_folder_of_reference)
            if version_identifier_of_project == "Latest":
                latest_version_hint = f" (v{project_version})"
            else:
                latest_version_hint = GeneralUtilities.empty_string
            reference_versions_html_lines.append(f'    <h2>{version_identifier_of_project}{latest_version_hint}</h2>')
            reference_versions_html_lines.append("    Contained codeunits:<br/>")
            reference_versions_html_lines.append("    <ul>")
            for codeunit_reference_folder in list(folder for folder in GeneralUtilities.get_direct_folders_of_folder(all_available_version_identifier_folder_of_reference)):
                reference_versions_html_lines.append(f'      <li><a href="./{version_identifier_of_project}/{os.path.basename(codeunit_reference_folder)}/index.html">' +
                                                     f'{os.path.basename(codeunit_reference_folder)} {version_identifier_of_project}</a></li>')
            reference_versions_html_lines.append("    </ul>")
            reference_versions_html_lines.append('    <hr/>')
            if version_identifier_of_project == "Latest":
                latest_version_hint = "    <h2>History</h2>"

        design_file = None
        design = "ModestDark"
        if design == "ModestDark":
            design_file = GeneralUtilities.get_modest_dark_url()
        # TODO make designs from customizable sources be available by a customizable name and outsource this to a class-property because this is duplicated code.
        if design_file is None:
            design_html = GeneralUtilities.empty_string
        else:
            design_html = f'<link type="text/css" rel="stylesheet" href="{design_file}" />'

        reference_versions_links_file_content = "    \n".join(reference_versions_html_lines)
        title = f"{projectname}-reference"
        reference_index_file = os.path.join(reference_folder, "index.html")
        reference_index_file_content = f"""<!DOCTYPE html>
<html lang="en">

  <head>
    <meta charset="UTF-8">
    <title>{title}</title>
    {design_html}
  </head>

  <body>
    <h1>{title}</h1>
{reference_versions_links_file_content}
  </body>

</html>
"""  # see https://getbootstrap.com/docs/5.1/getting-started/introduction/
        GeneralUtilities.write_text_to_file(reference_index_file, reference_index_file_content)

    @GeneralUtilities.check_arguments
    def push_nuget_build_artifact(self, push_script_file: str, codeunitname: str, registry_address: str, repository_folder_name: str, api_key: str):
        # when pusing to "default public" nuget-server then use registry_address: "nuget.org"
        build_artifact_folder = GeneralUtilities.resolve_relative_path(f"../../Submodules/{repository_folder_name}/{codeunitname}/Other/Artifacts/BuildResult_NuGet", os.path.dirname(push_script_file))
        self.__sc.push_nuget_build_artifact(self.__sc.find_file_by_extension(build_artifact_folder, "nupkg"), registry_address, api_key)

    @GeneralUtilities.check_arguments
    def assert_no_uncommitted_changes(self, repository_folder: str):
        if self.__sc.git_repository_has_uncommitted_changes(repository_folder):
            raise ValueError(f"Repository '{repository_folder}' has uncommitted changes.")

    @GeneralUtilities.check_arguments
    def ensure_certificate_authority_for_development_purposes_is_generated(self, product_folder: str):
        product_name: str = os.path.basename(product_folder)
        now = datetime.now()
        ca_name = f"{product_name}CA_{now.year:04}{now.month:02}{now.day:02}{now.hour:02}{now.min:02}{now.second:02}"
        ca_folder = os.path.join(product_folder, "Other", "Resources", "CA")
        generate_certificate = True
        if os.path.isdir(ca_folder):
            ca_files = [file for file in GeneralUtilities.get_direct_files_of_folder(ca_folder) if file.endswith(".crt")]
            if len(ca_files) > 0:
                ca_file = ca_files[-1]  # pylint:disable=unused-variable
                certificate_is_valid = True  # TODO check if certificate is really valid
                generate_certificate = not certificate_is_valid
        if generate_certificate:
            self.__sc.generate_certificate_authority(ca_folder, ca_name, "DE", "SubjST", "SubjL", "SubjO", "SubjOU")
        # TODO add switch to auto-install the script if desired
        # for windows: powershell Import-Certificate -FilePath ConSurvCA_20241121000236.crt -CertStoreLocation 'Cert:\CurrentUser\Root'
        # for linux: (TODO)

    @GeneralUtilities.check_arguments
    def generate_certificate_for_development_purposes_for_product(self, repository_folder: str):
        self.__sc.assert_is_git_repository(repository_folder)
        product_name = os.path.basename(repository_folder)
        ca_folder: str = os.path.join(repository_folder, "Other", "Resources", "CA")
        self.__generate_certificate_for_development_purposes(product_name, os.path.join(repository_folder, "Other", "Resources"), ca_folder, None)

    @GeneralUtilities.check_arguments
    def generate_certificate_for_development_purposes_for_external_service(self, service_folder: str, domain: str = None):
        testservice_name = os.path.basename(service_folder)
        ca_folder: str = None  # TODO
        self.__generate_certificate_for_development_purposes(testservice_name, os.path.join(service_folder, "Resources"), ca_folder, domain)

    @GeneralUtilities.check_arguments
    def generate_certificate_for_development_purposes_for_codeunit(self, codeunit_folder: str, domain: str = None):
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        self.ensure_product_resource_is_imported(codeunit_folder, "CA")
        ca_folder: str = os.path.join(codeunit_folder, "Other", "Resources", "CA")
        self.__generate_certificate_for_development_purposes(codeunit_name, os.path.join(codeunit_folder, "Other", "Resources"), ca_folder, domain)

    @GeneralUtilities.check_arguments
    def __generate_certificate_for_development_purposes(self, service_name: str, resources_folder: str, ca_folder: str, domain: str = None):
        if domain is None:
            domain = f"{service_name}.test.local"
        domain = domain.lower()
        resource_name: str = "DevelopmentCertificate"
        certificate_folder: str = os.path.join(resources_folder, resource_name)

        resource_content_filename: str = service_name+resource_name
        certificate_file = os.path.join(certificate_folder, f"{domain}.crt")
        unsignedcertificate_file = os.path.join(certificate_folder, f"{domain}.unsigned.crt")
        certificate_exists = os.path.exists(certificate_file)
        if certificate_exists:
            certificate_expired = GeneralUtilities.certificate_is_expired(certificate_file)
            generate_new_certificate = certificate_expired
        else:
            generate_new_certificate = True
        if generate_new_certificate:
            GeneralUtilities.ensure_directory_does_not_exist(certificate_folder)
            GeneralUtilities.ensure_directory_exists(certificate_folder)
            GeneralUtilities.write_message_to_stdout("Generate TLS-certificate for development-purposes.")
            self.__sc.generate_certificate(certificate_folder, domain, resource_content_filename, "DE", "SubjST", "SubjL", "SubjO", "SubjOU")
            self.__sc.generate_certificate_sign_request(certificate_folder, domain, resource_content_filename, "DE", "SubjST", "SubjL", "SubjO", "SubjOU")
            ca_name = os.path.basename(self.__sc.find_last_file_by_extension(ca_folder, "crt"))[:-4]
            self.__sc.sign_certificate(certificate_folder, ca_folder, ca_name, domain, resource_content_filename)
            GeneralUtilities.ensure_file_does_not_exist(unsignedcertificate_file)

    @GeneralUtilities.check_arguments
    def copy_product_resource_to_codeunit_resource_folder(self, codeunit_folder: str, resourcename: str) -> None:
        repository_folder = GeneralUtilities.resolve_relative_path(f"..", codeunit_folder)
        self.__sc.assert_is_git_repository(repository_folder)
        src_folder = GeneralUtilities.resolve_relative_path(f"Other/Resources/{resourcename}", repository_folder)
        GeneralUtilities.assert_condition(os.path.isdir(src_folder), f"Required product-resource {resourcename} does not exist. Expected folder: {src_folder}")
        trg_folder = GeneralUtilities.resolve_relative_path(f"Other/Resources/{resourcename}", codeunit_folder)
        GeneralUtilities.ensure_directory_does_not_exist(trg_folder)
        GeneralUtilities.ensure_directory_exists(trg_folder)
        GeneralUtilities.copy_content_of_folder(src_folder, trg_folder)

    @GeneralUtilities.check_arguments
    def ensure_product_resource_is_imported(self, codeunit_folder: str, product_resource_name: str) -> None:
        product_folder = os.path.dirname(codeunit_folder)
        source_folder = os.path.join(product_folder, "Other", "Resources", product_resource_name)
        target_folder = os.path.join(codeunit_folder, "Other", "Resources", product_resource_name)
        GeneralUtilities.ensure_directory_does_not_exist(target_folder)
        GeneralUtilities.ensure_directory_exists(target_folder)
        GeneralUtilities.copy_content_of_folder(source_folder, target_folder)

    @GeneralUtilities.check_arguments
    def get_codeunits(self, repository_folder: str, ignore_disabled_codeunits: bool = True) -> list[str]:
        codeunits_with_dependent_codeunits: dict[str, set[str]] = dict[str, set[str]]()
        subfolders = GeneralUtilities.get_direct_folders_of_folder(repository_folder)
        for subfolder in subfolders:
            codeunit_name: str = os.path.basename(subfolder)
            codeunit_file = os.path.join(subfolder, f"{codeunit_name}.codeunit.xml")
            if os.path.exists(codeunit_file):
                if ignore_disabled_codeunits and not self.codeunit_is_enabled(codeunit_file):
                    continue
                codeunits_with_dependent_codeunits[codeunit_name] = self.get_dependent_code_units(codeunit_file)
        sorted_codeunits = self._internal_get_sorted_codeunits_by_dict(codeunits_with_dependent_codeunits)
        return sorted_codeunits

    @GeneralUtilities.check_arguments
    def codeunit_is_enabled(self, codeunit_file: str) -> bool:
        root: etree._ElementTree = etree.parse(codeunit_file)
        return GeneralUtilities.string_to_boolean(str(root.xpath('//cps:codeunit/@enabled', namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'})[0]))

    @GeneralUtilities.check_arguments
    def merge_to_main_branch(self, repository_folder: str, source_branch: str = "other/next-release", target_branch: str = "main", verbosity: int = 1, additional_arguments_file: str = None, fast_forward_source_branch: bool = False) -> None:
        # This is an automatization for automatic merges. Usual this merge would be done by a pull request in a sourcecode-version-control-platform
        # (like GitHub, GitLab or Azure DevOps)
        GeneralUtilities.write_message_to_stdout(f"Merge to main-branch...")
        self.__sc.assert_is_git_repository(repository_folder)
        self.assert_no_uncommitted_changes(repository_folder)

        src_branch_commit_id = self.__sc.git_get_commit_id(repository_folder,  source_branch)
        if (src_branch_commit_id == self.__sc.git_get_commit_id(repository_folder,  target_branch)):
            raise ValueError(f"Can not merge because the source-branch and the target-branch are on the same commit (commit-id: {src_branch_commit_id})")

        self.__sc.git_checkout(repository_folder, source_branch)
        self.build_codeunits(repository_folder, verbosity, TasksForCommonProjectStructure.get_qualitycheck_environment_name(), additional_arguments_file, True, None, [], True, "Check if product is buildable")
        self.__sc.git_merge(repository_folder, source_branch, target_branch, False, False, None, False, False)
        self.__sc.git_commit(repository_folder, f'Merge branch {source_branch} into {target_branch}', stage_all_changes=True, no_changes_behavior=1)
        self.__sc.git_checkout(repository_folder, target_branch)
        if fast_forward_source_branch:
            self.__sc.git_merge(repository_folder, target_branch, source_branch, True, True)

    @GeneralUtilities.check_arguments
    def merge_to_stable_branch(self, create_release_file: str, createRelease_configuration: CreateReleaseConfiguration):

        GeneralUtilities.write_message_to_stdout(f"Create release for project {createRelease_configuration.projectname}.")
        GeneralUtilities.write_message_to_stdout(f"Merge to stable-branch...")
        self.__sc.assert_is_git_repository(createRelease_configuration.repository_folder)
        folder_of_create_release_file_file = os.path.abspath(os.path.dirname(create_release_file))

        build_repository_folder = GeneralUtilities.resolve_relative_path(f"..{os.path.sep}..", folder_of_create_release_file_file)
        self.assert_no_uncommitted_changes(build_repository_folder)

        repository_folder = GeneralUtilities.resolve_relative_path(f"Submodules{os.path.sep}{createRelease_configuration.repository_folder_name}", build_repository_folder)
        mergeInformation = MergeToStableBranchInformationForProjectInCommonProjectFormat(repository_folder, createRelease_configuration.additional_arguments_file, createRelease_configuration.artifacts_folder)
        createReleaseInformation = CreateReleaseInformationForProjectInCommonProjectFormat(repository_folder, createRelease_configuration.artifacts_folder, createRelease_configuration.projectname, createRelease_configuration.public_repository_url, mergeInformation.targetbranch, mergeInformation.additional_arguments_file, mergeInformation.export_target, createRelease_configuration.push_artifacts_scripts_folder)
        createReleaseInformation.verbosity = createRelease_configuration.verbosity

        self.__sc.git_checkout(build_repository_folder, createRelease_configuration.build_repository_branch)
        self.__sc.git_checkout(createReleaseInformation.reference_repository, createRelease_configuration.reference_repository_branch_name)

        self.__sc.assert_is_git_repository(repository_folder)
        self.__sc.assert_is_git_repository(createReleaseInformation.reference_repository)

        # TODO check if repository_folder-merge-source-branch and repository_folder-merge-target-branch have different commits
        self.assert_no_uncommitted_changes(repository_folder)
        mergeInformation.verbosity = createRelease_configuration.verbosity
        mergeInformation.push_target_branch = createRelease_configuration.remotename is not None
        mergeInformation.push_target_branch_remote_name = createRelease_configuration.remotename
        mergeInformation.push_source_branch = createRelease_configuration.remotename is not None
        mergeInformation.push_source_branch_remote_name = createRelease_configuration.remotename
        new_project_version = self.__standardized_tasks_merge_to_stable_branch(mergeInformation)

        self.__standardized_tasks_release_artifact(createReleaseInformation)

        GeneralUtilities.assert_condition(createRelease_configuration.reference_repository_remote_name is not None, "Remote for reference-repository not set.")
        self.__sc.git_commit(createReleaseInformation.reference_repository, f"Added reference of {createRelease_configuration.projectname} v{new_project_version}")
        self.__sc.git_push_with_retry(createReleaseInformation.reference_repository, createRelease_configuration.reference_repository_remote_name, createRelease_configuration.reference_repository_branch_name, createRelease_configuration.reference_repository_branch_name, verbosity=createRelease_configuration.verbosity)
        self.__sc.git_commit(build_repository_folder, f"Added {createRelease_configuration.projectname} release v{new_project_version}")
        GeneralUtilities.write_message_to_stdout(f"Finished release for project {createRelease_configuration.projectname} v{new_project_version} successfully.")
        return new_project_version

    @GeneralUtilities.check_arguments
    def create_release_starter_for_repository_in_standardized_format(self, create_release_file: str, logfile: str, verbosity: int, addLogOverhead: bool, commandline_arguments: list[str]):
        # hint: arguments can be overwritten by commandline_arguments
        folder_of_this_file = os.path.dirname(create_release_file)
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        result = self.__sc.run_program("python", f"CreateRelease.py --overwrite_verbosity {str(verbosity)}", folder_of_this_file,  verbosity=verbosity, log_file=logfile, addLogOverhead=addLogOverhead, print_live_output=True, throw_exception_if_exitcode_is_not_zero=False)
        if result[0] != 0:
            raise ValueError(f"CreateRelease.py resulted in exitcode {result[0]}.")

    @GeneralUtilities.check_arguments
    def __standardized_tasks_merge_to_stable_branch(self, information: MergeToStableBranchInformationForProjectInCommonProjectFormat) -> str:
        src_branch_commit_id = self.__sc.git_get_commit_id(information.repository,  information.sourcebranch)
        if (src_branch_commit_id == self.__sc.git_get_commit_id(information.repository,  information.targetbranch)):
            raise ValueError(f"Can not merge because the source-branch and the target-branch are on the same commit (commit-id: {src_branch_commit_id})")

        self.assert_no_uncommitted_changes(information.repository)
        self.__sc.git_checkout(information.repository, information.sourcebranch)
        self.__sc.run_program("git", "clean -dfx", information.repository,  verbosity=information.verbosity, throw_exception_if_exitcode_is_not_zero=True)
        project_version = self.__sc.get_semver_version_from_gitversion(information.repository)

        self.build_codeunits(information.repository, information.verbosity, information.target_environmenttype_for_qualitycheck, information.additional_arguments_file, False, information.export_target, [], True, "Productive build")  # verify hat codeunits are buildable with productive-config before merge

        self.assert_no_uncommitted_changes(information.repository)

        commit_id = self.__sc.git_merge(information.repository, information.sourcebranch, information.targetbranch, True, True)
        self.__sc.git_create_tag(information.repository, commit_id, f"v{project_version}", information.sign_git_tags)

        if information.push_source_branch:
            GeneralUtilities.write_message_to_stdout("Push source-branch...")
            self.__sc.git_push_with_retry(information.repository, information.push_source_branch_remote_name, information.sourcebranch, information.sourcebranch, pushalltags=True, verbosity=information.verbosity)

        if information.push_target_branch:
            GeneralUtilities.write_message_to_stdout("Push target-branch...")
            self.__sc.git_push_with_retry(information.repository, information.push_target_branch_remote_name, information.targetbranch, information.targetbranch, pushalltags=True, verbosity=information.verbosity)

        return project_version

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_docker_project(self, build_script_file: str, target_environment_type: str, verbosity: int, commandline_arguments: list[str]) -> None:
        self.standardized_tasks_build_for_docker_project_with_additional_build_arguments(build_script_file, target_environment_type, verbosity, commandline_arguments, dict[str, str]())
        self.generate_sbom_for_docker_image(build_script_file, verbosity, commandline_arguments)

    @GeneralUtilities.check_arguments
    def merge_sbom_file_from_dependent_codeunit_into_this(self, build_script_file: str, dependent_codeunit_name: str) -> None:
        codeunitname: str = Path(os.path.dirname(build_script_file)).parent.parent.name
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", str(os.path.dirname(build_script_file)))
        repository_folder = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        dependent_codeunit_folder = os.path.join(repository_folder, dependent_codeunit_name).replace("\\", "/")
        t = TasksForCommonProjectStructure()
        sbom_file = f"{repository_folder}/{codeunitname}/Other/Artifacts/BOM/{codeunitname}.{t.get_version_of_codeunit_folder(codeunit_folder)}.sbom.xml"
        dependent_sbom_file = f"{repository_folder}/{dependent_codeunit_name}/Other/Artifacts/BOM/{dependent_codeunit_name}.{t.get_version_of_codeunit_folder(dependent_codeunit_folder)}.sbom.xml"
        self.merge_sbom_file(repository_folder, dependent_sbom_file, sbom_file)

    @GeneralUtilities.check_arguments
    def merge_sbom_file(self, repository_folder: str, source_sbom_file_relative: str, target_sbom_file_relative: str) -> None:
        GeneralUtilities.assert_file_exists(os.path.join(repository_folder, source_sbom_file_relative))
        GeneralUtilities.assert_file_exists(os.path.join(repository_folder, target_sbom_file_relative))
        target_original_sbom_file_relative = os.path.dirname(target_sbom_file_relative)+"/"+os.path.basename(target_sbom_file_relative)+".original.xml"
        os.rename(os.path.join(repository_folder, target_sbom_file_relative), os.path.join(repository_folder, target_original_sbom_file_relative))

        self.ensure_cyclonedxcli_is_available(repository_folder)
        cyclonedx_exe = os.path.join(repository_folder, "Other/Resources/CycloneDXCLI/cyclonedx-cli")
        if GeneralUtilities.current_system_is_windows():
            cyclonedx_exe = cyclonedx_exe+".exe"
        self.__sc.run_program(cyclonedx_exe, f"merge --input-files {source_sbom_file_relative} {target_original_sbom_file_relative} --output-file {target_sbom_file_relative}", repository_folder)
        GeneralUtilities.ensure_file_does_not_exist(os.path.join(repository_folder, target_original_sbom_file_relative))
        self.__sc.format_xml_file(os.path.join(repository_folder, target_sbom_file_relative))

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_docker_project_with_additional_build_arguments(self, build_script_file: str, target_environment_type: str, verbosity: int, commandline_arguments: list[str], custom_arguments: dict[str, str]) -> None:
        use_cache: bool = False
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        codeunitname: str = Path(os.path.dirname(build_script_file)).parent.parent.name
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", str(os.path.dirname(build_script_file)))
        codeunitname_lower = codeunitname.lower()
        codeunit_file = os.path.join(codeunit_folder, f"{codeunitname}.codeunit.xml")
        codeunitversion = self.get_version_of_codeunit(codeunit_file)
        args = ["image", "build", "--pull", "--force-rm", "--progress=plain", "--build-arg", f"TargetEnvironmentType={target_environment_type}", "--build-arg", f"CodeUnitName={codeunitname}", "--build-arg", f"CodeUnitVersion={codeunitversion}", "--build-arg", f"CodeUnitOwnerName={self.get_codeunit_owner_name(codeunit_file)}", "--build-arg", f"CodeUnitOwnerEMailAddress={self.get_codeunit_owner_emailaddress(codeunit_file)}"]
        for custom_argument_key, custom_argument_value in custom_arguments.items():
            args.append("--build-arg")
            args.append(f"{custom_argument_key}={custom_argument_value}")
        args = args+["--tag", f"{codeunitname_lower}:latest", "--tag", f"{codeunitname_lower}:{codeunitversion}", "--file", f"{codeunitname}/Dockerfile"]
        if not use_cache:
            args.append("--no-cache")
        args.append(".")
        codeunit_content_folder = os.path.join(codeunit_folder)
        self.__sc.run_program_argsasarray("docker", args, codeunit_content_folder, verbosity=verbosity, print_errors_as_information=True)
        artifacts_folder = GeneralUtilities.resolve_relative_path("Other/Artifacts", codeunit_folder)
        app_artifacts_folder = os.path.join(artifacts_folder, "BuildResult_OCIImage")
        GeneralUtilities.ensure_directory_does_not_exist(app_artifacts_folder)
        GeneralUtilities.ensure_directory_exists(app_artifacts_folder)
        self.__sc.run_program_argsasarray("docker", ["save", "--output", f"{codeunitname}_v{codeunitversion}.tar", f"{codeunitname_lower}:{codeunitversion}"], app_artifacts_folder, verbosity=verbosity, print_errors_as_information=True)
        self.copy_source_files_to_output_directory(build_script_file)

    @GeneralUtilities.check_arguments
    def generate_sbom_for_docker_image(self, build_script_file: str, verbosity: int, commandline_arguments: list[str]) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        codeunitname: str = Path(os.path.dirname(build_script_file)).parent.parent.name
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", str(os.path.dirname(build_script_file)))
        artifacts_folder = GeneralUtilities.resolve_relative_path("Other/Artifacts", codeunit_folder)
        codeunitname_lower = codeunitname.lower()
        sbom_folder = os.path.join(artifacts_folder, "BOM")
        codeunitversion = self.get_version_of_codeunit(os.path.join(codeunit_folder, f"{codeunitname}.codeunit.xml"))
        GeneralUtilities.ensure_directory_exists(sbom_folder)
        self.__sc.run_program_argsasarray("docker", ["sbom", "--format", "cyclonedx", f"{codeunitname_lower}:{codeunitversion}", "--output", f"{codeunitname}.{codeunitversion}.sbom.xml"], sbom_folder, verbosity=verbosity, print_errors_as_information=True)
        self.__sc.format_xml_file(sbom_folder+f"/{codeunitname}.{codeunitversion}.sbom.xml")

    @GeneralUtilities.check_arguments
    def push_docker_build_artifact(self, push_artifacts_file: str, registry: str, verbosity: int, push_readme: bool, commandline_arguments: list[str], repository_folder_name: str, remote_image_name: str = None) -> None:
        folder_of_this_file = os.path.dirname(push_artifacts_file)
        filename = os.path.basename(push_artifacts_file)
        codeunitname_regex: str = "([a-zA-Z0-9]+)"
        filename_regex: str = f"PushArtifacts\\.{codeunitname_regex}\\.py"
        if match := re.search(filename_regex, filename, re.IGNORECASE):
            codeunitname = match.group(1)
        else:
            raise ValueError(f"Expected push-artifacts-file to match the regex \"{filename_regex}\" where \"{codeunitname_regex}\" represents the codeunit-name.")
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        repository_folder = GeneralUtilities.resolve_relative_path(f"..{os.path.sep}..{os.path.sep}Submodules{os.path.sep}{repository_folder_name}", folder_of_this_file)
        codeunit_folder = os.path.join(repository_folder, codeunitname)
        artifacts_folder = self.get_artifacts_folder(repository_folder, codeunitname)
        applicationimage_folder = os.path.join(artifacts_folder, "BuildResult_OCIImage")
        image_file = self.__sc.find_file_by_extension(applicationimage_folder, "tar")
        image_filename = os.path.basename(image_file)
        codeunit_version = self.get_version_of_codeunit(os.path.join(codeunit_folder, f"{codeunitname}.codeunit.xml"))
        if remote_image_name is None:
            remote_image_name = codeunitname
        remote_image_name = remote_image_name.lower()
        local_image_name = codeunitname.lower()
        remote_repo = f"{registry}/{remote_image_name}"
        remote_image_latest = f"{remote_repo}:latest"
        remote_image_version = f"{remote_repo}:{codeunit_version}"
        GeneralUtilities.write_message_to_stdout("Load image...")
        self.__sc.run_program("docker", f"load --input {image_filename}", applicationimage_folder, verbosity=verbosity)
        GeneralUtilities.write_message_to_stdout("Tag image...")
        self.__sc.run_program("docker", f"tag {local_image_name}:{codeunit_version} {remote_image_latest}", verbosity=verbosity)
        self.__sc.run_program("docker", f"tag {local_image_name}:{codeunit_version} {remote_image_version}", verbosity=verbosity)
        GeneralUtilities.write_message_to_stdout("Push image...")
        self.__sc.run_program("docker", f"push {remote_image_latest}", verbosity=verbosity)
        self.__sc.run_program("docker", f"push {remote_image_version}", verbosity=verbosity)
        if push_readme:
            self.__sc.run_program("docker-pushrm", f"{remote_repo}", codeunit_folder, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def get_dependent_code_units(self, codeunit_file: str) -> list[str]:
        root: etree._ElementTree = etree.parse(codeunit_file)
        result = set(root.xpath('//cps:dependentcodeunit/text()', namespaces={'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'}))
        result = sorted(result)
        return result

    @GeneralUtilities.check_arguments
    def dependent_codeunit_exists(self, repository: str, codeunit: str) -> None:
        codeunit_file = f"{repository}/{codeunit}/{codeunit}.codeunit.xml"
        return os.path.isfile(codeunit_file)

    @GeneralUtilities.check_arguments
    def standardized_tasks_linting_for_docker_project(self, linting_script_file: str, verbosity: int, targetenvironmenttype: str, commandline_arguments: list[str]) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments,  verbosity)
        # TODO check if there are errors in sarif-file

    @GeneralUtilities.check_arguments
    def copy_licence_file(self, common_tasks_scripts_file: str) -> None:
        folder_of_current_file = os.path.dirname(common_tasks_scripts_file)
        license_file = GeneralUtilities.resolve_relative_path("../../License.txt", folder_of_current_file)
        target_folder = GeneralUtilities.resolve_relative_path("Artifacts/License", folder_of_current_file)
        GeneralUtilities.ensure_directory_exists(target_folder)
        shutil.copy(license_file, target_folder)

    @GeneralUtilities.check_arguments
    def take_readmefile_from_main_readmefile_of_repository(self, common_tasks_scripts_file: str) -> None:
        folder_of_current_file = os.path.dirname(common_tasks_scripts_file)
        source_file = GeneralUtilities.resolve_relative_path("../../ReadMe.md", folder_of_current_file)
        target_file = GeneralUtilities.resolve_relative_path("../ReadMe.md", folder_of_current_file)
        GeneralUtilities.ensure_file_does_not_exist(target_file)
        shutil.copyfile(source_file, target_file)

    @GeneralUtilities.check_arguments
    def standardized_tasks_do_common_tasks(self, common_tasks_scripts_file: str, codeunit_version: str, verbosity: int,  targetenvironmenttype: str,  clear_artifacts_folder: bool, additional_arguments_file: str, assume_dependent_codeunits_are_already_built: bool, commandline_arguments: list[str]) -> None:
        additional_arguments_file = self.get_additionalargumentsfile_from_commandline_arguments(commandline_arguments, additional_arguments_file)
        target_environmenttype = self.get_targetenvironmenttype_from_commandline_arguments(commandline_arguments, targetenvironmenttype)  # pylint: disable=unused-variable
        # assume_dependent_codeunits_are_already_built = self.get_assume_dependent_codeunits_are_already_built_from_commandline_arguments(commandline_arguments, assume_dependent_codeunits_are_already_built)
        if commandline_arguments is None:
            raise ValueError('The "commandline_arguments"-parameter is not defined.')
        if len(commandline_arguments) == 0:
            raise ValueError('An empty array as argument for the "commandline_arguments"-parameter is not valid.')
        commandline_arguments = commandline_arguments[1:]
        repository_folder: str = str(Path(os.path.dirname(common_tasks_scripts_file)).parent.parent.absolute())
        self.__sc.assert_is_git_repository(repository_folder)
        codeunit_name: str = str(os.path.basename(Path(os.path.dirname(common_tasks_scripts_file)).parent.absolute()))
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        project_version = self.get_version_of_project(repository_folder)
        codeunit_folder = os.path.join(repository_folder, codeunit_name)

        # check codeunit-conformity
        # TODO check if foldername=="<codeunitname>[.codeunit.xml]" == <codeunitname> in file
        supported_codeunitspecificationversion = "2.9.4"  # should always be the latest version of the ProjectTemplates-repository
        codeunit_file = os.path.join(codeunit_folder, f"{codeunit_name}.codeunit.xml")
        if not os.path.isfile(codeunit_file):
            raise ValueError(f'Codeunitfile "{codeunit_file}" does not exist.')
        # TODO implement usage of self.reference_latest_version_of_xsd_when_generating_xml
        namespaces = {'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure',  'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
        root: etree._ElementTree = etree.parse(codeunit_file)

        # check codeunit-spcecification-version
        try:
            codeunit_file_version = root.xpath('//cps:codeunit/@codeunitspecificationversion', namespaces=namespaces)[0]
            if codeunit_file_version != supported_codeunitspecificationversion:
                raise ValueError(f"ScriptCollection only supports processing codeunits with codeunit-specification-version={supported_codeunitspecificationversion}.")
            schemaLocation = root.xpath('//cps:codeunit/@xsi:schemaLocation', namespaces=namespaces)[0]
            xmlschema.validate(codeunit_file, schemaLocation)
            # TODO check if the properties codeunithastestablesourcecode, codeunithasupdatabledependencies, throwexceptionifcodeunitfilecannotbevalidated, developmentState and description exist and the values are valid
        except Exception as exception:
            if self.codeunit_throws_exception_if_codeunitfile_is_not_validatable(codeunit_file):
                raise exception
            else:
                GeneralUtilities.write_message_to_stderr(f'Warning: Codeunitfile "{codeunit_file}" can not be validated due to the following exception:')
                GeneralUtilities.write_exception_to_stderr(exception)

        # check codeunit-name
        codeunit_name_in_codeunit_file = root.xpath('//cps:codeunit/cps:name/text()', namespaces=namespaces)[0]
        if codeunit_name != codeunit_name_in_codeunit_file:
            raise ValueError(f"The folder-name ('{codeunit_name}') is not equal to the codeunit-name ('{codeunit_name_in_codeunit_file}').")

        # check owner-name
        codeunit_ownername_in_codeunit_file = self. get_codeunit_owner_name(codeunit_file)
        GeneralUtilities.assert_condition(GeneralUtilities.string_has_content(codeunit_ownername_in_codeunit_file), "No valid name for codeunitowner given.")

        # check owner-emailaddress
        codeunit_owneremailaddress_in_codeunit_file = self.get_codeunit_owner_emailaddress(codeunit_file)
        GeneralUtilities.assert_condition(GeneralUtilities.string_has_content(codeunit_owneremailaddress_in_codeunit_file), "No valid email-address for codeunitowner given.")

        # check development-state
        developmentstate = root.xpath('//cps:properties/@developmentstate', namespaces=namespaces)[0]
        developmentstate_active = "Active development"
        developmentstate_maintenance = "Maintenance-updates only"
        developmentstate_inactive = "Inactive"
        GeneralUtilities.assert_condition(developmentstate in (developmentstate_active, developmentstate_maintenance, developmentstate_inactive), f"Invalid development-state. Must be '{developmentstate_active}' or '{developmentstate_maintenance}' or '{developmentstate_inactive}' but was '{developmentstate}'.")

        # check for mandatory files
        files = ["Other/Build/Build.py", "Other/QualityCheck/Linting.py", "Other/Reference/GenerateReference.py"]
        if self.codeunit_has_testable_sourcecode(codeunit_file):
            # TODO check if the testsettings-section appears in the codeunit-file
            files.append("Other/QualityCheck/RunTestcases.py")
        if self.codeunit_has_updatable_dependencies(codeunit_file):
            # TODO check if the updatesettings-section appears in the codeunit-file
            files.append("Other/UpdateDependencies.py")
        for file in files:
            combined_file = os.path.join(codeunit_folder, file)
            if not os.path.isfile(combined_file):
                raise ValueError(f'The mandatory file "{file}" does not exist in the codeunit-folder.')

        if os.path.isfile(os.path.join(codeunit_folder, "Other", "requirements.txt")):
            self.install_requirementstxt_for_codeunit(codeunit_folder, verbosity)

        # check developer
        if self.validate_developers_of_repository:
            expected_authors: list[tuple[str, str]] = []
            expected_authors_in_xml = root.xpath('//cps:codeunit/cps:developerteam/cps:developer', namespaces=namespaces)
            for expected_author in expected_authors_in_xml:
                author_name = expected_author.xpath('./cps:developername/text()', namespaces=namespaces)[0]
                author_emailaddress = expected_author.xpath('./cps:developeremailaddress/text()', namespaces=namespaces)[0]
                expected_authors.append((author_name, author_emailaddress))
            actual_authors: list[tuple[str, str]] = self.__sc.get_all_authors_and_committers_of_repository(repository_folder, codeunit_name, verbosity)
            # TODO refactor this check to only check commits which are behind this but which are not already on main
            # TODO verify also if the commit is signed by a valid key of the author
            for actual_author in actual_authors:
                if not (actual_author) in expected_authors:
                    actual_author_formatted = f"{actual_author[0]} <{actual_author[1]}>"
                    raise ValueError(f'Author/Comitter "{actual_author_formatted}" is not in the codeunit-developer-team. If {actual_author} is a authorized developer for this codeunit you should consider defining this in the codeunit-file or adapting the name using a .mailmap-file (see https://git-scm.com/docs/gitmailmap). The developer-team-check can also be disabled using the property validate_developers_of_repository.')

        dependent_codeunits = self.get_dependent_code_units(codeunit_file)
        for dependent_codeunit in dependent_codeunits:
            if not self.dependent_codeunit_exists(repository_folder, dependent_codeunit):
                raise ValueError(f"Codeunit {codeunit_name} does have dependent codeunit {dependent_codeunit} which does not exist.")

        # TODO implement cycle-check for dependent codeunits

        # clear previously builded artifacts if desired:
        if clear_artifacts_folder:
            artifacts_folder = os.path.join(codeunit_folder, "Other", "Artifacts")
            GeneralUtilities.ensure_directory_does_not_exist(artifacts_folder)

        # get artifacts from dependent codeunits
        # if assume_dependent_codeunits_are_already_built:
        #    self.build_dependent_code_units(repository_folder, codeunit_name, verbosity, target_environmenttype, additional_arguments_file, commandline_arguments)
        self.copy_artifacts_from_dependent_code_units(repository_folder, codeunit_name)

        # update codeunit-version
        self.update_version_of_codeunit(common_tasks_scripts_file, codeunit_version)

        # set project version
        package_json_file = os.path.join(repository_folder, "package.json")  # TDOO move this to a general project-specific (and codeunit-independent-script)
        if os.path.isfile(package_json_file):
            package_json_data: str = None
            with open(package_json_file, "r", encoding="utf-8") as f1:
                package_json_data = json.load(f1)
                package_json_data["version"] = project_version
            with open(package_json_file, "w", encoding="utf-8") as f2:
                json.dump(package_json_data, f2, indent=2)
            GeneralUtilities.write_text_to_file(package_json_file, GeneralUtilities.read_text_from_file(package_json_file).replace("\r", ""))

        # set default constants
        self.set_default_constants(os.path.join(codeunit_folder))

        # Copy changelog-file
        changelog_folder = os.path.join(repository_folder, "Other", "Resources", "Changelog")
        changelog_file = os.path.join(changelog_folder, f"v{project_version}.md")
        target_folder = os.path.join(codeunit_folder, "Other", "Artifacts", "Changelog")
        GeneralUtilities.ensure_directory_exists(target_folder)
        shutil.copy(changelog_file, target_folder)

        # Hints-file
        hints_file = os.path.join(codeunit_folder, "Other", "Reference", "ReferenceContent", "Hints.md")
        if not os.path.isfile(hints_file):
            raise ValueError(f"Hints-file '{hints_file}' does not exist.")

        # Copy license-file
        self.copy_licence_file(common_tasks_scripts_file)

        # Generate diff-report
        self.generate_diff_report(repository_folder, codeunit_name, codeunit_version)

    @GeneralUtilities.check_arguments
    def __suport_information_exists(self, repository_folder: str, version_of_product: str) -> bool:
        self.__sc.assert_is_git_repository(repository_folder)
        folder = os.path.join(repository_folder, "Other", "Resources", "Support")
        file = os.path.join(folder, "InformationAboutSupportedVersions.csv")
        if not os.path.isfile(file):
            return False
        entries = GeneralUtilities.read_csv_file(file, True)
        for entry in entries:
            if entry[0] == version_of_product:
                return True
        return False

    @GeneralUtilities.check_arguments
    def get_versions(self, repository_folder: str) -> list[(str, datetime, datetime)]:
        self.__sc.assert_is_git_repository(repository_folder)
        folder = os.path.join(repository_folder, "Other", "Resources", "Support")
        file = os.path.join(folder, "InformationAboutSupportedVersions.csv")
        result: list[str] = list[(str, datetime, datetime)]()
        if not os.path.isfile(file):
            return result
        entries = GeneralUtilities.read_csv_file(file, True)
        for entry in entries:
            result.append((entry[0], GeneralUtilities.string_to_datetime(entry[1]), GeneralUtilities.string_to_datetime(entry[2])))
        return result

    @GeneralUtilities.check_arguments
    def get_supported_versions(self, repository_folder: str, moment: datetime) -> list[(str, datetime, datetime)]:
        self.__sc.assert_is_git_repository(repository_folder)
        result: list[str] = list[(str, datetime, datetime)]()
        for entry in self.get_versions(repository_folder):
            if entry[1] <= moment and moment <= entry[2]:
                result.append(entry)
        return result

    @GeneralUtilities.check_arguments
    def get_unsupported_versions(self, repository_folder: str, moment: datetime) -> list[(str, datetime, datetime)]:
        self.__sc.assert_is_git_repository(repository_folder)
        result: list[str] = list[(str, datetime, datetime)]()
        for entry in self.get_versions(repository_folder):
            if not (entry[1] <= moment and moment <= entry[2]):
                result.append(entry)
        return result

    @GeneralUtilities.check_arguments
    def mark_current_version_as_supported(self, repository_folder: str, version_of_product: str, supported_from: datetime, supported_until: datetime):
        self.__sc.assert_is_git_repository(repository_folder)
        if self.__suport_information_exists(repository_folder, version_of_product):
            raise ValueError(f"Version-support for v{version_of_product} already defined.")
        folder = os.path.join(repository_folder, "Other", "Resources", "Support")
        GeneralUtilities.ensure_directory_exists(folder)
        file = os.path.join(folder, "InformationAboutSupportedVersions.csv")
        if not os.path.isfile(file):
            GeneralUtilities.ensure_file_exists(file)
            GeneralUtilities.append_line_to_file(file, "Version;SupportBegin;SupportEnd")
        GeneralUtilities.append_line_to_file(file, f"{version_of_product};{GeneralUtilities.datetime_to_string(supported_from)};{GeneralUtilities.datetime_to_string(supported_until)}")

    @GeneralUtilities.check_arguments
    def get_codeunit_owner_name(self, codeunit_file: str) -> None:
        namespaces = {'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure',  'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
        root: etree._ElementTree = etree.parse(codeunit_file)
        result = root.xpath('//cps:codeunit/cps:codeunitownername/text()', namespaces=namespaces)[0]
        return result

    @GeneralUtilities.check_arguments
    def get_codeunit_owner_emailaddress(self, codeunit_file: str) -> None:
        namespaces = {'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
        root: etree._ElementTree = etree.parse(codeunit_file)
        result = root.xpath('//cps:codeunit/cps:codeunitowneremailaddress/text()', namespaces=namespaces)[0]
        return result

    @GeneralUtilities.check_arguments
    def generate_diff_report(self, repository_folder: str, codeunit_name: str, current_version: str) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        codeunit_folder = os.path.join(repository_folder, codeunit_name)
        target_folder = GeneralUtilities.resolve_relative_path("Other/Artifacts/DiffReport", codeunit_folder)
        GeneralUtilities.ensure_directory_does_not_exist(target_folder)
        GeneralUtilities.ensure_directory_exists(target_folder)
        target_file_light = os.path.join(target_folder, "DiffReport.html").replace("\\", "/")
        target_file_dark = os.path.join(target_folder, "DiffReportDark.html").replace("\\", "/")
        src = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # hash/id of empty git-tree
        src_prefix = "Begin"
        if self.__sc.get_current_git_branch_has_tag(repository_folder):
            latest_tag = self.__sc.get_latest_git_tag(repository_folder)
            src = self.__sc.git_get_commitid_of_tag(repository_folder, latest_tag)
            src_prefix = latest_tag
        dst = "HEAD"
        dst_prefix = f"v{current_version}"

        temp_file = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        try:
            GeneralUtilities.ensure_file_does_not_exist(temp_file)
            GeneralUtilities.write_text_to_file(temp_file, self.__sc.run_program("git", f'--no-pager diff --src-prefix={src_prefix}/ --dst-prefix={dst_prefix}/ {src} {dst} -- {codeunit_name}', repository_folder)[1])
            self.__sc.run_program_argsasarray("pygmentize", ['-l', 'diff', '-f', 'html', '-O', 'full', '-o', target_file_light, '-P', 'style=default', temp_file], repository_folder)
            self.__sc.run_program_argsasarray("pygmentize", ['-l', 'diff', '-f', 'html', '-O', 'full', '-o', target_file_dark, '-P', 'style=github-dark', temp_file], repository_folder)
        finally:
            GeneralUtilities.ensure_file_does_not_exist(temp_file)

    @GeneralUtilities.check_arguments
    def get_version_of_project(self, repository_folder: str) -> str:
        self.__sc.assert_is_git_repository(repository_folder)
        return self.__sc.get_semver_version_from_gitversion(repository_folder)

    @GeneralUtilities.check_arguments
    def replace_common_variables_in_nuspec_file(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        codeunit_version = self.get_version_of_codeunit_folder(codeunit_folder)
        nuspec_file = os.path.join(codeunit_folder, "Other", "Build", f"{codeunit_name}.nuspec")
        self.__sc.replace_version_in_nuspec_file(nuspec_file, codeunit_version)

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_angular_codeunit(self, build_script_file: str, build_environment_target_type: str, verbosity: int, commandline_arguments: list[str]) -> None:
        build_script_folder = os.path.dirname(build_script_file)
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", build_script_folder)
        GeneralUtilities.ensure_directory_does_not_exist(f"{codeunit_folder}/.angular")
        self.standardized_tasks_build_for_node_codeunit(build_script_file, build_environment_target_type, verbosity, commandline_arguments)

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_for_node_codeunit(self, build_script_file: str, build_environment_target_type: str, verbosity: int, commandline_arguments: list[str]) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        build_script_folder = os.path.dirname(build_script_file)
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", build_script_folder)
        self.run_with_epew("npm", f"run build-{build_environment_target_type}", codeunit_folder, verbosity=verbosity)
        self.standardized_tasks_build_bom_for_node_project(codeunit_folder, verbosity, commandline_arguments)
        self.copy_source_files_to_output_directory(build_script_file)

    @GeneralUtilities.check_arguments
    def standardized_tasks_build_bom_for_node_project(self, codeunit_folder: str, verbosity: int, commandline_arguments: list[str]) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        relative_path_to_bom_file = f"Other/Artifacts/BOM/{os.path.basename(codeunit_folder)}.{self.get_version_of_codeunit_folder(codeunit_folder)}.sbom.xml"
        self.run_with_epew("cyclonedx-npm", f"--output-format xml --output-file {relative_path_to_bom_file}", codeunit_folder, verbosity=verbosity)
        self.__sc.format_xml_file(codeunit_folder+"/"+relative_path_to_bom_file)

    @GeneralUtilities.check_arguments
    def standardized_tasks_linting_for_angular_codeunit(self, linting_script_file: str, verbosity: int, build_environment_target_type: str, commandline_arguments: list[str]) -> None:
        self.standardized_tasks_linting_for_node_codeunit(linting_script_file, verbosity, build_environment_target_type, commandline_arguments)

    @GeneralUtilities.check_arguments
    def standardized_tasks_linting_for_node_codeunit(self, linting_script_file: str, verbosity: int, build_environment_target_type: str, commandline_arguments: list[str]) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        build_script_folder = os.path.dirname(linting_script_file)
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", build_script_folder)
        self.run_with_epew("ng", "lint", codeunit_folder, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def standardized_tasks_run_testcases_for_flutter_project_in_common_project_structure(self, script_file: str, verbosity: int, args: list[str], package_name: str, build_environment_target_type: str, generate_badges: bool):
        codeunit_folder = GeneralUtilities.resolve_relative_path("../../..", script_file)
        repository_folder = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        src_folder = GeneralUtilities.resolve_relative_path(package_name, codeunit_folder)
        verbosity = self.get_verbosity_from_commandline_arguments(args, verbosity)
        self.run_with_epew("flutter", "test --coverage", src_folder, verbosity)
        test_coverage_folder_relative = "Other/Artifacts/TestCoverage"
        test_coverage_folder = GeneralUtilities.resolve_relative_path(test_coverage_folder_relative, codeunit_folder)
        GeneralUtilities.ensure_directory_exists(test_coverage_folder)
        coverage_file_relative = f"{test_coverage_folder_relative}/TestCoverage.xml"
        coverage_file = GeneralUtilities.resolve_relative_path(coverage_file_relative, codeunit_folder)
        self.run_with_epew("lcov_cobertura", f"coverage/lcov.info --base-dir . --excludes test --output ../{coverage_file_relative} --demangle", src_folder, verbosity)
        content = GeneralUtilities.read_text_from_file(coverage_file)
        content = re.sub('<![^<]+>', '', content)
        content = re.sub('\\\\', '/', content)
        content = re.sub('\\ name=\\"lib\\"', '', content)
        content = re.sub('<package ', f'<package name="{codeunit_name}" ', content)
        content = re.sub('\\ filename=\\"lib/', f' filename="{package_name}/lib/', content)
        GeneralUtilities.write_text_to_file(coverage_file, content)
        self.run_testcases_common_post_task(repository_folder, codeunit_name, verbosity, generate_badges, build_environment_target_type, args)

    @GeneralUtilities.check_arguments
    def standardized_tasks_run_testcases_for_angular_codeunit(self, runtestcases_script_file: str, build_environment_target_type: str, generate_badges: bool, verbosity: int, commandline_arguments: list[str]) -> None:
        # prepare
        codeunit_name: str = os.path.basename(str(Path(os.path.dirname(runtestcases_script_file)).parent.parent.absolute()))
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", os.path.dirname(runtestcases_script_file))
        repository_folder = os.path.dirname(codeunit_folder)

        # run testcases
        self.standardized_tasks_run_testcases_for_node_codeunit(runtestcases_script_file, build_environment_target_type, generate_badges, verbosity, commandline_arguments)

        # rename file
        coverage_folder = os.path.join(codeunit_folder, "Other", "Artifacts", "TestCoverage")
        target_file = os.path.join(coverage_folder, "TestCoverage.xml")
        GeneralUtilities.ensure_file_does_not_exist(target_file)
        os.rename(os.path.join(coverage_folder, "cobertura-coverage.xml"), target_file)
        self.__rename_packagename_in_coverage_file(target_file, codeunit_name)

        # adapt backslashs to slashs
        content = GeneralUtilities.read_text_from_file(target_file)
        content = re.sub('\\\\', '/', content)
        GeneralUtilities.write_text_to_file(target_file, content)

        # aggregate packages in testcoverage-file
        roottree: etree._ElementTree = etree.parse(target_file)
        existing_classes = list(roottree.xpath('//coverage/packages/package/classes/class'))

        old_packages_list = roottree.xpath('//coverage/packages/package')
        for package in old_packages_list:
            package.getparent().remove(package)

        root = roottree.getroot()
        packages_element = root.find("packages")
        package_element = etree.SubElement(packages_element, "package")
        package_element.attrib['name'] = codeunit_name
        package_element.attrib['lines-valid'] = root.attrib["lines-valid"]
        package_element.attrib['lines-covered'] = root.attrib["lines-covered"]
        package_element.attrib['line-rate'] = root.attrib["line-rate"]
        package_element.attrib['branches-valid'] = root.attrib["branches-valid"]
        package_element.attrib['branches-covered'] = root.attrib["branches-covered"]
        package_element.attrib['branch-rate'] = root.attrib["branch-rate"]
        package_element.attrib['timestamp'] = root.attrib["timestamp"]
        package_element.attrib['complexity'] = root.attrib["complexity"]

        classes_element = etree.SubElement(package_element, "classes")

        for existing_class in existing_classes:
            classes_element.append(existing_class)

        result = etree.tostring(roottree, pretty_print=True).decode("utf-8")
        GeneralUtilities.write_text_to_file(target_file, result)

        # post tasks
        self.run_testcases_common_post_task(repository_folder, codeunit_name, verbosity, generate_badges, build_environment_target_type, commandline_arguments)

    @GeneralUtilities.check_arguments
    def standardized_tasks_run_testcases_for_node_codeunit(self, runtestcases_script_file: str, build_environment_target_type: str, generate_badges: bool, verbosity: int, commandline_arguments: list[str]) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", os.path.dirname(runtestcases_script_file))
        self.run_with_epew("npm", f"run test-{build_environment_target_type}", codeunit_folder, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def __rename_packagename_in_coverage_file(self, file: str, codeunit_name: str) -> None:
        root: etree._ElementTree = etree.parse(file)
        packages = root.xpath('//coverage/packages/package')
        for package in packages:
            package.attrib['name'] = codeunit_name
        result = etree.tostring(root).decode("utf-8")
        GeneralUtilities.write_text_to_file(file, result)

    @GeneralUtilities.check_arguments
    def do_npm_install(self, package_json_folder: str, force: bool, verbosity: int = 1) -> None:
        argument1 = "install"
        if force:
            argument1 = f"{argument1} --force"
        self.run_with_epew("npm", argument1, package_json_folder, verbosity=verbosity)

        argument2 = "install --package-lock-only"
        if force:
            argument2 = f"{argument2} --force"
        self.run_with_epew("npm", argument2, package_json_folder, verbosity=verbosity)

        argument3 = "clean-install"
        if force:
            argument3 = f"{argument3} --force"
        self.run_with_epew("npm", argument3, package_json_folder, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def run_with_epew(self, program: str, argument: str = "", working_directory: str = None, verbosity: int = 1, print_errors_as_information: bool = False, log_file: str = None, timeoutInSeconds: int = 600, addLogOverhead: bool = False, title: str = None, log_namespace: str = "", arguments_for_log:  list[str] = None, throw_exception_if_exitcode_is_not_zero: bool = True, custom_argument: object = None, interactive: bool = False) -> tuple[int, str, str, int]:
        sc: ScriptCollectionCore = ScriptCollectionCore()
        sc.program_runner = ProgramRunnerEpew()
        return sc.run_program(program, argument, working_directory, verbosity, print_errors_as_information, log_file, timeoutInSeconds, addLogOverhead, title, log_namespace, arguments_for_log, throw_exception_if_exitcode_is_not_zero, custom_argument, interactive)

    @GeneralUtilities.check_arguments
    def set_default_constants(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        self.set_constant_for_commitid(codeunit_folder)
        self.set_constant_for_commitdate(codeunit_folder)
        self.set_constant_for_codeunitname(codeunit_folder)
        self.set_constant_for_codeunitversion(codeunit_folder)
        self.set_constant_for_codeunitmajorversion(codeunit_folder)
        self.set_constant_for_description(codeunit_folder)

    @GeneralUtilities.check_arguments
    def set_constant_for_commitid(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        repository = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        commit_id = self.__sc.git_get_commit_id(repository)
        self.set_constant(codeunit_folder, "CommitId", commit_id)

    @GeneralUtilities.check_arguments
    def set_constant_for_commitdate(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        repository = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        commit_date: datetime = self.__sc.git_get_commit_date(repository)
        self.set_constant(codeunit_folder, "CommitDate", GeneralUtilities.datetime_to_string(commit_date))

    @GeneralUtilities.check_arguments
    def set_constant_for_codeunitname(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name: str = os.path.basename(codeunit_folder)
        self.set_constant(codeunit_folder, "CodeUnitName", codeunit_name)

    @GeneralUtilities.check_arguments
    def set_constant_for_codeunitversion(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_version: str = self.get_version_of_codeunit_folder(codeunit_folder)
        self.set_constant(codeunit_folder, "CodeUnitVersion", codeunit_version)

    @GeneralUtilities.check_arguments
    def set_constant_for_codeunitmajorversion(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_version: str = self.get_version_of_codeunit_folder(codeunit_folder)
        major_version = int(codeunit_version.split(".")[0])
        self.set_constant(codeunit_folder, "CodeUnitMajorVersion", str(major_version))

    @GeneralUtilities.check_arguments
    def set_constant_for_description(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name: str = os.path.basename(codeunit_folder)
        codeunit_description: str = self.get_codeunit_description(f"{codeunit_folder}/{codeunit_name}.codeunit.xml")
        self.set_constant(codeunit_folder, "CodeUnitDescription", codeunit_description)

    @GeneralUtilities.check_arguments
    def set_constant(self, codeunit_folder: str, constantname: str, constant_value: str, documentationsummary: str = None, constants_valuefile: str = None) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        if documentationsummary is None:
            documentationsummary = GeneralUtilities.empty_string
        constants_folder = os.path.join(codeunit_folder, "Other", "Resources", "Constants")
        GeneralUtilities.ensure_directory_exists(constants_folder)
        constants_metafile = os.path.join(constants_folder, f"{constantname}.constant.xml")
        if constants_valuefile is None:
            constants_valuefile_folder = constants_folder
            constants_valuefile_name = f"{constantname}.value.txt"
            constants_valuefiler_reference = f"./{constants_valuefile_name}"
        else:
            constants_valuefile_folder = os.path.dirname(constants_valuefile)
            constants_valuefile_name = os.path.basename(constants_valuefile)
            constants_valuefiler_reference = os.path.join(constants_valuefile_folder, constants_valuefile_name)

        # TODO implement usage of self.reference_latest_version_of_xsd_when_generating_xml
        GeneralUtilities.write_text_to_file(constants_metafile, f"""<?xml version="1.0" encoding="UTF-8" ?>
<cps:constant xmlns:cps="https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure" constantspecificationversion="1.1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/raw/main/Conventions/RepositoryStructure/CommonProjectStructure/constant.xsd">
    <cps:name>{constantname}</cps:name>
    <cps:documentationsummary>{documentationsummary}</cps:documentationsummary>
    <cps:path>{constants_valuefiler_reference}</cps:path>
</cps:constant>""")
        # TODO validate generated xml against xsd
        GeneralUtilities.write_text_to_file(os.path.join(constants_valuefile_folder, constants_valuefile_name), constant_value)

    @GeneralUtilities.check_arguments
    def get_constant_value(self, source_codeunit_folder: str, constant_name: str) -> str:
        self.assert_is_codeunit_folder(source_codeunit_folder)
        value_file_relative = self.__get_constant_helper(source_codeunit_folder, constant_name, "path")
        value_file = GeneralUtilities.resolve_relative_path(value_file_relative, os.path.join(source_codeunit_folder, "Other", "Resources", "Constants"))
        return GeneralUtilities.read_text_from_file(value_file)

    @GeneralUtilities.check_arguments
    def get_constant_documentation(self, source_codeunit_folder: str, constant_name: str) -> str:
        self.assert_is_codeunit_folder(source_codeunit_folder)
        return self.__get_constant_helper(source_codeunit_folder, constant_name, "documentationsummary")

    @GeneralUtilities.check_arguments
    def __get_constant_helper(self, source_codeunit_folder: str, constant_name: str, propertyname: str) -> str:
        self.assert_is_codeunit_folder(source_codeunit_folder)
        root: etree._ElementTree = etree.parse(os.path.join(source_codeunit_folder, "Other", "Resources", "Constants", f"{constant_name}.constant.xml"))
        results = root.xpath(f'//cps:{propertyname}/text()', namespaces={
            'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure'
        })
        length = len(results)
        if (length == 0):
            return ""
        elif length == 1:
            return results[0]
        else:
            raise ValueError("Too many results found.")

    @GeneralUtilities.check_arguments
    def copy_development_certificate_to_default_development_directory(self, codeunit_folder: str, build_environment: str, domain: str = None, certificate_resource_name: str = "DevelopmentCertificate") -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        if build_environment != "Productive":
            codeunit_name: str = os.path.basename(codeunit_folder)
            if domain is None:
                domain = f"{codeunit_name}.test.local".lower()

            src_folder = os.path.join(codeunit_folder, "Other", "Resources", certificate_resource_name)
            src_file_pfx = os.path.join(src_folder, f"{codeunit_name}{certificate_resource_name}.pfx")
            src_file_psw = os.path.join(src_folder, f"{codeunit_name}{certificate_resource_name}.password")

            trg_folder = os.path.join(codeunit_folder, "Other", "Workspace", "Configuration", "Certificates")
            trg_file_pfx = os.path.join(trg_folder, f"{domain}.pfx")
            trg_file_psw = os.path.join(trg_folder, f"{domain}.password")

            GeneralUtilities.assert_file_exists(src_file_pfx)
            GeneralUtilities.assert_file_exists(src_file_psw)
            GeneralUtilities.ensure_file_does_not_exist(trg_file_pfx)
            GeneralUtilities.ensure_file_does_not_exist(trg_file_psw)

            GeneralUtilities.ensure_directory_exists(trg_folder)

            GeneralUtilities.ensure_directory_exists(trg_folder)
            shutil.copyfile(src_file_pfx, trg_file_pfx)
            shutil.copyfile(src_file_psw, trg_file_psw)

    @GeneralUtilities.check_arguments
    def set_constants_for_certificate_public_information(self, codeunit_folder: str, source_constant_name: str = "DevelopmentCertificate", domain: str = None) -> None:
        """Expects a certificate-resource and generates a constant for its public information"""
        self.assert_is_codeunit_folder(codeunit_folder)
        certificate_file = os.path.join(codeunit_folder, "Other", "Resources", source_constant_name, f"{source_constant_name}.crt")
        with open(certificate_file, encoding="utf-8") as text_wrapper:
            certificate = crypto.load_certificate(crypto.FILETYPE_PEM, text_wrapper.read())
        certificate_publickey = crypto.dump_publickey(crypto.FILETYPE_PEM, certificate.get_pubkey()).decode("utf-8")
        self.set_constant(codeunit_folder, source_constant_name+"PublicKey", certificate_publickey)

    @GeneralUtilities.check_arguments
    def set_constants_for_certificate_private_information(self, codeunit_folder: str) -> None:
        """Expects a certificate-resource and generates a constant for its sensitive information in hex-format"""
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        resource_name: str = "DevelopmentCertificate"
        filename: str = codeunit_name+"DevelopmentCertificate"
        self.generate_constant_from_resource_by_filename(codeunit_folder, resource_name, f"{filename}.pfx", "PFX")
        self.generate_constant_from_resource_by_filename(codeunit_folder, resource_name, f"{filename}.password", "Password")

    @GeneralUtilities.check_arguments
    def generate_constant_from_resource_by_filename(self, codeunit_folder: str, resource_name: str, filename: str, constant_name: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        certificate_resource_folder = GeneralUtilities.resolve_relative_path(f"Other/Resources/{resource_name}", codeunit_folder)
        resource_file = os.path.join(certificate_resource_folder, filename)
        resource_file_content = GeneralUtilities.read_binary_from_file(resource_file)
        resource_file_as_hex = resource_file_content.hex()
        self.set_constant(codeunit_folder, f"{resource_name}{constant_name}Hex", resource_file_as_hex)

    @GeneralUtilities.check_arguments
    def generate_constant_from_resource_by_extension(self, codeunit_folder: str, resource_name: str, extension: str, constant_name: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        certificate_resource_folder = GeneralUtilities.resolve_relative_path(f"Other/Resources/{resource_name}", codeunit_folder)
        resource_file = self.__sc.find_file_by_extension(certificate_resource_folder, extension)
        resource_file_content = GeneralUtilities.read_binary_from_file(resource_file)
        resource_file_as_hex = resource_file_content.hex()
        self.set_constant(codeunit_folder, f"{resource_name}{constant_name}Hex", resource_file_as_hex)

    @GeneralUtilities.check_arguments
    def copy_constant_from_dependent_codeunit(self, codeunit_folder: str, constant_name: str, source_codeunit_name: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        source_codeunit_folder: str = GeneralUtilities.resolve_relative_path(f"../{source_codeunit_name}", codeunit_folder)
        value = self.get_constant_value(source_codeunit_folder, constant_name)
        documentation = self.get_constant_documentation(source_codeunit_folder, constant_name)
        self.set_constant(codeunit_folder, constant_name, value, documentation)

    @GeneralUtilities.check_arguments
    def copy_resources_from_dependent_codeunit(self, codeunit_folder: str, resource_name: str, source_codeunit_name: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        source_folder: str = GeneralUtilities.resolve_relative_path(f"../{source_codeunit_name}/Other/Resources/{resource_name}", codeunit_folder)
        target_folder: str = GeneralUtilities.resolve_relative_path(f"Other/Resources/{resource_name}", codeunit_folder)
        GeneralUtilities.ensure_directory_does_not_exist(target_folder)
        shutil.copytree(source_folder, target_folder)

    @GeneralUtilities.check_arguments
    def copy_resources_from_global_project_resources(self, codeunit_folder: str, resource_name: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        source_folder: str = GeneralUtilities.resolve_relative_path(f"../Other/Resources/{resource_name}", codeunit_folder)
        target_folder: str = GeneralUtilities.resolve_relative_path(f"Other/Resources/{resource_name}", codeunit_folder)
        GeneralUtilities.ensure_directory_does_not_exist(target_folder)
        shutil.copytree(source_folder, target_folder)

    @GeneralUtilities.check_arguments
    def generate_openapi_file(self, buildscript_file: str, runtime: str, verbosity: int, commandline_arguments: list[str], swagger_document_name: str = "APISpecification") -> None:
        GeneralUtilities.write_message_to_stdout("Generate OpenAPI-specification-file...")
        codeunitname = os.path.basename(str(Path(os.path.dirname(buildscript_file)).parent.parent.absolute()))
        repository_folder = str(Path(os.path.dirname(buildscript_file)).parent.parent.parent.absolute())
        codeunit_folder = os.path.join(repository_folder, codeunitname)
        self.assert_is_codeunit_folder(codeunit_folder)
        artifacts_folder = os.path.join(codeunit_folder, "Other", "Artifacts")
        GeneralUtilities.ensure_directory_exists(os.path.join(artifacts_folder, "APISpecification"))
        verbosity = self.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        codeunit_version = self.get_version_of_codeunit_folder(codeunit_folder)

        versioned_api_spec_file = f"APISpecification/{codeunitname}.v{codeunit_version}.api.json"
        self.__sc.run_program("swagger", f"tofile --output {versioned_api_spec_file} BuildResult_DotNet_{runtime}/{codeunitname}.dll {swagger_document_name}", artifacts_folder, verbosity=verbosity)
        api_file: str = os.path.join(artifacts_folder, versioned_api_spec_file)
        shutil.copyfile(api_file, os.path.join(artifacts_folder, f"APISpecification/{codeunitname}.latest.api.json"))

        resources_folder = os.path.join(codeunit_folder, "Other", "Resources")
        GeneralUtilities.ensure_directory_exists(resources_folder)
        resources_apispec_folder = os.path.join(resources_folder, "APISpecification")
        GeneralUtilities.ensure_directory_exists(resources_apispec_folder)
        resource_target_file = os.path.join(resources_apispec_folder, f"{codeunitname}.api.json")
        GeneralUtilities.ensure_file_does_not_exist(resource_target_file)
        shutil.copyfile(api_file, resource_target_file)

        with open(api_file, encoding="utf-8") as api_file_content:
            reloaded_json = json.load(api_file_content)

            yamlfile1: str = str(os.path.join(artifacts_folder, f"APISpecification/{codeunitname}.v{codeunit_version}.api.yaml"))
            GeneralUtilities.ensure_file_does_not_exist(yamlfile1)
            GeneralUtilities.ensure_file_exists(yamlfile1)
            with open(yamlfile1, "w+", encoding="utf-8") as yamlfile:
                yaml.dump(reloaded_json, yamlfile, allow_unicode=True)

            yamlfile2: str = str(os.path.join(artifacts_folder, f"APISpecification/{codeunitname}.latest.api.yaml"))
            GeneralUtilities.ensure_file_does_not_exist(yamlfile2)
            shutil.copyfile(yamlfile1, yamlfile2)

            yamlfile3: str = str(os.path.join(resources_apispec_folder, f"{codeunitname}.api.yaml"))
            GeneralUtilities.ensure_file_does_not_exist(yamlfile3)
            shutil.copyfile(yamlfile1, yamlfile3)

    @GeneralUtilities.check_arguments
    def get_latest_version_of_openapigenerator(self) -> None:
        github_api_releases_link = "https://api.github.com/repos/OpenAPITools/openapi-generator/releases"
        with urllib.request.urlopen(github_api_releases_link) as release_information_url:
            latest_release_infos = json.load(release_information_url)[0]
            latest_version = latest_release_infos["tag_name"][1:]
            return latest_version

    @GeneralUtilities.check_arguments
    def set_version_of_openapigenerator_by_update_dependencies_file(self, update_dependencies_script_file: str, used_version: str = None) -> None:
        codeunit_folder: str = GeneralUtilities.resolve_relative_path("../..", update_dependencies_script_file)
        self.set_version_of_openapigenerator(codeunit_folder, used_version)

    @GeneralUtilities.check_arguments
    def set_version_of_openapigenerator(self, codeunit_folder: str, used_version: str = None) -> None:
        target_folder: str = os.path.join(codeunit_folder, "Other", "Resources", "Dependencies", "OpenAPIGenerator")
        version_file = os.path.join(target_folder, "Version.txt")
        if used_version is None:
            used_version = self.get_latest_version_of_openapigenerator()
        GeneralUtilities.ensure_directory_exists(target_folder)
        GeneralUtilities.ensure_file_exists(version_file)
        GeneralUtilities.write_text_to_file(version_file, used_version)

    @GeneralUtilities.check_arguments
    def ensure_openapigenerator_is_available(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        openapigenerator_folder = os.path.join(codeunit_folder, "Other", "Resources", "OpenAPIGenerator")
        internet_connection_is_available = GeneralUtilities.internet_connection_is_available()
        filename = "open-api-generator.jar"
        jar_file = f"{openapigenerator_folder}/{filename}"
        jar_file_exists = os.path.isfile(jar_file)
        if internet_connection_is_available:  # Load/Update
            version_file = os.path.join(codeunit_folder, "Other", "Resources", "Dependencies", "OpenAPIGenerator", "Version.txt")
            used_version = GeneralUtilities.read_text_from_file(version_file)
            download_link = f"https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/{used_version}/openapi-generator-cli-{used_version}.jar"
            GeneralUtilities.ensure_directory_does_not_exist(openapigenerator_folder)
            GeneralUtilities.ensure_directory_exists(openapigenerator_folder)
            urllib.request.urlretrieve(download_link, jar_file)
        else:
            if jar_file_exists:
                GeneralUtilities.write_message_to_stdout("Warning: Can not check for updates of OpenAPIGenerator due to missing internet-connection.")
            else:
                raise ValueError("Can not download OpenAPIGenerator.")

    @GeneralUtilities.check_arguments
    def generate_api_client_from_dependent_codeunit_in_angular(self, file: str, name_of_api_providing_codeunit: str, generated_program_part_name: str) -> None:
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", file)
        target_subfolder_in_codeunit = f"src/app/generated/{generated_program_part_name}"
        language = "typescript-angular"
        self.ensure_openapigenerator_is_available(codeunit_folder)
        openapigenerator_jar_file = os.path.join(codeunit_folder, "Other", "Resources", "OpenAPIGenerator", "open-api-generator.jar")
        openapi_spec_file = os.path.join(codeunit_folder, "Other", "Resources", "DependentCodeUnits", name_of_api_providing_codeunit, "APISpecification", f"{name_of_api_providing_codeunit}.latest.api.json")
        target_folder = os.path.join(codeunit_folder, target_subfolder_in_codeunit)
        GeneralUtilities.ensure_folder_exists_and_is_empty(target_folder)
        self.__sc.run_program("java", f'-jar {openapigenerator_jar_file} generate -i {openapi_spec_file} -g {language} -o {target_folder} --global-property supportingFiles --global-property models --global-property apis', codeunit_folder)

    @GeneralUtilities.check_arguments
    def generate_api_client_from_dependent_codeunit_in_dotnet(self, file: str, name_of_api_providing_codeunit: str, base_namespace: str) -> None:
        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", file)
        codeunit_name = os.path.basename(codeunit_folder)
        client_subpath = f"{codeunit_name}/APIClients/{name_of_api_providing_codeunit}"
        namespace = f"{base_namespace}.APIClients.{name_of_api_providing_codeunit}"
        target_subfolder_in_codeunit = client_subpath
        language = "csharp"
        additional_properties = f"--additional-properties packageName={namespace}"

        codeunit_folder = GeneralUtilities.resolve_relative_path("../..", file)
        self.ensure_openapigenerator_is_available(codeunit_folder)
        openapigenerator_jar_file = os.path.join(codeunit_folder, "Other", "Resources", "OpenAPIGenerator", "open-api-generator.jar")
        openapi_spec_file = os.path.join(codeunit_folder, "Other", "Resources", "DependentCodeUnits", name_of_api_providing_codeunit, "APISpecification", f"{name_of_api_providing_codeunit}.latest.api.json")
        target_folder = os.path.join(codeunit_folder, target_subfolder_in_codeunit)
        GeneralUtilities.ensure_directory_exists(target_folder)
        self.__sc.run_program("java", f'-jar {openapigenerator_jar_file} generate -i {openapi_spec_file} -g {language} -o {target_folder} --global-property supportingFiles --global-property models --global-property apis {additional_properties}', codeunit_folder)

        # move docs to correct folder
        target_folder_docs = os.path.join(target_folder, "docs")
        target_folder_docs_correct = os.path.join(codeunit_folder, "Other", "Reference", "ReferenceContent", f"{name_of_api_providing_codeunit}-API")
        GeneralUtilities.ensure_directory_does_not_exist(target_folder_docs_correct)
        GeneralUtilities.ensure_directory_exists(target_folder_docs_correct)
        GeneralUtilities.move_content_of_folder(target_folder_docs, target_folder_docs_correct)
        GeneralUtilities.ensure_directory_does_not_exist(target_folder_docs)

        code_folders = GeneralUtilities.get_direct_folders_of_folder(os.path.join(target_folder, "src"))

        # remove test-folder
        tests_folder = [x for x in code_folders if x.endswith(".Test")][0]
        GeneralUtilities.ensure_directory_does_not_exist(tests_folder)

        # move source to correct folder
        src_folder = [x for x in code_folders if not x.endswith(".Test")][0]
        target_folder_src = GeneralUtilities.resolve_relative_path("../..", src_folder)

        for targetfile in GeneralUtilities.get_direct_files_of_folder(target_folder_src):
            GeneralUtilities.ensure_file_does_not_exist(targetfile)
        for folder in GeneralUtilities.get_direct_folders_of_folder(target_folder_src):
            f = folder.replace("\\", "/")
            if not f.endswith("/.openapi-generator") and not f.endswith("/src"):
                GeneralUtilities.ensure_directory_does_not_exist(f)
        GeneralUtilities.ensure_directory_exists(target_folder_src)
        GeneralUtilities.move_content_of_folder(src_folder, target_folder_src)
        GeneralUtilities.ensure_directory_does_not_exist(src_folder)
        for targetfile in GeneralUtilities.get_direct_files_of_folder(target_folder_src):
            GeneralUtilities.ensure_file_does_not_exist(targetfile)

    @GeneralUtilities.check_arguments
    def replace_version_in_packagejson_file(self, packagejson_file: str, codeunit_version: str) -> None:
        encoding = "utf-8"
        with open(packagejson_file, encoding=encoding) as f:
            data = json.load(f)
        data['version'] = codeunit_version
        with open(packagejson_file, 'w', encoding=encoding) as f:
            json.dump(data, f, indent=2)

    @GeneralUtilities.check_arguments
    def build_dependent_code_units(self, repo_folder: str, codeunit_name: str, verbosity: int, target_environmenttype: str, additional_arguments_file: str, commandlinearguments: list[str]) -> None:
        verbosity = self.get_verbosity_from_commandline_arguments(commandlinearguments, verbosity)
        codeunit_file = os.path.join(repo_folder, codeunit_name, codeunit_name + ".codeunit.xml")
        dependent_codeunits = self.get_dependent_code_units(codeunit_file)
        dependent_codeunits_folder = os.path.join(repo_folder, codeunit_name, "Other", "Resources", "DependentCodeUnits")
        GeneralUtilities.ensure_directory_does_not_exist(dependent_codeunits_folder)
        if 0 < len(dependent_codeunits):
            GeneralUtilities.write_message_to_stdout(f"Start building dependent codeunits for codeunit {codeunit_name}.")
        for dependent_codeunit in dependent_codeunits:
            self.__build_codeunit(os.path.join(repo_folder, dependent_codeunit), verbosity, target_environmenttype, additional_arguments_file, False, False, commandlinearguments)
        if 0 < len(dependent_codeunits):
            GeneralUtilities.write_message_to_stdout(f"Finished building dependent codeunits for codeunit {codeunit_name}.")

    @GeneralUtilities.check_arguments
    def copy_artifacts_from_dependent_code_units(self, repo_folder: str, codeunit_name: str) -> None:
        codeunit_file = os.path.join(repo_folder, codeunit_name, codeunit_name + ".codeunit.xml")
        dependent_codeunits = self.get_dependent_code_units(codeunit_file)
        if len(dependent_codeunits) > 0:
            GeneralUtilities.write_message_to_stdout(f"Get dependent artifacts for codeunit {codeunit_name}.")
        dependent_codeunits_folder = os.path.join(repo_folder, codeunit_name, "Other", "Resources", "DependentCodeUnits")
        GeneralUtilities.ensure_directory_does_not_exist(dependent_codeunits_folder)
        for dependent_codeunit in dependent_codeunits:
            target_folder = os.path.join(dependent_codeunits_folder, dependent_codeunit)
            GeneralUtilities.ensure_directory_does_not_exist(target_folder)
            other_folder = os.path.join(repo_folder, dependent_codeunit, "Other")
            artifacts_folder = os.path.join(other_folder, "Artifacts")
            shutil.copytree(artifacts_folder, target_folder)

    @GeneralUtilities.check_arguments
    def add_github_release(self, productname: str, projectversion: str, build_artifacts_folder: str, github_username: str, repository_folder: str, commandline_arguments: list[str], additional_attached_files: list[str]) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        GeneralUtilities.write_message_to_stdout(f"Create GitHub-release for {productname}...")
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, 1)
        github_repo = f"{github_username}/{productname}"
        artifact_files = []
        codeunits = self.get_codeunits(repository_folder)
        for codeunit in codeunits:
            artifact_files.append(self.__sc.find_file_by_extension(f"{build_artifacts_folder}\\{productname}\\{projectversion}\\{codeunit}", "Productive.Artifacts.zip"))
        if additional_attached_files is not None:
            for additional_attached_file in additional_attached_files:
                artifact_files.append(additional_attached_file)
        changelog_file = os.path.join(repository_folder, "Other", "Resources", "Changelog", f"v{projectversion}.md")
        self.__sc.run_program_argsasarray("gh", ["release", "create", f"v{projectversion}", "--repo",  github_repo, "--notes-file", changelog_file, "--title", f"Release v{projectversion}"]+artifact_files, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def get_dependencies_which_are_ignored_from_updates(self, codeunit_folder: str, print_warnings_for_ignored_dependencies: bool) -> list[str]:
        self.assert_is_codeunit_folder(codeunit_folder)
        namespaces = {'cps': 'https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
        codeunit_name = os.path.basename(codeunit_folder)
        codeunit_file = os.path.join(codeunit_folder, f"{codeunit_name}.codeunit.xml")
        root: etree._ElementTree = etree.parse(codeunit_file)
        ignoreddependencies = root.xpath('//cps:codeunit/cps:properties/cps:updatesettings/cps:ignoreddependencies/cps:ignoreddependency', namespaces=namespaces)
        result = [x.text.replace("\\n", GeneralUtilities.empty_string).replace("\\r", GeneralUtilities.empty_string).replace("\n", GeneralUtilities.empty_string).replace("\r", GeneralUtilities.empty_string).strip() for x in ignoreddependencies]
        if print_warnings_for_ignored_dependencies and len(result) > 0:
            GeneralUtilities.write_message_to_stderr(f"Warning: Codeunit {codeunit_name} contains the following dependencies which will are ignoed for automatic updates: "+', '.join(result))
        return result

    @GeneralUtilities.check_arguments
    def update_dependencies_of_typical_flutter_codeunit(self, update_script_file: str, verbosity: int, cmd_args: list[str]) -> None:
        codeunit_folder = GeneralUtilities.resolve_relative_path("..", os.path.dirname(update_script_file))
        ignored_dependencies = self.get_dependencies_which_are_ignored_from_updates(codeunit_folder, True)
        # TODO implement

    @GeneralUtilities.check_arguments
    def update_dependencies_of_typical_python_repository_requirements(self, repository_folder: str, verbosity: int, cmd_args: list[str]) -> None:
        verbosity = self.get_verbosity_from_commandline_arguments(cmd_args, verbosity)

        development_requirements_file = os.path.join(repository_folder, "Other", "requirements.txt")
        if (os.path.isfile(development_requirements_file)):
            self.__sc.update_dependencies_of_python_in_requirementstxt_file(development_requirements_file, [], verbosity)

    @GeneralUtilities.check_arguments
    def update_dependencies_of_typical_python_codeunit(self, update_script_file: str, verbosity: int, cmd_args: list[str]) -> None:
        codeunit_folder = GeneralUtilities.resolve_relative_path("..", os.path.dirname(update_script_file))
        ignored_dependencies = self.get_dependencies_which_are_ignored_from_updates(codeunit_folder, True)
        # TODO consider ignored_dependencies
        verbosity = self.get_verbosity_from_commandline_arguments(cmd_args, verbosity)

        setup_cfg = os.path.join(codeunit_folder, "setup.cfg")
        if (os.path.isfile(setup_cfg)):
            self.__sc.update_dependencies_of_python_in_setupcfg_file(setup_cfg, ignored_dependencies, verbosity)

        development_requirements_file = os.path.join(codeunit_folder, "requirements.txt")  # required for codeunits which contain python-code which need third-party dependencies
        if (os.path.isfile(development_requirements_file)):
            self.__sc.update_dependencies_of_python_in_requirementstxt_file(development_requirements_file, ignored_dependencies, verbosity)

        development_requirements_file2 = os.path.join(codeunit_folder, "Other", "requirements.txt")  # required for codeunits which contain python-scripts which needs third-party dependencies
        if (os.path.isfile(development_requirements_file2)):
            self.__sc.update_dependencies_of_python_in_requirementstxt_file(development_requirements_file2, ignored_dependencies, verbosity)

    @GeneralUtilities.check_arguments
    def update_dependencies_of_typical_dotnet_codeunit(self, update_script_file: str, verbosity: int, cmd_args: list[str]) -> None:
        codeunit_folder = GeneralUtilities.resolve_relative_path("..", os.path.dirname(update_script_file))
        ignored_dependencies = self.get_dependencies_which_are_ignored_from_updates(codeunit_folder, True)
        verbosity = self.get_verbosity_from_commandline_arguments(cmd_args, verbosity)
        codeunit_name = os.path.basename(codeunit_folder)

        build_folder = os.path.join(codeunit_folder, "Other", "Build")
        self.__sc.run_program("python", "Build.py", build_folder, verbosity)

        test_csproj_file = os.path.join(codeunit_folder, f"{codeunit_name}Tests", f"{codeunit_name}Tests.csproj")
        self.__sc.update_dependencies_of_dotnet_project(test_csproj_file, verbosity, ignored_dependencies)
        csproj_file = os.path.join(codeunit_folder, codeunit_name, f"{codeunit_name}.csproj")
        self.__sc.update_dependencies_of_dotnet_project(csproj_file, verbosity, ignored_dependencies)

    @GeneralUtilities.check_arguments
    def update_dependencies_of_package_json(self, folder: str, verbosity: int, cmd_args: list[str]) -> None:
        if self.is_codeunit_folder(folder):
            ignored_dependencies = self.get_dependencies_which_are_ignored_from_updates(folder, True)
        else:
            ignored_dependencies = []
        # TODO consider ignored_dependencies
        result = self.run_with_epew("npm", "outdated", folder, verbosity, throw_exception_if_exitcode_is_not_zero=False)
        if result[0] == 0:
            return  # all dependencies up to date
        elif result[0] == 1:
            package_json_content = None
            package_json_file = f"{folder}/package.json"
            with open(package_json_file, "r", encoding="utf-8") as package_json_file_object:
                package_json_content = json.load(package_json_file_object)
                lines = GeneralUtilities.string_to_lines(result[1])[1:][:-1]
                for line in lines:
                    normalized_line_splitted = ' '.join(line.split()).split(" ")
                    package = normalized_line_splitted[0]
                    latest_version = normalized_line_splitted[3]
                    if package in package_json_content["dependencies"]:
                        package_json_content["dependencies"][package] = latest_version
                    if package in package_json_content["devDependencies"]:
                        package_json_content["devDependencies"][package] = latest_version
            with open(package_json_file, "w", encoding="utf-8") as package_json_file_object:
                json.dump(package_json_content, package_json_file_object, indent=4)
            self.do_npm_install(folder, True, verbosity)
        else:
            GeneralUtilities.write_message_to_stderr("Update dependencies resulted in an error.")

    @GeneralUtilities.check_arguments
    def generate_tasksfile_from_workspace_file(self, repository_folder: str, append_cli_args_at_end: bool = False) -> None:
        """This function works platform-independent also for non-local-executions if the ScriptCollection commandline-commands are available as global command on the target-system."""
        if self.__sc.program_runner.will_be_executed_locally():  # works only locally, but much more performant than always running an external program
            self.__sc.assert_is_git_repository(repository_folder)
            workspace_file: str = self.__sc.find_file_by_extension(repository_folder, "code-workspace")
            task_file: str = repository_folder + "/Taskfile.yml"
            lines: list[str] = ["version: '3'", GeneralUtilities.empty_string, "tasks:", GeneralUtilities.empty_string]
            workspace_file_content: str = self.__sc.get_file_content(workspace_file)
            jsoncontent = json.loads(workspace_file_content)
            tasks = jsoncontent["tasks"]["tasks"]
            tasks.sort(key=lambda x: x["label"].split("/")[-1], reverse=False)  # sort by the label of the task
            for task in tasks:
                if task["type"] == "shell":

                    description: str = task["label"]
                    name: str = GeneralUtilities.to_pascal_case(description)
                    command = task["command"]
                    relative_script_file = task["command"]

                    relative_script_file = "."
                    cwd: str = None
                    if "options" in task:
                        options = task["options"]
                        if "cwd" in options:
                            cwd = options["cwd"]
                            cwd = cwd.replace("${workspaceFolder}", ".")
                            cwd = cwd.replace("\\", "\\\\").replace('"', '\\"')  # escape backslashes and double quotes for YAML
                            relative_script_file = cwd
                    if len(relative_script_file) == 0:
                        relative_script_file = "."

                    command_with_args = command
                    if "args" in task:
                        args = task["args"]
                        if len(args) > 1:
                            command_with_args = f"{command_with_args} {' '.join(args)}"

                    if "description" in task:
                        additional_description = task["description"]
                        description = f"{description} ({additional_description})"

                    if append_cli_args_at_end:
                        command_with_args = f"{command_with_args} {{{{.CLI_ARGS}}}}"

                    description_literal = description.replace("\\", "\\\\").replace('"', '\\"')  # escape backslashes and double quotes for YAML
                    command_with_args = command_with_args.replace("\\", "\\\\").replace('"', '\\"')  # escape backslashes and double quotes for YAML

                    lines.append(f"  {name}:")
                    lines.append(f'    desc: "{description_literal}"')
                    lines.append('    silent: true')
                    if cwd is not None:
                        lines.append(f'    dir: "{cwd}"')
                    lines.append("    cmds:")
                    lines.append(f'      - "{command_with_args}"')
                    lines.append('    aliases:')
                    lines.append(f'      - {name.lower()}')
                    if "aliases" in task:
                        aliases = task["aliases"]
                        for alias in aliases:
                            lines.append(f'      - {alias}')
                    lines.append(GeneralUtilities.empty_string)

            self.__sc.set_file_content(task_file, "\n".join(lines))
        else:
            self.__sc.run_program("scgeneratetasksfilefromworkspacefile", f"--repositoryfolder {repository_folder}")

    @GeneralUtilities.check_arguments
    def start_local_test_service(self, file: str):
        example_folder = os.path.dirname(file)
        docker_compose_file = os.path.join(example_folder, "docker-compose.yml")
        for service in self.__sc.get_services_from_yaml_file(docker_compose_file):
            self.__sc.kill_docker_container(service)
        example_name = os.path.basename(example_folder)
        title = f"Test{example_name}"
        self.__sc.run_program("docker", f"compose -p {title.lower()} up --detach", example_folder, title=title)

    @GeneralUtilities.check_arguments
    def stop_local_test_service(self, file: str):
        example_folder = os.path.dirname(file)
        example_name = os.path.basename(example_folder)
        title = f"Test{example_name}"
        self.__sc.run_program("docker", f"compose -p {title.lower()} down", example_folder, title=title)

    @GeneralUtilities.check_arguments
    def standardized_tasks_update_version_in_docker_examples(self, file, codeunit_version) -> None:
        folder_of_current_file = os.path.dirname(file)
        codeunit_folder = GeneralUtilities.resolve_relative_path("..", folder_of_current_file)
        codeunit_name = os.path.basename(codeunit_folder)
        codeunit_name_lower = codeunit_name.lower()
        examples_folder = GeneralUtilities.resolve_relative_path("Other/Reference/ReferenceContent/Examples", codeunit_folder)
        for example_folder in GeneralUtilities.get_direct_folders_of_folder(examples_folder):
            docker_compose_file = os.path.join(example_folder, "docker-compose.yml")
            if os.path.isfile(docker_compose_file):
                filecontent = GeneralUtilities.read_text_from_file(docker_compose_file)
                replaced = re.sub(f'image:\\s+{codeunit_name_lower}:\\d+\\.\\d+\\.\\d+', f"image: {codeunit_name_lower}:{codeunit_version}", filecontent)
                GeneralUtilities.write_text_to_file(docker_compose_file, replaced)

    @GeneralUtilities.check_arguments
    def start_dockerfile_example(self, current_file: str, verbosity: int, remove_old_container: bool, remove_volumes_folder: bool, commandline_arguments: list[str], env_file: str) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        folder = os.path.dirname(current_file)
        example_name = os.path.basename(folder)
        oci_image_artifacts_folder = GeneralUtilities.resolve_relative_path("../../../../Artifacts/BuildResult_OCIImage", folder)
        image_filename = os.path.basename(self.__sc.find_file_by_extension(oci_image_artifacts_folder, "tar"))
        codeunit_name = os.path.basename(GeneralUtilities.resolve_relative_path("../../../../..", folder))
        if remove_old_container:
            docker_compose_file = f"{folder}/docker-compose.yml"
            container_names = []
            lines = GeneralUtilities.read_lines_from_file(docker_compose_file)
            for line in lines:
                if match := re.search("container_name:\\s*'?([^']+)'?", line):
                    container_names.append(match.group(1))
            GeneralUtilities.write_message_to_stdout(f"Ensure container of {docker_compose_file} do not exist...")
            for container_name in container_names:
                GeneralUtilities.write_message_to_stdout(f"Ensure container {container_name} does not exist...")
                self.__sc.run_program("docker", f"container rm -f {container_name}", oci_image_artifacts_folder, verbosity=0, throw_exception_if_exitcode_is_not_zero=False)
        if remove_volumes_folder:
            volumes_folder = os.path.join(folder, "Volumes")
            GeneralUtilities.write_message_to_stdout(f"Ensure volumes-folder '{volumes_folder}' does not exist...")
            GeneralUtilities.ensure_directory_does_not_exist(volumes_folder)
            GeneralUtilities.ensure_directory_exists(volumes_folder)
        GeneralUtilities.write_message_to_stdout("Load docker-image...")
        self.__sc.run_program("docker", f"load -i {image_filename}", oci_image_artifacts_folder, verbosity=verbosity)
        docker_project_name = f"{codeunit_name}_{example_name}".lower()
        GeneralUtilities.write_message_to_stdout("Start docker-container...")
        argument = f"compose --project-name {docker_project_name}"
        if env_file is not None:
            argument = f"{argument} --env-file {env_file}"
        argument = f"{argument} up --detach"
        self.__sc.run_program("docker", argument, folder, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def ensure_env_file_is_generated(self, current_file: str, env_file_name: str, env_values: dict[str, str]):
        folder = os.path.dirname(current_file)
        env_file = os.path.join(folder, env_file_name)
        if not os.path.isfile(env_file):
            lines = []
            for key, value in env_values.items():
                lines.append(f"{key}={value}")
            GeneralUtilities.write_lines_to_file(env_file, lines)

    @GeneralUtilities.check_arguments
    def stop_dockerfile_example(self, current_file: str, verbosity: int, remove_old_container: bool, remove_volumes_folder: bool, commandline_arguments: list[str]) -> None:
        verbosity = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)
        folder = os.path.dirname(current_file)
        example_name = os.path.basename(folder)
        codeunit_name = os.path.basename(GeneralUtilities.resolve_relative_path("../../../../..", folder))
        docker_project_name = f"{codeunit_name}_{example_name}".lower()
        GeneralUtilities.write_message_to_stdout("Stop docker-container...")
        self.__sc.run_program("docker", f"compose --project-name {docker_project_name} down", folder, verbosity=verbosity)

    @GeneralUtilities.check_arguments
    def create_artifact_for_development_certificate(self, codeunit_folder: str):
        self.assert_is_codeunit_folder(codeunit_folder)
        ce_source_folder = GeneralUtilities.resolve_relative_path("Other/Resources/DevelopmentCertificate", codeunit_folder)
        ca_source_folder = GeneralUtilities.resolve_relative_path("Other/Resources/CA", codeunit_folder)
        ce_target_folder = GeneralUtilities.resolve_relative_path("Other/Artifacts/DevelopmentCertificate", codeunit_folder)
        ca_target_folder = GeneralUtilities.resolve_relative_path("Other/Artifacts/CA", codeunit_folder)

        GeneralUtilities.ensure_directory_does_not_exist(ce_target_folder)
        GeneralUtilities.ensure_directory_exists(ce_target_folder)
        GeneralUtilities.copy_content_of_folder(ce_source_folder, ce_target_folder)
        GeneralUtilities.ensure_directory_does_not_exist(ca_target_folder)
        GeneralUtilities.ensure_directory_exists(ca_target_folder)
        GeneralUtilities.copy_content_of_folder(ca_source_folder, ca_target_folder)

    @GeneralUtilities.check_arguments
    def _internal_get_sorted_codeunits_by_dict(self, codeunits: dict[str, set[str]]) -> list[str]:
        sorted_codeunits = {
            node: sorted(codeunits[node])
            for node in sorted(codeunits)
        }

        ts = TopologicalSorter()
        for node, deps in sorted_codeunits.items():
            ts.add(node, *deps)

        result_typed = list(ts.static_order())
        result = [str(item) for item in result_typed]
        return result

    @GeneralUtilities.check_arguments
    def get_project_name(self, repository_folder: str) -> str:
        self.__sc.assert_is_git_repository(repository_folder)
        for file in GeneralUtilities.get_direct_files_of_folder(repository_folder):
            if file.endswith(".code-workspace"):
                return Path(file).stem
        raise ValueError(f'Project-name can not be calculated for repository "{repository_folder}"')

    def __check_target_environmenttype(self, target_environmenttype: str):
        allowed_values = list(self.get_default_target_environmenttype_mapping().values())
        if not (target_environmenttype in allowed_values):
            raise ValueError(f"Invalid target-environmenttype: '{target_environmenttype}'")

    @GeneralUtilities.check_arguments
    def build_codeunit(self, codeunit_folder: str, verbosity: int = 1, target_environmenttype: str = "QualityCheck", additional_arguments_file: str = None, is_pre_merge: bool = False, export_target_directory: str = None, assume_dependent_codeunits_are_already_built: bool = False, commandlinearguments: list[str] = []) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        repository_folder = os.path.dirname(codeunit_folder)
        self.build_specific_codeunits(repository_folder, [codeunit_name], verbosity, target_environmenttype, additional_arguments_file, is_pre_merge, export_target_directory, assume_dependent_codeunits_are_already_built, commandlinearguments, False)

    @GeneralUtilities.check_arguments
    def build_codeunitsC(self, repository_folder: str, image: str, verbosity: int = 1, target_environmenttype: str = "QualityCheck", additional_arguments_file: str = None, commandlinearguments: list[str] = []) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        if target_environmenttype == "Development":
            raise ValueError(f"build_codeunitsC is not available for target_environmenttype {target_environmenttype}.")
        # TODO handle additional_arguments_file
        # TODO add option to allow building different codeunits in same project with different images due to their demands
        # TODO check if image provides all demands of codeunit
        self.__sc.run_program("docker", f"run --volume {repository_folder}:/Workspace/Repository " + f"-e repositoryfolder=/Workspace/Repository -e verbosity={verbosity} -e targetenvironment={target_environmenttype} {image}", repository_folder)

    @GeneralUtilities.check_arguments
    def build_codeunits(self, repository_folder: str, verbosity: int = 1, target_environmenttype: str = "QualityCheck", additional_arguments_file: str = None, is_pre_merge: bool = False, export_target_directory: str = None, commandline_arguments: list[str] = [], do_git_clean_when_no_changes: bool = False, note: str = None) -> None:
        self.__check_target_environmenttype(target_environmenttype)
        self.__sc.assert_is_git_repository(repository_folder)
        repository_folder = GeneralUtilities.resolve_relative_path_from_current_working_directory(repository_folder)
        codeunits = self.get_codeunits(repository_folder, False)
        project_version = self.get_version_of_project(repository_folder)

        now = datetime.now()
        if not self.__suport_information_exists(repository_folder, project_version):
            support_time = timedelta(days=365*2+30*3+1)  # TODO make this configurable
            until = now + support_time
            until_day = datetime(until.year, until.month, until.day, 0, 0, 0)
            from_day = datetime(now.year, now.month, now.day, 0, 0, 0)
            self.mark_current_version_as_supported(repository_folder, project_version, from_day, until_day)

        project_resources_folder = os.path.join(repository_folder, "Other", "Scripts")
        PrepareBuildCodeunits_script_name = "PrepareBuildCodeunits.py"
        prepare_build_codeunits_scripts = os.path.join(project_resources_folder, PrepareBuildCodeunits_script_name)

        if do_git_clean_when_no_changes and not self.__sc.git_repository_has_uncommitted_changes(repository_folder):
            self.__sc.run_program("git", "clean -dfx", repository_folder)
        if os.path.isfile(prepare_build_codeunits_scripts):
            GeneralUtilities.write_message_to_stdout(f'Run "{PrepareBuildCodeunits_script_name}"')
            result = self.__sc.run_program("python", f"{PrepareBuildCodeunits_script_name}", project_resources_folder, throw_exception_if_exitcode_is_not_zero=False, print_live_output=True)
            if result[0] != 0:
                raise ValueError(f"PrepareBuildCodeunits.py resulted in exitcode {result[0]}.")

        self.__do_repository_checks(repository_folder, project_version)
        self.build_specific_codeunits(repository_folder, codeunits, verbosity, target_environmenttype, additional_arguments_file, is_pre_merge, export_target_directory, False, commandline_arguments, do_git_clean_when_no_changes, note)

    @GeneralUtilities.check_arguments
    def build_specific_codeunits(self, repository_folder: str, codeunits: list[str], verbosity: int = 1, target_environmenttype: str = "QualityCheck", additional_arguments_file: str = None, is_pre_merge: bool = False, export_target_directory: str = None, assume_dependent_codeunits_are_already_built: bool = True, commandline_arguments: list[str] = [], do_git_clean_when_no_changes: bool = False, note: str = None, check_for_new_files: bool = True) -> None:
        now_begin: datetime = datetime.now()
        codeunits_list = "{"+", ".join(["a", "b"])+"}"
        if verbosity > 2:
            GeneralUtilities.write_message_to_stdout(f"Start building codeunits ({codeunits_list}) in repository '{repository_folder}'...")
        self.__sc.assert_is_git_repository(repository_folder)
        self.__check_target_environmenttype(target_environmenttype)
        repository_folder = GeneralUtilities.resolve_relative_path_from_current_working_directory(repository_folder)
        repository_name = os.path.basename(repository_folder)
        contains_uncommitted_changes_at_begin = self.__sc.git_repository_has_uncommitted_changes(repository_folder)
        if contains_uncommitted_changes_at_begin:
            if is_pre_merge:
                raise ValueError(f'Repository "{repository_folder}" has uncommitted changes.')
        codeunit_subfolders = [os.path.join(repository_folder, codeunit) for codeunit in codeunits]
        codeunits_with_dependent_codeunits: dict[str, set[str]] = dict[str, set[str]]()

        for subfolder in codeunit_subfolders:
            codeunit_name: str = os.path.basename(subfolder)
            codeunit_file = os.path.join(subfolder, f"{codeunit_name}.codeunit.xml")
            GeneralUtilities.assert_condition(os.path.exists(codeunit_file), f"Codeunit-file '{codeunit_file}' does nost exist.")
            codeunits_with_dependent_codeunits[codeunit_name] = self.get_dependent_code_units(codeunit_file)
        sorted_codeunits = self.get_codeunits(repository_folder)
        sorted_codeunits = [codeunit for codeunit in sorted_codeunits if codeunit in codeunits]
        project_version = self.get_version_of_project(repository_folder)

        message = f"Build codeunits in product {repository_name}... (Started: {GeneralUtilities.datetime_to_string(now_begin)})"
        if note is not None:
            message = f"{message} ({note})"
        GeneralUtilities.write_message_to_stdout(message)

        if len(sorted_codeunits) == 0:
            raise ValueError(f'No codeunit found in subfolders of "{repository_folder}".')
        else:
            if verbosity > 1:
                GeneralUtilities.write_message_to_stdout(f"Attempt to build codeunits ({codeunits_list}) for project version {project_version} in the following order:")
                i = 0
                for codeunit in sorted_codeunits:
                    i = i+1
                    GeneralUtilities.write_message_to_stdout(f"{i}.: {codeunit}")
            for codeunit in sorted_codeunits:
                GeneralUtilities.write_message_to_stdout(GeneralUtilities.get_line())
                self.__build_codeunit(os.path.join(repository_folder, codeunit), verbosity, target_environmenttype, additional_arguments_file, is_pre_merge, assume_dependent_codeunits_are_already_built, commandline_arguments)
            GeneralUtilities.write_message_to_stdout(GeneralUtilities.get_line())
        contains_uncommitted_changes_at_end = self.__sc.git_repository_has_uncommitted_changes(repository_folder)
        if contains_uncommitted_changes_at_end and (not is_pre_merge) and check_for_new_files:
            if contains_uncommitted_changes_at_begin:
                GeneralUtilities.write_message_to_stdout(f'There are still uncommitted changes in the repository "{repository_folder}".')
            else:
                message = f'Due to the build-process the repository "{repository_folder}" has new uncommitted changes.'
                if target_environmenttype == "Development":
                    GeneralUtilities.write_message_to_stderr(f"Warning: {message}")
                else:
                    raise ValueError(message)

        if export_target_directory is not None:
            project_name = self.get_project_name(repository_folder)
            for codeunit in sorted_codeunits:
                codeunit_version = self.get_version_of_codeunit_folder(os.path.join(repository_folder,  codeunit))
                artifacts_folder = os.path.join(repository_folder,  codeunit, "Other", "Artifacts")
                target_folder = os.path.join(export_target_directory, project_name, project_version, codeunit)
                GeneralUtilities.ensure_directory_does_not_exist(target_folder)
                GeneralUtilities.ensure_directory_exists(target_folder)
                filename_without_extension = f"{codeunit}.v{codeunit_version}.{target_environmenttype}.Artifacts"
                shutil.make_archive(filename_without_extension, 'zip', artifacts_folder)
                archive_file = os.path.join(os.getcwd(), f"{filename_without_extension}.zip")
                shutil.move(archive_file, target_folder)

        now_end: datetime = datetime.now()
        message2 = f"Finished build codeunits in product {repository_name}. (Finished: {GeneralUtilities.datetime_to_string(now_end)})"
        if note is not None:
            message2 = f"{message2} ({note})"
        GeneralUtilities.write_message_to_stdout(message2)

    @GeneralUtilities.check_arguments
    def __do_repository_checks(self, repository_folder: str, project_version: str) -> None:  # TDOO move this to a general project-specific (and codeunit-independent-script)
        self.__sc.assert_is_git_repository(repository_folder)
        self.__check_if_changelog_exists(repository_folder, project_version)
        self.__check_whether_security_txt_exists(repository_folder)
        self.__check_whether_general_reference_exists(repository_folder)
        self.__check_whether_workspace_file_exists(repository_folder)
        self.__check_for_staged_or_committed_ignored_files(repository_folder)

    @GeneralUtilities.check_arguments
    def __check_whether_general_reference_exists(self, repository_folder: str) -> None:
        GeneralUtilities.assert_file_exists(os.path.join(repository_folder, "Other", "Reference", "Reference.md"))

    @GeneralUtilities.check_arguments
    def __check_if_changelog_exists(self, repository_folder: str, project_version: str) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        changelog_folder = os.path.join(repository_folder, "Other", "Resources", "Changelog")
        changelog_file = os.path.join(changelog_folder, f"v{project_version}.md")
        if not os.path.isfile(changelog_file):
            raise ValueError(f"Changelog-file '{changelog_file}' does not exist. Try creating it using 'sccreatechangelogentry' for example.")

    @GeneralUtilities.check_arguments
    def __check_whether_security_txt_exists(self, repository_folder: str) -> None:
        security_txt_file_relative = ".well-known/security.txt"
        security_txt_file = GeneralUtilities.resolve_relative_path(security_txt_file_relative, repository_folder)
        if not os.path.isfile(security_txt_file):
            raise ValueError(f"The repository does not contain a '{security_txt_file_relative}'-file. See https://securitytxt.org/ for more information.")
        # TODO throw error if the date set in the file is expired
        # TODO write wartning if the date set in the file expires soon

    @GeneralUtilities.check_arguments
    def __check_for_staged_or_committed_ignored_files(self, repository_folder: str) -> None:
        for file in self.__sc.get_staged_or_committed_git_ignored_files(repository_folder):
            GeneralUtilities.write_message_to_stderr(f'Warning: Repository contains staged or committed file "{file}" which is git-ignored.')

    @GeneralUtilities.check_arguments
    def __check_whether_workspace_file_exists(self, repository_folder: str) -> None:
        count = 0
        for file in GeneralUtilities.get_direct_files_of_folder(repository_folder):
            if file.endswith(".code-workspace"):
                count = count + 1
        if count != 1:
            raise ValueError('The repository must contain exactly one ".code-workspace"-file on the top-level.')

    @GeneralUtilities.check_arguments
    def update_dependency_in_resources_folder(self, update_dependencies_file, dependency_name: str, latest_version_function: str) -> None:
        dependency_folder = GeneralUtilities.resolve_relative_path(f"../Resources/Dependencies/{dependency_name}", update_dependencies_file)
        version_file = os.path.join(dependency_folder, "Version.txt")
        version_file_exists = os.path.isfile(version_file)
        write_to_file = False
        if version_file_exists:
            current_version = GeneralUtilities.read_text_from_file(version_file)
            if current_version != latest_version_function:
                write_to_file = True
        else:
            GeneralUtilities.ensure_directory_exists(dependency_folder)
            GeneralUtilities.ensure_file_exists(version_file)
            write_to_file = True
        if write_to_file:
            GeneralUtilities.write_text_to_file(version_file, latest_version_function)

    @GeneralUtilities.check_arguments
    def __ensure_grylibrary_is_available(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        grylibrary_folder = os.path.join(codeunit_folder, "Other", "Resources", "GRYLibrary")
        grylibrary_dll_file = os.path.join(grylibrary_folder, "BuildResult_DotNet_win-x64", "GRYLibrary.dll")
        internet_connection_is_available = GeneralUtilities.internet_connection_is_available()
        grylibrary_dll_file_exists = os.path.isfile(grylibrary_dll_file)
        if internet_connection_is_available:  # Load/Update GRYLibrary
            grylibrary_latest_codeunit_file = "https://raw.githubusercontent.com/anionDev/GRYLibrary/stable/GRYLibrary/GRYLibrary.codeunit.xml"
            with urllib.request.urlopen(grylibrary_latest_codeunit_file) as url_result:
                grylibrary_latest_version = self.get_version_of_codeunit_file_content(url_result.read().decode("utf-8"))
            if grylibrary_dll_file_exists:
                grylibrary_existing_codeunit_file = os.path.join(grylibrary_folder, "SourceCode", "GRYLibrary.codeunit.xml")
                grylibrary_existing_codeunit_version = self.get_version_of_codeunit(grylibrary_existing_codeunit_file)
                if grylibrary_existing_codeunit_version != grylibrary_latest_version:
                    GeneralUtilities.ensure_directory_does_not_exist(grylibrary_folder)
            if not os.path.isfile(grylibrary_dll_file):
                GeneralUtilities.ensure_directory_does_not_exist(grylibrary_folder)
                GeneralUtilities.ensure_directory_exists(grylibrary_folder)
                archive_name = f"GRYLibrary.v{grylibrary_latest_version}.Productive.Artifacts.zip"
                archive_download_link = f"https://github.com/anionDev/GRYLibrary/releases/download/v{grylibrary_latest_version}/{archive_name}"
                archive_file = os.path.join(grylibrary_folder, archive_name)
                urllib.request.urlretrieve(archive_download_link, archive_file)
                with zipfile.ZipFile(archive_file, 'r') as zip_ref:
                    zip_ref.extractall(grylibrary_folder)
                GeneralUtilities.ensure_file_does_not_exist(archive_file)
        else:
            if grylibrary_dll_file_exists:
                GeneralUtilities.write_message_to_stdout("Warning: Can not check for updates of GRYLibrary due to missing internet-connection.")
            else:
                raise ValueError("Can not download GRYLibrary.")

    @GeneralUtilities.check_arguments
    def ensure_ffmpeg_is_available(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        ffmpeg_folder = os.path.join(codeunit_folder, "Other", "Resources", "FFMPEG")
        internet_connection_is_available = GeneralUtilities.internet_connection_is_available()
        exe_file = f"{ffmpeg_folder}/ffmpeg.exe"
        exe_file_exists = os.path.isfile(exe_file)
        if internet_connection_is_available:  # Load/Update
            GeneralUtilities.ensure_directory_does_not_exist(ffmpeg_folder)
            GeneralUtilities.ensure_directory_exists(ffmpeg_folder)
            ffmpeg_temp_folder = ffmpeg_folder+"Temp"
            GeneralUtilities.ensure_directory_does_not_exist(ffmpeg_temp_folder)
            GeneralUtilities.ensure_directory_exists(ffmpeg_temp_folder)
            zip_file_on_disk = os.path.join(ffmpeg_temp_folder, "ffmpeg.zip")
            original_zip_filename = "ffmpeg-master-latest-win64-gpl-shared"
            zip_link = f"https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/{original_zip_filename}.zip"
            urllib.request.urlretrieve(zip_link, zip_file_on_disk)
            shutil.unpack_archive(zip_file_on_disk, ffmpeg_temp_folder)
            bin_folder_source = os.path.join(ffmpeg_temp_folder, "ffmpeg-master-latest-win64-gpl-shared/bin")
            bin_folder_target = ffmpeg_folder
            GeneralUtilities.copy_content_of_folder(bin_folder_source, bin_folder_target)
            GeneralUtilities.ensure_directory_does_not_exist(ffmpeg_temp_folder)
        else:
            if exe_file_exists:
                GeneralUtilities.write_message_to_stdout("Warning: Can not check for updates of FFMPEG due to missing internet-connection.")
            else:
                raise ValueError("Can not download FFMPEG.")

    @GeneralUtilities.check_arguments
    def ensure_plantuml_is_available(self, target_folder: str) -> None:
        self.ensure_file_from_github_assets_is_available_with_retry(target_folder, "plantuml", "plantuml", "PlantUML", "plantuml.jar", lambda latest_version: "plantuml.jar")

    @GeneralUtilities.check_arguments
    def ensure_androidappbundletool_is_available(self, target_folder: str) -> None:
        self.ensure_file_from_github_assets_is_available_with_retry(target_folder, "google", "bundletool", "AndroidAppBundleTool", "bundletool.jar", lambda latest_version: f"bundletool-all-{latest_version}.jar")

    @GeneralUtilities.check_arguments
    def ensure_mediamtx_is_available(self, target_folder: str) -> None:
        def download_and_extract(osname: str, osname_in_github_asset: str, extension: str):
            resource_name: str = f"MediaMTX_{osname}"
            zip_filename: str = f"{resource_name}.{extension}"
            self.ensure_file_from_github_assets_is_available_with_retry(target_folder, "bluenviron", "mediamtx", resource_name, zip_filename, lambda latest_version: f"mediamtx_{latest_version}_{osname_in_github_asset}_amd64.{extension}")
            resource_folder: str = os.path.join(target_folder, "Other", "Resources", resource_name)
            target_folder_extracted = os.path.join(resource_folder, "MediaMTX")
            local_zip_file: str = os.path.join(resource_folder, f"{resource_name}.{extension}")
            GeneralUtilities.ensure_folder_exists_and_is_empty(target_folder_extracted)
            if extension == "zip":
                with zipfile.ZipFile(local_zip_file, 'r') as zip_ref:
                    zip_ref.extractall(target_folder_extracted)
            elif extension == "tar.gz":
                with tarfile.open(local_zip_file, "r:gz") as tar:
                    tar.extractall(path=target_folder_extracted)
            else:
                raise ValueError(f"Unknown extension: \"{extension}\"")
            GeneralUtilities.ensure_file_does_not_exist(local_zip_file)

        download_and_extract("Windows", "windows", "zip")
        download_and_extract("Linux", "linux", "tar.gz")
        download_and_extract("MacOS", "darwin", "tar.gz")

    @GeneralUtilities.check_arguments
    def ensure_cyclonedxcli_is_available(self, target_folder: str) -> None:
        local_filename = "cyclonedx-cli"
        filename_on_github: str
        if GeneralUtilities.current_system_is_windows():
            filename_on_github = "cyclonedx-win-x64.exe"
            local_filename = local_filename+".exe"
        else:
            filename_on_github = "cyclonedx-linux-x64"
        self.ensure_file_from_github_assets_is_available_with_retry(target_folder, "CycloneDX", "cyclonedx-cli", "CycloneDXCLI", local_filename, lambda latest_version: filename_on_github)

    @GeneralUtilities.check_arguments
    def ensure_file_from_github_assets_is_available_with_retry(self, target_folder: str, githubuser: str, githubprojectname: str, resource_name: str, local_filename: str, get_filename_on_github, amount_of_attempts: int = 5) -> None:
        GeneralUtilities.retry_action(lambda: self.ensure_file_from_github_assets_is_available(target_folder, githubuser, githubprojectname, resource_name, local_filename, get_filename_on_github), amount_of_attempts)

    @GeneralUtilities.check_arguments
    def ensure_file_from_github_assets_is_available(self, target_folder: str, githubuser: str, githubprojectname: str, resource_name: str, local_filename: str, get_filename_on_github) -> None:
        resource_folder = os.path.join(target_folder, "Other", "Resources", resource_name)
        internet_connection_is_available = GeneralUtilities.internet_connection_is_available()
        file = f"{resource_folder}/{local_filename}"
        file_exists = os.path.isfile(file)
        if internet_connection_is_available:  # Load/Update
            GeneralUtilities.ensure_directory_does_not_exist(resource_folder)
            GeneralUtilities.ensure_directory_exists(resource_folder)
            headers = {'Cache-Control': 'no-cache'}
            response = requests.get(f"https://api.github.com/repos/{githubuser}/{githubprojectname}/releases/latest", timeout=10, headers=headers)
            latest_version = response.json()["tag_name"]
            filename_on_github = get_filename_on_github(latest_version)
            link = f"https://github.com/{githubuser}/{githubprojectname}/releases/download/{latest_version}/{filename_on_github}"
            urllib.request.urlretrieve(link, file)
        else:
            if file_exists:
                GeneralUtilities.write_message_to_stdout(f"Warning: Can not check for updates of {resource_name} due to missing internet-connection.")
            else:
                raise ValueError(f"Can not download {resource_name}.")

    @GeneralUtilities.check_arguments
    def generate_svg_files_from_plantuml_files_for_repository(self, repository_folder: str) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        self.ensure_plantuml_is_available(repository_folder)
        plant_uml_folder = os.path.join(repository_folder, "Other", "Resources", "PlantUML")
        target_folder = os.path.join(repository_folder, "Other",  "Reference")
        self.__generate_svg_files_from_plantuml(target_folder, plant_uml_folder)

    @GeneralUtilities.check_arguments
    def generate_svg_files_from_plantuml_files_for_codeunit(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        repository_folder = os.path.dirname(codeunit_folder)
        self.ensure_plantuml_is_available(repository_folder)
        plant_uml_folder = os.path.join(repository_folder, "Other", "Resources", "PlantUML")
        target_folder = os.path.join(codeunit_folder, "Other", "Reference")
        self.__generate_svg_files_from_plantuml(target_folder, plant_uml_folder)

    @GeneralUtilities.check_arguments
    def __generate_svg_files_from_plantuml(self, diagrams_files_folder: str, plant_uml_folder: str) -> None:
        for file in GeneralUtilities.get_all_files_of_folder(diagrams_files_folder):
            if file.endswith(".plantuml"):
                output_filename = self.get_output_filename_for_plantuml_filename(file)
                argument = ['-jar', f'{plant_uml_folder}/plantuml.jar', '-tsvg', os.path.basename(file)]
                folder = os.path.dirname(file)
                self.__sc.run_program_argsasarray("java", argument, folder, verbosity=0)
                result_file = folder+"/" + output_filename
                GeneralUtilities.assert_file_exists(result_file)
                self.__sc.format_xml_file(result_file)

    @GeneralUtilities.check_arguments
    def get_output_filename_for_plantuml_filename(self, plantuml_file: str) -> str:
        for line in GeneralUtilities.read_lines_from_file(plantuml_file):
            prefix = "@startuml "
            if line.startswith(prefix):
                title = line[len(prefix):]
                return title+".svg"
        return Path(plantuml_file).stem+".svg"

    @GeneralUtilities.check_arguments
    def generate_codeunits_overview_diagram(self, repository_folder: str) -> None:
        self.__sc.assert_is_git_repository(repository_folder)
        project_name: str = os.path.basename(repository_folder)
        target_folder = os.path.join(repository_folder, "Other", "Reference", "Technical", "Diagrams")
        GeneralUtilities.ensure_directory_exists(target_folder)
        target_file = os.path.join(target_folder, "CodeUnits-Overview.plantuml")
        lines = ["@startuml CodeUnits-Overview"]
        lines.append(f"title CodeUnits of {project_name}")

        codeunits = self.get_codeunits(repository_folder)
        for codeunitname in codeunits:
            codeunit_file: str = os.path.join(repository_folder, codeunitname, f"{codeunitname}.codeunit.xml")

            description = self.get_codeunit_description(codeunit_file)

            lines.append(GeneralUtilities.empty_string)
            lines.append(f"[{codeunitname}]")
            lines.append(f"note as {codeunitname}Note")
            lines.append(f"  {description}")
            lines.append(f"end note")
            lines.append(f"{codeunitname} .. {codeunitname}Note")

        lines.append(GeneralUtilities.empty_string)
        for codeunitname in codeunits:
            codeunit_file: str = os.path.join(repository_folder, codeunitname, f"{codeunitname}.codeunit.xml")
            dependent_codeunits = self.get_dependent_code_units(codeunit_file)
            for dependent_codeunit in dependent_codeunits:
                lines.append(f"{codeunitname} --> {dependent_codeunit}")

        lines.append(GeneralUtilities.empty_string)
        lines.append("@enduml")

        GeneralUtilities.write_lines_to_file(target_file, lines)

    @GeneralUtilities.check_arguments
    def load_deb_control_file_content(self, file: str, codeunitname: str, codeunitversion: str, installedsize: int, maintainername: str, maintaineremail: str, description: str,) -> str:
        content = GeneralUtilities.read_text_from_file(file)
        content = GeneralUtilities.replace_variable_in_string(content, "codeunitname", codeunitname)
        content = GeneralUtilities.replace_variable_in_string(content, "codeunitversion", codeunitversion)
        content = GeneralUtilities.replace_variable_in_string(content, "installedsize", str(installedsize))
        content = GeneralUtilities.replace_variable_in_string(content, "maintainername", maintainername)
        content = GeneralUtilities.replace_variable_in_string(content, "maintaineremail", maintaineremail)
        content = GeneralUtilities.replace_variable_in_string(content, "description", description)
        return content

    @GeneralUtilities.check_arguments
    def calculate_deb_package_size(self, binary_folder: str) -> int:
        size_in_bytes = 0
        for file in GeneralUtilities.get_all_files_of_folder(binary_folder):
            size_in_bytes = size_in_bytes+os.path.getsize(file)
        result = math.ceil(size_in_bytes/1024)
        return result

    @GeneralUtilities.check_arguments
    def create_deb_package_for_artifact(self, codeunit_folder: str, maintainername: str, maintaineremail: str, description: str, verbosity: int, cmd_arguments: list[str]) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        verbosity = self.get_verbosity_from_commandline_arguments(cmd_arguments, verbosity)
        codeunit_name = os.path.basename(codeunit_folder)
        binary_folder = GeneralUtilities.resolve_relative_path("Other/Artifacts/BuildResult_DotNet_linux-x64", codeunit_folder)
        deb_output_folder = GeneralUtilities.resolve_relative_path("Other/Artifacts/BuildResult_Deb", codeunit_folder)
        control_file = GeneralUtilities.resolve_relative_path("Other/Build/DebControlFile.txt", codeunit_folder)
        installedsize = self.calculate_deb_package_size(binary_folder)
        control_file_content = self.load_deb_control_file_content(control_file, codeunit_name, self.get_version_of_codeunit_folder(codeunit_folder), installedsize, maintainername, maintaineremail, description)
        self.__sc.create_deb_package(codeunit_name, binary_folder, control_file_content, deb_output_folder, verbosity, 555)

    @GeneralUtilities.check_arguments
    def create_zip_file_for_artifact(self, codeunit_folder: str, artifact_source_name: str, name_of_new_artifact: str, verbosity: int, cmd_arguments: list[str]) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        verbosity = self.get_verbosity_from_commandline_arguments(cmd_arguments, verbosity)
        src_artifact_folder = GeneralUtilities.resolve_relative_path(f"Other/Artifacts/{artifact_source_name}", codeunit_folder)
        shutil.make_archive(name_of_new_artifact, 'zip', src_artifact_folder)
        archive_file = os.path.join(os.getcwd(), f"{name_of_new_artifact}.zip")
        target_folder = GeneralUtilities.resolve_relative_path(f"Other/Artifacts/{name_of_new_artifact}", codeunit_folder)
        GeneralUtilities.ensure_folder_exists_and_is_empty(target_folder)
        shutil.move(archive_file, target_folder)

    def generate_winget_zip_manifest(self, codeunit_folder: str, artifact_name_of_zip: str):
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_version = self.get_version_of_codeunit_folder(codeunit_folder)
        build_folder = os.path.join(codeunit_folder, "Other", "Build")
        artifacts_folder = os.path.join(codeunit_folder, "Other", "Artifacts", artifact_name_of_zip)
        manifest_folder = os.path.join(codeunit_folder, "Other", "Artifacts", "WinGet-Manifest")
        GeneralUtilities.assert_folder_exists(artifacts_folder)
        artifacts_file = self.__sc.find_file_by_extension(artifacts_folder, "zip")
        winget_template_file = os.path.join(build_folder, "WinGet-Template.yaml")
        winget_manifest_file = os.path.join(manifest_folder, "WinGet-Manifest.yaml")
        GeneralUtilities.assert_file_exists(winget_template_file)
        GeneralUtilities.ensure_directory_exists(manifest_folder)
        GeneralUtilities.ensure_file_exists(winget_manifest_file)
        manifest_content = GeneralUtilities.read_text_from_file(winget_template_file)
        manifest_content = GeneralUtilities.replace_variable_in_string(manifest_content, "version", codeunit_version)
        manifest_content = GeneralUtilities.replace_variable_in_string(manifest_content, "sha256_hashvalue", GeneralUtilities.get_sha256_of_file(artifacts_file))
        GeneralUtilities.write_text_to_file(winget_manifest_file, manifest_content)

    @GeneralUtilities.check_arguments
    def update_year_in_license_file_in_common_scripts_file(self, common_tasks_scripts_file: str) -> None:
        self.update_year_in_license_file(GeneralUtilities.resolve_relative_path("../../..", common_tasks_scripts_file))

    @GeneralUtilities.check_arguments
    def update_year_in_license_file(self, repository_folder: str) -> None:
        self.__sc.update_year_in_first_line_of_file(os.path.join(repository_folder, "License.txt"))

    @GeneralUtilities.check_arguments
    def update_year_for_dotnet_codeunit_in_common_scripts_file(self, common_tasks_scripts_file: str) -> None:
        self.update_year_for_dotnet_codeunit(GeneralUtilities.resolve_relative_path("../..", common_tasks_scripts_file))

    @GeneralUtilities.check_arguments
    def update_year_for_dotnet_codeunit(self, codeunit_folder: str) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name = os.path.basename(codeunit_folder)
        csproj_file = os.path.join(codeunit_folder, codeunit_name, f"{codeunit_name}.csproj")
        self.__sc.update_year_in_copyright_tags(csproj_file)
        csprojtests_file = os.path.join(codeunit_folder, f"{codeunit_name}Tests", f"{codeunit_name}Tests.csproj")
        self.__sc.update_year_in_copyright_tags(csprojtests_file)
        nuspec_file = os.path.join(codeunit_folder, "Other", "Build", f"{codeunit_name}.nuspec")
        if os.path.isfile(nuspec_file):
            self.__sc.update_year_in_copyright_tags(nuspec_file)

    @GeneralUtilities.check_arguments
    def repository_has_codeunits(self, repository: str, ignore_disabled_codeunits: bool = True) -> bool:
        return len(self.get_codeunits(repository, ignore_disabled_codeunits))

    @GeneralUtilities.check_arguments
    def verify_artifact_exists(self, codeunit_folder: str, artifact_name_regexes: dict[str, bool]) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        codeunit_name: str = os.path.basename(codeunit_folder)
        artifacts_folder = os.path.join(codeunit_folder, "Other/Artifacts")
        existing_artifacts = [os.path.basename(x) for x in GeneralUtilities.get_direct_folders_of_folder(artifacts_folder)]
        for artifact_name_regex, required in artifact_name_regexes.items():
            artifact_exists = False
            for existing_artifact in existing_artifacts:
                pattern = re.compile(artifact_name_regex)
                if pattern.match(existing_artifact):
                    artifact_exists = True
            if not artifact_exists:
                message = f"Codeunit {codeunit_name} does not contain an artifact which matches the name '{artifact_name_regex}'."
                if required:
                    raise ValueError(message)
                else:
                    GeneralUtilities.write_message_to_stderr(f"Warning: {message}")

    @GeneralUtilities.check_arguments
    def __build_codeunit(self, codeunit_folder: str, verbosity: int = 1, target_environmenttype: str = "QualityCheck", additional_arguments_file: str = None, is_pre_merge: bool = False, assume_dependent_codeunits_are_already_built: bool = False, commandline_arguments: list[str] = []) -> None:
        self.assert_is_codeunit_folder(codeunit_folder)
        now = datetime.now()
        codeunit_folder = GeneralUtilities.resolve_relative_path_from_current_working_directory(codeunit_folder)
        repository_folder = GeneralUtilities.resolve_relative_path("..", codeunit_folder)
        codeunit_name: str = os.path.basename(codeunit_folder)
        if verbosity > 2:
            GeneralUtilities.write_message_to_stdout(f"Start building codeunit {codeunit_name}")
        codeunit_file = os.path.join(codeunit_folder, f"{codeunit_name}.codeunit.xml")

        if (not os.path.isfile(codeunit_file)):
            raise ValueError(f'"{codeunit_folder}" is no codeunit-folder.')

        if not self.codeunit_is_enabled(codeunit_file):
            GeneralUtilities.write_message_to_stdout(f"Warning: Codeunit {codeunit_name} is disabled.")
            return

        GeneralUtilities.write_message_to_stdout(f"Start building codeunit {codeunit_name}.")
        GeneralUtilities.write_message_to_stdout(f"Build-environmenttype: {target_environmenttype}")
        if not self.__sc.git_repository_has_uncommitted_changes(repository_folder):
            self.__sc.run_program("git", "clean -dfx", codeunit_folder)

        verbosity_for_executed_programs = self.get_verbosity_from_commandline_arguments(commandline_arguments, verbosity)

        other_folder = os.path.join(codeunit_folder, "Other")
        build_folder = os.path.join(other_folder, "Build")
        quality_folder = os.path.join(other_folder, "QualityCheck")
        reference_folder = os.path.join(other_folder, "Reference")
        additional_arguments_c: str = GeneralUtilities.empty_string
        additional_arguments_b: str = GeneralUtilities.empty_string
        additional_arguments_r: str = GeneralUtilities.empty_string
        additional_arguments_l: str = GeneralUtilities.empty_string
        additional_arguments_g: str = GeneralUtilities.empty_string
        additional_arguments_f: str = GeneralUtilities.empty_string
        general_argument = f' --overwrite_verbosity {str(verbosity)} --overwrite_targetenvironmenttype {target_environmenttype}'

        c_additionalargumentsfile_argument = GeneralUtilities.empty_string

        if is_pre_merge:
            general_argument = general_argument+" --overwrite_is_pre_merge true"
            GeneralUtilities.write_message_to_stdout("This is a pre-merge-build")

        if assume_dependent_codeunits_are_already_built:
            c_additionalargumentsfile_argument = c_additionalargumentsfile_argument+" --overwrite_assume_dependent_codeunits_are_already_built true"
            diagnostic = False
            if diagnostic:
                GeneralUtilities.write_message_to_stdout("Assume dependent codeunits are already built")

        if additional_arguments_file is not None:
            config = configparser.ConfigParser()
            config.read(additional_arguments_file)
            section_name = f"{codeunit_name}_Configuration"
            if config.has_option(section_name, "ArgumentsForCommonTasks"):
                additional_arguments_c = " " + config.get(section_name, "ArgumentsForCommonTasks")
            if config.has_option(section_name, "ArgumentsForBuild"):
                additional_arguments_b = " " + config.get(section_name, "ArgumentsForBuild")
            if config.has_option(section_name, "ArgumentsForRunTestcases"):
                additional_arguments_r = " " + config.get(section_name, "ArgumentsForRunTestcases")
            if config.has_option(section_name, "ArgumentsForLinting"):
                additional_arguments_l = " " + config.get(section_name, "ArgumentsForLinting")
            if config.has_option(section_name, "ArgumentsForGenerateReference"):
                additional_arguments_g = " " + config.get(section_name, "ArgumentsForGenerateReference")
            if config.has_option(section_name, "ArgumentsForOnFinish"):
                additional_arguments_f = " " + config.get(section_name, "ArgumentsForOnFinish")
            c_additionalargumentsfile_argument = f' --overwrite_additionalargumentsfile "{additional_arguments_file}"'

        GeneralUtilities.write_message_to_stdout('Run "CommonTasks.py"...')
        self.__sc.run_program("python", f"CommonTasks.py{additional_arguments_c}{general_argument}{c_additionalargumentsfile_argument}", other_folder, verbosity=verbosity_for_executed_programs, throw_exception_if_exitcode_is_not_zero=True, print_live_output=2 < verbosity)
        self.verify_artifact_exists(codeunit_folder, dict[str, bool]({"Changelog": False, "License": True, "DiffReport": True}))

        GeneralUtilities.write_message_to_stdout('Run "Build.py"...')
        self.__sc.run_program("python", f"Build.py{additional_arguments_b}{general_argument}", build_folder, verbosity=verbosity_for_executed_programs, throw_exception_if_exitcode_is_not_zero=True, print_live_output=2 < verbosity)

        artifacts = {"BuildResult_.+": True, "BOM": False, "SourceCode": True}
        if self.codeunit_has_testable_sourcecode(codeunit_file):
            artifacts["CodeAnalysisResult"] = False
        self.verify_artifact_exists(codeunit_folder, dict[str, bool](artifacts))

        codeunit_hast_testable_sourcecode = self.codeunit_has_testable_sourcecode(codeunit_file)
        if codeunit_hast_testable_sourcecode:
            GeneralUtilities.write_message_to_stdout('Run "RunTestcases.py"...')
            self.__sc.run_program("python", f"RunTestcases.py{additional_arguments_r}{general_argument}", quality_folder, verbosity=verbosity_for_executed_programs, throw_exception_if_exitcode_is_not_zero=True, print_live_output=2 < verbosity)
            self.verify_artifact_exists(codeunit_folder, dict[str, bool]({"TestCoverage": True, "TestCoverageReport": False}))

        GeneralUtilities.write_message_to_stdout('Run "Linting.py"...')
        self.__sc.run_program("python", f"Linting.py{additional_arguments_l}{general_argument}", quality_folder, verbosity=verbosity_for_executed_programs, throw_exception_if_exitcode_is_not_zero=True, print_live_output=2 < verbosity)
        self.verify_artifact_exists(codeunit_folder, dict[str, bool]())

        GeneralUtilities.write_message_to_stdout('Run "GenerateReference.py"...')
        self.__sc.run_program("python", f"GenerateReference.py{additional_arguments_g}{general_argument}", reference_folder, verbosity=verbosity_for_executed_programs, throw_exception_if_exitcode_is_not_zero=True, print_live_output=2 < verbosity)
        self.verify_artifact_exists(codeunit_folder, dict[str, bool]({"Reference": True}))

        if os.path.isfile(os.path.join(other_folder, "OnBuildingFinished.py")):
            GeneralUtilities.write_message_to_stdout('Run "OnBuildingFinished.py"...')
            self.__sc.run_program("python", f"OnBuildingFinished.py{additional_arguments_f}{general_argument}", other_folder, verbosity=verbosity_for_executed_programs, throw_exception_if_exitcode_is_not_zero=True, print_live_output=2 < verbosity)

        artifacts_folder = os.path.join(codeunit_folder, "Other", "Artifacts")
        artifactsinformation_file = os.path.join(artifacts_folder, f"{codeunit_name}.artifactsinformation.xml")
        codeunit_version = self.get_version_of_codeunit(codeunit_file)
        GeneralUtilities.ensure_file_exists(artifactsinformation_file)
        artifacts_list = []
        for artifact_folder in GeneralUtilities.get_direct_folders_of_folder(artifacts_folder):
            artifact_name = os.path.basename(artifact_folder)
            artifacts_list.append(f"        <cps:artifact>{artifact_name}<cps:artifact>")
        artifacts = '\n'.join(artifacts_list)
        moment = GeneralUtilities.datetime_to_string(now)
        # TODO implement usage of self.reference_latest_version_of_xsd_when_generating_xml
        GeneralUtilities.write_text_to_file(artifactsinformation_file, f"""<?xml version="1.0" encoding="UTF-8" ?>
<cps:artifactsinformation xmlns:cps="https://projects.aniondev.de/PublicProjects/Common/ProjectTemplates/-/tree/main/Conventions/RepositoryStructure/CommonProjectStructure" artifactsinformationspecificationversion="1.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://raw.githubusercontent.com/anionDev/ProjectTemplates/main/Templates/Conventions/RepositoryStructure/CommonProjectStructure/artifactsinformation.xsd">
    <cps:name>{codeunit_name}</cps:name>
    <cps:version>{codeunit_version}</cps:version>
    <cps:timestamp>{moment}</cps:timestamp>
    <cps:targetenvironmenttype>{target_environmenttype}</cps:targetenvironmenttype>
    <cps:artifacts>
{artifacts}
    </cps:artifacts>
</cps:artifactsinformation>""")
        # TODO validate artifactsinformation_file against xsd
        GeneralUtilities.write_message_to_stdout(f"Finished building codeunit {codeunit_name} without errors.")

    def __ensure_changelog_file_is_added(self, repository_folder: str, version_of_project: str):
        changelog_file = os.path.join(repository_folder, "Other", "Resources", "Changelog", f"v{version_of_project}.md")
        if not os.path.isfile(changelog_file):
            GeneralUtilities.ensure_file_exists(changelog_file)
            GeneralUtilities.write_text_to_file(changelog_file, """# Release notes

## Changes

- Updated dependencies.
""")

    @GeneralUtilities.check_arguments
    def generic_update_dependencies(self, repository_folder: str, verbosity: int = 1):
        # Prepare
        GeneralUtilities.write_message_to_stdout("Update dependencies...")
        self.__sc.assert_is_git_repository(repository_folder)
        codeunits = self.get_codeunits(repository_folder)
        update_dependencies_script_filename = "UpdateDependencies.py"
        target_environmenttype = "QualityCheck"
        project_name: str = os.path.basename(repository_folder)
        GeneralUtilities.assert_condition(not self.__sc.git_repository_has_uncommitted_changes(repository_folder), "There are uncommitted changes in the repository.")
        self.build_codeunits(repository_folder, target_environmenttype=target_environmenttype, do_git_clean_when_no_changes=True, note="Prepare dependency-update")  # Required because update dependencies is not always possible for not-buildet codeunits (depends on the programming language or package manager)

        # update dependencies of resources
        global_scripts_folder = os.path.join(repository_folder, "Other", "Scripts")
        if os.path.isfile(os.path.join(global_scripts_folder, update_dependencies_script_filename)):
            self.__sc.run_program("python", update_dependencies_script_filename, global_scripts_folder, print_live_output=True)
            version_of_project = self.get_version_of_project(repository_folder)
            self.__ensure_changelog_file_is_added(repository_folder, version_of_project)
            GeneralUtilities.write_message_to_stdout(f"Updated global dependencies of {project_name}.")
            self.build_codeunits(repository_folder, verbosity, "QualityCheck", None, False, None, [], False, "Build codeunits due to updated product-wide dependencies")

        # update dependencies of codeunits
        for codeunit in codeunits:
            codeunit_file = os.path.join(repository_folder, codeunit, f"{codeunit}.codeunit.xml")
            codeunit_has_updatable_dependencies = self.codeunit_has_updatable_dependencies(codeunit_file)
            codeunit_folder: str = os.path.join(repository_folder, codeunit)
            self.build_codeunit(codeunit_folder, verbosity, "QualityCheck", None, False, None, False, [])
            if codeunit_has_updatable_dependencies:
                codeunit_folder = os.path.join(repository_folder, codeunit)
                update_dependencies_script_folder = os.path.join(codeunit_folder, "Other")
                GeneralUtilities.ensure_directory_exists(os.path.join(update_dependencies_script_folder, "Resources", "CodeAnalysisResult"))
                self.__sc.run_program("python", update_dependencies_script_filename, update_dependencies_script_folder, verbosity, print_live_output=True)
                if self.__sc.git_repository_has_uncommitted_changes(repository_folder):
                    version_of_project = self.get_version_of_project(repository_folder)
                    self.__ensure_changelog_file_is_added(repository_folder, version_of_project)
                    GeneralUtilities.write_message_to_stdout(f"Updated dependencies in codeunit {codeunit}.")

        self.build_codeunits(repository_folder, verbosity, "QualityCheck", None, False, None, [], False, "Build all codeunits due to updated dependencies")
        self.__sc.git_commit(repository_folder, "Updated dependencies")

    class GenericPrepareNewReleaseArguments:
        current_file: str
        product_name: str
        commandline_arguments: list[str]

        def __init__(self, current_file: str, product_name: str, commandline_arguments: list[str]):
            self.current_file = current_file
            self.product_name = product_name
            self.commandline_arguments = commandline_arguments

    @GeneralUtilities.check_arguments
    def generic_prepare_new_release(self, generic_prepare_new_release_arguments: GenericPrepareNewReleaseArguments):
        GeneralUtilities.write_message_to_stdout(f"Prepare release for {generic_prepare_new_release_arguments.product_name}.")

        # constants
        folder_of_this_file = os.path.dirname(generic_prepare_new_release_arguments.current_file)
        build_repository_folder = GeneralUtilities.resolve_relative_path("../..", folder_of_this_file)
        self.__sc.assert_is_git_repository(build_repository_folder)

        repository_folder = GeneralUtilities.resolve_relative_path(f"../../Submodules/{generic_prepare_new_release_arguments.product_name}", folder_of_this_file)
        self.__sc.assert_is_git_repository(repository_folder)
        reference_folder = repository_folder+"Reference"
        self.__sc.assert_is_git_repository(reference_folder)
        verbosity: int = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(generic_prepare_new_release_arguments.commandline_arguments, 1)

        merge_source_branch = "other/next-release"  # maybe this should be configurable
        main_branch = "main"  # maybe this should be configurable

        # prepare
        self.assert_no_uncommitted_changes(repository_folder)
        self.assert_no_uncommitted_changes(reference_folder)
        self.assert_no_uncommitted_changes(build_repository_folder)
        self.__sc.git_checkout(build_repository_folder, "main", True)
        self.__sc.git_checkout(repository_folder, merge_source_branch, True)
        self.__sc.git_checkout(reference_folder, "main", True)
        self.assert_no_uncommitted_changes(repository_folder)
        self.assert_no_uncommitted_changes(reference_folder)
        self.__sc.git_commit(build_repository_folder, "Updated submodules")

        if "--dependencyupdate" in generic_prepare_new_release_arguments.commandline_arguments:
            GeneralUtilities.write_message_to_stdout("Debug: Update dependencies...")
            self.generic_update_dependencies(repository_folder)
            self.assert_no_uncommitted_changes(repository_folder)
        else:
            GeneralUtilities.write_message_to_stdout("Debug: Dependency-update skipped.")

        GeneralUtilities.write_message_to_stdout(f"Check reference-repository...")
        now = datetime.now()
        for unsupported_version in self.get_unsupported_versions(repository_folder, now):
            reference_folder = f"{reference_folder}/ReferenceContent/v{unsupported_version}"
            GeneralUtilities.ensure_directory_does_not_exist(reference_folder)
        self.__sc.git_commit(reference_folder, "Removed reference of outdated versions.")

        merge_source_branch_commit_id = self.__sc.git_get_commit_id(repository_folder, merge_source_branch)
        main_branch_commit_id = self.__sc.git_get_commit_id(repository_folder, main_branch)
        if merge_source_branch_commit_id == main_branch_commit_id:
            GeneralUtilities.write_message_to_stdout("Release will not be prepared because there are no changed which can be released.")
        else:
            self.merge_to_main_branch(repository_folder, merge_source_branch, verbosity=verbosity, fast_forward_source_branch=True)
            self.__sc.git_commit(build_repository_folder, "Updated submodule due to merge to main-branch.")
        GeneralUtilities.write_message_to_stdout(f"Finished prepare release for {generic_prepare_new_release_arguments.product_name}.")

    class GenericCreateReleaseArguments():
        current_file: str
        product_name: str
        common_remote_name: str
        artifacts_target_folder: str
        commandline_arguments: list[str]

        def __init__(self, current_file: str, product_name: str, common_remote_name: str, artifacts_target_folder: str, commandline_arguments: list[str]):
            self.current_file = current_file
            self.product_name = product_name
            self.common_remote_name = common_remote_name
            self.artifacts_target_folder = artifacts_target_folder
            self.commandline_arguments = commandline_arguments

    @GeneralUtilities.check_arguments
    def generic_create_release(self, generic_create_release_arguments: GenericCreateReleaseArguments) -> tuple[bool, str]:
        GeneralUtilities.write_message_to_stdout(f"Create release for {generic_create_release_arguments.product_name}.")
        folder_of_this_file = os.path.dirname(generic_create_release_arguments.current_file)
        build_repository_folder = GeneralUtilities.resolve_relative_path("../..", folder_of_this_file)
        repository_folder_name = generic_create_release_arguments.product_name
        repository_folder = GeneralUtilities.resolve_relative_path(f"../../Submodules/{generic_create_release_arguments.product_name}", folder_of_this_file)
        self.__sc.assert_is_git_repository(repository_folder)

        merge_source_branch = "main"  # TODO make this configurable
        main_branch = "stable"  # TODO make this configurable

        additional_arguments_file = os.path.join(folder_of_this_file, "AdditionalArguments.configuration")
        verbosity: int = TasksForCommonProjectStructure.get_verbosity_from_commandline_arguments(generic_create_release_arguments.commandline_arguments, 1)
        createReleaseConfiguration: CreateReleaseConfiguration = CreateReleaseConfiguration(generic_create_release_arguments.product_name, generic_create_release_arguments.common_remote_name, generic_create_release_arguments.artifacts_target_folder, folder_of_this_file, verbosity, repository_folder, additional_arguments_file, repository_folder_name)

        merge_source_branch_commit_id = self.__sc.git_get_commit_id(repository_folder, merge_source_branch)
        main_branch_commit_id = self.__sc.git_get_commit_id(repository_folder, main_branch)
        if merge_source_branch_commit_id == main_branch_commit_id:
            GeneralUtilities.write_message_to_stdout("Release will not be done because there are no changed which can be released.")
            return False, None
        else:
            self.__sc.git_checkout(repository_folder, merge_source_branch)
            reference_repo: str = os.path.join(build_repository_folder, "Submodules", f"{generic_create_release_arguments.product_name}Reference")
            self.__sc.git_commit(reference_repo, "Updated reference")
            self.__sc.git_push_with_retry(reference_repo, generic_create_release_arguments.common_remote_name, "main", "main")
            self.__sc.git_commit(build_repository_folder, "Updated submodule")

            # create release
            new_version = self.merge_to_stable_branch(generic_create_release_arguments.current_file, createReleaseConfiguration)
            GeneralUtilities.write_message_to_stdout(f"Finished create release for {generic_create_release_arguments.product_name}.")
            return True, new_version

    class UpdateHTTPDocumentationArguments:
        current_file: str
        product_name: str
        common_remote_name: str
        new_project_version: str
        reference_repository_name: str
        commandline_arguments: list[str]
        main_branch_name: str

        def __init__(self, current_file: str, product_name: str, common_remote_name: str, new_project_version: str, reference_repository_name: str, commandline_arguments: list[str]):
            self.current_file = current_file
            self.product_name = product_name
            self.common_remote_name = common_remote_name
            self.new_project_version = new_project_version
            self.reference_repository_name = reference_repository_name
            self.commandline_arguments = commandline_arguments
            self.main_branch_name = "main"

    @GeneralUtilities.check_arguments
    def create_changelog_entry(self, repositoryfolder: str, message: str, commit: bool, force: bool):
        self.__sc.assert_is_git_repository(repositoryfolder)
        random_file = os.path.join(repositoryfolder, str(uuid.uuid4()))
        if force and not self.__sc.git_repository_has_uncommitted_changes(repositoryfolder):
            GeneralUtilities.ensure_file_exists(random_file)
        current_version = self.get_version_of_project(repositoryfolder)
        changelog_file = os.path.join(repositoryfolder, "Other", "Resources", "Changelog", f"v{current_version}.md")
        if os.path.isfile(changelog_file):
            GeneralUtilities.write_message_to_stdout(f"Changelog-file '{changelog_file}' already exists.")
        else:
            GeneralUtilities.ensure_file_exists(changelog_file)
            GeneralUtilities.write_text_to_file(changelog_file, f"""# Release notes

## Changes

- {message}
""")
        GeneralUtilities.ensure_file_does_not_exist(random_file)
        if commit:
            self.__sc.git_commit(repositoryfolder, f"Added changelog-file for v{current_version}.")

    @GeneralUtilities.check_arguments
    def update_http_documentation(self, update_http_documentation_arguments: UpdateHTTPDocumentationArguments):
        GeneralUtilities.write_message_to_stdout(f"Update HTTP-documentation for for {update_http_documentation_arguments.product_name}...")
        folder_of_this_file = str(os.path.dirname(update_http_documentation_arguments.current_file))

        ref_repo = GeneralUtilities.resolve_relative_path(f"../../Submodules/{update_http_documentation_arguments.reference_repository_name}", folder_of_this_file)
        self.__sc.assert_is_git_repository(ref_repo)
        self.__sc.git_checkout(ref_repo, update_http_documentation_arguments.main_branch_name)

        # update reference
        target = os.path.join(ref_repo, "Reference", update_http_documentation_arguments.product_name)
        GeneralUtilities.ensure_directory_does_not_exist(target)
        shutil.copytree(GeneralUtilities.resolve_relative_path(f"../../Submodules/{update_http_documentation_arguments.product_name}Reference/ReferenceContent", folder_of_this_file), target)
        self.__sc.git_commit(ref_repo, f"Added reference of {update_http_documentation_arguments.product_name} v{update_http_documentation_arguments.new_project_version}")

        # Sync reference-repository
        self.__sc.git_fetch(ref_repo, update_http_documentation_arguments.common_remote_name)
        self.__sc.git_merge(ref_repo, update_http_documentation_arguments.common_remote_name+"/"+update_http_documentation_arguments.main_branch_name, update_http_documentation_arguments.main_branch_name)
        self.__sc.git_checkout(ref_repo, update_http_documentation_arguments.main_branch_name)
        self.__sc.git_push_with_retry(ref_repo, update_http_documentation_arguments.common_remote_name, update_http_documentation_arguments.main_branch_name, update_http_documentation_arguments.main_branch_name)
        self.__sc.git_commit(GeneralUtilities.resolve_relative_path("../..", folder_of_this_file), f"Updated content of {update_http_documentation_arguments.product_name} v{update_http_documentation_arguments.new_project_version} in {update_http_documentation_arguments.reference_repository_name}-submodule")

    @GeneralUtilities.check_arguments
    def install_requirementstxt_for_codeunit(self, codeunit_folder: str, verbosity: int):
        self.__sc.install_requirementstxt_file(codeunit_folder+"/Other/requirements.txt", verbosity)

    @GeneralUtilities.check_arguments
    def install_requirementstxt_for_repository(self, repository_folde: str, verbosity: int):
        self.__sc.install_requirementstxt_file(repository_folde+"/Other/requirements.txt", verbosity)

    @GeneralUtilities.check_arguments
    def update_submodule(self, repository_folder: str, submodule_name: str, local_branch: str = "main", remote_branch: str = "main", remote: str = "origin"):
        submodule_folder = GeneralUtilities.resolve_relative_path("Other/Resources/Submodules/"+submodule_name, repository_folder)
        self.__sc.git_fetch(submodule_folder, remote)
        self.__sc.git_checkout(submodule_folder, local_branch)
        self.__sc.git_pull(submodule_folder, remote, local_branch, remote_branch, True)
        current_version = self.__sc.get_semver_version_from_gitversion(repository_folder)
        changelog_file = os.path.join(repository_folder, "Other", "Resources", "Changelog", f"v{current_version}.md")
        if (not os.path.isfile(changelog_file)):
            GeneralUtilities.ensure_file_exists(changelog_file)
            GeneralUtilities.write_text_to_file(changelog_file, """# Release notes

## Changes

- Updated geo-ip-database.
""")

    @GeneralUtilities.check_arguments
    def update_images_in_example(self, codeunit_folder: str):
        iu = ImageUpdater()
        iu.add_default_mapper()
        dockercomposefile: str = f"{codeunit_folder}\\Other\\Reference\\ReferenceContent\\Examples\\MinimalDockerComposeFile\\docker-compose.yml"
        excluded = ["opendms"]
        iu.update_all_services_in_docker_compose_file(dockercomposefile, VersionEcholon.LatestPatchOrLatestMinor, excluded)
        iu.check_for_newest_version(dockercomposefile, excluded)

    @GeneralUtilities.check_arguments
    def clone_repository_as_resource(self, local_repository_folder: str, remote_repository_link: str, resource_name: str, repository_subname: str = None) -> None:
        GeneralUtilities.write_message_to_stdout(f'Clone resource {resource_name}...')
        resrepo_commit_id_folder: str = os.path.join(local_repository_folder, "Other", "Resources", f"{resource_name}Version")
        resrepo_commit_id_file: str = os.path.join(resrepo_commit_id_folder, f"{resource_name}Version.txt")
        latest_version: str = GeneralUtilities.read_text_from_file(resrepo_commit_id_file)
        resrepo_data_folder: str = os.path.join(local_repository_folder, "Other", "Resources", resource_name).replace("\\", "/")
        current_version: str = None
        resrepo_data_version: str = os.path.join(resrepo_data_folder, f"{resource_name}Version.txt")
        if os.path.isdir(resrepo_data_folder):
            if os.path.isfile(resrepo_data_version):
                current_version = GeneralUtilities.read_text_from_file(resrepo_data_version)
        if (current_version is None) or (current_version != latest_version):
            target_folder: str = resrepo_data_folder
            if repository_subname is not None:
                target_folder = f"{resrepo_data_folder}/{repository_subname}"
            GeneralUtilities.ensure_folder_exists_and_is_empty(target_folder)
            self.__sc.run_program("git", f"clone --recurse-submodules {remote_repository_link} {target_folder}")
            self.__sc.run_program("git", f"checkout {latest_version}", target_folder)
            GeneralUtilities.write_text_to_file(resrepo_data_version, latest_version)

            git_folders: list[str] = []
            git_files: list[str] = []
            for dirpath, dirnames, filenames in os.walk(target_folder):
                for dirname in dirnames:
                    if dirname == ".git":
                        full_path = os.path.join(dirpath, dirname)
                        git_folders.append(full_path)
                for filename in filenames:
                    if filename == ".git":
                        full_path = os.path.join(dirpath, filename)
                        git_files.append(full_path)
            for git_folder in git_folders:
                if os.path.isdir(git_folder):
                    GeneralUtilities.ensure_directory_does_not_exist(git_folder)
            for git_file in git_files:
                if os.path.isdir(git_file):
                    GeneralUtilities.ensure_file_does_not_exist(git_file)

    def set_latest_version_for_clone_repository_as_resource(self, resourcename: str, github_link: str, branch: str = "main"):
        current_file = str(Path(__file__).absolute())
        repository_folder = GeneralUtilities.resolve_relative_path("../../..", current_file)

        resrepo_commit_id_folder: str = os.path.join(repository_folder, "Other", "Resources", f"{resourcename}Version")
        resrepo_commit_id_file: str = os.path.join(resrepo_commit_id_folder, f"{resourcename}Version.txt")
        current_version: str = GeneralUtilities.read_text_from_file(resrepo_commit_id_file)

        stdOut = [l.split("\t") for l in GeneralUtilities.string_to_lines(self.__sc.run_program("git", f"ls-remote {github_link}")[1])]
        stdOut = [l for l in stdOut if l[1] == f"refs/heads/{branch}"]
        GeneralUtilities.assert_condition(len(stdOut) == 1)
        latest_version: str = stdOut[0][0]
        if current_version != latest_version:
            GeneralUtilities.write_text_to_file(resrepo_commit_id_file, latest_version)
