from io import StringIO
from pathlib import Path
from datetime import datetime
import fitz
import pandas as pd
from langchain.docstore.document import Document
from .basepdf import BasePDF


class PDFBlocks(BasePDF):
    """
    Load a PDF Table as Blocks of text.
    """
    _extension = ['.pdf']

    def __init__(
        self,
        table_settings: dict = {},
        **kwargs
    ):
        self._skiprows = kwargs.pop('skiprows', None)
        super().__init__(**kwargs)
        # Table Settings:
        self.table_settings = {
            # "vertical_strategy": "text",
            # "horizontal_strategy": "text",
            "intersection_x_tolerance": 5,
            "intersection_y_tolerance": 5
        }
        if table_settings:
            self.table_settings.update(table_settings)

    def unique_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename duplicate columns in the DataFrame to ensure they are unique.

        Args:
            df (pd.DataFrame): The DataFrame with potential duplicate column names.

        Returns:
            pd.DataFrame: A DataFrame with unique column names.
        """
        seen = {}
        new_columns = []
        for col in df.columns:
            new_col = col
            count = seen.get(col, 0)
            while new_col in new_columns:
                count += 1
                new_col = f"{col}_{count}"
            new_columns.append(new_col)
            seen[col] = count
        df.columns = new_columns
        return df

    def get_markdown(self, df: pd.DataFrame) -> str:
        """
        Convert a DataFrame to a Markdown string.

        Args:
            df (pd.DataFrame): The DataFrame to convert.

        Returns:
            str: The JSON string.
        """
        buffer = StringIO()
        df = self.unique_columns(df)
        df.to_markdown(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def parse_table(self, table_idx, table, page_number, path) -> pd.DataFrame:
        df = table.to_pandas()  # convert to pandas DataFrame
        df = df.dropna(axis=1, how='all')
        df = df.dropna(how='all', axis=0)  # Drop empty rows
        page = page_number + 1
        table_meta = {
            "url": '',
            "source": f"{path.name} Page.#{page} Table.#{table_idx}",
            "filename": path.name,
            "question": '',
            "answer": '',
            "type": 'table',
            "summary": '',
            "category": self.category,
            "source_type": self._source_type,
            "created_at": datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
            "document_meta": {
                "table_index": table_idx,
                "table_shape": df.shape,
                "table_columns": df.columns.tolist(),
                "description": f"Extracted from Page.#{page}."
            }
        }
        return df, table_meta

    def _load_pdf(self, path: Path) -> list:
        """
        Load a PDF file using the Fitz library.

        Args:
            path (Path): The path to the PDF file.

        Returns:
            list: A list of Langchain Documents.
        """
        if self._check_path(path):
            self.logger.info(f"Loading PDF file: {path}")
            pdf = fitz.open(str(path))  # Open the PDF file
            docs = []
            # Create document-level context
            document_context = f"File Name: {path.name}\n"
            document_context += f"Document Type: {self.doctype}\n"
            document_context += f"Source Type: {self._source_type}\n\n"
            for page_number in range(pdf.page_count):
                page = pdf[page_number]
                try:
                    tabs = page.find_tables(**self.table_settings)
                    for tab_idx, tab in enumerate(tabs):
                        df, _meta = self.parse_table(tab_idx, tab, page_number, path)
                        try:
                            markdown_table = self.get_markdown(df)
                            docs.append(
                                Document(
                                    page_content=document_context + markdown_table,
                                    metadata=_meta
                                )
                            )
                        except Exception as exc:
                            print(exc)
                        ## Sample information:
                        print('::: Printing Table Information === ')
                        print(df)
                        print("::: Printing Column Information === ")
                        for column, t in df.dtypes.items():
                            print(column, "->", t, "->", df[column].iloc[0])
                        # convert into markdown:
                        txt = df.to_markdown()
                        if txt:
                            docs.append(
                                Document(page_content=document_context + txt, metadata=_meta)
                            )
                except Exception as exc:
                    print(exc)
                    continue
            return docs
