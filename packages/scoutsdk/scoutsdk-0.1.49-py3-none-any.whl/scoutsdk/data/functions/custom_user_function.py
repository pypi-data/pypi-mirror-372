from pydantic import BaseModel, Field
from scoutsdk.api import ScoutAPI
from scouttypes.assistants import AssistantPublicResponse
from scoutsdk import scout


class TypedObjectFunctionParameters(BaseModel):
    text_file_name: str = Field(
        description="Description of the field usage (Seen by the LLM)"
    )
    text_file_size: int = Field(
        description="Description of the field usage (Seen by the LLM)"
    )


@scout.function(description="Description of the function usage (Seen by the LLM)")
def this_is_a_test_function(
    my_parameter: str = Field(description="Description of the field (Seen by the LLM)"),
    my_custom_class_parameter: TypedObjectFunctionParameters = Field(
        description="Description of the field (Seen by the LLM)"
    ),
):
    scout_api = ScoutAPI()  # Instanciate a ScoutAPI. When used in an assistant, Token and URL are automatically filled.
    assistants: list[AssistantPublicResponse] = (
        scout_api.assistants.list_all()
    )  # Call the ScoutAPI
    print(assistants)

    variable_from_assistant = scout.context.get("variable_from_assistant")
    print(variable_from_assistant)

    secret_from_assistant = scout.context.get("secret_from_assistant")
    print(secret_from_assistant)
    return "success"
