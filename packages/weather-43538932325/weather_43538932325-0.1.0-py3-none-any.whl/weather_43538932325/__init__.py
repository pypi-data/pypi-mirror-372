from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "北京，晴天,3级西南风"
    
def main() -> None:
    mcp.run(transport="stdio")
