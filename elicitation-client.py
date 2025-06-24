import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession
import mcp.types as types
from mcp.shared.context import RequestContext
from typing import Any, Dict
import re
import signal
import sys

# Configuration
MCP_SERVER_URL = "http://localhost:8000/mcp"


class ElicitationHandler:
    """Handles different types of elicitation requests."""

    @staticmethod
    def get_date_input() -> str:
        """Get and validate date input from user."""
        while True:
            try:
                date_input = input(
                    "Enter the date for your booking (YYYY-MM-DD): "
                ).strip()
                if re.match(r"^\d{4}-\d{2}-\d{2}$", date_input):
                    return date_input
                print("Please enter date in YYYY-MM-DD format.")
            except KeyboardInterrupt:
                raise
            except EOFError:
                raise KeyboardInterrupt

    @staticmethod
    def get_party_size_input() -> int:
        """Get and validate party size input from user."""
        while True:
            try:
                party_size = int(
                    input("Enter the number of people (1-20): ").strip()
                )
                if 1 <= party_size <= 20:
                    return party_size
                print("Party size must be between 1 and 20.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                raise
            except EOFError:
                raise KeyboardInterrupt

    @staticmethod
    def get_confirmation_input() -> Dict[str, Any]:
        """Get confirmation and notes from user."""
        try:
            print("\nBooking confirmation required:")
            confirm_input = input(
                "Do you want to confirm this booking? (y/n): "
            ).lower().strip()
            confirm = confirm_input in ['y', 'yes', '1', 'true']

            notes = ""
            if confirm:
                notes = input(
                    "Any special requests or notes? (optional): "
                ).strip()

            return {"confirm": confirm, "notes": notes}
        except (KeyboardInterrupt, EOFError):
            raise KeyboardInterrupt


async def smart_elicitation_callback(
    context: RequestContext["ClientSession", Any],
    params: types.ElicitRequestParams,
) -> types.ElicitResult | types.ErrorData:
    """Smart elicitation callback that handles different request types."""

    try:
        print("\n--- Server Request ---")
        print(f"Message: {params.message}")

        message = params.message.lower()
        handler = ElicitationHandler()

        # Determine response type based on message content
        if "date" in message and "confirm" not in message:
            response_data = {"date": handler.get_date_input()}

        elif "party size" in message or "number of people" in message:
            response_data = {"party_size": handler.get_party_size_input()}

        elif "confirm" in message:
            response_data = handler.get_confirmation_input()

        else:
            # Fallback for unknown requests
            print("Unknown request type. Please provide input:")
            user_input = input("Your response: ").strip()
            response_data = {"response": user_input}

        return types.ElicitResult(
            action="accept",
            content=response_data
        )

    except KeyboardInterrupt:
        print("\n⚠️  User cancelled input")
        return types.ElicitResult(
            action="cancel",
            content={}
        )
    except Exception as e:
        print(f"Error in elicitation callback: {e}")
        return types.ErrorData(
            code=types.INTERNAL_ERROR,
            message=f"Elicitation failed: {str(e)}"
        )


async def run():
    """Main client execution function."""
    try:
        async with streamablehttp_client(
            url=MCP_SERVER_URL,
        ) as (read_stream, write_stream, _):

            async with ClientSession(
                read_stream=read_stream,
                write_stream=write_stream,
                elicitation_callback=smart_elicitation_callback
            ) as session:

                # Initialize session
                init_result = await session.initialize()
                capabilities_list = list(
                    init_result.capabilities.__dict__.keys()
                )
                print(f"✅ Connected with capabilities: {capabilities_list}")

                # List available tools
                tools = await session.list_tools()
                tool_names = [tool.name for tool in tools.tools]
                print(f"✅ Available tools: {tool_names}")

                print("\n🍽️  Starting table booking process...")

                # Test different scenarios
                scenarios = [
                    {"name": "No arguments (full elicitation)", "args": {}},
                    {"name": "With date only", "args": {"date": "2025-07-01"}},
                    {"name": "Invalid date",
                     "args": {"date": "2024-01-01", "party_size": 4}},
                ]

                for scenario in scenarios:
                    print(f"\n--- Testing: {scenario['name']} ---")
                    try:
                        result = await session.call_tool(
                            name="book_table",
                            arguments=scenario["args"]
                        )
                        print(f"✅ Result: {result.content[0].text}")
                    except Exception as e:
                        print(f"❌ Error: {e}")

                    # Ask if user wants to try another scenario
                    if scenario != scenarios[-1]:
                        try:
                            continue_test = input(
                                "\nTry next scenario? (y/n): "
                            ).lower().strip()
                            if continue_test not in ['y', 'yes']:
                                break
                        except (KeyboardInterrupt, EOFError):
                            print("\n⚠️  Demo cancelled by user")
                            break

                return "Demo completed!"

    except KeyboardInterrupt:
        print("\n⚠️  Connection cancelled by user")
        return "Demo cancelled"
    except Exception as e:
        print(f"\n❌ Connection error: {e}")
        return f"Demo failed: {e}"


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\n⚠️  Received interrupt signal, shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    try:
        result = asyncio.run(run())
        print(f"\n🎉 {result}")
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
