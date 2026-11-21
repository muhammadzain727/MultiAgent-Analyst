from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyFashionHub")

@mcp.tool()
def get_products():
    """Retrieve products from the ecommerce database."""
    # Your SQL query implementation goes here
    pass