import os
import streamlit.components.v1 as components
import requests
import json
import streamlit as st
from typing import Optional

_RELEASE = True


if not _RELEASE:
    _render_component_func = components.declare_component(
        "render_response",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _render_component_func = components.declare_component("render_response", path=build_dir)

def render_response(c1Response, key=None):
    """Create a new instance of "render_response".

    Parameters
    ----------
    c1_response: str
        The c1_response of the thing we're saying hello to. The component will display
        the text "Hello, {c1_response}!"
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    llmFriendlyMessage: str
        The llmFriendlyMessage of the thing we're saying hello to. The component will display
        the text "Hello, {llmFriendlyMessage}!"
    humanFriendlyMessage: str
        The humanFriendlyMessage of the thing we're saying hello to. The component will display
        the text "Hello, {humanFriendlyMessage}!"

    """
    component_value = _render_component_func(c1Response=c1Response, key=key, default=None)
    return component_value


def visualize(instructions: str='', data=None, api_key: Optional[str] = None, key: Optional[str] = None):
    """Create a visualization using the Thesys visualize endpoint.

    Parameters
    ----------
    data: any
        The data to visualize - can be any format typically used with Streamlit
        (dataframes, lists, dicts, etc.). Will be converted to JSON format.
    api_key: str
        The Thesys API key for authentication. You can get your API key from https://console.thesys.dev.
    instructions: str or None
        The instructions to pass to the LLM for the visualization.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    component_value
        The result from the rendered component containing any user interactions
    """
    if api_key is None or data is None:
        st.error("API key & data is required to use the visualize method")
        return None
    try:
        # Convert data to JSON format for visualization
        if hasattr(data, 'to_json'):
            # Handle pandas DataFrames
            data_json = data.to_json(orient='records')
        elif isinstance(data, (dict, list)):
            # Handle dictionaries and lists
            data_json = json.dumps(data)
        else:
            # Handle strings and other types
            data_json = str(data)

        # Call the Thesys endpoint using requests with correct OpenAI format
        system_prompt = """
        You are a data visualization expert.
        You are going to receive a dataset and a prompt. Generate visualization based on the prompt and the dataset.
        If no instructions are provided, generate the best visualization to represent the entire dataset.
        If instructions are provided, generate only the visualization that is requested and nothing else.
        Be succint and only return the visualization(s) and nothing else.
        """
        system_prompt += f"\n{instructions}" if instructions else ""
        response = requests.post(
            "https://api.thesys.dev/v1/embed/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "c1/anthropic/claude-sonnet-4/v-20250709",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Dataset: \n{data_json}\n\nPrompt: \n{instructions}"}
                ]
            }
        )

        if response.status_code == 201:
            visualize_response = response.json()
            # Extract the content from the response using OpenAI format
            if "choices" in visualize_response and len(visualize_response["choices"]) > 0:
                content = visualize_response["choices"][0]["message"]["content"]
                # Use the existing render_response function to display the content
                return render_response(content, key=key)
            else:
                # Log error and return None if response format is invalid
                st.error("Invalid response format from Thesys visualize endpoint")
                return None
        else:
            # Log error and return None instead of passing error to render_response
            st.error(f"Error calling Thesys visualize endpoint: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        # Log error and return None instead of passing error to render_response
        st.error(f"Exception calling Thesys visualize endpoint: {str(e)}")
        return None
