# edinet_tools.py
import datetime
import json
import os
import urllib.parse
import urllib.request
import logging
import time
from typing import List, Dict, Union

from .config import EDINET_API_KEY, SUPPORTED_DOC_TYPES

# Use module-specific logger
logger = logging.getLogger(__name__)


# API interaction functions
def fetch_documents_list(date: Union[str, datetime.date],
                         type: int = 2,
                         max_retries: int = 3,
                         delay_seconds: int = 5,
                         api_key: str = None) -> Dict:
    """
    Retrieve disclosure documents from EDINET API for a specified date with retries.
    """
    if isinstance(date, str):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date string. Use format 'YYYY-MM-DD'")
        date_str = date
    elif isinstance(date, datetime.date):
        date_str = date.strftime('%Y-%m-%d')
    else:
        raise TypeError("Date must be 'YYYY-MM-DD' or datetime.date")

    url = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
    params = {
        "date": date_str,
        "type": type,   # '1' is metadata only; '2' is metadata and results
        "Subscription-Key": api_key or EDINET_API_KEY,
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to fetch documents for {date_str}...")
            with urllib.request.urlopen(full_url) as response:
                # Check for non-200 status codes
                if response.getcode() != 200:
                    logger.error(f"API returned status code {response.getcode()} for date {date_str}.")
                    # Attempt to read error body if available
                    try:
                         error_body = response.read().decode('utf-8')
                         logger.error(f"Error body: {error_body}")
                    except Exception:
                         pass
                    # If it's a client error (4xx) or server error (5xx), might be retryable
                    if 400 <= response.getcode() < 600 and attempt < max_retries - 1:
                         logger.warning(f"Retrying in {delay_seconds}s...")
                         time.sleep(delay_seconds)
                         continue # Retry
                    else:
                         # Non-retryable error or last attempt
                         raise urllib.error.HTTPError(full_url, response.getcode(), f"HTTP Error: {response.getcode()}", response.headers, None)


                data = json.loads(response.read().decode('utf-8'))
                logger.info(f"Successfully fetched documents for {date_str}.")
                return data

        except urllib.error.URLError as e:
            logger.error(f"URL Error fetching documents for {date_str}: {e}")
            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {delay_seconds}s...")
                time.sleep(delay_seconds)
            else:
                logger.error("Max retries reached for fetching documents.")
                raise # Re-raise the last exception
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching documents for {date_str}: {e}")
            if attempt < max_retries - 1:
                 logger.warning(f"Retrying in {delay_seconds}s...")
                 time.sleep(delay_seconds)
            else:
                 logger.error("Max retries reached for fetching documents.")
                 raise # Re-raise

    # This line should theoretically not be reached if max_retries > 0
    raise Exception("Failed to fetch documents after multiple retries.")


def fetch_document(doc_id: str, max_retries: int = 3, delay_seconds: int = 5, api_key: str = None) -> bytes:
    """
    Retrieve a specific document from EDINET API with retries and return raw bytes.
    """
    url = f'https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}'
    params = {
      "type": 5,  # '5' for CSV
      "Subscription-Key": api_key or EDINET_API_KEY,
    }
    query_string = urllib.parse.urlencode(params)
    full_url = f'{url}?{query_string}'

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1} to fetch document {doc_id}...")
            with urllib.request.urlopen(full_url) as response:
                 # Check for non-200 status codes
                 if response.getcode() != 200:
                     logger.error(f"API returned status code {response.getcode()} for document {doc_id}.")
                     try:
                          error_body = response.read().decode('utf-8')
                          logger.error(f"Error body: {error_body}")
                     except Exception:
                          pass

                     if 400 <= response.getcode() < 600 and attempt < max_retries - 1:
                          logger.warning(f"Retrying in {delay_seconds}s...")
                          time.sleep(delay_seconds)
                          continue # Retry
                     else:
                          raise urllib.error.HTTPError(full_url, response.getcode(), f"HTTP Error: {response.getcode()}", response.headers, None)

                 content = response.read()
                 logger.info(f"Successfully fetched document {doc_id}.")
                 return content

        except urllib.error.URLError as e:
            logger.error(f"URL Error fetching document {doc_id}: {e}")
            if attempt < max_retries - 1:
                logger.warning(f"Retrying in {delay_seconds}s...")
                time.sleep(delay_seconds)
            else:
                logger.error("Max retries reached for fetching document.")
                raise
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching document {doc_id}: {e}")
            if attempt < max_retries - 1:
                 logger.warning(f"Retrying in {delay_seconds}s...")
                 time.sleep(delay_seconds)
            else:
                 logger.error("Max retries reached for fetching document.")
                 raise

    raise Exception(f"Failed to fetch document {doc_id} after multiple retries.")


