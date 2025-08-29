import gradio as gr
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from .server import completion_queue
import base64
import io
from PIL import Image

class HumanCompletionUI:
    def __init__(self, server_url: str = "http://localhost:8002"):
        self.server_url = server_url
        self.current_call_id: Optional[str] = None
        self.refresh_interval = 2.0  # seconds
        self.last_image = None  # Store the last image for display
    
    def format_messages_for_chatbot(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format messages for display in gr.Chatbot with type='messages'."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tool_calls = msg.get("tool_calls", [])
            
            # Handle different content formats
            if isinstance(content, list):
                # Multi-modal content - can include text and images
                formatted_content = []
                for item in content:
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        if text.strip():  # Only add non-empty text
                            formatted_content.append(text)
                    elif item.get("type") == "image_url":
                        image_url = item.get("image_url", {}).get("url", "")
                        if image_url:
                            # Check if it's a base64 image or URL
                            if image_url.startswith("data:image"):
                                # For base64 images, decode and create gr.Image
                                try:
                                    header, data = image_url.split(",", 1)
                                    image_data = base64.b64decode(data)
                                    image = Image.open(io.BytesIO(image_data))
                                    formatted_content.append(gr.Image(value=image))
                                except Exception as e:
                                    print(f"Error loading image: {e}")
                                    formatted_content.append(f"[Image loading error: {e}]")
                            else:
                                # For URL images, create gr.Image with URL
                                formatted_content.append(gr.Image(value=image_url))
                
                # Determine final content format
                if len(formatted_content) == 1:
                    content = formatted_content[0]
                elif len(formatted_content) > 1:
                    content = formatted_content
                else:
                    content = "[Empty content]"
            
            # Ensure role is valid for Gradio Chatbot
            if role not in ["user", "assistant"]:
                role = "assistant" if role == "system" else "user"
            
            # Invert roles for better display in human UI context
            # (what the AI says becomes "user", what human should respond becomes "assistant")
            if role == "user":
                role = "assistant"
            else:
                role = "user"
            
            # Add the main message if it has content
            if content and str(content).strip():
                formatted.append({"role": role, "content": content})
            
            # Handle tool calls - create separate messages for each tool call
            if tool_calls:
                for tool_call in tool_calls:
                    function_name = tool_call.get("function", {}).get("name", "unknown")
                    arguments_str = tool_call.get("function", {}).get("arguments", "{}")
                    
                    try:
                        # Parse arguments to format them nicely
                        arguments = json.loads(arguments_str)
                        formatted_args = json.dumps(arguments, indent=2)
                    except json.JSONDecodeError:
                        # If parsing fails, use the raw string
                        formatted_args = arguments_str
                    
                    # Create a formatted message for the tool call
                    tool_call_content = f"```json\n{formatted_args}\n```"
                    
                    formatted.append({
                        "role": role,
                        "content": tool_call_content,
                        "metadata": {"title": f"🛠️ Used {function_name}"}
                    })
        
        return formatted
    
    def get_pending_calls(self) -> List[Dict[str, Any]]:
        """Get pending calls from the server."""
        try:
            response = requests.get(f"{self.server_url}/pending", timeout=5)
            if response.status_code == 200:
                return response.json().get("pending_calls", [])
        except Exception as e:
            print(f"Error fetching pending calls: {e}")
        return []
    
    def complete_call_with_response(self, call_id: str, response: str) -> bool:
        """Complete a call with a text response."""
        try:
            response_data = {"response": response}
            response_obj = requests.post(
                f"{self.server_url}/complete/{call_id}",
                json=response_data,
                timeout=10
            )
            response_obj.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error completing call: {e}")
            return False
    
    def complete_call_with_tool_calls(self, call_id: str, tool_calls: List[Dict[str, Any]]) -> bool:
        """Complete a call with tool calls."""
        try:
            response_data = {"tool_calls": tool_calls}
            response_obj = requests.post(
                f"{self.server_url}/complete/{call_id}",
                json=response_data,
                timeout=10
            )
            response_obj.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error completing call: {e}")
            return False
    
    def complete_call(self, call_id: str, response: Optional[str] = None, tool_calls: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Complete a call with either a response or tool calls."""
        try:
            response_data = {}
            if response:
                response_data["response"] = response
            if tool_calls:
                response_data["tool_calls"] = tool_calls
            
            response_obj = requests.post(
                f"{self.server_url}/complete/{call_id}",
                json=response_data,
                timeout=10
            )
            response_obj.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error completing call: {e}")
            return False
    
    def get_last_image_from_messages(self, messages: List[Dict[str, Any]]) -> Optional[Any]:
        """Extract the last image from the messages for display above conversation."""
        last_image = None
        
        for msg in reversed(messages):  # Start from the last message
            content = msg.get("content", "")
            
            if isinstance(content, list):
                for item in reversed(content):  # Get the last image in the message
                    if item.get("type") == "image_url":
                        image_url = item.get("image_url", {}).get("url", "")
                        if image_url:
                            if image_url.startswith("data:image"):
                                # For base64 images, create a gr.Image component
                                try:
                                    header, data = image_url.split(",", 1)
                                    image_data = base64.b64decode(data)
                                    image = Image.open(io.BytesIO(image_data))
                                    return image
                                except Exception as e:
                                    print(f"Error loading image: {e}")
                                    continue
                            else:
                                # For URL images, return the URL
                                return image_url
        
        return last_image
    
    def refresh_pending_calls(self):
        """Refresh the list of pending calls."""
        pending_calls = self.get_pending_calls()
        
        if not pending_calls:
            return (
                gr.update(choices=["latest"], value="latest"),  # dropdown
                gr.update(value=None),  # image (no image)
                gr.update(value=[]),  # chatbot (empty messages)
                gr.update(interactive=False)  # submit button
            )
        
        # Sort pending calls by created_at to get oldest first
        sorted_calls = sorted(pending_calls, key=lambda x: x.get("created_at", ""))
        
        # Create choices for dropdown
        choices = [("latest", "latest")]  # Add "latest" option first
        
        for call in sorted_calls:
            call_id = call["id"]
            model = call.get("model", "unknown")
            created_at = call.get("created_at", "")
            # Format timestamp
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = created_at
            
            choice_label = f"{call_id[:8]}... ({model}) - {time_str}"
            choices.append((choice_label, call_id))
        
        # Default to "latest" which shows the oldest pending conversation
        selected_call_id = "latest"
        if selected_call_id == "latest" and sorted_calls:
            # Use the oldest call (first in sorted list)
            selected_call = sorted_calls[0]
            conversation = self.format_messages_for_chatbot(selected_call.get("messages", []))
            self.current_call_id = selected_call["id"]
            # Get the last image from messages
            self.last_image = self.get_last_image_from_messages(selected_call.get("messages", []))
        else:
            conversation = []
            self.current_call_id = None
            self.last_image = None
        
        return (
            gr.update(choices=choices, value="latest"),
            gr.update(value=self.last_image),
            gr.update(value=conversation),
            gr.update(interactive=bool(choices))
        )
    
    def on_call_selected(self, selected_choice):
        """Handle when a call is selected from the dropdown."""
        if not selected_choice:
            return (
                gr.update(value=None),  # no image
                gr.update(value=[]),  # empty chatbot
                gr.update(interactive=False)
            )
        
        pending_calls = self.get_pending_calls()
        if not pending_calls:
            return (
                gr.update(value=None),  # no image
                gr.update(value=[]),  # empty chatbot
                gr.update(interactive=False)
            )
        
        # Handle "latest" option
        if selected_choice == "latest":
            # Sort calls by created_at to get oldest first
            sorted_calls = sorted(pending_calls, key=lambda x: x.get("created_at", ""))
            selected_call = sorted_calls[0]  # Get the oldest call
            call_id = selected_call["id"]
        else:
            # Extract call_id from the choice for specific calls
            call_id = None
            for call in pending_calls:
                call_id_short = call["id"][:8]
                if call_id_short in selected_choice:
                    call_id = call["id"]
                    break
            
            if not call_id:
                return (
                    gr.update(value=None),  # no image
                    gr.update(value=[]),  # empty chatbot
                    gr.update(interactive=False)
                )
            
            # Find the selected call
            selected_call = next((c for c in pending_calls if c["id"] == call_id), None)
        
        if not selected_call:
            return (
                gr.update(value=None),  # no image
                gr.update(value=[]),  # empty chatbot
                gr.update(interactive=False)
            )
        
        conversation = self.format_messages_for_chatbot(selected_call.get("messages", []))
        self.current_call_id = call_id
        # Get the last image from messages
        self.last_image = self.get_last_image_from_messages(selected_call.get("messages", []))
        
        return (
            gr.update(value=self.last_image),
            gr.update(value=conversation),
            gr.update(interactive=True)
        )
    
    def submit_response(self, response_text: str):
        """Submit a text response to the current call."""
        if not self.current_call_id:
            return (
                gr.update(value=response_text),  # keep response text
                gr.update(value="❌ No call selected")  # status
            )
        
        if not response_text.strip():
            return (
                gr.update(value=response_text),  # keep response text
                gr.update(value="❌ Response cannot be empty")  # status
            )
        
        success = self.complete_call_with_response(self.current_call_id, response_text)
        
        if success:
            status_msg = "✅ Response submitted successfully!"
            return (
                gr.update(value=""),  # clear response text
                gr.update(value=status_msg)  # status
            )
        else:
            return (
                gr.update(value=response_text),  # keep response text
                gr.update(value="❌ Failed to submit response")  # status
            )
    
    def submit_action(self, action_type: str, **kwargs) -> str:
        """Submit a computer action as a tool call."""
        if not self.current_call_id:
            return "❌ No call selected"
        
        import uuid
        
        # Create tool call structure
        action_data = {"type": action_type, **kwargs}
        tool_call = {
            "id": f"call_{uuid.uuid4().hex[:24]}",
            "type": "function",
            "function": {
                "name": "computer",
                "arguments": json.dumps(action_data)
            }
        }
        
        success = self.complete_call_with_tool_calls(self.current_call_id, [tool_call])
        
        if success:
            return f"✅ {action_type.capitalize()} action submitted as tool call"
        else:
            return f"❌ Failed to submit {action_type} action"
    
    def submit_click_action(self, x: int, y: int, action_type: str = "click", button: str = "left") -> str:
        """Submit a coordinate-based action."""
        if action_type == "click":
            return self.submit_action(action_type, x=x, y=y, button=button)
        else:
            return self.submit_action(action_type, x=x, y=y)
    
    def submit_type_action(self, text: str) -> str:
        """Submit a type action."""
        return self.submit_action("type", text=text)
    
    def submit_hotkey_action(self, keys: str) -> str:
        """Submit a hotkey action."""
        return self.submit_action("keypress", keys=keys)
    
    def submit_description_click(self, description: str, action_type: str = "click", button: str = "left") -> str:
        """Submit a description-based action."""
        if action_type == "click":
            return self.submit_action(action_type, element_description=description, button=button)
        else:
            return self.submit_action(action_type, element_description=description)
    
    def wait_for_pending_calls(self, max_seconds: float = 10.0, check_interval: float = 0.2):
        """Wait for pending calls to appear or until max_seconds elapsed.
        
        This method loops and checks for pending calls at regular intervals,
        returning as soon as a pending call is found or the maximum wait time is reached.
        
        Args:
            max_seconds: Maximum number of seconds to wait
            check_interval: How often to check for pending calls (in seconds)
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < max_seconds:
            # Check if there are any pending calls
            pending_calls = self.get_pending_calls()
            if pending_calls:
                # Found pending calls, return immediately
                return self.refresh_pending_calls()
            
            # Wait before checking again
            time.sleep(check_interval)
        
        # Max wait time reached, return current state
        return self.refresh_pending_calls()


def create_ui():
    """Create the Gradio interface."""
    ui_handler = HumanCompletionUI()
    
    with gr.Blocks(title="Human-in-the-Loop Agent Tool") as demo:
        gr.Markdown("# 🤖 Human-in-the-Loop Agent Tool")
        gr.Markdown("Review AI conversation requests and provide human responses.")
        
        with gr.Row():
            with gr.Column(scale=2):
                with gr.Group():
                    screenshot_image = gr.Image(
                        label="Screenshot",
                        interactive=False,
                        height=600
                    )
                    
                    # Action type selection for image clicks
                    with gr.Row():
                        action_type_radio = gr.Radio(
                            label="Action Type",
                            choices=["click", "double_click", "move", "left_mouse_up", "left_mouse_down"],
                            value="click",
                            scale=2
                        )
                        action_button_radio = gr.Radio(
                            label="Button (for click only)",
                            choices=["left", "right", "wheel", "back", "forward"],
                            value="left",
                            visible=True,
                            scale=1
                        )
                    
                    conversation_chatbot = gr.Chatbot(
                        label="Messages",
                        type="messages",
                        height=500,
                        show_copy_button=True
                    )
            
            with gr.Column(scale=1):
                with gr.Group():
                    call_dropdown = gr.Dropdown(
                        label="Select a pending call",
                        choices=["latest"],
                        interactive=True,
                        value="latest"
                    )
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary")

                with gr.Group():
                    response_text = gr.Textbox(
                        label="Response",
                        lines=3,
                        placeholder="Enter your response here..."
                    )
                    submit_btn = gr.Button("📤 Submit Response", variant="primary", interactive=False)
                
                # Action Accordions
                with gr.Accordion("🖱️ Click Actions", open=False):
                    with gr.Group():
                        with gr.Row():
                            click_x = gr.Number(label="X", value=0, minimum=0)
                            click_y = gr.Number(label="Y", value=0, minimum=0)
                        with gr.Row():
                            click_action_type = gr.Dropdown(
                                label="Action Type",
                                choices=["click", "double_click", "move", "left_mouse_up", "left_mouse_down"],
                                value="click"
                            )
                            click_button = gr.Dropdown(
                                label="Button (for click only)",
                                choices=["left", "right", "wheel", "back", "forward"],
                                value="left"
                            )
                        click_submit_btn = gr.Button("Submit Action")
                
                with gr.Accordion("📝 Type Action", open=False):
                    with gr.Group():
                        type_text = gr.Textbox(
                            label="Text to Type",
                            placeholder="Enter text to type..."
                        )
                        type_submit_btn = gr.Button("Submit Type")
                
                with gr.Accordion("⌨️ Keypress Action", open=False):
                    with gr.Group():
                        keypress_text = gr.Textbox(
                            label="Keys",
                            placeholder="e.g., ctrl+c, alt+tab"
                        )
                        keypress_submit_btn = gr.Button("Submit Keypress")
                
                with gr.Accordion("🎯 Description Action", open=False):
                    with gr.Group():
                        description_text = gr.Textbox(
                            label="Element Description",
                            placeholder="e.g., 'Privacy and security option in left sidebar'"
                        )
                        with gr.Row():
                            description_action_type = gr.Dropdown(
                                label="Action Type",
                                choices=["click", "double_click", "move", "left_mouse_up", "left_mouse_down"],
                                value="click"
                            )
                            description_button = gr.Radio(
                                label="Button (for click only)",
                                choices=["left", "right", "wheel", "back", "forward"],
                                value="left"
                            )
                        description_submit_btn = gr.Button("Submit Description Action")
                
                status_display = gr.Textbox(
                    label="Status",
                    interactive=False,
                    value="Ready to receive calls..."
                )
        
        # Event handlers
        refresh_btn.click(
            fn=ui_handler.refresh_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )
        
        call_dropdown.change(
            fn=ui_handler.on_call_selected,
            inputs=[call_dropdown],
            outputs=[screenshot_image, conversation_chatbot, submit_btn]
        )
        
        def handle_image_click(evt: gr.SelectData):
            if evt.index is not None:
                x, y = evt.index
                action_type = action_type_radio.value or "click"
                button = action_button_radio.value or "left"
                result = ui_handler.submit_click_action(x, y, action_type, button)
                ui_handler.wait_for_pending_calls()
                return result
            return "No coordinates selected"

        screenshot_image.select(
            fn=handle_image_click,
            outputs=[status_display]
        ).then(
            fn=ui_handler.wait_for_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )

        # Response submission
        submit_btn.click(
            fn=ui_handler.submit_response,
            inputs=[response_text],
            outputs=[response_text, status_display]
        ).then(
            fn=ui_handler.refresh_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )
        
        # Toggle button radio visibility based on action type
        def toggle_button_visibility(action_type):
            return gr.update(visible=(action_type == "click"))
        
        action_type_radio.change(
            fn=toggle_button_visibility,
            inputs=[action_type_radio],
            outputs=[action_button_radio]
        )

        # Action accordion handlers
        click_submit_btn.click(
            fn=ui_handler.submit_click_action,
            inputs=[click_x, click_y, click_action_type, click_button],
            outputs=[status_display]
        ).then(
            fn=ui_handler.wait_for_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )
        
        type_submit_btn.click(
            fn=ui_handler.submit_type_action,
            inputs=[type_text],
            outputs=[status_display]
        ).then(
            fn=ui_handler.wait_for_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )
        
        keypress_submit_btn.click(
            fn=ui_handler.submit_hotkey_action,
            inputs=[keypress_text],
            outputs=[status_display]
        ).then(
            fn=ui_handler.wait_for_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )
        
        def handle_description_submit(description, action_type, button):
            if description:
                result = ui_handler.submit_description_click(description, action_type, button)
                ui_handler.wait_for_pending_calls()
                return result
            return "Please enter a description"

        description_submit_btn.click(
            fn=handle_description_submit,
            inputs=[description_text, description_action_type, description_button],
            outputs=[status_display]
        ).then(
            fn=ui_handler.wait_for_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )
        
        # Load initial data
        demo.load(
            fn=ui_handler.refresh_pending_calls,
            outputs=[call_dropdown, screenshot_image, conversation_chatbot, submit_btn]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=7860)
