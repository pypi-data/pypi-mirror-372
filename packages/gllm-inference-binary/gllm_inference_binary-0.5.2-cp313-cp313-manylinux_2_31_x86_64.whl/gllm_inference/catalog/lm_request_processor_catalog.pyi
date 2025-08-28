from _typeshed import Incomplete
from gllm_inference.builder import build_lm_request_processor as build_lm_request_processor
from gllm_inference.catalog.catalog import BaseCatalog as BaseCatalog
from gllm_inference.request_processor import LMRequestProcessor as LMRequestProcessor

MODEL_ID_ENV_VAR_REGEX_PATTERN: str
LM_REQUEST_PROCESSOR_REQUIRED_COLUMNS: Incomplete
CONFIG_SCHEMA_MAP: Incomplete

class LMRequestProcessorCatalog(BaseCatalog[LMRequestProcessor]):
    '''Loads multiple LM request processors from certain sources.

    Attributes:
        components (dict[str, LMRequestProcessor]): Dictionary of the loaded LM request processors.

    Initialization:
        # Example 1: Load from Google Sheets using client email and private key
        ```python
        catalog = LMRequestProcessorCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            client_email="...",
            private_key="...",
        )

        lm_request_processor = catalog.name
        ```

        # Example 2: Load from Google Sheets using credential file
        ```python
        catalog = LMRequestProcessorCatalog.from_gsheets(
            sheet_id="...",
            worksheet_id="...",
            credential_file_path="...",
        )

        lm_request_processor = catalog.name
        ```

        # Example 3: Load from CSV
        ```python
        catalog = LMRequestProcessorCatalog.from_csv(csv_path="...")

        lm_request_processor = catalog.name
        ```

        # Example 4: Load from record
        ```python
        catalog = LMRequestProcessorCatalog.from_records(
            name="...",
            system_template="...",
            user_template="...",
            model_id="...",
            credentials="...",
            config="...",
            output_parser_type="...",
        )

        lm_request_processor = catalog.name
        ```

    Template Format Example:
        # Example 1: Google Sheets
        For an example of how a Google Sheets file can be formatted to be loaded using LMRequestProcessorCatalog, see:
        https://docs.google.com/spreadsheets/d/1CX9i45yEinv1UdB3s6uHNMj7mxr2-s1NFHfFDvMsq0E/edit?usp=drive_link

        # Example 2: CSV
        For an example of how a CSV file can be formatted to be loaded using LMRequestProcessorCatalog, see:
        https://drive.google.com/file/d/10nYKn_r9SVnTkaik-caMqUjX6prUZ62M/view?usp=drive_link

    Template Explanation:
        The required columns are:
            1. name (str): The name of the LM request processor.
            2. system_template (str): The system template of the prompt builder.
            3. user_template (str): The user template of the prompt builder.
            4. model_id (str): The model ID of the LM invoker.
            5. credentials (str | json_str): The credentials of the LM invoker.
            6. config (json_str): The additional configuration of the LM invoker.
            7. output_parser_type (str): The type of the output parser.

        Important Notes:
        1. At least one of `system_template` or `user_template` must be filled.
        2. The `model_id`:
            2.1. Must be filled with the model ID of the LM invoker, e.g. "openai/gpt-4.1-nano".
            2.2. Can be partially loaded from the environment variable using the "${ENV_VAR_KEY}" syntax,
                e.g. "azure-openai/${AZURE_ENDPOINT}/${AZURE_DEPLOYMENT}".
            2.3. For the available model ID formats, see: https://gdplabs.gitbook.io/sdk/resources/supported-models
        3. `credentials` is optional. If it is filled, it can either be:
            3.1. An environment variable name containing the API key (e.g. OPENAI_API_KEY).
            3.2. An environment variable name containing the path to a credentials JSON file
                (e.g. GOOGLE_CREDENTIALS_FILE_PATH). Currently only supported for Google Vertex AI.
            3.3. A dictionary of credentials, with each value being an environment variable name corresponding to the
                credential (e.g. {"api_key": "OPENAI_API_KEY"}). Currently supported for Bedrock and LangChain.
            If it is empty, the LM invoker will use the default credentials loaded from the environment variables.
        4. `config` is optional. If filled, must be a dictionary containing the configuration for the LM invoker.
            If it is empty, the LM invoker will use the default configuration.
        5. `output_parser_type` can either be:
            5.1. none: No output parser will be used.
            5.2. json: The JSONOutputParser will be used.
    '''