def save_document_content(doc_content: bytes, output_path: str) -> None:
    """Save the document content (bytes) to file."""
    try:
        with open(output_path, 'wb') as file_out:
            file_out.write(doc_content)
        logger.info(f"Saved document content to {output_path}")
    except IOError as e:
        logger.error(f"Error saving document content to {output_path}: {e}")
        raise # Re-raise to indicate failure

def download_documents(docs: List[Dict], download_dir: str = './downloads') -> None:
    """
    Download all documents in the provided list.
    """
    os.makedirs(download_dir, exist_ok=True)
    logger.info(f"Ensured download directory exists: {download_dir}")

    total_docs = len(docs)
    logger.info(f"Starting download of {total_docs} documents.")

    for i, doc in enumerate(docs, 1):
        doc_id = doc.get('docID')
        doc_type_code = doc.get('docTypeCode')
        filer = doc.get('filerName')

        if not doc_id or not doc_type_code or not filer:
            logger.warning(f"Skipping document {i}/{total_docs} due to missing metadata: {doc}")
            continue

        save_name = f'{doc_id}-{doc_type_code}-{filer}.zip'
        output_path = os.path.join(download_dir, save_name)

        logger.info(f"Downloading {i}/{total_docs}: `{save_name}`")

        if not os.path.exists(output_path):
            try:
                # make GET request to `documents/{docID}` endpoint
                doc_content = fetch_document(doc_id)
                save_document_content(doc_content, output_path)
            except Exception as e:
                logger.error(f"Error downloading and saving {save_name}: {e}")
        else:
            # logger.info(f"File already exists: {save_name}")
            pass # Keep this silent unless debugging needed

    logger.info(f"Download process complete. Files saved to: `{download_dir}`")


# Document filtering and processing
def filter_documents(docs: List[Dict],
                     edinet_codes: Union[List[str], str] = [],
                     doc_type_codes: Union[List[str], str] = [],
                     excluded_doc_type_codes: Union[List[str], str] = [],
                     require_sec_code: bool = True) -> List[Dict]:
    """Filter list of documents by EDINET codes and document type codes."""
    if isinstance(edinet_codes, str):
        edinet_codes = [edinet_codes]
    if isinstance(doc_type_codes, str):
        doc_type_codes = [doc_type_codes]
    if isinstance(excluded_doc_type_codes, str):
        excluded_doc_type_codes = [excluded_doc_type_codes]

    filtered_list = []
    for doc in docs:
         # Basic checks
        if 'docID' not in doc or 'docTypeCode' not in doc or 'filerName' not in doc:
            logger.warning(f"Skipping document with incomplete metadata: {doc}")
            continue

        # Check for supported document types (optional, but good practice)
        if doc['docTypeCode'] not in SUPPORTED_DOC_TYPES:
             # logger.debug(f"Skipping document type {doc['docTypeCode']} ({doc['filerName']}) - not supported.")
             continue # Skip document types we don't explicitly support analysis for

        # Apply EDINET code filter
        if edinet_codes and doc.get('edinetCode') not in edinet_codes:
            continue

        # Apply document type code filter
        if doc_type_codes and doc['docTypeCode'] not in doc_type_codes:
            continue

        # Apply excluded document type code filter
        if doc['docTypeCode'] in excluded_doc_type_codes:
            continue

        # Apply require securities code filter
        if require_sec_code and doc.get('secCode') is None:
            continue

        filtered_list.append(doc)

    logger.info(f"Filtered down to {len(filtered_list)} documents from initial list of {len(docs)}.")
    return filtered_list


def get_documents_for_date_range(start_date: datetime.date,
                                 end_date: datetime.date,
                                 edinet_codes: List[str] = [],
                                 doc_type_codes: List[str] = [],
                                 excluded_doc_type_codes: List[str] = [],
                                 require_sec_code: bool = True,
                                 api_key: str = None) -> List[Dict]:
    """Retrieve and filter documents for a date range."""
    matching_docs = []
    current_date = start_date
    while current_date <= end_date:
        try:
            docs_res = fetch_documents_list(date=current_date, api_key=api_key)
            if docs_res and docs_res.get('results'):
                logger.info(f"Found {len(docs_res['results'])} documents on EDINET for {current_date}.")
                filtered_docs = filter_documents(
                        docs_res['results'], edinet_codes,
                        doc_type_codes, excluded_doc_type_codes, require_sec_code
                )
                matching_docs.extend(filtered_docs)
                logger.info(f"Added {len(filtered_docs)} matching documents for {current_date}.")
            elif docs_res and docs_res.get('results') is None:
                 logger.info(f"No documents listed for {current_date}.")
            elif not docs_res:
                 logger.warning(f"Empty response received for {current_date}.")

        except Exception as e:
            logger.error(f"Error processing documents for date {current_date}: {e}")
            # Continue to next date even if one date fails
        finally:
             current_date += datetime.timedelta(days=1)

    logger.info(f"Finished retrieving documents for date range. Total matching documents: {len(matching_docs)}")
    return matching_docs
