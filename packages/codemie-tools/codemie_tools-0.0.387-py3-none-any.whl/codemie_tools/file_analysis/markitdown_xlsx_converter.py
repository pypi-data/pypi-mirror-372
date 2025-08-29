import logging
from typing import BinaryIO, Any

import markitdown
import pandas as pd
from markitdown import StreamInfo, DocumentConverterResult
from markitdown.converters import HtmlConverter

logger = logging.getLogger(__name__)

class XlsxConverter(markitdown.converters.XlsxConverter):
    """
    Converts XLSX files to Markdown, with each sheet presented as a separate Markdown table.
    Customized to filter out empty rows and columns (NaN values) to reduce markdown size and improve readability.
    """

    def __init__(self, sheet_names: list[str]=None) -> None:
        super().__init__()
        self.sheet_names = sheet_names
        logger.info("Enable custom XLSX converter")

    def convert(
            self,
            file_stream: BinaryIO,
            stream_info: StreamInfo,
            **kwargs: Any,  # Options to pass to the converter
    ) -> DocumentConverterResult:
        """
        Converts Excel files to markdown tables, filtering out empty rows and columns to reduce output size.
        """

        # Load all sheets as dict of DataFrames
        sheets = pd.read_excel(
            file_stream,
            engine="openpyxl",
            sheet_name=self.sheet_names,
            keep_default_na=False,
            na_filter=False,
        )
        logger.debug(f"Found {len(sheets)} sheets. {sheets.keys()}")
        # Clean all sheets, store in a new dict
        sheets_clean = {}
        for sheet_name, df in sheets.items():
            # Drop columns where all rows are NaN or empty string
            # This reduces the width of the markdown table by removing unused columns
            df_clean = df.dropna(axis=1, how='all')
            df_clean = df_clean.loc[:, ~(df_clean.apply(lambda x: x.astype(str).str.strip() == '').all())]
            # Drop rows where all columns are NaN or empty string
            # This reduces the height of the markdown table by removing empty rows
            df_clean = df_clean.dropna(axis=0, how='all')
            df_clean = df_clean.loc[~(df_clean.apply(lambda x: x.astype(str).str.strip() == '').all(axis=1))]
            sheets_clean[sheet_name] = df_clean

        md_content = ""
        for sheet_name, df in sheets_clean.items():
            md_content += f"## {sheet_name}\n"
            html_content = df.to_html(index=False)
            md_content += (
                    self._html_converter.convert_string(
                        html_content, **kwargs
                    ).markdown.strip()
                    + "\n\n"
            )

        return DocumentConverterResult(markdown=md_content.strip())
