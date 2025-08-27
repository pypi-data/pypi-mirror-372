from fastpluggy.core.widgets import ButtonWidget
from fastapi import Request


def websocket_notification_button(request: Request):
    """
    Create a button to send a WebSocket notification.
    """

    try:
        url_ws_send_message = request.url_for('send_message', method='json')

        content = """
            fetch('__url_ws_send_message__', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({type: 'message', content: 'test notification'})
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => console.log(data))
            .catch(error => console.error('Error sending message:', error));
        """.replace('__url_ws_send_message__', url_ws_send_message)

        return ButtonWidget(
            url= "#",  # No direct URL needed since we use JavaScript
            label= "Send WebSocket Notification",
            css_class= "btn btn-primary",
            onclick=content ,
        )
    except Exception as e:
        error_message = f"Error creating WebSocket notification button: {e}"
        print(error_message)
        return ButtonWidget(
            url="#",  # Dummy URL since the button is disabled
            label="Send WebSocket Notification (Error)",
            css_class="btn btn-danger",
            disabled=True,
            onclick=f"console.error('{error_message}')",
        )
