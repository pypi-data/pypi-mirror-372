import os
import requests
import json
from types import MappingProxyType
from typing import List, Mapping, Union, Optional, Any
from functools import singledispatchmethod
import dataclasses
from threading import Lock
import time
import rich
from wxo_agentic_evaluation.service_provider.provider import Provider

ACCESS_URL = "https://iam.cloud.ibm.com/identity/token"
ACCESS_HEADER = {
    "content-type": "application/x-www-form-urlencoded",
    "accept": "application/json",
}

YPQA_URL = "https://yp-qa.ml.cloud.ibm.com"
PROD_URL = "https://us-south.ml.cloud.ibm.com"
DEFAULT_PARAM = MappingProxyType(
    {"min_new_tokens": 1, "decoding_method": "greedy", "max_new_tokens": 400}
)


class WatsonXProvider(Provider):
    def __init__(
        self,
        model_id=None,
        api_key=None,
        space_id=None,
        api_endpoint=PROD_URL,
        url=ACCESS_URL,
        timeout=60,
        params=None,
        embedding_model_id=None,
    ):
        super().__init__()
        self.url = url
        if (embedding_model_id is None) and (model_id is None):
            raise Exception("either model_id or embedding_model_id must be specified")
        self.model_id = model_id
        api_key = os.environ.get("WATSONX_APIKEY", api_key)
        if not api_key:
            raise Exception("apikey must be specified")
        self.api_key = api_key
        self.access_data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key,
        }
        self.api_endpoint = api_endpoint
        space_id = os.environ.get("WATSONX_SPACE_ID", space_id)
        if not space_id:
            raise Exception("space id must be specified")
        self.space_id = space_id
        self.timeout = timeout
        self.embedding_model_id = embedding_model_id
        self.lock = Lock()

        self.params = params if params else DEFAULT_PARAM
        
        if isinstance(self.params, MappingProxyType):
            self.params = dict(self.params)
        if dataclasses.is_dataclass(self.params):
            self.params = dataclasses.asdict(self.params)

        self.refresh_time = None
        self.access_token = None
        self._refresh_token()

    def _get_access_token(self):
        response = requests.post(
            self.url, headers=ACCESS_HEADER, data=self.access_data, timeout=self.timeout
        )
        if response.status_code == 200:
            token_data = json.loads(response.text)
            token = token_data["access_token"]
            expiration = token_data["expiration"]
            expires_in = token_data["expires_in"]
            # 9 minutes before expire
            refresh_time = expiration - int(0.15 * expires_in)
            return token, refresh_time

        raise RuntimeError(
            f"try to acquire access token and get {response.status_code}"
        )

    def prepare_header(self):
        headers = {"Authorization": f"Bearer {self.access_token}",
                  "Content-Type": "application/json"}
        return headers

    @singledispatchmethod
    def generate(self, sentence):
        raise ValueError(f"Input must either be a string or a list of dictionaries")

    @generate.register
    def _(self, sentence: str):
        headers = self.prepare_header()

        data = {"model_id": self.model_id, "input": sentence,
                "parameters": self.params, "space_id": self.space_id}
        generation_url = f"{self.api_endpoint}/ml/v1/text/generation?version=2023-05-02"
        resp = requests.post(url=generation_url, headers=headers, json=data)
        if resp.status_code == 200:
            return resp.json()["results"][0]
        else:
            resp.raise_for_status()

    @generate.register
    def _(self, sentence: list):
        chat_url = f"{self.api_endpoint}/ml/v1/text/chat?version=2023-05-02"
        headers = self.prepare_header()
        data = {
            "model_id": self.model_id,
            "messages": sentence,
            "parameters": self.params,
            "space_id": self.space_id
        }
        resp = requests.post(url=chat_url, headers=headers, json=data)
        if resp.status_code == 200:
            return resp.json()
        else:
            resp.raise_for_status()

    def _refresh_token(self):
        # if we do not have a token or the current timestamp is 9 minutes away from expire.
        if not self.access_token or time.time() > self.refresh_time:
            with self.lock:
                if not self.access_token or time.time() > self.refresh_time:
                    self.access_token, self.refresh_time = self._get_access_token()

    def query(self, sentence: Union[str, Mapping[str, str]]) -> str:
        if self.model_id is None:
            raise Exception("model id must be specified for text generation")
        try:
            response = self.generate(sentence)
            if (generated_text := response.get("generated_text")):
                return generated_text
            elif (message := response.get("message")):
                return message
            else:
                raise ValueError(f"Unexpected response from WatsonX: {response}")
            
        except Exception as e:
            with self.lock:
                if "authentication_token_expired" in str(e):
                    self._refresh_token()
                raise e

    def batch_query(self, sentences: List[str]) -> List[dict]:
        return [self.query(sentence) for sentence in sentences]

    def encode(self, sentences: List[str]) -> List[list]:
        if self.embedding_model_id is None:
            raise Exception("embedding model id must be specified for text encoding")

        headers = self.prepare_header()
        url = f"{self.api_endpoint}/ml/v1/text/embeddings?version=2023-10-25"

        data = {"inputs": sentences, "model_id": self.model_id, "space_id": self.space_id}
        resp = requests.post(url=url, headers=headers, json=data)
        if resp.status_code == 200:
            return [entry["embedding"] for entry in resp.json()["results"]]
        else:
            resp.raise_for_status()

