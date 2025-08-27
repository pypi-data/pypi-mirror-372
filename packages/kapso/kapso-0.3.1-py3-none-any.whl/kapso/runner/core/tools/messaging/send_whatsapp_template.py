"""
Definition for the SendWhatsappTemplateMessage tool.
"""

from pydantic import BaseModel, Field


class SendWhatsappTemplateMessage(BaseModel):
    """
    Use this tool to send a WhatsApp Template message to the user.
    The tool will use registered template configurations to determine if it should wait for a response.

    Key usage guidelines:
    - Use when you need to send a structured WhatsApp template message
    - If you see a string with format #{variable_name} in the parameters, replace it with the value
    - The template_parameters is required and must be a dictionary. If no parameters are needed, use an empty dictionary.

    Args (all required):
        template_name: The name of the template to send
        phone_number: The recipient's phone number
        template_parameters: A dictionary of template parameters
    """

    template_name: str = Field(description="The name of the template to send")
    phone_number: str = Field(description="The recipient's phone number")
    template_parameters: dict = Field(description="A dictionary of template parameters")
