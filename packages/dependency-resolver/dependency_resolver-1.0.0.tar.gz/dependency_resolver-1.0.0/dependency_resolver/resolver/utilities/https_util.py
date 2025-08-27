import logging
import requests
from .errors_util import UtilityError

_logger:logging.Logger = logging.getLogger(__name__)


def download(source:str, target:str, chunks:int = 1024 * 1024 * 50) :
    """
    Streams the specified source url into a target file.
    Parameters:
        source - Full absolute URL to the source
        target - Full absolute path to the destination file (note existing file will be truncated if it exists)
        chunks - Response is streamed in chunks to avoid memory issues (number of bytes). 50MB by default.
    Raises:
        errors.HTTPError if it fails to download.
    """
    _logger.debug(f"Downloading {source} to {target}")

    try :
        response:requests.Response = requests.get(source, stream=True, allow_redirects=True, timeout=10)
        response.raise_for_status()  # check for any http errors
        with open(target, 'wb') as targetFile :
            for chunk in response.iter_content(chunks, decode_unicode=False) :
                targetFile.write(chunk)
    except requests.ConnectionError as connection :
        _logger.error(f"Failed to fetch {source}. There was a connection error: {connection}.")
        raise HttpError(f"Failed to fetch {source}. There was a connection error: {connection}.") from connection
    except requests.Timeout as timeout :
        _logger.error(f"Failed to fetch {source}. The request timed out: {timeout}.")
        raise HttpError(f"Failed to fetch {source}. The request timed out: {timeout}.") from timeout
    except requests.HTTPError as http :
        _logger.error(f"Failed to fetch {source}. There was an {http.response.status_code} http error: {http}.")
        raise HttpError(f"Failed to fetch {source}. There was an {http.response.status_code} http error: {http}.") from http
    except requests.RequestException as error :
        _logger.error(f"Failed to fetch {source}. There was an issue with the request: {error}")
        raise HttpError(f"Failed to fetch {source}. There was an issue with the request: {error}") from error


class HttpError(UtilityError) :
    """Raised by the zip utility functions to indicate some issue."""