class LLMResponse:
    """
    NOTE: Taken from LLM-Eval-Kit
    Response object that can contain both content and tool calls
    """

    def __init__(self, content: str, tool_calls: Optional[List[Mapping[str, Any]]] = None):
        self.content = content
        self.tool_calls = tool_calls or []

    def __str__(self) -> str:
        """Return the content of the response as a string."""
        return self.content

    def __repr__(self) -> str:
        """Return a string representation of the LLMResponse object."""
        return f"LLMResponse(content='{self.content}', tool_calls={self.tool_calls})"

class WatsonXLLMKitWrapper(WatsonXProvider):
    def generate(
            self,
            prompt: Union[str, List[Mapping[str, str]]],
            *,
            schema,
            retries: int = 3,
            generation_args: Optional[Any] = None,
            **kwargs: Any
        ):

        """
        In future, implement validation of response like in llmevalkit
        """

        for attempt in range(1, retries + 1):
            try:
                raw_response = super().generate(prompt)
                response = self._parse_llm_response(raw_response)
                return response
            except Exception as e:
                rich.print(f"[b][r] WatsonX generation failed with error '{str(e)}' during `quick-eval` ... Attempt ({attempt} / {retries}))")

    def _parse_llm_response(self, raw: Any) -> Union[str, LLMResponse]:
        """
        Extract the generated text and tool calls from a watsonx response.

        - For text generation: raw['results'][0]['generated_text']
        - For chat:           raw['choices'][0]['message']['content']
        """
        content = ""
        tool_calls = []

        if isinstance(raw, dict) and "choices" in raw:
            choices = raw["choices"]
            if isinstance(choices, list) and choices:
                first = choices[0]
                msg = first.get("message")
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                    # Extract tool calls if present
                    if "tool_calls" in msg and msg["tool_calls"]:
                        tool_calls = []
                        for tool_call in msg["tool_calls"]:
                            tool_call_dict = {
                                "id": tool_call.get("id"),
                                "type": tool_call.get("type", "function"),
                                "function": {
                                    "name": tool_call.get("function", {}).get("name"),
                                    "arguments": tool_call.get("function", {}).get(
                                        "arguments"
                                    ),
                                },
                            }
                            tool_calls.append(tool_call_dict)
                elif "text" in first:
                    content = first["text"]

        if not content and not tool_calls:
            raise ValueError(f"Unexpected watsonx response format: {raw!r}")

        # Return LLMResponse if tool calls exist, otherwise just content
        if tool_calls:
            return LLMResponse(content=content, tool_calls=tool_calls)

        return content

if __name__ == "__main__":
    provider = WatsonXProvider(model_id="meta-llama/llama-3-2-90b-vision-instruct")

    prompt = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>


Your username is nwaters and you want to find out timeoff schedule for yourself for 20250101 to 20250303
<|eot_id|><|start_header_id|>user<|end_header_id|>


Reminder:
- try to respond only once per input
- if you get everything you need. respond with END

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
my username is nwaters. what's my timeoff schedule?<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
we need to call get_assignment_id for username nwaters. do you want to make the function call? yes/no<|eot_id|>
<|start_header_id|>user<|end_header_id|>
yes<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
ok, i have your assignment id. what's the start and end date?<|eot_id|>
<|start_header_id|>user<|end_header_id|>
start and end is 20250101 to 20250303<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
Usernwaters did not take anytime off during the period<|eot_id|>

{% endfor -%}
<|eot_id|><|start_header_id|>user<|end_header_id|>
"""

    print(provider.query(prompt))