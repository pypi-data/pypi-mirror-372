import io
import warnings
from typing import Optional, List

import pandas as pd
from langchain_core.language_models import BaseChatModel
from langchain_experimental.tools import PythonAstREPLTool

from codemie_tools.base.base_toolkit import BaseToolkit
from codemie_tools.base.file_object import MimeType, FileObject
from codemie_tools.base.models import ToolKit, ToolSet, Tool
from codemie_tools.file_analysis.csv_tool import CSVTool, get_csv_delimiter
from codemie_tools.file_analysis.file_analysis_tool import FileAnalysisTool
from codemie_tools.file_analysis.pdf_tool import PDFTool
from codemie_tools.file_analysis.pptx_tool import PPTXTool
from codemie_tools.file_analysis.tool_vars import FILE_ANALYSIS_TOOL, PPTX_TOOL, PDF_TOOL, CSV_TOOL


class FileAnalysisToolkit(BaseToolkit):
    model_config = {
        "arbitrary_types_allowed": True
    }
    files: Optional[List[FileObject]] = None
    chat_model: Optional[BaseChatModel] = None
    warnings_length_limit: int = 30

    @classmethod
    def get_tools_ui_info(cls, *args, **kwargs):
        return ToolKit(
            toolkit=ToolSet.FILE_ANALYSIS,
            tools=[
                Tool.from_metadata(FILE_ANALYSIS_TOOL),
                Tool.from_metadata(PPTX_TOOL),
                Tool.from_metadata(PDF_TOOL),
                Tool.from_metadata(CSV_TOOL),
            ]
        ).model_dump()

    def get_tools(self):
        """Get tools for processing files based on their types.
    
        Returns:
            List of tools for file processing
        """
        tools = []
        if not self.files:
            return tools

        # Create buckets for different file types
        pptx_files = []
        pdf_files = []
        csv_files = []
        other_files = []

        # Sort files into buckets
        for file_obj in self.files:
            file_mime = MimeType(file_obj.mime_type)
            if file_mime.is_pptx:
                pptx_files.append(file_obj)
            elif file_mime.is_pdf:
                pdf_files.append(file_obj)
            elif file_mime.is_csv:
                csv_files.append(file_obj)
            else:
                other_files.append(file_obj)

        if pptx_files:
            tools.append(PPTXTool(files=pptx_files, chat_model=self.chat_model))

        if pdf_files:
            tools.append(PDFTool(files=pdf_files, chat_model=self.chat_model))

        # Process CSV files
        if csv_files:
            # Get dataframes and description from _process_csv_files
            dataframes, repl_tool_description = self._pre_process_csv_files(csv_files)

            if dataframes:
                repl_tool = PythonAstREPLTool(locals=dataframes)
                repl_tool.description = repl_tool_description
                tools.extend([repl_tool, CSVTool(files=csv_files)])

        if other_files:
            tools.append(FileAnalysisTool(files=other_files, chat_model=self.chat_model))

        return tools

    @classmethod
    def get_toolkit(cls, files: List[FileObject], chat_model: Optional[BaseChatModel] = None):
        return cls(
            files=files,
            chat_model=chat_model
        )

    def _pre_process_csv_files(self, csv_files):
        """Process CSV files and return dataframes and tool description.
    
        Args:
            csv_files: List of FileObject instances representing CSV files
    
        Returns:
            tuple: (dataframes dictionary, repl_tool_description, warnings_string, csv_files)
        """
        # Read all CSV files and combine them into a dictionary of dataframes
        dataframes = {}
        all_warnings = []
    
        for file_obj in csv_files:
            with warnings.catch_warnings(record=True) as wlist:
                data = FileObject.to_string_content(file_obj.content)
                try:
                    data_frame = pd.read_csv(
                        io.StringIO(data),
                        delimiter=get_csv_delimiter(data, 128),
                        on_bad_lines="warn"
                    )
                    # Store the dataframe with its filename as key (without extension)
                    file_name = file_obj.name
                    if '.' in file_name:
                        file_name = file_name.rsplit('.', 1)[0]
                    dataframes[file_name] = data_frame
    
                    # Collect warnings
                    file_warnings = [str(warning.message) for warning in wlist[:self.warnings_length_limit]]
                    if file_warnings:
                        all_warnings.append(f"Warnings for {file_obj.name}:\n" + "\n".join(file_warnings))
                except Exception as e:
                    all_warnings.append(f"Error processing {file_obj.name}: {str(e)}")
                    continue
    
        # Combine all warnings
        warnings_string = "\n\n".join(all_warnings) if all_warnings else None
    
        # Create repl tool description if there are dataframes
        repl_tool_description = None
        if dataframes:
            repl_tool_description = self._generate_csv_prompt_for_multiple_files(
                dataframes,
                warnings_string
            )
    
        return dataframes, repl_tool_description
    
    @staticmethod
    def _generate_csv_prompt_for_multiple_files(dataframes: dict, warnings_string: Optional[str] = None):
        warning_section = ""
        if warnings_string:
            warning_section = (
                f"\n**ALWAYS note these warnings if they exist. Warning(s) while reading CSV files:**\n"
                f"{warnings_string}\n"
                "These warnings were generated while loading CSV files. "
                "They may indicate malformed rows, missing values, or other data issues. "
                "Please take them into account when analyzing the data.\n"
            )

        df_template = """```python
        {df_name}.head().to_markdown()
        >>> {df_head}
        ```"""
        df_context = "\n\n".join(
            df_template.format(df_head=_df.head().to_markdown(), df_name=df_name)
            for df_name, _df in dataframes.items()
        )
        return f"""You have access to a number of pandas dataframes. \
        Here is a sample of rows from each dataframe and the python code that was used to generate the sample:
        
        {df_context}
        
        {warning_section}

        Given a user question about the dataframes, write the Python code to answer it. \
        Don't assume you have access to any libraries other than built-in Python ones and pandas. \
        Make sure to refer only to the variables mentioned above."""
