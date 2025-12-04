"""Tool that retrieves and parses ICP data using structured output."""

import json
from pathlib import Path

import pandas as pd
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

from ..schema.icp import IdealCustomerProfile


def retrieve_icp_tool(llm: ChatOpenAI) -> Tool:
    """Tool that retrieves and parses ICP data using structured output."""

    def _retrieve_icp(*args, **kwargs) -> str:
        """Read ICP data from CSV and parse into structured IdealCustomerProfile format."""
        # Find ICP.csv file - check both current directory and tools directory
        csv_path = Path("ICP.csv")
        if not csv_path.exists():
            csv_path = Path(__file__).parent / "ICP.csv"
        if not csv_path.exists():
            csv_path = Path("src/application/tools/ICP.csv")
        if not csv_path.exists():
            raise FileNotFoundError("ICP.csv not found")

        # Read raw data
        df = pd.read_csv(csv_path)
        icp_dict = dict(zip(df["Parameter"], df["Value"]))

        # Format data for LLM parsing
        data_str = "\n".join([f"{k}: {v}" for k, v in icp_dict.items()])

        # Use structured output to parse
        parser = llm.with_structured_output(IdealCustomerProfile)

        prompt = f"""
        Parse the following Ideal Customer Profile (ICP) data into structured format.

        Raw Data:
        {data_str}

        Extract and structure:
        - Industries (allowed/blocked) - split semicolon-separated values into lists
        - Employee count range (min/max) - convert to integers
        - Regions (allowed/blocked) - split semicolon-separated values into lists
        - Technologies required - split semicolon-separated values into lists
        - Buyer personas - split semicolon-separated values into lists
        - Excluded personas - split semicolon-separated values into lists
        """

        # Parse into structured format and return as JSON string
        icp = parser.invoke([{"role": "user", "content": prompt}])
        return json.dumps(icp.model_dump())

    return Tool(
        name="retrieve_icp",
        description="Retrieves and parses the Ideal Customer Profile (ICP) data.",
        func=_retrieve_icp,
    )