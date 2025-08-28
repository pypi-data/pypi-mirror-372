# Copyright (C) 2022 Alteryx, Inc. All rights reserved.
#
# Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT;
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Converts file provider classes to and from XML and CSV files."""
from pathlib import Path
from typing import Any, Dict, List, Set
from xml.parsers.expat import ExpatError

from ayx_python_sdk.core.field import FieldType
from ayx_python_sdk.core.metadata import Metadata
from ayx_python_sdk.providers.file_provider.file_provider_input_anchor import (
    FileProviderInputAnchor,
)
from ayx_python_sdk.providers.file_provider.file_provider_output_anchor import (
    FileProviderOutputAnchor,
)

import pandas as pd

import xmltodict


class FileAdapter:
    """
    File adapter class definition.

    This class converts input files into file provider objects and
    then also converts file provider objects back into output files.
    """

    def __init__(self, tool_config: Path, workflow_config: Path):
        """
        Instantiate a file adapter.

        Parameters
        ----------
        tool_config
            The path to the XML file that contains the tool configuration.
        workflow_config
            The path to the XML file that contains the anchor configurations.
        """
        config = self.convert_to_dict(tool_config)
        self.tool_config: Dict[str, Any] = config["Configuration"]
        self.workflow_config = self.convert_to_dict(workflow_config)
        tool_info = self.workflow_config["AlteryxJavaScriptPlugin"]["Properties"][
            "MetaInfo"
        ]
        self.name = tool_info["Name"]
        self.description = tool_info["Description"]
        self.use_append: Set = set()

    def convert_to_dict(self, xml_file: Path) -> Dict[str, Any]:
        """
        Convert a XML file to a Python dictionary.

        Parameters
        ----------
        xml_file
            The XML file that should be converted to a Python dictionary.

        Returns
        -------
        Dict[str, Any]
            The anchor configuration information.
        """
        try:
            with open(xml_file) as fd:
                return dict(xmltodict.parse(fd.read(), strip_whitespace=True))
        except ExpatError:
            raise RuntimeError(
                f"Error while parsing file {xml_file}, make sure that this file is well-formed"
            )

    def csv_to_dataframe(self, input_file: Path) -> pd.DataFrame:
        """
        Convert a CSV file to a pandas dataframe.

        Parameters
        ----------
        input_file
            The input CSV file that should be converted to a pandas dataframe.

        Returns
        -------
        pandas.Dataframe
            The pandas dataframe that contains the input records.
        """
        return pd.read_csv(input_file)

    def xml_to_metadata(self, xml_file: Path) -> Metadata:
        """
        Convert an XML file to record metadata.

        Parameters
        ----------
        xml_file
            The XML file that should be converted to Metadata.

        Returns
        -------
        Metadata
            The metadata information from the incoming XML file.
        """
        try:
            metadata = Metadata()
            metadata_dict = self.convert_to_dict(xml_file)
            # Iterate through each element of the XML called "Field"
            fields = metadata_dict["RecordInfo"]["Field"]
            for field in fields:
                name = field["@name"]  # required
                field_type = FieldType(field["@type"])  # required
                size = int(field.get("@size", 0))
                scale = int(field.get("@scale", 0))
                source = field.get("@source", "")
                desc = field.get("@description", "")
                metadata.add_field(
                    name=name,
                    field_type=field_type,
                    size=size,
                    scale=scale,
                    source=source,
                    description=desc,
                )

            return metadata
        # Add additional context to why KeyError occured
        except KeyError:
            # TODO: log error messages (all of them not just this function) instead of printing it when logging goes into file provider
            print("Metadata XML is missing attributes.")
            print(
                "The Metadata XML must have a 'RecordInfo' element as the root element, with 'Field' elements as its children."
            )
            print(
                "Each 'Field' element in the metadata file must have the following attributes: 'name', 'size', 'type'."
            )
            raise

    # TODO Remove duplicate code in build_input_anchors and build_output_anchors
    def build_input_anchors(self) -> List[FileProviderInputAnchor]:
        """
        Build the input anchors based on anchor configuration settings.

        Returns
        -------
        List[FileProviderInputAnchor]
            The list of file provider input anchor information.
        """
        try:
            anchor_settings = self.workflow_config["AlteryxJavaScriptPlugin"][
                "GuiSettings"
            ]

            input_anchors = anchor_settings.get("InputConnections")
            if not input_anchors:
                input_anchor_configs = []
            else:
                input_anchor_configs_raw = input_anchors["Connection"]
                if not isinstance(input_anchor_configs_raw, list):
                    input_anchor_configs = [input_anchor_configs_raw]
                else:
                    input_anchor_configs = input_anchor_configs_raw

            return [
                FileProviderInputAnchor(
                    name=config["@Name"],
                    allow_multiple=config["@AllowMultiple"].lower() == "true",
                    optional=config["@Optional"].lower() == "true",
                )
                for config in input_anchor_configs
            ]
        # error to add more context to KeyError
        except KeyError:
            print("Tool's workflow config XML is missing attributes.")
            print(
                "Each Connection in the config file must have the following attributes: 'Name', 'AllowMultiple', 'Optional'"
            )
            raise

    def build_output_anchors(self) -> List[FileProviderOutputAnchor]:
        """
        Build the output anchors based on tool config settings.

        Returns
        -------
        List[FileProviderOutputAnchor]
            The list of file provider output anchor information.
        """
        try:
            anchor_settings = self.workflow_config["AlteryxJavaScriptPlugin"][
                "GuiSettings"
            ]

            output_anchors = anchor_settings.get("OutputConnections")

            if not output_anchors:
                output_anchor_configs = []
            else:
                output_anchor_configs_raw = output_anchors["Connection"]
                if not isinstance(output_anchor_configs_raw, list):
                    output_anchor_configs = [output_anchor_configs_raw]
                else:
                    output_anchor_configs = output_anchor_configs_raw

            return [
                FileProviderOutputAnchor(
                    name=config["@Name"],
                    allow_multiple=False,
                    optional=config["@Optional"].lower() == "true",
                )
                for config in output_anchor_configs
            ]
        # Add more context to why KeyError occured
        except KeyError:
            # TODO: Add logging instead of printing
            print("Tool's workflow config XML is missing attributes.")
            print(
                "Each Connection in the config file must have the following attributes: 'Name', 'AllowMultiple', 'Optional'"
            )
            raise

    def dataframe_to_csv(self, output_file: Path, dataframe: pd.DataFrame) -> None:
        """
        Convert a pandas dataframe to an output CSV file.

        Parameters
        ----------
        output_file
            The path for the output file where the dataframe values should be held.
        dataframe
            The pandas dataframe that should be converted to a CSV file.
        """
        # TODO Add error handling for to_csv
        dataframe.to_csv(
            output_file,
            index=False,
            mode="a" if output_file in self.use_append else "w",
            header=False if output_file in self.use_append else True,
        )
        self.use_append.add(output_file)

    def metadata_to_xml(self, output_file: Path, metadata: Metadata) -> None:
        """
        Convert record metadata to a XML file.

        Parameters
        ----------
        output_file
            The path for the output file where the metadata information should be held.
        metadata
            The Metadata that should be converted to a XML file.
        """
        # Record each field in record metadata to a different row in an XML file
        field_list = []
        for field in metadata.fields:
            field_dict = {
                "@name": field.name,
                "@type": field.type.value,
            }
            if field.size:
                field_dict["@size"] = field.size
            if field.description:
                field_dict["@description"] = field.description
            if field.scale:
                field_dict["@scale"] = field.scale
            if field.source:
                field_dict["@source"] = field.source
            field_list.append(field_dict)
        fields_dict = {"Field": field_list}
        to_xml = {"RecordInfo": fields_dict}

        # Create the output XML file
        xml = xmltodict.unparse(
            input_dict=to_xml, pretty=True, short_empty_elements=True
        )
        with open(output_file, "w") as fd:
            fd.write(xml + "\n")
