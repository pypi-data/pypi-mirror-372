import json
import requests
from typing import Any, Optional, Tuple


class RequestUtils:
    @staticmethod
    def post(
        url: str,
        headers: dict,
        json_payload: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        stream: bool = False,
        params: Optional[dict] = None,
    ) -> Tuple[Any, int]:
        if files is not None and json_payload is not None:
            data = {"json_payload": json.dumps(json_payload)}
            json_payload = None

        response = requests.post(
            url=url,
            headers=headers,
            files=files,
            json=json_payload,
            data=data,
            params=params,
        )
        return RequestUtils._process_response(response, stream=stream)

    @staticmethod
    def put(
        url: str,
        headers: dict,
        payload: Optional[dict] = None,
    ) -> Tuple[Any, int]:
        response = requests.put(url=url, headers=headers, json=payload)
        return RequestUtils._process_response(response)

    @staticmethod
    def get(
        url: str,
        headers: dict,
        stream: bool = False,
        params: Optional[dict] = None,
    ) -> Tuple[Any, int]:
        response = requests.get(url=url, headers=headers, params=params)
        return RequestUtils._process_response(response, stream=stream)

    @staticmethod
    def delete(
        url: str,
        headers: dict,
        json_payload: Optional[dict] = None,
    ) -> Tuple[Any, int]:
        response = requests.delete(url=url, headers=headers, json=json_payload)
        return RequestUtils._process_response(response)

    @staticmethod
    def patch(
        url: str,
        headers: dict,
        json_payload: Optional[dict] = None,
    ) -> Tuple[Any, int]:
        response = requests.patch(url=url, headers=headers, json=json_payload)
        return RequestUtils._process_response(response)

    @staticmethod
    def _process_response(
        response: requests.Response,
        stream: bool = False,
    ) -> Tuple[Any, int]:
        try:
            RequestUtils._check_for_error_response(response)
            if stream:
                return (
                    RequestUtils._handle_stream_response(response=response),
                    response.status_code,
                )
            else:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return (response.json(), response.status_code)
                elif "text/" in content_type:
                    return (response.text, response.status_code)
                else:
                    return (response.content, response.status_code)
        except requests.exceptions.HTTPError as e:
            response_content = response.content.decode("utf-8")
            error_message = f"{str(e)}\n{response_content}"
            raise type(e)(error_message) from e
        except Exception as e:
            error_message = f"{str(e)}\n{response}"
            raise type(e)(error_message) from e

    @staticmethod
    def _handle_stream_response(
        response: requests.Response,
    ) -> Any:
        accumulated_current_data = ""
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                decoded_chunk = chunk.decode("utf-8")
                if decoded_chunk.strip() == ":" or len(decoded_chunk) == 0:
                    continue

                current_data = accumulated_current_data + decoded_chunk
                accumulated_current_data = ""

                if not current_data.endswith("\n"):
                    accumulated_current_data += current_data
                    continue

                chunks = current_data.strip().split("\n")

                received_stream_chunks = [
                    json.loads(f"{chunk}")
                    for chunk in chunks
                    if chunk and chunk.strip() != ":"
                ]

                # only return the last chunk if the stream is finished
                for received_chunk in received_stream_chunks:
                    if received_chunk.get("finish_reason"):
                        return received_chunk

        return {}

    @staticmethod
    def _check_for_error_response(response: requests.Response) -> None:
        response.raise_for_status()

        # look for the error in the response
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type or "text/event-stream" in content_type:
            try:
                response_json = response.json()
                if isinstance(response_json, dict):
                    # Check for an 'error' key with a truthy value
                    error_content = response_json.get("error")
                    if error_content:
                        raise Exception(f"API error in JSON response: {error_content}")
            except requests.exceptions.JSONDecodeError:
                if "application/json" in content_type:
                    raise Exception(f"API error in JSON response: {response}")
